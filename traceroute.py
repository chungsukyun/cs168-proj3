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
        if e[0] == "[":
            i += 1
    return i

def find_index_string(lst, s):
    i = 0
    while i < len(lst):
        e = lst[i]
        if e[:len(s)]==s:
            return i
        i += 1
    return ""

def find_string(lst, s):
    i = 0
    while i < len(lst):
        e = lst[i]
        if e[:len(s)]==s:
            return e
        i += 1
    return ""

def run_traceroute(hostname_file_name, num_packets, output_filename):
    hostnames = []
    hostname_file = open(hostname_file_name, 'r')
    line = hostname_file.readline().rstrip()
    while line != "":
        hostnames += [line]
        line = hostname_file.readline().rstrip()
    # traceroute_dict = {}
    timestamp = str(time.time())
    #datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")
    # traceroute_dict["timestamp"] = timestamp
    big_string = ""
    first = True
    for name in hostnames:
        name_hops = []
        ls_output, err = subprocess.Popen(["traceroute", "-A", "-q", str(num_packets), name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
        if first == True:
            big_string = ls_output
            first = False
        else:
            big_string += ls_output
    target = open(output_filename, "w")
    target.write(big_string)
    #     ls_output_lines = ls_output.splitlines()
    #     for line in ls_output_lines:
    #         line = line.split()
    #         if line[0] == "traceroute":
    #             continue
    #         if find_num_names(line) == 0:
    #             name_hops += [[{"name": "None", "ip": "None", "ASN": "None"}]]
    #         else:
    #             entry = []
    #             for i in range(find_num_names(line)):
    #                 ASN = ""
    #                 IP = ""
    #                 Name = ""
    #                 j = find_index_string(line, "[")
    #                 if line[j][1] == "*":
    #                     ASN = "None"
    #                 else:
    #                     ASN = line[j][3:(len(line[j])-1)]
    #                 if line[j-1][1] == "*":
    #                     IP = "None"
    #                 else:
    #                     IP = line[j-1][1:(len(line[j-1])-1)]
    #                 if line[j-2][0] == "*":
    #                     Name = "None"
    #                 else:
    #                     Name = line[j-2]
    #                 line = line[j+1:]
    #                 entry += [{"name": Name, "ip": IP, "ASN": ASN}]
    #             name_hops += [entry]
    #     traceroute_dict[name] = name_hops
    # with open(output_filename, "w") as fp:
    #     json.dump(traceroute_dict, fp)


if function_name == "run_traceroute":
    hostname_file_name = sys.argv[2]
    num_packets = int(sys.argv[3])
    output_filename = sys.argv[4]
    run_traceroute(hostname_file_name, num_packets, output_filename)

elif function_name == "parse_traceroute":
    raw_traceroute_filename = sys.argv[2]

else:
    print "The function you have called does not exist."
