# exchange parser

import ast


def read_str_from(file_path):
    with open(file_path, 'r') as f:
        str_ds = f.read()
    return ast.literal_eval(str_ds)


def save_to(afile, data):
    with open(afile, 'w') as f:
        f.write(data)


def save_list_to(afile, list_or_set):
    with open(afile, 'w') as f:
        list_str = "["
        for item in list_or_set:
            list_str += ("\"" + str(item) + "\", ")
        list_str += "]"
        f.write(list_str)
