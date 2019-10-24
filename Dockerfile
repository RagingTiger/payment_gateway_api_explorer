# Ref: https://github.com/Docker-Hub-frolvlad/docker-alpine-python3
FROM alpine:3.10

# This hack is widely applied to avoid python printing issues in docker containers.
# See: https://github.com/Docker-Hub-frolvlad/docker-alpine-python3/pull/13
ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=payment_gateway_api_server \
    PYTHONVERSION=3.7.5-r1

# Get Flask App source code
WORKDIR /usr/local/src
COPY payment_gateway_api_server /usr/local/src/payment_gateway_api_server

# Install python and requirements
RUN echo "**** install Python ****" && \
    apk add --no-cache python3=${PYTHONVERSION} && \
    if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi && \
    \
    echo "**** install requirements ****" && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --no-cache --upgrade -r payment_gateway_api_server/requirements.txt

# Setup flask as entrypoint/command
CMD ["flask", "run", "--host", "0.0.0.0"]
