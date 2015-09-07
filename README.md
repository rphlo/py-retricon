py-retricon
===========

Library to create identicons similar to Github avatars.

Port of node-retricon https://github.com/sehrgut/node-retricon to python.

Usage
=====

    from retricon import retricon
    
    img = retricon("Hello World!")
    img.save('hello.png', 'PNG')


Parameters
==========

    style           Predefined style (Default: None)
    tile_size       Size of a tile (Default: 1)
    tile_color      Tiles color (Default: 0)
    tile_padding    Padding of each tiles (Default: 0)
    bg_color        Background color (Default: None)
    image_padding   Padding of the icon (Default: 0)
    tiles           Number of tiles that make the width of the icon (Default: 5)
    min_fill        Minimum ratio of tile in the image (Default: 0.3)
    max_fill        Maximum ratio of tile in the image (Default: 0.9)
    vertical_sym    Use vertical symmetry (Default: True)
    horizontal_sym  Use horizontal symmetry (Default: False)
    width           Width of the output image in pixels (Default: 500)


Predefined styles
=================

    'github'
    'gravatar'
    'mono'
    'mosaic'
    'mini'
    'window'


Valid color value
=================

    None -> transparent
    0 -> the lighter color chosen for you from the hash
    1 -> the darker color chosen for you from the hash
    An array describing the RGB(A) color (e.g. [125, 75, 250])
    An hexadecimal representation of the color (e.g. "0fd5e4")
