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

        if sub_n == 'childless':
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
    # move_pov_files(old_video_path, new_video_path, change_log)
    move_images(old_video_path, new_video_path, keep_frames, change_log)


def move_confirmed(old_path, new_path, change_log):
    old_data_dir, tt_split, category, old_video_dir = old_path.split('/')
    new_data_dir, tt_split, category, new_video_dir = new_path.split('/')
    annotation_tt_split = 'new_' + tt_split + '_wbox'

    old_annotation_path = '/'.join([old_data_dir, annotation_tt_split, category, old_video_dir])
    new_annotation_path = '/'.join([new_data_dir, annotation_tt_split, category, new_video_dir])
    append_to_change_log(new_path + ' without cuts', old_path, change_log)
    append_to_change_log(new_annotation_path + ' without cuts', old_annotation_path, change_log)

    # move_pov_files(old_path, new_path, change_log)
    os.makedirs(new_path)
    os.makedirs(new_annotation_path)
    #os.rename(old_path, new_path)
    #os.rename(old_annotation_path, new_annotation_path)


def move_images(old_video_path, new_video_path, keep_frames, change_log):
    file_ext = '.png'
    # new_movie_paths = []
    new_frame_idx = 0
    # try:
    old_data_dir, tt_split, category, old_video_dir = old_video_path.split('/')
    new_data_dir, tt_split, category, new_video_dir = new_video_path.split('/')
    annotation_tt_split = 'new_' + tt_split + '_wbox'
    old_annotation_path = '/'.join([old_data_dir, annotation_tt_split, category, old_video_dir])
    new_annotation_path = '/'.join([new_data_dir, annotation_tt_split, category, new_video_dir])

    os.makedirs(new_video_path)
    os.makedirs(new_annotation_path)

    pvn, mvn, sub_n = get_name_parts(old_video_dir)
    if sub_n != 'childless':
        old_video_path = '/'.join([old_data_dir + annotation_tt_split + category]) + '/' + pvn + '_' + mvn
    else:
        sub_n = 0

    # except FileExistsError:
    #     pass
    # for idx, span in enumerate(keep_frames):
    # try:
    span = keep_frames[int(sub_n)]
    for frame in range(int(span[0]), int(span[1])+1):
        old_file = old_video_path + '/' + str(frame).zfill(5) + file_ext
        new_file = new_video_path + '/' + str(new_frame_idx).zfill(5) + file_ext
        # new_movie_paths.append(new_file)
        # #os.rename(old_file, new_file)
        append_to_change_log(new_file, old_file, change_log)
        #os.rename(old_file, new_file)
        move_annotations(old_annotation_path, new_annotation_path, frame, new_frame_idx, change_log)
        new_frame_idx += 1
    # except (ValueError, FileNotFoundError) as e:
        #     pass
    pass


def move_annotations(old_annotation_path, new_annotation_path, frame, image_idx, change_log):
    annotation_extensions = ['_00.mat', '_00_ge.mat']

    for file_ext in annotation_extensions:
            try:
                old_file = old_annotation_path + '/' + str(frame).zfill(5) + file_ext
                new_file = new_annotation_path + '/' + str(image_idx).zfill(5) + file_ext
                # append_to_change_log(new_file, old_file, change_log)
                #os.rename(old_file, new_file)
            except(ValueError, FileNotFoundError) as e:
                append_to_change_log('doesn\'t exist', old_file, change_log)


def move_pov_files(old_video_path, new_video_path, change_log):
    old_data_dir, tt_split, category, old_video_dir = old_video_path.split('/')
    new_data_dir, tt_split, category, new_video_dir = new_video_path.split('/')

    annotation_tt_split = 'new_' + tt_split + '_wbox'

    old_annotation_path = '/'.join([old_data_dir, annotation_tt_split, category, old_video_dir])
    new_annotation_path = '/'.join([new_data_dir, 'save_fr', annotation_tt_split, category, new_video_dir])

    pov_ext = '_00_fr.mat'
    os.makedirs(new_annotation_path)
    for fr_file in glob.glob(old_annotation_path + '/*' + pov_ext):
        fr_file_name = fr_file.rsplit('/', maxsplit=1)[1]
        #os.rename(fr_file, new_annotation_path + '/' + fr_file_name)


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




