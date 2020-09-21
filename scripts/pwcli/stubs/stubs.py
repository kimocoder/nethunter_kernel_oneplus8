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

import sys
import shutil
import os
import subprocess
import time
import logging
import configparser
import stubslib

# logging
logging.basicConfig()
logger = logging.getLogger('stubs')

# uncomment to get debug logs
#logger.setLevel(logging.DEBUG)

# the toplevel source directory
srcdir = os.environ['SRCDIR']

# the directory where the tests can store temporary data
testdatadir = os.environ['DATADIR']

stubsdir = os.path.join(srcdir, 'stubs')

logger.debug('srcdir=%r' % (srcdir))
logger.debug('testdatadir=%r' % (testdatadir))
logger.debug('stubsdir=%r' % (stubsdir))

# separate port numbers compared torun_stub so that it can be run
# concurrently with tests
PATCHWORK_PORT=8105
SMTP_PORT=5870

class BuilderStub():
    STUB_BUILDER_DIR = '.stub-builder'
    FILE_WARNINGS_COUNT = os.path.join(STUB_BUILDER_DIR, 'warnings_count')
    FILE_RETURN_VALUE = os.path.join(STUB_BUILDER_DIR, 'return_value')

    def __init__(self):
        os.environ['PATH'] = '%s:%s' % ((stubsdir), os.environ['PATH'])

    def cleanup(self):
        if not os.path.exists(self.STUB_BUILDER_DIR):
            return

        shutil.rmtree(self.STUB_BUILDER_DIR)

    def create_builder_dir(self):
        if os.path.exists(self.STUB_BUILDER_DIR):
            if not os.path.isdir(self.STUB_BUILDER_DIR):
                raise Exception('Not a directory: %s' % (self.STUB_BUILDER_DIR))

            # directory already exists
            return

        os.mkdir(self.STUB_BUILDER_DIR)

    def set_warning_count(self, count):
        self.create_builder_dir()

        # raises IOError to the caller if fails
        f = open(self.FILE_WARNINGS_COUNT, 'w')
        f.write('%d' % count)
        f.close()

    def get_warning_count(self):
        if not os.path.exists(self.FILE_WARNINGS_COUNT):
            return 0

        # raises IOError and others to the caller if failures
        f = open(self.FILE_WARNINGS_COUNT, 'r')
        count = int(f.read())
        f.close()

        return count

    def set_return_value(self, value):
        self.create_builder_dir()

        # raises IOError to the caller if fails
        f = open(self.FILE_RETURN_VALUE, 'w')
        f.write('%d' % value)
        f.close()

    def get_return_value(self):
        if not os.path.exists(self.FILE_RETURN_VALUE):
            return 0

        # raises IOError and others to the caller if failures
        f = open(self.FILE_RETURN_VALUE, 'r')
        count = int(f.read())
        f.close()

        return count

class StgStub():
    IMPORT_FAIL = 'import-fail'

    def __init__(self):
        self.gitdir = os.path.join(testdatadir, 'git')
        self.objectsdir = os.path.join(self.gitdir, 'objects')
        self.stgdir = os.path.join(self.gitdir, 'stg')
        self.stgpatchesfile = os.path.join(self.stgdir, 'patches')

        logger.debug('StgStub(): stgdir=%r' % (self.stgdir))

        # create gitdir if it doesn't happen to exist
        if not os.path.exists(self.gitdir):
            os.mkdir(self.gitdir)

        os.mkdir(self.stgdir)
        
        os.environ['STUB_GIT_DATADIR'] = self.gitdir
        os.environ['GIT_DIR'] = 'git'
        os.environ['PATH'] = '%s:%s' % ((stubsdir), os.environ['PATH'])

        self.started = False

    def start(self):
        logger.debug('StgStub.start(): %s' % (os.getcwd()))
        p = subprocess.Popen(['stg', '--version', 'import'], stdout=subprocess.PIPE)
        (stdout, stderr) = p.communicate()

        stg_version = stdout.splitlines()[0]

        if stg_version != b'stub-stg':
            raise Exception('Not running stg-stub: %s' % stg_version)

        self.started = True

    def stop(self):
        if not self.started:
            return

        self.started = False

    def cleanup(self):
        shutil.rmtree(self.stgdir)

        # remove gitdir only if it's empty (which most likely means
        # that this instance created it)
        try:
            os.rmdir(self.gitdir)
        except OSError:
            # the directory was not empty, ignore the error
            pass

    def set_import_failure(self, val):
        gitrepo = stubslib.GitRepository.load(self.gitdir)
        gitrepo.set_stg_import_failure(val)
    
