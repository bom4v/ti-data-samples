#!/usr/bin/env python3

#
import getopt, sys, re, csv, tarfile, inspect, os
#
from copy import deepcopy
# BZip2
import bz2
# python-magic (to recognize file types): http://github.com/ahupp/python-magic
import magic
#
from collections import OrderedDict
#
from datetime import datetime
# Basic Encoding Rules (BER)
from pyasn1.codec.ber import decoder as ber_decoder
# Distinguished Encoding Rules (DER)
from pyasn1.codec.der import decoder as der_decoder
from pyasn1.codec.native.encoder import encode as py_encode
# Errors
from pyasn1.error import *
# Pretty print
import pprint
# NRT RDE (near real-time RDE)
from nrtrde import Nrtrde

# Retrieving the directory of the Python script
py_filepath = inspect.getframeinfo (inspect.currentframe()).filename
py_dirname = os.path.dirname (os.path.abspath (py_filepath))

# Global variables
def_nrt_filepath = py_dirname + '/../data/nrt/NRUKRKSRUSUT0304561'

fieldnames = ['specificationVersionNumber', 'releaseVersionNumber', 'fileName',
              'fileAvailableTimeStamp', 'fileUtcTimeOffset',
              'sender', 'recipient', 'sequenceNumber', 'callEventsCount',
              'eventType',
              'imsi', 'imei', 'callEventStartTimeStamp', 'utcTimeOffset',
              'callEventDuration', 'causeForTermination',
              'accessPointNameNI', 'accessPointNameOI',
              'dataVolumeIncoming', 'dataVolumeOutgoing',
              'sgsnAddress', 'ggsnAddress',
              'chargingId', 'chargeAmount',
              'teleServiceCode', 'bearerServiceCode', 'supplementaryServiceCode',
              'dialledDigits', 'connectedNumber', 'thirdPartyNumber',
              'callingNumber', 'recEntityId', 'callReference',
              'locationArea', 'cellId', 'msisdn', 'servingNetwork']

bcd_fieldnames = ['imei', 'imsi', 'msisdn']

date_fieldnames = ['fileAvailableTimeStamp', 'callEventStartTimeStamp']

byte_fieldnames = ['sender', 'recipient', 'sequenceNumber',
                   'utcTimeOffset', 'teleServiceCode', 'bearerServiceCode',
                   'supplementaryServiceCode',
                   'dialledDigits',
                   'connectedNumber', 'thirdPartyNumber', 'callingNumber',
                   'recEntityId', 'accessPointNameNI', 'accessPointNameOI',
                   'sgsnAddress', 'ggsnAddress']

def usage (script_name):
    """
    Display the usage.
    """

    print ("")
    print ("Usage: %s [options]" % script_name)
    print ("")
    print ("That script explores a few details of NRT data files")
    print ("")
    print ("Options:")
    print ("  -h, --help                   : outputs this help and exits")
    print ("  -v, --verbose                : verbose output (debugging)")
    print ("  -i, --input <NRT file-path>  : NRT data file")
    print ("                      Default  : '" + def_nrt_filepath + "'")
    print ("  -o, --output <CSV file-path> : CSV data file")
    print ("                      Default  : standard output")
    print ("")  

def handle_opt():
    """
    Handle the command-line options
    """

    try:
        opts, args = getopt.getopt (sys.argv[1:], "hv:i:o:",
                                    ["help", "verbose", "input", "output"])

    except (getopt.GetoptError, err):
        # Print help information and exit. It will print something like
        # "option -d not recognized"
        print (str (err))
        usage (sys.argv[0], usage_doc)
        sys.exit(2)
    
    # Options
    verboseFlag = False
    nrt_filepath = def_nrt_filepath
    nrt_file_param = sys.stdin
    csv_file_param = sys.stdout
    
    # Handling
    for o, a in opts:
        if o in ("-h", "--help"):
            usage (sys.argv[0])
            sys.exit()
        elif o in ("-v", "--verbose"):
            verboseFlag = True
        elif o in ("-i", "--input"):
            nrt_file_param = a
        elif o in ("-o", "--output"):
            csv_file_param = a
        else:
            assert False, "Unhandled option"

    # Report the configuration
    print ("Input NRT data file: '" + str(nrt_file_param) + "'")
    print ("Output CSV data file: '" + str(csv_file_param) + "'")
    return (verboseFlag, nrt_file_param, csv_file_param)

