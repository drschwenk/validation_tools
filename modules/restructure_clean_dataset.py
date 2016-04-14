import os
import ast
import glob
import shutil
import random
from restruct_helpers import get_name_parts
from restruct_helpers import return_non_hidden
from restruct_helpers import generate_new_dir_structure
from restruct_helpers import append_to_change_log
from restruct_helpers import reset_logfile
from restruct_helpers import get_keep_frames


def convert_vid_path_to_anno(vid_path):
    # prediction_videos_final_train / passing - rugby / 95_6
    try:
        data_dir, tt_split, category, video_dir = vid_path.split('/')
        anno_path = '/'.join([data_dir, 'new_' + tt_split + '_wbox', category, video_dir])
    except ValueError:
        data_dir, tt_split, category = vid_path.split('/')
        anno_path = '/'.join([data_dir, 'new_' + tt_split + '_wbox', category])
    return anno_path


def move_stable_dir(data_path, change_file_log, new_prefix):
    img_dir_path = (new_prefix + data_path).rsplit('/', maxsplit=1)[0]
    data_dir, an_sub_path, _ = data_path.split('/', maxsplit=2)
    anno_dir_path = new_prefix + data_dir + '/new_' + an_sub_path + '_wbox'

    os.makedirs(img_dir_path)
    os.makedirs(anno_dir_path)
    for stable_file_path in glob.glob(data_path + '/stable*'):
        old_anno = convert_vid_path_to_anno(stable_file_path)
        new_stable_path = new_prefix + stable_file_path
        new_anno = convert_vid_path_to_anno(new_stable_path)
        os.rename(stable_file_path, new_stable_path)
        append_to_change_log(new_stable_path, stable_file_path, change_log_file)
        os.rename(old_anno, new_anno)
        append_to_change_log(new_anno, old_anno, change_log_file)


def remove_dupes(dupe_log, change_log):
    with open(dupe_log, 'r') as f:
        dupes = f.readlines()
    dupe_pairs = []
    for idx, line in enumerate(dupes):
        if not idx %3:
            dupe_1 = dupes[idx+1].strip()
            dupe_2 = line.strip()
            dupe_pairs.append([dupe_1.rsplit('/', maxsplit=1)[0],
                               dupe_2.rsplit('/', maxsplit=1)[0]])
    for pair in dupe_pairs:
        vid_dir = 'data/' + pair[1]
        anno_dir =  convert_vid_path_to_anno(vid_dir)
        shutil.rmtree(vid_dir)
        shutil.rmtree(anno_dir)
        with open(change_log, 'a') as log:
            log.write(pair[0] + ' and ' + pair[1] + ' are duplicates, removing ' + pair[1] + '\n')


def delete_superseded_dirs(root_dir, to_delete, change_log):
    for action_type in to_delete:
        with open(change_log, 'a') as log:
            vid_dir = root_dir + action_type
            anno_dir = convert_vid_path_to_anno(vid_dir)
            shutil.rmtree(vid_dir)
            shutil.rmtree(anno_dir)
            log.write('deleting directory- ' + vid_dir + '\n')
            log.write('deleting directory- ' + anno_dir + '\n')


def test_train_split_three_cats(replacement_dir, new_prefix, change_log):
    random.seed(15)
    for rep_dir in glob.glob(replacement_dir+'/*'):
        for mov in glob.glob(rep_dir + '/*'):
            anno_dir = mov.replace('prediction_videos_3_categories',
                                   'new_prediction_videos_3_categories_wbox')
            if random.randint(1, 3) < 3:
                new_vid_path = mov.replace('3_categories', 'final_train')
                new_anno_path = anno_dir.replace('3_categories', 'final_train')

            else:
                new_vid_path = mov.replace('3_categories', 'final_test')
                new_anno_path =anno_dir.replace('3_categories', 'final_test')
            os.makedirs(new_vid_path)
            os.makedirs(new_anno_path)
            try:
                os.rename(mov, new_vid_path)
                os.rename(anno_dir, new_anno_path)
            except FileNotFoundError:
                with open(change_log, 'a') as log:
                    log.write(mov + ' annotations not found \n')
            append_to_change_log(new_vid_path, mov, change_log)
            append_to_change_log(new_anno_path, anno_dir, change_log)


