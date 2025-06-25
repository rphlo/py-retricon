__all__ = ['retricon']
import codecs
import hashlib
import math
import struct
from PIL import Image, ImageDraw


def brightness(r, g, b):
    return math.sqrt(.241 * r * r + .691 * g * g + .068 * b * b)


def key_brightness(a):
    return brightness(a[0], a[1], a[2])


def fixed_length_hash(buf, length):
    if length > 64:
        msg = 'sha512 can only generate 64B of data: {}B requested'
        raise Exception(msg.format(length))
    hex_length = length * 2
    val = hashlib.sha512(buf).hexdigest()
    if len(val) % hex_length != 0:
        val += "0" * (hex_length - len(val) % hex_length)
    ii = hex_length
    ret = val[0:ii]
    while ii < len(val):
        ret = format(int(ret, 16) ^ int(val[ii:ii + hex_length], 16), 'x')
        ii += hex_length
    if len(ret) < hex_length:
        ret = "0" * (hex_length - len(ret)) + ret
    return codecs.decode(ret, 'hex')


def id_hash(name, length, min_fill, max_fill, use_colors):
    buf = name + " "
    buf_bytes = str.encode(buf)
    needed_bytes = int(math.ceil(length / 8.0))
    if use_colors:
        needed_bytes += 6
    for ii in range(0x100):
        buf_bytes = buf_bytes[:-1] + struct.pack('B', ii)
        fp = fixed_length_hash(buf_bytes, needed_bytes)
        fp = [struct.unpack('B', fp[ii:ii+1])[0] for ii, x in enumerate(fp)]
        pixels = []
        set_pixels = 0
        if use_colors:
            colors = [fp[:3], fp[3:6]]
            colors = sorted(colors, key=key_brightness)
            fp = fp[6:]
        else:
            colors = [None, None]
        for byte, offset in ((_byte, _offset)
                             for _byte in fp for _offset in range(7, -1, -1)):
            pixel_val = (byte >> offset) & 1
            pixels.append(pixel_val)
            if pixel_val == 1:
                set_pixels += 1
            if len(pixels) == length:
                break
        if min_fill * length < set_pixels < max_fill * length:
            return {
                'colors': colors,
                'pixels': pixels
            }
    raise Exception("String `{}` unhashable in single-byte search"
                    " space.".format(name))


def fill_pixels(raw, dimension):
    pic = [None] * dimension
    for row in range(dimension):
        pic[row] = [None] * dimension
        for col in range(dimension):
            ii = row * dimension + col
            pic[row][col] = raw['pixels'][ii]
    return pic


def fill_pixels_vert_sym(raw, dimension):
    mid = int(math.ceil(dimension / 2.0))
    odd = dimension % 2 != 0
    pic = [None] * dimension
    for row in range(dimension):
        pic[row] = [None] * dimension
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
    pic = [None] * dimension
    for row in range(dimension):
        pic[row] = [None] * dimension
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
    pic = [None] * dimension
    for row in range(dimension):
        pic[row] = [None] * dimension
        for col in range(dimension):
            if row < mid:
                ii = (row * dimension) + col
            else:
                ii = (dimension - 1 - row) * dimension + col
            pic[row][col] = raw['pixels'][ii]
    return pic


