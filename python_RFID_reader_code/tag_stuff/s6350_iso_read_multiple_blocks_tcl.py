#!/usr/bin/env python3
#

# The s6350_iso_read_multiple_blocks program returns data from a 
# range of contiguous memory blocks in an ISO 15693 complant tag.
#
# The program also displays the tag 'security' or lock bit status.
# The following assumptions are made:
#
# Blocks are 32 bits in length.
# Data is returned as four 2 digit bytes in hex.
# Block security bits are returned in 1 hex byte.
#
# Not a lot of error checking is done.  If the user asks for more
# data than a tag has, cryptic reader errors will be thrown.
#
# This command can deal with up to 256 bytes maximum of returned data.
# This 256 bytes is for the ENTIRE returned packet, including header,
# packet length, flags and all.  The non-data overhead of the returned
# packet is 10 bytes, leaving 246 bytes left for data.  If each block
# returns 4 bytes of block data, and 1 byte of security bits, then
# the total number of blocks that can be read is 246 / 5 = 49.2
# That means that the maximum number of blocks that can be returned
# at once, taking into account security bits, is 49 or 0x31 blocks.
#
# Also note that the command field for "number of blocks" is always set
# to the number of blocks requested minus 1.  So setting it to zero will
# return 1 block.
#
# See TI 6350 user manual and the ISO 15693-3 document for more information.
#
# This is the tkinter version providing a GUI.
#
# MTS 2020

import io
import sys
import serial
import list_ports
import s6350_iso_read_multiple_blocks
from s6350_iso_read_multiple_blocks import *
import tkinter
from tkinter import *

def do_it():

    all_results = ti_read_multiple_blocks(topbox.e1.get(),
                                          secondbox.e1.get(),
                                          secondbox.e2.get(),
                                          secondbox.e3.get())

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
win.master.title('Read Multiple Blocks')  # This is the main window title
#
# Next is the container that holds the entry for the port to use, label for
# the entry, and button widgets for application actions.
#
topbox = Label(win, relief=RAISED, bd=2)
topbox.pack(side=TOP, fill='x')

#
# Next is the container that holds the entry for an address, label for
# the entry, and another entry for data plus the label for that.
#
secondbox = Label(win, relief=RAISED, bd=2)
secondbox.pack(side=TOP, fill='x')

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
topbox.b1 = Button(topbox, relief = RAISED, text='Rescan Ports')
topbox.b2 = Button(topbox, relief = RAISED, text='Read Tags')

topbox.l1.pack(side=LEFT)
topbox.e1.pack(side=LEFT)
topbox.b1.pack(side=LEFT)
topbox.b2.pack(side=LEFT, expand=True)

#
# Widgets that go into the secondbox container
#
secondbox.l1 = Label(secondbox, text='Tag ID: ')
secondbox.e1 = Entry(secondbox, width=20, relief=SUNKEN, bd=2,)
secondbox.l2 = Label(secondbox, text='Start block # in hex:')
secondbox.e2 = Entry(secondbox, width=5, relief=SUNKEN, bd=2,)
secondbox.l3 = Label(secondbox, text='# of blocks in hex:')
secondbox.e3 = Entry(secondbox, width=5, relief=SUNKEN, bd=2,)

secondbox.l1.pack(side=LEFT)
secondbox.e1.pack(side=LEFT)
secondbox.e3.pack(side=RIGHT, padx='2m')
secondbox.l3.pack(side=RIGHT)
secondbox.e2.pack(side=RIGHT, padx='2m')
secondbox.l2.pack(side=RIGHT)

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
# The command for the button b1 is a good example of how to provide
# callback references that include arguments.
#
win.t1['yscrollcommand'] = win.sb1.set
win.sb1['command'] = win.t1.yview
topbox.b1['command'] = scan_ports
topbox.b2['command'] = do_it

win.mainloop()
