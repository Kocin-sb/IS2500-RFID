#!/usr/bin/env python3
#

#
# This demo gets the version information from a TI S6350 RFID reader.
# This is the CLI tools version.
#
# MTS 2020

import io
import sys
import serial

    
#
# This is the real body of the program.  It opens the communication port
# to the RFID reader, forms the correct command to read the version
# information, and puts the information into the text widget.
#

def ti_reader_version(port_to_use):

    result = []
#
# The TI reader defaults to 57600 baud, 8 bit data, 1 stop bit and no parity.
# There is also no handshaking.
#

    try:
        tiser = serial.Serial(port_to_use, baudrate=57600, bytesize=8,
                              parity='N', stopbits=1, timeout=0.5,
                              xonxoff=0, rtscts=0, dsrdtr=0)
    except:
        result.append("Can't open " + port_to_use + ".")
        result.append("Under linux or Apple OS you need the full path, ie /dev/ttyUSB0.")
        result.append("Under windows use the communication port name, ie COM8.")
        return result

#
# Form a read version command.  To use the write() method in python it needs
# to be in the form of a string or a buffer, which is just a pointer into
# memory.  This code forms an array of bytes from a list that contains the
# command to send and then uses a buffer (memoryview) to write it out.
#

    read_version_command = [0x01, 0x09, 0, 0, 0, 0, 0xf0, 0xf8, 0x07]
    command = bytearray(9)
    idx = 0

    for i in read_version_command:
        command[idx] = i
        idx += 1

    tiser.write(memoryview(command))  # memoryview == buffer

#
# We read the returned data from the reader in 2 passes.  First we read
# the first two bytes.  The second byte is the length of the entire returned
# packet.  From that we determine how many more bytes to read which are then
# read in the second pass.
#
# Remember that in python3 the serial.read() method returns data as numeric bytes.
# (In python2 the serial.read() method returns data as string objects.)
# So in python3 no conversions need to be done to get integers or hex strings.
#

    line_size = tiser.read(2)  # first pass, read first two bytes of reply

    if len(line_size) < 2:
        result.append("No data returned.  Is the reader turned on?")
        return result

# second pass
#    print ("Reply length is " + str(line_size[1]) + " bytes.")
    line_data = tiser.read(line_size[1] - 2)  # get the rest of the reply
#    print ("I read " + str(len(line_data)) + " bytes.")

#
# Use the returned data to form a single response list of integers.  Integers
# are exactly what the RFID reader is sending back.  Doing this makes it
# easier to process the returned data.
#

    response_len = line_size[1] # this is the length of the entire response
    response = []
    idx = 0

    response.append(line_size[0]) # response SOF
    response.append(line_size[1]) # response size
# In the next line the -2 accounts for the SOF and size bytes done above.
    while idx < (response_len - 2): # do the rest of the response
        response.append(line_data[idx])
        idx += 1

#
# Compute the checksum.  To compute the checksum of the returned data you
# just take the XOR of all the data bytes that were returned and compare with
# the checksum bytes that were returned.  The 'while' statment ranges from 0
# to the length of the returned data - 2.  The minus 2 is to adjust for the
# index (we number from 0) and also so that we do not include the returned
# last checksum bytes in our own calculation.  We compute the checksum on the
# returned data bytes, but not including the returned checksum bytes.
#

    chksum = 0
    idx = 0
    while idx < (response_len - 2):
        chksum ^= response[idx]
        idx += 1

#
# Compare the checksums and if they match dig out and print the
# firmware revision number.  The firmware rev number is contained in
# bytes 7 and 8 of the response in all cases of this command.
#

    if chksum == (response[response_len - 2]):  # and compare them
        result.append("TI S6350 RFID Reader")
        result.append("Firmware Version: " +
                   str(response[8]) + "." +
                   hex(response[7])[2:4]) # the [2:4] cuts off the 0x
    else:
        result.append("Checksum error!")
#        print (chksum)
#        print (response[response_len - 2])

    tiser.close()
    return result


#
# Standalone 'main' starts here.
#

if __name__ == '__main__':
#
# Check that there is at least one argument which hopefully will be
# the serial port ID that is to be used.
#

    if len(sys.argv) < 2 :
        print ("Usage: " + sys.argv[0] + " serial_port_to_use")
        sys.exit()

    all_results = ti_reader_version(sys.argv[1])
    for line in all_results:
        print(line)

