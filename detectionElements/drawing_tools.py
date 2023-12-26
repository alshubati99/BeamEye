import collections
import numpy as np
import cv2
import PIL.Image as Image
import PIL.ImageDraw as ImageDraw
import PIL.ImageFont as ImageFont

count = 0

def convert_and_draw_box(image,
                         y_min,
                         x_min,
                         y_max,
                         x_max,
                         color,
                         thickness=4,
                         display_str_list=(),
                         labels=False,
                         crowd=False,
                         accuracy=False,
                         ):
	# Check if the image is in BGR format
	if image.shape[-1] == 3:  # If the image has 3 channels
		is_bgr = True
		# Convert BGR to RGB
		image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	else:
		is_bgr = False
		image_rgb = image

	# Convert to PIL Image
	image_from_image_array = Image.fromarray(np.uint8(image_rgb)).convert('RGB')
	draw_box(image_from_image_array, y_min, x_min, y_max, x_max, color,
	         thickness, display_str_list,
	         labels,
	         crowd,
	         accuracy)

	# Convert back to numpy array
	modified_array = np.array(image_from_image_array)

	# Convert back to BGR if the original image was in BGR
	if is_bgr:
		modified_array = cv2.cvtColor(modified_array, cv2.COLOR_RGB2BGR)

	# Copy the modified array back to the original image
	np.copyto(image, modified_array)



def draw_box(image,
             y_min,
             x_min,
             y_max,
             x_max,
             color,
             thickness=4,
             display_str_list=(),
             labels=False,
             crowd=False,
             accuracy=False,

             ):
	draw = ImageDraw.Draw(image)
	im_width, im_height = image.size

	(left, right, top, bottom) = (x_min * im_width, x_max * im_width,
	                              y_min * im_height, y_max * im_height)

	global count

	draw.line([(left, top), (left, bottom), (right, bottom),
	           (right, top), (left, top)], width=thickness, fill=color)
	# color decided here
	count += 1
	try:
		font = ImageFont.truetype('arial.ttf', 26)
	except IOError:
		font = ImageFont.load_default()


	if labels or accuracy:

		className, acc = display_str_list[0].split(": ")
		if crowd:
			className = "Crowd"
			display_str_list[0] = f"{className}: {acc}"

		if not accuracy:
			display_str_list = [className]

		if not labels:
			display_str_list = [acc]
		# if both, string will have both from parameter
		display_str_heights = [font.getsize(ds)[1] for ds in display_str_list]
		# Each display_str has a top and bottom margin of 0.05x.
		total_display_str_height = (1 + 2 * 0.05) * sum(display_str_heights)

		if top > total_display_str_height:
			text_bottom = top
		else:
			text_bottom = bottom + total_display_str_height
		# Reverse list and print from bottom to top.
		for display_str in display_str_list[::-1]:
			text_width, text_height = font.getsize(display_str)
			margin = np.ceil(0.05 * text_height)
			draw.rectangle(
				((left, text_bottom - text_height - 2 * margin),
				 (left + text_width, text_bottom)), fill=color)
			draw.text(
				(left + margin, text_bottom - text_height - margin),
				display_str,
				fill='black',
				font=font)
			text_bottom -= text_height - 2 * margin


def draw_boxes_on_image_array(image,
                              boxes,
                              classes,
                              scores,
                              category_index,
                              min_score_thresh=.3,
                              line_thickness=4,
                              labels=False,
                              crowd=False,
                              accuracy=False,
                              pedestrian_color='undefined',
                              crowd_color='undefined',
                              ):

	box_to_display_str_map = collections.defaultdict(list)

	filtered_boxes = boxes
	offset = 0

	for i in range(boxes.shape[0]):
		if (classes[i] not in category_index) or all(value == 0.0 for value in boxes[i]) or scores[i] is None:
			filtered_boxes = np.delete(filtered_boxes, [i - offset], axis=0)
			offset += 1
			continue

		if scores[i] >= min_score_thresh:
			box = tuple(boxes[i].tolist())
			class_name = category_index[classes[i]]['name']

			display_str = '{}: {}%'.format(
				class_name,
				int(100 * scores[i]))

			box_to_display_str_map[box].append(display_str)

	intersected_boxes = []
	pedestrian_count_frame = 0
	crowd_count_frame = 0

	if crowd:
		from detectionElements.checkCrowd import check_intersected_boxes
		intersected_boxes, crowd_count_frame = check_intersected_boxes(filtered_boxes)

	precision = 1e-6

	for box in filtered_boxes:

		box = tuple(box.tolist())

		if crowd and not np.any(np.all(np.isclose(intersected_boxes, box, atol=precision), axis=1)):
			continue

		pedestrian_count_frame += 1
		y_min, x_min, y_max, x_max = box

		convert_and_draw_box(
			image,
			y_min,
			x_min,
			y_max,
			x_max,
			color=pedestrian_color,
			thickness=line_thickness,
			display_str_list=box_to_display_str_map[box],
			labels=labels,
			crowd=False,
			accuracy=accuracy,
		)

	if crowd:
		for intersected_box in intersected_boxes:
			intersected_box = tuple(intersected_box.tolist())
			if np.any(np.all(np.isclose(filtered_boxes, intersected_box, atol=precision), axis=1)):
				# already drawn
				continue

			y_min, x_min, y_max, x_max = intersected_box
			convert_and_draw_box(
				image,
				y_min,
				x_min,
				y_max,
				x_max,
				color=crowd_color,
				thickness=line_thickness,
				#display_str_list=box_to_display_str_map[box],
				display_str_list=["Crowd : "],
				labels=labels,
				crowd=True,
				accuracy=accuracy, )

	return image, pedestrian_count_frame, crowd_count_frame
