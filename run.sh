#!/bin/bash

docker run -dit --network minifab --name avalon --rm \
  -v $(pwd)/vars/keyfiles:/keyfiles \
  -v $(pwd)/apps:/pysrc \
  -v $(pwd)/vars/mychannel_network.json:/pysrc/network.json \
  hfrd/tongpy:3.6.9

