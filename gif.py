
"""Python module to open a GIF (Graphical Interchange Format) file and access its contents

This module contains functions to extract the following information from a GIF file:
File Header, Screen Descriptors, Global Colour Table, Image Descriptors and Image Data. This module
does not include support for GIF Extensions and only works for GIF files with a global colour table.
"""

def load_file(file_name):
    '''Takes in the path to a file, returns the file data in byte format and the file name'''
    
    # try except loop to recieve any errors if file is not found
    try:
        gif1 = open(file_name, 'rb')
        # print("gif file exiists")
        file = gif1.read()
        filename = file_name
    
    except:
        file = bytes(0)
        filename = "file not found"
    
    return file, filename

def extract_header(data):
    '''Takes gif data in byte format and reutrns the data header'''
    
    # header data found in the first 6 bytes, which are in ascii format
    header = data[0:6].decode()
    
    return header


def extract_screen_descriptor(data):
    '''Takes gif data in byte format and returns screen descriptors of the gif in integer format'''
    
    # screen descriptors are 7 bytes long starting from the 6th byte
    width = int.from_bytes(data[6:8], "little") # integer value of 2 bytes in little endian format
    height = int.from_bytes(data[8:10], "little")
    packed_data = data[10]
    binary_data = bin(packed_data).strip("0b")
    gc_fl = binary_data[0]
    cr = int(binary_data[1:4],2)
    sort_fl = int(binary_data[4],2)
    gc_size = int(binary_data[5:],2)
    bcolour_i = data[11]
    pxa_ratio = data[12]
    
    if pxa_ratio != 0:
        pxa_ratio = (pxa_ratio + 15)/64
    
    return width, height, gc_fl, cr, sort_fl, gc_size, bcolour_i, pxa_ratio
    


def extract_global_colour_table(data):
    '''Takes gif data in byte format and returns the global colour table (GCT) as a list. The nested list contains the RGB intensities of each colour as a another list'''
    
    # calling extract_screen_descriptor to get the size of the GCT
    scn_gc_size = extract_screen_descriptor(data)[5]
    
    
    total_colours = 2**(scn_gc_size+1)
    colour_table = []
    
    # GCT starts from 13th byte
    colour_bytes = data[13:13+(total_colours*3)]
    
    # appending RGB intensities of each colour from byte stream into the colour table
    for i in range(0, len(colour_bytes), 3):
        x = i
        indiv_colour = colour_bytes[x:x+3]
        indiv_colour_int = list(map(int, indiv_colour))
        colour_table.append(indiv_colour_int)
        
    return colour_table

def extract_image_descriptor(data):
    '''Takes gif data in byte format and returns the image descriptors '''
    
    # finding start of image descriptor
    # image descriptor block is exactly 10 bytes long
    
    colour_table = extract_global_colour_table(data)
    ID_index = 13 + len(colour_table)*3
    
    left = int.from_bytes(data[ID_index+1:ID_index+3], "little")
    top = int.from_bytes(data[ID_index+3:ID_index+5], "little")
    width = int.from_bytes(data[ID_index+5:ID_index+7], "little")
    height = int.from_bytes(data[ID_index+7:ID_index+9], "little")
    packed_field = data[ID_index+9]
    binary_data = format(packed_field, "b").zfill(8)
    lc_fl = int(binary_data[0],2)
    itl_fl = int(binary_data[1],2)
    sort_fl = int(binary_data[2],2)
    res = int(binary_data[3:5],2)
    lc_size = int(binary_data[5:],2)

    
    return left, top, width, height, lc_fl, itl_fl, sort_fl, res, lc_size
    
