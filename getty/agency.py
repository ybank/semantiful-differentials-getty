# get interested runtime targets

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
