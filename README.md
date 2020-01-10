[//]: # (SPDX-License-Identifier: CC-BY-4.0)

## Hyperledger Fabric Avalon

### Getting minifabric so that you can stand up a fabric network

```curl -o ~/.local/bin/minifab -L https://tinyurl.com/twrt8zv && chmod +x ~/.local/bin/minifab```

### Clone this repository

```https://github.com/litong01/avalon.git```

### Go to the avalon directory and stand up a fabric network

```cd avalon && minifab up -i 1.4.1```

This process will take awhile if this is the first time you are setting up
a fabric network. If for some reason, the network is no longer running, you
can simply do the following command to bring things backup

```minifab down && minifab up -i 1.4.1```

### Install avalon chaincode onto the fabric network
```
sudo cp -r chaincode/* vars/chaincode/*
minifab install -n <chaincodename> -v <chaincodeversion>
minifab instantiate
```

where &lt;chaincodename&gt; should be a name of avalon chaincodes such as
registry, etc., &lt;chaincodeversion&gt; should be the version of chaincode
such as 1.0. If you have updates to the chaincode, you should do the same
steps above but use a new version number.

### Run avalon apps

Two applications were developed to test the go chaincode and connector python
code. The program named consumer.py in apps/src directory is the program to
listen to fabric events. The program named producer.py in apps/src was developed
to submit transactions and query against fabric blockchain network.

#### To start a container to run these programs:

```
./run.sh
```

#### To listen to event workerRegistered, execute the following command
```
docker exec -it avalon bash
cd /pysrc
python3 consumer.py 500
```

### To produce some events and do query

```
docker exec -it avalon bash
cd /pysrc
python3 producer.py <parameters>
```

where &lt;parameters&gt; should be something depends on what you exactly
want to do. Simply do `python3 producer.py` to see the usages

## License <a name="license"></a>

Hyperledger Project source code files are made available under the Apache
License, Version 2.0 (Apache-2.0), located in the [LICENSE](LICENSE) file.
Hyperledger Project documentation files are made available under the Creative
Commons Attribution 4.0 International License (CC-BY-4.0), available at http://creativecommons.org/licenses/by/4.0/.
