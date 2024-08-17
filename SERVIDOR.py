import socket
import threading
import time

host = '127.0.0.1'
porta = 5000
soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
origem = (host, porta)
soquete.bind(origem)
soquete.listen(5)

clientes_conectados = {}

def verificar_clientes_periodicamente():
    while True:
        print("Verificando clientes conectados...")
        for nome, info in list(clientes_conectados.items()):
            try:
                soquete_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                soquete_cliente.connect((info['ip'], info['porta']))
                soquete_cliente.close()
            except:
                print(f"Cliente {nome} desconectado.")
                del clientes_conectados[nome]
        time.sleep(30)  # Verifica a cada 30 segundos

def service(conexao, cliente):
    print('Conectado por', cliente)
    nome = conexao.recv(1024).decode('utf-8')
    clientes_conectados[nome] = {'ip': cliente[0], 'porta': cliente[1]}

    while True:
        mensagem = conexao.recv(1024).decode('utf-8')
        if not mensagem:
            break
        print(f"Cliente {cliente[0]}:{cliente[1]} Enviou: {mensagem}")
        codigo, destinatario_hash, conteudo = mensagem.split(",", 2)

        if codigo == "1":
            if destinatario_hash:
                if destinatario_hash in clientes_conectados:
                    ip_destinatario = clientes_conectados[destinatario_hash]['ip']
                    porta_destinatario = clientes_conectados[destinatario_hash]['porta']
                    soquete_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    soquete_cliente.connect((ip_destinatario, porta_destinatario))
                    soquete_cliente.send(f"{nome},{conteudo}".encode('utf-8'))
                    soquete_cliente.close()
                    conexao.send("Mensagem enviada ao destinatário.".encode('utf-8'))
                else:
                    conexao.send("Destinatário não encontrado.".encode('utf-8'))
            else:
                for cliente_nome, info in clientes_conectados.items():
                    if cliente_nome != nome:
                        soquete_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        soquete_cliente.connect((info['ip'], info['porta']))
                        soquete_cliente.send(f"{nome},{conteudo}".encode('utf-8'))
                        soquete_cliente.close()
                conexao.send("Mensagem enviada para todos os clientes.".encode('utf-8'))

        elif codigo == "3":
            conexao.send("Conexão encerrada.".encode('utf-8'))
            break

    del clientes_conectados[nome]
    conexao.close()

# Inicia a thread para verificar clientes periodicamente
threading.Thread(target=verificar_clientes_periodicamente, daemon=True).start()

while True:
    conexao, cliente = soquete.accept()
    cliente_thread = threading.Thread(target=service, args=(conexao, cliente))
    cliente_thread.start()
