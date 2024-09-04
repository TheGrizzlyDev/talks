#!/usr/bin/env bash

ls -lisa
WINEPREFIX="$(realpath '{WINEPREFIX}')" xvfb-run wine {ARGS}