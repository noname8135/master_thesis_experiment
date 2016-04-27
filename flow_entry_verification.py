from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import *
from ryu.ofproto import ofproto_v1_3
from ryu.lib.mac import haddr_to_bin 
from ryu.lib.packet import *




class Flow_entry_verification(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = { 'wsgi': WSGIApplication }
    def __init__(self, *args, **kwargs):
        super(Flow_entry_verification, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        wsgi = kwargs['wsgi']
        wsgi.register(SimpleSwitchController , {simple_switch_instance_name : self })

    def add_flow(self, datapath, priority, match, actions, inst, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser    
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,match=match, instructions=inst)    
        #Modify flow table
        datapath.send_msg(mod)

    def send_packet_out(self, datapath, buffer_id, in_port):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
        actions = []
        req = ofp_parser.OFPPacketOut(datapath, buffer_id, in_port, actions)
        datapath.send_msg(req)

    '''
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        self.logger.info("packet in %s %s %s %s", dpid, src, dst, msg.in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = msg.in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            self.add_flow(datapath, msg.in_port, dst, actions)

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = datapath.ofproto_parser.OFPPacketOut(
            datapath=datapath, buffer_id=msg.buffer_id, in_port=msg.in_port,
            actions=actions, data=data)
        datapath.send_msg(out)
    '''

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        msg = ev.msg

        self.logger.debug('EventOFPSwitchFeatures received:'
            'datapath id = 0x%016x n_buffer=%d'
            'n_tables=%d aux_id=%d capabilities=0x%08x',msg.datapath_id, msg.n_buffers, msg.n_tables,
            msg.auxiliary_id, msg.capabilities)
        
        match = parser.OFPMatch(eth_type = 0x0806)
        actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
        self.add_flow(datapath, 0, match, actions, inst)
        print datapath
        if datapath.id == 1:        ## SWITCH 1
            match = parser.OFPMatch(eth_type = 0x0800, ipv4_src = "10.0.0.1", ipv4_dst = "10.0.0.5")#h1 to h5
            actions = [parser.OFPActionOutput(3)]
            inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
            self.add_flow(datapath, 0, match, actions, inst)
            
            match = parser.OFPMatch(eth_type = 0x0800, ipv4_src = "10.0.0.2", ipv4_dst = "10.0.0.6")#h2 to h6
            actions = [parser.OFPActionOutput(4)]
            inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
            self.add_flow(datapath, 0, match, actions, inst)
            
            match = parser.OFPMatch(eth_type = 0x0800, ipv4_src = "10.0.0.5", ipv4_dst = "10.0.0.1")#h5 to h1
            actions = [parser.OFPActionOutput(1)]
            inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
            self.add_flow(datapath, 0, match, actions, inst)
            
            match = parser.OFPMatch(eth_type = 0x0800, ipv4_src = "10.0.0.6", ipv4_dst = "10.0.0.2")#h6 to h2
            actions = [parser.OFPActionOutput(2)]
            inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
            self.add_flow(datapath, 0, match, actions, inst)
            
        elif datapath.id == 2:      ## SWITCH 2
            match = parser.OFPMatch(eth_type = 0x0800, ipv4_src = "10.0.0.1", ipv4_dst = "10.0.0.5")#h1 to h5
            actions = [parser.OFPActionOutput(3)]
            inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
            self.add_flow(datapath, 0, match, actions, inst)
            
            match = parser.OFPMatch(eth_type = 0x0800, ipv4_src = "10.0.0.5", ipv4_dst = "10.0.0.1")#h5 to h1
            actions = [parser.OFPActionOutput(1)]
            inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
            self.add_flow(datapath, 0, match, actions, inst)
            
        elif datapath.id == 3:      ## SWITCH 3
            match = parser.OFPMatch(eth_type = 0x0800, ipv4_src = "10.0.0.1", ipv4_dst = "10.0.0.5")#h1 to h5
            actions = [parser.OFPActionOutput(3)]
            inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
            self.add_flow(datapath, 0, match, actions, inst)
            
            match = parser.OFPMatch(eth_type = 0x0800, ipv4_src = "10.0.0.2", ipv4_dst = "10.0.0.6")#h2 to h6
            actions = [parser.OFPActionOutput(4)]
            inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
            self.add_flow(datapath, 0, match, actions, inst)
            
            match = parser.OFPMatch(eth_type = 0x0800, ipv4_src = "10.0.0.5", ipv4_dst = "10.0.0.1")#h5 to h1
            actions = [parser.OFPActionOutput(2)]
            inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
            self.add_flow(datapath, 0, match, actions, inst)
            
            match = parser.OFPMatch(eth_type = 0x0800, ipv4_src = "10.0.0.6", ipv4_dst = "10.0.0.2")#h6 to h2
            actions = [parser.OFPActionOutput(1)]
            inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
            self.add_flow(datapath, 0, match, actions, inst)
        elif datapath.id == 4:      ## SWITCH 4
            match = parser.OFPMatch(eth_type = 0x0800, ipv4_src = "10.0.0.2", ipv4_dst = "10.0.0.6")#h2 to h6
            actions = [parser.OFPActionOutput(5)]
            inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
            self.add_flow(datapath, 0, match, actions, inst)
            match = parser.OFPMatch(eth_type = 0x0800, ipv4_src = "10.0.0.6", ipv4_dst = "10.0.0.2")#h6 to h2
            actions = [parser.OFPActionOutput(1)]
            inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
            self.add_flow(datapath, 0, match, actions, inst)            
            print "Flow entry added"

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def _port_status_handler(self, ev):
        msg = ev.msg
        reason = msg.reason
        port_no = msg.desc.port_no
        ofproto = msg.datapath.ofproto
        if reason == ofproto.OFPPR_ADD:
            self.logger.info("port added %s", port_no)
        elif reason == ofproto.OFPPR_DELETE:
            self.logger.info("port deleted %s", port_no)
        elif reason == ofproto.OFPPR_MODIFY:
            self.logger.info("port modified %s", port_no)
        else:
            self.logger.info("Illeagal port state %s %s", port_no, reason)


#Packet_Out reference
#OFPP_TABLE -> send to first flow table.
#OFPP_ALL Forwarded to all physical ports except receiving ports
#OFPP_CONTROLLER -> send to controller