#!/usr/bin/env bash
rm -rf ${BASH_SOURCE%/*}/../data/*; cp -r ${BASH_SOURCE%/*}/../backup/* data
