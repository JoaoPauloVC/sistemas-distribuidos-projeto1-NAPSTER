import socket

#Classe Servidor que cumpre a todos os requisitos especificados no Projeto
class Server:
    def __init__(self, ip, porta):
        self.ip = ip
        self.porta = porta
        self.peers = {}  # Dicionário para armazenar informações dos pares (peer)

    def iniciar(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.ip, self.porta))
        server_socket.listen(5)
        print(f"Servidor iniciado em {self.ip}:{self.porta}")

        while True:
            peer_socket, client_address = server_socket.accept()
            self.resolve_requisicao_PEER(peer_socket, client_address)

    #Seção 4.a Recebe e responde Requisições dos Peers
    def resolve_requisicao_PEER(self, peer_socket, client_address):
        pedido = peer_socket.recv(1024).decode()
        pedido_inicio = pedido.split()
        peer_endereco = pedido_inicio[1].split(":")
        peer_ip = peer_endereco[0]
        peer_porta = peer_endereco[1]

        if len(pedido_inicio) > 0:
            requisicao = pedido_inicio[0]
            if requisicao == "JOIN":
                resposta = self.resolve_JOIN(pedido_inicio[1:])
                arquivos = " ".join(pedido_inicio[2:])
                print(f"Peer {peer_ip}:{peer_porta} adicionado com arquivos {arquivos}")
            elif requisicao == "SEARCH":
                resposta = self.resolve_SEARCH(pedido_inicio[2])
                print(f"Peer {peer_ip}:{peer_porta} solicitou arquivo {pedido_inicio[2]}")
            elif requisicao == "UPDATE":
                resposta = self.resolve_UPDATE(pedido_inicio[1])
            else:
                resposta = "Comando Inválido"
        else:
            resposta = "Requisição Vazia"

        peer_socket.sendall(resposta.encode())
        peer_socket.close()

    #Seção 4.b Requisição JOIN
    def resolve_JOIN(self, peer_info):
        # Processar informações do par e armazená-las
        # Exemplo: peer_info = ['PeerX', 'file1.mp4', 'file2.mp4']
        peer_nome = peer_info[0]
        peer_arquivos = peer_info[1:]

        peer_endereco = peer_nome.split(":")
        peer_ip = peer_endereco[0]
        peer_porta = int(peer_endereco[1])

        self.peers[(peer_ip, peer_porta)] = peer_arquivos

        return "JOIN_OK"

    #Seção 4.c Requisição SEARCH
    def resolve_SEARCH(self, nome_arquivo):
        # Procura peers que possuem o arquivo solicitado
        peers_com_arquivo = []
        for peer, arquivos in self.peers.items():
            if nome_arquivo in arquivos:
                peers_com_arquivo.append(peer)

        # Formata os pares de IP e Porta
        peers_formatados = [f"{ip}:{porta}" for ip, porta in peers_com_arquivo]

        return " ".join(peers_formatados)
    
    #Seção 4.d Requisição UPDATE
    def resolve_UPDATE(self, nome_arquivo):
        # Atualiza informações do peer após o download de um arquivo
        for peer, files in self.peers.items():
            if nome_arquivo not in files:
                self.peers[peer].append(nome_arquivo)

        return "UPDATE_OK"

#Seção 4.e Captura dos dados do Servidor através do teclado.
if __name__ == "__main__":
    server_ip = input("Servidor IP: ")
    server_port = int(input("Servidor Porta: "))

    server = Server(server_ip, server_port)
    server.iniciar()
