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
    hostname_file = open(hostname_filename, 'r')
    line = hostname_file.readline().rstrip()
    while line != "":
        hostnames += [line]
        line = hostname_file.readline().rstrip()
    json_list = []
    for name in hostnames:
        name_dict = {}
        name_dict["Name"] = name
        if dns_query_server != None:
            ls_output, err = subprocess.Popen(["dig", name, "@" + dns_query_server], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
        else:
            ls_output, err = subprocess.Popen(["dig", "+trace", "+tries=1", "+nofail", "+nodnssec", name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
            name_dict["Success"] = True
            query_list = []
            time_lines = ls_output.split(";;")
            i = 1
            print ls_output
            while i < len(time_lines) - 1:
                time = int(time_lines[i+1].split()[6])
                lines = time_lines[i].splitlines()[1:]
                for line in lines:
                    query_dict = {}
                    line = line.split()
                    print line
                    query_dict["Queried name"] = line[0]
                    query_dict["TTL"] = int(line[1])
                    query_dict["Type"] = line[3]
                    query_dict["Data"] = line[4]
                i += 1


            print ls_output

if function_name == "run_dig":
    hostname_filename = sys.argv[2]
    output_filename = sys.argv[3]
    if len(sys.argv) > 4:
        dns_query_server = sys.argv[4]
    else:
        dns_query_server = None
    run_dig(hostname_filename, output_filename, dns_query_server)
