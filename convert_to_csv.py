#!/usr/bin/env python3
import argparse
import os.path
import collections
import string
import csv
import os
import fnmatch

class ConvertFailure(Exception):
    """Exception raised by script caused by user error""" 
    pass

class InternalConvertFailure(Exception):
    """"Exception raised by script for internal (not user caused) error"""
    pass


def collect_header(in_file):
    lines = []

    while True:
        line = in_file.readline()
        if not line.strip():
            break
        lines.append(line)
    return lines

def get_column_names(header):
    def parse_column_name(line):
        parts = line.split(':', maxsplit=1)
        if len(parts) != 2:
            raise InternalConvertFailure("Header Column Names Malformed: " + line)
        col_num = int(parts[0])
        col_name = parts[1].strip()
        return col_num, col_name
        
    
    header_clean = [strip_comment_and_whitespace(line) for line in header]
    column_names = []
    
    number_of_columns, _ = parse_column_name(header_clean[-1])
    header_cols = header_clean[len(header_clean) - number_of_columns :]

    for expected_col_num_from_0, line in enumerate(header_cols):
        col_num, col_name = parse_column_name(line)
        if expected_col_num_from_0 + 1 != col_num:
            raise InternalConvertFailure(
                "Header Column Names Misnumbered(expected: {}, got: {})".format(
                    expected_col_num_from_0, col_num))
        sanitized_col_name = sanitize_name(col_name)
        column_names.append(sanitized_col_name)
    return column_names

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
    header = collect_header(in_file)

    column_names = get_column_names(header)

    process_data(in_file, out_file, column_names)
    
    in_file.close()
    out_file.close()

    
def convert_files_in_directory(directory, delete_after_conversion):
    def convert_dat_file_path_to_csv(dat_path):
        no_ext = dat_path[:-3]
        return no_ext + "csv"
        
    dat_paths = []
    for root, dirnames, filenames in os.walk(directory):
        
        for filename in fnmatch.filter(filenames, '*.dat'):
            file_path = os.path.join(root, filename)
            dat_paths.append(file_path)

    for dat_path in dat_paths:
        dat_handle = open(dat_path, 'r')
        csv_handle = open(convert_dat_file_path_to_csv(dat_path), 'w')
        convert(dat_handle, csv_handle)
        dat_handle.close()
        csv_handle.close()
        if delete_after_conversion:
            os.remove(dat_path)

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Converts Avida .dat files to csv files.")
    
    parser.add_argument("in_file", type=argparse.FileType('r'), nargs='?')
    parser.add_argument("out_file", type=argparse.FileType('w'), nargs='?')
    parser.add_argument("--directory")
    parser.add_arguemnt("--delete_after_conversion", action='store_true')
    args = parser.parse_args()
    if args.directory:
        convert_files_in_directory(
            args.directory, args.delete_after_conversion)
    else:
        if args.in_file and args.out_file:
            convert(args.in_file, args.out_file)
