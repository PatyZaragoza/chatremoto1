import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

class ChatServer:
    def __init__(self, root):
        self.root = root
        self.root.title("Servidor de Chat")
        
        # Configuración de la interfaz gráfica
        tk.Label(root, text="Servidor de Chat").pack(pady=10)
        
        self.chat_display = scrolledtext.ScrolledText(root, state="normal", height=15, wrap="word")
        self.chat_display.pack(fill="both", padx=20, pady=10)
        self.chat_display.insert(tk.END, "Servidor listo para conectar.\n")
        
        self.host = '0.0.0.0'  # Escuchar en todas las interfaces
        self.port = 2222
        self.clients = []  # Lista para almacenar los sockets de los clientes

        self.start_server()

    def start_server(self):
        # Crear el socket del servidor
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)  # Escuchar hasta 5 conexiones
        self.chat_display.insert(tk.END, f"Servidor iniciado en {self.host}:{self.port}\n")
        threading.Thread(target=self.accept_clients, daemon=True).start()  # Iniciar el hilo para aceptar clientes

    def accept_clients(self):
        while True:
            client_socket, address = self.server_socket.accept()
            self.clients.append(client_socket)  # Agregar el nuevo cliente a la lista
            self.chat_display.insert(tk.END, f"Cliente conectado: {address}\n")
            threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()  # Manejar el cliente en un hilo

    def handle_client(self, client_socket):
        while True:
            try:
                mensaje = client_socket.recv(1024).decode("utf-8")
                if mensaje:
                    self.chat_display.insert(tk.END, f"Mensaje recibido: {mensaje}\n")
                    self.broadcast(mensaje, client_socket)  # Reenviar el mensaje a todos los clientes
                else:
                    break  # Salir si no hay mensaje
            except Exception as e:
                break  # Salir si ocurre un error

        client_socket.close()  # Cerrar el socket cuando el cliente se desconecta
        self.clients.remove(client_socket)  # Eliminar el cliente de la lista

    def broadcast(self, mensaje, sender_socket):
        for client in self.clients:
            if client != sender_socket:  # No enviar el mensaje al cliente que lo envió
                try:
                    client.send(mensaje.encode("utf-8"))  # Enviar el mensaje a otros clientes
                except Exception as e:
                    self.chat_display.insert(tk.END, f"Error al enviar a un cliente: {str(e)}\n")
                    client.close()  # Cerrar el socket si ocurre un error
                    self.clients.remove(client)  # Remover el cliente de la lista si se cierra

# Configuración del servidor
root = tk.Tk()
server = ChatServer(root)
root.mainloop()
