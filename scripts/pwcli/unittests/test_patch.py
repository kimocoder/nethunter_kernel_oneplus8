#!/usr/bin/env python3
#
# Copyright (c) 2015, The Linux Foundation.
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

import unittest
import mock
import email
import re

import pwcli

FAKE_ATTRIBUTES = {
    'id': '11',
    'web_url': 'http://www.example.com/',
    'msgid': '12345678',
    'date': '2020-04-23T15:06:27',
    'name': 'nnnn',
    'commit_ref': '12345678',
    'state' : 'ssss',
    'submitter': {'name': 'Ed Example',
                   'email': 'ed@example.com'},
    'delegate': {'username': 'dddd'},
    'mbox': 'http://www.example.com',
    'series': [],
    'pull_url': None,
}

TEST_MBOX = 'Content-Type: text/plain; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\nSubject: [1/7] foo\nFrom: Dino Dinosaurus <dino@example.com>\nX-Patchwork-Id: 12345\nMessage-Id: <11111@example.com>\nTo: list@example.com\nDate: Thu,  10 Feb 2011 15:23:31 +0300\n\nFoo commit log. Ignore this text\n\nSigned-off-by: Dino Dinosaurus <dino@example.com>\n\n---\nFIXME: add the patch here\n'

class TestPatch(unittest.TestCase):
    @mock.patch('pwcli.PWCLI')
    def test_attributes(self, pw):
        attributes = FAKE_ATTRIBUTES
        patch = pwcli.Patch(pw)
        patch.parse_json(attributes)

        self.assertEqual(patch.get_name(), attributes['name'])
        self.assertEqual(patch.get_id(), attributes['id'])
        self.assertEqual(patch.get_delegate(), attributes['delegate']['username'])
        self.assertEqual(patch.get_state_name(), attributes['state'])

        pw.get_state_id = mock.Mock(return_value='7777')
        patch.set_state_name('accepted')
        self.assertEqual(patch.get_state_name(), 'accepted')

    def test_reply_msg(self):
        patch = pwcli.Patch(None)
        patch.parse_json(FAKE_ATTRIBUTES)

        patch.get_email = mock.Mock(return_value=email.message_from_string(TEST_MBOX))
        patch.get_url = mock.Mock(return_value='http://localhost:8000/1001/')

        from_name = 'Matt Edmond'
        from_email = 'me@example.com'
        reply = patch.get_reply_msg(from_name, from_email)

        self.assertEqual(reply['From'], '%s <%s>' % (from_name, from_email))
        self.assertEqual(reply['To'], 'Dino Dinosaurus <dino@example.com>')

        # make sure that our email is not in CC
        self.assertIn('Cc', reply)
        self.assertEqual(reply['Cc'].count(from_email), 0)

        self.assertEqual(reply['Subject'], 'Re: [1/7] foo')

    def test_get_mbox_for_stgit(self):
        attributes = FAKE_ATTRIBUTES
        patch = pwcli.Patch(None)
        patch.parse_json(attributes)

        patch.get_mbox = mock.Mock(return_value=TEST_MBOX)

        mbox = patch.get_mbox_for_stgit()
        msg = email.message_from_string(mbox)

        # Check that the first line matches mbox format
        #
        # It would be nice to mock datetime.datetime so that we would
        # not have to skip the date from the first line but I didn't
        # figure out how to do that, without a library like freezegun.
        firstline = mbox.splitlines()[0]
        self.assertTrue(firstline.startswith('From nobody '))

        self.assertEqual(msg['Subject'], 'foo')

        # check that Patchwork-Id is set
        id_line = r'\nPatchwork-Id: %s\n' % (attributes['id'])
        search = re.search(id_line, msg.get_payload())
        self.assertTrue(search != None)

    def test_clean_subject(self):
        patch = pwcli.Patch(None)

        c = patch.clean_subject

        self.assertEqual(c('[] One two three four'), 'One two three four')
        self.assertEqual(c('[1/100] One two three four'), 'One two three four')
        self.assertEqual(c('[PATCH 1/100] One two three four'),
                         'One two three four')
        self.assertEqual(c('[PATCH RFC 14/14] foo: bar koo'), 'foo: bar koo')
        self.assertEqual(c('[RFC] [PATCH 14/99]   foo: bar koo'), 'foo: bar koo')
        self.assertEqual(c('bar: use array[]'), 'bar: use array[]')
        self.assertEqual(c('[PATCH] bar: use array[]'), 'bar: use array[]')
        self.assertEqual(c('[] [A] [B] [   PATCH 1/100000  ] bar: use [] in array[]'),
                         'bar: use [] in array[]')

    def test_get_patch_index(self):
        patch = pwcli.Patch(None)

        # mock get_name() method for easier testing
        m = mock.Mock()
        patch.get_name_original = m

        m.return_value = 'foo: bar'
        self.assertEqual(patch.get_patch_index(), None)

        m.return_value = '[1/2] foo: bar'
        self.assertEqual(patch.get_patch_index(), 1)

        m.return_value = '[99/200] foo: bar'
        self.assertEqual(patch.get_patch_index(), 99)

        m.return_value = '[for-3.4 200/200] foo: bar'
        self.assertEqual(patch.get_patch_index(), 200)

    def test_get_tags(self):
        patch = pwcli.Patch(None)

        # mock get_name() method for easier testing
        m = mock.Mock()
        patch.get_name_original = m

        m.return_value = 'foo: bar'
        self.assertEqual(patch.get_tags(), None)

        m.return_value = '[v2] foo: bar'
        self.assertEqual(patch.get_tags(), '[v2]')

        m.return_value = '[2/2] foo: bar'
        self.assertEqual(patch.get_tags(), '[2/2]')

        m.return_value = '[RFC,7/9] foo: bar'
        self.assertEqual(patch.get_tags(), '[RFC,7/9]')

if __name__ == '__main__':
    unittest.main()