class GitStub():
    def __init__(self, smtpport=SMTP_PORT):
        self.gitdir = os.path.join(testdatadir, 'git')

        logger.debug('GitStub(): gitdir=%r' % (self.gitdir))

        os.mkdir(self.gitdir)
        
        # create the config file
        self.config = configparser.RawConfigParser()
        user = 'user'
        self.config.add_section(user)
        self.config.set(user, 'email', 'test@example.com')
        self.config.set(user, 'name', 'Timo Testi')

        sendemail = 'sendemail'
        self.config.add_section(sendemail)
        self.config.set(sendemail, 'smtpserver', 'localhost')
        self.config.set(sendemail, 'smtpserverport', str(smtpport))

        with open(os.path.join(self.gitdir, 'config'), 'w') as configfile:
            self.config.write(configfile)
        
        
        os.environ['STUB_GIT_DATADIR'] = self.gitdir

        os.environ['GIT_DIR'] = 'git'
        os.environ['PATH'] = '%s:%s' % ((stubsdir), os.environ['PATH'])

        self.started = False

    def start(self):
        logger.debug('GitStub.start(): %s' % (os.getcwd()))
        p = subprocess.Popen(['git', '--version', 'branch'], stdout=subprocess.PIPE)
        (stdout, stderr) = p.communicate()

        git_version = stdout.splitlines()[0]

        if git_version != b'stub-git':
            raise Exception('Not running git-stub: %s' % git_version)

        self.started = True

    def stop(self):
        if not self.started:
            return

        self.started = False

    def cleanup(self):
        shutil.rmtree(self.gitdir)

    def set_commit_failure(self, val):
        gitrepo = stubslib.GitRepository.load(self.gitdir)
        gitrepo.set_commit_failure(val)

    def get_commits_oneline(self, val):
        gitrepo = stubslib.GitRepository.load(self.gitdir)
        return gitrepo.get_commits_oneline(val)
        
class SmtpdStub():

    def __init__(self, port=SMTP_PORT):
        self.smtpddir = os.path.join(testdatadir, 'smtpd')
        self.port = port

        # setup directory for smtpd
        os.mkdir(self.smtpddir)
        os.environ['STUB_SMTPD_DATADIR'] = self.smtpddir

        logger.debug('SmtpdStub(): smtpddir=%r, smtpport=%d' % (self.smtpddir,
                                                                self.port))

        self.started = False

    def start(self):
        # Note: there's a problem that stdout from smtpd output does
        # not go to cmdtest stdout log anymore (after switching away
        # from using the run_stub script). I do not know why it is
        # exactly, maybe something to do how Popen() inherits stdout
        # rules from the running process?
        self.smtpd = subprocess.Popen([os.path.join(stubsdir, 'smtpd'),
                                       '--port=%d' % self.port])

        # wait some time to make sure that the stub started
        time.sleep(0.2)

        if self.smtpd.poll() != None:
            raise Exception('Failed to start smtpd stub: %d' % self.smtpd.returncode)

        self.started = True

    def stop(self):
        if not self.started:
            return

        self.smtpd.terminate()
        self.smtpd.wait()

        self.started = False

    def cleanup(self):
        shutil.rmtree(self.smtpddir)

    def get_mails(self):
        mails = []

        mailfiles = sorted(os.listdir(self.smtpddir))
        logger.debug('SmtpdStub(): mailfiles=%r' % (mailfiles))

        for filename in mailfiles:
            f = open(os.path.join(self.smtpddir, filename), 'r')
            mails.append(f.read())
            f.close()

        return mails

    def get_mails_as_string(self):
        result = ''
        sep = '----------------------------------------------------------------------'
        i = 0

        for mail in self.get_mails():
            result += 'mail %d:\n%s\n%s%s\n' % (i, sep, mail, sep)
            i += 1

        return result

