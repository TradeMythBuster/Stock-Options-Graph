from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import sqlite3
import matplotlib.pyplot as plt
import configuration
from sys import platform

class remove:
	def __init__(self, master, value, first, second, third, fourth, fifth, database):
		self.number = value
		self.myframe = Frame(master)
		self.myframe.grid(row = self.number+2,column=0,columnspan = 10,pady = 5)
		Label(self.myframe,text=first +'\t'+ second +'\t'+ third +'\tPremium : '+ fourth + '\tQuantity : '+ fifth,
			font=("Calibri", 13)).grid(row=self.number+2,column=0,columnspan = 4,padx=5,pady = 5,stick = W)
		Button(self.myframe, text=" X ",bg='red',font=("Calibri", 13),command=lambda:self.remove_option(database)).grid(row=self.number+2,column=5,padx = 5,pady =5,stick = W)

	def remove_option(self, database):
		self.myframe.destroy()
		conn = sqlite3.connect(database)
		c = conn.cursor()
		c.execute("DELETE from strats where rowid = "+str(self.number))
		conn.commit()
		conn.close()

def save_db(database):
	files = [('Database','*.db')]
	file = filedialog.asksaveasfile(filetypes = files, defaultextension = files)
	conn = sqlite3.connect(database)
	c = conn.cursor()
	c.execute("SELECT * FROM strats")
	legs = c.fetchall()
	conn.close()
	conn = sqlite3.connect(str(file).split("'")[1])
	c = conn.cursor()
	c.execute("""CREATE TABLE IF NOT EXISTS strats (action text,ce_pe text,strike real,premium real,quantity integer)""")
	c.executemany('INSERT INTO strats VALUES(?,?,?,?,?);',legs)
	conn.commit()
	conn.close()

def open_file():
    root.filename = filedialog.askopenfilename(initialdir="/",title = "Select A File",filetypes=(("All Files","*.*"),))
    if(root.filename):
	    add_strat(root.filename)
    # Label(root,text=root.filename).grid(row=6,column =0)

def add_leg(database):
	global buy_sell,ce_pe,strike,premium,quantity,strike_entry,premium_entry,quantity_entry,screen1
	number = 0
	conn = sqlite3.connect(database)
	c = conn.cursor()
	with conn:
	    c.execute("INSERT INTO strats VALUES (:action, :ce_pe, :strike, :premium, :quantity)",
	    {'action': buy_sell.get(), 'ce_pe': ce_pe.get(), 'strike': strike.get(), 'premium': premium.get(), 'quantity': quantity.get()})
	    c.execute("SELECT *,rowid FROM strats")
	    number = c.fetchall()[-1][-1]

	_ = remove(screen1, number, str(buy_sell.get()), str(strike.get()), str(ce_pe.get()), str(premium.get()), str(quantity.get()), database)

	premium_entry.delete(0,END)
	quantity_entry.delete(0,END)
	strike_entry.delete(0,END)
	quantity_entry.insert(0,int(0))
	premium_entry.insert(0,float(0))
	strike_entry.insert(0,float(0))

def create_graph(database):
	from_strike = 0 #hard coded for now
	to_strike = 0 #hard coded for now
	max_pre = 0

	conn = sqlite3.connect(database)
	c = conn.cursor()
	c.execute("SELECT *,rowid FROM strats")

	legs = c.fetchall()
	from_strike = legs[0][2]
	for leg in legs:
		from_strike = min(from_strike,leg[2])
		to_strike = max(to_strike,leg[2])
		max_pre = max(max_pre,leg[3])

	from_strike -= max_pre*10
	to_strike += max_pre*10
	range_strike = []
	total_pnl = []
	while(from_strike < to_strike):
	    range_strike.append(round(from_strike,2))
	    from_strike+=0.01
	range_strike.append(to_strike)
	total_pnl = [0 for x in range_strike]

	for leg in legs:
		pnl = []
		if(leg[0] == "BUY" and leg[1] == "CALL"):
			for i in range_strike:
				pnl.append(((max((i-leg[2]),0) - leg[3])*leg[4]))

		elif(leg[0] == "SELL" and leg[1] == "CALL"):
			for i in range_strike:
				pnl.append(((leg[3] - max((i-leg[2]),0))*leg[4]))

		elif(leg[0] == "BUY" and leg[1] == "PUT"):
			for i in range_strike:
				pnl.append(((max((leg[2]-i),0)-leg[3])*leg[4]))

		elif(leg[0] == "SELL" and leg[1] == "PUT"):
			for i in range_strike:
				pnl.append(((leg[3] - max((leg[2]-i),0))*leg[4]))
		for i in range(0,len(range_strike)):
			total_pnl[i] += pnl[i]

	fig, ax = plt.subplots()
	ax.plot(range_strike,total_pnl)
	ax.set(xlabel='Strike', ylabel='PnL',
	title='Options Pay-Off Diagram')
	# plt.xlim(0,to_strike+1)
	ax.grid()
	plt.show()
	range_strike = []
	total_pnl = []

	if(database == 'trial.db'):#CHECK THIS LOGIC
		c.execute("DROP TABLE IF EXISTS strats")
		conn.commit()

