FROM alpine/git AS BUILD

RUN cd /tmp && git init avalon && cd avalon                         && \
    git remote add origin https://github.com/hyperledger/avalon.git && \
    git config core.sparsecheckout true                             && \
    echo "sdk/avalon_sdk/fabric/*.py" >> .git/info/sparse-checkout  && \
    git pull --depth=1 origin master

FROM python:3.6.9

RUN apt update && \
    apt-get install -y python-dev python3-dev libssl-dev && \
    pip3 install virtualenv && \
    pip3 install git+https://github.com/hyperledger/fabric-sdk-py.git
COPY --from=build /tmp/avalon/sdk/avalon_sdk/fabric /usr/local/lib/python3.6/site-packages/avalon
