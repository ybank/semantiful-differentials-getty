# misc: utils for analysis, algorithms, prefix processings, etc.


# Return the longest prefix of all list elements. The return might be short.
def __common_prefix(m):
    if not m:
        raise ValueError('list of strings should not be empty')
    min_s = min(m)
    max_s = max(m)
    for i, c in enumerate(min_s):
        if c != max_s[i]:
            return min_s[:i]
    return min_s


# Return common prefix
def common_prefixes(m):
    if not m:
        raise ValueError('list of strings should not be empty')
    min_length = 10  # minimum length set, magical number
    result = set()
    current_prefix = ''
    working = []
    remaining = list(m)
    remaining.sort()
    simple_result = __common_prefix(m)
    if len(simple_result) > min_length:
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
                    if len(new_prefix) > min_length:
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


# formalize method (etc.) prefixes so they are recognizable by Daikon filter
def formalize(prefixes):
    result = []
    for prefix in prefixes:
        prefix = prefix.replace(":", ".").replace(".", "\.")
        result.append(prefix)
    return "\|".join(result)


# formalize one method so it is recognizable by Daikon filter
def dfformat(method):
    return method.replace(":", ".").replace(".", "\.") + "\("


# formalize one method so it is recognizable by Daikon filter
def fsformat(method):
    return method.replace(":", "_").replace("$", "_").replace(".", "_")
