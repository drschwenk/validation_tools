import os
import ast
import glob
from restruct_helpers import get_name_parts
from restruct_helpers import return_non_hidden
from restruct_helpers import generate_new_dir_structure
from restruct_helpers import append_to_change_log
from restruct_helpers import reset_logfile


def move_stable_dir():
    pass


def remove_dupes():
    pass


def test_train_split_three_cats():
    pass


def make_single_category_moves(trim_decisions, category, data_path, directory_renaming_instructions, change_log):
    for movie in directory_renaming_instructions:
        new_movie_path = movie[0]
        old_movie_path = movie[1]

        old_movie_sub_path, old_movie_dir = old_movie_path.rsplit('/', maxsplit=1)

        pvn, mvn, sub_n = get_name_parts(old_movie_dir)

        old_data_dir, tt_split, cat, video_dir = old_movie_path.split('/')
        new_data_dir, tt_split, cat, new_video_dir = new_movie_path.split('/')

        if not sub_n:
            keep_frames = trim_decisions[old_movie_path]
        else:
            keep_frames = trim_decisions[old_movie_sub_path + '/' + old_movie_dir.rsplit('_', maxsplit=1)[0]]

        if keep_frames == 'confirmed':
            move_confirmed(old_movie_path, new_movie_path, change_log)
        else:
            pass
            move_split(old_movie_path, new_movie_path, keep_frames, change_log)


def move_split(old_video_path, new_video_path, keep_frames, change_log):
    """
    splits and moves frames of a single movie to the new master
    """
    mov_pov_files(old_video_path, new_video_path, change_log)
    move_images(old_video_path, new_video_path, keep_frames, change_log)
    move_annotations(old_video_path, new_video_path, keep_frames, change_log)


def move_confirmed(old_path, new_path, change_log):
    old_data_dir, tt_split, category, old_video_dir = old_path.split('/')
    new_data_dir, tt_split, category, new_video_dir = new_path.split('/')
    annotation_tt_split = 'new_' + tt_split + '_wbox'

    old_annotation_path = '/'.join([old_data_dir, annotation_tt_split, category, old_video_dir])
    new_annotation_path = '/'.join([new_data_dir, annotation_tt_split, category, new_video_dir])
    append_to_change_log(new_path + ' without cuts', old_path, change_log)
    append_to_change_log(new_annotation_path + ' without cuts', old_annotation_path, change_log)

    mov_pov_files(old_path, new_path, change_log)
    os.makedirs(new_path)
    os.makedirs(new_annotation_path)


def move_images(old_video_path, new_video_path, keep_frames, change_log):
    file_ext = '.png'
    # new_movie_paths = []
    new_frame_idx = 0
    # try:
    os.makedirs(new_video_path)
    # except FileExistsError:
    #     pass
    for idx, span in enumerate(keep_frames):
        # try:
        for frame in range(int(span[0]), int(span[1])+1):
            old_file = old_video_path + '/' + str(frame).zfill(5) + file_ext
            new_file = new_video_path + '/' + str(new_frame_idx).zfill(5) + file_ext
            # new_movie_paths.append(new_file)
            # os.rename(old_file, new_file)
            append_to_change_log(new_file, old_file, change_log)
            new_frame_idx += 1
    # except (ValueError, FileNotFoundError) as e:
        #     pass
    pass


def move_annotations(old_video_path, new_video_path, keep_frames, change_log):
    old_data_dir, tt_split, category, old_video_dir = old_video_path.split('/')
    new_data_dir, tt_split, category, new_video_dir = new_video_path.split('/')

    annotation_tt_split = 'new_' + tt_split + '_wbox'

    old_annotation_path = '/'.join([old_data_dir, annotation_tt_split, category, old_video_dir])
    new_annotation_path = '/'.join([new_data_dir, annotation_tt_split, category, new_video_dir])

    annotation_extensions = ['_00.mat', '_00_ge.mat']
    os.makedirs(new_annotation_path)
    for file_ext in annotation_extensions:
        new_frame_idx_anno = 0
        for idx, span in enumerate(keep_frames):
            try:
                for frame in range(int(span[0]), int(span[1]) + 1):
                    old_file = old_annotation_path + '/' + str(frame).zfill(5) + file_ext
                    new_file = new_annotation_path + '/' + str(new_frame_idx_anno).zfill(5) + file_ext
                    append_to_change_log(new_file, old_file, change_log)
                    os.open(old_file, 1)
                    new_frame_idx_anno += 1
            except(ValueError, FileNotFoundError) as e:
                append_to_change_log('doesn\'t exist', old_file, change_log)


def mov_pov_files(old_video_path, new_video_path, change_log):
    old_data_dir, tt_split, category, old_video_dir = old_video_path.split('/')
    new_data_dir, tt_split, category, new_video_dir = new_video_path.split('/')

    annotation_tt_split = 'new_' + tt_split + '_wbox'

    old_annotation_path = '/'.join([old_data_dir, annotation_tt_split, category, old_video_dir])
    new_annotation_path = '/'.join([new_data_dir, 'saved_pov', annotation_tt_split, category, new_video_dir])
    pov_ext = '_00_fr.mat'
    os.makedirs(new_annotation_path)
    for fr_file in glob.glob(old_annotation_path + '/*' + pov_ext):
        new_file_path = new_annotation_path + '/' + fr_file
        append_to_change_log(new_file_path, fr_file, change_log)


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
    for cat in categories[4:6]:
        if cat[:-1] in categories:
            new_path = new_data_dir_prefix + data_path + cat[:-1] + '/'
            #### CHANGE TO NEW PATH   ####
            last_cat_dir = get_name_parts(os.listdir(new_path)[-1])[0]
            resume_index = int(last_cat_dir)
        else:
            new_path = new_data_dir_prefix + data_path + cat + '/'

        old_path = data_path + cat + '/'
        directory_renaming_instructions = generate_new_dir_structure(trim_decisions, cat, old_path, new_path, change_log, resume_index)
        make_single_category_moves(trim_decisions, cat, data_path, directory_renaming_instructions, change_log)
    return


if __name__ == '__main__':
    change_log_file = 'change_log.txt'
    if os.path.isfile(change_log_file):
        reset_logfile(change_log_file)
    root_data_path = 'data/prediction_videos_final_'
    for split in ['test/', 'train/'][1:]:
        trim_and_move_all_categories(root_data_path + split, './combined_log.txt', change_log_file, 'master_')




