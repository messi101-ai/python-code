import argparse
import struct
import io
import os
import codecs
import json
import chardet
import logging
import datetime



def detect_inputfile_encoding(inputfile):
    """
    return the encoding of the file
    """
    with open(inputfile, 'rb') as rawdata:
        result = chardet.detect(rawdata.read(10000))
    input_encoding = result['encoding']
    return input_encoding

def read_json_schema(schemafile):
    """
    Read Json file and return colnames, offsets and returnheader".
    """
    with open(schemafile, 'r') as jsonschemafile:
         data=jsonschemafile.read()    
            
    json_dict = json.loads(data)
    colnames = json_dict['ColumnNames']
    offsets = json_dict['Offsets']
    includeheader = json_dict['IncludeHeader']
    fixedwidthencoding = json_dict['FixedWidthEncoding']
    delimitedencoding  = json_dict['DelimitedEncoding']
    return colnames,offsets,includeheader

def write_csv_file(inputfile,input_encoding,colnames,offsets,outputdir,errordir):
#   Check overhead of writing full string vs file
#   log dir and error dir 
#   include header 

# create colstring from colnames from schema file
    l = (len(colnames)) - 1
    colstring = ''
    for i in range(0, len(colnames)): 
        if i == l:
            colstring+="\"" + colnames[i].strip() + "\"" + "\r\n"
        else:
            colstring+="\"" + colnames[i].strip() + "\","
        
#     print(colnames)
#     print(colstring)

# convert offsets to int
    for i in range(0, len(offsets)): 
        offsets[i] = int(offsets[i]) 

# create slices from offset of schema file        
    widths = offsets
    slices = []
    pieces = []
    offset = 0
    for w in widths:
        slices.append(slice(offset, offset + w))
        offset += w
        
    input_filestream = codecs.open(inputfile, 'r',input_encoding)
    
# Create outputfilename
    input_filename, input_file_extension = os.path.splitext(inputfile)
    output_filename =  input_filename + ".csv"
    output_file = codecs.open(output_filename, 'w+', 'utf-8')

# add colnames to csvfile
    output_file.write(colstring)
    line_cnt = 1
    for line in input_filestream:
        outputstream = ''
        pieces = [line[slice] for slice in slices]
        l = (len(pieces)) - 1
        for i in range(0, len(pieces)):
            if i == l:
                pieces[i] = "\"" + pieces[i].strip() + "\"" + "\r\n"
                outputstream+=pieces[i]
#             print('a')
#             print(pieces[i])
            else:
                pieces[i] = "\"" + pieces[i].strip() + "\","
                outputstream+=pieces[i]
#             print(outputstream)
#     print('b')
#     print(outputstream)        
        output_file.write(outputstream)
#             print( "\"" + pieces[i].strip() + "\",")
#     print('a')
#     print(pieces)
    input_filestream.close()   
    output_file.close()
    print("csv complete") 

def main():
# input args
#     usage:python win1252_to_utf8.py -s schema_file -i input_files -o output_dir -e error_dir

    parser = argparse.ArgumentParser(description = 'Convert windows-1252 fixed width  to  utf-8 based on JSON schema')
    required_arguments = parser.add_argument_group('required arguments')
    required_arguments.add_argument('-s', '--schema_file', help='JSON schema file for fixed width file', required=True)
    required_arguments.add_argument('-i', '--input_file', help='Input windows-1252 fixed width file/s', required=True)
    required_arguments.add_argument('-o', '--output_dir', help='output directory for utf8 csv files', required=True)
    required_arguments.add_argument('-e', '--error_dir', help='output directory for error files', required=True)
    required_arguments.add_argument('-l', '--log_dir', help='output directory for error files', required=True)
    

    args = parser.parse_args()
    schemafile = args.schema_file
    inputfile = args.input_file
    outputdir = args.output_dir
    errordir = args.error_dir
    logdir = args.log_dir

    # validate args
   
    # setting logger info
    run_date=datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
    logfilename = logdir + 'fixed_file_to_csv_utf8_' + run_date
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logger = logging.getLogger()
    logger.addHandler(logging.FileHandler(logfilename, 'a'))
    print = logger.info
    print('a')
    print(schemafile)
#   Check if all input and output files/dirs for access and proper paths
    if not os.path.isdir(args.output_dir):
        print ("{0} is not a valid output directory")
        return 0
    if os.access(args.output_dir, os.W_OK) == False:
        print ("{0} is not a writable output directory")
        return 0
    
    if not os.path.isdir(args.error_dir):
        print ("{0} is not a valid output directory")
        return 0
    
    if os.access(args.error_dir, os.W_OK) == False:
        print ("{0} is not a writable output directory")
        return 0
    
    if not os.path.isdir(args.log_dir):
        print ("{0} is not a valid output directory")
        return 0
    if os.access(args.log_dir, os.W_OK) == False:
        print ("{0} is not a writable output directory")
        return 0
   
    if not os.path.isfile(schemafile):
        print ("Schema File not exists")
        return 0
    
    if not os.path.isfile(inputfile):
        print ("Input File not exists")    
        return 0    
    
#  read json schema file
    colnames,offsets,includeheader = read_json_schema(schemafile)
    if len(colnames) != len(offsets):
        print ("No of cols in Schema file do not match with offsets")

#  check encoding of input file
    
    input_encoding = detect_inputfile_encoding(inputfile)
    print(input_encoding)
    
# write to csv file 
    write_csv_file(inputfile,input_encoding,colnames,offsets,outputdir,errordir)
    print("complete") 
 
 
if __name__ == "__main__":
     main()
