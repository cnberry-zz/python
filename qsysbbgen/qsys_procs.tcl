package require -exact qsys 17.0

proc do_create_default_ip {ip_name} {

	set ret []
	create_system default_ip
	add_instance X $ip_name
	sync_sysinfo_parameters

	set params [get_instance_parameters X]
	foreach param $params {
	set value [get_instance_parameter_value X $param]
		lappend ret "qsys_parameter_$param=\"$value\""
	}

	return $ret
}

# load existing ip and get params and CLASS_NAME
proc do_load_ip {ip} {
	load_system $ip

	set ret []
	set inst [get_instances]
	set params [get_instance_parameters $inst]

	foreach param $params {
		set value [get_instance_parameter_value $inst $param]
		lappend ret "qsys_parameter_$param=\"$value\""
	}

	return $ret
}

proc do_get_ip_name {} {

	set inst [get_instances]
	return [get_instance_property $inst "CLASS_NAME"]

}

# create a non-default param file
proc do_create_params_file {fileName defaults current name} {

set outfile [open $fileName w]
puts $outfile $name
foreach defaultParam $defaults ipParam $current {
	if { $ipParam == $defaultParam } {
		#puts "DEFAULT: $ipParam"
	} else {
		puts $outfile "$ipParam"
	}
}
close $outfile

}
