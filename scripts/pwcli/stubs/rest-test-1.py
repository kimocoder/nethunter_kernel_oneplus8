#!/usr/bin/env python3
#
# Copyright (c) 2020, The Linux Foundation.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#


import json
import requests
import argparse
import os

SERVER_URL = 'https://patchwork.kernel.org/api/1.1'

USERNAME = 'kvalo'
PROJECT = 'linux-wireless'

# set patchwork token in PATCHWORK_TOKEN enviroment variable, but most
# of the commands will work without the token anyway

def get_auth_headers():
    headers = {}

    # if only set the token
    if 'PATCHWORK_TOKEN' in os.environ:
        headers['Authorization'] = 'Token %s' % (os.environ['PATCHWORK_TOKEN'])

    return headers

# state names listed in patchwork/fixtures/default_states.xml

def rest_get(args, url, params=None):
    if not url.startswith(SERVER_URL):
        url = '%s%s' % (SERVER_URL, url)

    r = requests.get(url, headers=get_auth_headers(), params=params)

    if args.dump:
        print('----------------------------------------------------------------------')
        print('%s:' % url)
        print(json.dumps(r.json(), indent=2))
        print('----------------------------------------------------------------------')

    r.raise_for_status()

    return r

def rest_patch(args, url, json):
    if not url.startswith(SERVER_URL):
        url = '%s%s' % (SERVER_URL, url)

    headers = get_auth_headers()
    headers['Content-Type'] = 'application/json'
    r = requests.patch(url, json=json, headers=headers)

    if args.dump:
        print('----------------------------------------------------------------------')
        print('%s:' % url)
        print(json.dumps(r.json(), indent=2))
        print('----------------------------------------------------------------------')

    r.raise_for_status()

    return r

def cmd_root(args):
    rest_get(args, '/')

def cmd_patch1(args):
    # Formatting: remove leading space
    r = rest_get(args, '/patches/11484825/')
    j = r.json()
    print(type(j['submitter']['name']))

    # Weird, this print causes an exception with --dump:
    #
    # $ ./rest-test-1.py --dump patch1 1>/dev/null
    # Traceback (most recent call last):
    #   File "./rest-test-1.py", line 111, in <module>
    #     main()
    #   File "./rest-test-1.py", line 108, in main
    #     args.func(args)
    #   File "./rest-test-1.py", line 45, in cmd_patch1
    #     print(j['submitter']['name'])
    # UnicodeEncodeError: 'ascii' codec can't encode character u'\xc9' in position 9: ordinal not in range(128)
    #
    # Also like this:
    #
    # $ ./rest-test-1.py patch1 1>/dev/null
    # Traceback (most recent call last):
    #   File "./rest-test-1.py", line 119, in <module>
    #     main()
    #   File "./rest-test-1.py", line 116, in main
    #     args.func(args)
    #   File "./rest-test-1.py", line 53, in cmd_patch1
    #     print(j['submitter']['name'])
    # UnicodeEncodeError: 'ascii' codec can't encode character u'\xc9' in position 9: ordinal not in range(128)
    print(j['submitter']['name'])

    rest_get(args, '/patches/11484825/comments/')

def cmd_patch2(args):
    # rtw88: add support for 802.11n RTL8723DE devices
    r = rest_get(args, '/patches/11494413/')
    j = r.json()
    print(j['submitter']['name'], type(j['submitter']['name']))

    rest_get(args, '/series/272629/')
    rest_get(args, '/covers/11494407/')
    rest_get(args, '/covers/11494407/comments/')

def cmd_auth1(args):
    pass

def cmd_users1(args):
    rest_get(args, '/users/?q=kvalo')

def cmd_patches1(args):
    r = rest_get(args, '/patches/', { 'project' : PROJECT,
                                      'delegate' : USERNAME,
                                      'state' : [ 'new', 'under-review' ] })
    j = r.json()
    print('%s patches' % (len(j)))

    for patch in j:
        print(patch['submitter']['name'], patch['name'], patch['state'],
              patch['date'])

def cmd_patches2(args):
    r = rest_get(args, '/patches/', { 'project' : PROJECT,
                                      'delegate' : USERNAME,
                                      'state' : 'deferred' })
    while True:
        j = r.json()
        print('%s patches' % (len(j)))

        if 'next' not in r.links:
            # no more pages
            break

        r = rest_get(args, r.links['next']['url'])

