#!/usr/bin/python

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_0
from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import packet, ethernet, ether_types, tcp


class L2Switch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]    

    def __init__(self, *args, **kwargs):
        super(L2Switch, self).__init__(*args, **kwargs)
        self.num = 0

    def add_flow(self, datapath, in_port, dst, src, tp_dst, actions):
        ofproto = datapath.ofproto

        match = datapath.ofproto_parser.OFPMatch(
            in_port=in_port, tp_dst=tp_dst, dl_type=2048, nw_proto=6,
            dl_dst=haddr_to_bin(dst), dl_src=haddr_to_bin(src))

        mod = datapath.ofproto_parser.OFPFlowMod(
            datapath=datapath, match=match, cookie=0,
            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
            priority=ofproto.OFP_DEFAULT_PRIORITY,
            flags=ofproto.OFPFF_CHECK_OVERLAP, actions=actions)
        datapath.send_msg(mod)
    
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        # Dados sendo transmitidos
        msg = ev.msg

        # Switch que emitiu o evento
        datapath = msg.datapath
        
        # id do switch que se comunicou com esse controlador
        dpid = datapath.id 

        # openflow protocol
        ofproto = datapath.ofproto

        # O Pacote (pronto para ser trabalhado com nossas libs)
        pkt = packet.Packet(msg.data)

        # O pacote interpretado no "ponto de vista" Ethernet
        pkt_eth = pkt.get_protocol(ethernet.ethernet)

        # O pacote interpretado no "ponto de vista" TCP
        pkt_tcp = pkt.get_protocol(tcp.tcp)

        # Ignorando pacotes LLDP
        if pkt_eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        # macs da topologia que queremos comunicar os pings
        h1_mac = '1e:0b:fa:73:69:f1'
        h2_mac = '1e:0b:fa:73:69:f2'

        self.logger.info('[%s]', str(self.num))
        self.logger.info(
            "packet in -> dpid: %s, src: %s, dst: %s, in_port: %s",
            dpid, pkt_eth.src, pkt_eth.dst, msg.in_port)
        
        if (pkt_tcp):
            self.logger.info('app port dst:' + str(pkt_tcp.dst_port))

        # Logica para adicionar os fluxos
        out_port = ofproto.OFPP_FLOOD
        if (pkt_eth.src == h1_mac and pkt_eth.dst == h2_mac) \
            or (pkt_eth.src == h2_mac and pkt_eth.dst == h1_mac) \
            and pkt_tcp:
            if dpid == 1:
                if msg.in_port == 1:
                    if pkt_tcp.dst_port == 5001:
                        out_port = 2
                    elif pkt_tcp.dst_port == 5002:
                        out_port = 3
                    elif pkt_tcp.dst_port == 5003:
                        out_port = 4
                else:
                    out_port = 1
            elif dpid in [2, 3]:
                if msg.in_port == 1:
                    out_port = 2
                else:
                    out_port = 1
            elif dpid == 4:
                if msg.in_port == 4:
                    out_port = 2
                else:
                    out_port = 4

        self.logger.info('out_port: ' + str(out_port))

        # definindo a acao a ser tomada com base na porta de destino
        actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]

        # adicionando um fluxo para evitar um packet_in na proxima vez
        if (out_port != ofproto.OFPP_FLOOD):
            self.add_flow(
                msg.datapath, msg.in_port, pkt_eth.dst,
                pkt_eth.src, pkt_tcp.dst_port, actions)
        
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        # encaminhando o pacote
        out = datapath.ofproto_parser.OFPPacketOut(
            datapath=datapath, buffer_id=msg.buffer_id, in_port=msg.in_port,
            actions=[datapath.ofproto_parser.OFPActionOutput(out_port)],
            data=data)
        datapath.send_msg(out)
        self.num += 1