def bcdToDecimal (bcd_string):
    """
    Decoder of BCD (Binary Coded Decimals) strings
    """
    dec_string = ''
    for char in bcd_string:
        for val in (char >> 4, char & 0xF):
            if val == 0xF:
                break
            dec_string += str(val)
    #
    return dec_string

def toString (byte_string, field_name):
    """
    Reformat the string
    """
    result_string = ''
    try:
        result_string = byte_string.decode ('utf-8')
    except AttributeError:
        print ("The '" + field_name + "' field is not a UTF-8 string: '" + str (byte_string)+ "'")
        
    return result_string

def toDateString (date_byte_string, field_name):
    """
    Reformat the date-time string
    """
    date_string = toString (date_byte_string, field_name)
    date_string = datetime.strptime (date_string, '%Y%m%d%H%M%S')
    date_string = datetime.strftime (date_string, '%Y-%m-%d %H:%M:%S')
    return date_string

def extractEventList (nrt_dict):
    """
    Extract a list of flattened call event structures
    """
    call_event_list = []
    flattened_dict = {key: None for key in fieldnames}
        
    # Level 1 (global level): file details
    for k1, v1 in nrt_dict.items():
        # The 'utcTimeOffset' name is used for two fields, one global
        # and the other one at the call event details (level #4).
        # The value is a byte string, and has to be converted into a standard
        # string
        if k1 == 'utcTimeOffset':
            k1 = 'fileUtcTimeOffset'
            v1 = toString (v1, k1)

        # Date-Time string
        elif k1 in date_fieldnames:
            v1 = toDateString (v1, k1)

        # Byte strings
        elif k1 in byte_fieldnames:
            v1 = toString (v1, k1)

        # Register the key-value pairs at the global level
        if k1 != 'callEvents':
            flattened_dict[k1] = v1

        else:
            # Level 2: list of events
            for call_event in v1:

                # Reset the list of fields
                tmp_field_list = []

                # Level 3: type of events
                for event_type, event_details in call_event.items():
                    flattened_dict['eventType'] = event_type

                    # Level 4: call event details
                    for k2, v2 in event_details.items():
                        # Level 5: service code
                        if k2 == 'serviceCode':
                            svc_code_list = v2
                            assert len(v2) == 1
                            for k3, v3 in svc_code_list.items():
                                k2 = k3
                                v2 = v3

                        # IMEI / IMSI are BCD strings
                        if k2 in bcd_fieldnames:
                            v2 = bcdToDecimal (v2)

                        # Date-Time strings
                        elif k2 in date_fieldnames:
                            v2 = toDateString (v2, k2)

                        # Byte strings
                        elif k2 in byte_fieldnames:
                            v2 = toString (v2, k2)                            

                        #
                        flattened_dict[k2] = v2

                        # Add 'k2' in the fields, which have been set
                        tmp_field_list.append (k2)

                    # Add the flattened event structure to the dedicated list
                    call_event_list.append (deepcopy (flattened_dict))

                    # DEBUG
                    #print ("tmp_field_list: " + str(tmp_field_list))
                    #print ("flattened_dict: " + str(flattened_dict))

                    # Reset the values, which have just been set,
                    # for the next turn
                    for k4 in tmp_field_list:
                        flattened_dict[k4] = None

    #
    return call_event_list

def extract_details_from_nrt (nrt_struct):
    """
    Extract some details of call events
    """
    # DEBUG
    # print (nrt_struct.prettyPrint())

    # Translate the NRT structure into a Python one
    py_nrt = py_encode (nrt_struct)

    # DEBUG
    # pp = pprint.PrettyPrinter (indent = 2)
    # pp.pprint (py_nrt)

    #
    return py_nrt

