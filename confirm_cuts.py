#! /usr/bin/env python

import glob
import cv2
import csv
import argparse
from subprocess import run
from subprocess import check_output


def get_key(image):
    valid_key_presses = {32: 'pass', 13: 'mark', 8: 'restart image', 98: 'back', 127: 'del', 102: 'flag'}
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

"""
def confirm(video_name):
    return 'confirmed'
"""


def show_image(image_name, frame_n, idx):
    category = image_name.split('/')[2]
    drawn_image = cv2.imread(image_name, 0)
    drawn_image = cv2.putText(drawn_image, 'idx= ' + str(idx) + '  frame= ' + frame_n,
                              (15, 40), cv2.FONT_HERSHEY_PLAIN, 2, (192, 192, 192), thickness=2)
    drawn_image = cv2.putText(drawn_image, category, (15, 75), cv2.FONT_HERSHEY_PLAIN, 2, (192, 192, 192), thickness=2)
    cv2.imshow('movie frame', drawn_image)
    return get_key(drawn_image)


def evaluate_video(video_path, video_idx):

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
        key_pressed = show_image(image_name, frame_n, video_idx)
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


def confirm_many_videos(path_prefix='data/prediction_videos_final_', logfile='pass.log',
                        starting_idx=0, stable_image_idx_offset=0):
    starting_idx += stable_image_idx_offset

    with open('./movies_sorted_by_length.csv', 'r') as f:
        reader = csv.reader(f)
        file_names = [path_prefix + fn[0] for fn in list(reader)]

    idx = starting_idx
    while idx < len(file_names[starting_idx:]):
        evaluation = evaluate_video(file_names[idx], idx)
        if evaluation == 'previous image':
            idx -= 1
            run('sed -i "" -e  "$ d " ' + logfile, shell=True)
            continue
        write_log(idx, file_names[idx], evaluation, logfile)
        idx += 1


def main():
    parser = argparse.ArgumentParser(description='Make confirmation and editing pass through VIND videos')
    parser.add_argument("-l", "--log", help="log file name")
    parser.add_argument("-i", "--startindex", help="starting index")
    parser.add_argument("-r", "--resume", help="resume", action="store_true")
    args = parser.parse_args()
    stable_image_idx_offset = 294
    starting_idx = 0
    if args.startindex:
        starting_idx = int(args.startindex)
    if args.resume:
        last_line = check_output('tail -1 ' + args.log, shell=True)
        starting_idx = int(last_line.split(b',')[0]) - stable_image_idx_offset + 1

    confirm_many_videos('data/prediction_videos_final_', args.log, starting_idx, stable_image_idx_offset)


if __name__ == '__main__':
    main()



