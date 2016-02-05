# misc: utils for analysis, algorithms, prefix processings, etc.


# Recognize constructor and reformat it
# pachage.class:method -> package.class:method
# package.class:<init> -> pachage.class:class
# package.class:<clinit> -> package.class$
# package.outerclass$innerclass:<init> -> package.outerclass$innerclass:innerclass
def method_name(method):
    colon_index = method.rfind(":")
    if method[colon_index+1:] == "<init>":
        prd_i = method.rfind(".")
        dlr_i = method.rfind("$")
        chop_i = max(prd_i, dlr_i)
        if chop_i == -1:
            chop_i = 0
        methodname = method[chop_i+1:colon_index]
        return method[:colon_index] + ":" + methodname
    elif method[colon_index+1:] == "<clinit>":
        prd_i = method.rfind(".")
        dlr_i = method.rfind("$")
        chop_i = max(prd_i, dlr_i)
        if chop_i == -1:
            chop_i = 0
        methodname = method[chop_i+1:colon_index]
        return method[:colon_index] + "$"
    else:
        return method


def method_names(methods):
    reformated = []
    for m in methods:
        reformated.append(method_name(m))
    return reformated


# Return the longest prefix of all list elements. The return might be short.
def __common_prefix(m):
    if not m:
        raise ValueError('list of strings should not be empty')
    reformated = method_names(m)
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
        m = method_names(m)
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
def reformat_all(prefixes):
    result = []
    for prefix in prefixes:
        prefix = "^" + prefix.replace(":", ".").replace(".", "\.")
        result.append(prefix)
    return "|".join(result)


# reformat one method so it is recognizable by Daikon filter
def dfformat(method, for_daikon=True):
    if for_daikon:
        method = "^" + method_name(method)
        if method.endswith("$"):
            return method.replace(":", ".").replace(".", "\.")
        else:
            return method.replace(":", ".").replace(".", "\.") + "\("
    else:
        return method.replace(":", ".").replace(".", "\.") + "\("


# reformat one method so it is recognizable by Daikon filter
def fsformat(method, for_daikon=True):
    if for_daikon:
        method = method_name(method)
        if method.endswith("$"):
            return method[:-1].replace(":", "_").replace("$", "_").replace(".", "_")
        else:
            return method.replace(":", "_").replace("$", "_").replace(".", "_")
    else:
        return method.replace(":", "_").replace("$", "_").replace(".", "_")
