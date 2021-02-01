# TeleBotNotifier

TeleBotNotifier is a Python tool written using FastAPI to interact with a telegram bot.

This was created out of the desire for a simple self-hosted notification system which could send a message just by sending a single http request.

## Configuration

The app is configured through the use of environment variables. The reason for this is it is designed to be run in a container, and configuration is simple when using environment variables in a container.

### Required Parameters

The app requires the following environment variables to be set.

| Parameter | Description |
| ----- | ----- |
| TELEBOTNOTIFIER_BOT_TOKEN | The http token provided when creating the bot. |
| TELEBOTNOTIFIER_CHAT_ID | The chat ID or channel name which you want to send messages to. |

### Optional Parameters

| Parameter | Default | Description |
| ----- | ----- | ------ |
| TELEBOTNOTIFIER_DEBUG | `0` | Set to `1` to enable debugging. Any other value will be ignored. |
| TELEBOTNOTIFIER_USE_HTTP | `0` | Set to `1` to prefer `http` over `https` when making requests to `api.telegram.org`. Any other value will be ignored. |

## Setup

### Telegram Bot

To use this service, you first need to create a telegram bot. Check the [Telegram documentation](https://core.telegram.org/bots#6-botfather) for more details.

Once the bot is set up and you have your bot's http token, send a message to the bot usign the Telegram mobile/desktop app.

Then make a request to `https://api.telegram.org/bot<BOT_TOKEN>/getUpdates` to get your chat ID.

### Docker Setup

Docker repo: <https://hub.docker.com/repository/docker/eddi16/telebotnotifier>

An example docker-compose configuration would look like:

```yaml
version: '3.6'

services:
  telebotnotifier:
    image: eddi16/telebotnotifier
    container_name: telebotnotifier
    environment:
      - TELEBOTNOTIFIER_BOT_TOKEN=<BOT HTTP TOKEN>
      - TELEBOTNOTIFIER_CHAT_ID=<CHAT ID>
      # Any optional env variables here
    ports:
    - 8000:8000
```

Or without docker-compose:

```sh
docker run -d -e TELEBOTNOTIFIER_BOT_TOKEN=<BOT HTTP TOKEN> -e TELEBOTNOTIFIER_CHAT_ID=<CHAT ID> -p 8000:8000 --name telebotnotifier eddi16/telebotnotifier
```

### Manual Setup

The API is started in the typical FastAPI fashion, by running the below command:

```sh
uvicorn telebotnotifier:app
```

See [https://www.uvicorn.org/](https://www.uvicorn.org/) for more options on configuring listening port, etc.

## Usage

Once the service is up and healthy, you are able to send a message from your bot in the specified chat/channel. e.g:

* In a browser:
  
![Browser request.](img/browser_request.png)

* Using `curl`

```sh
curl -G -X GET localhost:8000/msg --data-urlencode "msg=Hello, this is your bot speaking!"
```

* Sending file contents or other multi-line output

```sh
curl -G -X GET http://localhost:8000/msg --data-urlencode "msg=$(cat docker-compose.yml)"
```

## Additional Info

### Healthcheck

The service has a healthcheck function as the API was designed to be run in a container.

The healthcheck routine:

* Checks that the bot token is valid.
* Checks that the chat ID is valid for that bot.
