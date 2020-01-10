FROM python:3.6.9

RUN apt update && \
    apt-get install -y python-dev python3-dev libssl-dev && \
    pip3 install virtualenv && \
    pip3 install git+https://github.com/hyperledger/fabric-sdk-py.git
