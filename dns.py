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
        for j in range(5):
            name_dict = {}
            name_dict["Name"] = name
            if dns_query_server != None:
                ls_output, err = subprocess.Popen(["dig", name, "@" + dns_query_server], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
                queries = ls_output.split("; <")[1:]
                name_dict["Success"] = True
                query_list = []
                for query in queries:
                    query_dict = {}
                    print query.splitlines()[-5].split()[2]
                    query = query.split(";;")[6:]
                    ans_list = []
                    for section in query:
                        section = section.splitlines()[1:]
                        for line in section:
                            if len(line) == 0:
                                continue
                            ans_dict = {}
                            line = line.split()
                            ans_dict["Queried name"] = line[0]
                            ans_dict["TTL"] = int(line[1])
                            ans_dict["Type"] = line[3]
                            ans_dict["Data"] = line[4]
                            ans_list += [ans_dict]
                        query_dict["Answers"] = ans_list
                        query_list += [query_dict]
                    name_dict["Queries"] = query_list
                    json_list += [name_dict]
            else:
                ls_output, err = subprocess.Popen(["dig", "+trace", "+tries=1", "+nofail", "+nodnssec", name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
                name_dict["Success"] = True
                query_list = []
                time_lines = ls_output.split(";;")
                i = 1
                while i < len(time_lines) - 1:
                    query_dict = {}
                    time = int(time_lines[i+1].split()[6])
                    query_dict["Time in millis"] = time
                    lines = time_lines[i].splitlines()[1:]
                    ans_list = []
                    for line in lines:
                        if len(line) == 0:
                            continue
                        ans_dict = {}
                        line = line.split()
                        ans_dict["Queried name"] = line[0]
                        ans_dict["TTL"] = int(line[1])
                        ans_dict["Type"] = line[3]
                        ans_dict["Data"] = line[4]
                        ans_list += [ans_dict]
                    query_dict["Answers"] = ans_list
                    query_list += [query_dict]
                    i += 1
                name_dict["Queries"] = query_list
                json_list += [name_dict]
    with open(output_filename, "w") as fp:
        json.dump(json_list, fp)

def get_average_ttls(filename):
    f = open(filename, "r")
    f_str = f.read()
    f_list = json.loads(f_str)

if function_name == "run_dig":
    hostname_filename = sys.argv[2]
    output_filename = sys.argv[3]
    if len(sys.argv) > 4:
        dns_query_server = sys.argv[4]
    else:
        dns_query_server = None
    run_dig(hostname_filename, output_filename, dns_query_server)
elif function_name == "get_average_ttls":
    filename = sys.argv[2]
    get_average_ttls(filename)
