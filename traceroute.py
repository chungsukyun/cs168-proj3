import subprocess
import json
import sys
import numpy
import math

function_name = sys.argv[1]

if function_name == "run_traceroute":
    hostnames = []
    hostname_file_name = sys.argv[2]
    hostname_file = open(hostname_file_name, 'r')
    line = hostname_file.readline().rstrip()
    while line != "":
        hostnames += [line]
        line = hostname_file.readline().rstrip()
    num_packets = int(sys.argv[3])
    output_filename = sys.argv[4]
    print hostnames
    for name in hostnames:
        ls_output, err = subprocess.Popen(["traceroute", "-A", "-q", str(num_packets), name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
        ls_output_lines = ls_output.splitlines()
        print ls_output_lines[1][0]

elif function_name == "parse_traceroute":
    pass
else:
    print "The function you have called does not exist."
