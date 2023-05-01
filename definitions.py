"""
Some helper functions for creating the packet formats. These are not used but help to define the packet layout
"""


def composepacket (version, hdrlen, tosdscp, totallength, identification, flags, fragmentoffset, timetolive, protocoltype, headerchecksum, sourceaddress, destinationaddress):
    if version != 4:
        return 1 
    if hdrlen.bit_length() > 4 or hdrlen < 0:
        return 2
    if tosdscp.bit_length() > 6 or tosdscp < 0:
        return 3
    if totallength.bit_length() > 16 or totallength < 0:
        return 4
    if identification.bit_length() > 16 or identification < 0:
        return 5
    if flags.bit_length() > 3 or flags < 0:
        return 6
    if fragmentoffset.bit_length() > 13 or fragmentoffset < 0:
        return 7
    if timetolive.bit_length() > 8 or timetolive < 0:
        return 8
    if protocoltype.bit_length() > 8 or protocoltype < 0:
        return 9
    if headerchecksum.bit_length() > 16 or headerchecksum < 0:
        return 10
    if sourceaddress.bit_length() > 32 or sourceaddress < 0:
        return 11
    if destinationaddress.bit_length() > 32 or destinationaddress < 0:
        return 12
    
    packet = bytearray(20)
    packet[0] = version << 4 | hdrlen
    packet[1] = tosdscp << 2
    packet[2] = totallength >> 8
    packet[3] = totallength & 0x00FF
    packet[4] = identification >> 8
    packet[5] = identification & 0x00FF
    packet[6] = flags << 5 | (fragmentoffset >> 8)
    packet[7] = fragmentoffset & 0x00FF
    packet[8] = timetolive
    packet[9] = protocoltype
    packet[10] = headerchecksum >> 8
    packet[11] = headerchecksum & 0x00FF
    packet[12] = sourceaddress >> 24
    packet[13] = sourceaddress >> 16 & 0x00FF
    packet[14] = sourceaddress >> 8 & 0x0000FF
    packet[15] = sourceaddress & 0x000000FF
    packet[16] = destinationaddress >> 24
    packet[17] = destinationaddress >> 16 & 0x00FF
    packet[18] = destinationaddress >> 8 & 0x0000FF
    packet[19] = destinationaddress & 0x000000FF
    
    return packet

# ------------------------------------------------------------------------------
def basicpacketcheck (packet):
    if len(packet) < 20:
        return 1
    if (packet[0] >> 4) != 4:
        return 2
    if not valid_checksum(packet):
        return 3
    if (packet[2] << 8 | packet[3]) != len(packet):
        return 4
    return True

def valid_checksum(packet):
    x = 0
    for i in range(10):
        c = (packet[2*i] << 8 | packet[2*i + 1])       
        x += c
    
    while x > 0xFFFF:
        x0 = x & 0xFFFF
        x1 = x >> 16
        x = x0 + x1
    return x == 0xFFFF

# ------------------------------------------------------------------------------
def destaddress (packet):
    destint = packet[16] << 24 | packet[17] << 16 | packet[18] << 8 | packet[19]
    iplist = [str(packet[16]), str(packet[17]), str(packet[18]), str(packet[19])]
    deststr = ".".join(iplist)
    return destint, deststr

# ------------------------------------------------------------------------------
def payload (packet):
    headerlength = packet[0] & 0x0F
    return packet[4*headerlength:]

print(payload(bytearray(b'F\x00\x00\x1e\x00\x00\x00\x00@\x06h\x86\x11"3DUfw\x88\x00\x00\x00\x00\x13\x14\x15\x16\x17\x18')))