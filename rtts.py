import subprocess
import json
import sys
import numpy
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plot
from matplotlib.backends import backend_pdf

function_name = sys.argv[1]

def find_string(lst, s):
    i = 0
    while i < len(lst):
        e = lst[i]
        if e[:len(s)]==s:
            return e
        i += 1
    return ""

if function_name == "run_ping":
    hostnames = []
    hostname_file_name = sys.argv[2]
    hostname_file = open(hostname_file_name, 'r')
    line = hostname_file.readline().rstrip()
    while line != "":
        hostnames += [line]
        line = hostname_file.readline().rstrip()
    num_packets = str(int(sys.argv[3]) + 1)
    raw_ping_output_filename = sys.argv[4]
    aggregated_ping_output_filename = sys.argv[5]
    raw_ping_dict = {}
    aggregated_ping_dict = {}

    for name in hostnames:
        print name
        ls_output, err = subprocess.Popen(["ping", "-c", num_packets, name], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        ls_output_lines = ls_output.splitlines()
        rtt_list = []
        line_counter = 1
        packet_counter = 1
        drop_counter = 0
        while packet_counter < int(num_packets):
            line = ls_output_lines[line_counter]
            line = line.split()
            if find_string(line, "icmp_seq=")[9:] == "":
                rtt_list += [-1.000]
                drop_counter += 1
            elif int(find_string(line, "icmp_seq=")[9:]) != packet_counter:
                rtt_list += [-1.000]
                drop_counter += 1
            else:
                rtt = float(find_string(line, "time=")[5:])
                rtt_list += [rtt]
                line_counter += 1
            packet_counter += 1
        raw_ping_dict[name] = rtt_list
        drop_rate = float(float(drop_counter)/float(int(num_packets)-1))
        filtered = filter(lambda a: a != -1.000, rtt_list)
        median_rtt = -1.000
        max_rtt = -1.000
        if len(filtered) != 0:
            median_rtt = round(numpy.median(filtered), int(3 - math.ceil(math.log10(abs(numpy.median(filtered))))))
            max_rtt = round(numpy.amax(filtered), int(3 - math.ceil(math.log10(abs(numpy.amax(filtered))))))
        aggregated_ping_dict[name] = {"drop_rate": drop_rate, "max_rtt": max_rtt, "median_rtt": median_rtt}

    with open(raw_ping_output_filename, "w") as fp:
        json.dump(raw_ping_dict, fp)
    with open(aggregated_ping_output_filename, "w") as fp:
        json.dump(aggregated_ping_dict, fp)

elif function_name == "plot_median_rtt_cdf":
    agg_ping_results_filename = sys.argv[2]
    output_cdf_filename = sys.argv[3]
    json_file = open(agg_ping_results_filename)
    json_str = json_file.read()
    aggregated_ping_dict = json.loads(json_str)
    median_rtt_list = []
    for key in aggregated_ping_dict.keys():
        if aggregated_ping_dict[key]["median_rtt"] != -1.000:
            median_rtt_list += [aggregated_ping_dict[key]["median_rtt"]]
    median_rtt_list.sort()
    y_list = range(1, len(median_rtt_list) + 1)
    for i in range(len(median_rtt_list)):
        y_list[i] = float(y_list[i])/float(len(median_rtt_list))
    plot.plot(median_rtt_list, y_list, label="median rtt cdf")
    plot.legend()
    plot.grid()
    plot.xlabel("Median RTT")
    plot.ylabel("Cumulative Fraction of Websites")
    with backend_pdf.PdfPages(output_cdf_filename) as pdf:
        pdf.savefig()

elif function_name == "plot_ping_cdf":
    raw_ping_results_filename = sys.argv[2]
    output_cdf_filename = sys.argv[3]
    json_file = open(raw_ping_results_filename)
    json_str = json_file.read()
    raw_ping_dict = json.loads(json_str)
    for key in raw_ping_dict.keys():
        rtt_list = raw_ping_dict[key]
        rtt_list.sort()
        y_list = range(1, len(rtt_list) + 1)
        for i in range(len(rtt_list)):
            y_list[i] = float(y_list[i])/float(len(rtt_list))
        plot.plot(rtt_list, y_list, label=key)
    plot.legend()
    plot.grid()
    plot.xlabel("RTT")
    plot.ylabel("Cumulative Fraction of RTTs")
    with backend_pdf.PdfPages(output_cdf_filename) as pdf:
        pdf.savefig()

else:
    print "The function you have called does not exist."
