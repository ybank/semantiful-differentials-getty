#!/usr/bin/env python

import ast
import subprocess

# TODO: git rev-parse HEAD

def sys_call(cmd):
    ret = subprocess.call(cmd.split(" "))
    if ret != 0:
        print "Error in command: " + cmd
        raise SystemExit("system exit: " + str(ret))

def read_str_from(file_path):
    with open(file_path, 'r') as file:
        str_ds = file.read()
    return ast.literal_eval(str_ds)


