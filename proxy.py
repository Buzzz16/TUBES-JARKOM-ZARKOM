import socket
import threading
import os
import time

PROXY_PORT = 8080
PROXY_HOST = '0.0.0.0'
WEBSERVER_HOST = '10.98.145.21' # Sesuaikan dengan IP Web Server jika beda perangkat
WEBSERVER_PORT = 8000

CACHE_DIR = "./cache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def handle_client(client_socket, addr):
    start_time = time.time()
    try:
        request = client_socket.recv(4096)
        if not request:
            client_socket.close()
            return
            
        req_str = request.decode('utf-8')
        first_line = req_str.split('\r\n')[0]
        url_path = first_line.split()[1]
        
        # Penamaan file cache sederhana berdasarkan URL (ubah / jadi _)
        cache_filename = url_path.replace('/', '_')
        if cache_filename == '_': cache_filename = '_index.html'
        cache_path = os.path.join(CACHE_DIR, cache_filename)

        # Cek apakah ada di cache
        if os.path.exists(cache_path):
            # CACHE HIT
            with open(cache_path, 'rb') as f:
                response = f.read()
            client_socket.sendall(response)
            elapsed_time = (time.time() - start_time) * 1000
            print(f"[PROXY LOG] {addr[0]} | {url_path} | HIT | {elapsed_time:.2f} ms")
        else:
            # CACHE MISS - Teruskan ke Web Server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.settimeout(5.0) # Timeout 5 detik
            
            try:
                server_socket.connect((WEBSERVER_HOST, WEBSERVER_PORT))
                server_socket.sendall(request)
                
                # Terima respon dari web server
                response = b""
                while True:
                    data = server_socket.recv(4096)
                    if not data: break
                    response += data
                
                # Simpan ke cache (hanya jika responsnya HTTP 200)
                if b"200 OK" in response:
                    with open(cache_path, 'wb') as f:
                        f.write(response)
                
                client_socket.sendall(response)
                elapsed_time = (time.time() - start_time) * 1000
                print(f"[PROXY LOG] {addr[0]} | {url_path} | MISS | {elapsed_time:.2f} ms")
                
            except socket.timeout:
                error_resp = "HTTP/1.1 504 Gateway Timeout\r\n\r\n<h1>504 Gateway Timeout</h1>"
                client_socket.sendall(error_resp.encode())
                print(f"[PROXY ERROR] 504 Gateway Timeout")
            except Exception as e:
                error_resp = "HTTP/1.1 502 Bad Gateway\r\n\r\n<h1>502 Bad Gateway</h1>"
                client_socket.sendall(error_resp.encode())
                print(f"[PROXY ERROR] 502 Bad Gateway: {e}")
            finally:
                server_socket.close()

    except Exception as e:
        print(f"Proxy error: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    proxy_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_server.bind((PROXY_HOST, PROXY_PORT))
    proxy_server.listen(10)
    print(f"[*] Proxy Server berjalan di port {PROXY_PORT}")
    
    while True:
        client, addr = proxy_server.accept()
        # Threading per koneksi
        threading.Thread(target=handle_client, args=(client, addr)).start()