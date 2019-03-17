#!/usr/bin/env bash
conda env export --no-builds -f ${BASH_SOURCE%/*}/../environment.yml
