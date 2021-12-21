import struct

# stupid shit cuz python lacks pass-by-reference
class MutableNum:
    def __init__(self, start_value):
        self.value = start_value

    def __int__(self):
        return self.value

    def __str__(self):
        return "%d" % self.value
    
    def __add__(self, other):
        if isinstance(other, MutableNum):
            self.value += other.value
        else:
            self.value += other
        return self
    
    def __sub__(self, other):
        if isinstance(other, MutableNum):
            self.value -= other.value
        else:
            self.value -= other
        return self
    
    def __mul__(self, other):
        if isinstance(other, MutableNum):
            self.value *= other.value
        else:
            self.value *= other
        return self
    
    def __pow__(self, other):
        if isinstance(other, MutableNum):
            self.value **= other.value
        else:
            self.value **= other
        return self
    
    def __truediv__(self, other):
        if isinstance(other, MutableNum):
            self.value /= other.value
        else:
            self.value /= other
        return self
    
    def __floordiv__(self, other):
        if isinstance(other, MutableNum):
            self.value //= other.value
        else:
            self.value //= other
        return self
    
    def __mod__(self, other):
        if isinstance(other, MutableNum):
            self.value %= other.value
        else:
            self.value %= other
        return self
    
    def __eq__(self, other):
        return self.value == other.value
    
    def __ne__(self, other):
        return self.value != other.value
    
    def __lt__(self, other):
        return self.value < other.value

    def __le__(self, other):
        return self.value <= other.value

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        return self.value >= other.value

def read_int(f):
    b = f.read(4)
    return struct.unpack('<i', b)[0]

def write_int(f, i):
    f.write(struct.pack("<i", int(i)))

def read_int8(f):
    return ord(f.read(1))

def write_int8(f, i):
    f.write(struct.pack("<c", int(i).to_bytes(1, 'little')))

def read_filetime(f):
    b = f.read(8)
    thelong = struct.unpack('<q', b)[0]
    thelong -= 11644473600000 * 10000   # change epoch from 1 Jan 1601 to 1 Jan 1970
    return thelong / 10000000           # convert from 100-nanosecond intervals to seconds

def write_filetime(f, t):
    t = t * 10000000                    # convert from seconds to 100-nanosecond intervals
    t += 11644473600000 * 10000         # change epoch from 1 Jan 1970 to 1 Jan 1601
    f.write(struct.pack("<q", int(t)))

def read_string(f, n):
    b = f.read(n)
    return b.decode('iso8859-1')

def write_string(f, s, write_len=True):
    if write_len:
        write_int8(f, len(s))
    format_string = "%ds" % len(s)
    f.write(struct.pack(format_string, s.encode("iso8859-1")))