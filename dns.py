import subprocess
import json
import sys
import numpy
import math
import time
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plot
from matplotlib.backends import backend_pdf
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
                    print query
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
                    test_name = answer["Queried name"]
                    if test_name[len(test_name)-1] == ".":
                        test_name = test_name[:len(test_name)-1]
                    if dig["Name"] == test_name:
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
                    test_name = answer["Queried name"]
                    if test_name[len(test_name)-1] == ".":
                        test_name = test_name[:len(test_name)-1]
                    if dig["Name"] == test_name:
                        terminating_time += query["Time in millis"]
        if time != 0:
            whole_list += [time]
        if terminating_time != 0:
            terminating_list += [terminating_time]
    if len(whole_list) != 0:
        wl = numpy.mean(whole_list)
    if len(terminating_list) != 0:
        tl = numpy.mean(terminating_list)
    return [wl, tl]

def generate_time_cdfs(json_filename, output_filename):
    f = open(json_filename)
    f_str = f.read()
    f_list = json.loads(f_str)
    whole_list = []
    terminating_list = []
    for dig in f_list:
        time = 0
        terminating_time = 0
        for query in dig["Queries"]:
            time += query["Time in millis"]
            for answer in query["Answers"]:
                if answer["Type"] == "A" or answer["Type"] == "CNAME":
                    test_name = answer["Queried name"]
                    if test_name[len(test_name)-1] == ".":
                        test_name = test_name[:len(test_name)-1]
                    if dig["Name"] == test_name:
                        terminating_time += query["Time in millis"]
        if time != 0:
            whole_list += [time]
        if terminating_time != 0:
            terminating_list += [terminating_time]
    whole_list.sort()
    terminating_list.sort()
    y_list1 = range(1, len(whole_list) + 1)
    y_list2 = range(1, len(terminating_list) + 1)
    for i in range(len(whole_list)):
        y_list1[i] = float(y_list1[i])/float(len(whole_list))
    for i in range(len(terminating_list)):
        y_list2[i] = float(y_list2[i])/float(len(terminating_list))
    plot.plot(whole_list, y_list1, label="total time cdf")
    plot.plot(terminating_list, y_list2, label="final request time cdf")
    plot.xscale("log")
    plot.legend()
    plot.grid()
    plot.xlabel("time in millis")
    plot.ylabel("cumulative fraction of successful dig calls")
    with backend_pdf.PdfPages(output_filename) as pdf:
        pdf.savefig()

def count_different_dns_responses(filename1, filename2):
    f1 = open(filename1, "r")
    f2 = open(filename2, "r")
    f1_str = f1.read()
    f2_str = f2.read()
    f1_list = json.loads(f1_str)
    f2_list = json.loads(f2_str)
    f1_dict = {}
    f2_dict = {}
    f1_diff = 0
    whole_diff = 0
    for dig in f1_list:
        for query in dig["Queries"]:
            query_set = set()
            for answer in query["Answers"]:
                if answer["Type"] == "A" or answer["Type"] == "CNAME":
                    test_name = answer["Queried name"]
                    if test_name[len(test_name)-1] == ".":
                        test_name = test_name[:len(test_name)-1]
                    if dig["Name"] == test_name:
                        query_set.add(answer["Data"])
            if len(query_set) != 0:
                if dig["Name"] not in f1_dict.keys():
                    f1_dict[dig["Name"]] = [query_set]
                else:
                    f1_dict[dig["Name"]] += [query_set]
    for dig in f2_list:
        for query in dig["Queries"]:
            query_set = set()
            for answer in query["Answers"]:
                if answer["Type"] == "A" or answer["Type"] == "CNAME":
                    test_name = answer["Queried name"]
                    if test_name[len(test_name)-1] == ".":
                        test_name = test_name[:len(test_name)-1]
                    if dig["Name"] == test_name:
                        query_set.add(answer["Data"])
            if len(query_set) != 0:
                if dig["Name"] not in f2_dict.keys():
                    f2_dict[dig["Name"]] = [query_set]
                else:
                    f2_dict[dig["Name"]] += [query_set]
    for hostname in f1_dict:
        counter = set()
        for s in f1_dict[hostname]:
            counter.add(frozenset(s))
        if len(counter) > 1:
            f1_diff += 1
    whole_dict = f1_dict.copy()
    for hostname in f2_dict:
        if hostname not in whole_dict.keys():
            whole_dict[hostname] = f2_dict[hostname]
        else:
            whole_dict[hostname] += f2_dict[hostname]
    for hostname in whole_dict:
        counter = set()
        for s in whole_dict[hostname]:
            counter.add(frozenset(s))
        if len(counter) > 1:
            whole_diff += 1
    print [f1_diff, whole_diff]
    return [f1_diff, whole_diff]



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
elif function_name == "generate_time_cdfs":
    json_filename = sys.argv[2]
    output_filename = sys.argv[3]
    generate_time_cdfs(json_filename, output_filename)
elif function_name == "count_different_dns_responses":
    filename1 = sys.argv[2]
    filename2 = sys.argv[3]
    count_different_dns_responses(filename1, filename2)