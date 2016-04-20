#!/usr/bin/python
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf

SWITCH_NUM = 10

def myNetwork():

	net = Mininet()

	info( '*** Adding controller\n' )
	c0 = net.addController(name='c0',controller=RemoteController,ip='127.0.0.1', port=6633)
	info( '*** Add switches\n')
	for i in xrange(1,SWITCH_NUM+1):
		eval('s'+str(i)+'= net.addSwitch(\'s'+str(i)'\', cls=OVSKernelSwitch)')
'''	info( '*** Add hosts\n')
	h1 = net.addHost('h1', cls=Host, mac='00:04:00:00:00:01', ip='10.0.0.1/32', defaultRoute='h1-eth0')
	h2 = net.addHost('h2', cls=Host, mac='00:04:00:00:00:02', ip='10.0.0.2/32', defaultRoute='h2-eth0')
	h3 = net.addHost('h3', cls=Host, mac='00:04:00:00:00:03', ip='10.0.0.3/32', defaultRoute='h3-eth0')
	h4 = net.addHost('h4', cls=Host, mac='00:04:00:00:00:04', ip='10.0.0.4/32', defaultRoute='h4-eth0')
	h5 = net.addHost('h5', cls=Host, mac='00:04:00:00:00:05', ip='10.0.0.5/32', defaultRoute='h5-eth0')
	h6 = net.addHost('h6', cls=Host, mac='00:04:00:00:00:06', ip='10.0.0.6/32', defaultRoute='h6-eth0')
	linkBW_1 = {'bw':10}
	linkBW_2 = {'bw':20}
	linkBW_3 = {'bw':30}
	linkBW_4 = {'bw':40}
	linkBW_5 = {'bw':100}
'''
	info( '*** Add links\n')
	for i in xrange(1,SWITCH_NUM):
		eval('net.addLink(s'+str(i)+', s'+str(i+1)+', ')
	net.addLink(s1, s3, cls=TCLink)
	print "\n"
	
	info( '*** Starting network\n')
	net.build()
	info( '*** Starting controllers\n')
	for controller in net.controllers:
		controller.start()

	info( '*** Starting switches\n')
	for i in xrange(1,SWITCH_NUM):
		print "Switch %d start" % i
		eval('net.get(\'s'+str(i)+'\').start([c0])')
	info( '*** Configuring switches\n')
	CLI(net)
	net.stop()

if __name__ == '__main__':
	setLogLevel( 'info' )
	myNetwork()
