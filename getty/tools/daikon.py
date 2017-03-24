# misc: utils for analysis, algorithms, prefix processings, etc.

import re
from copy import deepcopy

import config


def simplify_target_name(t, common_package=""):
    last_dash_pos = t.rfind("-")
    ln_info = (t[last_dash_pos+1:].split(",")
                    if last_dash_pos != -1
                    else [None, None])
    if len(ln_info) == 1:
        curr_ln = int(ln_info[0])
        prev_ln = None
        post_ln = None
    elif len(ln_info) == 2:
        [prev_ln, post_ln] = ln_info
        if prev_ln is not None:
            prev_ln = int(prev_ln)
        if post_ln is not None:
            post_ln = int(post_ln)
        curr_ln = None
    if last_dash_pos != -1:
        tname = t[:last_dash_pos]
    else:
        tname = t
    full_name = tname
    if config.extreme_simple_mode:
        if common_package != '':
            tname = tname[len(common_package)+1:]
        params = [p.strip() for p in re.split("(,|\(|\)|<|>|\[|\]|\$|:)", tname)]
        for i in range(len(params) - 1):
            j = i + 1
            part_value = params[j]
            last_dot_pos = part_value.rfind(".")
            if last_dot_pos != -1:
                params[j] = part_value[last_dot_pos+1:]
        tname = "".join(params)
    else:
        hidden_packages = deepcopy(config.hidden_package_names)
        if common_package != '':
            tname = tname[len(common_package)+1:]
            hidden_packages.append(common_package)
        if hidden_packages:
            leftp = tname.find("(")
            rightp = tname.find(")")
            params = [p.strip() for p in re.split("(,|\(|\)|<|>|\[|\]|\$|:)", tname[leftp+1:rightp])]
            lparams = len(params)
            for pkg in hidden_packages:
                lpkg = len(pkg)
                for i in range(lparams):
                    if params[i].startswith(pkg):
                        params[i] = params[i][lpkg+1:]
            params_str = re.sub(",", ", ", "".join(params))
            if leftp != -1:
                tname = tname[:leftp] + "(" + params_str + ")"
    short_name = tname
    short_display_name = tname.replace("<", "&lt;").replace(">", "&gt;")
    return short_name, short_display_name, prev_ln, post_ln, curr_ln, full_name


# Recognize constructor and reformat it
# pachage.class:method -> package.class:method
# package.class:<init> -> pachage.class:class
# package.class:<clinit> -> package.class
# package.outerclass$innerclass:<init> -> package.outerclass$innerclass:innerclass
def real_name_ff(target):
    colon_index = target.rfind(":")
    if colon_index == -1:
        # not a target, but a class name, for example
        return target
    elif target[colon_index+1:] == "<init>":
        prd_i = target.rfind(".")
        dlr_i = target.rfind("$")
        chop_i = max(prd_i, dlr_i)
        methodname = target[chop_i+1:colon_index]
        return target[:colon_index+1] + methodname
    elif target[colon_index+1:] == "<clinit>":
        return target[:colon_index] + ".class.init"
    else:
        return target


# Recognize constructor and reformat it, with signature info
# pachage.class:method(String, int) -> package.class:method(String, int)
# package.class:<init>(String, int) -> pachage.class:class(String, int)
# package.class:<clinit> -> package.class
# package.outerclass$innerclass:<init>(String, int) -> package.outerclass$innerclass:innerclass(String, int)
def real_name_ff_with_sigs(target):
    colon_index = target.rfind(":")
    leftp_index = target.rfind("(")
    rightp_index = target.rfind(")")
    if colon_index == -1:
        # not a target, but a class name, for example
        return target
    elif target[colon_index+1:] == "<init>":
        prd_i = target[:leftp_index].rfind(".")
        dlr_i = target[:leftp_index].rfind("$")
        chop_i = max(prd_i, dlr_i)
        methodname = target[chop_i+1:colon_index]
        return target[:colon_index+1] + methodname + target[leftp_index:rightp_index+1]
    elif target[colon_index+1:] == "<clinit>":
        return target[:colon_index] + ".class.init"
    else:
        return target


