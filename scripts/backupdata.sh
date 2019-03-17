#!/usr/bin/env bash
rm -rf ${BASH_SOURCE%/*}/../backup/*; cp -r ${BASH_SOURCE%/*}/../data/* backup
