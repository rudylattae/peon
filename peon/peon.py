#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Original By Jeff Winkler, http://jeffwinkler.net
# Got the code at http://jeffwinkler.net/2006/04/27/keeping-your-nose-green/

# Copyright Bernardo Heynemann <heynemann@gmail.com>

# Licensed under the Open Software License ("OSL") v. 3.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.opensource.org/licenses/osl-3.0.php

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import glob
import os
import stat
import time
from os.path import abspath, dirname, join


_checksum = 0


class Urgency(object):
    low = 0
    normal = 1
    critical = 2


def _get_stats_from_filename(filename):
    stats = os.stat(filename)
    return stats[stat.ST_SIZE] + stats[stat.ST_MTIME]


def _get_checksum_from_dir(dirpath, pattern):
    result = 0
    for file in glob.glob(os.path.join(dirpath, pattern)):
        absolute_filename = os.path.abspath(file)
        result += _get_stats_from_filename(absolute_filename)
    return result


def checkSumRecursive(directory, pattern='*.py'):
    result = 0
    for dirpath, dirs, files in os.walk(directory):
        result += _get_checksum_from_dir(dirpath, pattern)
    return result


def something_has_changed(dir):
    global _checksum
    if _checksum == 0:
        _checksum = checkSumRecursive(dir)
    new_checksum = checkSumRecursive(dir)
    if new_checksum != _checksum:
        _checksum = new_checksum
        return True
    return False


def main():
    '''
    Watch for changes in all files indicated by a glob pattern,
    by default it looks for '*.py'.
    If something has changes, run a given command or nosetests.
    '''
    val = 0
    command = " ".join(sys.argv[1:]) or 'nosetests'
    is_build_broken = False

    try:
        while True:
            if something_has_changed('.'):
                os.system('reset')
                status = os.system(command)
                if status != 0:
                    is_build_broken = True
                    notify("Broken build",
                            "Your command of '%s' returned exit"\
                            "code '%s'. Please verify the console output for"\
                            "more info." % (command, status),
                            "stop.png",
                            urgency=Urgency.critical)
                elif is_build_broken:
                    is_build_broken = False
                    notify("Build fixed",
                           "Your build with command '%s' IS FIXED!" % command,
                           "tick.png")

            time.sleep(1)
    except KeyboardInterrupt:
        return


def notify(title, message, image, urgency=Urgency.normal):
    try:
        import pynotify
    except:
        return

    urgencies = {
        Urgency.low: pynotify.URGENCY_LOW,
        Urgency.normal: pynotify.URGENCY_NORMAL,
        Urgency.critical: pynotify.URGENCY_CRITICAL,
    }

    if pynotify.init("Nosy"):
        n = pynotify.Notification(title,
                                  message,
                                  abspath(join(dirname(__file__), image)))
        n.set_urgency(urgencies[urgency])
        n.show()
        time.sleep(2)
        n.close()

if __name__ == '__main__':
    sys.exit(main())
