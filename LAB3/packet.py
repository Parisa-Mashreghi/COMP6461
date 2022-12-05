import ipaddress
from sortedcontainers import SortedDict

MIN_LEN = 11
MAX_LEN = 1024

DATA = 0
SYN = 1
SYN_ACK = 2
ACK = 3
NAK = 4

def packets_to_message(buffer_pkt):
    print('packets_to_message')
    barray = bytearray()
    for seq, pkt in buffer_pkt.items():
        barray.extend(pkt.payload)
        # print(barray, len(barray))
    # print(barray, len(barray))
    return barray

def message_to_packets(message, peer_ip, peer_port, seq):
    # print('000000000000000')
    # print(peer_ip)
    # print('000000000000000')
    p_list = list()
    c_byte = message
    while len(c_byte) != 0:
        p_list.append(c_byte[:1013])
        c_byte = c_byte[1013:]
    p_list.append(bytearray())
    # print(p_list)

    package = list()
    for payload in p_list:
        p = Packet(packet_type=DATA,
                   seq_num=seq,
                   peer_ip_addr=peer_ip,
                   peer_port=peer_port,
                   payload=payload)
        package.append(p)
        # print(p)
        seq += 1
    return package

class Packet:
    """
    Packet represents a simulated UDP packet.
    """

    def __init__(self, packet_type, seq_num, peer_ip_addr, peer_port, payload):
        self.packet_type = int(packet_type)
        self.seq_num = int(seq_num)
        self.peer_ip_addr = peer_ip_addr
        self.peer_port = int(peer_port)
        self.payload = payload

    def to_bytes(self):
        """
        to_raw returns a bytearray representation of the packet in big-endian order.
        """
        buf = bytearray()
        buf.extend(self.packet_type.to_bytes(1, byteorder='big'))
        buf.extend(self.seq_num.to_bytes(4, byteorder='big'))
        # print('------------------------------')
        # print(self.peer_ip_addr)
        # print('------------------------------')
        buf.extend(self.peer_ip_addr.packed)
        buf.extend(self.peer_port.to_bytes(2, byteorder='big'))

        buf.extend(self.payload)

        return buf

    def __repr__(self, *args, **kwargs):
        return "#%d, type=%d, peer=%s:%s, size=%d" % (self.seq_num, self.packet_type, self.peer_ip_addr, self.peer_port, len(self.payload))

    @staticmethod
    def from_bytes(raw):
        """from_bytes creates a packet from the given raw buffer.

            Args:
                raw: a bytearray that is the raw-representation of the packet in big-endian order.

            Returns:
                a packet from the given raw bytes.

            Raises:
                ValueError: if packet is too short or too long or invalid peer address.
        """
        if len(raw) < MIN_LEN:
            raise ValueError("packet is too short: {} bytes".format(len(raw)))
        if len(raw) > MAX_LEN:
            raise ValueError("packet is exceeded max length: {} bytes".format(len(raw)))

        curr = [0, 0]

        def nbytes(n):
            curr[0], curr[1] = curr[1], curr[1] + n
            return raw[curr[0]: curr[1]]

        packet_type = int.from_bytes(nbytes(1), byteorder='big')
        seq_num = int.from_bytes(nbytes(4), byteorder='big')
        peer_addr = ipaddress.ip_address(nbytes(4))
        peer_port = int.from_bytes(nbytes(2), byteorder='big')
        payload = raw[curr[1]:]

        return Packet(packet_type=packet_type,
                      seq_num=seq_num,
                      peer_ip_addr=peer_addr,
                      peer_port=peer_port,
                      payload=payload)
