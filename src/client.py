import datetime
import config
import socket
import struct
import sys
import os

multicast_group = (config.MULTICAST_GROUP, config.MULTICAST_PORT_EXPRESSION)

def log(text):
    now = datetime.datetime.now().ctime()
    print("[{}] {}".format(now, text))

log("Criando o socket de comunicação com o servidor")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(1)                                                  
ttl = struct.pack('b', 1)                                           
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)    

while True:
    expression_string = bytes(input("Digite a expressão a ser calculada:"), "utf-8")
    log("Enviando a expressão...")
    sent = sock.sendto(expression_string, multicast_group)
    msg_count = 0
    try:
        recv_message, server_address = sock.recvfrom(config.MULTICAST_BUFFER_SIZE_BYTES)
        if recv_message:
            msg_count += 1
    except socket.timeout:
        if msg_count <= 0:
            log("Nenhuma resposta foi recebida!")
        break
    else:
        log('O resultado {} foi recebido do servidor {}'.format(recv_message.decode("utf-8"), server_address))