#!/bin/env bash
# script builds all of daliuge and EAGLE, installs rascil and the rascil-tweaks
# (including a minimal rascil-data directory) and starts EAGLE with the YAN-970
# test-graph loaded.
alias python=python3

cd /tmp
python3 -m venv venv
source venv/bin/activate
# clone the DALiuGE repo
git clone https://github.com/ICRAR/daliuge
# build common
cd daliuge/daliuge-common && ./build_common.sh dep
# build and start engine dev version with correct common
cd ../daliuge-engine && ./build_engine.sh dev 1.0.0 && ./run_engine.sh dev
# build and start translator dep version
cd ../daliuge-translator && ./build_translator.sh dep && ./run_translator.sh dep
# clone EAGLE repo; build and run
cd /tmp && git clone https://github.com/ICRAR/EAGLE
cd EAGLE && ./build_eagle.sh dep
/tmp/EAGLE/run_eagle.sh dep
cd /tmp
# additional rascil-tweaks installations requires git
docker exec -u root -ti daliuge-engine bash -c "apt -y install git"
# install RASCIL into engine
docker exec -u root -t daliuge-engine bash -c "pip install --prefix ~/dlg/code --extra-index-url https://artefact.skao.int/repository/pypi-internal/simple rascil==0.6.0"
# install rascil-tweaks from github (additional functions and fixes)
docker exec -u root -t daliuge-engine bash -c "pip install --prefix ~/dlg/code/lib/python3.8/site-packages git+https://github.com/awicenec/rascil-tweaks.git"
# restart engine to enable imports of additional packages
cd /tmp/daliuge/daliuge-engine
./stop_engine.sh
./run_engine.sh dev
# open web-browser with correct graph loaded
python3 -m webbrowser "http://localhost:8888/?service=GitHub&repository=ICRAR/EAGLE-graph-repo&branch=master&path=SDP%20Pipelines&filename=cont_img_YAN-970-sub-sub.graph"
./instructions.sh
./cleanup.sh


