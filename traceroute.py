import subprocess
import json
import sys
import numpy
import math
import time
import datetime

function_name = sys.argv[1]

def find_num_names(lst):
    i = 0
    for e in lst:
        if e[:3] == "[AS":
            i += 1
    return i

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
    traceroute_dict = {}
    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")
    traceroute_dict["timestamp"] = timestamp
    print traceroute_dict["timestamp"]
    for name in hostnames:
        ls_output, err = subprocess.Popen(["traceroute", "-A", "-q", str(num_packets), name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
        ls_output_lines = ls_output.splitlines()
        for line in ls_output_lines:
            line = line.split()
            if line[0] == "traceroute":
                continue
            if find_num_names(line) == 0:
                pass


elif function_name == "parse_traceroute":
    pass
else:
    print "The function you have called does not exist."
