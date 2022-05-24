#!/bin/env bash
echo "Stopping engine"
docker stop daliuge-engine
echo "Stopping translator"
docker stop daliuge-translator
docker stop eagle-dep
echo "Removing code"
rm -rf /tmp/daliuge /tmp/EAGLE
echo "Good-bye!"
