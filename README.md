# LZW-GIF-decompression

GIF files comprise a sequence of data blocks which contain information about the GIF format, header, screen descriptors, image descriptors, colour table and the image data, which is the bulk of the data blocks.

After importing gif.py, the functions described below may be used to view the GIF's data in an easily understandable format.



extract_header(data)


The compression method GIF's use is a variant of LZW (Lempel-Ziv-Welch) compression
