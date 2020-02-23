[//]: # (SPDX-License-Identifier: CC-BY-4.0)

## Hyperledger Fabric Avalon Test Application

This repo contains example applications to demotrate fabric avalon in action

### Prerequsites

To run the test applications, [docker](https://www.docker.com/) 18.03 or newer and [git](https://git-scm.com/) are required.

### Getting minifabric so that you can set up environment

```curl -o ~/.local/bin/minifab -L https://tinyurl.com/twrt8zv && chmod +x ~/.local/bin/minifab```

[Minifabric](https://github.com/litong01/minifabric) is a tool to deploy fabric network in docker environment

### Clone this repository

```git clone https://github.com/litong01/avalonapps.git```

### Go to the avalonapps directory and stand up a fabric network

```cd avalonapps && minifab up```

This process will take awhile if this is the first time you are setting up
a fabric network. 

To shutdown the fabric network and restart the whole process, do the following:

```minifab down && minifab up```

To remove everything including the fabric network, do the following:
```minifab cleanup```

### Retrieve avalon chaincode and install worker chaincode onto the fabric network
```
./getandinstall.sh
minifab install,approve,commit -n worker
```

You can install, approve and commit other Avalon chaincode by using different chaincode
name with the same command.

### Run avalon apps

Two applications were developed to test the go chaincode and connector python
code. The program named consumer.py in apps directory is the program to
listen to fabric events. The program named producer.py in apps was developed
to submit transactions and query against fabric blockchain network.

#### To start the container to run these programs:
```
./run.sh
```
This command starts a container which uses a [container image](https://hub.docker.com/repository/docker/hfrd/tongpy) includes Hyperledger [fabric
python sdk](https://github.com/hyperledger/fabric-sdk-py) and [Fabric Avalon python connector](https://github.com/hyperledger/avalon/tree/master/sdk/avalon_sdk/fabric).

#### To listen to event workerRegistered, execute the following command
```
docker exec -it avalon bash
cd /pysrc
python3 consumer.py 500
```
The above command runs the Avalon event listener and wait for workerRegister event. It
will wait for 500 seconds, then quit. If you wish to listen for a shorter or longer
period, you can change the value to your desired value. When there are workerRegistered
events produced on Fabric network, this app will show the events.

### To produce some events

```
docker exec -it avalon bash
cd /pysrc
python3 producer.py worker workerRegister
```

This command will register a new worker and produce one workerRegistered event.

## License <a name="license"></a>

Hyperledger Project source code files are made available under the Apache
License, Version 2.0 (Apache-2.0), located in the [LICENSE](LICENSE) file.
Hyperledger Project documentation files are made available under the Creative
Commons Attribution 4.0 International License (CC-BY-4.0), available at http://creativecommons.org/licenses/by/4.0/.
