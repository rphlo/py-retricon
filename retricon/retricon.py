__all__ = ['retricon']
import hashlib
import math
import struct
from PIL import Image, ImageDraw


def brightness(r, g, b):
    return math.sqrt(.241*r*r+.691*g*g+.068*b*b)


def cmp_brightness(a, b):
    return cmp(brightness(a[0], a[1], a[2]), brightness(b[0], b[1], b[2]))


def fprint(buf, length):
    if length > 64:
        raise Exception('sha512 can only generate 64B of data:'
                        ' %dB requested' % length)
    hex_length = length*2
    val = hashlib.sha512(buf).digest().encode('hex_codec')
    if len(val) % hex_length != 0:
        val += "0"*(hex_length-len(val) % hex_length)
    ii = hex_length
    ret = val[0:ii]
    while ii < len(val):
        ret = format(int(ret, 16) ^ int(val[ii:ii+hex_length], 16), 'x')
        ii += hex_length
    if len(ret) < hex_length:
        ret = "0"*(hex_length-len(ret)) + ret
    return ret.decode('hex_codec')


def id_hash(name, length, min_fill, max_fill):
    buf = name+" "
    for ii in range(0x100):
        buf = buf[:-1]+struct.pack('B', ii)
        fp = fprint(buf, int(math.ceil(length/8.0)+6))
        fp = map(lambda x: struct.unpack('B', x)[0], fp)
        pixels = []
        for byte in fp[6:]:
            for offset in range(8):
                pixels.append((byte >> offset) & 1)
        pixels = pixels[:length]
        set_pixels = len(filter(lambda x:x==1, pixels))
        colors = [fp[:3], fp[3:6]]
        colors = sorted(colors, cmp=cmp_brightness)
        if min_fill * length < set_pixels < max_fill * length:
            return {
                'colors': colors,
                'pixels': pixels
            }
    raise Exception("String '''%s''' unhashable in"
                    " single-byte search space." % name)


def fill_pixels(raw, dimension):
    pic = [0]*dimension
    for row in range(dimension):
        pic[row] = [0]*dimension
        for col in range(dimension):
            ii = row * dimension + col
            pic[row][col] = raw['pixels'][ii]
    return pic


def fill_pixels_vert_sym(raw, dimension):
    mid = int(math.ceil(dimension / 2.0))
    odd = dimension % 2 != 0
    pic = [0]*dimension
    for row in range(dimension):
        pic[row] = [0]*dimension
        for col in range(dimension):
            if col < mid:
                ii = row * mid + col
            else:
                dist_middle = mid - col
                if odd:
                    dist_middle -= 1
                dist_middle = abs(dist_middle)
                ii = row * mid + mid - 1 - dist_middle
            pic[row][col] = raw['pixels'][ii]
    return pic


def fill_pixels_cent_sym(raw, dimension):
    mid = int(math.ceil(dimension / 2.0))
    odd = dimension % 2 != 0
    pic = [0]*dimension
    for row in range(dimension):
        pic[row] = [0]*dimension
        for col in range(dimension):
            if col >= mid:
                dist_middle = mid - col
                if odd:
                    dist_middle -= 1
                dist_middle = abs(dist_middle)
            if row < mid:
                if col < mid:
                    ii = (row * mid) + col
                else:
                    ii = (row * mid) + mid - 1 - dist_middle
            else:
                if col < mid:
                    ii = (dimension - 1 - row) * mid + col
                else:
                    ii = (dimension - 1 - row) * mid + mid - 1 - dist_middle
            pic[row][col] = raw['pixels'][ii]
    return pic


def fill_pixels_hori_sym(raw, dimension):
    mid = int(math.ceil(dimension / 2.0))
    pic = [0]*dimension
    for row in range(dimension):
        pic[row] = [0]*dimension
        for col in range(dimension):
            if row < mid:
                ii = (row * dimension) + col
            else:
                ii = (dimension - 1 - row) * dimension + col
            pic[row][col] = raw['pixels'][ii]
    return pic


