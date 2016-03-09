# exchange parser

import ast


def read_str_from(file_path):
    with open(file_path, 'r') as file:
        str_ds = file.read()
    return ast.literal_eval(str_ds)


def save_to(file, data):
    with open(file, 'w') as f:
        f.write(data)
