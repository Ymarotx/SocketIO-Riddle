import uvicorn
import socketio
import logging

from src.all_riddles import riddles

static_files = {'/': 'static/index.html', '/static': './static'}
sio = socketio.AsyncServer(cors_allowed_origins='*',async_mode='asgi')
app = socketio.ASGIApp(sio,static_files=static_files)

logging.basicConfig(level='INFO',
                    # filename='logs.log',
                    format='%(filename)s:%(lineno)d #%(levelname)-8s'
                           '[%(asctime)s)] - %(name)s - %(message)s')

logger = logging.getLogger(__name__)

@sio.event
async def connect(sid,environ):
    logger.info(f'User {sid} connected')
    await sio.save_session(sid=sid,session={'num_riddle' : 0,
                                            'score' : 0})
    assert await sio.get_session(sid=sid), f'Fault save session. Try save sid={sid}'

@sio.on('next')
async def next_event(sid,data):
    session = await sio.get_session(sid=sid)
    assert session, f'Fault in get session. Expected not null dict, got {session}'
    current_riddle = session['num_riddle']
    if current_riddle == 5:
        await sio.emit('over',to=sid,data={'text':'Over'})
        await sio.emit('score',to=sid,data={'value':0})
    else:
        await sio.emit('riddle',to=sid,data={'text':riddles[current_riddle]['text']})

@sio.on('answer')
async def receive_answer(sid,data):
    session = await sio.get_session(sid=sid)
    cur_rid = session['num_riddle']
    score = session['score']
    answer_user = data.get('text')
    answer_riddle = riddles[cur_rid]['answer']
    is_correct = False
    if answer_user.lower() == answer_riddle.lower():
        is_correct = True
        score += 1
    await sio.emit('result',to=sid,data={'riddle':riddles[cur_rid]['text'],
                                         'is_correct':is_correct,
                                         'answer':answer_riddle})
    await sio.emit('score',to=sid,data={'value':score})
    session['score'] = score
    session['num_riddle'] = cur_rid + 1
    await sio.save_session(sid=sid,session=session)

@sio.event
async def disconnect(sid):
    logger.info(f'User {sid} disconnect')

if __name__ == "__main__":
    uvicorn.run(app,host='127.0.0.1',port=8000)



