import os
import ast
from restruct_helpers import get_name_parts
from restruct_helpers import return_non_hidden


def move_stable_dir():
    pass


def remove_dupes():
    pass


def test_train_split_three_cats():
    pass


def clean_category_to_master(confirmation_log, category, data_path):
    dir_changes = []

    movie_dirs = return_non_hidden(data_path + category)
    parent_idx = 0
    current_parent = 0
    child_index = 0
    copies_detected = False

    movies_with_splits = []
    for movie in movie_dirs:
        movie_path = data_path + category + '/' + movie
        data_dir, split, subdivided_cats, video_dir = movie_path.split('/')
        if 'copy' in movie:
            movie_path = '/'.join([data_dir, split, subdivided_cats + '2', video_dir])
        try:
            keep_frames = confirmation_log[movie_path.replace(' copy', '')]
        except KeyError:
            try:
                movie_path_rn = '/'.join([data_dir, split, subdivided_cats + '2', video_dir.replace(' copy', '')])
                keep_frames = confirmation_log[movie_path_rn]
            except KeyError:
                movie_path_rn = '/'.join([data_dir, split, subdivided_cats + '3', video_dir.replace(' copy', '')])
                keep_frames = confirmation_log[movie_path_rn]
        if keep_frames == 'flagged':
            pass
        if keep_frames == 'confirmed':
            movies_with_splits.append(movie)
        else:
            # print(movie_path, new_master_dir, keep_frames)
            # clean_movie_to_master(movie_path, new_master_dir, keep_frames)

            if len(keep_frames) > 1:
                for idx, span in enumerate(keep_frames):
                    movies_with_splits.append(movie + '_' + str(idx))
            else:
                movies_with_splits.append(movie)

    for movie in movies_with_splits:
        pvn, mvn, sub_n = get_name_parts(movie)
        if pvn != current_parent:
            if copies_detected:
                parent_idx += 1
                copies_detected = False
            current_parent = pvn
            parent_idx += 1
            child_index = 0
            dir_changes.append([str(parent_idx).zfill(3) + '_' + str(child_index).zfill(2), movie])
        else:
            if 'copy' in movie:
                copies_detected = True
                dir_changes.append([str(parent_idx + 1).zfill(3) + '_' + str(child_index).zfill(2), movie])
            else:
                child_index += 1
                dir_changes.append([str(parent_idx).zfill(3) + '_' + str(child_index).zfill(2), movie])
    return dir_changes


def make_category_moves(movie_frames_dict, subdivided_cats, data_path, new_master_dir, dir_changes):
    for movie in dir_changes:
        new_name = movie[0]
        old_name = movie[1]
        old_movie_path = 0
        pvn, mvn, sub_n = get_name_parts(old_name)
        if not sub_n:
            old_movie_path = data_path + subdivided_cats + '/' + old_name
        else:
            old_movie_path = data_path + subdivided_cats + '/' + pvn + '_' + mvn

        try:
            keep_frames = movie_frames_dict[old_movie_path.replace(' copy', '')]
        except KeyError:
            try:
                old_movie_path_rn = data_path + subdivided_cats + '2' + '/' + old_movie_path.split('/')[-1].replace(' copy', '')
                keep_frames = movie_frames_dict[old_movie_path_rn]
            except:
                old_movie_path_rn = data_path + subdivided_cats + '3' + '/' + old_movie_path.split('/')[-1].replace(' copy', '')
                keep_frames = movie_frames_dict[old_movie_path_rn]

        if keep_frames == 'confirmed':
            move_confirmed(old_movie_path, new_name, new_master_dir)

        else:
            pass
            move_split(old_movie_path, new_name, new_master_dir, keep_frames)


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


def move_confirmed(old_path, new_name, new_master_dir):
    old_data_dir, split, subdivided_cats, video_dir = old_path.split('/')
    annotation_split = 'new_' + split + '_wbox'
    old_annotation_dir = '/'.join([old_data_dir, annotation_split, subdivided_cats, video_dir])

    new_video_path = '/'.join([new_master_dir, split, subdivided_cats, new_name])
    new_annotation_path = '/'.join([new_master_dir, annotation_split, subdivided_cats, new_name])
    try:
        os.makedirs(new_video_path)
        os.makedirs(new_annotation_path)
    except FileExistsError:
        pass
    try:
        os.rename(old_path, new_video_path)
        os.rename(old_annotation_dir, new_annotation_path)
    except OSError:
        pass
    return


def trim_move_images():
    pass


def trim_move_annotations():
    pass


def trim_move_all_categories(data_path, trim_log_file):
    movie_frames_dict = {}
    with open(trim_log_file, 'r') as f:
        trim_log = f.readlines()
    for movie in trim_log:
        index, movie_path, keep_frames = movie.split(', ', maxsplit=2)
        # print(movie_path, '\n')
        # This try-except block converts frame ranged to a python list, flags remain strings
        try:
            movie_frames_dict[movie_path] = ast.literal_eval(keep_frames)
        except ValueError:
            movie_frames_dict[movie_path] = keep_frames.strip()
    categories = return_non_hidden(data_path)
    combined_categories = []
    for cat in categories[:15]:
        # print(cat, '\n')
        if cat[:-1] in categories:
            old_path = data_path + '/' + cat
            new_path = data_path + '/' + cat[:-1]
            # print(cat, return_non_hidden(old_path), '\n')
            for mov_dir in return_non_hidden(old_path):
                print(mov_dir)
        #         try:
        #             os.rename(old_path + '/' + mov_dir, new_path + '/' + mov_dir)
        #         except OSError:
        #             os.rename(old_path + '/' + mov_dir, new_path + '/' + mov_dir + ' copy')
        # # dir_change = clean_category_to_master(movie_frames_dict, cat, data_path)
        # print(dir_change)
        # make_category_moves(movie_frames_dict, cat, data_path, 'master', dir_change)
    return


if __name__ == '__main__':
    root_data_path = 'data/prediction_videos_final_'
    for split in ['test/', 'train/'][1:]:
        trim_move_all_categories(root_data_path + split, './combined_log.txt')

