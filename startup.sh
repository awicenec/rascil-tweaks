#!/usr/bin/env bash
# Script to startup daliuge containers
# Calling:
#
#   ./startup.sh [daliuge_tag] [eagle_tag] [anything]
#
# if none is provided daliuge_tag = master and eagle_tag
# if a third option is present only the engine is started

set -e

ENGINE_OPTS="\
--shm-size=2g --ipc=shareable \
--rm \
--name daliuge-engine \
-v /var/run/docker.sock:/var/run/docker.sock \
-p 5555:5555 -p 6666:6666 \
-p 8000:8000 -p 8001:8001 \
-p 8002:8002 -p 9000:9000 \
--user $(id -u):$(id -g) \
" 

common_prep ()
{
    mkdir -p ${DLG_ROOT}/workspace
    mkdir -p ${DLG_ROOT}/testdata
    mkdir -p ${DLG_ROOT}/code
    # get current user and group id and prepare passwd and group files
    DOCKER_GID=`python3 -c "from prepareUser import prepareUser; print(prepareUser(DLG_ROOT='${DLG_ROOT}'))"`
    ENGINE_OPTS=${ENGINE_OPTS}" --group-add ${DOCKER_GID}"
    ENGINE_OPTS=${ENGINE_OPTS}" -v ${DLG_ROOT}/workspace/settings/passwd:/etc/passwd"
    ENGINE_OPTS=${ENGINE_OPTS}" -v ${DLG_ROOT}/workspace/settings/group:/etc/group"
    ENGINE_OPTS=${ENGINE_OPTS}" -v ${DLG_ROOT}:${DLG_ROOT} --env DLG_ROOT=${DLG_ROOT}"
}

get_docker_tag ()
{
    IMAGE=$1
    TEST=`curl -s --unix-socket /var/run/docker.sock http:/localhost/v1.41/images/json \
    | jq -r '.[]|.RepoTags|map(select(.| contains("'"${IMAGE}"'")))|.[]|split(":")[1]\
    |select(.=="'"${2}"'")'`
    #echo "params" "input: ${1} ${2}" $TEST ${IMAGE}:${TAG}
    if [[ ! "$TEST" && "$2" -ne "master" ]] # master is never in repo
    then
        docker pull ${IMAGE}:${2}
    fi
    echo $2
}

# start engine
export DLG_ROOT="$HOME/dlg" # for this we are always using user's HOME
# get prepareUser script and templates
curl -so prepareUser.py https://raw.githubusercontent.com/ICRAR/daliuge/master/daliuge-engine/dlg/prepareUser.py
curl -so passwd.template https://raw.githubusercontent.com/ICRAR/daliuge/master/daliuge-engine/dlg/passwd.template
curl -so group.template https://raw.githubusercontent.com/ICRAR/daliuge/master/daliuge-engine/dlg/group.template

if [ ! $1 ] 
then 
    DLG_TAG="master"
else
    DLG_TAG=`get_docker_tag "icrar/daliuge-engine" ${1}`
fi
common_prep
echo "Running Engine:${DLG_TAG} in background..."
echo "docker run -td ${ENGINE_OPTS}  icrar/daliuge-engine:${DLG_TAG}"
docker run -td ${ENGINE_OPTS}  icrar/daliuge-engine:${DLG_TAG}
sleep 3
# start_local_managers.sh
curl -d '{"nodes": ["localhost"]}' -H "Content-Type: application/json" -X POST http://localhost:9000/managers/island/start

[ $3 ] && exit  # if there is a third command line option we stop here

# start translator
# we assume using the same tag
echo
echo "Running Translator:${DLG_TAG} in background..."
docker run --name daliuge-translator --rm -td -p 8084:8084 icrar/daliuge-translator:${DLG_TAG}

# start EAGLE
if [ ! $2 ]
then
    EAGLE_TAG="master"
else
    EAGLE_TAG=`get_docker_tag "icrar/eagle" $2`
fi
echo
echo "Running EAGLE:${EAGLE_TAG} in background..."
docker run -d --name eagle-dep --rm -p 8888:80/tcp icrar/eagle:${EAGLE_TAG}
# sleep 5
# python -m webbrowser http://localhost:8888
