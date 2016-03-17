# prover logic

from tools.daikon import fsformat
from tools.os import from_sys_call_enforce


def can_imply(invs_a, invs_b):
    pass


def is_different(target, go, prev_hash, post_hash):
    prev_invs_file = go + "_getty_inv__" + fsformat(target) + "__" + prev_hash + "_.inv.txt"
    post_invs_file = go + "_getty_inv__" + fsformat(target) + "__" + post_hash + "_.inv.txt"
    difftext = from_sys_call_enforce(" ".join(["git diff", prev_invs_file, post_invs_file]))
    if difftext == "":
        return False
    else:
        return True
