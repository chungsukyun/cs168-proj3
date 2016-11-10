import subprocess
import json
import sys
import numpy
import math
import time
import datetime

function_name = sys.argv[1]

def dot_count(string):
    i = 0
    count = 0
    while i < len(string):
        if string[i] == ".":
            count += 1
        i += 1
    return count

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
                    query_dict["Time in millis"] = int(query.splitlines()[-5].split()[3])
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
    root_list = []
    tld_list = []
    other_name_list = []
    terminating_list = []
    rl = 0
    tld = 0
    onl = 0
    tl = 0
    for dig in f_list:
        root_list_1 = []
        tld_list_1 = []
        other_name_list_1 = []
        terminating_list_1 = []
        for query in dig["Queries"]:
            root_list_2 = []
            tld_list_2 = []
            other_name_list_2 = []
            terminating_list_2 = []
            for answer in query["Answers"]:
                if answer["Type"] == "A" or answer["Type"] == "CNAME":
                    terminating_list_2 += [answer["TTL"]]
                if answer["Queried name"] == ".":
                    root_list_2 += [answer["TTL"]]
                elif dot_count(answer["Queried name"]) == 1:
                    tld_list_2 += [answer["TTL"]]
                elif answer["Type"] == "NS":
                    other_name_list_2 += [answer["TTL"]]
            rl2 = 0
            tld2 = 0
            onl2 = 0
            tl2 = 0
            if len(root_list_2) != 0:
                rld2 = numpy.mean(root_list_2)
                root_list_1 += [rld2]
            if len(tld_list_2) != 0:
                tld2 = numpy.mean(tld_list_2)
                tld_list_1 += [tld2]
            if len(other_name_list_2) != 0:
                onl2 = numpy.mean(other_name_list_2)
                other_name_list_1 += [onl2]
            if len(terminating_list_2) != 0:
                tl2 = numpy.mean(terminating_list_2)
                terminating_list_1 += [tl2]
        rl1 = 0
        tld1 = 0
        onl1 = 0
        tl1 = 0
        if len(root_list_1) != 0:
            rld1 = numpy.mean(root_list_1)
            root_list += [rld1]
        if len(tld_list_1) != 0:
            tld1 = numpy.mean(tld_list_1)
            tld_list += [tld1]
        if len(other_name_list_1) != 0:
            onl1 = numpy.mean(other_name_list_1)
            other_name_list += [onl1]
        if len(terminating_list_1) != 0:
            tl1 = numpy.mean(terminating_list_1)
            terminating_list += [tl1]
    if len(root_list) != 0:
        rld = numpy.mean(root_list)
    if len(tld_list) != 0:
        tld = numpy.mean(tld_list)
    if len(other_name_list) != 0:
        onl = numpy.mean(other_name_list)
    if len(terminating_list) != 0:
        tl = numpy.mean(terminating_list)
    return [rld, tld, onl, tl]

def get_average_times(filename):
    f = open(filename, "r")
    f_str = f.read()
    f_list = json.loads(f_str)
    whole_list = []
    terminating_list = []
    wl = 0
    tl = 0
    for dig in f_list:
        time = 0
        terminating_time = 0
        for query in dig["Queries"]:
            time += query["Time in millis"]
            for answer in query["Answers"]:
                if answer["Type"] == "A" or answer["Type"] == "CNAME":
                    terminating_time += query["Time in millis"]
        if time != 0:
            whole_list += [time]
        if terminating_time != 0:
            terminating_list += [terminating_time]
    if len(whole_list) != 0:
        wl = numpy.mean(whole_list)
    if len(terminating_list) != 0:
        tl = numpy.mean(terminating_list)
    print [wl, tl]
    return [wl, tl]


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
elif function_name == "get_average_times":
    filename = sys.argv[2]
    get_average_times(filename)