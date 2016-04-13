import os
import ast
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


def make_single_category_moves(trim_decisions, category, data_path, directory_renaming_instructions):
    for movie in directory_renaming_instructions:
        new_movie_path = movie[0]
        old_movie_path = movie[1]

        old_movie_sub_path, old_movie_dir = old_movie_path.rsplit('/', maxsplit = 1)

        pvn, mvn, sub_n = get_name_parts(old_movie_dir)

        if not sub_n:
            keep_frames = trim_decisions[old_movie_path]
        else:
            keep_frames = trim_decisions[old_movie_sub_path + '/' + old_movie_dir.rsplit('_', maxsplit=1)[0]]
        if keep_frames == 'confirmed':
            move_confirmed(old_movie_path, new_movie_path)

        else:
            pass
            # move_split(old_movie_path, new_movie_path, keep_frames)


def move_split(old_path, new_name, new_master_dir, keep_frames):
    """
    splits and moves frames of a single movie to the new master
    """

    # this removes the data dir from the path
    # os.makedirs(new_path)

    image_extension = '.png'
    annotation_extensions = ['_00.mat', '_00_ge.mat','_00_fr.mat']
    pov_ext = '_00_fr.mat'

    old_data_dir, split, subdivided_cats, video_dir = old_path.split('/')
    annotation_split = 'new_' + split + '_wbox'

    old_annotation_dir = '/'.join([old_data_dir, annotation_split, subdivided_cats, video_dir])

    new_video_path = '/'.join([new_master_dir, split, subdivided_cats, new_name])
    new_annotation_path = '/'.join([new_master_dir, annotation_split, subdivided_cats, new_name])

    file_ext = image_extension
    new_movie_paths = []
    new_frame_idx = 0
    try:
        os.makedirs(new_video_path)
        os.makedirs(new_annotation_path)
        os.makedirs(new_annotation_path.replace(new_master_dir, 'save_fr_mat_files'))
    except FileExistsError:
        pass
    for idx, span in enumerate(keep_frames):
        try:
            for frame in range(int(span[0]), int(span[1])+1):
                old_file = old_path + '/' + str(frame).zfill(5) + file_ext
                new_file = new_video_path + '/' + str(new_frame_idx).zfill(5) + file_ext
                new_movie_paths.append(new_file)
                os.rename(old_file, new_file)

                new_frame_idx += 1
        except (ValueError, FileNotFoundError) as e:
            pass

    for file_ext in annotation_extensions:
        new_frame_idx_anno = 0
        for idx, span in enumerate(keep_frames):
            try:
                for frame in range(int(span[0]), int(span[1]) + 1):
                    old_file = old_annotation_dir + '/' + str(frame).zfill(5) + file_ext
                    if file_ext == pov_ext:
                        new_annotation_path = new_annotation_path.replace(new_master_dir, 'save_fr_mat_files')
                    new_file = new_annotation_path + '/' + str(new_frame_idx_anno).zfill(5) + file_ext
                    new_movie_paths.append(new_file)
                    os.rename(old_file, new_file)
                    new_frame_idx_anno += 1
            except (FileNotFoundError, ValueError) as e:
                pass
    return


def move_confirmed(old_path, new_path):
    old_data_dir, tt_split, cat, video_dir = old_path.split('/')
    new_data_dir, tt_split, cat, video_dir = new_path.split('/')

    print(old_data_dir, new_data_dir, '\n')

    # trim_and_move_images()
    # trim_and_move_annotations()

    # try:
    #     os.makedirs(new_video_path)
    #     os.makedirs(new_annotation_path)
    # except FileExistsError:
    #     pass
    # try:
    #     os.rename(old_path, new_video_path)
    #     os.rename(old_annotation_dir, new_annotation_path)
    # except OSError:
    #     pass
    return


def move_images():

    pass


def move_annotations(old_data_dir, new_data_dir, category, old_mov_name, new_mov_name):
    annotation_tt_split = 'new_' + split + '_wbox'
    old_annotation_path = '/'.join([old_data_dir, annotation_tt_split, category, old_mov_name])
    new_annotation_path = '/'.join([new_data_dir, annotation_tt_split, category, new_mov_name])
    pass


def trim_and_move_all_categories(data_path, trim_log_file, change_log):
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
            new_path = data_path + cat[:-1] + '/'
            last_cat_dir = get_name_parts(os.listdir(new_path)[-1])[0]
            resume_index = int(last_cat_dir)
        else:
            new_path = data_path + cat + '/'

        old_path = data_path + cat + '/'
        directory_renaming_instructions = generate_new_dir_structure(trim_decisions, cat, old_path, new_path, change_log, resume_index)
        make_single_category_moves(trim_decisions, cat, data_path, directory_renaming_instructions)
    return


if __name__ == '__main__':
    change_log_file = 'change_log.txt'
    if os.path.isfile(change_log_file):
        reset_logfile(change_log_file)
    root_data_path = 'data/prediction_videos_final_'
    for split in ['test/', 'train/'][1:]:
        trim_and_move_all_categories(root_data_path + split, './combined_log.txt', change_log_file)




