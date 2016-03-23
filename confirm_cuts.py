#! /usr/bin/env python

import glob
import cv2
import csv
import argparse
from subprocess import run


def get_key(image):
    valid_key_presses = {32: 'pass', 13: 'mark', 8: 'restart image', 98: 'back', 127: 'del'}
    while True:
        user_key = cv2.waitKey(0)
        if user_key in valid_key_presses:
            pass
        elif user_key == 27:
            new_image = cv2.putText(image, 'quit', (30, 80), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), thickness=2)
            cv2.imshow('movie frame', new_image)
            cv2.waitKey(800)
            exit()
        else:
            new_image = cv2.putText(image, 'try again', (30, 80), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), thickness=2)
            cv2.imshow('movie frame', new_image)
            continue
        return valid_key_presses[user_key]


def confirm(video_name):
    # with open(video_name + '/good.txt', 'w') as f:
    #     pass
        # f.write(video_name + ' is good')
    return 'confirmed'


def show_image(image_name, frame_n):
    drawn_image = cv2.imread(image_name, 0)
    drawn_image = cv2.putText(drawn_image, 'frame ' + frame_n,
                              (15, 40), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), thickness=2)
    cv2.imshow('movie frame', drawn_image)
    return get_key(drawn_image)


def evaluate_video(video_path):

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
    idx = 0
    while idx < len(video_frames):
        image_name = video_frames[idx]
        frame_n = image_name.split('/')[-1].split('.png')[0]
        key_pressed = show_image(image_name, frame_n)
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
        idx += 1
    if motion_frames:
        return motion_frames
    else:
        return confirm(video_path)


def write_log(idx, vid, evaluation, logfile):
    with open(logfile, 'a') as log:
        log.write(str(idx) + ', ' + vid + ', ' + str(evaluation) + '\n')


def confirm_many_videos(path_prefix='data/prediction_videos_final_', logfile='pass.log', starting_idx=0):
    stable_image_idx_offset = 294           # skips stable images
    starting_idx += stable_image_idx_offset

    with open('./movies_sorted_by_length.csv', 'r') as f:
        reader = csv.reader(f)
        file_names = [path_prefix + fn[0] for fn in list(reader)]

    idx = starting_idx
    while idx < len(file_names[starting_idx:]):
        evaluation = evaluate_video(file_names[idx])
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
    args = parser.parse_args()
    starting_idx = 0
    if args.startindex:
        starting_idx = int(args.startindex)
    confirm_many_videos('data/prediction_videos_final_', 'first_pass.log', starting_idx)

if __name__ == '__main__':
    main()