# Recognize constructor and reformat it
# pachage.class:method -> package.class:method
# package.class:<init> -> pachage.class:class
# package.class:<clinit> -> package.class
# package.outerclass$innerclass:<init> -> package.outerclass$innerclass:innerclass
def real_name_pi(target):
    colon_index = target.rfind(":")
    if colon_index == -1:
        # not a target, but a class name, for example
        return target
    elif target[colon_index+1:] == "<init>":
        prd_i = target.rfind(".")
        dlr_i = target.rfind("$")
        chop_i = max(prd_i, dlr_i)
        methodname = target[chop_i+1:colon_index]
        return target[:colon_index+1] + methodname
    elif target[colon_index+1:] == "<clinit>":
        return target[:colon_index] + ":::CLASS"
    else:
        return target


# Recognize constructor and reformat it
# pachage.class:method() -> package.class:method()
# package.class:<init>() -> pachage.class:class()
# package.class:<clinit>() -> package.class
# package.outerclass$innerclass:<init> -> package.outerclass$innerclass:innerclass
def real_name_pi_with_sigs(target):
    colon_index = target.rfind(":")
    leftp_index = target.rfind("(")
    rightp_index = target.rfind(")")
    if colon_index == -1:
        # not a target, but a class name, for example
        return target
    elif target[colon_index+1:].startswith("<init>"):
        prd_i = target[:leftp_index].rfind(".")
        dlr_i = target[:leftp_index].rfind("$")
        chop_i = max(prd_i, dlr_i)
        methodname = target[chop_i+1:colon_index]
        return target[:colon_index+1] + methodname + target[leftp_index:rightp_index+1].replace(" ", "")
    elif target[colon_index+1:] == "<clinit>":
        return target[:colon_index] + ":::CLASS"
    else:
        return target


# real name should be just as it is from BCEL!
def real_name(target):
    return target


def real_names(targets):
    reformated = []
    for m in targets:
        reformated.append(real_name(m))
    return reformated


# Return the longest prefix of all list elements. The return might be short.
def __common_prefix(m):
    if not m:
        raise ValueError('list of strings should not be empty')
    reformated = real_names(m)
    min_s = min(reformated)
    max_s = max(reformated)
    for i, c in enumerate(min_s):
        if c != max_s[i]:
            return min_s[:i]
    return min_s


# Return common prefix
__min_common_prefix_length = 10  # minimum length set, magical number
def common_prefixes(m, min_len=__min_common_prefix_length, daikon_style=True):
    if not m:
        raise ValueError('list of strings should not be empty')
    if daikon_style:
        m = real_names(m)
    result = set()
    current_prefix = ''
    working = []
    remaining = list(m)
    remaining.sort()
    simple_result = __common_prefix(m)
    if len(simple_result) > min_len:
        return [simple_result]
    else:
        while remaining != []:
            temp = remaining.pop()
            if working == []:
                working.append(temp)
                current_prefix = temp
            else:  # current_prefix is based on working, and is long enough
                if not temp.startswith(current_prefix):
                    working.append(temp)
                    new_prefix = __common_prefix(working)
                    if len(new_prefix) > min_len:
                        current_prefix = new_prefix
                    else:
                        result.add(current_prefix)
                        working = [temp]
                        current_prefix = temp
        if working == []:
            raise RuntimeError('right after loop working set should not be empty')
        else:
            result.add(current_prefix)
    return result


# reformat method (etc.) prefixes so they are recognizable by Daikon frontend (Chicory) filter
def reformat_all_prefixes(prefixes, more_ppts=False):
    result = []
    for prefix in prefixes:
        if more_ppts:
            colon_index = prefix.rfind(":")
            if colon_index != -1:
                prefix = prefix[:colon_index]  # includes class$, class.*, and more (class*)
        prefix = "^" + prefix.replace(":", ".").replace(".", "\.")
        result.append(prefix)
    return "|".join(result)


