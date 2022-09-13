import socket
import sys
import _thread
import json
import time

HOST = ""  # Endereco IP do Servidor
PORT = 5000  # Porta que o Servidor esta
IP_SERVIDOR = "10.0.1.10"
NICKNAME = None
ID_SALA = None
ID_MSG = 1
ENTROU_SALA = False

def server(udp):
    global ENTROU_SALA
    global ID_SALA
    orig = ("", PORT)
    udp.bind(orig)
    while True:
        msg, cliente = udp.recvfrom(1024)
        msg_decoded = msg.decode('utf-8')
        string_dict = json.loads(msg_decoded)
        if string_dict["acao"] == 1:
            if string_dict["id_sala"] == ID_SALA:
                if string_dict["status"] == 1:
                    ENTROU_SALA = True
        elif string_dict["acao"] == 2:
            if string_dict["id_sala"] == ID_SALA:
                if string_dict["status"] == 1:
                    ENTROU_SALA = False
                    ID_SALA = None
        elif string_dict["acao"] == 3:
            if string_dict["id_sala"] == ID_SALA:
                if string_dict["status"] == 1:
                    #sys.stdout.write('\r')
                    #sys.stdout.flush()
                    print(f'\r{string_dict["nome"]}->{string_dict["msg"]}', end="")
                    print("\n(Voce)-> ", end="")
        #print(f"-> #{cliente}# {string_dict}")


def client():
    global ID_SALA
    global ID_MSG
    global NICKNAME
    print(f"Starting UDP Server on port {PORT}")
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    _thread.start_new_thread(server, (udp,))
    message = None
    dest = (IP_SERVIDOR, PORT)
    nome = input("Informe o seu nickname-> ")
    NICKNAME = nome
    try:
        sala = int(input("Informe o ID da sala que deseja entrar-> "))
        ID_SALA = sala
        entrar_sala = { 
            "acao": 1, 
            "nome": nome,
            "id_sala": sala
        }
        string_json = json.dumps(entrar_sala)
        udp.sendto(string_json.encode('utf-8'), dest)
    except Exception as ex:
        sys.exit(0)
    
    count = 0
    print("Aguardando confirmacao.")
    while True:
        if not ENTROU_SALA:
            count += 1
        else:
            break
        if count == 10:
            sys.exit(0)
        time.sleep(1)
    print(f"Voce entrou na sala {ID_SALA}")
    print("- Digite '!sair' para sair da sala")
    print(25 * "-")
    while message != "!sair":
        message = input("(Voce)-> ")
        if message == "!sair":
            msg = {
                "acao": 2,
                "nome": NICKNAME,
                "id_sala": ID_SALA,
            }
        else:
            msg = {
                "acao": 3,
                "nome": NICKNAME,
                "id_sala": ID_SALA,
                "id_msg": ID_MSG,
                "msg": message
            }
        string_json = json.dumps(msg)
        udp.sendto(string_json.encode('utf-8'), dest)
        ID_MSG += 1
    udp.close()

if __name__ == "__main__":
    client()
