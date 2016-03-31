import os
import ast


def split_single_movie(movie_dir, frame_spans, new_path):
    """
    splits and moves frames of a single movie to the new master
    """

    # this removes the data dir from the path
    file_ext = '.png'
    # os.mkdir(new_path)
    for span in frame_spans:
        for frame in range(int(span[0]), int(span[1])+1):
            old_file = movie_dir+str(frame).zfill(5) + file_ext
            new_file = new_path+str(frame).zfill(5) + file_ext
            print(old_file, new_file)
            # os.rename(old_file, new_file)
    return


def split_single_annotation(movie_dir, frame_spans, new_master_path):
    """
    splits and moves frames of a single movies annotations to the new master
    """
    file_ext = '_00.mat'
    ge_ext = '_00_ge.mat'

    return


def preserve_fr_annotations(movie_dir, frame_spans, new_master_path):
    """
    """
    fr_annotation_dir = 'viewpoint_annotations'
    fr_annotation_path = new_master_path + fr_annotation_dir

    return


def clean_movie_to_master(movie_path, new_master_dir, keep_frames):
    old_data_dir, split, subdivided_cats, video_dir = movie_path.split('/')
    old_movie_dir = '/'.join([old_data_dir, split, subdivided_cats, video_dir])
    
    new_master_path = '/'.join([new_master_dir, split, subdivided_cats, video_dir])

    split_single_movie(old_movie_dir, keep_frames, new_master_path)
    
    return new_master_path


def clean_all_to_master(confirmation_log, new_master_dir):
    movie_splits = []
    with open(confirmation_log, 'r') as f:
        movie_splits = f.readlines()

    for movie in movie_splits:
        index, movie_path, keep_frames = movie.split(', ', maxsplit=2)
        frame_list = ast.literal_eval(keep_frames)
    clean_movie_to_master(movie_path, new_master_dir, frame_list)
    return
