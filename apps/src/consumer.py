#!/usr/bin/python
import asyncio
import json
import os
import logging
import sys
import random

from avalon import base
from avalon import event_listener

logger = logging.getLogger(__name__)

# Sample handler
def eventHandler(event, block_num, txnid, status):
    print("WE ARE BEING CALLED")
    print(event, block_num, txnid, status)

def main():
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "ERROR"))
    logging.getLogger('avalon').setLevel(logging.INFO)
    if len(sys.argv) != 2:
        print("Usage:")
        print("          " + sys.argv[0] + " <no_of_seconds_to_wait>")
        exit(1)

    config = None
    with open('network.json', 'r') as profile:
        config = json.load(profile)

    orgname = base.get_net_info(config, 'client', 'organization')
    peername = random.choice(base.get_net_info(config, 'organizations', orgname, 'peers'))
    print(orgname)
    print(peername)    

    ec = eventlistener.EventListener('network.json', 'mychannel', orgname, peername, 'Admin')
    ec.config = 'blockmark'
    ec.event = 'workerRegistered'
    ec.chaincode = 'registry'
    ec.handler = eventHandler

    loop = asyncio.get_event_loop()
    tasks = [ec.startEventHandling(), ec.stopEventHandling(int(sys.argv[1]))]
    loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))
    loop.close()

if __name__ == "__main__":
    main()
