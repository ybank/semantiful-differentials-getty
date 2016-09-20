# prover logic

import os

from tools.daikon import fsformat
from tools.os import from_sys_call_enforce


def can_imply(invs_a, invs_b):
    pass


def is_different(target, go, prev_hash, post_hash):
    prev_invs_file = go + "_getty_inv__" + fsformat(target) + "__" + prev_hash + "_.inv.out"
    post_invs_file = go + "_getty_inv__" + fsformat(target) + "__" + post_hash + "_.inv.out"
    if (not os.path.exists(prev_invs_file)) or (not os.path.exists(post_invs_file)):
        return True
    difftext = from_sys_call_enforce(" ".join(["git diff", prev_invs_file, post_invs_file]))
    if difftext == "":
        return False
    else:
        return True
