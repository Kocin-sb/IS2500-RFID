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
# This is the CLI tool version.
#
# MTS 2020

import io
import sys
import serial

#
# The getReturnPacket function reads a reply packet from the S6350 reader.
# It does some checking of the data and if the packet is intact and the
# checksum is right it will return the packet to the calling program as a
# list of integers.
#
# The get return packet also checks for functional and communication errors.
# A functional error occurs if the RFID reader doesn't work.  This is
# indicated if no data is read from the RFID reader and the serial connection
# times out.  Communication errors are those where the reader works, but the
# returned data is corrupt as indicated by the checksum bytes.  Both of these
# errors are fatal, so if they occur a message will be printed and the program
# will exit.
#
# There could also be ISO command errors.  Those are not necessarily fatal
# and are handled in the chkErrorISO routine.
#

def getReturnPacket(tiser):

    result = []
#
# We read the returned data from the reader in 2 passes.  First we read
# the first two bytes.  The second byte is the length of the entire returned
# packet.  From that we determine how many more bytes to read which are then
# read in the second pass.
#
#
# We read the returned data from the reader in 2 passes.  First we read
# the first two bytes.  The second byte is the length of the entire returned
# packet.  From that we determine how many more bytes to read which are then
# read in the second pass.
#

    rddat = []
    line_size = tiser.read(2)  # first pass, read first two bytes of reply
#   print(line_size)

    if len(line_size) < 2:
        result.append("No data returned.  Is the reader turned on?")
        tiser.close()
        return result

# second pass
#    print ("Reply length is " + str(ord(line_size[1])) + " bytes.")
    line_data = tiser.read(line_size[1] - 2)  # get the rest of the reply
  # print ("I read " + str(len(line_data)) + " bytes.")

#
# The returned data is in the form of string objects.  Use that data to form
# a single response list of integers.  Integers are exactly what the RFID reader
# is sending back.  Doing this makes it easier to process the returned data.
#

    rddat_len = line_size[1] # this is the length of the entire response
    idx = 0

    rddat.append(line_size[0]) # response SOF
    rddat.append(line_size[1]) # response size
# In the next line the -2 accounts for the SOF and size bytes done above.
    while idx < (rddat_len - 2): # do the rest of the response
        rddat.append(line_data[idx])
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
    while idx < (rddat_len - 2):
        chksum ^= rddat[idx]
        idx += 1

#
# Compare the checksums and if they don't match then bail out.
# If they do match then all is well and all that remains is to
# dig out and print the tag data.
#

    if chksum != (rddat[rddat_len - 2]):  # and compare them
        result.append("Checksum error!")
#    print (chksum)
#    print (rddat[rddat_len - 2])
        tiser.close()
        return result
    
    return rddat   #  return the reader data as a list


#
# The chkErrorISO function will take a packet returned by the
# reader as a list of bytes and check it for any operational
# errors.  Operational errors are ones where the reader is
# functional and communication is functional but something
# went wrong with the requested operation, for example asking
# for a tag UID that does not belong to any tag in the field.
#
# Note that functional errors and communication errors are
# checked for in the getReturnPacket routine.
#
# The routine will return a list that contains the ISO error
# code as an integer and the meaning of the error as a string.
# An error code of 0 means no error (OK or command success).
# 

def chkErrorISO(rddat): 
    if (len(rddat)==11) and (rddat[7] == 0x01):  # if there is an error
        error_code = rddat[8]  # get the code from the reader
        error_meaning = {
            "0x3" : "The option is not supported" ,
            "0x2" : "Command not supported.",
            "0x0f" : "Error with no information given",
            "0x10" : "Specified block is not available",
            "0x11" : "The specified block is already locked and thus cannot be locked again",
            "0x12" : "The specified block is locked and its content cannot be changed",
            "0x13" : "The specified block was not successfully programmed",
            "0x14" : "The specified block was not successfully locked",
            "0x15" : "The specified block is read−protectedx",
            }.get(hex(rddat[8]), "Unknown error code.")
    elif (len(rddat)==10) and (rddat[5] == 0x01):  # if there is an error
        error_code = rddat[7]  # get the code from the reader
        error_meaning = {
            "0x3" : "The option is not supported" ,
            "0x2" : "Command not supported.",
            "0x0f" : "Error with no information given",
            "0x10" : "Specified block is not available",
            "0x11" : "The specified block is already locked and thus cannot be locked again",
            "0x12" : "The specified block is locked and its content cannot be changed",
            "0x13" : "The specified block was not successfully programmed",
            "0x14" : "The specified block was not successfully locked",
            "0x15" : "The specified block is read−protectedx",
            }.get(hex(rddat[7]), "Unknown error code.") + " \n... Error ISO passtrhough byte not found"
    else:
        error_code = 0  # else 0 = all OK
        error_meaning = "OK"

    return [error_code, error_meaning]  # return code and meaning as a list


