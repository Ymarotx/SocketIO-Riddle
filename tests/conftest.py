import socketio
from pytest_asyncio import fixture


@fixture(scope='module')
def client():
    sio = socketio.Client()
    yield sio
    sio.disconnect()

@fixture(scope='module')
def events(client):
    all_events = {}

    def event_handler(event,data):
        all_events[event] = data

    client.on('*',event_handler)
    yield all_events

@fixture(scope="module")
def riddles():
    from src.all_riddles import riddles

    result = {riddle['text'] : riddle['answer'] for riddle in riddles}

    def get_riddle(text):
        return result.get(text)

    return get_riddle
