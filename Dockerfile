FROM alpine:latest

MAINTAINER edwardklesel@gmail.com

RUN apk add --update python3 py3-pip curl

# Copy files to the working directory
ENV WORKDIR=/app
RUN mkdir ${WORKDIR}
WORKDIR ${WORKDIR}

COPY ./requirements.txt .
COPY ./telebotnotifier.py .

# Install required packaged
RUN pip3 install -r requirements.txt --ignore-installed six

# Expose the relevant ports
EXPOSE 8000

# Set the healthcheck command
HEALTHCHECK CMD curl --fail http://localhost:8000/healthcheck || exit 1

# Start the server
CMD uvicorn telebotnotifier:app --port=8000 --host=0.0.0.0