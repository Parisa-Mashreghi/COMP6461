import socket
import packet
import logging
from numpy import uint32


class libarq():
    def __init__(self, router=('localhost', 3000), sequence=0):
        self.count_max = 20
        self.address = None
        self.socket = None
        self.packet = None
        # self.client_list = list()
        self.router = router
        self.sequence = sequence
        self.log = logging.getLogger('ARQ')

    def bind(self, address):
        self.address = address

    def listen(self, count):
        self.count_max = count

    def open_socket(self, family=-1, type=-1):
        self.socket = socket.socket(family, type)  # SOCK_DGRAM or SOCK_STREAM?

    def grow_sequence(self, sequence, add_value):
        se = uint32(sequence) + uint32(add_value)
        if se < sequence:
            se = se + uint32(1)
        return se

    def accept_client(self):
        print("create a new thread")

        client_socket = libarq()
        client_socket.open_socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        client_socket.socket.sendto(self.router, packet.Packet(packet_type=packet.SYN_ACK,
                                                               peer_ip_addr=self.packet.peer_ip_addr,
                                                               peer_port=self.packet.peer_port,
                                                               seq_num=self.packet.seq_num,
                                                               payload="".encode("utf-8")).to_bytes())
        print("send SYN-ACK")

        if self.packet.packet_type == packet.SYN:
            client_socket.sequence = self.grow_sequence(self.packet.seq_num, 1)
            client_socket.remote = (self.packet.peer_ip_addr, self.packet.peer_port)
            client_socket.socket.connect(self.router)
            print("receive ACK, sequence #:" + str(self.packet.seq_num))
            # print("Router: ", route)
            print("Packet: ", self.packet)
            print("Payload: ", self.packet.payload.decode("utf-8"))
            return client_socket, (self.packet.peer_ip_addr, self.packet.peer_port)
        else:
            return None, None

    def accept(self):
        try:
            data, route = self.socket.recvfrom(1024)  # max buffer size is 1024 Bytes
            self.packet = packet.Packet.from_bytes(data)

            ### MUST CHANGE ###
            print("Router: ", route)
            print("Packet: ", self.packet)
            print("Payload: ", self.packet.payload.decode("utf-8"))

            # if len(self.client_list) > self.count_max:
            #     return None, None  # add proper return

            if self.packet.packet_type == packet.SYN:
                return self.accept_client()

        except socket.timeout as e:
            self.log.error(e)
            return None, None

    def close(self):
        self.socket.close()
        # for conenctions in self.client_list:
        #     conenctions.close()
