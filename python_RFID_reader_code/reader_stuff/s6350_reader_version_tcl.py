#!/usr/bin/env python3
#

#
# This demo gets the version information from a TI S6350 RFID reader.
# This is the tkinter version providing a GUI.
#
# MTS 2020

import io
import sys
import serial
import list_ports
import s6350_reader_version
from s6350_reader_version import *
import tkinter
from tkinter import *


def do_it():

    all_results = ti_reader_version(topbox.e1.get())
    for line in all_results:
        write_text(line)


def write_text(text_to_write):

    win.t1.insert(END, text_to_write + '\n')

#
# The next routine scans and find the first listed connected serial port.
# The routine will not find serial ports that are not talking to anything.
# The assumption here is that the RFID reader is most likely the only serial
# device currently connected.
#

def scan_ports():
    
    topbox.e1.delete(0, END)  # clear out anything in the entry box
    active_ports = list_ports.serial_ports()
    if( len(active_ports) > 0 ):
        topbox.e1.insert(0, active_ports[0])
    else:
        win.t1.insert(END, "No connected serial ports found."+"\n")
        win.t1.insert(END, "Connect RFID reader and click 'Rescan Ports'."+"\n")


#
# The main part of the program starts here.  It just forms the GUI
# and starts the event loop to handle GUI events.
#

win = Frame()
win.pack()
win.master.title('Reader Version')  # This is the main window title
#
# Next is the container that holds the entry, label for the entry,
# and button widgets.
#
topbox = Label(win, relief=RAISED, bd=2)
topbox.pack(side=TOP, fill='x')

#
# The main text box and the scroll bar that goes with it.

win.t1 = Text(win, relief=RAISED, bd= 2)
win.sb1 = Scrollbar(win, background='#ffffff')
win.sb1.pack(side=RIGHT, fill='y')
win.t1.pack (side=TOP)

#
# Widgets that go into the topbox container
#
topbox.l1 = Label(topbox, text='Serial Port: ')
topbox.e1 = Entry(topbox, width=25, relief=SUNKEN, bd=2,)
topbox.b1 = Button(topbox, relief = RAISED, text='Get Version')
topbox.b2 = Button(topbox, relief = RAISED, text='Rescan Ports')

topbox.l1.pack(side=LEFT)
topbox.e1.pack(side=LEFT)
topbox.b2.pack(side=LEFT)
topbox.b1.pack(side=LEFT, expand=True)

#
# Show the first found active serial port in the label.
#

scan_ports()

#
# Specify commands for widgets that need them set.  They are set
# here because they usually can't be set when the widget is
# instantiated because often the command needed depends on some other
# widget that doesn't exist yet.  When that happens, python throws
# errors.  So the way to do it is to instantiate the widgets first, and
# then specify any commands that apply to them here.
#
# The commented out command for the button b1 is a good example of how
# to provide callback references that include arguments.
#
win.t1['yscrollcommand'] = win.sb1.set
win.sb1['command'] = win.t1.yview
topbox.b2['command'] = scan_ports
topbox.b1['command'] = do_it
#b1['command'] = lambda: ti_reader_version(topbox.e1.get())

win.mainloop()
