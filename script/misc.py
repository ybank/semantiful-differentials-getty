# misc: utils for analysis, algorithms, prefix processings, etc.


# Recognize constructor and reformat it
# pachage.class:method -> package.class:method
# package.class:<init> -> pachage.class:class
# package.class:<clinit> -> package.class
# package.outerclass$innerclass:<init> -> package.outerclass$innerclass:innerclass
def real_name(target):
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
        return target[:colon_index]
    else:
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


# reformat method (etc.) prefixes so they are recognizable by Daikon filter
def reformat_all(prefixes, more_ppts=False):
    result = []
    for prefix in prefixes:
        if more_ppts:
            colon_index = prefix.rfind(":")
            if colon_index != -1:
                prefix = prefix[:colon_index]  # includes class$, class.*, and more (class*)
        prefix = "^" + prefix.replace(":", ".").replace(".", "\.")
        result.append(prefix)
    return "|".join(result)


# reformat one method so it is recognizable by Daikon filter
def dfformat(target, more_ppts=False):
    target = real_name(target)
    colon_index = target.rfind(":")
    if colon_index == -1:
          # includes class$, class.*, and more (class*)
        return "^" + target.replace(":", ".").replace(".", "\.")
    else:
        if more_ppts:
              # includes class$, class.*, and more (class*)
            return "^" + target[:colon_index].replace(":", ".").replace(".", "\.")
        else:
            return "^" + target.replace(":", ".").replace(".", "\.") + "\("


# reformat one target so it is recognizable by Daikon filter
def fsformat(target, for_daikon=True):
    if for_daikon:
        target = real_name(target)
    return target.replace(":", "_").replace("$", "_").replace(".", "_")
