import socket
import json

DEBUG = True
PORT = 5000  # Porta que o Servidor esta
LISTA_USUARIO = []


def adicionar_usuario(usuario, cliente):
    novo_usuario = {}
    novo_usuario["nome"] = usuario["nome"]
    novo_usuario["conexao"] = cliente
    novo_usuario["id_sala"] = usuario["id_sala"]
    LISTA_USUARIO.append(novo_usuario)


def remover_usuario(usuario, cliente):
    usuario_removido = {}
    usuario_removido["nome"] = usuario["nome"]
    usuario_removido["conexao"] = cliente
    usuario_removido["id_sala"] = usuario["id_sala"]
    LISTA_USUARIO.remove(usuario_removido)


def enviar_mensagem_grupo(udp, cliente, string_dict, msg):
    msg_json = json.dumps(msg)
    
    for users in LISTA_USUARIO:
        if users["id_sala"] == string_dict["id_sala"]:
            if users["conexao"] != cliente:
                udp.sendto(msg_json.encode("utf-8"), users["conexao"])


def entrar_sala(udp, cliente, string_dict):
    adicionar_usuario(string_dict, cliente)
    msg = {
        "acao": 1,
        "nome": string_dict["nome"],
        "id_sala": string_dict["id_sala"],
        "status": 1
    }
    msg_json = json.dumps(msg)
    if DEBUG:
        print(f"*ENTROU*{msg_json} -> {cliente}")
    udp.sendto(msg_json.encode("utf-8"), cliente)

    msg = {
        "id_sala": string_dict["id_sala"],
        "nome": string_dict["nome"],
        "msg": f"{string_dict['nome']} ENTROU NA SALA"
    }
    
    enviar_mensagem_grupo(udp, cliente, string_dict, msg)


def sair_sala(udp, cliente, string_dict):
    remover_usuario(string_dict, cliente)
    msg = {
        "acao": 2,
        "nome": string_dict["nome"],
        "id_sala": string_dict["id_sala"],
        "status": 1
    }
    msg_json = json.dumps(msg)
    if DEBUG:
        print(f"*REMOVIDO*{msg_json} -> {cliente}")
    udp.sendto(msg_json.encode("utf-8"), cliente)

    msg = {
        "id_sala": string_dict["id_sala"],
        "nome": string_dict["nome"],
        "msg": f"{string_dict['nome']} SAIU DA SALA"
    }
    enviar_mensagem_grupo(udp, cliente, string_dict, msg)


def mensagem_sala_grupo(udp, cliente, string_dict):
    msg = {
        "acao": 3,
        "nome": string_dict["nome"],
        "id_sala": string_dict["id_sala"],
        "id_msg": string_dict["id_msg"],
        "status": 1
    }
    msg_json = json.dumps(msg)
    if DEBUG:
        print(f"*MSG RECEBIDA*{msg_json} -> {cliente}")
    #Mensagem de confirmacao para quem enviou
    udp.sendto(msg_json.encode("utf-8"), cliente)
    msg = {
        "id_sala": string_dict["id_sala"],
        "nome": string_dict["nome"],
        "msg": string_dict["msg"]
    }
    enviar_mensagem_grupo(udp, cliente, string_dict, msg)


def chat_server(udp):
    print(f"Starting UDP Server on port {PORT}")
    orig = ("", PORT)
    udp.bind(orig)
    while True:
        msg, cliente = udp.recvfrom(1024)
        msg_decoded = msg.decode('utf-8')
        if DEBUG:
            print(f"{msg_decoded}")
        try:
            string_dict = json.loads(msg_decoded)
            if string_dict["acao"] == 1:
                entrar_sala(udp, cliente, string_dict)
            elif string_dict["acao"] == 2:
                sair_sala(udp, cliente, string_dict)
            elif string_dict["acao"] == 3:
                mensagem_sala_grupo(udp, cliente, string_dict)
        except Exception as ex:
            pass


def main():
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    chat_server(udp)


if __name__ == "__main__":
    main()
