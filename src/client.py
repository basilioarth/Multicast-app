import datetime
import socket
import struct
import sys
import os

MULTICAST_GROUP = "224.14.0.244"
MULTICAST_PORT_EXPRESSION = 1901
MULTICAST_PORT_PING = 1902
MULTICAST_BUFFER_SIZE_BYTES = 64

multicast_group = (MULTICAST_GROUP, MULTICAST_PORT_EXPRESSION)

def log(text):
    now = datetime.datetime.now().ctime()
    print("[{}] {}".format(now, text))

# Create the UDP datagram socket and configure a few options
log("Criando o socket de comunicação com o servidor")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(1)                                                  # Timeout in seconds
ttl = struct.pack('b', 1)                                           # Set TTL to 1 hop (limits the network reach to local-only)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)    # Define socket options

expression_string = bytes(input("Digite a expressão a ser calculada:"), "utf-8")

log("Enviando a expressão...")
try:
    sent = sock.sendto(expression_string, multicast_group)
    msg_count = 0
    while True:
        try:
            recv_message, server_address = sock.recvfrom(MULTICAST_BUFFER_SIZE_BYTES)
            if recv_message:
                msg_count += 1
        except socket.timeout:
            if msg_count <= 0:
                log("Nenhuma resposta foi recebida!")
            break
        else:
            log('O resultado {} foi recebido do servidor {}'.format(recv_message.decode("utf-8"), server_address))
finally:
    log("Encerrando a aplicação cliente")
    sock.close()