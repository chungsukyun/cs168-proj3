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
    big_string = "timestamp: " + timestamp +"\n"
    for name in hostnames:
        # name_hops = []
        ls_output, err = subprocess.Popen(["traceroute", "-A", "-q", str(num_packets), name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
        big_string += ls_output
    target = open(output_filename, "w")
    target.write(big_string)

def parse_traceroute(raw_traceroute_filename, output_filename):
    f = open(raw_traceroute_filename, "r")
    file_string = f.read()
    file_lines = file_string.splitlines()
    name_hops = []
    hostname = ""
    traceroute_dict = {}
    for line in file_lines:
        if line[:10] == "timestamp:":
            name_hops = line[11:]
            hostname = "timestamp"
            continue
        if line[:10] == "traceroute" or line[:7] == "Tracing":
            if hostname != "":
                traceroute_dict[hostname] = name_hops
            line = line.split()
            hostname = line[2]
            name_hops = []
            continue
        if find_num_names(line) == 0:
            name_hops += [[{"name": "None", "ip": "None", "ASN": "None"}]]
        else:
            line = line.split()
            entry = []
            for i in range(find_num_names(line)):
                ASN = ""
                IP = ""
                Name = ""
                j = find_index_string(line, "[")
                if line[j][1] == "*":
                    ASN = "None"
                else:
                    x = 0
                    b = False
                    while x < len(line[j]):
                        if line[j][x] == "/":
                            b = True
                            break
                        x += 1
                    if b == True:
                        ASN = line[j][3:x] + "/" + line[j][x+3:(len(line[j])-1)]
                        print ASN
                    else:
                        ASN = line[j][3:(len(line[j])-1)]
                if line[j-1][1] == "*":
                    IP = "None"
                else:
                    IP = line[j-1][1:(len(line[j-1])-1)]
                if line[j-2][0] == "*":
                    Name = "None"
                else:
                    Name = line[j-2]
                line = line[j+1:]
                entry += [{"name": Name, "ip": IP, "ASN": ASN}]
        name_hops += [entry]
    traceroute_dict[hostname] = name_hops
    with open(output_filename, "w") as fp:
        json.dump(traceroute_dict, fp)

def append():
    f1 = open("traceroute_a_1.json")
    f2 = open("traceroute_a_2.json")
    f3 = open("traceroute_a_3.json")
    f4 = open("traceroute_a_4.json")
    f5 = open("traceroute_a_5.json")
    f1_str = f1.read()
    f2_str = f2.read()
    f3_str = f3.read()
    f4_str = f4.read()
    f5_str = f5.read()
    with open("tr_a.json", "w") as fp:
        fp.write("%s \n %s \n %s \n %s \n %s" % (f1_str, f2_str, f3_str, f4_str, f5_str))

if function_name == "run_traceroute":
    hostname_file_name = sys.argv[2]
    num_packets = int(sys.argv[3])
    output_filename = sys.argv[4]
    run_traceroute(hostname_file_name, num_packets, output_filename)

elif function_name == "parse_traceroute":
    raw_traceroute_filename = sys.argv[2]
    output_filename = sys.argv[3]
    parse_traceroute(raw_traceroute_filename, output_filename)

elif function_name == "append":
    append()
else:
    print "The function you have called does not exist."
