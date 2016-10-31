# get interested runtime targets

import re
from copy import deepcopy

import config
from tools.ex import read_str_from


def investigate(go, agent_path, old_all_methods, new_all_methods, prev_hash, post_hash):
    all_interested = set(old_all_methods + new_all_methods)
    return all_interested


def construct_invocation_map(triples_file):
    triples = read_str_from(triples_file)
    to_map = {}
    from_map = {}
    for triple in triples:
        active = triple[0]
        passive = triple[1]
        count = triple[2]
        if active in to_map:
            if passive in to_map[active]:
                to_map[active][passive] += count
            else:
                to_map[active][passive] = count
        else:
            to_map[active] = {}
            to_map[active][passive] = count
        if passive in from_map:
            if active in from_map[passive]:
                from_map[passive][active] += count
            else:
                from_map[passive][active] = count
        else:
            from_map[passive] = {}
            from_map[passive][active] = count
    return from_map, to_map


def caller_callee(go, ahash):
    the_file = go + "_getty_dyncg_" + ahash + "_.ex"
    return construct_invocation_map(the_file)


def pred_succ(go, ahash):
    the_file = go + "_getty_dynfg_" + ahash + "_.ex"
    return construct_invocation_map(the_file)


def get_test_set_dyn(target_set, callee_of, junit_torun):
    test_set = set()
    all_test_classes = junit_torun.split(" ")[1:]
    for possible_test_mtd in callee_of.keys():
        if (not re.match(".*:((suite)|(setUp)|(tearDown))$", possible_test_mtd)):
            for one_test in all_test_classes:
                if possible_test_mtd.startswith(one_test):
                    test_set.add(possible_test_mtd)
    return test_set


def _neighbor_for(target, the_map):
    if target in the_map:
        return set(the_map[target].keys())
    else:
        return set()


def refine_targets(target_set, test_set,
                   caller_of, callee_of, pred_of, succ_of,
                   changed_methods, changed_tests,
                   inner_dataflow_methods, outer_dataflow_methods):
    refined_target_set = deepcopy(target_set)
    if config.analyze_tests:
        refined_target_set = refined_target_set | test_set
    if config.limit_interest:
        # do not use static call graph information for now, but consider to use it for better results!
        all_related = set()
        all_for_current = set(changed_methods) | set(changed_tests)
        for _ in range(config.limit_distance):
            all_neighbors = set()
            all_related = all_related | all_for_current
            for tgt in all_for_current:
                if tgt not in test_set or not config.analyze_less_tests:
                    all_neighbors |= _neighbor_for(tgt, pred_of)
                    all_neighbors |= _neighbor_for(tgt, succ_of)
                    all_neighbors |= _neighbor_for(tgt, caller_of)
                all_neighbors |= _neighbor_for(tgt, callee_of)
            all_for_current = all_neighbors - all_related
        all_related = all_related | all_for_current
        refined_target_set = refined_target_set & all_related
    return refined_target_set
