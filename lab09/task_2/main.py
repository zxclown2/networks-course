import argparse
import socket

def check_ports(adress, start, end):
    free_ports = []
    
    for port in range(start, end + 1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if s.connect_ex((adress, port)) != 0:
            free_ports.append(port)
        s.close()

    return free_ports

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--start_port', type=int, default=0)
    parser.add_argument('--end_port', type=int, default=65535)

    args = parser.parse_args()

    print(check_ports(args.host, args.start_port, args.end_port))