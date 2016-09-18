# exchange parser

import ast


def read_str_from(file_path):
    with open(file_path, 'r') as f:
        str_ds = f.read()
    return ast.literal_eval(str_ds)


def save_to(afile, data):
    with open(afile, 'w') as f:
        f.write(data)
