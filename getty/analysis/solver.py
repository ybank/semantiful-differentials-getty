# prover logic

import os

from tools.daikon import fsformat
from tools.os import from_sys_call_enforce


def can_imply(invs_a, invs_b):
    pass


def is_different(target, go, prev_hash, post_hash):
    tfs = fsformat(target)
    prev_invs_file = go + "_getty_inv__" + tfs + "__" + prev_hash + "_.inv.out"
    post_invs_file = go + "_getty_inv__" + tfs + "__" + post_hash + "_.inv.out"
    if (not os.path.exists(prev_invs_file)) or (not os.path.exists(post_invs_file)):
        return True
    difftext = from_sys_call_enforce(" ".join(["git diff", prev_invs_file, post_invs_file]))
    if difftext == "":
        return False
    else:
        return True


def is_possibly_different(target, go, prev_hash, post_hash):
    tfs = fsformat(target)
    osot_invf = go + "_getty_inv__" + tfs + "__" + prev_hash + "_.inv.out"
    nsnt_invf = go + "_getty_inv__" + tfs + "__" + post_hash + "_.inv.out"
    osnt_invf = go + "_getty_inv__" + tfs + "__" + prev_hash + "_" + post_hash + "_.inv.out"
    nsot_invf = go + "_getty_inv__" + tfs + "__" + post_hash + "_" + prev_hash + "_.inv.out"
    all_pairs = [(osot_invf, nsnt_invf), (osnt_invf, nsnt_invf),
                 (osot_invf, osnt_invf), (nsot_invf, nsnt_invf)]
    for fpair in all_pairs:
        if (not os.path.exists(fpair[0])) or (not os.path.exists(fpair[1])):
            return True
        difftext = from_sys_call_enforce(" ".join(["git diff", fpair[0], fpair[1]]))
        if difftext != "":
            return True
    return False

