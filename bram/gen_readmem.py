import argparse
import pathlib

'''
This module is used to generate a Verilog file for use by readmemh/readmemb
for text files.
'''

def isascii(s):
    """Check if the characters in string s are in ASCII, U+0-U+7F."""
    return len(s) == len(s.encode())

def write_char(write_file, char_to_write, binary, bit_width = 8):

    ## Update character to print in comment
    if char_to_write == '\n':
        char_to_print_in_comment = "\\n"
    elif char_to_write == '\r':
        char_to_print_in_comment = "\\r"
    elif char_to_write == "\0":
        char_to_print_in_comment = ""
    else:
        char_to_print_in_comment = char_to_write

    # check for non-ascii
    if not isascii(char_to_write):
        # For non-ascci characters, write a space
        comment = f"// Non-ASCII character: \'{char_to_print_in_comment}\'"
        char_to_write = ' '
    else:
        comment = f"// {char_to_print_in_comment}"

    # Data format
    if binary:
        text_data = f"{ord(char_to_write):0{bit_width}b}"
    else:
        text_data = f"{ord(char_to_write):02x}"
    write_file.write(f"{text_data} {comment}\n")

def main():
    parser = argparse.ArgumentParser(
                    prog='gen_readmem',
                    description='Generates a Verilog file for use by readmemh/readmemb')
    parser.add_argument('input_filename', type=str, help='The name of the file to parse')
    parser.add_argument('output_filename', type=str, help='The name of the file to generate')
    parser.add_argument('--width', type=int, default=8, help='The width of the data in bits')
    parser.add_argument('-b', '--binary', action='store_true', help="Generate binary file")
    parser.add_argument('-r', '--cr', action='store_true', help="Add carriage return to the end of each line")
    parser.add_argument('-l', '--length', type=int, help="Number of elements in memory (for default values)")
    args = parser.parse_args()

    write_file = open(args.output_filename, 'w')
    python_path = pathlib.Path(__file__).resolve()
    write_file.write(f"// Generated by \'{python_path.name}\' from {args.input_filename}\n")
    values = 0
    with open(args.input_filename, 'r') as read_file:
        while True:
            char = read_file.read(1)
            if not char:
                break
            write_char(write_file,char,args.binary)    
            values += 1
            if args.cr and char == '\n':
                write_char(write_file,'\r',args.binary)
                values += 1
    if args.length:
        for i in range(args.length-values):
            write_char(write_file,'\0',args.binary)

    write_file.close()

if __name__ == "__main__":
    main()