def extract_image(data):
    '''Takes gif data in byte format and returns the decompressed GIF image as a 3D array. 
    First dimension is the rows, second dimension is the columns and third dimension is the RGB components of that entry '''
    
    # finding start of image data
    # call extract_global_colour_table to get colour table 
    colour_table = extract_global_colour_table(data)
    length_byte = 23 + 1 + len(colour_table)*3 # byte for length of sub block

    lzw_min_size = data[length_byte-1]
    data_bytes_length = data[length_byte]
    read_bytes = bytes(0)

    # creating data byte list to read off, accounting for multiple sub blocks
    # looping until a length byte of 0 value is found, signalling the end of sub blocks
    while data_bytes_length != 0:
        if data[length_byte + 1 + data_bytes_length] == 0:
            sub_block = data[(length_byte+1):(length_byte+1+data_bytes_length)]
            data_bytes_length = 0
            read_bytes += (sub_block)
        else:
            length_byte = data[length_byte + 1 + data_bytes_length]
            sub_block = data[(length_byte+1):(length_byte+1+data_bytes_length)]
            read_bytes += sub_block
    
        
    # creating list of data bytes in binary format
    data_bin_list = [] 
    
    for i in read_bytes:
        bin_byte = format(i,"b").zfill(8)
        data_bin_list.append(bin_byte)
    
    
    # list reversed and converted to string to put bits in sequence 
    data_bin_list.reverse() 
    data_bin_string = "".join(data_bin_list)
    
    loc = 0 # index of binary bits being read
    bit_len = lzw_min_size+1 # initial length of binary bits for each code
    code_count = 0 # number of codes added to stream
    code_table_length = 2**lzw_min_size
    codestream = [] # initialize code stream
 
    colour_codes = list(range(0,2**lzw_min_size))
    clear_code = 2**lzw_min_size 
    end_code = 2**lzw_min_size + 1
    new_code_b = None
    
    # GETTING CODE STREAM
    while new_code_b != end_code:
        
        if loc == 0:
            new_code_b = data_bin_string[(loc - bit_len):] #getting each code in binary bits
        else:
            new_code_b = data_bin_string[(loc - bit_len):loc]
        
        # adding code to code stream in integer format
        new_code = int(new_code_b,2)
        codestream.append(new_code)
        code_count += 1 
        loc -= bit_len # location of next bits to be read
        
        # one code added to code table for every code in code stream
        # when next code is too large to be represented in bit_len bit, bit_len increases
        if code_table_length + code_count == 2**bit_len:
            bit_len += 1
        
        # terminate loop when end of information code reached
        if new_code == end_code:
            break

  
    # create code table as dictionary
    code_table = {i:[i] for i in colour_codes}
    code_table[clear_code] = ['clear code']
    code_table[end_code] = ['end of information']
    copy_code_table = code_table
    
    # GETTING INDEX STREAM FROM CODE STREAM
    index_stream = [] #initialize index stream 
    
    for i in range(len(codestream)):
        code = codestream[i]
    
        if code == clear_code:
            # reinitialize code table when clear code signal sent
            code_table = copy_code_table
            continue
        
        if i == 1: #first code is always in code table
            index_stream.append(code_table[code])
            continue
        #prev_code = codestream[i-1]
        prev_code_value = code_table[codestream[i-1]]
    
        # if code is in the code table
        if code in code_table and code != end_code:
            code_value = code_table[code]
            index_stream.append(code_value) # output code value to index stream
            x = prev_code_value[:]
            x.append(code_value[0]) # value of new code table entry
            code_table[len(code_table)] = x # add new row to code table
            
        elif code == end_code:
            break
        
        # if code is not in code table
        else:
            x = prev_code_value[:] 
            x.append(x[0]) # value of new code table entry
            index_stream.append(x) # output code-1 value + K to index stream
            code_table[len(code_table)] = x # add new row to code table
        
    
    # index stream is currently a list of nested lists, so they all need to be unpacked   
    unpacked_index_stream = [i for values in index_stream for i in values]
    
    
    # convert index stream into rgb colour map array
    gif_rgb_values = []
    image = []
    
    for i in unpacked_index_stream:
        gif_rgb_values.append(colour_table[i])
    
    # get width from above function
    width = extract_image_descriptor(data)[2] 
    
    # format decompressed gif into 3D array
    for i in range(0, len(gif_rgb_values), width):
        x = i
        image.append(gif_rgb_values[x:x+width])
    
    
    return image     


def main():
    print()
    print('GIF Image Viewer') 
    print()
    
    file_name = 'squares.gif' 
    
    data, info = load_file(file_name) 
    for i in range(len(data)):
        pass
        #print(hex(data[i])) 
    #print(info)
    print()

    # extract GIF signature 
    signature = extract_header(data) 
    print(signature)
    print()

    # extract screen descriptor
    scn_w, scn_h, scn_gc_fl, scn_cr, scn_sort_fl, scn_gc_size, scn_bcolour_i, scn_px_ratio = extract_screen_descriptor(data)
    print('screen width: ', end='') 
    print(scn_w)
    print('screen height: ', end='') 
    print(scn_h)
    print('global color table flag: ', end='') 
    print(scn_gc_fl)
    print('colour resolution: ', end='') 
    print(scn_cr)
    print('sort flag: ', end='') 
    print(scn_sort_fl)
    print('global colour size: ', end='') 
    print(scn_gc_size)
    print('background colour index: ', end='') 
    print(scn_bcolour_i)
    print('pixel aspect ratio: ', end='') 
    print(scn_px_ratio)
    print()
    
    # extract global color map
    gc_table = extract_global_colour_table(data)
    for i in range(2**(scn_gc_size+1)): 
        print("#",end='') 
        print(i,end='\t') 
        print(gc_table[i][0],end='\t') 
        print(gc_table[i][1],end='\t') 
        print(gc_table[i][2])
    print(type(gc_table)) 
    print(type(gc_table[0][0])) 
    print()
    
    # extract image descriptor
    img_left, img_top, img_w, img_h, img_lc_fl, img_itl_fl, img_sort_fl, img_res, img_lc_size = extract_image_descriptor(data)
    print('image left: ', end='') 
    print(img_left)
    print('image top: ', end='') 
    print(img_top)
    print('image width: ', end='')    
    print(img_w)
    print('image height: ', end='')
    print(img_h)
    print('local colour able flag: ', end='' )
    print(img_lc_fl)
    print('interlace flag (0: sequential, 1: interlaced): ', end='') 
    print(img_itl_fl)
    print('sort flag (0: unorderd, 1: ordered): ', end='') 
    print(img_sort_fl)
    print('reserved values: ', end='')
    print(img_res)
    print('local colour table size: ', end='') 
    print(img_lc_size)
    print()

    # extract image data
    img = extract_image(data)
    
    # print image red channel
    print('img red channel:') 
    for i in range(len(img)):
        for j in range(len(img[0])): 
            print(img[i][j][0],end='\t')
        print()
    print()

    # print image green channel 
    print('img green channel:') 
    for i in range(len(img)):
        for j in range(len(img[0])): 
            print(img[i][j][1],end='\t')
        print()
    print()

    # print image blue channel 
    print('img blue channel:') 
    for i in range(len(img)):
        for j in range(len(img[0])): 
            print(img[i][j][2],end='\t')
        print()
    print()


if __name__ == '__main__': 
    main()