def make_single_category_moves(trim_decisions, category, data_path, directory_renaming_instructions, change_log):
    for movie in directory_renaming_instructions:
        new_movie_path = movie[0]
        old_movie_path = movie[1]

        old_movie_sub_path, old_movie_dir = old_movie_path.rsplit('/', maxsplit=1)

        pvn, mvn, sub_n = get_name_parts(old_movie_dir)

        if sub_n == 'childless':
            keep_frames = get_keep_frames(trim_decisions, old_movie_path)
            # keep_frames = trim_decisions[old_movie_path]
        else:
            keep_frames = get_keep_frames(trim_decisions, old_movie_sub_path + '/' +
                                          old_movie_dir.rsplit('_', maxsplit=1)[0])

        if keep_frames == 'confirmed':
            move_confirmed(old_movie_path, new_movie_path, change_log)
        else:
            # move_confirmed_pov_files(old_movie_path, new_movie_path, change_log)
            move_images_and_annotations(old_movie_path, new_movie_path, keep_frames, change_log)


def move_confirmed(old_path, new_path, change_log):
    old_data_dir, tt_split, old_category, old_video_dir = old_path.split('/')
    new_data_dir, tt_split, new_category, new_video_dir = new_path.split('/')
    annotation_tt_split = 'new_' + tt_split + '_wbox'

    old_annotation_path = '/'.join([old_data_dir, annotation_tt_split, old_category, old_video_dir])
    new_annotation_path = '/'.join([new_data_dir, annotation_tt_split, new_category, new_video_dir])

    move_confirmed_pov_files(old_path, new_path, change_log)
    os.makedirs(new_path)
    os.makedirs(new_annotation_path)

    if not os.path.isdir(old_annotation_path):
        append_to_change_log('has no annotations', old_annotation_path, change_log)
        return

    os.rename(old_path, new_path)
    os.rename(old_annotation_path, new_annotation_path)

    append_to_change_log(new_path + ' without cuts', old_path, change_log)
    append_to_change_log(new_annotation_path + ' without cuts', old_annotation_path, change_log)


def move_images_and_annotations(old_video_path, new_video_path, keep_frames, change_log):
    file_ext = '.png'
    new_frame_idx = 0
    old_data_dir, tt_split, old_category, old_video_dir = old_video_path.split('/')
    new_data_dir, tt_split, new_category, new_video_dir = new_video_path.split('/')
    annotation_tt_split = 'new_' + tt_split + '_wbox'
    old_annotation_path = '/'.join([old_data_dir, annotation_tt_split, old_category, old_video_dir])
    new_annotation_path = '/'.join([new_data_dir, annotation_tt_split, new_category, new_video_dir])
    save_anno_path = '/'.join([new_data_dir, 'save_fr', annotation_tt_split,
                               new_category, new_video_dir])
    os.makedirs(new_video_path)
    os.makedirs(new_annotation_path)
    os.makedirs(save_anno_path)

    pvn, mvn, sub_n = get_name_parts(old_video_dir)
    if sub_n != 'childless':
        old_video_path = '/'.join([old_data_dir, tt_split, old_category]) + '/' + pvn + '_' + mvn
        old_annotation_path = '/'.join([old_data_dir, annotation_tt_split, old_category]) + '/' + pvn + '_' + mvn
    else:
        sub_n = 0

    span = keep_frames[int(sub_n)]
    for frame in range(int(span[0]), int(span[1])+1):
        old_file = old_video_path + '/' + str(frame).zfill(5) + file_ext
        new_file = new_video_path + '/' + str(new_frame_idx).zfill(5) + file_ext
        os.rename(old_file, new_file)
        append_to_change_log(new_file, old_file, change_log)
        move_annotations(old_annotation_path, new_annotation_path, frame, new_frame_idx, change_log)
        new_frame_idx += 1


