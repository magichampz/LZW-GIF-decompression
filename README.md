# LZW-GIF-decompression

*As part of a programming assigment. The full assignment handout is provided above*

GIF files comprise a sequence of data blocks which contain information about the GIF format, header, screen descriptors, image descriptors, colour table and the image data, which is the bulk of the data blocks.  

### Functions
After importing gif.py, the functions described below may be used to view the GIF's data in an easily understandable format.

**data, info = load_file(gif_name)**
To store the gif data blocks in variable data. data (of type bytes) will then be passed into the following function

**extract_header(data)**
returns the header of the gif file in str format

**extract_screen_descriptor(data)**
returns screen descriptors (width, height, gc_fl, cr, sort_fl, gc_size, bcolour_i, pxa_ratio) in int format

**extract_global_colour_table(data)**
returns the RGB colour intensities of each colour in the GIF in a 2D list

**extract_image_descriptor(data)**
returns image descriptors (dimensions and flags) of GIF in int format

**extract_image_data(data)**
returns the decompressed GIF image as a 3D array, representing the RGB components of each cell in the GIF.


Run the main() function on squares.gif provided to view the outputs of each function, representing the information in the GIF.
sample-output.txt show the outputs you should expect to recieve from running main()


The compression method GIF's use is a variant of LZW (Lempel-Ziv-Welch) compression.
For more information on the GIF data blocks and LZW decompression, check out these links
https://giflib.sourceforge.net/whatsinagif/bits_and_bytes.html
https://giflib.sourceforge.net/whatsinagif/lzw_image_data.html
