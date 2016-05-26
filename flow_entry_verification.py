from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import *
from ryu.ofproto import ofproto_v1_3
from ryu.lib.mac import haddr_to_bin 
from ryu.lib.packet import *
import sys
import ryu
import json
import topo_gen
import array
import time
#from pprint import pprint


f = open('config/'+topo_gen.config_file,'r')
content = f.read().split(',')
f.close()
SWITCH_NUM = int(content[0])

class flow_entry_verification(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    def __init__(self, *args, **kwargs):
        super(flow_entry_verification, self).__init__(*args, **kwargs)
        self.switch_counter = 0
        self.switch_info = {}   #switch_info[datapath_id] = datapath object
        self.graph = {} #format: graph[switch] = [ (entry1 => match_field, value, destination_switch) (entry2) (entry3) ... ]
        global SWITCH_NUM
        self.entry_count = {}   #number of entry on every switch
        for i in xrange(1,SWITCH_NUM+1):
            self.graph[i] = set()
        self.switch_priority = {} #maintain according to the time that each switch is used as destination dynamically, the less the more prior  
    
    def add_flow(self, datapath, match, out_port, cookie_counter=0, buffer_id=None, priority=3):   #only action with output
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        actions = [parser.OFPActionOutput(out_port)]  #port for destination switch
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
        mod = parser.OFPFlowMod(datapath=datapath, cookie=cookie_counter, priority=priority, match=match, instructions=inst)    #Modify flow table
        datapath.send_msg(mod)

    def send_packet_out(self, datapath, in_port, data):    #forge a packet and send packet_out
        ofp = datapath.ofproto
        parser = datapath.ofproto_parser
        actions = [datapath.ofproto_parser.OFPActionOutput(ofp.OFPP_TABLE)] 
        print "sending PACKET_OUT to port %d of s%d with data %s" % (in_port, datapath.id, data)
        req = parser.OFPPacketOut(datapath=datapath, buffer_id=ofp.OFP_NO_BUFFER, in_port=ofp.OFPP_CONTROLLER, actions=actions, data=data)
        datapath.send_msg(req)

    def read_flow_entry(self):  #read from a file generated by topology.py
        global SWITCH_NUM
        f = open('config/'+topo_gen.config_file+'.port_to_switch','r')
        dst_switch = eval(f.read())
        f.close()
        cookie_counter = 1
        for i in xrange(1,SWITCH_NUM+1):
            self.switch_priority[i] = 0
            self.entry_count[i] = 0
        with open('config/'+topo_gen.config_file+'.entry','r') as f:
            for line in f:
                switch, match_field, match_value, out_port = line.rstrip().split(',')
                switch, out_port = int(switch), int(out_port)
                #print switch, match_field, match_value, out_port
                exec_str = 'match = self.switch_info[switch].ofproto_parser.OFPMatch('   #string to be executed
                if match_field[:4] == 'ipv4': 
                    exec_str += 'eth_type=0x0800, %s=\'%s\')' % (match_field, match_value)
                elif match_field[:4] == 'ipv6':
                    exec_str += 'eth_type=0x86DD, %s=\'%s\')' % (match_field, match_value)
                elif match_field[:3] == 'tcp':
                    exec_str += 'eth_type=0x0800, ip_proto=0x6, %s=%s)' % (match_field, match_value)
                elif match_field[:3] == 'udp':
                    exec_str += 'eth_type=0x0800, ip_proto=0x11, %s=%s)' % (match_field, match_value)
                elif match_field[:6] == 'icmpv4':
                    exec_str += 'eth_type=0x0800, ip_proto=0x1, %s=%s)' % (match_field, match_value)
                elif match_field[:6] == 'icmpv6':
                    exec_str += 'eth_type=0x86DD, ip_proto=0x3a, %s=%s)' % (match_field, match_value)
                elif match_field[:3] == 'eth':
                    exec_str += '%s=\'%s\')' % (match_field, match_value)
                else:
                    exec_str += '%s=%s)' % (match_field, match_value)
                exec(exec_str)
                self.add_flow(self.switch_info[switch], match, out_port, cookie_counter=cookie_counter)    #install new flow entry
                self.graph[switch].add((match_field,match_value,dst_switch[switch][out_port-1],cookie_counter))
                self.entry_count[switch] += 1
                self.switch_priority[dst_switch[switch][out_port-1]] += 1
                cookie_counter += 1
        '''
            match = parser.OFPMatch(eth_type = 0x0800, ipv4_src='140.123.103.188')  #ip
            match = parser.OFPMatch(eth_type = 0x0800, ip_proto=0x6, tcp_src=1234)    #tcp
            match = parser.OFPMatch(eth_type = 0x0800, ip_proto=0x11, udp_src=1234) #udp
            match = parser.OFPMatch(eth_type = 0x86DD, ip_proto=0x6, ipv6_src="2607:f0d0:1002:0051:0000:0000:0000:0004", tcp_src=1234)    #ip_v6 with tcp
            match = parser.OFPMatch(eth_type = 0x86DD, ip_proto=0x6, ipv6_src="2607:f0d0:1002:0051:0000:0000:0000:0004", tcp_src=1234, eth_src='0a:00:27:00:00:00')   #eth_src dst can fit in all
            match = parser.OFPMatch(eth_type = 0x0800, ip_proto=0x11, udp_src=1234, vlan_vid=0x1fff)    # vlan, max value here
            match = parser.OFPMatch(eth_type = 0x0800, ip_proto=0x1, icmpv4_type=10,icmpv4_code=1)
            match = parser.OFPMatch(eth_type = 0x0800, ip_proto=0x3a, icmpv6_code=1)
            icmp type, code => 8bits
        '''

    def find_aggregate_groups(self):
        global SWITCH_NUM
        visited_switch = set()  #used for all aggregate group
        visited_entry = set()   #refreshed for per aggregate group
        starting_switch = min([i for i in xrange(1,SWITCH_NUM+1) if self.switch_priority[i] != 0],key=lambda x:self.switch_priority[i])
        print "new group starting with s%d" % starting_switch
        self.find_one_group(starting_switch,{},visited_switch)

    def find_one_group(self, switch, pkt):    #get a flow entry that fit in the group
        #find
        most_prior_entry, min_priority = None, 99999999999
        for entry in self.graph[switch]:
            match_field, value, dst_switch, cookie = entry
            if self.entry_count[dst_switch] == 0:   #don't select the switch that has no more unvisited flow entry 
                continue
            if match_value not in packet or packet[match_field] == match_value: #this entry fit in the group!
                if self.switch_priority[dst_switch] < min_priority:
                    min_priority = self.switch_priority[dst_switch]
                    most_prior_entry = entry
        if most_prior_entry:
            self.visited_entry[prior_entry] = True
            match_field, value, dst_switch, cookie = most_prior_entry
            pkt[match_field] = value
            return find_one_group(dst_switch, pkt)
        return pkt
        
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        msg = ev.msg
        parser = datapath.ofproto_parser
        
        #table-miss
        match=parser.OFPMatch()
        self.add_flow(datapath,match,datapath.ofproto.OFPP_CONTROLLER,priority=0)   
        
        self.switch_info[datapath.id] = datapath #save datapath object of every switch
        self.switch_counter += 1
        global SWITCH_NUM
        if self.switch_counter == SWITCH_NUM:    #all switch ready
            self.read_flow_entry()  #read proactive installed entries

            #self.find_aggregate_groups()
            #pprint(self.graph)
        #actions = [parser.OFPActionOutput(ofproto.OFPP_TABLE)]  #packet out to first table

    def get_pkt_proto(self,field_type):
        '''
        field_set = ['vlan_vid','eth_dst','eth_src','ipv4_src','ipv4_dst',
        'ipv6_src','ipv6_dst','tcp_src','tcp_dst','udp_src','udp_dst','icmpv4_type','icmpv4_code',
        'icmpv6_type','icmpv6_code']
        
        if field_type == 'vlan_vid':
        elif field_type[] == '':
        elif field_type == '':
        elif field_type == '':
        elif field_type == '':
        elif field_type == '':
        '''
        pass

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def check_packet_back(self, ev):    #check if packets come back as expected
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto
        pkt = packet.Packet(array.array('B', ev.msg.data))

        if msg.reason == ofp.OFPR_NO_MATCH:
            reason = 'NO MATCH'
        elif msg.reason == ofp.OFPR_ACTION:
            reason = 'ACTION'
        elif msg.reason == ofp.OFPR_INVALID_TTL:
            reason = 'INVALID TTL'
        else:
            reason = 'unknown'
        print '************************'
        print 'OFPPacketIn received from s%d: buffer_id=%x total_len=%d reason=%s table_id=%d cookie=%d match=%s data=%s' % (dp.id, msg.buffer_id, msg.total_len, reason, msg.table_id, msg.cookie, msg.match, msg.data)
        for p in pkt.protocols: #print receiving packet
            print p
        print '________________________'

    def packout_test(self):
        pkt = packet.Packet()
        cond = ethernet.ethernet(src='aa:bb:dd:cc:ee:ff',dst='00:00:00:00:00:00')
        pkt.add_protocol(cond)
        cond = ipv4.ipv4(src='140.123.103.188',dst='147.187.218.231',proto=0x11)
        pkt.add_protocol(cond)
        cond = udp.udp(src_port=0,dst_port=5949)
        pkt.add_protocol(cond)
        print pkt
        pkt.serialize()
        time.sleep(1)
        self.send_packet_out(self.switch_info[1],1, pkt.data)
'''
show detail info in json
#self.logger.info('%s',json.dumps(msg.to_jsondict(), ensure_ascii=True, indent=3, sort_keys=True))

Packet_Out reference
#OFPP_TABLE -> send to first flow table.
#OFPP_ALL Forwarded to all physical ports except receiving ports
#OFPP_CONTROLLER -> send to controller

packet generating reference:
 def _handle_icmp(self, datapath, port, pkt_ethernet, pkt_ipv4, pkt_icmp):
        if pkt_icmp.type != icmp.ICMP_ECHO_REQUEST:
            return
        pkt = packet.Packet()
        pkt.add_protocol(ethernet.ethernet(ethertype=pkt_ethernet.ethertype,
                                           dst=pkt_ethernet.src,
                                           src=self.hw_addr))
        pkt.add_protocol(ipv4.ipv4(dst=pkt_ipv4.src,
                                   src=self.ip_addr,
                                   proto=pkt_ipv4.proto))
        pkt.add_protocol(icmp.icmp(type_=icmp.ICMP_ECHO_REPLY,
                                   code=icmp.ICMP_ECHO_REPLY_CODE,
                                   csum=0,
                                   data=pkt_icmp.data))
        self._send_packet(datapath, port, pkt)

    def _send_packet(self, datapath, port, pkt):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        pkt.serialize()
        self.logger.info("packet-out %s" % (pkt,))
        data = pkt.data
        actions = [parser.OFPActionOutput(port=port)]
        out = parser.OFPPacketOut(datapath=datapath,
                                  buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=ofproto.OFPP_CONTROLLER,
                                  actions=actions,
                                  data=data)
        datapath.send_msg(out)

#####install flow entry sample

'''