def move_annotations(old_annotation_path, new_annotation_path, frame, image_idx, change_log):
    if not os.path.isdir(old_annotation_path):
        append_to_change_log('has no annotations', old_annotation_path, change_log)
        return
    annotation_extensions = ['_00.mat', '_00_ge.mat', '_00_fr.mat']
    pov_ext = '_00_fr.mat'
    new_data_dir, annotation_tt_split, new_category, new_video_dir = new_annotation_path.split('/')
    for file_ext in annotation_extensions:
            old_file = old_annotation_path + '/' + str(frame).zfill(5) + file_ext

            if file_ext == pov_ext:
                new_annotation_path = '/'.join([new_data_dir, 'save_fr', annotation_tt_split,
                                                new_category, new_video_dir])
            new_file = new_annotation_path + '/' + str(image_idx).zfill(5) + file_ext
            try:
                append_to_change_log(new_file, old_file, change_log)
                os.rename(old_file, new_file)
            except(ValueError, FileNotFoundError) as e:
                append_to_change_log('doesn\'t exist', old_file, change_log)


def move_confirmed_pov_files(old_video_path, new_video_path, change_log):
    old_data_dir, tt_split, old_category, old_video_dir = old_video_path.split('/')
    new_data_dir, tt_split, new_category, new_video_dir = new_video_path.split('/')

    annotation_tt_split = 'new_' + tt_split + '_wbox'

    old_annotation_path = '/'.join([old_data_dir, annotation_tt_split, old_category, old_video_dir])
    new_annotation_path = '/'.join([new_data_dir, 'save_fr', annotation_tt_split, new_category, new_video_dir])

    pov_ext = '_00_fr.mat'
    os.makedirs(new_annotation_path)
    for fr_file in glob.glob(old_annotation_path + '/*' + pov_ext):
        fr_file_name = fr_file.rsplit('/', maxsplit=1)[1]
        os.rename(fr_file, new_annotation_path + '/' + fr_file_name)


def trim_and_move_all_categories(data_path, trim_log_file, change_log, new_data_dir_prefix):
    trim_decisions = {}
    with open(trim_log_file, 'r') as f:
        trim_log = f.readlines()
    for movie in trim_log:
        index, movie_path, keep_frames = movie.split(', ', maxsplit=2)
        # This try-except block converts frame ranges to a python list, flags remain strings
        try:
            trim_decisions[movie_path] = ast.literal_eval(keep_frames)
        except ValueError:
            trim_decisions[movie_path] = keep_frames.strip()
    categories = return_non_hidden(data_path)
    resume_index = 0
    for cat in categories:
        if cat[:-1] in categories:
            new_path = new_data_dir_prefix + data_path + cat[:-1] + '/'
            last_cat_dir = get_name_parts(os.listdir(new_path)[-1])[0]
            resume_index = int(last_cat_dir)
        else:
            new_path = new_data_dir_prefix + data_path + cat + '/'

        old_path = data_path + cat + '/'
        directory_renaming_instructions = generate_new_dir_structure(trim_decisions, cat, old_path, new_path, change_log, resume_index)
        make_single_category_moves(trim_decisions, cat, data_path, directory_renaming_instructions, change_log)
    return


if __name__ == '__main__':
    new_data_prefix = 'master_'
    change_log_file = 'change_log.txt'
    dupe_dirs = 'dupes.txt'
    root_data_path = 'data/prediction_videos_final_'

    if os.path.isfile(change_log_file):
        reset_logfile(change_log_file)

    superseded_dirs = ['test/throwing-basketball', 'train/kicking-basketball',
                       'train/rolling-bowling', 'test/rolling-bowling']
    delete_superseded_dirs(root_data_path, superseded_dirs, change_log_file)

    remove_dupes(dupe_dirs, change_log_file)
    replacement_mov_dir = 'data/prediction_videos_3_categories'
    test_train_split_three_cats(replacement_mov_dir, new_data_prefix, change_log_file)

    for split in ['test/', 'train/']:
        move_stable_dir(root_data_path + split, change_log_file, new_data_prefix)
        trim_and_move_all_categories(root_data_path + split, './combined_log.txt', change_log_file, new_data_prefix)




