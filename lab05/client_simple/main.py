import argparse
import smtplib
from email.message import EmailMessage

def send_email(server, port, frm, rcpt, subject, body, fmt='text'):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = frm
    msg['To'] = rcpt

    if fmt == 'html':
        msg.add_alternative(body, subtype='html')
    else:
        msg.set_content(body)
    try:
        with smtplib.SMTP(server, port) as smtp:
            smtp.send_message(msg)
        
    except Exception as e:
        print(f"Error while sending email: {e}")


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
