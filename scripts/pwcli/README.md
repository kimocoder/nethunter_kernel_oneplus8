# pwcli - a script for applying patches from patchwork and sending summary emails

## Introduction

`pwcli` is script which I wrote to ease my kernel maintainer duties.
It provides a simple readline interface for accessing patches in a
patchwork servers over Patchwork's REST API, uses git to commit the
patches to a local repository and send emails using an SMTP server.
The benefit from the script is that it doesn't matter if you apply one
or hundred patches, it's still the same amount of work for you (unless
there are conflicts, of course).

This still a prototype but it already helps me to avoid tedious manual
work and manage patches faster. All feedback very welcome:

Kalle Valo <kvalo@codeaurora.org>

## Screenshots

Here's an example how I use pwcli to commit a patch:

```
$ pwcli
Connecting to https://patchwork.kernel.org/
User          : kvalo
Project       : linux-wireless
Tree          : wireless-drivers-next
Branch        : master
New           : 26
Review        : 19
Upstream      : 7
Deferred      : 92
Total         : 144
master@wireless-drivers-next > list -s review
 [  1] [v2] ath10k: remove the max_sched_scan_reqs value        2019-11-14 Wen Gong     Under Review     
 [  2] [RESEND] ath11k: add tx hw 802.11 encapusaltion offlo... 2020-01-22 John Crispin Under Review     
 [  3] [v2,2/2] rtw88: Use udelay instead of usleep in atomi... 2020-04-23 Kai-Heng Fen Under Review     
 [  4] ath10k: Avoid override CE5 configuration for QCA99X0.... 2020-04-23 Maharaja Ken Under Review     
 [  5] [1/6] ath9k: fix AR9002 ADC and NF calibrations          2020-04-24 Sergey Ryaza Under Review     
 [  6] [2/6] ath9k: remove needless NFCAL_PENDING flag setting  2020-04-24 Sergey Ryaza Under Review     
 [  7] [3/6] ath9k: do not miss longcal on AR9002               2020-04-24 Sergey Ryaza Under Review     
 [  8] [4/6] ath9k: interleaved NF calibration on AR9002        2020-04-24 Sergey Ryaza Under Review     
 [  9] [5/6] ath9k: invalidate all calibrations at once         2020-04-24 Sergey Ryaza Under Review     
 [ 10] [6/6] ath9k: add calibration timeout for AR9002          2020-04-24 Sergey Ryaza Under Review     
 [ 11] [next] rtw88: fix spelling mistake "fimrware" -> "fir... 2020-04-24 Colin King   Under Review     
 [ 12] rtw88: fix sparse warnings for download firmware routine 2020-04-24 Tony Chuang  Under Review     
 [ 13] carl9170: remove P2P_GO support                          2020-04-25 Christian La Under Review     
 [ 14] ath5k: remove conversion to bool in ath5k_ani_calibra... 2020-04-26 Jason Yan    Under Review     
 [ 15] [v2,1/4] ath10k: enable firmware peer stats info for.... 2020-04-27 Wen Gong     Under Review     
 [ 16] [v2,2/4] ath10k: add rx bitrate report for SDIO          2020-04-27 Wen Gong     Under Review     
 [ 17] [v2,3/4] ath10k: add bitrate parse for peer stats info   2020-04-27 Wen Gong     Under Review     
 [ 18] [v2,4/4] ath10k: correct tx bitrate of iw for SDIO       2020-04-27 Wen Gong     Under Review     
 [ 19] [net-next] ath11k: use GFP_ATOMIC under spin lock        2020-04-27 Wei Yongjun  Under Review     
master@wireless-drivers-next > commit 12
Retrieving patches (1/1)
      rtw88: fix sparse warnings for download firmware routine 2020-04-24 Tony Chuang  Under Review     
------------------------------------------------------------
1 patches
commit All/aBort? a
Committing patches (1/1)
Build successful                                                 
============================================================
1 patches applied:

3d8bf50860c7 rtw88: fix sparse warnings for download firmware routine

Accepted/Under review/Changes requested/Rejected/New/Deferred/Superseded/aWaiting upstream/not aPplicable/rFc/aBort? a
Setting patch state (1/1)
Patch set to Accepted
master@wireless-drivers-next > 
```

At the same pwcli also opened the patchwork page on my browser:

https://patchwork.kernel.org/patch/11507425/ 

There I could check if the patch has received any comments and review
the patch myself. And also after the commit did a build check for me
and after I had accepted the patch it changed the state on the server
and sent a "thank you" email to notify the submitter the patch is
applied:

https://lkml.kernel.org/r/20200428084448.7D63BC433F2@smtp.codeaurora.org

Even though here I just installed one patch, I could do the same for a
patch series. For example, I had wanted to apply the ath9k patchset
with 6 patches I would have just issued:

```
master@wireless-drivers-next > commit 5-10
```

Otherwise the number of patches doesn't make a difference and a
similar email would have been sent as a response to the first patch.

## Installation

pwcli requires python3 and these packages (newer versions should work
but of course you never know):


```
ii  python3              3.5.1-3              interactive high-level object-oriented language
ii  python3-requests     2.9.1-3ubuntu0.1     elegant and simple HTTP library for Python3
ii  git                  1:2.7.4-0ubuntu1.9   fast, scalable, distributed revision control system
ii  diffstat             1.61-1               produces graph of changes introduced by a diff file
```

To install pwcli just to copy the script somewhere in your $PATH:

```
cp pwcli /usr/local/bin/
```

pwcli needs a configuration file in `.git/pwcli/config` in the git
repository you are working on. Here's a simple example using
kernel.org's linux-wireless project just for downloading patches:


```
[general]
server-url = https://patchwork.kernel.org/
project = linux-wireless
```

And here's my config file I use for maintaining kernel trees:

```
[general]
server-url = https://patchwork.kernel.org/
project = linux-wireless
username = edward
token = abcd123456789890
browser = xdg-open
build-command = make -j 8
automatic-emails = true
msgid-tag = Link: https://lore.kernel.org/r/%s
```

For more information about the configuration options see pwcli.conf.

For emails pwcli uses git configuration variables, so you want to make
sure they are correctly set:

```
git config user.name 'Edward Example'
git config user.email 'edward@example.com'
git config sendemail.smtpserver smtp.example.com
git config sendemail.smtpserverport 587
git config sendemail.smtpuser edward
git config sendemail.smtppass 1234567890
git config sendemail.smtpencryption tls
```

## Tests

There are various automatic tests for pwcli, use `run_tests` to run
them all. These are currently run on Ubuntu 16.04 with these packages
(the list might not be complete):

```
ii  cmdtest               0.22-1               blackbox testing of Unix command line programs
ii  python3-mock          1.3.0-2.1ubuntu1     Mocking and Testing Library (Python3 version)
ii  python3-pexpect       4.0.1-1              Python 3 module for automating interactive applications
ii  python3-flask-restful 0.3.4-1              REST API framework for Flask applications
ii  figlet                2.2.5-2              Make large character ASCII banners out of ordinary text
ii  pyflakes3             1.1.0-2              all passive checker of Python 2 and 3 programs
ii  pep8                  1.7.0-2              all Python PEP 8 code style checker
```

## Contributing patches

If you want to send patches please read `CONTRIBUTIONS` file and send
a pull request on https://github.com/kvalo/pwcli.
