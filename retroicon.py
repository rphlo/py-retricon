import hashlib, math
import struct

def brightness(r, g, b):
    return math.sqrt(.241*r*r+.691*g*g+.068*b*b)




def fprint(buf, length):
    if length>64:
        raise Exception('sha512 can only generate 64B of data: %dB requested'%length)
    
    x = hashlib.sha256(buf).digest().encode('hex_codec')
    i = length*2
    r = x[0:i]
    while i < len(x):
        r = format( int(r, 16)^int(x[i:i+length*2], 16), 'x')
        i += length*2
        
    return r.decode('hex_codec')

def idhash(str, n, minFill, maxFill):
    buf = str+" "
    
    for i in range(0x100):
        buf = buf[:-1]+struct.pack('>I', i)
        f = fprint(buf, int(math.ceil(n/8)+6))
        pixels = ((f.encode('hex_codec')[12:])[:n*2]).decode('hex_codec')
        return pixels

print fprint('test', 18)
print idhash('test', 52, 0, 127)
