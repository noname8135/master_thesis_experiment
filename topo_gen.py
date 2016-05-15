#!/usr/bin/python
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
import random 
import os.path

SWITCH_NUM = 5
entry_num_each_switch = 5

def flow_entry_gen(port_count):	#port count = the port that each switch have
	#[3,2,4,2,1]	s1 has 3 ports, s2 has 2, and so on
	# match = parser.OFPMatch(eth_type = 0x806)
	global SWITCH_NUM
	global entry_num_each_switch
	if not os.path.isfile('proactive_flow_entry.txt'):	#generate flow entries if it doesn't exist
		print "pre-install entry config file doesn't exist, random generating..."	
		field_set = ['in_port','vlan_vid','eth_dst','eth_src','ipv4_src','ipv4_dst',
		'ipv6_src','ipv6_dst','tcp_src','tcp_dst','udp_src','udp_dst','icmpv4_type','icmpv4_code',
		'icmpv6_type','icmpv6_code']

		f = open('proactive_flow_entry.txt','w')
		for switch in xrange(1,SWITCH_NUM+1):
			used = set()
			for datapath in xrange(entry_num_each_switch):
				out_port = str(random.randint(1,port_count[SWITCH_NUM-1]))
				field = random.choice(field_set)
				if field == 'eth_dst' or field == 'eth_src':
					value = hex(random.randint(0,0xff))
					for i in xrange(5):
						value += ':'+hex(random.randint(0,0xff))
				elif field == 'ipv4_src' or field == 'ipv4_dst':
					value = str(random.randint(0,0xff))
					for i in xrange(3):
						value += '.'+str(random.randint(0,255))
				elif field == 'ipv6_src' or field == 'ipv6_dst':
					value = hex(random.randint(0,0xff))
					for i in xrange(7):
						value += ':'+hex(random.randint(0,0xffff))
				elif field == 'in_port':
					value = str(SWITCH_NUM)
					while value == out_port:	#in_port and out_port should be different
						value = str(SWITCH_NUM)
				else:	
					if field == 'vlan_vid':
						value_range = 0x1fff
					elif field == 'tcp_src' or field == 'tcp_dst' or field == 'udp_src' or field == 'udp_dst':
						value_range = 0xffff
					else: #icmp code, value
					 	value_range = 0xff
					value = str(random.randint(0,value_range))
				value = value.replace('0x','')
				#print '===>'+str(switch)+','+field+','+value+','+out_port+'\n'
				if field+value not in used:
					f.write(str(switch)+','+field+','+value+','+out_port+'\n')
					used.add(field+value)
				#target switch, match field, match value, output port~
			del used
		f.close()
	else:
		print "Reading pre-install entry config file proactive_flow_entry.."

def myNetwork():      
	global SWITCH_NUM
	net = Mininet()
	info( '*** Adding controller\n' )
	c0 = net.addController(name='c0',controller=RemoteController,ip='127.0.0.1', port=6633)
	info( '*** Add switches\n')
	for i in xrange(1,SWITCH_NUM+1):
		exec('s'+str(i)+' = net.addSwitch(\'s'+str(i)+'\',cls=OVSKernelSwitch)')
 
	info( '*** Add links\n')
	net.addLink(s1,s2)
	net.addLink(s1,s4)
	net.addLink(s2,s3)
	net.addLink(s2,s4)
	net.addLink(s2,s5)
	net.addLink(s3,s5)
	net.addLink(s4,s5)
	dst_switch = [[2,4],[1,3,4,5],[2,5],[1,2,5],[2,3,4]]
	print "\n"
	port_count = [2,4,2,3,3]	
	flow_entry_gen(port_count)	#write to file

	info( '*** Starting network\n')
	net.build()
	info( '*** Starting controllers\n')
	for controller in net.controllers:
		controller.start()

	info( '*** Starting switches\n')
	for i in xrange(1,SWITCH_NUM+1):
		print "Switch %d start" % i
		exec('net.get(\'s'+str(i)+'\').start([c0])')
	info( '*** Configuring switches\n')
	CLI(net)
	net.stop()

if __name__ == '__main__':
	setLogLevel( 'info' )
	myNetwork()
