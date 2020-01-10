#!/bin/bash

docker run -dit --network minifab --name avalon --rm \
  -v $(pwd)/vars/keyfiles:/keyfiles \
  -v $(pwd)/apps/src:/pysrc \
  -v $(pwd)/vars/network.json:/src/network.json \
  hfrd/tongpy:3.6.9

