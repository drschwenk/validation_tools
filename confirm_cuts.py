import json
import numpy as np
from collections import defaultdict
import glob
import cv2


def confirm(video_name):
    with open('good.txt','w') as f:
        f.write(video_name + ' is good')


def get_user_key(image, windowName, imageClasses):
    while True:
        user_key = cv2.waitKey(0)
        if(user_key == 'a'):
            pass
        return


def show_image(image_name):
    drawn_image = cv2.imread(image_name, 0)
    drawn_image = cv2.putText(drawn_image, 'frame ' + image_name.split('/')[-1],
                              (15, 40), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), thickness=2)
    cv2.imshow('movie frame', drawn_image)
    cv2.waitKey(0)


def confirm_video(video_name):
    motion_frames = []

    video_frames = glob.glob('./' + video_name + '/*.png')[:5]
    for image_name in video_frames:
        show_image(image_name)

    return motion_frames

if __name__ == '__main__':
    confirm_video('79_2')