import time

import numpy as np
import os
from shutil import copy2
import tensorflow as tf
from time import sleep
import cv2
from detectionElements import label_map_util, drawing_tools

tf.compat.v1.disable_v2_behavior()
tf.TF_ENABLE_ONEDNN_OPTS = 0


# sys.path.insert(0, 'detectionElements')

detection_graph = tf.Graph()
with detection_graph.as_default():
	od_graph_def = tf.compat.v1.GraphDef()
	tf.compat.v1.disable_v2_behavior()
	with tf.io.gfile.GFile('detectionElements/_detectionModel.pb', 'rb') as fid:
		serialized_graph = fid.read()
		od_graph_def.ParseFromString(serialized_graph)
		tf.import_graph_def(od_graph_def, name='')

NUM_CLASSES = 50
label_map = label_map_util.load_labelmap('detectionElements/person_label_map.pbtxt')
categories = label_map_util.convert_label_map_to_categories(
	label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)


def save_frame(frame_number, frame):
	frame_name = "0" * (5 - len(str(frame_number))) + str(frame_number)
	cv2.imwrite(f"videoFrames//frame_{frame_name}.jpg", frame)


def empty_frames_folder():
	for frame in os.listdir("videoFrames"):
		os.remove(f"videoFrames//{frame}")




def frames_to_video(fps, output_folder='videoOut//'):
	output_folder += "//"
	image_folder = 'videoFrames//'
	video_name = output_folder + 'video.avi'

	images = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]
	# print(images)
	frame = cv2.imread(os.path.join(image_folder, images[0]))
	height, width, layers = frame.shape
	fourcc = cv2.VideoWriter_fourcc(*'XVID')
	video = cv2.VideoWriter(video_name, fourcc, fps, (width, height))

	# print(video_name)

	for image in images:
		video.write(cv2.imread(os.path.join(image_folder, image)))

	copy2(video_name, video_name[:-4] + "_copy.avi")
	cv2.destroyAllWindows()
	video.release()

	import uiElements.sharedVariables as User
	User.frames_progress = 100
	User.finished = True
	User.output_video = video_name


def detect():
	import uiElements.sharedVariables as User
	User.finished = False
	while User.wait:
		sleep(2)
		print("waiting")

	else:
		print("Got Video")
		User.wait = True
		from detectionElements.resizeVideo import resize_video
		high_res = User.high_res
		if not high_res:
			resized_video = resize_video(User.input_video_path)
			if resized_video:
				cap = cv2.VideoCapture(resized_video)
				print("resized video")
				User.input_video_path = resized_video
				print(cap)
		else:
			cap = cv2.VideoCapture(User.input_video_path)
			print("didnt resize video")
			# User.input_video_path = None
			print(User.input_video_path)
			print(cap)

	with open("uiElements//userSettings.txt", "r", encoding="utf-8") as f:
		settings = [line.split(" ")[-1] for line in f.read().split("\n")]
	include_labels, include_crowd, include_accuracy, pedestrian_color, crowd_color, output_path = settings
	output_path = output_path.replace("_SPACE_", " ")
	include_labels, include_crowd, include_accuracy, pedestrian_color, crowd_color = int(include_labels), int(
		include_crowd), int(include_accuracy), int(pedestrian_color), int(crowd_color)
	# in settings {1: "blue", 2: "purple", 3: "red", 4: "orange", 5: "yellow", 6: "green"}
	color_dict = {1: "#0094FF", 2: "#FF00F6", 3: "red", 4: "#FF6A00", 5: "yellow", 6: "#26FF5C"} # {1: "red", 2: "purple", 3: "blue", 4: "DodgerBlue", 5: "DeepSkyBlue", 6: "#00FF0C"}
	pedestrian_color = color_dict[pedestrian_color]
	crowd_color = color_dict[crowd_color]

	frame_rate = int(cap.get(cv2.CAP_PROP_FPS))

	fps = cap.get(cv2.CAP_PROP_FPS)

	video_frames_total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

	frame_count = 0
	video_frame_count = 0
	pedestrian_count_second, crowd_count_second = [], []
	# pedestrian_count_frame, crowd_count_frame = 0, 0

	def begin():

		empty_frames_folder()

		nonlocal frame_count, video_frame_count, pedestrian_color, crowd_color, cap

		with detection_graph.as_default():

			with tf.compat.v1.Session(graph=detection_graph) as sess:

				frames_left = 100  # percent
				pedestrian_count_frame, crowd_count_frame = 0, 0
				increment_progress_bar = 0

				while True:

					frame_count += 1

					if increment_progress_bar >= 2.28 * video_frames_total / 100:
						frames_left -= 2.28

						User.frames_progress += 2
						print(
							f"Processed {100 - frames_left:.2f}% of frames, {frames_left:.2f}% left. Progress Bar: {User.frames_progress}")
						increment_progress_bar = 0
					# if frame_count == frame_rate+1:
					success, image_np = cap.read()

					if not success:
						print('EOF')
						break

					# flatten image using numpy
					image_np_expanded = np.expand_dims(image_np, axis=0)
					image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
					boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
					scores = detection_graph.get_tensor_by_name('detection_scores:0')
					classes = detection_graph.get_tensor_by_name('detection_classes:0')
					num_detections = detection_graph.get_tensor_by_name('num_detections:0')
					(boxes, scores, classes, num_detections) = sess.run(
						[boxes, scores, classes, num_detections],
						feed_dict={image_tensor: image_np_expanded})

					# Visualization of the results of a detection.
					_, tmp_pedestrian_count_frame, tmp_crowd_count_frame = drawing_tools.draw_boxes_on_image_array(
						image_np,
						np.squeeze(boxes),
						np.squeeze(classes).astype(np.int32),
						np.squeeze(scores),
						category_index,
						line_thickness=2,
						labels=include_labels,  # bool(include_labels),
						crowd=include_crowd,
						accuracy=include_accuracy,  # bool(include_accuracy),
						pedestrian_color=pedestrian_color,
						crowd_color=crowd_color,
					)
					# 30 fps,
					if frame_count >= frame_rate:
						pedestrian_count_frame, crowd_count_frame = max(
							pedestrian_count_frame, tmp_pedestrian_count_frame
						), max(
							crowd_count_frame, tmp_crowd_count_frame
						)

						pedestrian_count_second.append(pedestrian_count_frame)
						crowd_count_second.append(crowd_count_frame)

						pedestrian_count_frame, crowd_count_frame = 0, 0
						frame_count = 0

					video_frame_count += 1
					save_frame(video_frame_count, image_np)

					increment_progress_bar += 1

				User.frame_rate = fps
				frames_to_video(fps, output_folder=output_path)


	begin()

	cap.release()
	User.pedestrian_count_second, User.crowd_count_second = pedestrian_count_second, crowd_count_second
	User.finished = True


while True:
	detect()
	sleep(5)
