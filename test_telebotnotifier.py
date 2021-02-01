from fastapi.testclient import TestClient
from os import getenv, environ
from random import randint
from telebotnotifier import app

client = TestClient(app)

stringvars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_'
bot_dudtoken = f"{randint(1000000000, 9999999999)}:{''.join([stringvars[randint(0,len(stringvars)-1)] for x in range(28)])}_{''.join([stringvars[randint(0,len(stringvars)-1)] for x in range(6)])}"
bot_dudchat = randint(1000000000, 9999999999)

class ConfigExeption(Exception):
    pass

# Confirm config variables are set
if not getenv('TELEBOTNOTIFIER_TEST_BOT_TOKEN', None) or not getenv('TELEBOTNOTIFIER_TEST_CHAT_ID', None):
    raise ConfigExeption(f"Config not set correctly. TELEBOTNOTIFIER_TEST_BOT_TOKEN={getenv('TELEBOTNOTIFIER_TEST_BOT_TOKEN')}, TELEBOTNOTIFIER_TEST_CHAT_ID={getenv('TELEBOTNOTIFIER_TEST_CHAT_ID')}")

def test_healthcheck_badtoken():

    # Set the tokens to dodgy values
    environ['TELEBOTNOTIFIER_BOT_TOKEN'] = bot_dudtoken

    response = client.get('/healthcheck')

    assert response.status_code == 500
    assert response.json() == {'bot': 'unhealthy'}

def test_healthcheck_badchat():

    global workingtoken

    environ['TELEBOTNOTIFIER_BOT_TOKEN'] = getenv('TELEBOTNOTIFIER_TEST_BOT_TOKEN')
    environ['TELEBOTNOTIFIER_CHAT_ID'] = str(bot_dudchat)
    
    response = client.get('/healthcheck')

    assert response.status_code == 500
    assert response.json() == {'bot': 'healthy', 'chat': 'unhealthy'}


def test_healthcheck_healthy():

    environ['TELEBOTNOTIFIER_BOT_TOKEN'] = getenv('TELEBOTNOTIFIER_TEST_BOT_TOKEN')
    environ['TELEBOTNOTIFIER_CHAT_ID'] = getenv('TELEBOTNOTIFIER_TEST_CHAT_ID')

    response = client.get('/healthcheck')

    assert response.status_code == 200
    assert response.json() == {'bot': 'healthy', 'chat': 'healthy'}


def test_info():

    response = client.get('/info')

    assert response.status_code == 200
    assert response.json() == {'token': getenv('TELEBOTNOTIFIER_BOT_TOKEN'), 'chatID': getenv('TELEBOTNOTIFIER_CHAT_ID')}
