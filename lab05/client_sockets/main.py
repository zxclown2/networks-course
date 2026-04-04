import argparse
import socket

def send_single_msg(sock, msg):
    if msg:
        msg += '\r\n'
        sock.sendall(msg.encode('ascii'))
    resp = sock.recv(1024).decode('ascii')
    # print(resp)
    return resp

def send_email(server, port, frm, rcpt, subject, body):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((server, port))

        send_single_msg(sock, None)
        send_single_msg(sock, 'HELO 127.0.0.1')
        send_single_msg(sock, f'MAIL FROM: <{frm}>')
        send_single_msg(sock, f'RCPT TO: <{rcpt}>')

        send_single_msg(sock, 'DATA')

        body_str = (
            f'From: {frm}\r\nTo: {rcpt}\r\nSubject: {subject}\r\n'
            'Content-Type: text/plain; charset=\"utf-8\"\r\n'
            'Content-Transfer-Encoding: 7bit\r\n\r\n'
            f'{body}\r\n.'
        )
        send_single_msg(sock, body_str)
        send_single_msg(sock, 'QUIT')

    except Exception as e:
        print(f'Error while sending email: {e}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="smtp client")

    parser.add_argument(
        '--sender', 
        type=str,
    )

    parser.add_argument(
        '--recipient', 
        type=str,
    )

    parser.add_argument(
        '--subject',
        type=str,
        default='subject'
    )

    parser.add_argument(
        '--body',
        type=str,
        default='body'
    )

    parser.add_argument(
        '--format',
        type=str,
        default='text'
    )

    parser.add_argument (
        '--server',
        type=str,
        default='127.0.0.1'
    )

    parser.add_argument(
        '--port',
        type=int,
        default=2525
    )
    args = parser.parse_args()

    send_email(
        server=args.server,
        port=args.port,
        frm=args.sender,
        rcpt=args.recipient,
        subject=args.subject,
        body=args.body
    )
