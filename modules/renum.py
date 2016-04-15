import os
import ast
import glob
import shutil


def get_name_parts(dir_name):
    pvn, mvn = dir_name.split('_')
    return pvn, mvn


def renumber_dir(cat_path, new_name, old_name, child_idx):
    new_name = str(new_name).zfill(3) + '_' + child_idx
    old_name = old_name + '_' + child_idx
    old_path = cat_path + '/' + old_name
    new_path = cat_path + '/' + new_name

    print('moving ', old_path, new_path)
    os.rename(old_path, new_path)


def renumber_category(cat_path):
    if 'stable' in cat_path:
        return

    first_dir = glob.glob(cat_path + '/*')[0]
    path_to_first, first_name = first_dir.rsplit('/', maxsplit=1)
    fvn, fcn = get_name_parts(first_name)
    if '001' == fvn:
        print(cat_path, ' good')
        return

    for img_dir in glob.glob(cat_path + '/*'):
        path_to_dir, dir_name = img_dir.rsplit('/', maxsplit=1)
        pvn, mvn = get_name_parts(dir_name)
        new_parent_idx = int(pvn) - int(fvn)
        renumber_dir(cat_path, new_parent_idx, pvn, mvn)

if __name__ == '__main__':
    for tt_split in glob.glob('./master_data/*'):
        for cat_dir_path in glob.glob(tt_split + '/*'):
            print(cat_dir_path)
            renumber_category(cat_dir_path)
