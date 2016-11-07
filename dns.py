import subprocess
import json
import sys
import numpy
import math
import time
import datetime

function_name = sys.argv[1]

def run_dig(hostname_filename, output_filename, dns_query_server):
    hostnames = []
    hostname_file = open(hostname_file_name, 'r')
    line = hostname_file.readline().rstrip()
    while line != "":
        hostnames += [line]
        line = hostname_file.readline().rstrip()
    for name in hostnames:
        print name
        if dns_query_server == None:
            ls_output, err = subprocess.Popen(["dig", name, "@" + dns_query_server], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
        else:
            ls_output, err = subprocess.Popen(["dig", "+trace", "+tries=1", "+nofail", name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
        print ls_output

if function_name == "run_dig":
    hostname_filename = sys.argv[2]
    output_filename = sys.argv[3]
    if len(sys.argv) > 4:
        dns_query_server = sys.argv[4]
    else:
        dns_query_server = None
    run_dig(hostname_filename, output_filename, dns_query_server)
