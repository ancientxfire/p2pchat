import socket


EXCLUDED_IP_RANGES = ["172","100","127"]
def getAllIps():
    ip_addresses = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")]
    socket.gethostbyname_ex(socket.gethostname())
    conv_ip_addresses = []
    for adress in ip_addresses: 
        if adress.startswith(tuple(EXCLUDED_IP_RANGES)):
            continue
        conv_ip_addresses.append(socket.inet_aton(adress))
    return conv_ip_addresses