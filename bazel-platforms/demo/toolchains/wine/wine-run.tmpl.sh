#!/usr/bin/env bash

ls -lisa
echo 'Running - {ARGS}'
WINEPREFIX="$(realpath '{WINEPREFIX}')" xvfb-run wine {ARGS}