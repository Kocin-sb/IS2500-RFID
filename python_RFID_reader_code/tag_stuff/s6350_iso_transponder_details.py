#!/usr/bin/env python3
#

#
# The s6350_iso_transponder_details program returns data from a
# single ISO15693 tag in the RFID reader field.  It essentially
# does an inventory with only 1 time slot, so only 1 tag can be
# found.  The following data from the tag can be returned.
#
# Transponder ID
# The Data Storage Format Identifier (DSFID)
#
# This is the CLI tool version.
#
# See TI 6350 user manual and the ISO 15693-3 document for more information.
#
# MTS 2020

import io
import sys
import serial

    
#
# This is the real body of the program.  It opens the communication port
# to the RFID reader, forms the correct command to turn the RF carrier
# on or off, and puts information for the user into the text widget.
#

def ti_iso_transponder_details(port_to_use):

    result = []

#
# The TI reader defaults to 57600 baud, 8 bit data, 1 stop bit and no parity.
# There is no handshaking.
#
# Note that the timeout here is set to 5 seconds.  That is more than enough
# time to allow the TI RFID reader to turn on its radio, command a tag, and get
# data back from it.  We assume that if we time out and we don't have any data
# then the RFID reader is not on line.
#

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
# Form an ISO read transponder details command with a slot length of 1.
# To use the write() method in python it needs to be in the form of a
# string or a buffer, which is just a pointer into memory.  This code
# forms an array of bytes from a list that contains the command to send
# and then uses a buffer (memoryview) to write it out.
#
# Note that the S6350 reader uses a wrapper that encapsulates all
# ISO commands.  Every ISO commands needs to have this wrapper with
# the S6350 reader.  For some commands the entire length is not
# known ahead of time, so some pieces are filled in later and the
# checksum bytes generated last and filled in.  Although this command
# can be completely known in advance, this code shows how to do it for
# other ISO commands where things need to be filled in later, such as
# specific UIDs or data to be written into a tag.
#
# In this wrapper, the bytes are as follows:
#
# 0: SOF
# 1 & 2: length LSB and MSB respectively, filled in later
# 3 & 4: TI reader address fields, alsways set to 0
# 5: TI reader command flags
# 6: TI reader ISO pass thru command, always 0x60
#

    read_transponder_details = [0x01, 0, 0, 0, 0, 0, 0x60]  # the ISO wrapper

#
# Extend the list with the actual ISO command without the SOF, CRC16 and EOF
# The bytes that extend the list are as follows:
#
# 7: ISO reader config byte 0.The value in this case is 0x11
# 8: Tag flags.  In this case indicating 1 time slot (0x27)
# 9: The ISO command.  In this case 0x01
# 10: The mask length for doing the inventory.  In this case it is 0
#

    read_transponder_details.extend([0x11, 0x27, 0x01, 0])

#
# Extend the list 1 more time with places for the checksum bytes.
# Those will be computed and added later to the resulting byte array
# that is formed to send to the reader.
#

    read_transponder_details.extend([0, 0])  # the two checksum bytes

#
# Now that the list containing the command template is done, it is
# possible to know the length of the command and create the byte array.
#

    command_len = len(read_transponder_details)
    command = bytearray(command_len)
    idx = 0

    for i in read_transponder_details:
        command[idx] = i
        idx += 1

# Fill in the length

    command[1] = command_len

# Compute and fill in the two checksum bytes

    chksum = 0
    idx = 0
    while idx < (command_len - 2):
        chksum ^= command[idx]
        idx += 1

    command[command_len - 2] = chksum  # 1st byte is the checksum
    command[command_len - 1] = chksum ^ 0xff  # 2nd byte is ones comp of the checksum

# Send out the command to the reader

    tiser.write(memoryview(command))  # memoryview is the same as buffer

#
# We read the returned data from the reader in 2 passes.  First we read
# the first two bytes.  The second byte is the length of the entire returned
# packet.  From that we determine how many more bytes to read which are then
# read in the second pass.
#

    line_size = tiser.read(2)  # first pass, read first two bytes of reply
    print(line_size)
    
    if len(line_size) < 2:
        result.append("No data returned.  Is the reader turned on?")
        tiser.close()
        return result

# second pass
#    print ("Reply length is " + line_size[1] + " bytes.")
    line_data = tiser.read(line_size[1] - 2)  # get the rest of the reply
    print ("I read " + str(len(line_data)) + " bytes.")

#
# The returned data is in the form of string objects.  Use that data to form
# a single response list of integers.  Integers are exactly what the RFID reader
# is sending back.  Doing this makes it easier to process the returned data.
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
# the checksum bytes that were returned.
#
# The 'while' statment ranges from 0 to the length of the returned data - 2.
# The minus 2 is to adjust for the index (we number from 0) and also so that
# we do not include the returned last checksum bytes in our own calculation.
# We compute the checksum on the returned data bytes, but not including the
# returned checksum bytes.
#

    chksum = 0
    idx = 0
    while idx < (response_len - 2):
        chksum ^= response[idx]
        idx += 1

#
# Compare the checksums and if they don't match then bail out.
# If they do match then all is well and all that remains is to
# dig out and print the tag data.
#

    if chksum != (response[response_len - 2]):  # and compare them
        result.append("Checksum error!")
#    print (chksum)
#    print (response[response_len - 2])
        tiser.close()
        return result

    if response[7] == 0x01:
        result.append("Transponder ID: " + "0x%0.2X" % response[20] + "%0.2X" % response[19]
              + "%0.2X" % response[18] + "%0.2X" % response[17]
              + "%0.2X" % response[16] + "%0.2X" % response[15]
              + "%0.2X" % response[14] + "%0.2X" % response[13])

        result.append("DSFID: " +  "0x%0.2X" % response[12])

    else:
        result.append("RFID tag not read.")
    print(response)
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

    all_results = ti_iso_transponder_details(sys.argv[1])
    for line in all_results:
        print(line)
