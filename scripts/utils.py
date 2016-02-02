import ast
import re
import subprocess


# system calls

def sys_call(cmd, ignore_bad_exit=False):
    ret = subprocess.call(cmd, shell=True)
    if ret != 0:
        print "\n-- << non-zero exit status code >> --"
        if ignore_bad_exit:
            print "Exit from command: \n\t" + cmd
            print "But we can safely ignore such non-zero exit status code this time.\n"
        else:
            print "Error in command: \n\t" + cmd + "\n"
            raise SystemExit("system exit: " + str(ret))


def from_sys_call(cmd):
    return subprocess.check_output(cmd, shell=True)


# maven calls

# FIXME: does not support multi-module project
def path_from_mvn_call(env):
    if env not in ["sourceDirectory", "scriptSourceDirectory", "testSourceDirectory", 
                   "outputDirectory", "testOutputDirectory", "directory"]:
        raise ValueError("incorrect env var: " + env)
    mvn_cmd = "mvn help:evaluate -Dexpression=project.build." + env + " | grep ^/"
    return subprocess.check_output(mvn_cmd, shell=True).strip()


# IMPROVE: supported multi-module project, but make it module-specific when needed
def classpath_from_mvn_call():
    mvn_cmd = "mvn dependency:build-classpath | grep ^\/"
    output = subprocess.check_output(mvn_cmd, shell=True).strip()
    all_paths = []
    classpaths = output.split("\n")
    for clspt in classpaths:
        classpath = clspt.strip()
        for one_path in classpath.split(":"):
            if one_path not in all_paths:
                all_paths.append(one_path)
    merged = "."
    for path in all_paths:
        merged += (":" + path)
    return merged


# without considering target folders
def full_env_classpath():
    return classpath_from_mvn_call() + ":$CLASSPATH"


# include target folders
def full_classpath(bin_output, test_output):
    return full_env_classpath() + ":" + bin_output + ":" + test_output


# exchange parser

def read_str_from(file_path):
    with open(file_path, 'r') as file:
        str_ds = file.read()
    return ast.literal_eval(str_ds)


# git calls

def get_parent_hash():
    two_hash_str = from_sys_call("git rev-list --max-count=2 --first-parent --topo-order HEAD").strip()
    current, parent = two_hash_str.split("\n")
    verify_parent = from_sys_call("git rev-parse HEAD^").strip()
    if parent == verify_parent:
        return parent
    else:
        raise ValueError(
            "parent commit hash disagree, rev-list-first-parent-topo-order vs. HEAD^: {0} vs {1}".\
            format(parent, verify_parent))


def get_current_head_branch():
    branches_str = from_sys_call("git branch --list").strip()
    branches_unpolished = branches_str.split("\n")
    for branch_unpolished in branches_unpolished:
        branch_raw = branch_unpolished.strip()
        if branch_raw[0] == "*":
            m = re.compile("^\* \(detached from ([a-z0-9]{5,})\)$").match(branch_raw)
            if m:
                return m.group(1)
            b = re.compile("^\* ([a-zA-Z0-9\-_]+)$").match(branch_raw)
            if b:
                return b.group(1)
            raise ValueError("unhandled branch name: " + branch_raw[2:].strip())
    raise EnvironmentError("no current head branch is listed")


# use with restore_and_pop_last, with care
def backup_and_stash_first():
    sys_call("git reset HEAD .")
    resp = from_sys_call("git stash save --keep-index --include-untracked").strip()
    if resp == "No local changes to save":
        return False
    else:
        return True


# use with backup_and_stash_first, with care
# should_further_recover is the return value of backup_and_stash_first
def restore_and_pop_last(head_branch, should_further_recover):
    sys_call("git checkout " + head_branch)
    if should_further_recover:
        sys_call("git stash pop", ignore_bad_exit=True)


def clear_temp_checkout(current_commit):
    sys_call("git reset --hard " + current_commit)
    resp = from_sys_call("git stash save --keep-index --include-untracked").strip()
    if resp != "No local changes to save":
        sys_call("git stash drop")
