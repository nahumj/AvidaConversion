#!/usr/bin/env python3
import argparse
import os.path
import collections

DataFileType = collections.namedtuple(
    "DataFileType",
    ["file_name", "first_line", "number_of_columns"])

FILE_NAME_TO_TYPE = {
    "time.dat":DataFileType("time.dat", "Avida time data", 4)
    }

class ConvertFailure(Exception):
    """Exception raised by script caused by user error""" 
    pass

class InternalConvertFailure(Exception):
    """"Exception raised by script for internal (not user caused) error"""
    pass


def collect_header(in_file, number_of_columns):
    lines = []

    # Number of header lines
    # 1 File Description
    # 2 Time Stamp of Run
    # 3 (multiple) Column descriptions
    # 4 Blank Spacer Line
    number_of_header_lines = 3 + number_of_columns
            
    for _ in range(number_of_header_lines):
        lines.append(in_file.readline())
    return lines



def strip_comment_and_whitespace(line):
    line_no_hash  = line.lstrip('#')
    return line_no_hash.strip()

def convert(in_file, out_file):
    in_file_name = os.path.basename(in_file.name)

    if in_file_name not in FILE_NAME_TO_TYPE:
        raise ConvertFailure("Unknown file type: " + in_file_name)
    data_type = FILE_NAME_TO_TYPE[in_file_name]

    
    
    first_line  = in_file.readline()
    first_line_striped = strip_comment_and_whitespace(first_line)

    
    print(in_file_name)
    print(first_line_striped)
    in_file.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Converts Avida .dat files to csv files.")
    parser.add_argument('in_file', type=argparse.FileType('r'))
    parser.add_argument('out_file', type=argparse.FileType('w'))
    args = parser.parse_args()

    convert(args.in_file, args.out_file)
