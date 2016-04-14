import os


def get_name_parts(dir_name):
    try:
        pvn, mvn, sub_mov_n = dir_name.split('_')
        return pvn, mvn, sub_mov_n
    except ValueError:
        pvn, mvn = dir_name.split('_')
        return pvn, mvn, 'childless'


def return_non_hidden(path):
    all_files = os.listdir(path)
    return [file for file in all_files if not file.startswith('.')]


def reset_logfile(logfile):
    os.remove(logfile)


def append_to_change_log(new_path, old_path, logfile):
    if old_path != 0:
        with open(logfile, 'a') as log:
            log.write('moving ' + old_path + ' to ' + new_path + '\n')
    else:
        with open(logfile, 'a') as log:
            log.write(new_path + ' was not included' + '\n')


def formatted_change(parent_idx, child_idx, movie):
    return [str(parent_idx).zfill(3) + '_' + str(child_idx).zfill(2), movie]


def generate_new_dir_structure(confirmation_log, category, old_path, new_path, change_log, resume_index=0):
    directory_renaming_instructions = []
    movie_dirs = return_non_hidden(old_path)
    subdivided_movies = []
    for movie in movie_dirs:
        movie_path = old_path + movie
        data_dir, split, subdivided_cats, video_dir = movie_path.split('/')
        movie_path = '/'.join([data_dir, split, subdivided_cats, video_dir])
        try:
            keep_frames = confirmation_log[movie_path]
        except KeyError:
            try:
                keep_frames = confirmation_log[movie_path.replace('final_train', '3_categories')]
            except KeyError:
                keep_frames = confirmation_log[movie_path.replace('final_test', '3_categories')]


        if keep_frames == 'flagged':
            append_to_change_log(movie_path, 0, change_log)
        elif keep_frames == 'confirmed':
            subdivided_movies.append(movie)
        else:
            if len(keep_frames) > 1:
                for idx, span in enumerate(keep_frames):
                    subdivided_movies.append(movie + '_' + str(idx))
            else:
                subdivided_movies.append(movie)

    parent_idx = resume_index
    current_parent = resume_index
    child_idx = 0
    for movie in subdivided_movies:
        parent_number, inter_n, sub_n = get_name_parts(movie)
        if parent_number != current_parent:
            current_parent = parent_number
            parent_idx += 1
            child_idx = 0
        else:
            child_idx += 1
        path_change = formatted_change(parent_idx, child_idx, movie)
        directory_renaming_instructions.append([new_path + path_change[0], old_path + path_change[1]])

    return directory_renaming_instructions
