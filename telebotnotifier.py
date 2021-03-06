from fastapi import FastAPI, status
from fastapi.responses import JSONResponse, RedirectResponse
import yaml
import requests
import logging
from os import getenv
import sys

app = FastAPI()

# Set global variables
global logger
global baseurl

# Use the uvicorn logger
logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)

# Define the Telegram API URL
baseurl = f'https://api.telegram.org'

@app.on_event('startup')
async def startup():


    # Set the base URL for Telegram API
    if getenv('TELEBOTNOTIFIER_USE_HTTP', False) == "1":
        baseurl = f'http://api.telegram.org'

    # Set the logging level
    if getenv('TELEBOTNOTIFIER_DEBUG', "0") == "1":
        logger.setLevel(logging.DEBUG)


@app.get("/")
async def root():
    return RedirectResponse(url='/info')


@app.get("/info")
async def info():
    return JSONResponse(content={'token': getenv('TELEBOTNOTIFIER_BOT_TOKEN',"not set"), 'chatID': getenv('TELEBOTNOTIFIER_CHAT_ID',"not set")}, status_code=status.HTTP_200_OK)


@app.get("/msg")
async def msg(msg = None):

    if not msg:
        logger.error('Empty message provided.')
        return JSONResponse(content={'ok': False, 'error': 'No message provided.'}, status_code=status.HTTP_400_BAD_REQUEST)

    logger.debug(f'Received request to send message "{msg}"')
    
    msg_url = f"{baseurl}/bot{getenv('TELEBOTNOTIFIER_BOT_TOKEN')}/sendMessage?chat_id={getenv('TELEBOTNOTIFIER_CHAT_ID')}&text={msg}"
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
        return JSONResponse(content={'ok': False, 'response': response_data}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.get("/healthcheck")
async def healthcheck():

    logger.debug('Starting healthcheck routine.')
    health = {}
    status_code = 200

    # Check if the TELEBOTNOTIFIER_BOT_TOKEN is set.
    # If not, exit immediately
    if not getenv('TELEBOTNOTIFIER_BOT_TOKEN',None):
        health['token'] = 'not set'
        logger.error('TELEBOTNOTIFIER_BOT_TOKEN environment vairable not set.')
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JSONResponse(content=health,status_code=status_code)

    #################
    # Check the bot #
    #################

    # Check the Telegram API to confirm the bot is online
    health_bot_url = f"{baseurl}/bot{getenv('TELEBOTNOTIFIER_BOT_TOKEN')}/getMe"
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

    health_chat_url = f"{baseurl}/bot{getenv('TELEBOTNOTIFIER_BOT_TOKEN')}/getChat?chat_id={getenv('TELEBOTNOTIFIER_CHAT_ID')}"
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
