import threading
from time import sleep
import random

input_video_path = None

wait = True

pedestrian_count_second, crowd_count_second = [0], [0]  # [0 for _ in range(30)], [0 for _ in range(30)]

finished = False

high_res = False

frames_progress = 0  # percent

output_video = None

frame_rate = 1

default="""input_video_path = None

wait = True

pedestrian_count_second, crowd_count_second = [0], [0]  # [0 for _ in range(30)], [0 for _ in range(30)]

finished = False

high_res = False

frames_progress = 0  # percent

output_video = None

frame_rate = 1"""