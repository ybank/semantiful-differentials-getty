#!/usr/bin/env python

import subprocess

# TODO: git rev-parse HEAD

def sys_call(cmd):
    ret = subprocess.call(cmd)
    if ret != 0:
        print "Error in command: " + " ".join(cmd)
        raise SystemExit("system exit: " + str(ret))


