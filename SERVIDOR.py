import socket
import threading
import time

host = '127.0.0.1'
porta = 5000
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind((host, porta))
servidor.listen(5)

clientes_conectados = {}
lock = threading.Lock()

def handle_client(conexao, endereco):
    print(f'Cliente conectado: {endereco}')
    
    nome = conexao.recv(1024).decode('utf-8')
    
    with lock:
        clientes_conectados[nome] = (conexao, endereco)
    
    print(f'{nome} registrado com IP {endereco[0]} e porta {endereco[1]}')

    try:
        while True:
            mensagem = conexao.recv(1024).decode('utf-8')
            if not mensagem:
                break
            
            if mensagem.startswith("Solicitar IP,"):
                nome_destinatario = mensagem.split(",")[1]
                with lock:
                    if nome_destinatario in clientes_conectados:
                        ip_destinatario, porta_destinatario = clientes_conectados[nome_destinatario][1]
                        resposta = f"{ip_destinatario},{porta_destinatario}"
                        conexao.send(resposta.encode('utf-8'))
                    else:
                        conexao.send("Destinatário não encontrado.".encode('utf-8'))
                        
            elif mensagem == "Solicitar todos IPs":
                resposta = ""
                with lock:
                    for nome_cliente, (conexao_cliente, endereco_cliente) in clientes_conectados.items():
                        ip_cliente, porta_cliente = endereco_cliente
                        resposta += f"{nome_cliente}: {ip_cliente}:{porta_cliente}\n"
                if resposta:
                    conexao.send(resposta.encode('utf-8'))
                else:
                    conexao.send("Nenhum cliente conectado.".encode('utf-8'))
    except:
        pass
    finally:
        with lock:
            del clientes_conectados[nome]
        conexao.close()
        print(f'Cliente {nome} desconectado.')

def monitorar_clientes():
    while True:
        with lock:
            desconectar = []
            for nome, (conexao, endereco) in list(clientes_conectados.items()):
                try:
                    conexao.send(b'')
                except:
                    desconectar.append(nome)
            for nome in desconectar:
                del clientes_conectados[nome]
                print(f'Cliente {nome} desconectado devido a inatividade.')
        time.sleep(5)  # Verifica os clientes a cada 5 segundos

# Inicia a thread de monitoramento
threading.Thread(target=monitorar_clientes, daemon=True).start()

while True:
    conexao, endereco = servidor.accept()
    threading.Thread(target=handle_client, args=(conexao, endereco)).start()
