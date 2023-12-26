import cv2
from pathlib import Path

def resize_video(input_video_path):
	# Path to your input video file

	# Path to your output video file
	output_video_path = str(Path(__file__).resolve().parent.parent) + '//videoResized//resized.mp4'

	# Open the input video file
	cap = cv2.VideoCapture(input_video_path)

	# Get the original video's width, height, and frames per second (fps)
	original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
	original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

	new_width = 587
	new_height = int(original_height * 587 / original_width)

	fps = int(cap.get(cv2.CAP_PROP_FPS))

	# Create a VideoWriter object to save the resized video
	fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')  # You can change the codec as needed
	#fourcc = cv2.VideoWriter_fourcc(*'XVID')  # You can change the codec as needed
	out = cv2.VideoWriter(output_video_path, fourcc, fps, (new_width, new_height), True)

	while True:
		ret, frame = cap.read()
		if not ret:
			break  # Break the loop if there are no more frames

		# Resize the frame to the new width and height
		resized_frame = cv2.resize(frame, (new_width, new_height))

		# Write the resized frame to the output video
		out.write(resized_frame)

	# Release the VideoCapture and VideoWriter objects
	cap.release()
	out.release()

	print("Video resized and saved successfully.")

	return output_video_path
