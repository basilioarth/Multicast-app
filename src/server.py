import threading
import datetime
import config
import socket
import struct
import time
import sys
import os

responded = []

def resolve_expression(expression_string):
    try:
        return eval(expression_string)
    except:
        return None

def log(text, hasBreakLine):
    now = datetime.datetime.now().ctime()
    if(hasBreakLine):
        print("\n[{}] {}".format(now, text))
    else:
        print("[{}] {}".format(now, text))

def create_socket(multicast_group, server_address):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(server_address)
    group = socket.inet_aton(multicast_group)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    return sock

def multicast_align_servers(pingsock, showAnotherServersResponse):
    multicast_pingaddress = (config.MULTICAST_GROUP, config.MULTICAST_PORT_PING)
    server_id = 1
    msg_count = 0
    global responded 
    pingsock.sendto(b'PING', multicast_pingaddress)
    while True:
        try:
            recv_message, sender_address = pingsock.recvfrom(config.MULTICAST_BUFFER_SIZE_BYTES)
            if recv_message:
                msg_count += 1
                received_id = int(recv_message.decode("utf-8"))
                if not showAnotherServersResponse:
                    log('Servidor {}{} ativo'.format(recv_message.decode("utf-8"), sender_address), False)
                if showAnotherServersResponse:
                    log('Resposta do servidor de ID: {}'.format(recv_message.decode("utf-8")), False)
                responded.append(received_id)
                if received_id >= server_id:
                    server_id = received_id + 1
        except socket.timeout:
            if msg_count <= 0:
                log("Nenhum outro servidor respondeu", False)
            break
    return server_id, responded

def multicast_ping_send(pingsock):
    global responded
    while True:
        time.sleep(1)
        responded.clear()
        multicast_align_servers(pingsock, False)

def multicast_ping_respond(server_id):
    local_address = ("", config.MULTICAST_PORT_PING)
    sock = create_socket(config.MULTICAST_GROUP, local_address)
    while True:
        recv_message, client_address = sock.recvfrom(config.MULTICAST_BUFFER_SIZE_BYTES)
        msg = recv_message.decode("utf-8")
        if msg == "PING":
            id_bytestr = str(server_id).encode("utf-8")
            sock.sendto(id_bytestr, client_address)

def set_response_server(server_id, pingsock):
    global responded
    responded_now = responded
    responded_now.sort()
    if server_id in responded_now:
        if responded.index(server_id) == 0:
            log("O servidor detentor do id {} responderá".format(server_id), False)
            return True
    return False

log("Inicializando servidor e testando conexão com outros servidores", False)
time.sleep(1)

pingsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
pingsock.settimeout(0.5)                                               
ttl = struct.pack('b', 1)                                               
pingsock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

server_id, responded = multicast_align_servers(pingsock, True)
if server_id == None:
    log("Falha ao definir o id do servidor", False)
    exit(1)

time.sleep(1)
log("Definindo o id do servidor para: {}".format(server_id), False)
time.sleep(1)

time.sleep(1)
log("Criando um socket para a resolução da expressão", False)
time.sleep(1)

server_address = ('', config.MULTICAST_PORT_EXPRESSION)
sock = create_socket(config.MULTICAST_GROUP, server_address)
time.sleep(1)
log("O servidor agora está aguardando pelo envio da expressão", False)
time.sleep(1)

time.sleep(1)
log("Criando um socket de comunicação entre servidores para o servidor {}\n".format(server_id), False)
time.sleep(1)

ping_responding_thread_send = threading.Thread(target=multicast_ping_send, args=[pingsock])
ping_responding_thread_send.start()
ping_responding_thread_response = threading.Thread(target=multicast_ping_respond, args=[server_id])
ping_responding_thread_response.start()

while True:
    recv_message, client_address = sock.recvfrom(config.MULTICAST_BUFFER_SIZE_BYTES)
    log("Requisição recebida de [{}]: {}".format(client_address, recv_message.decode("utf-8")), True)
    should_respond = set_response_server(server_id, pingsock)
    if should_respond:
        log("Calculando o resultado da expressão...", False)
        expression = recv_message.decode("utf-8")
        solved_data = resolve_expression(expression)
        log("Enviando o resultado: {}\n".format(solved_data), False)
        sock.sendto(str(solved_data).encode("utf-8"), client_address)
    else:
        log("Ignorando o cálculo da expressão\n", False)

ping_responding_thread_send._stop()
ping_responding_thread_response._stop()