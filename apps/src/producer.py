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
            txData = {'workerID': workerID, 'workerType': 1, 'organizationID': 'org1',
                 'applicationTypeId': ['a1','a2','a3'], 'details': 'whatever here'}
            pd.ccInvoke(txData, 'registry', sys.argv[1],'1.0')
    elif sys.argv[1] == 'workerLookUp':
        txData = {'workerType': 1, 'organizationID': '0', 'applicationTypeId': '0'}
        resp = pd.ccInvoke(txData, 'registry', sys.argv[1], '1.0', queryonly=True)
        print(resp)

    elif sys.argv[1] == 'query':
        workerID = sys.argv[2] if len(sys.argv) == 3 else 'ID001'
        pd.ccQuery([workerID], 'registry')

if __name__ == "__main__":
    main()
