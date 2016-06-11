__author__ = 'daph.kaplan, idan0610'
import sys
import os

symbol_table = {}
jump_table = {}
dest_table = {}
comp_table = {}


def _init_jump_table():
    '''
    Initiate the jump table.
    '''
    jump_table['null'] = '000'
    jump_table['JGT'] = '001'
    jump_table['JEQ'] = '010'
    jump_table['JGE'] = '011'
    jump_table['JLT'] = '100'
    jump_table['JNE'] = '101'
    jump_table['JLE'] = '110'
    jump_table['JMP'] = '111'


def _init_dest_table():
    '''
    Initiate the dest table.
    '''
    dest_table['null'] = '000'
    dest_table['M'] = '001'
    dest_table['D'] = '010'
    dest_table['MD'] = '011'
    dest_table['A'] = '100'
    dest_table['AM'] = '101'
    dest_table['AD'] = '110'
    dest_table['AMD'] = '111'


def _init_comp_table():
    '''
    Initiate the comp table.
    '''
    comp_table['0'] = '110101010'
    comp_table['1'] = '110111111'
    comp_table['-1'] = '110111010'
    comp_table['D'] = '110001100'
    comp_table['A'] = '110110000'
    comp_table['M'] = '111110000'
    comp_table['!D'] = '110001101'
    comp_table['!A'] = '110110001'
    comp_table['!M'] = '111110001'
    comp_table['-D'] = '110001111'
    comp_table['-A'] = '110110011'
    comp_table['-M'] = '111110011'
    comp_table['D+1'] = '110011111'
    comp_table['A+1'] = '110110111'
    comp_table['M+1'] = '111110111'
    comp_table['D-1'] = '110001110'
    comp_table['A-1'] = '110110010'
    comp_table['M-1'] = '111110010'
    comp_table['D+A'] = '110000010'
    comp_table['D+M'] = '111000010'
    comp_table['D-A'] = '110010011'
    comp_table['D-M'] = '111010011'
    comp_table['A-D'] = '110000111'
    comp_table['M-D'] = '111000111'
    comp_table['D&A'] = '110000000'
    comp_table['D&M'] = '111000000'
    comp_table['D|A'] = '110010101'
    comp_table['D|M'] = '111010101'
    comp_table['D<<'] = '010110000'
    comp_table['D>>'] = '010010000'
    comp_table['A<<'] = '010100000'
    comp_table['A>>'] = '010000000'
    comp_table['M<<'] = '011100000'
    comp_table['M>>'] = '011000000'





def _init_symbol_table():
    '''
    Initiate the symbol table.
    '''
    global symbol_table
    for i in range(0,16):
        symbol_table['R'+str(i)] = str(i)
    symbol_table['SCREEN'] = 16384
    symbol_table['KBD'] = 24576
    symbol_table['SP'] = 0
    symbol_table['LCL'] = 1
    symbol_table['ARG'] = 2
    symbol_table['THIS'] = 3
    symbol_table['THAT'] = 4


def first_scan(file_name):
    '''
    First scan of the file, in order to add symbols in the form of "(X)"
    :param file_name: the file
    '''
    lines_count = 0
    for line in file_name:
        clean_line = line.strip()
        if clean_line != '' and not clean_line.startswith('//') and not clean_line.startswith('('):
            lines_count += 1
        elif clean_line.startswith('('):
            if '//' in clean_line:
                clean_line = clean_line[:clean_line.find("//")]
                clean_line = clean_line.strip()
            table_name = clean_line.rsplit(')', 1)[0]
            table_name = table_name.rsplit('(', 1)[1]
            symbol_table[table_name] = lines_count

def decimal_binary(num):
    '''
    Convert from decimal representation to binary representation
    :param num: Decimal number to convert
    :return The binary representaion
    '''
    binary = int(num)
    binary = int(bin(binary)[2:])
    binary_string = str(binary)
    diff = 16 - len(binary_string)
    return "0" * diff + binary_string

def code_jump(string_jump):
    '''
    Returns the binary form of the given jump command
    :param string_jump: The jump command
    :return: Binary form of the jump command
    '''
    return jump_table[string_jump]

def code_dest(string_dest):
    '''
    Returns the binary form of the given dest command
    :param string_jump: The dest command
    :return: Binary form of the dest command
    '''
    return dest_table[string_dest]

def code_comp(string_comp):
    '''
    Returns the binary form of the given comp command
    :param string_jump: The comp command
    :return: Binary form of the comp command
    '''
    return comp_table[string_comp]


def parse(line):
    '''
    Parsing a single line from the file and calculating its binary form.
    :param line: The line to parse
    :return: Binary form of the line
    '''
    dest = "null"
    jump = "null"
    first_part = line

    if ";" in line:
        jump = line.rsplit(';', 1)[1]
        jump = jump.strip()
        first_part = line.rsplit(';', 1)[0]

    comp = first_part

    if "=" in first_part:
        comp = first_part.rsplit('=', 1)[1]
        comp = comp.strip()
        dest = first_part.rsplit('=', 1)[0]
        dest = dest.strip()

    return "1" +code_comp(comp) + code_dest(dest)+ code_jump(jump)



def second_scan(asm_file, hack_file):
    '''
    Second scan of the file. Passing through all the lines, parsing them, and
    converting them into binary form
    :param asm_file: The assembly file to parse
    :param hack_file: The results file
    '''
    num_line = 16
    for line in asm_file:
        clean_line = line.strip()
        if clean_line == '' or clean_line.startswith('//') or clean_line.startswith('('):
            # its a comment, or line in the form of "(X)", ignore it
            continue
        if '//' in clean_line:
            # The line has a comment at the end, remove it
            clean_line = clean_line[:clean_line.find("//")]
            clean_line = clean_line.strip()

        if clean_line.startswith('@'):
            #its a a-instruction
            address = clean_line.rsplit('@', 1)[1]
            if not address.isdigit():
                if address in symbol_table:
                    address = symbol_table[address]
                else:
                    symbol_table[address] = num_line
                    address = num_line
                    num_line += 1
            address = decimal_binary(address)
            hack_file.write(address+"\n")
        else:
            #its a c-instruction
            hack_file.write(parse(clean_line)+"\n")


def initiate_global_tables():
    '''
    Initiates the 3 tables of comp, dest and jump
    '''
    _init_comp_table()
    _init_dest_table()
    _init_jump_table()


def assemble_file(file_name):
    '''
    Assembling a single file
    :param file_name: The file to assemble
    '''
    _init_symbol_table()
    asm_file = open(file_name, 'r')
    name = file_name.rsplit('.', 1)[0]
    #create a file with the same name but is hack type
    hack_file = open(name+".hack", 'w')
    first_scan(asm_file)
    asm_file.seek(0)
    second_scan(asm_file, hack_file)
    asm_file.close()
    hack_file.close()
    global symbol_table
    symbol_table = {}



def main(args):
    '''
    Assembling a single file, or all asm files in the given directory
    :param args: file name, of directory name
    '''
    initiate_global_tables()
    if os.path.isfile(args):
        assemble_file(args)
    elif os.path.isdir(args):
        for filename in os.listdir(args):
            if(filename.endswith('.asm')):
                assemble_file(args + "/" + filename)
    else:
        print("this file doesnt exist")

main(sys.argv[1])
