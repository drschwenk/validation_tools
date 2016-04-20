#! /usr/bin/env python

import glob
import cv2
import csv
import os
import argparse
from scipy.io.matlab import loadmat
from subprocess import run
from subprocess import check_output


def get_key(image):
    valid_key_presses = {32: 'pass', 13: 'mark', 8: 'restart image', 98: 'back', 127: 'del', 102: 'flag', 110: 'next',
                         108: 'last', 114: 'advance_10'}
    while True:
        user_key = cv2.waitKey(0)
        if user_key in valid_key_presses:
            pass
        elif user_key == 27:
            new_image = cv2.putText(image, 'quit', (30, 80), cv2.FONT_HERSHEY_PLAIN, 2, (192, 192, 192),
                                    thickness=2)
            cv2.imshow('movie frame', new_image)
            cv2.waitKey(800)
            exit()
        else:
            new_image = cv2.putText(image, 'try again', (30, 110), cv2.FONT_HERSHEY_PLAIN, 2, (192, 192, 192),
                                    thickness=2)
            cv2.imshow('movie frame', new_image)
            continue
        return valid_key_presses[user_key]


def show_image(image_name, frame_n, idx, annotation_path, n_frames_total):
    category = image_name.split('/')[2]
    drawn_image = cv2.imread(image_name, 0)
    drawn_image = cv2.putText(drawn_image, 'idx= ' + str(idx) + '  frame= ' + frame_n + ' of ' + str(n_frames_total),
                              (15, 40), cv2.FONT_HERSHEY_PLAIN, 2, (192, 192, 192), thickness=2)
    drawn_image = cv2.putText(drawn_image, category, (15, 75), cv2.FONT_HERSHEY_PLAIN, 2, (192, 192, 192), thickness=2)
    draw_annotations(frame_n, annotation_path, drawn_image)
    cv2.imshow('movie frame', drawn_image)
    return get_key(drawn_image)


def draw_annotations(frame_n, annotation_path, drawn_image):
    annotation_file = annotation_path + '/' + frame_n + '_00.mat'
    if os.path.isfile(annotation_file):
        mat_file = loadmat(annotation_file)
        bnd_box = mat_file['box']
        cv2.rectangle(drawn_image, tuple([int(bnd_box[0][0]), int(bnd_box[0][1])]),
                      tuple([int(bnd_box[0][2]), int(bnd_box[0][3])]),
                      color=(192, 192, 192), thickness=1)
    else:
        cv2.putText(drawn_image, 'no annotation', (50, 90), cv2.FONT_HERSHEY_PLAIN, 2, (192, 192, 192), thickness=2)


def evaluate_video(video_path, video_idx, annotation_file):

    def add_mark(frame_range, marked_frame):
        range_complete = False
        if frame_range == [0, 0]:
            frame_range[0] = marked_frame
        elif int(frame_n) > int(frame_range[0]):
            frame_range[1] = frame_n
            range_complete = True
        return frame_range, range_complete

    motion_frames = []
    current_frame_range = [0, 0]
    video_frames = glob.glob(video_path + '/*.png')
    frame_n = 0
    idx = 0
    while idx < len(video_frames):
        image_name = video_frames[idx]
        frame_n = image_name.split('/')[-1].split('.png')[0]
        key_pressed = show_image(image_name, frame_n, video_idx, annotation_file, len(video_frames))
        if key_pressed == 'mark':
            new_range, complete = add_mark(current_frame_range, frame_n)
            if complete:
                motion_frames.append(new_range)
                current_frame_range = [0, 0]
            else:
                current_frame_range = new_range
        elif key_pressed == 'back':
            idx = max(idx - 1, 0)
            continue
        elif key_pressed == 'del':
            return 'previous image'
        elif key_pressed == 'flag':
            return 'flagged'
        elif key_pressed == 'next':
            idx = len(video_frames) - 1

        elif key_pressed == 'last':
            idx = len(video_frames) - 2
        elif key_pressed == 'advance_10':
            idx += 10
        idx += 1

    if current_frame_range[0] != 0 and current_frame_range[1] == 0:
        motion_frames.append(add_mark(current_frame_range, frame_n)[0])
    if motion_frames:
        return motion_frames
    else:
        return 'confirmed'


def write_log(idx, vid, evaluation, logfile):
    with open(logfile, 'a') as log:
        log.write(str(idx) + ', ' + vid + ', ' + str(evaluation) + '\n')


def confirm_many_videos(path_prefix, logfile,
                        starting_idx, stable_image_idx_offset, sorted_file_list):
    starting_idx += stable_image_idx_offset

    with open(sorted_file_list, 'r') as f:
        reader = csv.reader(f)
        file_names = ['master_data/' + path_prefix + fn[0] for fn in list(reader)]
    idx = starting_idx
    while idx < len(file_names):
        image_file_name = file_names[idx]
        this_prefix = image_file_name.split('/', maxsplit=2)
        this_prefix = this_prefix[1]
        annotation_file_name = image_file_name.replace(this_prefix, 'new_' + this_prefix + '_wbox')
        evaluation = evaluate_video(image_file_name, idx, annotation_file_name)
        if evaluation == 'previous image':
            idx -= 1
            run('sed -i "" -e  "$ d " ' + logfile, shell=True)
            continue
        write_log(idx, file_names[idx], evaluation, logfile)
        idx += 1


def view_results(path_prefix, starting_idx):
    f_path = 'master_data/' + path_prefix + '*/*/*'
    # print(f_path)
    file_list = glob.glob(f_path)
    # print(file_list)
    idx = starting_idx
    while idx < len(file_list):
        image_file_name = file_list[idx]
        this_prefix = image_file_name.split('/', maxsplit=2)
        this_prefix = this_prefix[1]
        annotation_file_name = image_file_name.replace(this_prefix, 'new_' + this_prefix + '_wbox')
        evaluation = evaluate_video(image_file_name, idx, annotation_file_name)
        idx += 1


def main():
    parser = argparse.ArgumentParser(description='Make confirmation and editing pass through VIND videos')
    parser.add_argument("-l", "--log", help="log file name")
    parser.add_argument("-i", "--startindex", help="starting index")
    parser.add_argument("-r", "--resume", help="resume", action="store_true")
    args = parser.parse_args()
    stable_image_idx_offset = 0
    starting_idx = 0
    if args.startindex:
        starting_idx = int(args.startindex)
    if args.resume:
        last_line = check_output('tail -1 ' + args.log, shell=True)
        starting_idx = int(last_line.split(b',')[0]) - stable_image_idx_offset + 1

    sorted_file_list = 'only_throwing.csv'
    prefix = 'prediction_videos_final_'
    # confirm_many_videos(prefix, args.log, starting_idx, stable_image_idx_offset, sorted_file_list)
    view_results(prefix, starting_idx)

if __name__ == '__main__':
    main()
