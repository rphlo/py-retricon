import hashlib, math
import struct

from PIL import Image, ImageDraw
    
def brightness(r, g, b):
    return math.sqrt(.241*r*r+.691*g*g+.068*b*b)

def cmp_brightness(a, b):
    return cmp(brightness(a[0], a[1], a[2]), brightness(b[0], b[1], b[2]))

def fprint(buf, length):
    if length>64:
        raise Exception('sha512 can only generate 64B of data: %dB requested'%length)

    x = hashlib.sha512(buf).digest().encode('hex_codec')
    i = length*2
    r = x[0:i]
    while i < len(x):
        r = format( int(r, 16)^int(x[i:i+length*2], 16), 'x')
        i += length
    if len(r)%2==1:
        r = "0"+r
    return r.decode('hex_codec')

def idhash(name, n, minFill, maxFill):
    buf = name+" "
    
    for i in range(0x100):
        buf = buf[:-1]+struct.pack('B', i)
        f = fprint(buf, int(math.ceil(n/8.0)+6))
        f = map(lambda x:struct.unpack('B', x)[0], f)
        pixels = []
        for x in ((f[6:])[:n]):
            for j in range(8):
                pixels.append((x>>j)&1)
        
        setPixels = len(filter(lambda x:x==1, pixels))
        c = [f[:3], f[3:6]]
        c = sorted(c, cmp=cmp_brightness)
        if setPixels > minFill * n and setPixels < maxFill * n:
            return {
                'colors': c,
                'pixels': pixels
            }
    raise Exception("String '''%s''' unhashable in single-byte search space."%name)

def fillPixels(id, dimension):
    pic = [0]*dimension
    for row in range(dimension):
        pic[row] = [0]*dimension
        for col in range(dimension):
            p = row * dimension + col
            pic[row][col] = id['pixels'][p]
    return pic
    
def fillPixelsVSym(id, dimension):
    mid = int(math.ceil(dimension / 2.0))
    odd = dimension % 2 != 0

    pic = [0]*dimension
    for row in range(dimension):
        pic[row] = [0]*dimension
        for col in range(dimension):
            p = row * mid + col
            if col >= mid:
                d = mid - col
                if odd:
                    d -= 1
                ad = abs(d)
                p = row * mid + mid - 1 - ad
            pic[row][col] = id['pixels'][p]
            
    return pic
    
def fillPixelsCSym(id, dimension):
    mid = int(math.ceil(dimension / 2.0))
    odd = dimension % 2 != 0

    pic = [0]*dimension
    for row in range(dimension):
        pic[row] = [0]*dimension
        for col in range(dimension):
            if row < mid:
                p = (row * mid) + col
                if col >= mid:
                    d = mid - col
                    if odd:
                        d -= 1
                    ad = abs(d)
                    p = (row * mid) + mid - 1 - ad
                pic[row][col] = id['pixels'][p]
            else:
                p = (dimension - 1 - row) * mid + col
                if col >= mid:
                    d = mid - col
                    if odd:
                        d -= 1
                    ad = abs(d)
                    p = (dimension-1-row) * mid + mid - 1 - ad
                pic[row][col] = id['pixels'][p]
    return pic
    
def fillPixelsHSym(id, dimension):
    mid = int(math.ceil(dimension / 2.0))
    odd = dimension % 2 != 0

    pic = [0]*dimension
    for row in range(dimension):
        pic[row] = [0]*dimension
        for col in range(dimension):
            p = (row * dimension) + col
            if row >= mid:
                p = (dimension - 1 - row) * dimension + col
            pic[row][col] = id['pixels'][p]
            
    return pic

