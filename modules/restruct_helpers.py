import os


def get_name_parts(dir_name):
    try:
        pvn, mvn, sub_mov_n = dir_name.split('_')
        return pvn, mvn, sub_mov_n
    except ValueError:
        pvn, mvn = dir_name.split('_')
        return pvn, mvn, 0


def return_non_hidden(path):
    all_files = os.listdir(path)
    return [file for file in all_files if not file.startswith('.')]


def reset_logfile(logfile):
    os.remove(logfile)


def append_to_change_log(new_path, old_path, logfile):
    with open(logfile, 'a') as log:
        log.write('moving ' + old_path + ' to ' + new_path + '\n')


def make_new_dir_structure(confirmation_log, category, data_path):
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
