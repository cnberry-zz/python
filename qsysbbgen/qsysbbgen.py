from sys import argv
import re
import os
import argparse
import shutil

#-----------------------------------------------------------------
#			main function
#-----------------------------------------------------------------
def main():
	# parser for input args and help
	parser = argparse.ArgumentParser(description="Create Synopsys blackbox modules for Intel Qsys IP")
	parser.add_argument("ip",help="qsys ip file to convert (*.ip)")
	parser.add_argument("-o","--output",help="output file to write to (default is stdout)")
	parser.add_argument("-q","--qsys_procs",help="absolute path to qsys_procs.tcl (default assumes local dir)")
	parser.add_argument("-v","--verbose",action="store_true",help="print out verbose messages (default off)")
	parser.add_argument("-c","--clean",action="store_true",help="remove work and output file before begining (default off)")
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
		qsysProcs =	os.path.abspath("qsys_procs.tcl")
	
	# clean dirs before making them
	if args.clean:
		if os.path.exists("work"):
			shutil.rmtree("work")
		if os.path.exists(args.output):
			os.remove(args.output)

	# get absoulte path for outputfile
	if args.output:
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
		print("output = {}".format(outputfile if args.output else "stdout"))
		print("basename = {}".format(baseName))

	
	# create qsys.tcl file
	with open("{}.tcl".format(baseName),"wt") as f:
		print("source \"{}\"".format(qsysProcs),file=f)	
		print("\n")
		print("set ip \"{}\"".format(qsysIp),file=f)	
		print("set ipParams [do_load_ip $ip]",file=f)
		print("set name [do_get_ip_name]",file=f)
		print("set defaultParams [do_create_default_ip $name]",file=f)
		print("do_create_params_file \"{0}_params.txt\" $defaultParams $ipParams $name".format(baseName),file=f)

	# call qsys-script
	cmd = "{} --new-quartus-project={} --script={}.tcl".format(qsysScript,baseName,baseName)
	os.system(cmd)

	# call qsys-generate
	cmd = "{} {} --quartus-project={} --synthesis=VERILOG".format(qsysGen,qsysIp,baseName)
	os.system(cmd)

	# read in *_bb.v and *_params.txt and merge them
	with open(outputfile,"a") as fout:
		with open("{}_params.txt".format(baseName),"rt") as fin:
			line = fin.readline().rstrip('\n')
			print("(* syn_haps_qsys_instance_name = \"{}\" *)".format(line),file=fout)	
			print("module {}".format(baseName),file=fout)
			print("\t#(",file=fout)
			
			lines = fin.read().splitlines();
			for line in lines[:-1]:
				print("\t\tparameter {},".format(line),file=fout)
			print("\t\tparameter {}".format(lines[-1]),file=fout)
				
			#line = fin.readline().rstrip('\n')
			#while line:
			#	print("\t\tparameter {},".format(line),file=fout)
			#	line = fin.readline().rstrip('\n')

			print("\t)(",file=fout)
		with open("{}/{}_bb.v".format(baseName,baseName),"rt") as fin:
			line = fin.readline().rstrip('\n') 
			line = fin.readline().rstrip('\n')
			while line:
				print("{}".format(line),file=fout)
				line = fin.readline().rstrip('\n')
		print("\n",file=fout)

if __name__ == "__main__":
	main()
