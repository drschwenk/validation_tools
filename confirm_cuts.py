import json
import numpy as np
from collections import defaultdict
import glob
import cv2
import csv


def get_key(image):
    valid_key_presses = {32: 'pass', 13: 'mark'}
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
    with open(video_name + '/good.txt', 'w') as f:
        f.write(video_name + ' is good')


def show_image(image_name, frame_n):
    drawn_image = cv2.imread(image_name, 0)
    drawn_image = cv2.putText(drawn_image, 'frame ' + frame_n,
                              (15, 40), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), thickness=2)
    cv2.imshow('movie frame', drawn_image)
    return get_key(drawn_image)


def evaluate_video(video_path):
    motion_frames = []
    video_frames = glob.glob(video_path + '/*.png')[:5]
    for image_name in video_frames:
        frame_n = image_name.split('/')[-1].split('.png')[0]
        if show_image(image_name, frame_n) == 'mark':
            motion_frames.append(frame_n)
    if motion_frames:
        return motion_frames
    else:
        confirm(video_path)


def confirm_many_videos(path_prefix='data/prediction_videos_final_'):
    with open('./movies_sorted_by_length.csv', 'r') as f:
        reader = csv.reader(f)
        file_names = [path_prefix + fn[0] for fn in list(reader)]
    for vid in file_names[500:505]:
        print(evaluate_video(vid))


if __name__ == '__main__':
    confirm_many_videos('data/prediction_videos_final_')
