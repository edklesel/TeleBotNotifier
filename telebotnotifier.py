from fastapi import FastAPI, status
from fastapi.responses import JSONResponse, RedirectResponse
import yaml
import requests
import logging
import os
import sys

app = FastAPI()

# Get mandatory environment variables
TELEBOTNOTIFIER_BOT_TOKEN = os.environ.get('TELEBOTNOTIFIER_BOT_TOKEN', None)
TELEBOTNOTIFIER_CHAT_ID = os.environ.get('TELEBOTNOTIFIER_CHAT_ID', None)

# Get optional environment variables
TELEBOTNOTIFIER_DEBUG = os.environ.get('TELEBOTNOTIFIER_DEBUG', "0")
TELEBOTNOTIFIER_USE_HTTP = os.environ.get('TELEBOTNOTIFIER_USE_HTTP', False)

# Set the base URL for Telegram API
if os.environ.get('TELEBOTNOTIFIER_USE_HTTP', False) == "1":
    baseurl_protocol = 'http'
else:
    baseurl_protocol = 'https'

baseurl = f'{baseurl_protocol}://api.telegram.org'

# Use the uvicorn logger
logger = logging.getLogger("uvicorn")

if os.environ.get('TELEBOTNOTIFIER_DEBUG', "0") == "1":
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)


@app.get("/")
async def root():
    return RedirectResponse(url='/info')


@app.get("/info")
async def info():
    return JSONResponse(content={'token': os.environ['TELEBOTNOTIFIER_BOT_TOKEN'], 'chatID': os.environ['TELEBOTNOTIFIER_CHAT_ID']}, status_code=status.HTTP_200_OK)


@app.get("/msg")
async def msg(msg = None):

    if not msg:
        logger.error('Empty message provided.')
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST)

    logger.debug(f'Received request to send message "{msg}"')
    
    msg_url = f"{baseurl}/bot{os.environ.get('TELEBOTNOTIFIER_BOT_TOKEN')}/sendMessage?chat_id={os.environ.get('TELEBOTNOTIFIER_CHAT_ID')}&text={msg}"
    logger.debug(f"Making request to {msg_url}")
    response = requests.get(msg_url)

    response_data = response.json()
    response_code = response.status_code

    if response_code == 200 and 'ok' in response_data and response_data['ok']:
        logger.debug('Message successfully delivered.')
        return JSONResponse(content={'ok': True}, status_code=status.HTTP_200_OK)

    else:
        logger.error('Error delivering message.')
        logger.exception(response_data)
        return JSONResponse(content={'ok': False}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.get("/healthcheck")
async def healthcheck():

    logger.debug('Starting healthcheck routine.')
    health = {}
    status_code = 200

    # Check if the TELEBOTNOTIFIER_BOT_TOKEN is set.
    # If not, exit immediately
    if not os.environ.get('TELEBOTNOTIFIER_BOT_TOKEN',None):
        health['token'] = 'not set'
        logger.error('TELEBOTNOTIFIER_BOT_TOKEN environment vairable not set.')
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JSONResponse(content=health,status_code=status_code)

    #################
    # Check the bot #
    #################

    # Check the Telegram API to confirm the bot is online
    health_bot_url = f"{baseurl}/bot{os.environ.get('TELEBOTNOTIFIER_BOT_TOKEN')}/getMe"
    logger.debug(f'Making request to {health_bot_url}')
    response = requests.get(health_bot_url)

    response_data = response.json()
    response_code = response.status_code

    # If the token works and the bot is online
    if response_code == 200:
        if 'ok' in response_data and response_data['ok']:
            health['bot'] = 'healthy'
            logger.debug('Bot is healthy.')

        else:
            health['bot'] = 'unhealthy'
            logger.error("Unable to parse response from Telegram API.")
            logger.exception(response_data)
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    elif response_code == 401:
        health['bot'] = 'unhealthy'
        logger.error('401 code received from Telegram API. Check bot token.')
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    else:
        health['bot'] = 'unhealthy'
        logger.error('Unable to parse response from Telegram API.')
        logger.exception(response_data)
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    # If the token is bad, the rest of the tests are redundant.
    if health['bot'] == 'unhealthy':
        return JSONResponse(content=health, status_code=status_code)

    ##################
    # Check the chat #
    ##################

    health_chat_url = f"{baseurl}/bot{os.environ.get('TELEBOTNOTIFIER_BOT_TOKEN')}/getChat?chat_id={os.environ.get('TELEBOTNOTIFIER_CHAT_ID')}"
    logger.debug(f"Making request to {health_chat_url}")
    response = requests.get(health_chat_url)

    response_data = response.json()
    response_code = response.status_code

    if response_code == 200:
        if 'ok' in response_data and response_data['ok']:
            health['chat'] = 'healthy'
            logger.debug('Chat ID is valid.')
        
        else:
            health['chat'] = 'unhealthy'
            logger.error("Unable to parse response from Telegram API.")
            logger.exception(response_data)
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    elif response_code == 400:
        health['chat'] = 'unhealthy'
        logger.error('400 code received from Telegram API. Check chat ID.')
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    else:
        health['bot'] = 'unhealthy'
        health['chat'] = 'unhealthy'
        logger.error('Unable to parse response from Telegram API.')
        logger.exception(response_data)
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    return JSONResponse(content=health,status_code=status_code)
