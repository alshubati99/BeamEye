import os.path
import shutil
import tkinter as tk
from tkinter import PhotoImage, filedialog, messagebox
import customtkinter as ctk
from uiElements.tkVideoPlayer import TkinterVideo
from uiElements.SettingsWindow import open_settings_window, settings_inherit_root
from time import sleep
import threading
import cv2
from pathlib import Path
from shutil import move
from PIL import Image, ImageTk

input_video_path = ""
thread_crowd, thread_people, threads_started = threading.Thread, threading.Thread, False
current_pd_number_color, current_crowd_number_color = None, None
parent = Path(__file__).resolve().parent
# if called from uiHandler will return uiElements
# if called from BeamEye.py will return GP
# we need GP//uiAssets path for ui assets
# following block is to get path to folder of the app (GP), whatever its (new) name is
# and add \\uiuAssets\\ to it

# if the parent folder isn't GP ==> a sub-folder of GP
while not os.path.isdir(str(parent) + '\\uiAssets\\'):
	# go back to its parent
	parent = parent.parent
GP_path = parent
uiAssets = str(GP_path) + '\\uiAssets\\'

root = tk.Tk()
root.title("BeamEye")
root.iconbitmap(uiAssets + "logo.ico")
# UI has too many elements to control during resizing, especially during video
# playback, we get screen size and base the app window on a smaller area
# before resizing is disabled.
# getting user screen size, change values to test different screen sizes
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
# define window size percentage, max is 1 == screen size
resize_ratio = .75
# setting window size 75% screen size
width, height = int(screen_width * resize_ratio), int((screen_width * resize_ratio) * 9 / 16)
# keeping 16:9 aspect ratio to match videos' placeholders
root.geometry(f"{int(screen_width * resize_ratio)}x{int((screen_width * resize_ratio) * 9 / 16)}")
# disable resizing
root.resizable(False, False)
root.configure(bg="black")

# root.geometry(f"{width}x{height}")

pc = "#30A8E6"
ended = False
crowd_is_included = None
progressbar, progressbar_progress, progressbar_placeholder_label = ctk.CTkProgressBar, 0, tk.Label
current_loading_canvas, current_video_canvas = tk.Canvas, tk.Canvas

# background_image_hello = PhotoImage(file=uiAssets + 'home2.png')
pedestrian_count_second, crowd_count_second = [], []
new_video = False


def set_aspect_ratio():
	s_width = root.winfo_screenwidth()
	s_height = root.winfo_screenheight()

	# Initial aspect ratio adjustment
	new_width = root.winfo_width()
	new_height = int(new_width * 9 / 16)

	# If height exceeds screen, adjust width based on screen height
	if new_height > s_height:
		new_height = s_height
		new_width = int(new_height * 16 / 9)

	# If width now exceeds screen, reduce both to fit within screen
	if new_width > s_width:
		new_width = s_width
		new_height = int(new_width * 9 / 16)

	# Apply the new dimensions
	root.geometry(f"{new_width}x{new_height}")


def new_coordinates(old_x, old_y, old_width=None, old_height=None):
	window_width, window_height = root.winfo_width(), root.winfo_height()
	new_x = old_x * window_width / 1300
	new_y = old_y * window_height / 750
	if old_width is not None:
		new_width = old_width * window_width / 1300
		new_height = old_height * window_width / 750
		return new_x, new_y, new_width, new_height
	return new_x, new_y


