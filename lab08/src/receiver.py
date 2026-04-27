import random
import socket
from checksum import add_checksum, extract_packet

class Receiver:
    def __init__(self, logger, port, drop_rate):
        self.drop_rate = drop_rate
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', port))
        self.logger = logger
        self.result = []

    def stop(self):
        self.logger.info('stopping')
        self.sock.close()
        self.logger.info(f'result is:\n{'\n'.join(self.result)}')
    
    def run(self):
        exp_num = 0

        while True:
            data, client = self.sock.recvfrom(1024)
            if random.random() < self.drop_rate:
                self.logger.info('packet dropped')
                continue
            
            data = extract_packet(data)
            try:
                raw_msg = data.decode('utf-8').split('!')
                num, msg = raw_msg[0], raw_msg[1:]
                num = int(num)
            except Exception as e:
                self.logger.info(f'bad packet')
                continue

            if num == exp_num:
                self.logger.info(f'added: {'!'.join(msg)}')
                exp_num = 1 - exp_num
                self.result.append('!'.join(msg))

            self.sock.sendto(add_checksum(f'ACK_{num}'.encode('utf-8')), client)

    def serve(self):
        try:
            self.run()
        finally:
            self.logger.info(f'\nstopping server')
            try:
                self.sock.close()
            except OSError:
                pass
            self.logger.info(f'result is:\n{'\n'.join(self.result)}')