# reformat methods (etc.) so they are recognizable by Daikon frontend (Chicory) filter
def reformat_all(targets, more_ppts=False):
    classes = set()  # class names, all class/object invariant ppt (to add ":" in post processing)
    all_methods = set()  # class names, all all-methods ppt (to add "." in post processing)
    single_methods = set()  # method names, all single-method ppt (to add "(" in post processing)
    for target in targets:
        target = real_name(target)
        colon_index = target.rfind(":")
        if colon_index == -1:
            classes.add(target)
            if more_ppts:
                all_methods.add(target)
        else:
            single_methods.add(target)
            if more_ppts:
                classes.add(target[:colon_index])
    filtered_single_methods = set()
    for method in single_methods:
        colon_idx = method.rfind(":")
        if colon_idx == -1:
            raise ValueError("method set expects all elements with colon")
        else:
            all_its_class_methods = method[:colon_idx]
            if not all_its_class_methods in all_methods:
                filtered_single_methods.add(method)
    all_to_go = []
    for clz in classes:
        all_to_go.append("^" + clz.replace(":", ".").replace(".", "\.").replace("$", "\$") + ":")
    for amtd in all_methods:
        all_to_go.append("^" + amtd.replace(":", ".").replace(".", "\.").replace("$", "\$") + "\.")
    for fsmtd in filtered_single_methods:
        all_to_go.append("^" + fsmtd.replace(":", ".").replace(".", "\.").replace("$", "\$") + "\(")
    return "|".join(all_to_go)


# reformat one method (etc.) so it is recognizable by Daikon.PrintInvariants filter
# filter pattern example:
#     --ppt-select-pattern="^org\.apache\.commons\.csv\.QuoteMode.QuoteMode\("
def dpformat(target, more_ppts=False):
    target = real_name_pi(target)
    tci = target.rfind(":::")
    if tci != -1:
        return "^" + target[:tci].replace(":", ".").replace(".", "\.").replace("$", "\$") + target[tci:]
    colon_index = target.rfind(":")
    if colon_index == -1:
        if more_ppts:
            # includes class and class.*
            return "^" + target.replace(":", ".").replace(".", "\.").replace("$", "\$") + "(:|\.)"
        else:
            return "^" + target.replace(":", ".").replace(".", "\.").replace("$", "\$") + ":"
    else:
        if more_ppts:
            # include possible parents and the method itself
            possible_parents = target[:colon_index].replace(":", ".")
            itself = target.replace(":", ".")
            return ("^" + possible_parents + ":|^" + itself + "\(").replace(".", "\.").replace("$", "\$")
        else:
            return "^" + target.replace(":", ".").replace(".", "\.").replace("$", "\$") + "\("


