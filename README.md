py-retricon
===========

Port of node-retricon https://github.com/sehrgut/node-retricon to python

Usage
=====

    from retricon import retricon
    
    img = retricon("Hello World!")
    img.save('hello.png', 'PNG')

Parameters
==========

    style           Predefined style: 'github', 'gravatar', 'mono', 'mini', 'window' (Default: None)
    pixel_size      Size of a tile (Default: 10)
    bg_color        Background color. (Default: None)
    pixel_color     Tiles color (Default: 0)
    pixel_padding   Padding between tiles (Default: 0)
    image_padding   Padding on the image(Default: 0)
    tiles           Number of tiles that make the width and height of the image (Default: 5)
    min_fill        Minimun ratio of tile in the image (Default: 0.3)
    max_fill        Maximun ratio of tile in the image (Default: 0.9)
    vertical_sym    If image use vertical symmetry (Default: True)
    horizontal_sym  If image use vertical symmetry (Default: )

Valid color value
=================

    None -> transparent background, 
    0 -> the lighter color chosen for you, 
    1 -> the darker 
    An array describing the RGB(A) color (e.g. [125, 75, 250])
    An hexadecimal representation of the color (e.g. "0fd5e4")