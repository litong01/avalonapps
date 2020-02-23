FROM alpine/git AS BUILD

RUN cd /tmp && git init avalon && cd avalon                         && \
    git remote add origin https://github.com/hyperledger/avalon.git && \
    git config core.sparsecheckout true                             && \
    echo "sdk/avalon_sdk/fabric/*.py" >> .git/info/sparse-checkout  && \
    git pull --depth=1 origin master                                && \
    cd /tmp && git init fabric-sdk-py && cd fabric-sdk-py           && \
    git remote add origin https://github.com/hyperledger/fabric-sdk-py.git && \
    git config core.sparsecheckout true                             && \
    echo "hfc/*" >> .git/info/sparse-checkout  && \
    git pull --depth=1 origin master

FROM alpine:3.11

# This hack is widely applied to avoid python printing issues in docker containers.
# See: https://github.com/Docker-Hub-frolvlad/docker-alpine-python3/pull/13
ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache python3 git bash linux-headers build-base python3-dev libffi-dev openssl-dev && \
    if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi                           && \
    python3 -m ensurepip && rm -r /usr/lib/python*/ensurepip                                        && \
    pip3 install --no-cache --upgrade pip setuptools wheel protobuf                                 && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi                                     && \
    pip3 install --no-cache aiogrpc cryptography grpcio requests pycryptodomex hkdf rx
COPY --from=build /tmp/avalon/sdk/avalon_sdk/fabric /usr/lib/python3.8/site-packages/avalon
COPY --from=build /tmp/fabric-sdk-py/hfc /usr/lib/python3.8/site-packages/hfc
