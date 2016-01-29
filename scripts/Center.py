#!/usr/bin/env python

import ast
import subprocess
import sys

from sets import Set

# TODO: git rev-parse HEAD

def sys_call(cmd):
    ret = subprocess.call(cmd, shell=True)
    if ret != 0:
        print "Error in command: " + cmd
        raise SystemExit("system exit: " + str(ret))

def from_sys_call(cmd):
    return subprocess.check_output(cmd, shell=True)

def path_from_mvn_call(env):
    if env not in ["sourceDirectory", "scriptSourceDirectory", "testSourceDirectory", 
                   "outputDirectory", "testOutputDirectory", "directory"]:
        raise ValueError("incorrect env var: " + env)
    mvn_cmd = "mvn help:evaluate -Dexpression=project.build." + env + " | grep ^/"
    return subprocess.check_output(mvn_cmd, shell=True).strip()

def read_str_from(file_path):
    with open(file_path, 'r') as file:
        str_ds = file.read()
    return ast.literal_eval(str_ds)


#### script ####

print("\n*************************************************************");
print("Getty Center: Semantiful Differential Analyzer");
print("*************************************************************\n");

villa_path = "/Users/yanyan/Projects/research/eclipse/Getty/bin/Getty.Villa.jar"

if len(sys.argv) == 1:
    rbs = from_sys_call("git branch -r").strip()
    all_remote_branches = Set()
    for rb in rbs.split("\n"):
        rb = rb.strip().split(" ")[0]
        all_remote_branches.add(rb)
    if "origin/HEAD" in all_remote_branches:
        remote_head = "origin/HEAD"
    elif "origin/master" in all_remote_branches:
        remote_head = "origin/master"
    elif "origin/trunk" in all_remote_branches:
        remote_head = "origin/trunk"
    else:
        raise ValueError("expecting remote branches to contain HEAD, master, or trunk")
    prev_hash = from_sys_call("git rev-parse " + remote_head).strip()
    post_hash = from_sys_call("git rev-parse HEAD").strip()
elif len(sys.argv) == 2:
    prev_hash = sys.argv[1]
    post_hash = from_sys_call("git rev-parse HEAD")
elif len(sys.argv) == 3:
    prev_hash = sys.argv[1]
    post_hash = sys.argv[2]
else:
    raise ValueError("number of arguments should be 0, 1, or 2")
# consider using `git rev-parse --short HEAD` if shorter names are preferred

# print prev_hash
# print post_hash

pwd = from_sys_call("pwd").strip() + "/"
print "current working directory: " + pwd + "\n"

src_path = path_from_mvn_call("sourceDirectory")
bin_path = path_from_mvn_call("outputDirectory")
test_src_rel_path = path_from_mvn_call("testSourceDirectory")
if test_src_rel_path.startswith(pwd):
    test_src_rel_path = test_src_rel_path[len(pwd):]
else:
    raise ValueError("pwd is not a prefix of test src path")
print "current test src path (relative): " + test_src_rel_path + "\n"
# pkg_prefix = "-"
pkg_prefix = "org.apache.commons"

diff_out = "/tmp/bcel.diff"
sys_call("git diff {0} {1} > {2}".format(prev_hash, post_hash, diff_out))

sys_call("mvn test")

run_villa = "java -jar {0} -s {1} {2} {3} {4} {5} {6}".format(villa_path, 
                                                              diff_out, bin_path, test_src_rel_path, 
                                                              pkg_prefix, prev_hash, post_hash)
print "\n\nstart to run Villa ... \n" + run_villa
sys_call(run_villa)

changed_methods = read_str_from("/tmp/getty/_getty_chgmtd_src_new_{1}_.ex".format(prev_hash, post_hash))
all_callers = read_str_from("/tmp/getty/_getty_clr_{0}_.ex".format(post_hash))
all_cccs = read_str_from("/tmp/getty/_getty_ccc_{0}_.ex".format(post_hash))
all_methods = read_str_from("/tmp/getty/_getty_allmtd_src_{0}_.ex".format(post_hash))

print changed_methods
print all_callers
print all_cccs
print all_methods
