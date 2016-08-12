#!/usr/bin/python
from mininet.net import Mininet
from mininet.node import *
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import *
from mininet.util import *
from mininet.topo import *

import fnss
import networkx
import random 
import os.path
import sys

config_file = 'fat_tree_4'

def flow_entry_gen(SWITCH_NUM,ENTRY_FACTOR,tier_type,port_to_switch):	#port count = the port that each switch have
	#[3,2,4,2,1]	s1 has 3 ports, s2 has 2, and so on
	used = set() #(located_switch,match_field,match_value)
	tot_entry = 0
	global config_file

	if not os.path.isfile('config/'+config_file+'.entry'):	#generate flow entries if it doesn't exist
		print "pre-install entry config file doesn't exist, random generating..."	
		field_set = ['eth_dst','eth_src','ipv4_src','ipv4_dst','tcp_src','tcp_dst','udp_src','udp_dst','icmpv4_type','icmpv4_code']
		f = open('config/'+config_file+'.entry','w')
		for switch in port_to_switch:
			used_this_switch = set()
			if tier_type[switch-1] == 'core':
				FLOW_PER_SWITCH = ENTRY_FACTOR
			elif tier_type[switch-1] == 'aggregation':
				FLOW_PER_SWITCH = ENTRY_FACTOR
			elif tier_type[switch-1] == 'edge':
				FLOW_PER_SWITCH = ENTRY_FACTOR
			tot_entry += FLOW_PER_SWITCH
			ports = []
			
			for port in port_to_switch[switch]:
				dst_str = port_to_switch[switch][port]
				if dst_str[0] == 'h':
					dst_tier_type = 'leaf'
				else:
					dst_tier_type = tier_type[int(dst_str[1:])-1]
				ports.append(port)
				'''if config_file[:8] == 'two_tier':
					if tier_type[switch-1] == 'core' and dst_tier_type == 'edge':
						ports.append(port)
					elif tier_type[switch-1] == 'edge' and dst_tier_type == 'leaf':
						ports.append(port)
				else:
					if tier_type[switch-1] == 'core' and dst_tier_type == 'aggregation':
						ports.append(port)
					elif tier_type[switch-1] == 'aggregation' and dst_tier_type == 'edge':
						ports.append(port)
					elif tier_type[switch-1] == 'edge' and dst_tier_type == 'leaf':
						ports.append(port)
				'''
			a = 0
			while a < FLOW_PER_SWITCH:
				out_port = str(random.choice(ports))
				field = random.choice(field_set)
				dup = random.randint(0,5)	#=0 -> duplicate
				priority = str(random.randint(1,1000))
				if len(used) > FLOW_PER_SWITCH and dup == 0:
					on_switch, field, value = random.choice(list(used))
					while on_switch == switch or (field,value) in used_this_switch:
						on_switch, field, value = random.choice(list(used))
					used_this_switch.add((field,value))
					f.write(str(switch)+','+field+','+str(value)+','+out_port+','+priority+'\n')
					a += 1
					continue
				if field == 'eth_dst' or field == 'eth_src':
					value = hex(random.randint(1,0xff)).replace('0x','')
					for i in xrange(5):
						value += ':'+hex(random.randint(1,0xff)).replace('0x','')
				elif field == 'ipv4_src' or field == 'ipv4_dst':
					value = '192.168.56.'+str(random.randint(1,0xff))
				elif field == 'ipv6_src' or field == 'ipv6_dst':
					value = hex(random.randint(1,0xff))
					for i in xrange(7):
						value += ':'+hex(random.randint(1,0xffff))
				elif field == 'in_port':
					value = str(SWITCH_NUM)
					while value == out_port:	#in_port and out_port should be different to avoid infinity loop
						value = str(SWITCH_NUM)
				elif field == 'tcp_src' or field == 'tcp_dst': 
					b = random.randint(0,99)
					common_ports = [7,20,21,22,23,25,43,53,109,110,156,161,194,546,547]	#common port other than http and https
					if b < 50:	#http
						value = 80
					elif b < 75:	# https
						value = 443
					elif b < 90:	#other common
						value = random.choice([7,20,21,22,23,25,43,53,109,110,156,161,194,546,547])
					else:	#others
						value = 7
						while value in common_ports:
							value = random.randint(1,1024)
				elif field == 'udp_src' or field == 'udp_dst':
					value = random.randint(1,1024)
				else: #icmp code, value
					 value = random.randint(1,0xff)
				if (field,value) not in used_this_switch:	#prevent same match field with same value in same switch
					f.write(str(switch)+','+field+','+str(value)+','+out_port+','+priority+'\n')
					used_this_switch.add((field,value))
					used.add((switch,field,value))
					a += 1
				#target switch, match field, match value, output port~
			del used_this_switch
		f.close()
	else:
		print "pre-install entries file exist.."
	return tot_entry

def myNetwork():      
	content = config_file.split('_')
	if config_file[:8] == 'fat_tree':
		k = int(content[2])
		topo = fnss.fat_tree_topology(k)
		tl = 'layer'
	elif config_file[:8] == 'two_tier':
		core,edge = int(content[2]),int(content[3])
		topo = fnss.two_tier_topology(core,edge,1)
		tl = 'tier'
	elif config_file[:10] == 'three_tier':
		core,aggregation,edge = int(content[2]),int(content[3]),int(content[4])
		topo = fnss.three_tier_topology(core,aggregation,edge,1)
		tl = 'tier'

	node_type = networkx.get_node_attributes(topo,'type')
	SWITCH_NUM = 0
	for i in node_type:
		if node_type[i] == 'switch':
			SWITCH_NUM += 1
	
	tier_list = []
	#print topo.nodes('tier')
	for node in topo.nodes('tier'):
		tier_list.append(node[1][tl])
	ENTRY_FACTOR = 5000
	print 'switch count:%d, entry factor: %d' % (SWITCH_NUM,ENTRY_FACTOR)
	mn_topo = fnss.to_mininet(topo)
	#switch = partial(OVSSwitch,protocols='OpenFlow15')
	net = Mininet(topo=mn_topo,controller=RemoteController)#,switch=switch)
	net.start()
	port_to_switch = {} #destination of each switch, ex: dst_switch[0][2] = port 3 of s1
	for i in xrange(SWITCH_NUM):
		port_to_switch[i+1] = {}

	for link in net.topo.links():
		src_switch, dst_switch = link #might also be host
		src_port, dst_port = net.topo.port(src_switch,dst_switch)
		#print '%s port %d to %s port %d' % (src_switch,src_port,dst_switch,dst_port)
		if src_switch[0] != 'h':
			port_to_switch[int(src_switch[1:])][src_port] = dst_switch
		if dst_switch[0] != 'h':
			port_to_switch[int(dst_switch[1:])][dst_port] = src_switch
	
	if not os.path.isfile('config/'+config_file+'.port_to_switch'):
		f = open('config/'+config_file+'.port_to_switch','w')
		f.write(str(port_to_switch))
		f.close()
	TOTAL_ENTRY = flow_entry_gen(SWITCH_NUM,ENTRY_FACTOR, tier_list, port_to_switch)	
	if not os.path.isfile('config/'+config_file):
		print 'generating new config files....'
		f = open('config/'+config_file,'w')
		f.write('%d,%d,%d' % (SWITCH_NUM, ENTRY_FACTOR, TOTAL_ENTRY))
		f.close()
	CLI(net)
	net.stop()
	

if __name__ == '__main__':
	setLogLevel( 'info' )
	myNetwork()
