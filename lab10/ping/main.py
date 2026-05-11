import argparse
import os
import socket
import struct
import sys
import time

def get_checksum(string):
    res = 0
    end = (len(string) // 2) * 2
    for i in range(0, end, 2):
        val = string[i + 1] * 256 + string[i]
        res = (res + val) & 0xffffffff
    if end < len(string):
        res = (res + string[-1]) & 0xffffffff
    res = (res >> 16) + (res & 0xffff)
    res += (res >> 16)
    res = ~res & 0xffff
    return res >> 8 | (res << 8 & 0xff00)

def ping_single(target, seq, sock):
    pid = os.getpid() & 0xffff
    header = struct.pack('bbHHH', 8, 0, 0, pid, seq)
    data = struct.pack('d', time.time())
    
    checksum = get_checksum(header + data)
    header = struct.pack('bbHHH', 8, 0, socket.htons(checksum), pid, seq)
    
    sock.sendto(header + data, (target, 0))

    timeout = 1
    wait_start = time.time()

    while True:
        try:
            sock.settimeout(timeout)
            packet, addr = sock.recvfrom(1024)
            time_received = time.time()
            
            icmp_header = packet[20:28]
            type, _, _, req_pid, rec_seq = struct.unpack('bbHHH', icmp_header)
            
            if type == 0 and req_pid == pid:
                rtt = (time_received - struct.unpack('d', packet[28:36])[0]) * 1000
                print(f'Reply from {addr[0]}: seq={rec_seq} time={rtt:.2f} ms')
                return rtt

            timeout = 1 - time.time() + wait_start

            if timeout <= 0:
                print('timeout expired')
                return -1
        
        except socket.timeout:
            print('timeout expired')
            return -1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('target')

    args = parser.parse_args()
    try:
        target_ip = socket.gethostbyname(args.target)
    except Exception as e:
        print(f'can not resolve {args.target}')
        sys.exit(1)
    print(f'ping {args.target} ({target_ip})...\n')
    
    icmp = socket.getprotobyname('icmp')
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    sock.settimeout(1.0)
    
    seq = 1
    rtts = []
    sent = 0
    start_time = time.time()
    try:
        while True:
            sent += 1
            rtt = ping_single(target_ip, seq, sock)
            if rtt > -1:
                rtts.append(rtt)
            seq += 1
            time.sleep(1)
    except KeyboardInterrupt:
        total_time = time.time() - start_time
        print(f'--- {args.target} ping statistics ---')
        loss = .0 if sent == 0 else 1 - len(rtts) / sent

        print(f'{sent} packets transmitted, {len(rtts)} received, {loss * 100:.2f}% packet loss, time {total_time * 1000:.0f} ms')
        if len(rtts) > 0:
            print(f'rtt min/avg/max = {min(rtts):.2f}/{sum(rtts) / len(rtts):.2f}/{max(rtts):.2f}')
        else:
            print(f'no packets received')
        sock.close()