def retricon(
        name,
        pixelSize = 10,
        bgColor = None,
        pixelPadding = 0,
        imagePadding = 0,
        tiles = 5,
        minFill = 0.3,
        maxFill = 0.90,
        pixelColor = 0,
        vSym = True,
        hSym = False
    ):
    
    dimension = tiles
    border = pixelPadding
    mid = int(math.ceil(dimension/2.0))
    if vSym and hSym:
        id = idhash(name, mid*mid, minFill, maxFill)
        pic = fillPixelsCSym(id, dimension)
    elif vSym or hSym:
        id = idhash(name, mid*dimension, minFill, maxFill)
        if vSym:
            pic = fillPixelsVSym(id, dimension)
        else:
            pic = fillPixelsHSym(id, dimension)
    else:
        id = idhash(name, dimension*dimension, minFill, maxFill)
        pic = fillPixels(id, dimension)
    csize = pixelSize*dimension+imagePadding*2
    
    im = Image.new('RGBA', (csize, csize))
    draw = ImageDraw.Draw(im)
    
    if bgColor is not None:
        if isinstance(bgColor, basestring):
            bgColor = [
                struct.unpack('B', bgColor[0:2].decode('hex_codec'))[0],
                struct.unpack('B', bgColor[2:4].decode('hex_codec'))[0],
                struct.unpack('B', bgColor[4:6].decode('hex_codec'))[0]
            ]
        elif isinstance(bgColor, int):
            bgColor = id['colors'][bgColor]
    
        draw.rectangle(
            (0,0, csize, csize), 
            fill = tuple(bgColor)
        )
    
    if isinstance(pixelColor, basestring):
        pixelColor = [
            struct.unpack('B', pixelColor[0:2].decode('hex_codec'))[0],
            struct.unpack('B', pixelColor[2:4].decode('hex_codec'))[0],
            struct.unpack('B', pixelColor[4:6].decode('hex_codec'))[0]
        ]
    elif isinstance(pixelColor, int):
        pixelColor = id['colors'][pixelColor]
    
    for x in range(dimension):
        for y in range(dimension):
            if pic[y][x] == 1:
                x0 = (x*pixelSize) + border + imagePadding
                y0 = (y*pixelSize) + border + imagePadding
                width = pixelSize - (border * 2)
                draw.rectangle( 
                    (x0, y0, x0 + width, y0 + width), 
                    fill = tuple(pixelColor)
                )
    del draw
    return im

def github(name, *args, **kwargs):
    return retricon(
        name, 
        pixelSize=70, 
        bgColor="F0F0F0", 
        pixelPadding=-1, 
        imagePadding=35, 
        tiles=5,
        vSym=True,
        hSym=False,
        *args, **kwargs
    )

def gravatar(name, *args, **kwargs):
    return retricon(
        name,  
        bgColor=1,  
        tiles=8,
        vSym=True,
        hSym=False,
        *args, **kwargs
    )
    
def mono(name, *args, **kwargs):
    return retricon(
        name,
        bgColor = 'F0F0F0',
        pixelColor= '000000',
        tiles= 6,
        pixelSize= 12,
        pixelPadding= -1,
        imagePadding= 6,
        vSym=True,
        hSym=False,
        *args, **kwargs
    )

def mosaic(name, *args, **kwargs):
    return retricon(
        name,
        imagePadding= 2,
        pixelPadding= 1,
        pixelSize= 16,
        bgColor= 'F0F0F0',
        vSym=True,
        hSym=False,
        *args, **kwargs
    )

def mini(name, *args, **kwargs):
    return retricon(
        name,
        pixelSize= 10,
        pixelPadding= 1,
        tiles= 3,
        bgColor= 0,
        pixelColor= 1,
        vSym=False,
        hSym=False,
        *args, **kwargs
    )

def window(name, *args, **kwargs):
    return retricon(
        name,
        pixelColor= [255, 255, 255, 255],
        bgColor= 0,
        imagePadding= 2,
        pixelPadding= 1,
        pixelSize= 16,
        vSym=True,
        hSym=False,
        *args, **kwargs
    )
    

if __name__ == "__main__":
    import random
    name = "kibo-%d"%random.randrange(100000)
    im = retricon(name)
    im.save('default.png', 'PNG')
    im = github(name)
    im.save('github.png', 'PNG')
    im = gravatar(name)
    im.save('gravatar.png', 'PNG')
    im = mono(name)
    im.save('mono.png', 'PNG')
    im = mini(name)
    im.save('mini.png', 'PNG')
    im = mosaic(name)
    im.save('mosaic.png', 'PNG')
    im = window(name)
    im.save('window.png', 'PNG')
    im = retricon(name, vSym=True, hSym=False, tiles=14, bgColor= 0, pixelColor= 1, pixelPadding=1, pixelSize=10)
    im.save('vsym.png', 'PNG')
    im = retricon(name, vSym=False, hSym=True, tiles=14, bgColor= 0, pixelColor= 1, pixelPadding=1, pixelSize=10)
    im.save('hsym.png', 'PNG')
    im = retricon(name, vSym=False, hSym=False, tiles=14, bgColor= 0, pixelColor= 1, pixelPadding=1, pixelSize=10)
    im.save('noSym.png', 'PNG')
    im = retricon(name, vSym=True, hSym=True, tiles=42, bgColor= 0, pixelColor= 1, pixelPadding=1, pixelSize=10, maxFill=.5)
    im.save('cSym.png', 'PNG')
    