def open_hello_window():
	global current_canvas, main_root, w, h

	# upload canvas
	img_ = Image.open(uiAssets + 'home2.png')
	resized_image_ = img_.resize((root.winfo_width(), root.winfo_height()))
	tk_image_ = ImageTk.PhotoImage(resized_image_)
	background_image_hello = tk_image_
	hello_canvas = tk.Canvas(root, width=root.winfo_width() - 4, height=root.winfo_width() - 10)
	current_canvas = hello_canvas
	hello_canvas.place(x=0, y=0)
	hello_canvas.create_image(root.winfo_width() / 2, root.winfo_height() / 2, image=background_image_hello, anchor="c")

	# settings in upload window

	progressbar_placeholder = ctk.CTkProgressBar(master=hello_canvas, height=20,
	                                             width=400, bg_color="#041632", fg_color="#041632",
	                                             progress_color="#30A8E6", border_color="#30A8E6",
	                                             border_width=2, indeterminate_speed=0.01, mode='determinate'
	                                             )
	progressbar_placeholder.place(x=root.winfo_width() / 2 - 200, y=root.winfo_height() / 2 + 60)
	progressbar_placeholder.set(0)

	# settings canvas

	def wait_for_tenserflow_import():
		sleep(1)
		for _ in range(7):  # takes around 7 seconds to import tensorflow
			for __ in range(7):  # each .step() increases the bar by 2%, 7x7x2 = 98% of the bar after 7 seconds
				progressbar_placeholder.step()
			sleep(1 / 7)
		progressbar_placeholder.set(1)  # set the bar to 100%
		sleep(1)
		hello_canvas.destroy()

		return

	threading.Thread(target=wait_for_tenserflow_import).start()


def seconds_to_hhmmss(seconds):
	hours, remainder = divmod(seconds, 3600)
	minutes, seconds = divmod(remainder, 60)
	return "{:02d}:{:02d}:{:02d}".format(int(hours), int(minutes), int(seconds))


def update_current_timestamp(stamp: ctk.CTkLabel, timestamp: str):  # ,
	stamp.configure(text=timestamp)
	pass


video_end = False
current_canvas = None
main_root, w, h = None, 0, 0


