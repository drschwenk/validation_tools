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
        try:
            for frame in range(int(span[0]), int(span[1])+1):
                old_file = movie_dir + '/' + str(frame).zfill(5) + file_ext
                new_file = new_path + '/' + str(frame).zfill(5) + file_ext
                new_movie_paths.append(new_file)
                os.rename(old_file, new_file)
        except ValueError:
            pass
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


def get_name_parts(dname):
    try:
        pvn, mvn, submvn = dname.split('_')
        return pvn, mvn, submvn
    except ValueError:
        pvn, mvn = dname.split('_')
        return pvn, mvn, 0


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
            movie_path_rn = '/'.join([data_dir, split, subdivided_cats + '2', video_dir])
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
            old_movie_path_rn = data_path + subdivided_cats + '2' + '/' + old_name
            keep_frames = movie_frames_dict[old_movie_path_rn]

        if keep_frames == 'confirmed':
            move_confirmed(old_movie_path, new_name, new_master_dir)

        else:
            pass
            move_split(old_movie_path, new_name, new_master_dir, keep_frames)
    pass


def move_split(old_path, new_name, new_master_dir, keep_frames):
    """
    splits and moves frames of a single movie to the new master
    """

    # this removes the data dir from the path
    # os.makedirs(new_path)

    image_extension = '.png'
    annotation_extensions = ['_00.mat', '_00_ge.mat']
    pov_ext = '_00_fr.mat'

    old_data_dir, split, subdivided_cats, video_dir = old_path.split('/')
    annotation_split = 'new_' + split + '_wbox'

    old_annotation_dir = '/'.join([old_data_dir, annotation_split, subdivided_cats, video_dir])

    new_video_path = '/'.join([new_master_dir, split, subdivided_cats, new_name])
    new_annotation_path = '/'.join([new_master_dir, annotation_split, subdivided_cats, new_name])

    file_ext = image_extension
    new_movie_paths = []
    new_frame_idx = 0
    print(new_annotation_path)
    os.makedirs(new_video_path)
    os.makedirs(new_annotation_path)
    for idx, span in enumerate(keep_frames):
        try:
            for frame in range(int(span[0]), int(span[1])+1):
                old_file = old_path + '/' + str(frame).zfill(5) + file_ext
                new_file = new_video_path + '/' + str(new_frame_idx).zfill(5) + file_ext
                new_movie_paths.append(new_file)
                # os.rename(old_file, new_file)

                new_frame_idx += 1
        except ValueError:
            pass

    for idx, span in enumerate(keep_frames):
        for fext in annotation_extensions:
            try:
                for frame in range(int(span[0]), int(span[1]) + 1):
                    old_file = old_annotation_dir + '/' + str(frame).zfill(5) + fext
                    new_file = new_annotation_path + '/' + str(new_frame_idx).zfill(5) + fext
                    new_movie_paths.append(new_file)
                    os.rename(old_file, new_file)
                    new_frame_idx += 1
            except (FileNotFoundError, ValueError) as e:
                pass

    for idx, span in enumerate(keep_frames):
        try:
            for frame in range(int(span[0]), int(span[1]) + 1):
                old_file = old_annotation_dir + '/' + str(frame).zfill(5) + pov_ext
                new_file = 'pov_frames' + new_annotation_path + '/' + str(new_frame_idx).zfill(5) + pov_ext
                new_movie_paths.append(new_file)
                os.rename(old_file, new_file)
                new_frame_idx += 1
        except (FileNotFoundError, ValueError) as e:
            pass
    return


def move_confirmed(old_path, new_name, new_master_dir):
    old_data_dir, split, subdivided_cats, video_dir = old_path.split('/')
    annotation_split = 'new_' + split + '_wbox'
    old_annotation_dir = '/'.join([old_data_dir, annotation_split, subdivided_cats, video_dir])

    new_video_path = '/'.join([new_master_dir, split, subdivided_cats, new_name])
    new_annotation_path = '/'.join([new_master_dir, annotation_split, subdivided_cats, new_name])
    os.makedirs(new_video_path)
    os.makedirs(new_annotation_path)
    # os.rename(old_path, new_video_path)

    return


def return_non_hidden(path):
    all_files = os.listdir(path)
    return [file for file in all_files if not file.startswith('.')]


def clean_all_data(data_path, confirmation_log):

    movie_frames_dict = {}
    with open(confirmation_log, 'r') as f:
        log_f = f.readlines()
    for movie in log_f:
        index, movie_path, keep_frames = movie.split(', ', maxsplit=2)
        # print(movie_path, '\n')
        try:
            movie_frames_dict[movie_path] = ast.literal_eval(keep_frames)
        except ValueError:
            movie_frames_dict[movie_path] = keep_frames.strip()
    categories = return_non_hidden(data_path)
    for cat in categories:
        dir_change = clean_category_to_master(movie_frames_dict, cat, data_path)
        make_category_moves(movie_frames_dict, cat, data_path, 'master', dir_change)
    return

if __name__ == '__main__':
    data_path = 'data/prediction_videos_final_train/'
    clean_all_data(data_path, './combined_log.txt')
