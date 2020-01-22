#!/usr/bin/python
import json
import logging
import os
import random
import sys
import time

from avalon import base
from avalon import txcommiter

logger = logging.getLogger(__name__)

def main():
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "ERROR"))
    logging.getLogger('avalon').setLevel(logging.INFO)
    if len(sys.argv) < 2:
        print("Usage:")
        print("          " + sys.argv[0] + " workerRegister <no_of_workers_to_generate>")
        print("      or  " + sys.argv[0] + " workerLookUp")
        print("      or  " + sys.argv[0] + " query  <workerID>")
        exit(1)

    config = None
    with open('network.json', 'r') as profile:
        config = json.load(profile)

    orgname = base.get_net_info(config, 'client', 'organization')
    peername = random.choice(base.get_net_info(config, 'organizations', orgname, 'peers'))
    print(orgname)
    print(peername)    

    pd = txcommiter.TxCommitter('network.json', 'mychannel', orgname, peername, 'Admin')
    if sys.argv[1] == 'workerRegister':
        start = int(time.time())
        stop = int(sys.argv[2]) if len(sys.argv) == 3 else 1
        for i in range(start, start+stop):
            workerID = 'ID' + str(i)
            print(workerID)
            txData = [workerID, '1', 'org1', 'a1,a2,a3', 'whatever here']
            resp = pd.ccInvoke(txData, 'worker', sys.argv[1], '')
            print(resp)
    elif sys.argv[1] == 'workerLookUp':
        txData = ['1', '0', '0']
        resp = pd.ccInvoke(txData, 'worker', sys.argv[1], '', queryonly=True)
        # The following code demostrate how to use the lookupTag to do the lookups
        mypayload = json.loads(resp[0].response.payload)
        print(mypayload['lookupTag'])
        print(mypayload['ids'])
        txData = ['1', '0', '0', mypayload['lookupTag'] ]
        resp = pd.ccInvoke(txData, 'worker', 'workerLookUpNext', '', queryonly=True)
        mypayload = json.loads(resp[0].response.payload)
        print(mypayload['ids'])
    elif sys.argv[1] == 'workerLookUpNext':
        txData = ['1', '0', '0', sys.argv[2]]
        resp = pd.ccInvoke(txData, 'worker', sys.argv[1], '', queryonly=True)
        print(resp)
    elif sys.argv[1] == 'workerRetrieve':
        txData = [sys.argv[2]]
        resp = pd.ccInvoke(txData, 'worker', sys.argv[1], '', queryonly=True)
        print(json.loads(resp[0].response.payload))
    elif sys.argv[1] == 'workerQuery':
        workerID = sys.argv[2] if len(sys.argv) == 3 else 'ID001'
        pd.ccQuery([workerID], 'worker')
    elif sys.argv[1] == 'registryAdd':
        start = int(time.time())
        stop = int(sys.argv[2]) if len(sys.argv) == 3 else 1
        for i in range(start, start+stop):
            orgID = 'ID' + str(i)
            print(orgID)
            txData = [orgID, 'https://example.com', 'scAddr?', 'a1,a2,a3']
            resp = pd.ccInvoke(txData, 'registry', sys.argv[1], '')
            print(resp)
    elif sys.argv[1] == 'registryUpdate':
        start = int(time.time())
        stop = int(sys.argv[2]) if len(sys.argv) == 3 else 1
        for i in range(start, start+stop):
            orgID = 'ID' + str(i)
            print(orgID)
            txData = [orgID, 'https://example.com', 'scAddr_wwat?', 'a1,a2,a3,a4']
            resp = pd.ccInvoke(txData, 'registry', sys.argv[1], '')
            print(resp)
    elif sys.argv[1] == 'registryLookUp':
        txData = ['a2']
        resp = pd.ccInvoke(txData, 'registry', sys.argv[1], '', queryonly=True)
        # The following code demostrate how to use the lookupTag to do the lookups
        mypayload = json.loads(resp[0].response.payload)
        print(mypayload['lookupTag'])
        print(mypayload['ids'])
        txData = ['a2', mypayload['lookupTag']]
        resp = pd.ccInvoke(txData, 'registry', 'registryLookUpNext', '', queryonly=True)
        mypayload = json.loads(resp[0].response.payload)
        print(mypayload['ids'])
    elif sys.argv[1] == 'registryLookUpNext':
        txData = ['a2', sys.argv[2]]
        resp = pd.ccInvoke(txData, 'registry', sys.argv[1], '', queryonly=True)
        print(resp)
    elif sys.argv[1] == 'registryRetrieve':
        txData = [sys.argv[2]]
        resp = pd.ccInvoke(txData, 'registry', sys.argv[1], '', queryonly=True)
        print(json.loads(resp[0].response.payload))
    elif sys.argv[1] == 'registryQuery':
        orgID = sys.argv[2]
        pd.ccQuery([orgID], 'registry')
    elif sys.argv[1] == 'workOrderSubmit':
        txData = ['100', 'worderId', 'myrequesterid', 'whatever is here']
        resp = pd.ccInvoke(txData, 'order', sys.argv[1], '')
        print(resp)

if __name__ == "__main__":
    main()