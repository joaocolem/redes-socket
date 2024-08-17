import socket
import threading
import sys
import os

host_servidor = '127.0.0.1'
porta_servidor = 5000

soquete_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soquete_servidor.connect((host_servidor, porta_servidor))

nome = input("Escreva seu nome: ")
soquete_servidor.send(nome.encode('utf-8'))

conversas = {}
conversa_atual = None
portas_cache = {}
lock = threading.Lock()

# Dicionário para armazenar conexões persistentes
conexoes_persistentes = {}

def limpar_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def obter_porta_local():
    try:
        soquete_servidor.send(f"Solicitar IP,{nome}".encode('utf-8'))
        resposta = soquete_servidor.recv(1024).decode('utf-8')
        if resposta:
            _, porta_local = resposta.split(",")
            return int(porta_local)
        else:
            raise Exception("Não foi possível obter a porta local.")
    except Exception as e:
        print(f"Erro ao obter porta local: {e}")
        sys.exit()

def iniciar_soquete_local():
    global soquete_local
    try:
        porta_local = obter_porta_local()
        soquete_local = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soquete_local.bind((host_servidor, porta_local))
        soquete_local.listen(5)
        print(f"Aguardando conexões na porta {porta_local}...")
        threading.Thread(target=receber_conexoes, daemon=True).start()
    except Exception as e:
        print(f"Erro ao iniciar o soquete local: {e}")
        sys.exit()

def receber_conexoes():
    try:
        while True:
            conexao, endereco = soquete_local.accept()
            print(f"Conexão recebida de {endereco}")
            threading.Thread(target=ouvir_mensagens, args=(conexao,), daemon=True).start()
    except Exception as e:
        print(f"Erro ao receber conexões: {e}")
    finally:
        soquete_local.close()

def ouvir_mensagens(conexao):
    try:
        while True:
            mensagem = conexao.recv(1024).decode('utf-8')
            if mensagem:
                remetente, conteudo = mensagem.split(": ", 1)
                with lock:
                    if remetente not in conversas:
                        conversas[remetente] = []
                    conversas[remetente].append(f"{remetente}: {conteudo}")
    except Exception as e:
        print(f"Erro ao receber mensagem: {e}")
    finally:
        conexao.close()
        # Remove a conexão persistente se o destinatário se desconectar
        if remetente in conexoes_persistentes:
            del conexoes_persistentes[remetente]

def obter_porta_destinatario(destinatario):
    if destinatario in portas_cache:
        return portas_cache[destinatario]

    try:
        soquete_servidor.send(f"Solicitar IP,{destinatario}".encode('utf-8'))
        resposta = soquete_servidor.recv(1024).decode('utf-8')

        if resposta == "Destinatário não encontrado.":
            print(resposta)
            return None
        else:
            ip_destinatario, porta_destinatario = resposta.split(",")
            portas_cache[destinatario] = (ip_destinatario, int(porta_destinatario))
            return ip_destinatario, int(porta_destinatario)
    except Exception as e:
        print(f"Erro ao obter porta do destinatário: {e}")
        return None

def enviar_mensagem(destinatario, mensagem):
    if destinatario in conexoes_persistentes:
        soquete_destinatario = conexoes_persistentes[destinatario]
    else:
        ip_porta = obter_porta_destinatario(destinatario)
        if not ip_porta:
            print(f"Não foi possível obter porta para {destinatario}")
            return

        ip_destinatario, porta_destinatario = ip_porta
        try:
            soquete_destinatario = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            soquete_destinatario.connect((ip_destinatario, porta_destinatario))
            conexoes_persistentes[destinatario] = soquete_destinatario
        except Exception as e:
            print(f"Erro ao conectar ao destinatário: {e}")
            return

    try:
        soquete_destinatario.send(f"{nome}: {mensagem}".encode('utf-8'))
        # Armazena a mensagem enviada na conversa
        with lock:
            if destinatario not in conversas:
                conversas[destinatario] = []
            conversas[destinatario].append(f"Eu: {mensagem}")
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")
        # Se falhar, tenta remover a conexão e reenvia
        if destinatario in conexoes_persistentes:
            conexoes_persistentes[destinatario].close()
            del conexoes_persistentes[destinatario]
        enviar_mensagem(destinatario, mensagem)

def obter_lista_usuarios():
    try:
        soquete_servidor.send("Solicitar todos IPs".encode('utf-8'))
        resposta = soquete_servidor.recv(1024).decode('utf-8')
        return resposta.splitlines()
    except Exception as e:
        print(f"Erro ao obter lista de usuários: {e}")
        return []

def exibir_menu():
    while True:
        limpar_console()
        print("Selecione o destinatário para enviar a mensagem:\n")
        usuarios = obter_lista_usuarios()
        if usuarios:
            for idx, usuario in enumerate(usuarios, start=1):
                nome_cliente = usuario.split(":")[0]
                print(f"{idx} - {nome_cliente}")
            print(f"{len(usuarios) + 1} - Atualizar")
            print(f"{len(usuarios) + 2} - Sair")
        else:
            print("Nenhum outro usuário conectado.")
            print("1 - Atualizar")
            print("2 - Sair")

        opcao = input("\nEscolha uma opção: ")

        if opcao.isdigit() and 1 <= int(opcao) <= len(usuarios):
            selecionar_conversa(usuarios[int(opcao) - 1].split(":")[0])
        elif opcao == str(len(usuarios) + 1):
            continue
        elif opcao == str(len(usuarios) + 2):
            soquete_servidor.close()
            if soquete_local:
                soquete_local.close()
            for conn in conexoes_persistentes.values():
                conn.close()
            sys.exit()
        else:
            print("Opção inválida. Tente novamente.")

def selecionar_conversa(destinatario):
    global conversa_atual
    conversa_atual = destinatario

    while True:
        limpar_console()
        print(f"Conversa com {destinatario}:")
        if destinatario in conversas:
            for msg in conversas[destinatario]:
                print(msg)
        else:
            print("Nenhuma mensagem ainda.")

        mensagem = input("\nDigite sua mensagem (ou 'SAIR' para voltar ao menu): ")
        if mensagem.upper() == 'SAIR':
            break
        enviar_mensagem(destinatario, mensagem)

if __name__ == "__main__":
    iniciar_soquete_local()
    exibir_menu()
