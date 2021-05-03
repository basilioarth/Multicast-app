import threading
import datetime
import socket
import struct
import time
import sys
import os

MULTICAST_GROUP = "224.14.0.244"
MULTICAST_PORT_EXPRESSION = 1901
MULTICAST_PORT_PING = 1902
MULTICAST_BUFFER_SIZE_BYTES = 64
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

def multicast_initialize_server(pingsock, showAnotherServersResponse):
    multicast_pingaddress = (MULTICAST_GROUP, MULTICAST_PORT_PING)
    server_id = 1
    msg_count = 0
    global responded 
    pingsock.sendto(b'PING', multicast_pingaddress)
    while True:
        try:
            recv_message, sender_address = pingsock.recvfrom(MULTICAST_BUFFER_SIZE_BYTES)
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
    #pingsock.close()
    return server_id, responded

def multicast_ping_send(pingsock):
    global responded
    while True:
        time.sleep(1)
        responded.clear()
        multicast_initialize_server(pingsock, False)

'''
def multicast_ping_send(pingsock):
    multicast_pingaddress = (MULTICAST_GROUP, MULTICAST_PORT_PING)
    #pingsock.sendto(b'PING', multicast_pingaddress)
    msg_count = 0
    while True:
        time.sleep(1)
        responded.clear()
        pingsock.sendto(b'PING', multicast_pingaddress)
        try:
            recv_message, sender_address = pingsock.recvfrom(MULTICAST_BUFFER_SIZE_BYTES)
            if recv_message:
                msg_count += 1
                received_id = int(recv_message.decode("utf-8"))
                log('Servidor {}{} ativo'.format(recv_message.decode("utf-8"), sender_address), False)
                responded.append(received_id)
        except socket.timeout:
            if msg_count <= 0:
                log("Nenhum outro servidor respondeu", False)
    pingsock.close()
''' 

def multicast_ping_respond(server_id):
    local_address = ("", MULTICAST_PORT_PING)
    sock = create_socket(MULTICAST_GROUP, local_address)
    while True:
        recv_message, client_address = sock.recvfrom(MULTICAST_BUFFER_SIZE_BYTES)
        msg = recv_message.decode("utf-8")
        if msg == "PING":
            #log("Respondendo a mensagem de verificação como servidor {}".format(server_id), True)
            id_bytestr = str(server_id).encode("utf-8")
            sock.sendto(id_bytestr, client_address)

def set_response_server(server_id, pingsock):
    global responded
    responded_now = responded
    responded_now.sort()
    #log("Os seguintes servidores responderam: {}".format(responded), False)
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

server_id, responded = multicast_initialize_server(pingsock, True)
if server_id == None:
    log("Falha ao definir o id do servidor", False)
    exit(1)

time.sleep(1)
log("Definindo o id do servidor para: {}".format(server_id), False)
time.sleep(1)

# Create the UDP socket and bind it to network interface
time.sleep(1)
log("Criando um socket para a resolução da expressão", False)
time.sleep(1)

server_address = ('', MULTICAST_PORT_EXPRESSION)
sock = create_socket(MULTICAST_GROUP, server_address)
time.sleep(1)
log("O servidor agora está aguardando pelo envio da expressão", False)
time.sleep(1)

# Create the respond socket
time.sleep(1)
log("Criando um socket de comunicação entre servidores para o servidor {}".format(server_id), False)
time.sleep(1)
ping_responding_thread_send = threading.Thread(target=multicast_ping_send, args=[pingsock])
ping_responding_thread_send.start()
ping_responding_thread_response = threading.Thread(target=multicast_ping_respond, args=[server_id])
ping_responding_thread_response.start()

#log("O socket de comunicação entre servidores do servidor {} está ouvindo...".format(server_id))

while True:
    recv_message, client_address = sock.recvfrom(MULTICAST_BUFFER_SIZE_BYTES)
    log("Requisição recebida de [{}]: {}".format(client_address, recv_message), True)
    # Check with other servers who will respond the requisition
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