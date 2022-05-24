#!/bin/env bash
# script builds all of daliuge and EAGLE, installs rascil and the rascil-tweaks
# (including a minimal rascil-data directory) and starts EAGLE with the YAN-970
# test-graph loaded.

function get_latest_tag {
    tmpfile=$(mktemp /tmp/yan969-docker.XXXXXX)
    echo $1
    TAG=`curl -sX GET "https://hub.docker.com/v2/repositories/icrar/${1}/tags" | jq -r '.results | max_by(.last_updated) | .name'`
    echo ${TAG} ${tmpfile};
}

PROJECT="daliuge-engine"
cd /tmp
python3 -m venv venv
source venv/bin/activate
if ! command -v jq &> /dev/null
then
    echo "jq could not be found. Proceeding with hard-coded tags"
    ENGINE_TAG="2.3.0"
    TRANSLATOR_TAG="2.3.0"
    EAGLE_TAG="4.3.0"
else
    PROJECT="daliuge-engine"
    ENGINE_TAG=`curl -sX GET "https://hub.docker.com/v2/repositories/icrar/${PROJECT}/tags" | jq -r '.results | max_by(.last_updated) | .name'`
    echo "ENGINE_TAG: ${ENGINE_TAG}"
    PROJECT="daliuge-translator"
    TRANSLATOR_TAG=`curl -sX GET "https://hub.docker.com/v2/repositories/icrar/${PROJECT}/tags" | jq -r '.results | max_by(.last_updated) | .name'`
    echo "TRANSLATOR_TAG: $TRANSLATOR_TAG"
    PROJECT="eagle"
    EAGLE_TAG=`curl -sX GET "https://hub.docker.com/v2/repositories/icrar/${PROJECT}/tags" | jq -r '.results | max_by(.last_updated) | .name'`
    echo "EAGLE_TAG: ${EAGLE_TAG}"
fi
docker pull icrar/daliuge-engine:${ENGINE_TAG}
docker pull icrar/daliuge-translator:${TRANSLATOR_TAG}
docker pull icrar/eagle:${EAGLE_TAG}
cd $OLDPWD
if [ ! command -v startup.sh &> /dev/null ]
then
    echo "startup.sh not found or not executable"
    exit
else
    ./startup.sh $ENGINE_TAG $EAGLE_TAG
fi

if [ ! $1 ]
then
    # additional rascil-tweaks installations requires git
    docker exec -u root -ti daliuge-engine bash -c "apt -y install git"
    # install RASCIL into engine
    docker exec -u root -t daliuge-engine bash -c "pip install --prefix ~/dlg/code --extra-index-url https://artefact.skao.int/repository/pypi-internal/simple rascil==0.6.0"
    # install rascil-tweaks from github (additional functions and fixes)
    docker exec -u root -t daliuge-engine bash -c "pip install --prefix ~/dlg/code/lib/python3.8/site-packages git+https://github.com/awicenec/rascil-tweaks.git"
    # restart engine to enable imports of additional packages
fi
docker stop daliuge-engine
sleep 3 # else the cleanup has not finished
./startup.sh $ENGINE_TAG $EAGLE_TAG engine
# open web-browser with correct graph loaded
python3 -m webbrowser "http://localhost:8888/?service=GitHub&repository=ICRAR/EAGLE-graph-repo&branch=master&path=SDP%20Pipelines&filename=cont_img_YAN-970-sub-sub.graph"
./instructions.sh
./cleanup.sh
