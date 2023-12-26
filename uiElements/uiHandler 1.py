import os.path
import shutil
import tkinter as tk
from tkinter import PhotoImage, filedialog, messagebox
import customtkinter as ctk
try:
	from uiElements.tkVideoPlayer import TkinterVideo
	from uiElements.SettingsWindow import open_settings_window, settings_inherit_root
except ModuleNotFoundError:
	from tkVideoPlayer import TkinterVideo
	from SettingsWindow import open_settings_window, settings_inherit_root
from time import sleep
import threading
import cv2
from pathlib import Path
from shutil import move

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

loading_font = ("Lato", 50)

root = tk.Tk()
root.title("BeamEye")
root.iconbitmap(uiAssets + "logo.ico")
width, height = 1300, 750
root.geometry(f"{width}x{height}")
root.resizable(False, False)
root.configure(bg="#031532")

pc = "#30A8E6"
ended = False
progressbar, progressbar_progress, progressbar_placeholder_label = ctk.CTkProgressBar, 0, tk.Label
current_loading_canvas, current_video_canvas = tk.Canvas, tk.Canvas
background_image_hello = PhotoImage(file=uiAssets + 'home2.png')
pedestrian_count_second, crowd_count_second = [], []
new_video = False


def open_hello_window():
	global current_canvas, main_root, w, h

	# upload canvas

	hello_canvas = tk.Canvas(root, width=width - 4, height=height - 4)
	current_canvas = hello_canvas
	hello_canvas.place(x=0, y=0)
	hello_canvas.create_image(width / 2, height / 2, image=background_image_hello, anchor="c")

	# settings in upload window

	progressbar_placeholder = ctk.CTkProgressBar(master=hello_canvas, height=20,
	                                             width=400, bg_color="#041632", fg_color="#041632",
	                                             progress_color="#30A8E6", border_color="#30A8E6",
	                                             border_width=2, indeterminate_speed=0.01, mode='determinate'
	                                             )
	progressbar_placeholder.place(x=width / 2 - 200, y=height / 2 + 60)
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

	threading.Thread(target=open_hello_window).start()
	video_canvas = tk.Canvas(root)
	settings_inherit_root(root)
	background_image_loading = PhotoImage(file=uiAssets + 'blurred.png')

	def open_load_window():

		global progressbar, progressbar_progress, \
			progressbar_placeholder_label, current_loading_canvas, \
			current_video_canvas, ended, input_video_path

		loading_canvas = ctk.CTkCanvas(root, width=width - 4, height=height - 4)  # , bg="#031532")
		loading_canvas.place(x=0, y=0)

		current_loading_canvas = loading_canvas
		loading_canvas.create_image(width / 2, height / 2, image=background_image_loading, anchor="c", )
		progressbar = ctk.CTkProgressBar(master=loading_canvas, height=20,
		                                 width=400, bg_color="#40424A", fg_color="#4A4C51",  # bg_color: for corner
		                                 # edges, fg_color inside the bar (inactive part)
		                                 progress_color="#49FF3F", border_color="#49FF3F",
		                                 border_width=2, indeterminate_speed=0.01, mode='determinate'
		                                 )
		progressbar.set(0)

		progressbar_placeholder_label = tk.Label(loading_canvas, text='Waking Up The Robot', font=loading_font,
		                                         foreground="white",
		                                         background="#031532")
		progressbar_placeholder_label.place(x=295, y=250)

		p1 = tk.Label(loading_canvas, text='Extracting Video Frames...', font=loading_font, foreground="white",
		              background="#031532")
		p2 = tk.Label(loading_canvas, text='Processing The Frames...', font=loading_font, foreground="white",
		              background="#031532")
		p3 = tk.Label(loading_canvas, text='Putting The Frames Back Together', font=loading_font, foreground="white",
		              background="#031532")
		p4 = tk.Label(loading_canvas, text='Almost There', font=loading_font, foreground="white",
		              background="#031532")
		p5 = tk.Label(loading_canvas, text='All Set!', font=loading_font, foreground="#49FF3F",
		              background="#031532")
		progress_feedback = [p1, p2, p3, p4, p5]

		def stepper(fill=False):
			# full bar is 100%
			# each step is 2%

			import uiElements.sharedVariables as User

			global progressbar, progressbar_progress, progressbar_placeholder_label, ended
			if ended:
				pass
			placement_coordinates = [(310, 250), (320, 250), (160, 250), (450, 250), (550, 250)]

			progressbar_placeholder_label.place_forget()
			progressbar.place(x=1300 / 2 - 200, y=750 / 2 + 60)
			progressbar_progress += 2
			div = 100 // (len(progress_feedback) - 1)

			a, b = placement_coordinates[progressbar_progress // div]
			progress_feedback[progressbar_progress // div].place(x=a, y=b)
			progress_feedback[progressbar_progress // div - 1].place_forget()
			progressbar.step()

			if fill:
				progressbar.set(1)
				progressbar.place_forget()
				progress_feedback[-2].place_forget()
				progress_feedback[-1].place(x=550, y=250)
				ended = True
				sleep(2)
				progressbar_progress = 0
				User.frames_progress = 0

				load_video(User.input_video_path, vid_player)
				load_video(User.output_video, vid_player2)

				loading_canvas.destroy()

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
		play_pause_button.place(x=60, y=470)

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
			# threading.Thread(target=update_people_label).start()
			# threading.Thread(target=update_crowd_label).start()
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
		# progress_value.set(int(vid_player2.current_duration()))
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
			if bool(include_crowd):
				current_crowd_number_off.place_forget()
				max_crowd_number_off.place_forget()
				current_crowd_number.place(x=440, y=593)
				current_crowd_number.configure(text_color=color_dict[crowd_color])

				mc = User.crowd_count_second.index(max(User.crowd_count_second))
				max_crowd_number.configure(text_color=color_dict[crowd_color])
				max_crowd_number.configure(
					text=f"{seconds_to_hhmmss(mc - 1 if mc > 1 else mc)} "
					     f"- {seconds_to_hhmmss(mc + 1 if mc > 1 else mc + 2)}"
					     f"  ({max(User.crowd_count_second)})")
				max_crowd_number.place(x=870, y=600)
			else:
				current_crowd_number.place_forget()
				max_crowd_number.place_forget()

				current_crowd_number_off.place(x=440, y=600)
				max_crowd_number_off.place(x=870, y=600)

			current_pd_number.configure(text_color=color_dict[pedestrian_color])

			mp = User.pedestrian_count_second.index(max(User.pedestrian_count_second))
			max_people_number.configure(text_color=color_dict[pedestrian_color])
			max_people_number.configure(
				text=f"{seconds_to_hhmmss(mp - 1 if mp > 1 else mp)} - "
				     f"{seconds_to_hhmmss(mp + 1 if mp > 1 else mp + 2)}"
				     f"  ({max(User.pedestrian_count_second)})")

			max_people_number.place(x=870, y=550)

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

	background_image = PhotoImage(file= uiAssets + 'Rectangle 3.png')

	video_canvas.pack(fill="both", expand=True)

	current_video_canvas = video_canvas
	video_canvas.create_image(1400 / 2, 750 / 2, image=background_image, anchor="c")

	Lato = "Lato"

	video_title_label = tk.Label(root, text='Video Title', font=("Lato", 20), foreground="white", background="#051736")
	current_timestamp = ctk.CTkLabel(root, text="00:00:00", font=("Lato", 25), fg_color="#061C40", bg_color="#061C40",
	                                 corner_radius=8)
	current_timestamp.place(x=105, y=472)

	settings_button_image = PhotoImage(file=uiAssets + 'settings.png')

	ctk.CTkLabel(root, text="Max # of People/sec", font=("Lato", 20), fg_color="transparent", bg_color="#061C40", text_color= "white",
	             corner_radius=8).place(x=225, y=550)
	current_pd_number = ctk.CTkLabel(root, text="", font=("Lato", 30, "bold"), fg_color="transparent",
	                                 bg_color="#061C40", corner_radius=8,
	                                 text_color="#30A8E6")
	current_pd_number.place(x=440, y=545)

	ctk.CTkLabel(root, text="Max # of Crowds/sec", font=("Lato", 20), fg_color="transparent", bg_color="#081F46",
	             corner_radius=8).place(x=225, y=600)
	current_crowd_number = ctk.CTkLabel(root, text="", font=("Lato", 30, "bold"), fg_color="transparent",
	                                    bg_color="#061C41", corner_radius=8,
	                                    text_color="#30A8E6")
	current_crowd_number_off = ctk.CTkLabel(root, text="Off", font=("Lato", 20, "bold"), fg_color="transparent",
	                                        bg_color="#061C41", corner_radius=8,
	                                        text_color="#FF8484")

	ctk.CTkLabel(root, text="Max # of Crowds at: ", font=("Lato", 20), fg_color="transparent", bg_color="#05193B",
	             corner_radius=8).place(x=650, y=600)
	max_crowd_number = ctk.CTkLabel(root, text="", font=("Lato", 20, "bold"), fg_color="transparent",
	                                bg_color="#051839", corner_radius=8,
	                                text_color="#30A8E6")
	current_crowd_number_off = ctk.CTkLabel(root, text="Off", font=("Lato", 20, "bold"), fg_color="transparent",
	                                        bg_color="#051839", corner_radius=8,
	                                        text_color="#FF8484")

	ctk.CTkLabel(root, text="Max # of People at: ", font=("Lato", 20), fg_color="transparent", bg_color="#05193B",
	             corner_radius=8).place(x=650, y=550)
	max_people_number = ctk.CTkLabel(root, text="T", font=("Lato", 20, "bold"), fg_color="transparent",
	                                 bg_color="#051839", corner_radius=8,
	                                 text_color="#30A8E6")
	max_crowd_number_off = ctk.CTkLabel(root, text="Off", font=("Lato", 20, "bold"), fg_color="transparent",
	                                    bg_color="#051839", corner_radius=8,
	                                    text_color="#FF8484")

	settings_open_button = tk.Button(video_canvas,
	                                 image=settings_button_image,
	                                 border=0,
	                                 anchor='n',
	                                 background="#031027",
	                                 activebackground="#031027",
	                                 command=open_settings_window
	                                 )
	settings_open_button.place(x=1205, y=30)

	upload_video_button = ctk.CTkButton(root,
	                                    height=60,
	                                    width=333,
	                                    border_width=2,
	                                    corner_radius=8,
	                                    border_color="#30A8E6",
	                                    font=("Lato", 23),
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
	                                  font=("Lato", 23),
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
			screenshot_button.configure(text="Saved in /ScreenShots/ Folder!", fg_color="#36BC27",
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
	                                  font=("Lato", 23),
	                                  text='ScreenShot   ' + "\U0001F4F7",
	                                  fg_color="#30A8E6",
	                                  bg_color="#071B3D",
	                                  hover_color="#061C42",
	                                  command=screenshot
	                                  )
	screenshot_button.place(x=819, y=665)

	vid_player = TkinterVideo(master=video_canvas, scaled=True, background="#051F4A")
	vid_player.place(x=45, y=90, width=587, height=330)
	vid_player2 = TkinterVideo(scaled=True, master=video_canvas, background="#051F4A")
	vid_player2.place(x=655, y=90, width=587, height=330)

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
		nonlocal x, res_high
		import uiElements.sharedVariables as User
		if res_high:
			x.configure(text="LQ")
			res_high = False
			User.high_res = False
		else:
			x.configure(text="HQ")
			res_high = True
			User.high_res = True

	x = ctk.CTkButton(video_canvas,
	                  width=40, height=40,
	                  border_width=1,
	                  anchor='n',
	                  bg_color="#04132D",
	                  fg_color="#04132D",
	                  border_color='white',
	                  font=(Lato, 20),
	                  text="LQ",
	                  command=switch_res,
	                  )
	x.place(x=width - 60 - 40, y=470)

	def show_info():
		messagebox.showinfo(title="Changing Video Quality",
		                    message="HQ -> Use your video's original quality (More processing time)\nLQ --> Resize "
		                            "your video (Less processing time)\n\nLQ/HQ affect the quality of the screenshots "
		                            "and saved video as well.")

	i = ctk.CTkButton(video_canvas,
	                  width=20, height=20,
	                  border_width=2,
	                  corner_radius=20,
	                  anchor='n',
	                  bg_color="#04132D",
	                  fg_color="white",
	                  text_color="#04132D",
	                  font=(Lato, 20),
	                  text="?",
	                  command=show_info,
	                  )
	i.place(x=width - 60 - 85, y=470 + 6)

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
	vid_player.bind("<<Duration>>", update_duration)
	vid_player.bind("<<SecondChanged>>", update_scale)
	vid_player.bind("<<Ended>>", video_ended)
	vid_player2.bind("<<Duration>>", update_duration)
	vid_player2.bind("<<SecondChanged>>", update_scale)
	vid_player2.bind("<<Ended>>", video_ended)
	root.mainloop()


open_video_window()