def extract_details_from_filepath (nrt_file_path):
    """
    Extract some details of call events
    """

    # Build a NRT structure from the DER-serialized ASN.1 string
    nrt = None
    with open (nrt_file_path, mode='rb') as nrt_file:
        nrt_file_content = nrt_file.read()
    
        # Undo DER serialization, reconstruct NRT structure
        try:
            nrt, rest_of_input = ber_decoder.decode (nrt_file_content,
                                                     asn1Spec = Nrtrde.Nrtrde())
        except SubstrateUnderrunError:
            print ("Error in decoding '" + nrt_file_path + "'. Skipping it")
            nrt = None

    # Translate the NRT structure into a Python one
    py_nrt = None
    if nrt is not None:
        py_nrt = extract_details_from_nrt (nrt)

    #
    return py_nrt

def extract_details_from_archive (file_path, arch_type):
    """
    Extract details (ie, NRT structures) from a tar-ball archive
    """
    #
    arch_open_attr = 'r:'
    if arch_type == 'bzip2':
        arch_open_attr += 'bz2'
    elif arch_type == 'gzip':
        arch_open_attr += 'gz'
    elif arch_type == 'xz':
        arch_open_attr += 'xz'
    else:
        err_msg = "'" + arch_type + "' is not a known compression type for an archive"
        raise TypeError (err_msg)

    # DEBUG
    print ("Tar-ball file: '" + file_path + "', detected archive type: " + arch_type)
    
    # Count the number of files in the tar-ball archive
    with tarfile.open (file_path, arch_open_attr) as archive:
        nb_of_files = sum (1 for tar_info in archive if tar_info.isreg())

    # Browse the tar-ball archive
    idx = 0; displayed = False
    with tarfile.open (file_path, arch_open_attr) as archive:
        for tar_info in archive:
            # DEBUG
            # print ("File name: " + tar_info.name + ", file size: " + str(tar_info.size))
        
            if tar_info.isdir():
                # A directory
                continue
            elif tar_info.isreg():
                # A regular file
                idx += 1

                # DEBUG
                pct = int (100.0 * idx / nb_of_files)
                if pct % 10 == 0 and not displayed:
                    print (str(pct) + "% done: " + str(idx) + " / " + str(nb_of_files))
                    displayed = True
                elif pct %10 == 1:
                    displayed = False

                # Extract the file from the tar-ball archive
                nrt_file = archive.extractfile (tar_info)
                nrt_file_content = nrt_file.read()
    
                # Undo DER serialization, reconstruct NRT structure
                nrt = None
                try:
                    nrt, rest_of_input = ber_decoder.decode (nrt_file_content,
                                                             asn1Spec = Nrtrde.Nrtrde())
                except SubstrateUnderrunError:
                    print ("Error in decoding '" + tar_info.name + "' (size: " + str(tar_info.size) + ", type: '" + str(tar_info.type) + "'). Skipping it")
                    nrt = None

                # Translate the NRT structure into a Python one
                py_nrt = None
                if nrt is not None:
                    py_nrt = extract_details_from_nrt (nrt)

                # Clean the temporary extracted files
                nrt_file.close()
                archive.members = []

                #
                yield py_nrt

            else:
                # Unkown object extracted from the tar-ball archive
                err_msg = "Unknown file/object type. Name: " + tar_info.name + ", size: " + tar_info.size
                raise IOError (err_msg)        
    
def extract_details_from_stdin ():
    """
    Extract details (ie, NRT structures) from stdin
    """
    # Extract the NRT structures from the stdin
    nrt_file = sys.stdin.buffer.readlines()
    for nrt_file_content in nrt_file:
        # Undo DER serialization, reconstruct NRT structure
        nrt = None
        try:
            nrt, rest_of_input = ber_decoder.decode (nrt_file_content,
                                                     asn1Spec = Nrtrde.Nrtrde())
        except (SubstrateUnderrunError, PyAsn1Error) as err:
            print ("Error in decoding standard input: " + str(err))
            nrt = None
            continue

        # Translate the NRT structure into a Python one
        py_nrt = None
        if nrt is not None:
            py_nrt = extract_details_from_nrt (nrt)

        #
        yield py_nrt
    
def init_csv_file (csv_file_param):
    """
    Add the list of flattened event structures into the CSV file
    """
    csv_file = None
    if isinstance (csv_file_param, str):
        # The parameter is a file-path
        csv_file = open (csv_file_param, 'w', newline = '')

    elif hasattr (csv_file_param, 'write'):
        # The parameter is already a file (normally, stdout)
        csv_file = csv_file_param
        
    else:
        # Unknown
        raise IOError ('[Error] Output file parameter "' + str(csv_file_param) + '" unkown')

    # Write the header
    fileWriter = csv.DictWriter (csv_file, delimiter='^',
                                 fieldnames = fieldnames,
                                 dialect = 'unix', quoting = csv.QUOTE_NONE)

    #
    fileWriter.writeheader()    

