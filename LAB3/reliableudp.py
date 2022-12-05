import socket
import packet as PK
import time
from enum import Enum
from threading import Timer
from collections import OrderedDict
from sortedcontainers import SortedDict
import ipaddress

WINDOW_SIZE_LIMIT = 20
TIMEOUT_SEND = 5

class WindowStatus(Enum):
    INVALID = -1
    QUEUED = 10
    ACK = 3
    PROCESSING = 11
    TIMEOUT = 12
    NAK = 5

class SRWindow:
    def __init__(self, status, seq, packet):
        self.time = time.time()
        self.status = status
        self.seq = seq
        self.packet = packet

class ReliableUdpSocket:
    def __init__(self, peer_ip_port, router=('localhost', 3000)):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.router = router
        self.peer_ip_port = peer_ip_port
        self.swindow = SortedDict()
        self.rwindow = SortedDict()
        self.sseq = 1
        self.rseq = 1
        # self.timer = Timer(1, self.check_all)
        # self.timer.start()

    def bind(self, ip_port):
        self.sock.bind(ip_port)

    def connect(self, ip_port):
        print('connect')
        self.sock.connect(self.router)
        peer_ip = ipaddress.ip_address(socket.gethostbyname(ip_port[0]))
        peer_port = ip_port[1]
        # self.peer_ip_port = (peer_ip, peer_port)
        # print('--------tttttttttt----------------')
        # print(peer_ip)
        # print('--------ttttttttttttt------------')
        for i in range(1):
            try:
                p1 = PK.Packet(PK.SYN, self.sseq, peer_ip, peer_port, bytearray())
                self.sseq += 1
                print('******')
                print(p1)
                print('******')
                self.sock.sendall(p1.to_bytes())
                data, route = self.sock.recvfrom(1024)
                p2 = PK.Packet.from_bytes(data)
                print('------------------------------')
                print(p2)
                print('------------------------------')
                p3 = PK.Packet(PK.ACK, p2.seq_num + 1, p2.peer_ip_addr, p2.peer_port, bytearray())
                self.rseq = p2.seq_num + 1
                print('******')
                print(p3)
                print('******')
                self.sock.sendall(p3.to_bytes())
                self.peer_ip_port = (p2.peer_ip_addr, p2.peer_port)
                time.sleep(1)
                return self.peer_ip_port
            except Exception as e:
                pass
                # log.error(e)

    def accept(self):
        print('accept')
        while True:
            try:
                self.sock.settimeout(10)
                data, r = self.sock.recvfrom(1024) 
                p = PK.Packet.from_bytes(data)
                # print("Router: ", r)
                # print("Packet: ", p)
                # print("Payload: ", p.payload.decode("utf-8"))
                if p.packet_type == PK.SYN:
                    return self.create_socket(p)
            except socket.timeout as e:
                continue

    def create_socket(self, p):
        print('create_socket')
        # print(p.peer_ip_addr)
        # print(p.peer_port)
        csock = ReliableUdpSocket((p.peer_ip_addr, p.peer_port), self.router)
        csock.rseq = p.seq_num + 1
        np = PK.Packet(PK.SYN_ACK, p.seq_num, p.peer_ip_addr, p.peer_port, "".encode('utf-8'))
        csock.send_packet(np)
        return csock, p.peer_ip_addr

    def send_packet(self, p):
        w = SRWindow(WindowStatus.QUEUED, self.sseq, p)
        self.swindow[p.seq_num] = w
        self.send_packets()

    def sendall(self, ba):
        # print('sendall')
        pkts = PK.message_to_packets(ba, self.peer_ip_port[0], self.peer_ip_port[1], self.sseq)
        for p in pkts:
            w = SRWindow(WindowStatus.QUEUED, self.sseq, p)
            self.swindow[self.sseq] = w
            self.sseq += 1
        self.send_packets()

    def send_packets(self):
        # print('send_packets')
        # peer_ip = ipaddress.ip_address(socket.gethostbyname(self.router[0]))
        # peer_port = self.router[1]
        for seq, w in self.swindow.items():
            # print('******')
            # print(w.packet)
            # print('******')
            self.sock.sendto(w.packet.to_bytes(), self.router) 
        self.swindow.clear()

    # def send_packets(self):
    #     for window in self.swindow:
    #         if (window.status == WindowStatus.QUEUED) or (window.status == WindowStatus.NAK):
    #             self.sock.sendto(window.packet.to_bytes(), self.ip_port)
    #             window.status = WindowStatus.PROCESSING
    #             window.time = time.time()
    #         elif (window.status == WindowStatus.PROCESSING):
    #             wait = time.time() - window.time
    #             if (wait > TIMEOUT_SEND):
    #                 self.sock.sendto(window.packet.to_bytes(), self.ip_port)
    #                 window.time = time.time()

    def recvall(self):
        print('recvall')
        loss_list = list()
        first_seq = self.rseq
        # print(f'OOOOOOOOOOOOOOOO {first_seq}')
        # last_seq = 0
        keep_recv = True
        self.sock.settimeout(1)
        stime = time.time()
        timeout_check = False
        count_check = False
        new_count = 0
        while keep_recv:
            try:
                barray = self.sock.recv(PK.MAX_LEN)
                pkt = PK.Packet.from_bytes(barray)
                # print('------------------------------')
                # print(pkt)
                # print('------------------------------')
                if (pkt.packet_type == PK.DATA):
                    # if (not last_seq+1 == pkt.seq_num) and (not pkt.seq_num in loss_list):
                    #     for j in range(last_seq+1, pkt.seq_num):
                    #         loss_list.append(j)
                    w = SRWindow(pkt.packet_type, pkt.seq_num, pkt)
                    self.rwindow[pkt.seq_num] = w
                    new_count += 1
                    if (new_count > 5):
                        new_count = 0
                        count_check = True
                    # buffer_pkt[pkt.seq_num] = pkt
                    # last_seq = pkt.seq_num
                    # self.send_packet(PK.Packet(PK.ACK, pkt.seq_num, pkt.peer_ip_addr, pkt.peer_port, bytearray()))
                    # TODO send_ACK() if time is over or 10 packets were received
                    # if (len(pkt.payload) == 0 and len(loss_list) == 0):
                    #     keep_recv = False
                else:
                    pass
                    # self.swindow.append(PK.Packet(PK.ACK, pkt.seq_num, pkt.peer_ip_addr, pkt.peer_port, bytearray(0)))
                    # TODO send_ACK() if time is over or 10 packets were received
            except socket.timeout:
                timeout_check = True
            if timeout_check or count_check:
                keep_recv = self.process_recv_packets(first_seq)
                timeout_check = False
                count_check = False
            time.sleep(0.01)
        buffer_pkt = SortedDict()
        for seq, w in self.rwindow.items():
            buffer_pkt[seq] = w.packet
        return PK.packets_to_message(buffer_pkt)

    def process_recv_packets(self, first_seq):
        # print(' ^^^^^^^^ process_recv_packets')
        keys = list(self.rwindow.keys())
        keep_recv = False
        if len(keys) == 0:
            return True
        last_seq = keys[-1]
        last_len = len(self.rwindow[last_seq].packet.payload)
        expected = last_seq - first_seq + 1
        # print('expected ', expected)
        # print('first_seq ', first_seq)
        # print('last_seq ', last_seq)
        for i in range(first_seq, expected):
            if not i in keys:
                keep_recv = True
                self.send_packet(PK.Packet(PK.NAK, i, self.peer_ip_port[0], self.peer_ip_port[1], bytearray()))
        if (expected == len(keys)) and (last_len == 0):
            keep_recv = False
            self.rseq = last_seq + 1
        return keep_recv

    def close(self):
        self.sock.close()

