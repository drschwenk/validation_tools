import os
import ast


def split_single_movie(movie_dir, frame_spans, new_path, file_ext):
    """
    splits and moves frames of a single movie to the new master
    """

    # this removes the data dir from the path
    # os.makedirs(new_path)
    new_movie_paths = []
    for idx, span in enumerate(frame_spans):
        if len(frame_spans) > 1:
            new_path += '_' + str(idx)
        for frame in range(int(span[0]), int(span[1])+1):
            old_file = movie_dir + '/' + str(frame).zfill(5) + file_ext
            new_file = new_path + '/' + str(frame).zfill(5) + file_ext
            new_movie_paths.append(new_file)
            # os.rename(old_file, new_file)
    return new_movie_paths


def clean_movie_to_master(movie_path, new_master_dir, keep_frames):

    image_extension = '.png'
    annotation_extensions = ['_00.mat', '_00_ge.mat']
    pov_ext = '_00_fr.mat'

    old_data_dir, split, subdivided_cats, video_dir = movie_path.split('/')
    annotation_split = 'new_' + split + '_wbox'
    old_movie_dir = '/'.join([old_data_dir, split, subdivided_cats, video_dir])
    old_annotation_dir = '/'.join([old_data_dir, annotation_split, subdivided_cats, video_dir])

    new_master_path = '/'.join([new_master_dir, split, subdivided_cats, video_dir])
    new_annotation_path = '/'.join([new_master_dir, annotation_split, subdivided_cats, video_dir])
    # fr_annotation_path = new_master_dir + '/viewpoint_annotations/' + split + '/' + video_dir
    # split_single_movie(old_movie_dir, keep_frames, new_master_path, image_extension)
    # for ext in annotation_extensions:
    #     split_single_movie(old_annotation_dir, keep_frames, new_annotation_path, ext)

    # split_single_movie(old_annotation_dir, keep_frames, fr_annotation_path, pov_ext)
    return


def move_confirmed_to_master():
    pass


def get_name_parts(dname):
    try:
        pvn, mvn, submvn = dname.split('_')
        return pvn, mvn, submvn
    except ValueError:
        pvn, mvn = dname.split('_')
        return pvn, mvn, 0


def clean_category_to_master(confirmation_log, category, data_path, new_master_dir):
    dir_changes = []

    movie_dirs = return_non_hidden(data_path + category)
    parent_idx = 0
    current_parent = 0
    child_index = 0
    copies_detected = False

    movies_with_splits = []
    for movie in movie_dirs:

        movie_path = data_path + category + '/' + movie

        keep_frames = confirmation_log[movie_path]
        if keep_frames == 'flagged':
            pass
        if keep_frames == 'confirmed':
            movies_with_splits.append(movie)
        else:
            # print(movie_path, new_master_dir, keep_frames)
            # clean_movie_to_master(movie_path, new_master_dir, keep_frames)
            # print(split_single_movie(movie_dirs, keep_frames))
            pass

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

        keep_frames = confirmation_log[movie_path]
        if keep_frames == 'flagged':
            pass
        if keep_frames == 'confirmed':
            move_confirmed_to_master()
        else:
            pass
            # print(movie_path, new_master_dir, keep_frames)
            # clean_movie_to_master(movie_path, new_master_dir, keep_frames)
    return dir_changes


def confirmed():
    pass


def return_non_hidden(path):
    all_files = os.listdir(path)
    return [file for file in all_files if not file.startswith('.')]


def clean_all_data(data_path, confirmation_log):

    movie_frames_dict = {}
    with open(confirmation_log, 'r') as f:
        log_f = f.readlines()
    for movie in log_f:
        index, movie_path, keep_frames = movie.split(', ', maxsplit=2)
        # print(index, movie_path, keep_frames)
        try:
            movie_frames_dict[movie_path] = ast.literal_eval(keep_frames)
        except ValueError:
            movie_frames_dict[movie_path] = keep_frames.strip()
    categories = return_non_hidden(data_path)
    clean_category_to_master(movie_frames_dict, categories[8], data_path, 'test_real')
    return clean_category_to_master(movie_frames_dict, categories[8], data_path, 'test_real')



