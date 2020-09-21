
### NetHunter kernel for OnePlus 8 / 8 Pro

## What's supported?
There is a bunch of USB adapters (BT/WIFI/SDR/DVB) added, so below is just a highlight.
```sh
* rtl8812au (v5.6.4.2) from aircrack-ng added
* rtl8188eus (v5.3.9) from aircrack-ng added
* WiFi injection patches added.
* Supports monitor mode on internal WiFi SoC
* CDROM emulation supported (drivedroid)
* AirSpy / HackRF (RTL-SDR) supported
* Bluetooth (RFCOMM) support added.
* NTFS read/write
```

## Howto compile/build?
```sh

 * First be sure you have buildtools (standard Android kernel build tools) installed.
   $ apt-get install bison gawk bc ccache device-tree-compiler libssl-dev python3


 $ git clone https://github.com/kimocoder/nethunter_kernel_oneplus8 -b nethunter-10.0
 $ cd nethunter_kernel_oneplus8/
 $ ./build.sh
```

## Simple scripts to manage patches
```sh

 I have included a set of different scripts to manage imports from 'linux-stable',
 CodeAurora (Qualcomm (CAF) and Patchwork.

 Planning to merge latest drivers/patches from linux-stable? do;

 $ ./scripts/linux-stable.sh


 Planning to pull patches (cherry pick) from Patchwork? do;

 $ ./scripts/pwclient


 Keep your WiFi driver (QCACLD-3) up to date the simple way? do;
 $ ./scripts/qcacld3-setup.sh

 BUT AFTER SETTING THIS UP IN .GIT/CONFIG (REMOTE REPO)
 you will have to use this update scripts in the future;

 $ ./scripts/qcacld3-update.sh
```


-- kimocoder

