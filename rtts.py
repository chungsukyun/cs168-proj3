import subprocess
import json
import sys

function_name = sys.argv[1]

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
    name = hostnames[0]
    ls_output = subprocess.check_output("ping -c " + num_packets + " " + name, shell = True).decode("utf-8")
    ls_output_lines = ls_output.splitlines()
    rtt_list = []
    i = 1
    while i < int(num_packets):
        line = ls_output_lines[i]
        line = line.split()
        ttl = float(line[7][5:])
        rtt_list += [ttl]
        i += 1
    print rtt_list

    # for name in hostnames:
    #     ls_output = subprocess.check_output("ping -c " + num_packets + " " + name, shell=True).decode("utf-8")
    #     print ls_output

elif function_name == "plot_median_rtt_cdf":
    pass
elif function_name == "plot_ping_cdf":
    pass
else:
    print "The function you have called does not exist."
