import random
import socket

from checksum import add_checksum, extract_packet

class Sender:
    def __init__(self, logger, timeout, drop_rate):
        self.timeout, self.drop_rate = timeout, drop_rate
        self.logger = logger

    
    def send_data(self, host, port, data):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)
        num = 0

        for packet in data:
            ok = False
            packet_to_send = add_checksum(f'{num}!{packet}'.encode('utf-8'))
            while not ok:
                if random.random() < self.drop_rate:
                        self.logger.info('packet dropped')
                        continue

                sock.sendto(packet_to_send, (host, port))

                try:
                    data, _ = sock.recvfrom(1024)
                    data = extract_packet(data)
                    if data.decode('utf-8') == f'ACK_{num}':
                        ok = True
                        num = 1 - num
                except socket.timeout:
                    self.logger.info('timeout')
                    continue
                self.logger.info(f'success for packet: {packet}')
    
        sock.close()