def add_to_csv_file_from_nrt_struct (nrt_struct, csv_file_param):
    """
    Extract call events from a NRT structure,
    and add them into the given CSV file
    """
    # Extract a list of flattened call event structures
    call_event_list = extractEventList (nrt_struct)

    csv_file = None
    if isinstance (csv_file_param, str):
        # The parameter is a file-path
        csv_file = open (csv_file_param, 'a', newline = '')

    elif hasattr (csv_file_param, 'write'):
        # The parameter is already a file (normally, stdout)
        csv_file = csv_file_param

    else:
        # Unknown
        raise IOError ('[Error] Output file parameter "' + str(csv_file_param) + '" unkown')

    # Add the list of flattened event structures into the CSV file
    fileWriter = csv.DictWriter (csv_file, delimiter='^',
                                 fieldnames = fieldnames,
                                 dialect = 'unix', quoting = csv.QUOTE_NONE)

    # Browse the list of events
    for nrt_dict in call_event_list:
        # Write the dictionary
        fileWriter.writerow (nrt_dict)

def add_to_csv_file_from_nrt_file (nrt_file_param, csv_file_param):
    """
    Extract call events from a NRT file,
    and add them into the given CSV file
    """

    nrt_file = None
    if isinstance (nrt_file_param, str):
        # The parameter is a file-path
        # Detect the type of the file, in the Unix sense (it may be a directory)
        nrt_file_type = magic.from_file (nrt_file_param, mime = True)
        arch_type_bgn_idx = nrt_file_type.find ('application/x-') + 14

        if arch_type_bgn_idx == 14:
            # The input is an archive
            arch_type = nrt_file_type[arch_type_bgn_idx:]

            # The archive contains several NRT files, each of which holds
            # a NRT structure
            nrt_struct_gen = extract_details_from_archive (nrt_file_param,
                                                           arch_type)

            #
            if nrt_struct_gen is not None:
                for nrt_struct in nrt_struct_gen:
                    # Dump the content of the NRT structure (ie, call events)
                    # into the CSV file
                    add_to_csv_file_from_nrt_struct (nrt_struct, csv_file_param)

        else:
            # The input is a single NRT file
            # When the 'application/x-' sub-string cannot be found,
            # -1 is returned
            assert arch_type_bgn_idx == 13

            # The NRT file is converted to a NRT structure
            nrt_struct = extract_details_from_filepath (nrt_file_param)

            if nrt_struct is not None:
                # Dump the content of the NRT structure (ie, call events)
                # into the CSV file
                add_to_csv_file_from_nrt_struct (nrt_struct, csv_file_param)

    elif hasattr (nrt_file_param, 'readlines'):
        # The parameter is already a file (normally, stdin).
        # There may be several NRT data streams, each of which holds
        # a NRT structure
        nrt_struct_gen = extract_details_from_stdin ()

        #
        if nrt_struct_gen is not None:
            for nrt_struct in nrt_struct_gen:
                # Dump the content of the NRT structure (ie, call events)
                # into the CSV file
                add_to_csv_file_from_nrt_struct (nrt_struct, csv_file_param)

    else:
        # Unknown
        raise IOError ('[Error] Input file parameter "' + str(nrt_file_param) + '" unkown')
    
# How to profile: execute this and uncomment @profile
# $ kernprof.py --line-by-line --view nrt.py
#@profile
def main():
    """
    Main
    """
    # Parse the command-line options
    (verboseFlag, nrt_file_param, csv_file_param) = handle_opt()

    # Initialize the CSV file with the header
    init_csv_file (csv_file_param)

    # Read mobile-related events from the NRT file
    add_to_csv_file_from_nrt_file (nrt_file_param, csv_file_param)

def _test():
    """When called directly, launching doctests.
    """
    import doctest
    doctest.testmod()    

if __name__ == "__main__":
    #_test()
    main()