#
# The do_Hex_Input routine will take a string argument representing a number
# in hex and also an argument for a number of bytes.  It will turn the string
# argument into a little-endian list of bytes, each byte represented by an
# integer having a length of the requested number of bytes.  If all is well,
# it will return the list of bytes.  If an error occurs, it will instead
# return a string with the meaning of the error.  A calling program can
# determine what is coming back (a list or an error string) by using the
# builtin isinstance function.
#
# The user input string representing the hex number can optionally have a
# leading 0x.
#


def do_Hex_Input(user_input, num_bytes):

    formatter = "%0." + str(num_bytes * 2) + "x"

    try:
        s = formatter % int(user_input, base=16)
    except ValueError:
        return_bytes = "User input contains non-hex characters."
        return return_bytes

    if len(s) > (num_bytes * 2):
        return_bytes = "User input greater than required length."
        return return_bytes

    return_bytes = []
    x = 0

    while (x < num_bytes):
        return_bytes.append(int(s[-2 - (x * 2)] + s[-1 - (x * 2)], base=16))
        x = x + 1

    return return_bytes



####################################
#
# Main body of the code starts here.
#
####################################

def ti_read_multiple_blocks(port_to_use, tag_UID, tag_BLK, num_BLKS):

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
# To use the write() method in python it needs to be in the form of a
# string or a buffer, which is just a pointer into memory.  This code
# forms an array of bytes from a list that contains the command to send
# and then uses a buffer (memoryview) to write it out.
#
# Note that the S6350 reader uses a wrapper that encapsulates all
# ISO commands.  Every ISO commands needs to have this wrapper with
# the S6350 reader.  For some commands the entire length is not
# known ahead of time, so some pieces are filled in later and the
# checksum bytes generated last and filled in.  This command is a
# good example of a command where the length can change, in this
# case as the mask grows in length.
#
# In this wrapper, the bytes are as follows:
#
# 0: SOF
# 1 & 2: length LSB and MSB respectively, filled in later
# 3 & 4: TI reader address fields, alsways set to 0
# 5: TI reader command flags
# 6: TI reader ISO pass thru command, always 0x60
#

    read_addressed_block = [0x01, 0, 0, 0, 0, 0, 0x60]  # the ISO wrapper

#
# Extend the list with the actual ISO command without the SOF, CRC16 and EOF
# On the first inventory pass, the mask length is zero.  It will grow as
# collisions are encountered, but for now form the ISO inventory command
# asking for 16 time slots, and no mask.
#
# The bytes that extend the list are as follows:
#
# 7: ISO reader config byte 0.The value in this case is 0x11
# 8: Tag flags. Option flag is set to get security status. o_f=1, s_f=0, a_f=1
# 9: The ISO command.  In this case 0x23
#

    read_addressed_block.extend([0x11, 0x6b, 0x23])

#
# Extend the list again to provide space for the requested tag address (UID),
# starting memory block number, and the number of blocks.  Eight bytes for
# the UID and 2 bytes each for the starting block and number of blocks.
#

    read_addressed_block.extend([0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0])   # added an extra for the adress bytes.

#
# Extend the list 1 more time with places for the checksum bytes.
# Those will be computed and added later to the resulting byte array
# that is formed to send to the reader.
#

    read_addressed_block.extend([0, 0])  # the two checksum bytes

#
# Now that the list containing the command template is done, it
# is possible to compute the length of the command and create
# the byte array.
#

    command_len = len(read_addressed_block)
    command = bytearray(command_len)
    idx = 0

    for i in read_addressed_block:
        command[idx] = i
        idx += 1

# Fill in the length

    command[1] = command_len


# Get the requested UID from the argument list and fill it in

    uid = " "  # init this to be some string

    usr_str = tag_UID
    uid = do_Hex_Input(usr_str, 8)

    if isinstance(uid, str):
        result.append("Error: " + uid)
        result.append("")
        tiser.close()
        return result