def add_strat(database):
    global buy_sell,ce_pe,strike,premium,quantity,strike_entry,premium_entry,quantity_entry,screen1
    conn = sqlite3.connect(database)
    c = conn.cursor()
    if database == 'trial.db':
        try:
            c.execute("DROP TABLE strats")
            conn.commit()
        except:
            pass
        c.execute("""CREATE TABLE strats (action text,ce_pe text,strike real,premium real,quantity integer)""")
    screen1 = Toplevel(root)
    screen1.title("Create STRATEGY")
    img = PhotoImage(file='optionicon_linux.gif')
    if platform == "linux" or platform == "linux2":
        screen1.tk.call('wm', 'iconphoto', root._w, img)
    elif platform == "win32":
        screen1.iconbitmap("optionicon.ico")
    screen1.geometry("%dx%d+0+0"%(root.winfo_screenwidth(),root.winfo_screenheight()))
    
    Label(screen1,text = "Choose action (BUY/SELL) : ",padx = 5,pady = 5,font=("Calibri", 13)).grid(row=0,column = 0)
    buy_sell = ttk.Combobox(screen1, value=["BUY", "SELL"],width=6)
    buy_sell.current(0)
    buy_sell.grid(row=0,column = 1,padx = 5,pady = 5)
    
    Label(screen1,text = " "*15+"Choose type (CALL/PUT) : ",padx = 5,pady = 5,font=("Calibri", 13)).grid(row=0,column = 2)
    ce_pe = ttk.Combobox(screen1, value=["CALL", "PUT"],width=6)
    ce_pe.current(0)
    ce_pe.grid(row=0,column = 3,padx = 5,pady = 5)
    
    Label(screen1,text = " "*15+"Strike Price : ",padx = 5,pady = 5,font=("Calibri", 13)).grid(row=0,column = 4,padx = 5,pady = 5)
    strike = DoubleVar()
    strike_entry = Entry(screen1, textvariable = strike)
    strike_entry.grid(row=0,column = 5,padx = 5,pady = 5)
    
    Label(screen1,text = " "*15+"Premium : ",padx = 5,pady = 5,font=("Calibri", 13)).grid(row=0,column = 6,padx = 5,pady = 5)
    premium = DoubleVar()
    premium_entry = Entry(screen1, textvariable = premium)
    premium_entry.grid(row=0,column = 7,padx = 5,pady = 5)
    
    Label(screen1,text = " "*15+"Quantity : ",padx = 5,pady = 5,font=("Calibri", 13)).grid(row=0,column = 8,padx = 5,pady = 5)
    quantity = IntVar()
    quantity_entry = Entry(screen1, textvariable = quantity)
    quantity_entry.grid(row=0,column = 9,padx = 5,pady = 5)
    
    add_leg_button = Button(screen1,text='Add Option Leg',padx = 5,pady = 5,font=("Calibri", 13),command=lambda:add_leg(database))
    add_leg_button.grid(row=1,column=0)
    
    create_graph_button = Button(screen1,text='Create Graph',padx = 5,pady = 5,font=("Calibri", 13),command=lambda:create_graph(database))
    create_graph_button.grid(row=1,column=2)
    
    save_button = Button(screen1,text=' Save Strategy ',padx = 5,pady = 5,font=("Calibri", 13),command=lambda:save_db(database))
    save_button.grid(row=1,column=4)
    
    c.execute("SELECT *,rowid FROM strats")
    legs = c.fetchall()
    conn.close()
    for leg in legs:
        _ = remove(screen1, leg[5], str(leg[0]), str(leg[2]), str(leg[1]), str(leg[3]), str(leg[4]), database)

background = configuration.colors['background']
header_fg = configuration.colors['header_foreground']
header_bg = configuration.colors['header_background']

root =Tk()
root.geometry('381x150')#"%dx%d+0+0"%(root.winfo_screenwidth(),root.winfo_screenheight())
root.title("Options Pay-Off Builder")
root.configure(bg=background)
img = PhotoImage(file='optionicon_linux.gif')
if platform == "linux" or platform == "linux2":
    root.tk.call('wm', 'iconphoto', root._w, img)
elif platform == "win32":
    root.iconbitmap("optionicon.ico")

heading = Label(root, text="Options Pay-Off Graph Generator", height = 2, font=("Calibri", 18), fg=header_fg, bg=header_bg)
heading.grid(row=0, column=0, columnspan=2, stick=W+E)

create = Button(root, text=" Create New Strategy ", padx = 5, pady = 5, font=("Calibri", 13), command = lambda:add_strat('trial.db'))
create.grid(row=1, column=0, pady=15, padx = 6.25)

open_saved = Button(root, text=" Open Saved Strategy ", padx = 5, pady = 5, font=("Calibri", 13), command = open_file)
open_saved.grid(row=1, column = 1, pady = 15, padx = 6.25)

root.mainloop()
