from socket import socket, AF_INET, SOCK_DGRAM


# 获取本机 IPv4 地址
def getIPv4() -> str:
    try:
        s = socket(AF_INET, SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip, _ = s.getsockname()
    except Exception as e:
        print(f"获取本机 IP 地址出错, {e}")
    finally:
        s.close()
        return ip
