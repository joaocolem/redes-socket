import socket
import threading
import sys

host_servidor = '127.0.0.1'
porta_servidor = 5000

soquete_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soquete_servidor.connect((host_servidor, porta_servidor))

nome = input("Escreva seu nome: ")
soquete_servidor.send(nome.encode('utf-8'))

mensagens_recebidas = {}

def obter_porta_local():
    soquete_servidor.send(f"Solicitar IP,{nome}".encode('utf-8'))
    resposta = soquete_servidor.recv(1024).decode('utf-8')
    if resposta:
        b, porta_local = resposta.split(",")
        return int(porta_local)
    else:
        raise Exception("Não foi possível obter a porta local.")

def receber_conexoes():
    soquete_ouvinte = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    porta_local = obter_porta_local()
    soquete_ouvinte.bind((host_servidor, porta_local))
    soquete_ouvinte.listen(5) 
    while True:
        conexao, endereco = soquete_ouvinte.accept()
        threading.Thread(target=ouvir_mensagens, args=(conexao,)).start()

def ouvir_mensagens(conexao):
    while True:
        try:
            mensagem = conexao.recv(1024).decode('utf-8')
            if mensagem:
                remetente, conteudo = mensagem.split(": ", 1)
                if remetente not in mensagens_recebidas:
                    mensagens_recebidas[remetente] = []
                mensagens_recebidas[remetente].append(conteudo)
            else:
                break
        except Exception as e:
            print(f"Erro ao receber mensagem: {e}")
            break
    conexao.close()

def enviar_mensagem(destinatario, mensagem):
    soquete_servidor.send(f"Solicitar IP,{destinatario}".encode('utf-8'))
    resposta = soquete_servidor.recv(1024).decode('utf-8')
    
    if resposta == "Destinatário não encontrado.":
        print(resposta)
    else:
        ip_destinatario, porta_destinatario = resposta.split(",")
        try:
            soquete_destinatario = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            soquete_destinatario.connect((ip_destinatario, int(porta_destinatario)))
            soquete_destinatario.send(f"{nome}: {mensagem}".encode('utf-8'))
            soquete_destinatario.close()
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")

def menu():
    while True:
        print("\nMenu:")
        print("1 - Enviar mensagem")
        print("2 - Ver mensagens recebidas")
        print("3 - Sair")
        opcao = input("Escolha uma opção: ")
        
        if opcao == '1':
            destinatario = input("Digite o nome do destinatário: ")
            mensagem = input("Digite a mensagem: ")
            enviar_mensagem(destinatario, mensagem)
        elif opcao == '2':
            if not mensagens_recebidas:
                print("Nenhuma mensagem recebida.")
                continue
            print("Mensagens recebidas:")
            for remetente, mensagens in mensagens_recebidas.items():
                print(f"\nDe {remetente}:")
                for msg in mensagens:
                    print(f"  {msg}")
        elif opcao == '3':
            soquete_servidor.close()
            sys.exit()
        else:
            print("Opção inválida.")

# Inicia o servidor de escuta em uma thread separada
threading.Thread(target=receber_conexoes, daemon=True).start()

menu()
