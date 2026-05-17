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

def trace_single(target, seq, ttl, sock):
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
    
    pid = os.getpid() & 0xffff
    header = struct.pack('bbHHH', 8, 0, 0, pid, seq)
    data = struct.pack('d', time.time())    
    checksum = get_checksum(header + data)

    header = struct.pack('bbHHH', 8, 0, socket.htons(checksum), pid, seq)
    
    time_start = time.time()
    sock.sendto(header + data, (target, 0))
    wait_start = time.time()
    timeout = 1.0 
    while True:
        try:
            sock.settimeout(timeout)
            packet, addr = sock.recvfrom(1024)
            time_received = time.time()
            
            icmp_header = packet[20:28]
            type, _, _, req_pid, _ = struct.unpack('bbHHH', icmp_header)
            

            if type == 0 and req_pid == pid:
                rtt = (time.time() -  time_start) * 1000
                return addr[0], rtt, True
            elif type == 11:
                _, _, _, inner_pid, _ = struct.unpack('bbHHH', packet[48:56])
                if inner_pid == pid:
                    rtt = (time.time() -  time_start) * 1000
                    return addr[0], rtt, False

            timeout = 1 - time.time() + wait_start

            if timeout <= 0:
                return None, None, False
        
        except socket.timeout:
            return None, None, False


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('target')
    parser.add_argument('-p', '--packets', type=int, default=3)
    parser.add_argument('-m', '--max-hops', type=int, default=30)

    args = parser.parse_args()
    
    try:
        target_ip = socket.gethostbyname(args.target)
    except Exception as e:
        print(f'can not resolve {args.target}')
        sys.exit(1)
            
    icmp = socket.getprotobyname('icmp')
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)    
    seq = 1

    try:
        for ttl in range(1, args.max_hops + 1):
            print(f"{ttl}\t", end="")
            
            router_ip = None
            done = False
            
            for _ in range(args.packets):
                ip, rtt, is_done = trace_single(target_ip, seq, ttl, sock)
                seq += 1
                
                if rtt is not None:
                    print(f"{rtt:4.0f} ms  ", end="")
                    router_ip = ip
                else:
                    print(" *        ", end="")
                
                if is_done:
                    done = True

            if router_ip is not None:
                try:
                    host_name = socket.gethostbyaddr(router_ip)[0]
                    print(f"  {host_name}")
                except socket.herror:
                    print(f"  {router_ip}")
            else:
                print("timeout expired")

            if done:
                break
                
    finally:
        sock.close()
