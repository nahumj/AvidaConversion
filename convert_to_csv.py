#!/usr/bin/env python3
import argparse
import os.path
import collections
import string
import csv

DataFileType = collections.namedtuple(
    "DataFileType",
    ["file_name", "file_description", "number_of_columns"])

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

def check_header(header_lines, data_type):
    file_description = strip_comment_and_whitespace(header_lines[0])
    if file_description != data_type.file_description:
        raise InternalConvertFailure("Input file name doesn't match file description")
    last_header_line = header_lines[-1].strip()
    if last_header_line:
        raise InternalConvertFailure("Last Header Line Not Blank")
    
def get_timestamp_and_column_names(header):
    def parse_column_name(line):
        parts = line.split(':', maxsplit=1)
        if len(parts) != 2:
            raise InternalConvertFailure("Header Column Names Malformed: " + line)
        col_num = int(parts[0])
        col_name = parts[1].strip()
        return col_num, col_name
        
    
    header_clean = [strip_comment_and_whitespace(line) for line in header]
    del header_clean[-1] # Remove Blank Last Line
    del header_clean[0] # Remove File Description
    timestamp = header_clean.pop(0)
    column_names = []
    for expected_col_num_from_0, line in enumerate(header_clean):
        col_num, col_name = parse_column_name(line)
        if expected_col_num_from_0 + 1 != col_num:
            raise InternalConvertFailure("Header Column Names Misnumbered")
        sanitized_col_name = sanitize_name(col_name)
        column_names.append(sanitized_col_name)
    return timestamp, column_names

def sanitize_name(name):
    acceptable_characters = string.ascii_letters + string.digits + '_'
    letters = []
    for letter in name:
        if letter not in acceptable_characters:
            letter = '_'
        letters.append(letter)
    if letters[0] not in string.ascii_letters:
        letters = ['X', '_'] + letters
    return "".join(letters)

def strip_comment_and_whitespace(line):
    line_no_hash  = line.lstrip('#')
    return line_no_hash.strip()

def process_data(in_file, out_file, column_names):
    out_file.write(",".join(column_names) + '\n')
    writer = csv.writer(out_file, lineterminator='\n')

    reader = csv.reader(in_file, delimiter=' ')

    for row in reader:
        row_lengthed = row[:len(column_names)]
        writer.writerow(row_lengthed)

        
def convert(in_file, out_file):
    in_file_name = os.path.basename(in_file.name)

    if in_file_name not in FILE_NAME_TO_TYPE:
        raise ConvertFailure("Unknown file type: " + in_file_name)

    data_type = FILE_NAME_TO_TYPE[in_file_name]
    header = collect_header(in_file, data_type.number_of_columns)

    timestamp, column_names = get_timestamp_and_column_names(header)

    process_data(in_file, out_file, column_names)
    
    in_file.close()
    out_file.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Converts Avida .dat files to csv files.")
    parser.add_argument('in_file', type=argparse.FileType('r'))
    parser.add_argument('out_file', type=argparse.FileType('w'))
    args = parser.parse_args()

    convert(args.in_file, args.out_file)
