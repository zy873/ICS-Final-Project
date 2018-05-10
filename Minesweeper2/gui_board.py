from tkinter import *
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import pickle

strVar = ''
boolVar = True
user_name = ''

def get_data(event):
	global strVar
	global boolVar
	global user_name

	comment = "Comments: " + strVar.get() + '\n'
	if boolVar.get() == True:
		name = 'From: ' + 'Anonymous User' + '\n'
	else:
		name = 'From: ' + user_name + '\n'
	return comment, name
	
def bind_button(event):
	if boolVar.get():
			getDataButton.unbind("<Button-1>")
	else:
			getDataButton.bind("<Button-1>", get_data)
			

def main(username, lead_info):
	global strVar
	global boolVar
	global user_name
	user_name = username
	
	root = Tk()
	root.geometry("500x300+500+500")
	root.title("Leader Board")
	root.configure(bg = 'black')
	
	new_time = []
	new_grp  = []
	for time in sorted(lead_info.keys()):
		new_time.append(time)
		new_grp.append(lead_info[time])

	leader_title = Label(root,text = 'LEADER BOARD', bg = 'black', fg = 'white', font = 'courier 50 bold').grid(row = 0, column = 1)
	num_1 = Label(root, text = 'NO.1', bg = 'black', fg = '#3373e1', font = 'courier 20 italic').grid(row = 1, column = 0)
	name_1 = Label(root, text = new_grp[0] , bg = 'black', fg = '#3373e1', font = 'courier 20 italic').grid(row = 1, column = 1)
	time_1 = Label(root, text = str(new_time[0]), bg = 'black', fg = '#3373e1', font = 'courier 20 italic').grid(row = 1, column = 2)
	# add black space between two lines
	b = Label(root,bg = 'black').grid(row = 2, column = 0)
	
	num_2 = Label(root, text = 'NO.2', bg = 'black', fg = '#e53dcd', font = 'courier 20 italic').grid(row = 3, column = 0)
	name_2 = Label(root, text = new_grp[1] , bg = 'black', fg = '#e53dcd', font = 'courier 20 italic').grid(row = 3, column = 1)
	time_2 = Label(root, text = str(new_time[1]), bg = 'black', fg = '#e53dcd', font = 'courier 20 italic').grid(row = 3, column = 2)
	l = Label(root,bg = 'black').grid(row = 4, column = 0)
	
	num_3 = Label(root, text = 'NO.3', bg = 'black', fg = '#E25527', font = 'courier 20 italic').grid(row = 5, column = 0)
	name_3 = Label(root, text = new_grp[2] , bg = 'black', fg = '#E25527', font = 'courier 20 italic').grid(row = 5, column = 1)
	time_3 = Label(root, text = str(new_time[2]), bg = 'black', fg = '#E25527', font = 'courier 20 italic').grid(row = 5, column = 2)
	a = Label(root,bg = 'black').grid(row = 6, column = 0)
	c = Label(root,bg = 'black').grid(row = 7, column = 0)

	# open a new window to collect comments
	def new_window():
		global strVar
		global boolVar
		
		new = tk.Toplevel(root)
		new.title('Further Comments')
		new.geometry("600x400+500+500")
		new.configure(bg = '#f0f8ff')
		label = Label(new, text = "Enter Your Comments Here:", bg = '#f0f8ff', fg = 'black', font="courier 14 bold").grid(row = 0, column = 0,sticky = W, padx = 4)
		
		strVar = StringVar()
		strEntry = Entry(new, textvariable = strVar, bd = 5, width = 50)
		strEntry.grid(row = 1, column = 0)
		
		boolVar = BooleanVar()
		theCheckBut = Checkbutton(new, text = "Anonymous", variable = boolVar).grid(row = 2, column = 0)
		
		# set the botton to get data and close the window
		getDataButton = Button(new, text="Submit", command = lambda win= new: win.destroy())
		getDataButton.bind("<Button-1>", get_data)
		getDataButton.grid(row = 2, column = 1)

	# set the botton to open a new window for comments
	feedback_button = tk.Button(root, text = "Further Comments", command = new_window)
	feedback_button.grid(row = 8, column = 1)

	root.mainloop()



