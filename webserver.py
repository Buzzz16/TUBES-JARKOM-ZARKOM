import socket
import threading
import os
from datetime import datetime

TCP_PORT = 8000
UDP_PORT = 9000
HOST = '0.0.0.0'

# Kamus MIME Type untuk mengenali jenis file
MIME_TYPES = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.ico': 'image/x-icon'
}

def handle_tcp_client(client_socket, addr):
    try:
        request = client_socket.recv(4096).decode('utf-8', errors='ignore')
        if not request:
            return

        headers = request.split('\r\n')
        first_line = headers[0].split()
        if len(first_line) < 2:
            return
            
        method, path = first_line[0], first_line[1]
        
        # Jika hanya request '/', arahkan ke index.html
        if path == '/': 
            path = '/index.html'
            
        # Mengamankan path dan menghapus '/' di awal agar bisa dibaca OS lokal
        filepath = '.' + path 

        # Menentukan Content-Type berdasarkan ekstensi file
        ext = os.path.splitext(filepath)[1].lower()
        content_type = MIME_TYPES.get(ext, 'application/octet-stream') # Default jika tidak dikenali

        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            
            # HTTP 200 OK
            response_header = "HTTP/1.1 200 OK\r\n"
            response_header += f"Content-Type: {content_type}\r\n"
            response_header += f"Content-Length: {len(content)}\r\n\r\n"
            
            client_socket.sendall(response_header.encode('utf-8') + content)
            print(f"[TCP LOG] {datetime.now().strftime('%H:%M:%S')} | {addr[0]} | {path} | 200 OK")

        except FileNotFoundError:
            # Menggunakan file 404 dari folder status jika ada, jika tidak pakai default
            error_path = './status/404.html'
            if os.path.exists(error_path):
                with open(error_path, 'rb') as f:
                    error_msg = f.read()
            else:
                error_msg = b"<h1>404 Not Found</h1>"
                
            response_header = "HTTP/1.1 404 Not Found\r\n"
            response_header += "Content-Type: text/html\r\n\r\n"
            client_socket.sendall(response_header.encode('utf-8') + error_msg)
            print(f"[TCP LOG] {datetime.now().strftime('%H:%M:%S')} | {addr[0]} | {path} | 404 Not Found")

    except Exception as e:
        print(f"Error handling TCP client: {e}")
    finally:
        client_socket.close()

def start_tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, TCP_PORT))
    server.listen(5)
    print(f"[*] TCP Web Server berjalan di port {TCP_PORT}")
    
    while True:
        client, addr = server.accept()
        threading.Thread(target=handle_tcp_client, args=(client, addr)).start()

def start_udp_server():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((HOST, UDP_PORT))
    print(f"[*] UDP Echo Server berjalan di port {UDP_PORT}")
    
    while True:
        data, addr = udp_socket.recvfrom(1024)
        udp_socket.sendto(data, addr)

if __name__ == "__main__":
    threading.Thread(target=start_tcp_server).start()
    threading.Thread(target=start_udp_server).start()