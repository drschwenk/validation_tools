import os


def get_name_parts(dir_name):
    try:
        pvn, mvn, sub_mov_n= dir_name.split('_')
        return pvn, mvn, sub_mov_n
    except ValueError:
        pvn, mvn = dir_name.split('_')
        return pvn, mvn, 0


def return_non_hidden(path):
    all_files = os.listdir(path)
    return [file for file in all_files if not file.startswith('.')]