def cmd_events1(args):
    r = rest_get(args, '/events/', { 'patch': '11484825' } )
    j = r.json()

    for event in j:
        print(event['category'], event['date'])

def cmd_set_state1(args):
    # [v2] ath10k: add retry mechanism for ath10k_start
    r = rest_patch(args, '/patches/11340881/', { 'state': 'new' })
    j = r.json()
    print(j['name'], j['state'], j['delegate']['username'])

def cmd_set_delegate1(args):
    # kvalo's id is 25621
    r = rest_patch(args, '/patches/11340881/', { 'delegate': 25621 })
    j = r.json()
    print(j['name'], j['state'], j['delegate']['username'])

def cmd_mbox1(args):
    # rtw88: add support for 802.11n RTL8723DE devices
    r = rest_get(args, '/patches/11494413/')
    j = r.json()
    print(j['mbox'])

    r = requests.get(j['mbox'], headers=get_auth_headers())
    print(r.text)

def cmd_tags1(args):
    # [v2,06/18] mt76: add mac80211 driver for MT7915 PCIe-based chipsets
    r = rest_get(args, '/patches/11489259/')
    j = r.json()
    print('%s: tags %r' % (j['name'], j['tags']))
    print(j['content'])

def cmd_series1(args):
    r = rest_get(args, '/series/', { 'project' : PROJECT })
    j = r.json()
    print('%s series' % (len(j)))

    for series in j:
        print(series['submitter']['name'], series['name'], series['date'],
              '%d patches' % len(series['patches']))

def cmd_series2(args):
    # [PATCHv2,1/4] ath10k: Add wmi command support for station specific TID config
    r = rest_get(args, '/patches/11643791/')
    patch = r.json()

    # note: for some reason series is an array, just use the first one
    # and ignore the rest
    print(patch['series'][0]['id'], patch['series'][0]['name'])

    # fetch the full series
    r = rest_get(args, '/series/%d/' % (patch['series'][0]['id']))
    series = r.json()

    print(series['cover_letter']['id'], series['cover_letter']['web_url'])

def cmd_utf1(args):
    # carl9170: remove P2P_GO support
    r = rest_get(args, '/patches/11509803/')
    j = r.json()
    print(j['mbox'])

    r = requests.get(j['mbox'], headers=get_auth_headers())
    print(r.encoding)
    r.encoding = 'utf-8'
    text = r.text
    print(type(text))

    s = []
    for l in text.splitlines():
        s.append(ascii(l))
        if l.startswith('Reported-by:'):
            print(type(l))
            print(l)
            print(ascii(l))

    #print('\n'.join(s))

def cmd_pull1(args):
    r = rest_get(args, '/patches/11507893/')
    j = r.json()
    print(repr(j['pull_url']))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dump', action='store_true')

    subparsers = parser.add_subparsers()
    subparsers.add_parser('root').set_defaults(func=cmd_root)
    subparsers.add_parser('patch1').set_defaults(func=cmd_patch1)
    subparsers.add_parser('patch2').set_defaults(func=cmd_patch2)
    subparsers.add_parser('auth1').set_defaults(func=cmd_auth1)
    subparsers.add_parser('users1').set_defaults(func=cmd_users1)
    subparsers.add_parser('patches1').set_defaults(func=cmd_patches1)
    subparsers.add_parser('patches2').set_defaults(func=cmd_patches2)
    subparsers.add_parser('events1').set_defaults(func=cmd_events1)
    subparsers.add_parser('set-state1').set_defaults(func=cmd_set_state1)
    subparsers.add_parser('set-delegate1').set_defaults(func=cmd_set_delegate1)
    subparsers.add_parser('mbox1').set_defaults(func=cmd_mbox1)
    subparsers.add_parser('tags1').set_defaults(func=cmd_tags1)
    subparsers.add_parser('series1').set_defaults(func=cmd_series1)
    subparsers.add_parser('series2').set_defaults(func=cmd_series2)
    subparsers.add_parser('utf1').set_defaults(func=cmd_utf1)
    subparsers.add_parser('pull1').set_defaults(func=cmd_pull1)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
