#!/usr/bin/env bash


WINEPREFIX="$(realpath '{WINEPREFIX}')" xvfb-run wine {ARGS}