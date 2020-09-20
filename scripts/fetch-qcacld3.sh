#!/bin/bash


# OPTIONS / SETTINGS
CAF_TAG=LA.UM.8.12.r1-14100-sm8250.0






# Adding QCACLD-3 core as a remote repository.
# Use commands below these ones to fetch updates.
git remote add qcacld https://source.codeaurora.org/quic/la/platform/vendor/qcom-opensource/wlan/qcacld-3.0
git fetch $CAF_TAG
git merge -s ours --no-commit FETCH_HEAD --allow-unrelated-histories
git read-tree --prefix=drivers/staging/qcacld-3.0 -u FETCH_HEAD
git commit

# Use this one to fetch updates to existing CAF.
# Remember to check for newer TAGS now and then: https://wiki.codeaurora.org/xwiki/bin/QAEP/release
#git fetch qcacld $CAF_TAG
#git merge -X subtree=drivers/staging/qcacld-3.0 FETCH_HEAD


#
# Adding QCACLD-3 FW-API to remote repository.
#
git remote add fw-api https://source.codeaurora.org/quic/la/platform/vendor/qcom-opensource/wlan/fw-api
git fetch fw-api $CAF_TAG
git merge -s ours --no-commit FETCH_HEAD --allow-unrelated-histories
git read-tree --prefix=drivers/staging/fw-api -u FETCH_HEAD
git commit

#git fetch fw-api $CAF_TAG
#git merge -X subtree=drivers/staging/fw-api FETCH_HEAD

git remote add qca-wifi-host-cmn https://source.codeaurora.org/quic/la/platform/vendor/qcom-opensource/wlan/qca-wifi-host-cmn
git fetch qca-wifi-host-cmn $CAF_TAG
git merge -s ours --no-commit FETCH_HEAD --allow-unrelated-histories
git read-tree --prefix=drivers/staging/qca-wifi-host-cmn -u FETCH_HEAD
git commit

#git fetch qca-wifi-host-cmn $CAF_TAG
#git merge -X subtree=drivers/staging/qca-wifi-host-cmn FETCH_HEAD
