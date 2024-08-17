import socket
import json
import hashlib
import threading

host = '127.0.0.1'
porta = 5000
soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
destino = (host, porta)
soquete.connect(destino)

nome = input("Escreva seu nome: ")
soquete.send(nome.encode('utf-8'))

conexoes_anteriores = {}

def calcular_hash(nome_destinatario):
    return hashlib.sha256(nome_destinatario.encode('utf-8')).hexdigest()

def receber_mensagens():
    while True:
        mensagem = soquete.recv(1024).decode('utf-8')
        print(f"\nNova mensagem recebida: {mensagem}")

def menu():
    print("\nMenu:")
    print("1 - Enviar mensagem")
    print("2 - Sair")

threading.Thread(target=receber_mensagens, daemon=True).start()

while True:
    menu()
    opcao = input("Escolha uma opção: ")

    if opcao == "1":
        destinatario = input("Digite o nome do destinatário: ")
        hash_destinatario = calcular_hash(destinatario)

        if hash_destinatario not in conexoes_anteriores:
            soquete.send(f"Solicitar IP,{destinatario}".encode('utf-8'))
            resposta = soquete.recv(1024).decode('utf-8')
            if resposta == "Destinatário não encontrado.":
                print(resposta)
                continue
            else:
                ip_destinatario, porta_destinatario = resposta.split(",")
                conexoes_anteriores[hash_destinatario] = (ip_destinatario, int(porta_destinatario))

        mensagem = input("Escreva sua mensagem: ")
        pacote = f"1,{hash_destinatario},{mensagem}"
        soquete.send(pacote.encode('utf-8'))

    elif opcao == "2":
        soquete.send("3".encode('utf-8'))
        print("Conexão encerrada.")
        break

    else:
        print("Opção inválida. Tente novamente.")

soquete.close()