class PatchworkStub():
    def __init__(self, port=PATCHWORK_PORT):
        self.patchesdir = os.path.join(testdatadir, 'patches')
        srcpatchesdir = os.path.join(stubsdir, 'data', 'patches')

        self.port=port

        # create copy of patches
        shutil.copytree(srcpatchesdir, self.patchesdir)
        os.environ['STUB_PATCHWORK_DATADIR'] = self.patchesdir

        logger.debug('PatchworkStub(): patchesdir=%r' % (self.patchesdir))

        self.started = False

    def start(self):
        cmd = [os.path.join(stubsdir, 'patchwork')]
        if self.port:
            cmd += ['--port', str(self.port)]

        self.patchwork = subprocess.Popen(cmd)

        # wait some time to make sure that the stub started
        time.sleep(2)

        if self.patchwork.poll() != None:
            raise Exception('Failed to start patchwork stub: %d' % self.patchwork.returncode)

        self.started = True

    def stop(self):
        if not self.started:
            return

        self.patchwork.terminate()
        self.patchwork.wait()

        self.started = False

    def cleanup(self):
        shutil.rmtree(self.patchesdir)

class EditorStub():
    def __init__(self):
        # add a fake editor until we have a proper stub
        os.environ['EDITOR'] = '/bin/true'

    def start(self):
        pass
    
    def stop(self):
        pass
    
    def cleanup(self):
        pass

class PwcliWrapper():
    def __init__(self, stgit=False, builder='builder', patchworkport=PATCHWORK_PORT,
                 smtpport=SMTP_PORT, signature=None, censor=True):
        self.config = configparser.RawConfigParser()

        self.configpath = os.path.join(testdatadir, 'git/pwcli/config')
        self.dirname = os.path.dirname(self.configpath)
        
        # for some reason ConfigParser reverses the order
        general = 'general'
        self.config.add_section(general)
        self.config.set(general, 'project', 'stub-test')
        self.config.set(general, 'token', 'abcd1234567890')
        self.config.set(general, 'username', 'test')
        self.config.set(general, 'server-url', 'http://localhost:%d/' % (patchworkport))

        # TODO: write few tests for both of these, currently they are
        # not tested in any way
        self.config.set(general, 'automatic-emails', 'true')
        self.config.set(general, 'msgid-tag', 'Link: https://lore.kernel.org/r/%s')

        if builder:
            self.config.set(general, 'build-command', builder)

        if stgit:
            self.config.set(general, 'pending-mode', 'stgit')
            self.config.set(general, 'pending-branch', 'pending')
            self.config.set(general, 'main-branches', 'master')

        self.signature = signature

        if censor:
            os.environ['PWCLI_CENSOR_USER_AGENT'] = '1'
            os.environ['PWCLI_HARDCODE_DATE'] = '2011-02-15T01:00:00'

    def start(self):
        self.pwcli = subprocess.Popen([os.path.join(srcdir, 'pwcli'), '--debug'],
                                      stdin=sys.stdin, stdout=sys.stdout,
                                      stderr=sys.stderr)

    def wait(self):
        self.pwcli.wait()
    
    def stop(self):
        pass
    
    def cleanup(self):
        shutil.rmtree(self.dirname)

    def write_config(self):
        if not os.path.exists(self.dirname):
            os.makedirs(self.dirname)
        elif not os.path.isdir(self.dirname):
            raise Exception('%s exists but is not a directory' % (self.dirname))

        if self.signature:
            f = open(os.path.join(self.dirname, 'signature'), 'w')
            f.write(self.signature)
            f.close()

        with open(self.configpath, 'w') as configfile:
            self.config.write(configfile)
