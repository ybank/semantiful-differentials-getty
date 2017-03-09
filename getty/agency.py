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
        if (not re.match(".*:((suite)|(setUp)|(tearDown))-(\d)*$", possible_test_mtd)):
            for one_test in all_test_classes:
                if possible_test_mtd.startswith(one_test):
                    test_set.add(possible_test_mtd)
    return test_set


def _neighbor_for(target, the_map):
    if target in the_map:
        return set(the_map[target].keys())
    else:
        return set()


def _correct_offset(rough_targets, exact_target_map):
    sigspan = config.max_method_decl_span
    result = set([])
    potential_target_keys = exact_target_map.keys()
    size_tracked = len(result)
    for t in rough_targets:
        dash_index = t.rfind("-")
        if dash_index != -1:
            line_number = int(t[dash_index+1:].strip())
            for offset in range(sigspan):
                consider = t[:dash_index] + "-" + str(line_number + offset)
                if consider in potential_target_keys:
                    result.add(consider)
                    break
            if size_tracked < len(result):
                size_tracked = len(result)
            else:
                print 'RARE: no method name matches in the given offset'
                for anyone in potential_target_keys:
                    if anyone.startswith(t[:dash_index+1]):
                        result.add(anyone)
                        break
                if size_tracked < len(result):
                    size_tracked = len(result)
                else:
                    print 'VERY RARE: no method name matches in all possible targets'
        else:
            print 'The method comes without line number information (-(\d)*): ' + t
            for anyone in potential_target_keys:
                if anyone.startswith(t + "-"):
                    result.add(anyone)
    return result


def refine_targets(full_method_info_map, target_set, test_set,
                   caller_of, callee_of, pred_of, succ_of,
                   changed_methods, changed_tests,
                   inner_dataflow_methods, outer_dataflow_methods):
    target_set = set([])
    for ky in full_method_info_map.keys():
        target_set.add(full_method_info_map[ky])
    refined_target_set = set(deepcopy(target_set))
    
    cmbak = _correct_offset(changed_methods, full_method_info_map)
    changed_methods = set([])
    for cm in cmbak:
        if cm in full_method_info_map:
            changed_methods.add(full_method_info_map[cm])
    
    ctbak = _correct_offset(changed_tests, full_method_info_map)
    changed_tests = set([])
    for ct in ctbak:
        if ct in full_method_info_map:
            changed_tests.add(full_method_info_map[ct])

    if config.analyze_tests:
        refined_target_set = refined_target_set | test_set | changed_tests
    if config.limit_interest:
        # do not use static call graph information for now, but consider to use it for better results!
        all_related = set()
        all_for_current = changed_methods | changed_tests
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
    
    return refined_target_set, changed_methods, changed_tests
