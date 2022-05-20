#!/bin/env bash
echo "Stopping engine"
cd /tmp/daliuge/daliuge-engine && ./stop_engine.sh
echo "Stopping translator"
cd /tmp/daliuge/daliuge-translator && ./stop_translator.sh
echo "Stopping EAGLE"
cd /tmp/EAGLE && ./stop_eagle.sh dep
echo "Removing code"
rm -rf /tmp/daliuge /tmp/EAGLE
echo "Good-bye!"
