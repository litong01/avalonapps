#!/usr/bin/python
import json
import logging
import os
import random
import string
import sys
import time
import uuid

from avalon import base
from avalon import tx_commiter

logger = logging.getLogger(__name__)

def randomString(stringLength=32):
    """Generate a random string of fixed length """
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(stringLength))

def paramGen(amethod):
    params = []
    print("The parameters used to make the call:")
    for atype in amethod:
        if atype["type"] == "bytes32":
            params.append(uuid.uuid4().hex)
        elif atype["type"] in ["bytes", "string"]:
            params.append(randomString(random.randint(10, 50)))
        elif atype["type"] == "uint256":
            params.append(str(random.randint(1000, 1000000)))
        elif atype["type"] == "bytes32[]":
            thisparam = []
            for i in range(1, random.randint(3, 6)):
                thisparam.append(uuid.uuid4().hex)
            params.append(','.join(thisparam))
        print(atype["name"] + ': ' + params[-1])
    return params

def showResponse(resp):
    if len(resp) > 0 and hasattr(resp[0], 'response') and hasattr(resp[0].response, 'payload'):
        if resp[0].response.status != 200:
            print("\nThe execution result:\n", resp[0].response.message, "\n")
        else:
            payload = json.loads(resp[0].response.payload)
            print("\nThe execution payload:\n", payload, "\n")
    else:
        print("\n", resp, "\n")

def main():
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "ERROR"))
    logging.getLogger('avalon').setLevel(logging.INFO)

    autoParams = True
    if len(sys.argv) < 3:
        print("Usage:")
        print("          " + sys.argv[0] + " <chaincode_name> <method> [args]...")
        exit(1)
    elif len(sys.argv) > 3: 
        autoParams = False

    # Load the network profile
    config = None
    with open('network.json', 'r') as profile:
        config = json.load(profile)

    # Load the chaincode and its methods attributes
    validcalls = None
    with open('methods.json', 'r') as allmethods:
        validcalls = json.load(allmethods)

    # first parameter will be the chaincode name, the second will be the method name
    chaincodename = sys.argv[1]
    callname = sys.argv[2]
    if chaincodename not in validcalls.keys():
        print("Please specify a valid chaincode name. Valid ones are " + ",".join(validcalls.keys()) )
        exit(1)
    chaincode = validcalls[chaincodename]
    if callname not in chaincode.keys():
        print("Please specify a valid method name. Valid ones for chaincode " + chaincodename + " are " + ",".join(chaincode.keys()))
        exit(1)

    orgname = base.get_net_info(config, 'client', 'organization')
    peername = random.choice(base.get_net_info(config, 'organizations', orgname, 'peers'))
    print("Organization used: ", orgname)
    print("Peer used: ", peername)    

    # Get a tx commiter
    pd = txcommiter.TxCommitter('network.json', 'mychannel', orgname, peername, 'Admin')
  
    # Get the call attributes according to the method definitions.
    thecall = chaincode[callname]

    if autoParams:
        # If not enough parameters provided, we will generate these parameters
        params = paramGen(thecall['callparams'])
    else:
        # Use user provided parameters
        params = sys.argv[3:]
    resp = pd.ccInvoke(params, chaincodename, callname, '', queryonly=thecall['isQuery'])
    showResponse(resp)

    # For lookups methods, will also do a lookUpNext using the lookupTag returned.
    if callname.endswith('LookUp'):
        payload = json.loads(resp[0].response.payload)
        params.append(payload['lookupTag'])
        resp = pd.ccInvoke(params, chaincodename, callname+'Next', '', queryonly=True)
        showResponse(resp)

if __name__ == "__main__":
    main()