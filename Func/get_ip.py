from socket import socket, AF_INET, SOCK_DGRAM


def getIPv4():
    '''
    获取本机 IPv4 地址
    '''
    try:
        s = socket(AF_INET, SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception as e:
        print(e)
    finally:
        s.close()
        return ip
