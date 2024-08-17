import socket
import threading

host = '127.0.0.1'
porta = 5000
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind((host, porta))
servidor.listen(5)

clientes_conectados = {}

def handle_client(conexao, endereco):
    print(f'Cliente conectado: {endereco}')
    
    nome = conexao.recv(1024).decode('utf-8')
    clientes_conectados[nome] = endereco
    print(f'{nome} registrado com IP {endereco[0]} e porta {endereco[1]}')

    while True:
        mensagem = conexao.recv(1024).decode('utf-8')
        if not mensagem:
            break
        
        if mensagem.startswith("Solicitar IP,"):
            nome_destinatario = mensagem.split(",")[1]
            if nome_destinatario in clientes_conectados:
                ip_destinatario, porta_destinatario = clientes_conectados[nome_destinatario]
                resposta = f"{ip_destinatario},{porta_destinatario}"
                conexao.send(resposta.encode('utf-8'))
            else:
                conexao.send("Destinatário não encontrado.".encode('utf-8'))
                
        elif mensagem == "Solicitar todos IPs":
            resposta = ""
            for nome_cliente, (ip_cliente, porta_cliente) in clientes_conectados.items():
                resposta += f"{nome_cliente}: {ip_cliente}:{porta_cliente}\n"
            if resposta:
                conexao.send(resposta.encode('utf-8'))
            else:
                conexao.send("Nenhum cliente conectado.".encode('utf-8'))
            
    conexao.close()
    del clientes_conectados[nome]
    print(f'Cliente {nome} desconectado.')

while True:
    conexao, endereco = servidor.accept()
    threading.Thread(target=handle_client, args=(conexao, endereco)).start()