# Get the requested starting block from the argument list and fill it in

    stblk = " "  # init this to be some string

    usr_str = tag_BLK
    stblk = do_Hex_Input(usr_str, 2)

    if isinstance(stblk, str):
        result.append("Error: " + stblk)
        result.append("")
        tiser.close()
        return result

# Get the requested number of blocks from the user arg list fill it in

    numblk = " "  # init this to be some string
    inumblk = 50 # init this too

    usr_str = num_BLKS
    numblk = do_Hex_Input(usr_str, 1)

    if isinstance(numblk, str):
        result.append("Error: " + numblk)
        result.append("")
        tiser.close()
        return result

# Check to see if too many blocks have been requested.  As this code
# will include security bits, each block will take 5 bytes.  See comments
# at the start of this program for how this determines the max number of
# blocks that can be read at one time.
#
# Also note that the command field for "number of blocks" is always set
# to the number of blocks requested minus 1.  So setting it to zero will
# return 1 block.  This makes the human interface here difficult because
# if someone requests zero blocks, they probably mean they don't want
# any data at all.  Very wierd.  So what is done here is to do what is
# intuative.  The user will request the actual number of blocks wanted.
# If the user asks for 1 block, they get 1 block.  But in the event that
# the user requests zero block, they will still get 1 block minimum.
#

    inumblk = numblk[0]
    if inumblk > 49:
        result.append("Error: Reader can only return up to 49 (0x31) blocks in one command.\n")
        numblk = " "  # reinit this
        tiser.close()
        return result


# Fill in UID

    idx = 10 # init to index in command array for first byte of UID

    for i in uid:
        command[idx] = i
        idx += 1

# Fill in starting block number.

    command[18] = stblk[0]
    command[19] = stblk[1]

# Fill in number of blocks to read.  See comments above about this field.

    if numblk[0] > 0:
        command[20] = numblk[0] - 1
    else:
        command[20] = numblk[0]


# Compute and fill in the two checksum bytes

    chksum = 0
    idx = 0
    while idx < (command_len - 2):
        chksum ^= command[idx]
        idx += 1

    command[command_len - 2] = chksum  # 1st byte is the checksum
    command[command_len - 1] = chksum ^ 0xff  # 2nd byte is ones comp of the checksum

# Send out the command to the reader and get the reply
    print("Request : ",command.hex())
    tiser.write(memoryview(command))  # memoryview is the same as buffer
    response = getReturnPacket(tiser)  # read the response from the reader
    print("Responce :",response)

#
# Check if any ISO operational errors have occurred.
#
    if(len(response) < 2):  # if the reader sent nothing back
        tiser.close()
        return response

    iso_errors = chkErrorISO(response)
    if iso_errors[0] != 0:
        result.append("Reader returned ISO operational error!")
        result.append("Error code is: " + hex(iso_errors[0]))  # for grins, print the error code
        result.append(iso_errors[1])  # and the meaning
        result.append("")
        tiser.close()
        return result

    else:

#
# If no ISO errors, print out the memory block data and the lock bits.
#
# There is an assumption here that ISO 15693 compliant tags used
# with this reader all have 32 bits per data block and the security
# bits add one more byte.  When the day comes that this isn't the case,
# this code will break big time.
#

        idx = 0
        result.append("")
        while inumblk > 0:

            result.append("Block: " + "0x%0.2x" % stblk[0])
            result.append("Data: " + "0x%0.2x" % response[12 + idx]
                       + "%0.2x" % response[11 + idx]
                       + "%0.2x" % response[10+ idx]
                       + "%0.2x" % response[9+ idx])

            result.append("Security Bits: " +  "0x%0.2x" % response[8 + idx])
            result.append("")
            stblk[0] = stblk[0] + 1
            idx = idx + 5  # each block of data is 4 bytes total.
            inumblk = inumblk - 1
    
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

    if len(sys.argv) < 5 :
        print ("Usage: ")
        print (sys.argv[0] + " serial_port_to_use tag_UID start_block_number number_of_blocks")
        print ("Where tag_UID, start_block_number, and number_of_blocks are numbers in hex.")
        sys.exit()

    all_results = ti_read_multiple_blocks(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    for line in all_results:
        print(line)