def open_video_window():
	global root, current_video_canvas

	# threading.Thread(target=open_hello_window).start()
	video_canvas = tk.Canvas(root, bg="#051735")
	settings_inherit_root(root)
	img = Image.open(uiAssets + 'blurred.png')
	resized_image = img.resize((root.winfo_width(), root.winfo_height()))
	tk_image = ImageTk.PhotoImage(resized_image)
	background_image_loading = tk_image

	def open_load_window():

		global progressbar, progressbar_progress, \
			progressbar_placeholder_label, current_loading_canvas, \
			current_video_canvas, ended, input_video_path
		bg_color = "#031532"
		loading_canvas = ctk.CTkCanvas(root, width=root.winfo_width() - 4, height=root.winfo_height() - 4,
		                               bg=bg_color)  # , bg="#031532")
		loading_canvas.place(x=0, y=0)

		current_loading_canvas = loading_canvas
		loading_canvas.create_image(0, 0, image=background_image_loading, anchor="nw", )
		progressbar = ctk.CTkProgressBar(master=loading_canvas, height=int(20 * root.winfo_height() / 750),
		                                 width=int(400 * root.winfo_width() / 1300), bg_color="#3C3E46",
		                                 fg_color="#4A4C51",  # bg_color: for corner
		                                 # edges, fg_color inside the bar (inactive part)
		                                 progress_color="#49FF3F", border_color="#49FF3F",
		                                 border_width=2, indeterminate_speed=0.01, mode='determinate'
		                                 )
		progressbar.set(0)

		loading_font = ("Lato", int(40 / 750 * root.winfo_height()))

		progressbar_placeholder_label = tk.Label(loading_canvas, text='Waking Up The Robot', font=loading_font,
		                                         foreground="white",
		                                         background="#031532")
		canvas_width = root.winfo_width()
		canvas_height = root.winfo_height()

		# Calculate the position (center horizontally, 0.3 vertically)
		x_p = (canvas_width - progressbar_placeholder_label.winfo_reqwidth()) / 2
		y_p = canvas_height * 0.3

		# Place the label using the place method
		progressbar_placeholder_label.place(x=x_p, y=y_p)

		p1 = tk.Label(loading_canvas, text='Extracting Video Frames...', font=loading_font, foreground="white",
		              background=bg_color)
		p2 = tk.Label(loading_canvas, text='Processing The Frames...', font=loading_font, foreground="white",
		              background=bg_color)
		p3 = tk.Label(loading_canvas, text='Putting The Frames Back Together', font=loading_font, foreground="white",
		              background=bg_color)
		p4 = tk.Label(loading_canvas, text='Almost There', font=loading_font, foreground="white",
		              background=bg_color)
		p5 = tk.Label(loading_canvas, text='All Set!', font=loading_font, foreground="#49FF3F",
		              background=bg_color)
		progress_feedback = [p1, p2, p3, p4, p5]

		def stepper(fill=False):
			# full bar is 100%
			# each step is 2%

			import uiElements.sharedVariables as User

			global progressbar, progressbar_progress, progressbar_placeholder_label, ended
			if ended:
				pass

			progressbar_placeholder_label.place_forget()
			x_position_p = (loading_canvas.winfo_width() - progressbar.winfo_reqwidth()) / 2

			progressbar.place(x=x_position_p, y=root.winfo_height() / 2 + 60)
			progressbar_progress += 2
			div = 100 // (len(progress_feedback) - 1)

			canvas_width_here = loading_canvas.winfo_width()
			canvas_height_here = loading_canvas.winfo_height()

			# Calculate the position (center horizontally, 0.3 vertically)
			x_position = (canvas_width_here - progress_feedback[progressbar_progress // div].winfo_reqwidth()) / 2
			y_position = canvas_height_here * 0.3

			# Place the label using the place method
			progress_feedback[progressbar_progress // div].place(x=x_position, y=y_position)
			progress_feedback[progressbar_progress // div - 1].place_forget()
			progressbar.step()

			if fill:
				progressbar.set(1)
				progressbar.place_forget()
				progress_feedback[-2].place_forget()
				x_position = (canvas_width_here - progress_feedback[-1].winfo_reqwidth()) / 2
				y_position = canvas_height_here * 0.4

				# Place the label using the place method
				progress_feedback[-1].place(x=x_position, y=y_position)

				ended = True
				sleep(2)
				progressbar_progress = 0
				User.frames_progress = 0

				load_video(User.input_video_path, vid_player)
				load_video(User.output_video, vid_player2)

				loading_canvas.destroy()
				root.maxsize()
				User.finished = False
				return

		def fill_pb():
			import uiElements.sharedVariables as User
			global ended
			sleep(1)
			old_progress = 0
			while User.frames_progress != 100:
				for _ in range(old_progress, User.frames_progress, 2):
					stepper()
				old_progress = User.frames_progress

				sleep(.1)

			while not User.finished:
				sleep(.5)
			else:
				stepper(fill=True)
			ended = False
			return

		threading.Thread(target=fill_pb).start()

	def upload_button_func():

		global input_video_path, new_video, thread_people, thread_crowd, threads_started
		input_video_path = filedialog.askopenfilename(initialdir=str(Path(__file__).resolve().parent.parent),
		                                              filetypes=[("Videos", "*.mp4")])
		if not input_video_path:
			return

		nonlocal video_title_label
		new_video = True
		sleep(0.002)
		if (thread_people is not None and thread_crowd is not None) and threads_started:
			thread_people.join()
			thread_crowd.join()
			threads_started = False

		video_title = input_video_path.split("/")[-1]
		video_title_label.configure(text=video_title)
		video_title_label.place(x=45, y=30)
		nonlocal play_pause_button

		play_pause_button.place(x=60 * root.winfo_width() / 1300, y=470 * root.winfo_height() / 750 + 10)
		if input_video_path:
			import uiElements.sharedVariables as User
			User.input_video_path = input_video_path
			User.wait = False
			sleep(0.6)

			open_load_window()

	def update_duration(event):
		nonlocal vid_player, vid_player2
		duration = vid_player.video_info()["duration"]
		progress_slider["to"] = duration

	def play_pause():

		global new_video, thread_people, thread_crowd, threads_started
		if new_video:
			declare_threads()
			thread_people.start()
			thread_crowd.start()
			new_video = False
			threads_started = True
		nonlocal vid_player, vid_player2

		global video_end

		if vid_player.is_paused() and vid_player2.is_paused():
			threading.Thread(target=vid_player.play).start()
			threading.Thread(target=vid_player2.play).start()
			play_pause_button["image"] = pause_button_image

		else:
			vid_player.pause()
			vid_player2.pause()
			play_pause_button["image"] = play_button_image

	def video_ended(event):

		nonlocal vid_player, vid_player2, current_timestamp
		progress_slider.set(progress_slider["to"])
		play_pause_button["image"] = play_button_image
		progress_slider.set(0)
		current_timestamp.configure(text="00:00:00")

	def update_scale(event):
		global video_end
		nonlocal vid_player, vid_player2
		progress_value.set(int(vid_player.current_duration()))
		update_current_timestamp(current_timestamp, seconds_to_hhmmss(vid_player.current_duration()))

	def load_video(video: str, video_player: TkinterVideo):

		nonlocal current_pd_number, current_crowd_number, \
			current_crowd_number_off, max_people_number, \
			max_crowd_number, max_crowd_number_off
		import uiElements.sharedVariables as User

		color_dict = {1: "#0094FF", 2: "#FF00F6", 3: "red", 4: "#FF6A00", 5: "yellow",
		              6: "#26FF5C"}  # {1: "blue", 2: "purple", 3: "red", 4: "orange", 5: "yellow", 6: "green"}
		with open(str(GP_path) + "\\uiElements\\userSettings.txt", "r") as f:
			settings = f.read()
			settings = [line.split(" ")[-1] for line in settings.split("\n")]
			include_labels, include_crowd, include_accuracy, pedestrian_color, crowd_color, output_path = settings
			include_labels, include_crowd, include_accuracy, pedestrian_color, crowd_color = int(include_labels), int(
				include_crowd), int(include_accuracy), int(pedestrian_color), int(crowd_color)

			global crowd_is_included
			crowd_is_included = include_crowd

			if bool(include_crowd):
				current_crowd_number_off.place_forget()
				max_crowd_number_off.place_forget()

				current_crowd_number.place(x=480 / 1300 * video_canvas.winfo_width(),
				                           y=600 / 750 * video_canvas.winfo_height())
				current_crowd_number.configure(text_color=color_dict[crowd_color])

				mc = User.crowd_count_second.index(max(User.crowd_count_second))
				max_crowd_number.configure(text_color=color_dict[crowd_color])
				max_crowd_number.configure(
					text=f"{seconds_to_hhmmss(mc - 1 if mc > 1 else mc)} "
					     f"- {seconds_to_hhmmss(mc + 1 if mc > 1 else mc + 2)}"
					     f"  ({max(User.crowd_count_second)})")
				max_crowd_number.place(x=885 / 1300 * root.winfo_width(), y=600 / 750 * root.winfo_height())
			else:
				current_crowd_number.place_forget()
				max_crowd_number.place_forget()

				current_crowd_number_off.place(x=480 / 1300 * root.winfo_width(), y=600 / 750 * root.winfo_height())
				max_crowd_number_off.place(x=885 / 1300 * root.winfo_width(), y=600 / 750 * root.winfo_height())

			current_pd_number.configure(text_color=color_dict[pedestrian_color])

			mp = User.pedestrian_count_second.index(max(User.pedestrian_count_second))
			max_people_number.configure(text_color=color_dict[pedestrian_color])
			max_people_number.configure(
				text=f"{seconds_to_hhmmss(mp - 1 if mp > 1 else mp)} - "
				     f"{seconds_to_hhmmss(mp + 1 if mp > 1 else mp + 2)}"
				     f"  ({max(User.pedestrian_count_second)})")

		if not video:
			video = filedialog.askopenfilename()

		video_player.load(video)
		progress_slider.configure(to=0, from_=0)
		play_pause_button["image"] = play_button_image
		progress_value.set(0)

	def seek(value):
		vid_player.seek(int(value))
		vid_player.update()
		vid_player2.seek(int(value))
		vid_player2.update()

	video_canvas.pack(fill="both", expand=True)

	current_video_canvas = video_canvas

	def resize_video_canvas():
		video_canvas.config(width=root.winfo_width(), height=root.winfo_height())

	Lato = "Lato"

	video_title_label = tk.Label(root, text='Video Title', font=("Lato", int(20 / 750 * root.winfo_width())),
	                             foreground="white", background="#051736")
	current_timestamp = ctk.CTkLabel(root, text="00:00:00", font=("Lato", int(25 / 750 * root.winfo_width())),
	                                 fg_color="#051635", bg_color="#051635",
	                                 corner_radius=8)
	current_timestamp.place(x=105, y=472)

	pil_image2 = Image.open(uiAssets + 'settings.png')
	settings_button_image = ImageTk.PhotoImage(pil_image2)

	label_a = ctk.CTkLabel(root, text="Max # of People/sec: ", font=("Lato", int(20 / 750 * root.winfo_width())),
	                       fg_color="transparent",
	                       bg_color="#051635", text_color="white",
	                       corner_radius=8)  # .place(x=225, y=550)
	current_pd_number = ctk.CTkLabel(root, text="", font=("Lato", int(30 / 750 * root.winfo_width()), "bold"),
	                                 fg_color="transparent",
	                                 bg_color="#051635", corner_radius=8,
	                                 text_color="#30A8E6")
	current_pd_number.place(x=440, y=545)

	label_b = ctk.CTkLabel(root, text="Max # of Crowds/sec: ", font=("Lato", int(20 / 750 * root.winfo_width())),
	                       fg_color="transparent",
	                       bg_color="#051635", text_color="white",
	                       corner_radius=8)  # .place(x=225, y=600)
	current_crowd_number = ctk.CTkLabel(root, text="", font=("Lato", int(30 / 750 * root.winfo_width()), "bold"),
	                                    fg_color="transparent",
	                                    bg_color="#051635", corner_radius=8,
	                                    text_color="#30A8E6")
	current_crowd_number_off = ctk.CTkLabel(root, text="Off", font=("Lato", int(20 / 750 * root.winfo_width()), "bold"),
	                                        fg_color="transparent",
	                                        bg_color="#051635", corner_radius=8,
	                                        text_color="#FF8484")

	label_c = ctk.CTkLabel(root, text="Max # of Crowds at: ", font=("Lato", int(20 / 750 * root.winfo_width())),
	                       fg_color="transparent",
	                       bg_color="#051635", text_color="white",
	                       corner_radius=8)  # .place(x=650, y=600)
	max_crowd_number = ctk.CTkLabel(root, text="", font=("Lato", int(20 / 750 * root.winfo_width()), "bold"),
	                                fg_color="transparent",
	                                bg_color="#051635", corner_radius=8,
	                                text_color="#30A8E6")
	current_crowd_number_off = ctk.CTkLabel(root, text="Off", font=("Lato", int(20 / 750 * root.winfo_width()), "bold"),
	                                        fg_color="transparent",
	                                        bg_color="#051635", corner_radius=8,
	                                        text_color="#FF8484")

	label_d = ctk.CTkLabel(root, text="Max # of People at: ", font=("Lato", int(20 / 750 * root.winfo_width())),
	                       fg_color="transparent",
	                       bg_color="#051635", text_color="white",
	                       corner_radius=8)  # .place(x=650, y=550)
	max_people_number = ctk.CTkLabel(root, text="", font=("Lato", int(20 / 750 * root.winfo_width()), "bold"),
	                                 fg_color="transparent",
	                                 bg_color="#051635", corner_radius=8,
	                                 text_color="#30A8E6")
	max_crowd_number_off = ctk.CTkLabel(root, text="Off", font=("Lato", int(20 / 750 * root.winfo_width()), "bold"),
	                                    fg_color="transparent",
	                                    bg_color="#051635", corner_radius=8,
	                                    text_color="#FF8484")

	# settings_button_image = PhotoImage(file=uiAssets + 'settings.png')
	settings_open_button = tk.Button(video_canvas,
	                                 image=settings_button_image,
	                                 border=0,
	                                 anchor='n',
	                                 background="#031027",
	                                 activebackground="#031027",
	                                 command=open_settings_window
	                                 )
	settings_open_button.place(x=1205, y=30)

	def resize_settings_button():
		window_width, window_height = root.winfo_width(), root.winfo_height()
		original_image = Image.open(uiAssets + 'settings.png')
		im_w, im_h = original_image.size
		new_size = (int(im_w * window_width / 1300), int(im_h * window_height / 750))
		# Resize the image
		resized_image_ = original_image.resize(new_size)
		# Convert the PIL Image object to a Tkinter PhotoImage object
		tk_resized_image = ImageTk.PhotoImage(resized_image_)

		# Configure the button with the Tkinter-compatible image
		settings_open_button.configure(image=tk_resized_image)
		settings_open_button.place(x=60 * window_width / 1300, y=470 * window_height / 750 + 15)
		settings_open_button.image = tk_resized_image
		settings_open_button.place(x=root.winfo_width() * 0.93, y=root.winfo_height() * 0.02)

	upload_video_button = ctk.CTkButton(root,
	                                    height=60,
	                                    width=333,
	                                    border_width=2,
	                                    corner_radius=8,
	                                    border_color="#30A8E6",
	                                    font=("Lato", int(23 / 750 * root.winfo_width())),
	                                    text='Upload Video   ' + "\U0001F4E4",
	                                    fg_color="#30A8E6",
	                                    bg_color="#071B3D",
	                                    hover_color="#061C42",
	                                    command=upload_button_func,
	                                    )
	upload_video_button.place(x=145, y=665)

	def save_video_func():

		def video_saved_feedback():
			import uiElements.sharedVariables as User
			save_to = filedialog.askdirectory()
			if not save_to:
				return
			try:
				move(User.output_video[:-4] + "_copy.avi", save_to)
			except shutil.Error:
				pass

			nonlocal save_video_button
			save_video_button.configure(text="Saved in Specified Folder!", fg_color="#36BC27", hover_color="#36BC27",
			                            text_color="#071B3D")
			sleep(2)
			save_video_button.configure(text='Save Video   ' + "\U0001F4E5", fg_color="#30A8E6", hover_color="#061C42",
			                            text_color="white")
			return

		threading.Thread(target=video_saved_feedback).start()

	save_video_button = ctk.CTkButton(root,
	                                  height=60,
	                                  width=333,
	                                  border_width=2,
	                                  corner_radius=8,
	                                  border_color="#30A8E6",
	                                  bg_color="#071B3D",
	                                  font=("Lato", int(23 / 750 * root.winfo_width())),
	                                  text='Save Video   ' + "\U0001F4E5",
	                                  fg_color="#30A8E6",
	                                  hover_color="#061C42",
	                                  command=save_video_func
	                                  )
	save_video_button.place(x=482, y=665)

	def screenshot():

		import uiElements.sharedVariables as User

		def screenshot_saved_feedback():
			nonlocal screenshot_button
			screenshot_button.configure(text="Saved in ScreenShots/", fg_color="#36BC27",
			                            hover_color="#36BC27", text_color="#071B3D")
			sleep(2)
			screenshot_button.configure(text='ScreenShot   ' + "\U0001F4F7", fg_color="#30A8E6", hover_color="#061C42",
			                            text_color="white")
			return

		video_path = User.output_video
		cap = cv2.VideoCapture(video_path)
		frame_number_to_save = vid_player2.current_frame_number()
		cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number_to_save - 1)
		ret, frame = cap.read()
		if ret:
			output_folder = str(GP_path) + '\\ScreenShots\\'
			frame_filename = f'ScreenShot_{frame_number_to_save}.jpg'
			output_path = output_folder + frame_filename

			cv2.imwrite(output_path, frame)

			threading.Thread(target=screenshot_saved_feedback).start()
			print(f"Saved frame {frame_number_to_save} as {frame_filename} in {output_folder}")
		else:
			print(f"Frame {frame_number_to_save} does not exist in the video")
		cap.release()

	screenshot_button = ctk.CTkButton(root,
	                                  height=60,
	                                  width=350,
	                                  border_width=2,
	                                  corner_radius=8,
	                                  border_color="#30A8E6",
	                                  font=("Lato", int(23 / 750 * root.winfo_width())),
	                                  text='ScreenShot   ' + "\U0001F4F7",
	                                  fg_color="#30A8E6",
	                                  bg_color="#071B3D",
	                                  hover_color="#061C42",
	                                  command=screenshot
	                                  )
	screenshot_button.place(x=819, y=665)

	def resize_bottom_half():
		window_width, window_height = root.winfo_width(), root.winfo_height()
		n = 40 / 1300 * window_height
		nm = int(20 / 750 * window_height)
		# timestamp
		current_timestamp.configure(font=("Lato", int(25 / 750 * window_height)))
		current_timestamp.place(x=window_width * 0.08 + (10 * 1300 / window_width), y=window_height * 0.63 + 10)
		# play pause
		original_image = Image.open(uiAssets + 'playButton.png')
		im_w, im_h = original_image.size
		new_size = (int(im_w * window_width / 1300), int(im_h * window_height / 750))
		print(new_size)
		resized_image_2 = original_image.resize(new_size)
		tk_resized_image = ImageTk.PhotoImage(resized_image_2)
		play_pause_button.configure(image=tk_resized_image)
		play_pause_button.place(x=60 * window_width / 1300, y=470 * window_height / 750 + 15)
		play_pause_button.image = tk_resized_image
		# max pd
		# max c
		# max pd @
		# max c @
		static_labels = [label_a, label_b, label_c, label_d]
		for sl in static_labels:
			sl.configure(font=("Lato", int(25 / 750 * window_height)))
		static_labels[0].place(x=225 * window_width / 1300, y=550 * window_height / 750)
		static_labels[1].place(x=225 * window_width / 1300, y=600 * window_height / 750)
		static_labels[2].place(x=650 * window_width / 1300, y=600 * window_height / 750)
		static_labels[3].place(x=650 * window_width / 1300, y=550 * window_height / 750)
		# max pd non-static
		# max c non-static
		# max pd @ non-static
		# max c @ non-static
		global crowd_is_included

		current_crowd_number.configure(font=("Lato", nm))
		current_crowd_number.place(x=480 / 1300 * window_width, y=600 / 750 * window_height)

		max_crowd_number.configure(font=("Lato", nm))

		current_crowd_number_off.configure(font=("Lato", nm))
		max_crowd_number_off.configure(font=("Lato", nm))

		current_pd_number.configure(font=("Lato", nm))
		current_pd_number.place(x=480 / 1300 * window_width, y=550 / 750 * window_height)

		max_people_number.configure(font=("Lato", nm), text="H")
		max_people_number.place(x=885 / 1300 * window_width, y=550 / 750 * window_height)
		# LQ_HQ button
		ns = int(25 / 750 * window_height)
		LQHQ_button.configure(width=n, height=n, font=("Lato", ns))
		LQHQ_button.place(x=window_width - (window_width * 0.04) - 40, y=window_height * 0.63 + 18)
		# info button
		more_info.configure(width=n, height=n, font=("Lato", nm))
		more_info.place(x=window_width - (window_width * 0.04) - 80, y=window_height * 0.63 + 18)
		# video title label
		video_title_label.configure(font=("Lato", nm))
		video_title_label.place(x=45 / 1300 * window_width, y=window_height * 0.04 - nm)
		# button upload
		uw, uh = 333 / 1300 * window_width, 60 / 750 * window_height
		upload_video_button.configure(width=uw, height=uh, font=("Lato", ns))
		upload_video_button.place(x=145 / 1300 * window_width, y=665 / 750 * window_height)
		# button save
		save_video_button.configure(width=uw, height=uh, font=("Lato", ns))
		save_video_button.place(x=482 / 1300 * window_width, y=665 / 750 * window_height)
		# screenshot
		screenshot_button.configure(width=uw, height=uh, font=("Lato", ns))
		screenshot_button.place(x=819 / 1300 * window_width, y=665 / 750 * window_height)

		pass

	vid_player = TkinterVideo(master=video_canvas, scaled=True, background="#051F4A")
	vid_player.place(x=45 * width / 1300, y=90 * height / 750, width=587, height=330)
	print(45 * width / 1300, 90, 587, 330)
	vid_player2 = TkinterVideo(scaled=True, master=video_canvas, background="#051F4A")
	vid_player2.place(x=200 * width / 1300, y=90 * height / 1300, width=587, height=330)

	def resize_video_players():
		window_width = root.winfo_width()
		available_width = window_width - 2 * (window_width * 0.04) - 20  # 4% padding on each side and 20px space
		video_width = available_width / 2
		video_height = video_width * 9 / 16  # 16:9 aspect ratio

		# Position the first video
		vid_player.place(x=window_width * 0.04, y=root.winfo_height() * .04 + 40, width=video_width,
		                 height=video_height)

		# Position the second video
		vid_player2.place(x=window_width * 0.04 + video_width + 20, y=root.winfo_height() * .04 + 40, width=video_width,
		                  height=video_height)
		return

	def update_people_label():

		nonlocal current_pd_number, vid_player
		import uiElements.sharedVariables as User
		tmp_stamp = 0
		while True:

			current_duration = vid_player.current_duration()
			stamp = int(current_duration)
			if tmp_stamp == stamp:
				pass
			else:
				print("updating people")

				current_pd_number.configure(text=User.pedestrian_count_second[stamp]
				                            )
				tmp_stamp = stamp
			sleep(.001)
			if new_video:
				return

	def update_crowd_label():
		nonlocal current_crowd_number, vid_player
		import uiElements.sharedVariables as User
		tmp_stamp = 0
		while True:

			current_duration = vid_player.current_duration()
			stamp = int(current_duration)

			if stamp == tmp_stamp:
				pass
			else:
				current_crowd_number.configure(
					text=User.crowd_count_second[stamp]
				)
				tmp_stamp = stamp
			sleep(.001)
			if new_video:
				return

	def declare_threads():
		global thread_crowd, thread_people
		thread_crowd = threading.Thread(target=update_crowd_label)
		thread_people = threading.Thread(target=update_people_label)

	play_button_image = PhotoImage(file=uiAssets + 'playButton.png')
	pause_button_image = PhotoImage(file=uiAssets + 'pauseButton.png')
	play_pause_button = tk.Button(video_canvas,
	                              image=play_button_image,
	                              border=0,
	                              anchor='n',
	                              background="#C8C8C8",
	                              activebackground="#051837",
	                              command=play_pause)

	res_high = False

	def switch_res():
		nonlocal LQHQ_button, res_high
		import uiElements.sharedVariables as User
		if res_high:
			LQHQ_button.configure(text="LQ")
			res_high = False
			User.high_res = False
		else:
			LQHQ_button.configure(text="HQ")
			res_high = True
			User.high_res = True

	LQHQ_button = ctk.CTkButton(video_canvas,
	                            width=40, height=40,
	                            border_width=1,
	                            anchor='n',
	                            bg_color="#04132D",
	                            fg_color="#04132D",
	                            border_color='white',
	                            font=(Lato, int(20 / 750 * root.winfo_width())),
	                            text="LQ",
	                            command=switch_res,
	                            )
	LQHQ_button.place(x=width - 60 - 40, y=470)

	def show_info():
		messagebox.showinfo(title="Changing Video Quality",
		                    message="HQ -> Use your video's original quality (More processing time)\nLQ --> Resize "
		                            "your video (Less processing time)\n\nLQ/HQ affect the quality of the screenshots "
		                            "and saved video as well.")

	more_info = ctk.CTkButton(video_canvas,
	                          width=20, height=20,
	                          border_width=2,
	                          corner_radius=20,
	                          anchor='n',
	                          bg_color="#04132D",
	                          fg_color="white",
	                          text_color="#04132D",
	                          font=(Lato, int(20 / 750 * root.winfo_width())),
	                          text="?",
	                          command=show_info,
	                          )
	more_info.place(x=width - 60 - 85, y=470 + 6)

	progress_value = tk.IntVar(video_canvas, )
	ctk.deactivate_automatic_dpi_awareness()

	progress_slider = tk.Scale(video_canvas,
	                           variable=progress_value, from_=0, to=0,
	                           command=seek, orient="horizontal",
	                           sliderlength=25, length=1195, width=10,
	                           borderwidth=0, showvalue=False,
	                           background="#071B3D",
	                           highlightbackground="#071B3D",
	                           activebackground="#30A8E6")

	progress_slider.place(x=45, y=440)

	def resize_progress_slider():
		new_x, new_y, new_w, new_h = new_coordinates(45, 440, 1195, 10)
		progress_slider.configure(length=new_w)  # , width=new_h)
		progress_slider.place(x=new_x + 5, y=new_y + 10)
		pass

	vid_player.bind("<<Duration>>", update_duration)
	vid_player.bind("<<SecondChanged>>", update_scale)
	vid_player.bind("<<Ended>>", video_ended)
	vid_player2.bind("<<Duration>>", update_duration)
	vid_player2.bind("<<SecondChanged>>", update_scale)
	vid_player2.bind("<<Ended>>", video_ended)

	resize_settings_button()
	resize_video_players()
	resize_video_canvas()
	resize_progress_slider()
	resize_bottom_half()

	root.mainloop()


open_video_window()
