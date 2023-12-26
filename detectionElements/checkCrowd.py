import numpy as np


# Function to check if two boxes intersect
def do_boxes_intersect(box1, box2):
	ymin1, xmin1, ymax1, xmax1 = box1
	ymin2, xmin2, ymax2, xmax2 = box2
	x_overlap = max(0, min(xmax1, xmax2) - max(xmin1, xmin2))
	y_overlap = max(0, min(ymax1, ymax2) - max(ymin1, ymin2))
	return x_overlap > 0 and y_overlap > 0


# Function to find the bounding box containing intersecting boxes
def bounding_box(boxes):
	if len(boxes) == 0:
		return None

	# Initialize the bounding box with the first box
	ymin, xmin, ymax, xmax = boxes[0]

	# Loop through the remaining boxes to expand the bounding box
	for box in boxes[1:]:
		if do_boxes_intersect([ymin, xmin, ymax, xmax], box):
			ymin = min(ymin, box[0])
			xmin = min(xmin, box[1])
			ymax = max(ymax, box[2])
			xmax = max(xmax, box[3])

	return [ymin, xmin, ymax, xmax]


# Iterate through the array to find and replace intersecting boxes
def check_intersected_boxes(boxes):
	np.set_printoptions(precision=50)

	# Print the array
	crowds = 0
	i = 0
	while i < boxes.shape[0]:
		j = i + 1
		while j < boxes.shape[0]:
			if do_boxes_intersect(boxes[i], boxes[j]):
				# Find the bounding box containing both intersecting boxes
				bounding = bounding_box([boxes[i], boxes[j]])

				# Remove the intersecting boxes from the array
				boxes = np.delete(boxes, [i, j], axis=0)

				# Append the bounding box to the array
				boxes = np.append(boxes, [bounding], axis=0)

				# Reset the loop to start over
				i = 0
				j = i + 1
				crowds += 1
			else:
				j += 1
		i += 1

	return boxes, crowds
