#!/depot/Python-3.6.2/bin/python
from sys import argv
import re
import os
import argparse
import shutil

#-----------------------------------------------------------------
#			helper functions
#-----------------------------------------------------------------
def generate_all_params(ip,verbose):
	rParam = r"set_instance_parameter_value.*{(.*)} {(.*)}" 
	rIp = r"add_instance (\w+) (\w+) (\d+)" 
	params = []
	with open(ip,"rt") as fin:
			line = fin.readline()
			while line:
				if re.search(rParam,line):
					match = re.search(rParam,line)
					params.append("qsys_parameter_{} = \"{}\"".format(match.group(1),match.group(2)))
				if re.search(rIp,line):
					match = re.search(rIp,line)
					params.insert(0,"{}".format(match.group(2)))
					if verbose: print("Found instance {} {}".format(match.group(2),match.group(3)))
				line = fin.readline()

	return params

def generate_non_default_params(ip1,ip2,verbose):
	rParam = r"set_instance_parameter_value.*{(.*)} {(.*)}" 
	rIp = r"add_instance (\w+) (\w+) (\d+)" 
	ip1_params = {}
	ip2_params = {}
	params = []
	with open(ip1,"rt") as fin:
			line = fin.readline()
			while line:
				if re.search(rParam,line):
					match = re.search(rParam,line)
					ip1_params["qsys_parameter_{}".format(match.group(1))] = "{}".format(match.group(2))
				if re.search(rIp,line):
					match = re.search(rIp,line)
					params.insert(0,"{}".format(match.group(2)))
					if verbose: print("Found instance {} {}".format(match.group(2),match.group(3)))
				line = fin.readline()

	with open(ip2,"rt") as fin:
			line = fin.readline()
			while line:
				if re.search(rParam,line):
					match = re.search(rParam,line)
					ip2_params["qsys_parameter_{}".format(match.group(1))] = "{}".format(match.group(2))
				line = fin.readline()

	for key in ip1_params:
		if key in ip2_params:	
			if ip1_params[key] == ip2_params[key]:
				if verbose: print("Ignoring param {} with default {}".format(key,ip1_params[key]))
			else:
				params.append("{}=\"{}\"".format(key,ip1_params[key]))
		else:
			if verbose: print("Param {} default does not exists. Adding explicitly".format(key))
			params.append("{}=\"{}\"".format(key,ip1_params[key]))

	return params

def write_bb_to_file(outFileName,ipName,params):
	with open(outFileName,"a") as fout:
		print("(* syn_haps_qsys_instance_name = \"{}\" *)".format(params[0]),file=fout)	
		print("module {} #".format(ipName),file=fout)
		print("\t(",file=fout)
			
		for param in params[1:-1]:
			print("\t\tparameter {},".format(param),file=fout)
		print("\t\tparameter {}".format(params[-1]),file=fout)
		print("\t)(",file=fout)

		with open("{}/{}_bb.v".format(ipName,ipName),"rt") as fin:
			line = fin.readline().rstrip('\n') 
			line = fin.readline().rstrip('\n')
			while line:
				print("{}".format(line),file=fout)
				line = fin.readline().rstrip('\n')
		print("\n",file=fout)

#-----------------------------------------------------------------
#			main function
#-----------------------------------------------------------------
def main():
	# parser for input args and help
	parser = argparse.ArgumentParser(prog='qsysbbgen',description="Create Synopsys blackbox modules for Intel Qsys IP")
	parser.add_argument("ip",help="qsys ip file to convert (*.ip)")
	parser.add_argument("-o","--output",default="qsys_bb_lib.v",help="output file to write verilog bb to (default: \"qsys_bb_lib.v\")")
	parser.add_argument("-q","--qsys_procs",help="absolute path to qsys_procs.tcl (default: use qsys_proc local to qsysbbgen.py)")
	parser.add_argument("-v","--verbose",default=False,action="store_true",help="print out verbose messages (default: False)")
	parser.add_argument("-c","--clean",default=False,action="store_true",help="remove work and output file before begining (default: False)")
	parser.add_argument("-d","--default",default=False,action="store_true",help="include all gui parameters in bb output (default: False)")
	parser.add_argument('--version',action='version',version='%(prog)s 0.1')
	args = parser.parse_args()

	# setup qsys-script and qsys-generate
	if os.environ['QUARTUS_ROOTDIR']:
		qsysScript = "{}/sopc_builder/bin/qsys-script".format(os.environ['QUARTUS_ROOTDIR'])
		qsysGen = "{}/sopc_builder/bin/qsys-generate".format(os.environ['QUARTUS_ROOTDIR'])
	else:
		print("Error: environment variable $QUARTUS_ROOTDIR must be set")
		return

	# get absolute path for qsys_procs.tcl
	if args.qsys_procs:
		qsysProcs =	args.qsys_procs
	else:
		dir_path = os.path.dirname(os.path.realpath(__file__))
		qsysProcs =	"{}/qsys_procs.tcl".format(dir_path)

	if not os.path.exists(qsysProcs):
		print("Error: qsys_procs file: {} does not exist, please provide a valid path for this file".format(qsysProcs)) 
	
	# clean dirs before making them
	if args.clean:
		if os.path.exists("work"):
			shutil.rmtree("work")
		if os.path.exists(args.output):
			os.remove(args.output)

	# get absoulte path for outputfile
	outputfile = os.path.abspath(args.output);

	# create work dir and move into it
	if not os.path.exists("work"):
		os.makedirs("work")
	os.chdir("work");

# per ip operations---------

	# copy ip and get basename
	shutil.copyfile("../{}".format(args.ip),args.ip)
	baseName = os.path.splitext(args.ip)[0]
	qsysIp = args.ip

	# print out setup this run is using
	if args.verbose:
		print("qsys_ip = {}".format(qsysIp))
		print("qsys_procs = {}".format(qsysProcs))
		print("qsys-script = {}".format(qsysScript))
		print("qsys-generate = {}".format(qsysGen))
		print("output = {}".format(outputfile))
		print("basename = {}".format(baseName))

	# create qsys.tcl file
	with open("{}_gen.tcl".format(baseName),"wt") as f:
		print("source \"{}\"".format(qsysProcs),file=f)	
		print("\n")
		print("do_load_ip {}".format(qsysIp),file=f)
		print("set name [do_get_ip_name]",file=f)
		print("do_create_and_save_default_ip {}_default.ip $name".format(baseName),file=f)

	# call qsys-script
	cmd = "{} --new-quartus-project={} --script={}_gen.tcl".format(qsysScript,baseName,baseName)
	os.system(cmd)

	# call qsys-generate
	cmd = "{} {} --quartus-project={} --export-qsys-script".format(qsysGen,qsysIp,baseName)
	os.system(cmd)
	cmd = "{} {}_default.ip --quartus-project={} --export-qsys-script".format(qsysGen,baseName,baseName)
	os.system(cmd)
	cmd = "{} {} --quartus-project={} --synthesis=VERILOG".format(qsysGen,qsysIp,baseName)
	os.system(cmd)

	# generate params array
	if args.default:
		params = generate_all_params("{}.tcl".format(baseName),args.verbose)
	else:
		params = generate_non_default_params("{}.tcl".format(baseName),"{}_default.tcl".format(baseName),args.verbose)

	# read in *_bb.v and params and merge them
	write_bb_to_file(outputfile,baseName,params)

if __name__ == "__main__":
	main()
