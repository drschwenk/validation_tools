import os
import ast


def split_single_movie(movie_dir, frame_spans, new_path, file_ext):
    """
    splits and moves frames of a single movie to the new master
    """

    # this removes the data dir from the path
    # os.makedirs(new_path)
    for span in frame_spans:
        for frame in range(int(span[0]), int(span[1])+1):
            old_file = movie_dir + '/' + str(frame).zfill(5) + file_ext
            new_file = new_path + '/' + str(frame).zfill(5) + file_ext
            print(old_file, new_file)
            # os.rename(old_file, new_file)
    return


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
    fr_annotation_path = new_master_dir + '/viewpoint_annotations/' + split + '/' + video_dir
    # split_single_movie(old_movie_dir, keep_frames, new_master_path)i
    # for ext in annotation_extensions:
    #     split_single_movie(old_annotation_dir, keep_frames, new_annotation_path, ext)

    split_single_movie(old_annotation_dir, keep_frames, fr_annotation_path, pov_ext)
    return


def clean_all_to_master(confirmation_log, new_master_dir):
    with open(confirmation_log, 'r') as f:
        movie_splits = f.readlines()

    for movie in movie_splits:
        index, movie_path, keep_frames = movie.split(', ', maxsplit=2)
        frame_list = ast.literal_eval(keep_frames)
    clean_movie_to_master(movie_path, new_master_dir, frame_list)
    return


