import subprocess
import json
import sys
import numpy

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
        ls_output, err = subprocess.Popen(["ping", "-c", num_packets, name], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        # ls_output = subprocess.check_output("ping -c " + num_packets + " " + name, shell=True).decode("utf-8")
        ls_output_lines = ls_output.splitlines()
        rtt_list = []
        line_counter = 1
        packet_counter = 1
        drop_counter = 0
        while packet_counter < int(num_packets):
            line = ls_output_lines[line_counter]
            line = line.split()
            if find_string(line, "icmp_seq=")[9:] == "":
                rtt_list += [-1.0]
                drop_counter += 1
            elif int(find_string(line, "icmp_seq=")[9:]) != packet_counter:
                rtt_list += [-1.0]
                drop_counter += 1
            else:
                rtt = float(find_string(line, "time=")[5:])
                rtt_list += [rtt]
                line_counter += 1
            packet_counter += 1
        raw_ping_dict[name] = rtt_list
        drop_rate = float(float(drop_counter)/float(int(num_packets)-1))
        filtered = filter(lambda a: a != -1.0, rtt_list)
        median_rtt = -1.0
        max_rtt = -1.0
        if len(filtered) != 0:
            median_rtt = numpy.median(filtered)
            max_rtt = numpy.amax(filtered)
        aggregated_ping_dict[name] = {"drop_rate": drop_rate, "max_rtt": max_rtt, "median_rtt": median_rtt}
        print raw_ping_dict[name]
        print aggregated_ping_dict[name]

elif function_name == "plot_median_rtt_cdf":
    pass
elif function_name == "plot_ping_cdf":
    pass
else:
    print "The function you have called does not exist."
