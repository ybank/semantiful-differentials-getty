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

def __possible_diff_with_preprocessed_diff_html(target, go):
    tfs = fsformat(target)
    ni_hdiff = go + "_getty_inv__" + tfs + "__.inv.diff.html"
    si_hdiff = go + "_getty_inv__" + tfs + "__.inv.si.diff.html"
    ti4o_hdiff = go + "_getty_inv__" + tfs + "__.inv.ti4o.diff.html"
    ti4n_hdiff = go + "_getty_inv__" + tfs + "__.inv.ti4n.diff.html"
    for hd in [ni_hdiff, si_hdiff, ti4o_hdiff, ti4n_hdiff]:
        if os.path.exists(hd):
            with open(hd, 'r') as hdf:
                diff_html = hdf.read()
            if not (diff_html.find("<table") < 0 and diff_html.find("NO DIFFERENCE") >= 0):
                return True
        else:
            print '\n***'
            print '  could not find the preprocessed file: ' + hd
            print '    --> assuming there were no diffs'
            print '***\n'
    return False


def is_possibly_different(target, go, prev_hash, post_hash, preprocessed=False):
    if preprocessed:
        return __possible_diff_with_preprocessed_diff_html(target, go)
    else:
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
