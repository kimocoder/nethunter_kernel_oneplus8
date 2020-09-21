#!/usr/bin/env python3
#
# Copyright (c) 2016, The Linux Foundation.
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

import pwcli

class TestRunProcess(unittest.TestCase):
    def test_stdout(self):
        msg = 'This is a test\nLine 2'
        p = pwcli.RunProcess(['/bin/echo', '-n', msg])

        self.assertEqual(p.returncode, 0)
        self.assertEqual(p.stdoutdata, msg)
        self.assertEqual(p.stderrdata, '')

    def test_stderr(self):
        # Note: newlines in msg will fail for some reason
        msg = 'This is a test'
        python_cmd = 'import sys; sys.stderr.write("%s")' % (msg)

        p = pwcli.RunProcess(['python3', '-c', python_cmd])

        self.assertEqual(p.returncode, 0)
        self.assertEqual(p.stdoutdata, '')
        self.assertEqual(p.stderrdata, msg)
        
    def test_nonzero_returncode(self):
        value = 177
        python_cmd = 'import sys; sys.exit(%d)' % (value)

        p = pwcli.RunProcess(['python3', '-c', python_cmd])

        self.assertEqual(p.returncode, value)
        self.assertEqual(p.stdoutdata, '')
        self.assertEqual(p.stderrdata, '')

    def test_stdout_cb(self):
        msg = 'Line 1\nLine 2\nLine 3'
        cb_output = []
        cb = lambda line: cb_output.append(line)

        p = pwcli.RunProcess(['/bin/echo', '-n', msg], stdout_cb=cb)

        self.assertEqual(p.returncode, 0)
        self.assertEqual(p.stdoutdata, msg)
        self.assertEqual(p.stderrdata, '')

        # strip newlines for easy comparison
        cb_output = [s.strip() for s in cb_output]

        self.assertEqual(msg.split('\n'), cb_output)

    def test_input(self):
        msg = 'This is a test'
        p = pwcli.RunProcess(['cat'], input=msg)

        self.assertEqual(p.returncode, 0)
        self.assertEqual(p.stdoutdata, msg)
        self.assertEqual(p.stderrdata, '')

    def test_str(self):
        p = pwcli.RunProcess(['/bin/echo', 'foo', 'bar'])
        self.assertEqual(str(p), 'RunProcess(\'/bin/echo foo bar\', None, None)')

    def test_repr(self):
        msg = 'This is a test'

        p = pwcli.RunProcess(['cat'], input=msg)

        self.assertEqual(repr(p),
                         'RunProcess([\'cat\'], None, \'This is a test\')')
                         
if __name__ == '__main__':
    unittest.main()
