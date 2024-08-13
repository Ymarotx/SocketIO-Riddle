import time

import requests

URL = 'http://127.0.0.1:8000/'

def test_assets(client):

    response = requests.get(URL)
    assert response.status_code == 200, "Не удалось загрузить страницу index.html"

    page_content = response.content.decode('utf-8')
    assert '<script src="static/lariska.js"></script>' in page_content
    assert '<script src="static/script.js"></script>' in page_content
    assert '<link rel="stylesheet" type="text/css" href="static/style.css"/>' in page_content

    response_lariska = requests.get(URL + 'static/lariska.js')
    assert response_lariska.status_code == 200, "Не удалось подгрузить lariska.js"

    response_script = requests.get(URL + 'static/script.js')
    assert response_script.status_code == 200, "Не удалось подгрузить script.js"

    response_style = requests.get(URL + 'static/style.css')
    assert response_style.status_code == 200, "Не удалось подгрузить style.css"

def test_full_logic(client,events,riddles):

    client.connect(URL)
    assert client.connected, 'Client not connected'

    for i in range(1,5):
        client.emit('next',{})
        time.sleep(0.1)

        response = events.get('riddle')
        assert response, 'Not get event "riddle" after start game' if i == 1 \
            else 'Not get event "riddle" after press button "Next question" '
        assert 'text' in response, 'Not find text riddle in event "riddle" '
        time.sleep(0.1)

        answer = riddles(response['text'])

        client.emit('answer',{'text':answer})
        time.sleep(0.1)

        score = events.get('score')
        assert score, 'Not get event "score" after the answer to question'
        assert score['value'] == i, f'Score should be {i}, waiting {score["value"]}'

        result = events.get('result')
        assert result, 'Not get event ""result, after the answer to question'
        assert result['is_correct'] == True, 'Answer to question should be True'

        for event in ['result','score','riddle']:
            if event in events:
                del events[event]

    client.emit('next',{})
    time.sleep(0.1)
    client.emit('answer',{'text':'wrong answer'})
    time.sleep(0.1)
    result = events.get('result')
    assert result, 'Not get event "result", after wrong asnwer to question'
    assert result['is_correct'] == False, f'The answer should be incorrect'

    if 'score' in events:
        del events['score']

    client.emit('next',{})
    time.sleep(0.1)

    assert 'over' in events, 'The event "over" not get after end game'

    score = events.get('score')
    assert score, 'Not get event "score" after end game'
    assert score['value'] == 0, f'After end game count score should be 0, but got {score["value"]}'

