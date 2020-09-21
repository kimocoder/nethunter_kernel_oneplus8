#!/bin/bash
#
#
#
# QCACLD-3 CAF TAG FETCHER
# a small script for Android kernels: by kimocoder
#
#
#
# FIND LATEST CAF/TAGS AT
# Remember to check for newer TAGS now and then: https://wiki.codeaurora.org/xwiki/bin/QAEP/release
#
#



# OPTIONS / SETTINGS
CAF_TAG=LA.UM.8.12.r1-14100-sm8250.0





git fetch qcacld $CAF_TAG
git merge -X subtree=drivers/staging/qcacld-3.0 FETCH_HEAD

git fetch fw-api $CAF_TAG
git merge -X subtree=drivers/staging/fw-api FETCH_HEAD

git fetch qca-wifi-host-cmn $CAF_TAG
git merge -X subtree=drivers/staging/qca-wifi-host-cmn FETCH_HEAD
