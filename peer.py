import os
import socket
import threading


#Classe Peer que cumpre a todos os requisitos especificados no Projeto
class Peer:
    def __init__(self, ip, porta, diretorio):
        self.ip = ip
        self.porta = porta
        self.diretorio = diretorio
        

    def iniciar(self):
        servidor_thread = threading.Thread(target=self.iniciar_peer_servidor)
        servidor_thread.start()
               
        while True:
            requisicao = input("Menu interativo:\n1. JOIN\n2. SEARCH\n3. DOWNLOAD\nDigite o número da sua escolha: ")
            # 4. EXIT\n 
            # Retirado pois não é o print "exatamente" igual ao especificado no projeto.

            if requisicao == "1":
                self.envia_JOIN()
            elif requisicao == "2":
                self.envia_SEARCH()
            elif requisicao == "3":
                self.envia_DOWNLOAD()
            # elif requisicao == "4":
            #     break
            else:
                print("Escolha Inválida. Tente Novamente.")

    #Seção 5.b Requisição JOIN
    def envia_JOIN(self):
        servidor_ip = input("Servidor IP: ")
        servidor_porta = int(input("Servidor Porta: "))

        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((servidor_ip, servidor_porta))

            requisicao_JOIN = f"JOIN {self.ip}:{self.porta} {self.get_nome_arquivo()}"
            peer_socket.sendall(requisicao_JOIN.encode())

            resposta = peer_socket.recv(1024).decode()
            if resposta == "JOIN_OK":
                print(f"Sou peer {self.ip}:{self.porta} com arquivos {self.get_nome_arquivo()}")
                self.envia_UPDATE(servidor_ip, servidor_porta)
            else:
                print("Falha no Registro com o Servidor")

            peer_socket.close()
        except Exception as e:
            print("Erro enquanto conectava com o servidor:", str(e))

    #Seção 5.c Requisição UPDATE
    def envia_UPDATE(self, servidor_ip, servidor_porta):
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((servidor_ip, servidor_porta))

            requisicao_UPDATE = f"UPDATE {self.ip}:{self.porta} {self.get_nome_arquivo()}"
            peer_socket.sendall(requisicao_UPDATE.encode())

            # resposta = peer_socket.recv(1024).decode()
            # if resposta == "UPDATE_OK":
            #     print("Atualização enviada com sucesso para o servidor")
            # else:
            #     print("Falha ao enviar atualização para o servidor")

            peer_socket.close()
        except Exception as e:
            print("Erro ao se conectar com o servidor:", str(e))
    
    # Retorna uma lista de nomes de arquivos presentes na pasta do peer
    def get_nome_arquivo(self):
        
        nome_arquivos = []

        try:
            with os.scandir(self.diretorio) as entries:
                for entry in entries:
                    if entry.is_file():
                        nome_arquivos.append(entry.name)
        except Exception as e:
            print("Erro ocorreu enquanto lia arquivos da pasta:", str(e))

        return " ".join(nome_arquivos)

    #Seção 5.d Requisição SEARCH
    def envia_SEARCH(self):
        nome_arquivo = input("Insira o nome do arquivo para buscar: ")

        try:
            servidor_ip = input("Servidor IP: ")
            servidor_porta = int(input("Servidor Porta: "))

            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((servidor_ip, servidor_porta))

            requisicao_SEARCH = f"SEARCH {self.ip}:{self.porta} {nome_arquivo}"
            peer_socket.sendall(requisicao_SEARCH.encode())

            resposta = peer_socket.recv(1024).decode()
            if resposta:
                peers_com_arquivo = resposta.split()
                print("peers com arquivo solicitado:", " ".join(peers_com_arquivo))
            else:
                print("Não há nenhum peer com este arquivo.")

            peer_socket.close()
        except Exception as e:
            print("Erro ao se conectar com o servidor:", str(e))

    #Seção 5.f Ainda precisa arrumar.
    def envia_DOWNLOAD(self):
        peer_ip = input("Peer IP: ")
        peer_porta = int(input("Peer Porta: "))
        nome_arquivo = input("Nome do arquivo para baixar: ")

        
        download_thread = threading.Thread(target=self.realizar_download, args=(peer_ip, peer_porta, nome_arquivo))
        download_thread.start()

    #Seção 5.g Ainda precisa arrumar.
    def realizar_download(self, peer_ip, peer_porta, nome_arquivo):
        try:
            
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            peer_socket.connect((peer_ip, peer_porta))

            requisicao_DOWNLOAD = f"DOWNLOAD {nome_arquivo}"
            peer_socket.sendall(requisicao_DOWNLOAD.encode())

            resposta = peer_socket.recv(1024).decode()
            if resposta.startswith("Arquivo Encontrado!"):
                self.receber_arquivo(peer_socket, nome_arquivo)
            elif resposta == "Arquivo não encontrado":
                print("Arquivo não encontrado no peer")
            else:
                print("Erro durante a transferência do arquivo")

            peer_socket.close()
        except ConnectionRefusedError:
            print("Conexão recusada. Verifique se o peer está em execução e a porta está correta.")
        except Exception as e:
            print("Erro ao conectar com o Peer:", str(e))
            
    #Seção 5.h
    def receber_arquivo(self, peer_socket, nome_arquivo):
        try:
            caminho_arquivo = os.path.join(self.diretorio, nome_arquivo)
            with open(caminho_arquivo, "wb") as arquivo:
                while True:
                    data = peer_socket.recv(1024)
                    if len(data) == 0:
                        break
                    arquivo.write(data)

            print(f"Arquivo {nome_arquivo} baixado com sucesso na pasta {self.diretorio}")
        except Exception as e:
            print("Erro enquanto recebia o download:", str(e))

    # Método para iniciar o servidor e lidar com as requisições de outros peers
    def iniciar_peer_servidor(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.ip, self.porta))
        server_socket.listen(5)

        while True:
            peer_socket, client_address = server_socket.accept()
            self.resolve_requisicao_PEER(peer_socket, client_address)

    # Método para resolver as requisições recebidas de outros peers
    def resolve_requisicao_PEER(self, peer_socket, client_address):
        try:
            requisicao = peer_socket.recv(1024).decode()
            if requisicao.startswith("DOWNLOAD"):
                self.enviar_arquivo(peer_socket, requisicao.split()[1])
            # Outras possíveis respostas a serem tratadas aqui

        except Exception as e:
            print("Erro ao resolver a requisição do Peer:", str(e))
        finally:
            peer_socket.close()

    def enviar_arquivo(self, peer_socket, nome_arquivo):
        try:
            caminho_arquivo = os.path.join(self.diretorio, nome_arquivo)
            with open(caminho_arquivo, "rb") as arquivo:
                for data in arquivo:
                    peer_socket.sendall(data)

            print(f"Arquivo {nome_arquivo} enviado para o Peer")
        except FileNotFoundError:
            peer_socket.sendall("Arquivo não encontrado".encode())
        except Exception as e:
            print("Erro durante o envio do arquivo para o Peer:", str(e))


#Seção 5.i Captura dos dados do Peer através do teclado.
if __name__ == "__main__":
    peer_ip = input("Peer IP: ")
    peer_porta = int(input("Peer Porta: "))
    #Atenção: O input abaixo é o caminho até o diretório do peer em questão.  Exemplo: /home/medicoes/Documents/UFABC)
    diretorio = input("Pasta onde os arquivos estão armazenados: ")

    peer = Peer(peer_ip, peer_porta, diretorio)
    peer.iniciar()
