from checksum import add_checksum, extract_packet, get_checksum, check_data

if __name__ == '__main__':
    print('simple test')
    data = b'hello word'
    checksum = get_checksum(data)
    assert(check_data(data, checksum))
    print('PASSED')

    print('bad checksum')
    checksum += 100
    assert(not check_data(data, checksum))
    print('PASSED')

    print('extract_packet')
    data_with_sum = add_checksum(data)
    assert(extract_packet(data_with_sum) == data)
    print('PASSED')
