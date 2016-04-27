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

SWITCH_NUM = 5

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
	print "\n"
	
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