def retricon(name, style=None, pixel_size=10,
             bg_color=None, pixel_padding=0, image_padding=0,
             tiles=5, min_fill=0.3, max_fill=0.90, pixel_color=0,
             vertical_sym=True, horizontal_sym=False):
    if style == 'github':
        pixel_size = 70
        bg_color = "F0F0F0"
        pixel_padding = -1
        image_padding = 35
        tiles = 5
        vertical_sym = True
        horizontal_sym = False
    elif style == 'gravatar':
        bg_color = 1
        tiles = 8
        vertical_sym = True
        horizontal_sym = False
    elif style == 'mono':
        bg_color = 'F0F0F0'
        pixel_color = '000000'
        tiles = 6
        pixel_size = 12
        pixel_padding = -1
        image_padding = 6
        vertical_sym = True
        horizontal_sym = False
    elif style == 'mosaic':
        image_padding = 2
        pixel_padding = 1
        pixel_size = 16
        bg_color = 'F0F0F0'
        vertical_sym = True
        horizontal_sym = False
    elif style == 'mini':
        pixel_size = 10
        pixel_padding = 1
        tiles = 3
        bg_color = 0
        pixel_color = 1
        vertical_sym = False
        horizontal_sym = False
    elif style == 'window':
        pixel_color = [255, 255, 255, 255]
        bg_color = 0
        image_padding = 2
        pixel_padding = 1
        pixel_size = 16
        vertical_sym = True
        horizontal_sym = False
    dimension = tiles
    border = pixel_padding
    mid = int(math.ceil(dimension/2.0))
    if vertical_sym and horizontal_sym:
        raw = id_hash(name, mid*mid, min_fill, max_fill)
        pic = fill_pixels_cent_sym(raw, dimension)
    elif vertical_sym or horizontal_sym:
        raw = id_hash(name, mid*dimension, min_fill, max_fill)
        if vertical_sym:
            pic = fill_pixels_vert_sym(raw, dimension)
        else:
            pic = fill_pixels_hori_sym(raw, dimension)
    else:
        raw = id_hash(name, dimension*dimension, min_fill, max_fill)
        pic = fill_pixels(raw, dimension)
    csize = pixel_size*dimension+image_padding*2
    im = Image.new('RGBA', (csize, csize))
    draw = ImageDraw.Draw(im)
    if bg_color is not None:
        if isinstance(bg_color, basestring):
            bg_color = [
                struct.unpack('B', bg_color[0:2].decode('hex_codec'))[0],
                struct.unpack('B', bg_color[2:4].decode('hex_codec'))[0],
                struct.unpack('B', bg_color[4:6].decode('hex_codec'))[0]
            ]
        elif isinstance(bg_color, int):
            bg_color = raw['colors'][bg_color]
        draw.rectangle(
            (0, 0, csize, csize),
            fill=tuple(bg_color)
        )
    if pixel_color is None:
        pixel_color = [0, 0, 0, 0]
    if isinstance(pixel_color, basestring):
        pixel_color = [
            struct.unpack('B', pixel_color[0:2].decode('hex_codec'))[0],
            struct.unpack('B', pixel_color[2:4].decode('hex_codec'))[0],
            struct.unpack('B', pixel_color[4:6].decode('hex_codec'))[0]
        ]
    elif isinstance(pixel_color, int):
        pixel_color = raw['colors'][pixel_color]
    for x in range(dimension):
        for y in range(dimension):
            if pic[y][x] == 1:
                x0 = (x*pixel_size) + border + image_padding
                y0 = (y*pixel_size) + border + image_padding
                width = pixel_size - (border * 2) - 1
                draw.rectangle( 
                    (x0, y0, x0 + width, y0 + width), 
                    fill=tuple(pixel_color)
                )
    del draw
    return im


def test():
    import random
    val = "kibo-%d" % random.randrange(100000)
    im = retricon(val)
    im.save('default.png', 'PNG')
    im = retricon(val, style='github')
    im.save('github.png', 'PNG')
    im = retricon(val, style='gravatar')
    im.save('gravatar.png', 'PNG')
    im = retricon(val, style='mono')
    im.save('mono.png', 'PNG')
    im = retricon(val, style='mini')
    im.save('mini.png', 'PNG')
    im = retricon(val, style='mosaic')
    im.save('mosaic.png', 'PNG')
    im = retricon(val, style='window')
    im.save('window.png', 'PNG')
    im = retricon(val, vertical_sym=True, horizontal_sym=False, 
                  tiles=14, bg_color=0, pixel_color=1, pixel_padding=1, 
                  pixel_size=10)
    im.save('vertical_sym.png', 'PNG')
    im = retricon(val, vertical_sym=False, horizontal_sym=True, 
                  tiles=14, bg_color=0, pixel_color=1, pixel_padding=1, 
                  pixel_size=10)
    im.save('horizontal_sym.png', 'PNG')
    im = retricon(val, vertical_sym=False, horizontal_sym=False, 
                  tiles=14, bg_color=0, pixel_color=1, pixel_padding=1, 
                  pixel_size=10)
    im.save('noSym.png', 'PNG')
    im = retricon(val, vertical_sym=True, horizontal_sym=True, 
                  tiles=42, bg_color=0, pixel_color=1, pixel_padding=1, 
                  pixel_size=10, max_fill=.5)
    im.save('center_sym.png', 'PNG')
    im = retricon(val, bg_color=[255, 255, 0, 50], pixel_color=None)
    im.save('test_trans.png', 'PNG')

if __name__ == "__main__":
    test()