# reformat one method (etc.) so it is recognizable by Daikon.PrintInvariants filter
# filter pattern example:
#     --ppt-select-pattern="^org\.apache\.commons\.csv\.QuoteMode.QuoteMode\(java\.lang\.String, int\):::EXIT"
def dpformat_with_sigs(target, more_ppts=False):
    target = real_name_pi_with_sigs(target)
    tci = target.rfind(":::")
    if tci != -1:
        return ("^" +
            target[:tci].replace(":", ".").replace(".", "\.").replace("$", "\$")
                .replace("[", "\[").replace("]", "\]")
                .replace("<", "\<").replace(">", "\>")
                .replace("(", "\(").replace(")", "\)") +
            target[tci:])
    colon_index = target.rfind(":")
    if colon_index == -1:
        if more_ppts:
            # includes class and class.*
            return ("^" +
                target.replace(":", ".").replace(".", "\.").replace("$", "\$")
                    .replace("[", "\[").replace("]", "\]")
                    .replace("<", "\<").replace(">", "\>")
                    .replace("(", "\(").replace(")", "\)") +
                "(:|\.)")
        else:
            return ("^" +
                target.replace(":", ".").replace(".", "\.").replace("$", "\$")
                    .replace("[", "\[").replace("]", "\]")
                    .replace("<", "\<").replace(">", "\>")
                    .replace("(", "\(").replace(")", "\)") +
                ":")
    else:
        if more_ppts:
            # include possible parents and the method itself (and overloaded methods)
            possible_parents = target[:colon_index].replace(":", ".")
            itself = target.replace(":", ".")
            return ("^" + possible_parents + ":|^" + itself + "\(") \
                        .replace(".", "\.").replace("$", "\$") \
                        .replace("[", "\[").replace("]", "\]") \
                        .replace("<", "\<").replace(">", "\>") \
                        .replace("(", "\(").replace(")", "\)")
        else:
            rightp_index = target.rfind(")")
            if rightp_index != -1:
                return ("^" +
                    target[:rightp_index+1].replace(":", ".").replace(".", "\.").replace("$", "\$")
                        .replace("(", "\(").replace(")", "\)")
                        .replace("[", "\[").replace("]", "\]")
                        .replace("<", "\<").replace(">", "\>")
                        .replace(",", ",(\ )*"))
            else:
                return ("^" +
                    target.replace(":", ".").replace(".", "\.").replace("$", "\$")
                        .replace("[", "\[").replace("]", "\]")
                        .replace("<", "\<").replace(">", "\>")
                        .replace("(", "\(").replace(")", "\)") +
                    "\(")


# reformat all methods together so it is recognizable by Daikon filter
def dfformat_full(target_set):
    interest_set = set()
    for target in target_set:
        target = real_name(target)
        colon_index = target.rfind(":")
        if colon_index == -1:
            # includes class and class.*
            interest_set.add("^" + target.replace(":", ".").replace(".", "\.").replace("$", "\$") + ":")
            interest_set.add("^" + target.replace(":", ".").replace(".", "\.").replace("$", "\$") + "\.")
        else:
            possible_parents = target[:colon_index].replace(":", ".")
            itself = target.replace(":", ".")
            interest_set.add(("^" + possible_parents + ":").replace(".", "\.").replace("$", "\$"))
            interest_set.add(("^" + itself + "\(").replace(".", "\.").replace("$", "\$"))
    return "|".join(interest_set)


# reformat all methods together so it is recognizable by Daikon filter
def dfformat_full_ordered(target_set):
    parent_interest_set = set()
    method_interest_set = set()
    for target in target_set:
        target = real_name(target)
        colon_index = target.rfind(":")
        if colon_index == -1:
            # includes class and class.*
            parent_interest_set.add(
                "^" +
                target.replace(":", ".").replace(".", "\.").replace("$", "\$")
                    .replace("[", "\[").replace("]", "\]").replace("<", "\<").replace(">", "\>") +
                ":")
        else:
            possible_parent = target[:colon_index].replace(":", ".")
            parent_interest_set.add(
                ("^" + possible_parent + ":").replace(".", "\.").replace("$", "\$")
                    .replace("[", "\[").replace("]", "\]").replace("<", "\<").replace(">", "\>"))
            if config.class_level_expansion:
                method_interest_set.add(
                    ("^" + possible_parent + ".*").replace(".", "\.").replace("$", "\$")
                        .replace("[", "\[").replace("]", "\]").replace("<", "\<").replace(">", "\>"))
            else:
                itself = target.replace(":", ".")
                first_leftp = itself.find("(")
                if first_leftp != -1:
                    itself = itself[:first_leftp]
                method_interest_set.add(
                    ("^" + itself + "\(").replace(".", "\.").replace("$", "\$")
                        .replace("[", "\[").replace("]", "\]").replace("<", "\<").replace(">", "\>"))
    parent_pattern = "|".join(parent_interest_set)
    method_pattern = "|".join(method_interest_set)
    if parent_pattern == '' and method_pattern == '':
        return 'GETTY_WARNING_THIS_PATTERN_SHOULD_NOT_EXIST'
    elif parent_pattern == '':
        return method_pattern
    elif method_pattern == '':
        return parent_pattern
    else:
        return parent_pattern + "|" + method_pattern


