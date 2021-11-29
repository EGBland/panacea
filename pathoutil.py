import struct

def read_int(f):
    b = f.read(4)
    return struct.unpack('<i', b)[0]

def read_int8(f):
    return ord(f.read(1))

def read_filetime(f):
    b = f.read(8)
    thelong = struct.unpack('<q', b)[0]
    thelong -= 11644473600000 * 10000   # change epoch from 1 Jan 1601 to 1 Jan 1970
    return thelong / 10000000           # convert from 100-nanosecond intervals to seconds

def read_string(f, n):
    b = f.read(n)
    return b.decode('iso8859-1')