def retricon(name, tiles=5, tile_size=1, tile_color=0, bg_color=None,
             tile_padding=0, image_padding=0, min_fill=0.3, max_fill=0.90,
             vertical_sym=True, horizontal_sym=False, style=None,
             width=500):
    if style == 'github':
        tile_size = 70
        bg_color = "F0F0F0"
        tile_padding = -1
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
        tile_color = '000000'
        tiles = 6
        tile_size = 12
        tile_padding = -1
        image_padding = 6
        vertical_sym = True
        horizontal_sym = False
    elif style == 'mosaic':
        image_padding = 2
        tile_padding = 1
        tile_size = 16
        bg_color = 'F0F0F0'
        vertical_sym = True
        horizontal_sym = False
    elif style == 'mini':
        tile_size = 10
        tile_padding = 1
        tiles = 3
        bg_color = 0
        tile_color = 1
        vertical_sym = False
        horizontal_sym = False
    elif style == 'window':
        tile_color = [255, 255, 255, 255]
        bg_color = 0
        image_padding = 2
        tile_padding = 1
        tile_size = 16
        vertical_sym = True
        horizontal_sym = False
    elif style is not None:
        raise ValueError('Wrong parameter style')

    if bg_color is None:
        bg_color = [0, 0, 0, 0]
    if isinstance(bg_color, str):
        bg_color = [
            struct.unpack('B', codecs.decode(bg_color[0:2], 'hex'))[0],
            struct.unpack('B', codecs.decode(bg_color[2:4], 'hex'))[0],
            struct.unpack('B', codecs.decode(bg_color[4:6], 'hex'))[0]
        ]
    if tile_color is None:
        tile_color = [0, 0, 0, 0]
    if isinstance(tile_color, str):
        tile_color = [
            struct.unpack('B', codecs.decode(tile_color[0:2], 'hex'))[0],
            struct.unpack('B', codecs.decode(tile_color[2:4], 'hex'))[0],
            struct.unpack('B', codecs.decode(tile_color[4:6], 'hex'))[0]
        ]
    if isinstance(bg_color, int) or isinstance(tile_color, int):
        use_color = True
    else:
        use_color = False
    tile_width = tile_size + tile_padding * 2
    canvas_size = tile_width * tiles + image_padding * 2
    draw_scale = max((width // canvas_size), 1)
    dimension = tiles
    mid = int(math.ceil(dimension / 2.0))
    if vertical_sym and horizontal_sym:
        raw = id_hash(name, mid * mid, min_fill, max_fill, use_color)
        pic = fill_pixels_cent_sym(raw, dimension)
    elif vertical_sym or horizontal_sym:
        raw = id_hash(name, mid * dimension, min_fill, max_fill, use_color)
        if vertical_sym:
            pic = fill_pixels_vert_sym(raw, dimension)
        else:
            pic = fill_pixels_hori_sym(raw, dimension)
    else:
        raw = id_hash(name, dimension * dimension, min_fill, max_fill,
                      use_color)
        pic = fill_pixels(raw, dimension)
    if isinstance(bg_color, int):
        bg_color = raw['colors'][bg_color]
    if isinstance(tile_color, int):
        tile_color = raw['colors'][tile_color]
    im = Image.new('RGBA', (canvas_size * draw_scale,
                            canvas_size * draw_scale))
    draw = ImageDraw.Draw(im)
    draw.rectangle((0, 0, canvas_size * draw_scale, canvas_size * draw_scale),
                   fill=tuple(bg_color))
    for x in range(dimension):
        for y in range(dimension):
            if pic[y][x] == 1:
                x0 = (x * tile_width) + tile_padding + image_padding
                y0 = (y * tile_width) + tile_padding + image_padding
                draw.rectangle( 
                    (x0 * draw_scale, y0 * draw_scale,
                     (x0 + tile_size) * draw_scale - 1,
                     (y0 + tile_size) * draw_scale - 1),
                    fill=tuple(tile_color)
                )
    del draw
    out_img = im.resize((width, width), Image.Resampling.LANCZOS)
    del im
    return out_img


def test():
    val = "test-1000"
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
                  tiles=14, bg_color=0, tile_color=1, tile_padding=1, 
                  tile_size=10)
    im.save('vertical_sym.png', 'PNG')
    im = retricon(val, vertical_sym=False, horizontal_sym=True, 
                  tiles=14, bg_color=0, tile_color=1, tile_padding=1, 
                  tile_size=10)
    im.save('horizontal_sym.png', 'PNG')
    im = retricon(val, vertical_sym=False, horizontal_sym=False, 
                  tiles=10, bg_color=0, tile_color=1, tile_padding=1,
                  tile_size=10)
    im.save('noSym.png', 'PNG')
    im = retricon(val, vertical_sym=True, horizontal_sym=True, 
                  tiles=44, bg_color='00ff00', tile_color='ff0000',
                  tile_padding=1, tile_size=10, max_fill=.5)
    im.save('center_sym.png', 'PNG')
    im = retricon(val, bg_color=[255, 255, 0, 50], tile_color=None)
    im.save('test_trans.png', 'PNG')


if __name__ == "__main__":
    test()
