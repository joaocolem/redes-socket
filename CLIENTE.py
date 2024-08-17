import socket
import threading
import sys

host_servidor = '127.0.0.1'
porta_servidor = 5000

# Conectando ao servidor central
soquete_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soquete_servidor.connect((host_servidor, porta_servidor))

nome = input("Escreva seu nome: ")
soquete_servidor.send(nome.encode('utf-8'))

# Dicionário para armazenar mensagens recebidas
mensagens_recebidas = {}

def ouvir_mensagens():
    while True:
        try:
            mensagem = soquete_servidor.recv(1024).decode('utf-8')
            if mensagem:
                remetente, conteudo = mensagem.split(": ", 1)
                if remetente not in mensagens_recebidas:
                    mensagens_recebidas[remetente] = []
                mensagens_recebidas[remetente].append(conteudo)
        except:
            print("Conexão perdida com o servidor.")
            break

def enviar_mensagem(destinatario, mensagem):
    soquete_servidor.send(f"Solicitar IP,{destinatario}".encode('utf-8'))
    resposta = soquete_servidor.recv(1024).decode('utf-8')
    print(resposta)
    
    if resposta == "Destinatário não encontrado.":
        print(resposta)
    else:
        ip_destinatario, porta_destinatario = resposta.split(",")
        
        soquete_destinatario = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soquete_destinatario.connect((ip_destinatario, int(porta_destinatario)))
        soquete_destinatario.send(f"{nome}: {mensagem}".encode('utf-8'))
        soquete_destinatario.close()

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

threading.Thread(target=ouvir_mensagens, daemon=True).start()
menu()
