def count_checksum(data):
    if len(data) % 2 == 1:
        data += b'\x00'

    res = 0

    for i in range(0, len(data), 2):
        word = (data[i] << 8) + data[i + 1]
        res += word
        res = (res & 0xFFFF) + (res >> 16)

    res = (res & 0xFFFF) + (res >> 16)
    return res

def get_checksum(data):
    return ~count_checksum(data) & 0xFFFF

def check_data(data, checksum):
    res = count_checksum(data)
    res += checksum
    res = (res & 0xFFFF) + (res >> 16)
    return res == 0xFFFF

def add_checksum(data):
    return data + b'!' + str(get_checksum(data)).encode('utf-8')

def extract_packet(data):
    raw_packet = data.split(b'!')
    checksum = raw_packet[-1]
    try:
        checksum = int(checksum)
        packet = b'!'.join(raw_packet[:-1])
    except Exception as e:
        raise RuntimeError(f'Bad checksum')
    if not check_data(packet, checksum):
        raise RuntimeError('Bad checksum')
    return packet