# reformat all methods together so it is recognizable by Daikon filter
# get more than the method name because we replace "(" with "*"
def dfformat_full_ordered_more(target_set):
    parent_interest_set = set()
    method_interest_set = set()
    for target in target_set:
        target = real_name(target)
        colon_index = target.rfind(":")
        if colon_index == -1:
            # includes class and class.*
            parent_interest_set.add("^" + target.replace(":", ".").replace(".", "\.").replace("$", "\$") + ":")
        else:
            possible_parents = target[:colon_index].replace(":", ".")
            itself = target.replace(":", ".")
            parent_interest_set.add(("^" + possible_parents + ":").replace(".", "\.").replace("$", "\$"))
            method_interest_set.add(("^" + itself + "*").replace(".", "\.").replace("$", "\$"))
    parent_pattern = "|".join(parent_interest_set)
    method_pattern = "|".join(method_interest_set)
    if parent_pattern == '' and method_pattern == '':
        return 'GETTY_WARNING_THIS_PATTERN_SHOULD_NOT_EXIST'
    elif parent_pattern == '':
        return method_pattern
    elif method_pattern == '':
        return parent_pattern
    else:
        return parent_pattern + "|" + method_pattern


# extended filter (secure)
def select_full(target_set):
    interest_set = set()
    for target in target_set:
        target = real_name(target)
        colon_index = target.rfind(":")
        if colon_index == -1:
            # includes class and class.*
            interest_set.add("^" + target.replace(":", ".").replace(".", "\.").replace("$", "\$") + "(:|\.)")
        else:
            possible_parents = target[:colon_index].replace(":", ".")
            interest_set.add(("^" + possible_parents).replace(".", "\.").replace("$", "\$") + "(:|\.)")
    return "|".join(interest_set)


# get possible parent class
def parent_class(target):
    colon_index = target.rfind(":")
    if colon_index == -1:
        return target
    else:
        return target[:colon_index]


# from target set to target map [parent -> method]
def target_s2m(target_set):
    target_map = {}
    for target in target_set:
        parent = parent_class(target)
        if parent in target_map:
            target_map[parent].append(target)
        else:
            target_methods = []
            target_methods.append(target)
            target_map[parent] = target_methods
    return target_map


# reformat one target so it is recognizable by Daikon filter
def fsformat(target, for_daikon=True):
    if for_daikon:
        target = real_name_ff(target)
    return target.replace(":", "_").replace("$", "_").replace(".", "_")


# reformat one target so it is recognizable by Daikon filter - with signature info
def fsformat_with_sigs(target, for_daikon=True):
    if for_daikon:
        target_name = real_name_ff_with_sigs(target)
    tcp = config.the_common_package[0]
    target, _, _, _, _, _ = simplify_target_name(
        target_name, common_package=tcp)
    last_dash_pos = target.rfind("-")
    if last_dash_pos == -1:
        return target.replace(":", "_").replace("$", "_").replace(".", "_") \
                     .replace("(", "--").replace(")", "--") \
                     .replace("<", "--").replace(">", "--") \
                     .replace("[", "--").replace("]", "--") \
                     .replace(",", "-").replace(" ", "")
    else:
        return target[:last_dash_pos].replace(":", "_").replace("$", "_").replace(".", "_") \
                                     .replace("(", "--").replace(")", "--") \
                                     .replace("<", "--").replace(">", "--") \
                                     .replace("[", "--").replace("]", "--") \
                                     .replace(",", "-").replace(" ", "")


def purify_target_name(t):
    dash_pos = t.find("-")
    if dash_pos == -1:
        return t
    else:
        return t[:dash_pos]
