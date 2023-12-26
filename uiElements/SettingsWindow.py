import tkinter as tk
from tkinter import PhotoImage, filedialog
import customtkinter as CTk
from pathlib import Path

window = None
uiAssets = str(Path(__file__).resolve().parent.parent) + "//uiAssets//"
uiElements = str(Path(__file__).resolve().parent.parent) + "//uiElements//"
Lato = "Lato"


def settings_inherit_root(root):
	global window
	window = root


def open_settings_window(root=window):
	# settings will only be used in and by this function
	with open(uiElements + "/userSettings.txt", "r") as f:
		settings = f.read()
		settings = [line.split(" ")[-1] for line in settings.split("\n")]
		include_labels, include_crowd, include_accuracy, pedestrian_color, crowd_color, output_path = settings
		output_path = output_path.replace("_SPACE_", " ")
		include_labels, include_crowd, include_accuracy, pedestrian_color, crowd_color = int(include_labels), int(
			include_crowd), int(include_accuracy), int(pedestrian_color), int(crowd_color)

	color_dict = {1: "#0094FF", 2: "#FF00F6", 3: "red", 4: "#FF6A00", 5: "yellow", 6: "#26FF5C"}
	color_dict_key = 1

	def pick_color():
		nonlocal color_dict_key
		color_dict_key += 1
		return color_dict[color_dict_key - 1]

	global settings_opened

	settings_opened = True
	settings_window = tk.Toplevel(root, bg="#071F46")
	settings_window.geometry('450x600')
	settings_window.title('Settings')
	settings_window.iconbitmap(uiAssets + "logo.ico")
	settings_window.configure()
	settings_bg_color = "#071F46"

	topy = -20

	def increment_topy():
		nonlocal topy
		topy += 60
		return topy

	left_x = 0

	def increment_leftx():
		nonlocal left_x
		left_x += 30
		return left_x

	top_font = (Lato, 18)

	# include labels
	def include_labels_update():
		undo_saved()
		nonlocal include_labels
		include_labels += 1
		include_labels %= 2
		print(include_labels, include_labels_box.get())

	tk.Label(settings_window, text='Include Labels', font=top_font, foreground="white", background="#071F46").place(
		x=20, y=increment_topy())


	include_labels_box = CTk.CTkCheckBox(settings_window, height=20, width=20, text="", corner_radius=5,
										 fg_color=settings_bg_color, border_color="white", hover_color="white",
										 command=include_labels_update)
	if include_labels:
		include_labels_box.select()
	else:
		include_labels_box.deselect()

	include_labels_box.place(x=400, y=topy + 5)

	# include accuracy
	def include_accuracy_update():
		undo_saved()
		nonlocal include_accuracy
		include_accuracy += 1
		include_accuracy %= 2

	tk.Label(settings_window, text='Include Accuracy', font=top_font, foreground="white", background="#071F46").place(
		x=20, y=increment_topy())
	include_accuracy_box = CTk.CTkCheckBox(settings_window, height=20, width=20, text="", corner_radius=5,
										   fg_color=settings_bg_color, border_color="white", hover_color="white",
										   command=include_accuracy_update)
	if include_accuracy:
		include_accuracy_box.select()
	else:
		include_accuracy_box.deselect()
	include_accuracy_box.place(x=400, y=topy + 5)

	# crowd detect
	def include_crowd_update():
		undo_saved()
		nonlocal include_crowd
		include_crowd += 1
		include_crowd %= 2

	# print(include_crowd)

	tk.Label(settings_window, text='Include Crowd Detection', font=top_font, foreground="white",
			 background="#071F46").place(x=20, y=increment_topy())
	include_crowd_box = CTk.CTkCheckBox(settings_window, height=20, width=20, text="", corner_radius=5,
										fg_color=settings_bg_color, border_color="white", hover_color="white",
										command=include_crowd_update)
	if include_crowd:
		include_crowd_box.select()
	else:
		include_crowd_box.deselect()

	include_crowd_box.place(x=400, y=topy + 5)
	topy += 10
	# pedestrian box color
	same_color_error = tk.Label(settings_window, text='Pedestrian and Crowd colors can\'t be similar', font=(Lato, 10),
								foreground="red",
								background="#071F46")

	# choosing colors
	# pedestrian box colors
	def reset_pedestrian_checkboxes():
		undo_saved()
		nonlocal pd_color_checkBox_list, pedestrian_color, crowd_color, same_color_error
		same_color_error.place_forget()
		pd_color_checkBox_list[pedestrian_color - 1].deselect()
		if all(not box.get() for box in pd_color_checkBox_list):  # for no empty checkbox
			pd_color_checkBox_list[pedestrian_color - 1].select()

		else:
			for box in pd_color_checkBox_list:
				print(box.get(), end=", ")
				if box.get():
					tmp = pd_color_checkBox_list.index(box) + 1
					if tmp == crowd_color:
						same_color_error.place(x=20, y=560)
						pd_color_checkBox_list[tmp - 1].deselect()
						pd_color_checkBox_list[pedestrian_color - 1].select()
					else:
						pedestrian_color = tmp

	tk.Label(settings_window, text='Pedestrian Box Color', font=top_font, foreground="white",
			 background="#071F46").place(x=20, y=increment_topy())
	increment_topy()

	pd_color_checkBox_list = []
	pd_color_checkBox_one = CTk.CTkCheckBox(settings_window, height=20, width=20, text="", corner_radius=5,
											fg_color=pick_color(), border_color=color_dict[color_dict_key - 1],
											hover_color=color_dict[color_dict_key - 1],
											command=reset_pedestrian_checkboxes, )
	pd_color_checkBox_one.place(x=increment_leftx(), y=topy)
	pd_color_checkBox_list.append(pd_color_checkBox_one)

	pd_color_checkBox_two = CTk.CTkCheckBox(settings_window, height=20, width=20, text="", corner_radius=5,
											fg_color=pick_color(), border_color=color_dict[color_dict_key - 1],
											hover_color=color_dict[color_dict_key - 1],
											command=reset_pedestrian_checkboxes, )
	pd_color_checkBox_two.place(x=increment_leftx(), y=topy)
	pd_color_checkBox_list.append(pd_color_checkBox_two)

	pd_color_checkBox_three = CTk.CTkCheckBox(settings_window, height=20, width=20, text="", corner_radius=5,
											  fg_color=pick_color(), border_color=color_dict[color_dict_key - 1],
											  hover_color=color_dict[color_dict_key - 1],
											  command=reset_pedestrian_checkboxes, )
	pd_color_checkBox_three.place(x=increment_leftx(), y=topy)
	pd_color_checkBox_list.append(pd_color_checkBox_three)

	pd_color_checkBox_four = CTk.CTkCheckBox(settings_window, height=20, width=20, text="", corner_radius=5,
											 fg_color=pick_color(), border_color=color_dict[color_dict_key - 1],
											 hover_color=color_dict[color_dict_key - 1],
											 command=reset_pedestrian_checkboxes, )
	pd_color_checkBox_four.place(x=increment_leftx(), y=topy)
	pd_color_checkBox_list.append(pd_color_checkBox_four)

	pd_color_checkBox_five = CTk.CTkCheckBox(settings_window, height=20, width=20, text="", corner_radius=5,
											 fg_color=pick_color(), border_color=color_dict[color_dict_key - 1],
											 hover_color=color_dict[color_dict_key - 1],
											 command=reset_pedestrian_checkboxes, )
	pd_color_checkBox_five.place(x=increment_leftx(), y=topy)
	pd_color_checkBox_list.append(pd_color_checkBox_five)

	pd_color_checkBox_six = CTk.CTkCheckBox(settings_window, height=20, width=20, text="", corner_radius=5,
											fg_color=pick_color(), border_color=color_dict[color_dict_key - 1],
											hover_color=color_dict[color_dict_key - 1],
											command=reset_pedestrian_checkboxes, )
	pd_color_checkBox_six.place(x=increment_leftx(), y=topy)
	pd_color_checkBox_list.append(pd_color_checkBox_six)

	pd_color_checkBox_list[pedestrian_color - 1].select()
	default_p = False

	topy -= 20
	left_x = 0
	color_dict_key = 1

	# crowd box color
	def reset_crowd_checkboxes():
		undo_saved()
		nonlocal crowd_color_checkBox_list, crowd_color, default_c, pedestrian_color, same_color_error
		same_color_error.place_forget()
		crowd_color_checkBox_list[crowd_color - 1].deselect()
		if all(not box.get() for box in crowd_color_checkBox_list):  # for no empty checkbox
			crowd_color_checkBox_list[crowd_color - 1].select()

		else:
			for box in crowd_color_checkBox_list:
				print(box.get(), end=", ")
				if box.get():
					tmp = crowd_color_checkBox_list.index(box) + 1
					if tmp == pedestrian_color:
						same_color_error.place(x=20, y=560)
						crowd_color_checkBox_list[tmp - 1].deselect()
						crowd_color_checkBox_list[crowd_color - 1].select()
					else:
						crowd_color = tmp

	tk.Label(settings_window, text='Crowd Box Color', font=top_font, foreground="white", background="#071F46").place(
		x=20, y=increment_topy())
	increment_topy()
	crowd_color_checkBox_list = []
	crowd_color_checkBox_one = CTk.CTkCheckBox(settings_window, height=20, width=20, text="", corner_radius=5,
											   fg_color=pick_color(), border_color=color_dict[color_dict_key - 1],
											   hover_color=color_dict[color_dict_key - 1],
											   command=reset_crowd_checkboxes)
	crowd_color_checkBox_one.place(x=increment_leftx(), y=topy)
	crowd_color_checkBox_list.append(crowd_color_checkBox_one)
	crowd_color_checkBox_two = CTk.CTkCheckBox(settings_window, height=20, width=20, text="", corner_radius=5,
											   fg_color=pick_color(), border_color=color_dict[color_dict_key - 1],
											   hover_color=color_dict[color_dict_key - 1],
											   command=reset_crowd_checkboxes)
	crowd_color_checkBox_two.place(x=increment_leftx(), y=topy)
	crowd_color_checkBox_list.append(crowd_color_checkBox_two)
	crowd_color_checkBox_three = CTk.CTkCheckBox(settings_window, height=20, width=20, text="", corner_radius=5,
												 fg_color=pick_color(), border_color=color_dict[color_dict_key - 1],
												 hover_color=color_dict[color_dict_key - 1],
												 command=reset_crowd_checkboxes)
	crowd_color_checkBox_three.place(x=increment_leftx(), y=topy)
	crowd_color_checkBox_list.append(crowd_color_checkBox_three)
	crowd_color_checkBox_four = CTk.CTkCheckBox(settings_window, height=20, width=20, text="", corner_radius=5,
												fg_color=pick_color(), border_color=color_dict[color_dict_key - 1],
												hover_color=color_dict[color_dict_key - 1],
												command=reset_crowd_checkboxes)
	crowd_color_checkBox_four.place(x=increment_leftx(), y=topy)
	crowd_color_checkBox_list.append(crowd_color_checkBox_four)
	crowd_color_checkBox_five = CTk.CTkCheckBox(settings_window, height=20, width=20, text="", corner_radius=5,
												fg_color=pick_color(), border_color=color_dict[color_dict_key - 1],
												hover_color=color_dict[color_dict_key - 1],
												command=reset_crowd_checkboxes)
	crowd_color_checkBox_five.place(x=increment_leftx(), y=topy)
	crowd_color_checkBox_list.append(crowd_color_checkBox_five)
	crowd_color_checkBox_six = CTk.CTkCheckBox(settings_window, height=20, width=20, text="", corner_radius=5,
											   fg_color=pick_color(), border_color=color_dict[color_dict_key - 1],
											   hover_color=color_dict[color_dict_key - 1],
											   command=reset_crowd_checkboxes)
	crowd_color_checkBox_six.place(x=increment_leftx(), y=topy)
	crowd_color_checkBox_list.append(crowd_color_checkBox_six)

	crowd_color_checkBox_list[crowd_color - 1].select()
	default_c = False

	# output folder
	def change_output_folder():
		undo_saved()
		nonlocal output_path, current_output_text
		settings_window.withdraw()
		output_path = filedialog.askdirectory()
		print("got:", output_path)
		disp_output = output_path
		current_output_text.configure(text=f'Current: {disp_output}')
		settings_window.deiconify()

	topy -= 20
	left_x = 0
	tk.Label(settings_window, text='Output folder', font=top_font, foreground="white", background="#071F46").place(x=20,
																												   y=increment_topy() + 20)
	display_output = "\\" + output_path.replace("//", "\\").replace('"', "")
	current_output_text = tk.Label(settings_window, text=f'Current: {display_output}', font=(Lato, 10),
								   foreground="white", background="#071F46")
	current_output_text.place(x=20, y=increment_topy())
	output_folder_change_button = CTk.CTkButton(master=settings_window,
												width=120,
												height=40,
												border_width=2,
												border_color="white",
												bg_color=settings_bg_color,
												fg_color=settings_bg_color,
												corner_radius=8,
												text="Change",
												font=("Lato", 20),
												command=change_output_folder
												)
	output_folder_change_button.place(x=300, y=topy - 50)

	# output_folder_change_button.place(x = )

	# save settings
	def undo_saved():
		nonlocal settings_save_button
		settings_save_button.configure(text_color=settings_bg_color,
									   text='Save',
									   bg_color=settings_bg_color,
									   fg_color="white",
									   hover_color="#24EA3F", )

	def save_settings():
		nonlocal include_labels, include_crowd, include_accuracy, pedestrian_color, crowd_color, output_path, settings_save_button
		output_path = output_path.replace(" ", "_SPACE_")
		settings = f"labels {include_labels}\ncrowd {include_crowd}\naccuracy {include_accuracy}\npedestrian_color {pedestrian_color}\ncrowd_color {crowd_color}\nout_dir {output_path}"
		print(settings)
		with open(uiElements + "/userSettings.txt", "w") as f:
			f.write(settings)
		settings_save_button.configure(text='Saved!', fg_color="#24EA3F")

	settings_save_button = CTk.CTkButton(settings_window,
										 height=40,
										 width=120,
										 border_width=2,
										 corner_radius=8,
										 border_color="white",
										 font=("Lato", 20),
										 command=save_settings,
										 text_color=settings_bg_color,
										 text='Save',
										 bg_color=settings_bg_color,
										 fg_color="white",
										 hover_color="#24EA3F",

										 )
	settings_save_button.place(x=300, y=520)
	tk.Label(settings_window, text='Close without saving \nto cancel the changes', font=(Lato, 8), foreground="white",
			 background="#071F46").place(x=305, y=560)

	settings_window.wait_window()
