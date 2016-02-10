# git calls

import re

from tools.os import from_sys_call, sys_call


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