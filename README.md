# rascil_tweaks

[![codecov](https://codecov.io/gh/awicenec/rascil-tweaks/branch/main/graph/badge.svg?token=rascil-tweaks_token_here)](https://codecov.io/gh/awicenec/rascil-tweaks)
[![CI](https://github.com/awicenec/rascil-tweaks/actions/workflows/main.yml/badge.svg)](https://github.com/awicenec/rascil-tweaks/actions/workflows/main.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


rascil_tweaks created by awicenec

## Introduction

This small repo contains a few contributed daliuge functions and scripts in particular to get the SKA ticket https://jira.skatelescope.org/browse/YAN-969 resolved. The functions here are fixing some issues whith a few RASCIL functions and are quite specific. The shell scripts are meant to enable verification of the ticket results.

## Installation

Clone this repo into a directory of your choice.

## Intended Usage

In the root directory of this repo execute the main shell script

```
./yan969.sh
```
This will download, build and run the whole DALiuGE system, including EAGLE and launch a browser tab with the test graph related to YAN-969. Follow the instructions shown on the terminal where the script is being executed. The graph will be executed on the locally running engine. It uses a test data set which is downloaded during the graph execution. The last two components in the graph will report an error, because the generated image is empty and no sky components can be found.

Since the process above does take significant amount of time it is also possible to use the released docker images from dockerHub instead by executing the script

```
./yan969-docker.sh
```

