import socket
import time

PROXY_IP = '127.0.0.1' # Ganti dengan IP Proxy saat pakai 3 laptop
PROXY_PORT = 8080

WEBSERVER_IP = '127.0.0.1' # Ganti dengan IP Web Server saat pakai 3 laptop
UDP_PORT = 9000

CLIENT_ID = "babas"

def test_tcp_http(filename="/index.html"):
    print(f"\n[Client: {CLIENT_ID}] --- Memulai HTTP TCP Request ke Proxy ({PROXY_IP}:{PROXY_PORT}) ---")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((PROXY_IP, PROXY_PORT))
        request = f"GET {filename} HTTP/1.1\r\nHost: {PROXY_IP}\r\nConnection: close\r\n\r\n"
        client.sendall(request.encode('utf-8'))
        
        response = b""
        while True:
            data = client.recv(4096)
            if not data: break
            response += data
            
        print("\n[Respon dari Server/Proxy]:")
        print(response.decode('utf-8', errors='ignore')[:500] + "...\n")
        print(f"[Client: {CLIENT_ID}] Koneksi TCP ditutup dengan sukses.")
    except Exception as e:
        print(f"[Client: {CLIENT_ID}] Gagal koneksi HTTP: {e}")
    finally:
        client.close()

def test_udp_qos():
    print(f"\n[Client: {CLIENT_ID}] --- Memulai UDP QoS Pinger ke Web Server ({WEBSERVER_IP}:{UDP_PORT}) ---")
    udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_client.settimeout(1.0) 
    
    rtts = []
    lost_packets = 0
    jitters = []
    
    for i in range(1, 11):
        send_time = time.time()
        message = f"Ping {i} {send_time}".encode('utf-8')
        
        try:
            udp_client.sendto(message, (WEBSERVER_IP, UDP_PORT))
            data, server = udp_client.recvfrom(1024)
            recv_time = time.time()
            
            rtt = (recv_time - send_time) * 1000
            rtts.append(rtt)
            
            if len(rtts) > 1:
                jitter = abs(rtts[-1] - rtts[-2])
                jitters.append(jitter)
                
            print(f"[{CLIENT_ID}] Balasan dari {server[0]}: seq={i} time={rtt:.2f} ms")
        except socket.timeout:
            print(f"[{CLIENT_ID}] Request timed out (seq={i})")
            lost_packets += 1

    print(f"\n[Client: {CLIENT_ID}] --- Statistik QoS UDP ---")
    if rtts:
        print(f"Min RTT   : {min(rtts):.2f} ms")
        print(f"Max RTT   : {max(rtts):.2f} ms")
        print(f"Avg RTT   : {sum(rtts)/len(rtts):.2f} ms")
    if jitters:
        print(f"Avg Jitter: {sum(jitters)/len(jitters):.2f} ms")
    else:
        print("Avg Jitter: 0 ms")
        
    loss_percent = (lost_packets / 10) * 100
    print(f"Packet Loss: {loss_percent}%")

if __name__ == "__main__":
    print(f"=== Terminal Klien ({CLIENT_ID}) ===")
    print("Pilih mode pengujian jaringan:")
    print("1. Uji TCP & HTTP (Ambil data web via Proxy)")
    print("2. Uji UDP (QoS Ping langsung ke Server)")
    print("3. Uji Keduanya")
    
    pilihan = input(f"[{CLIENT_ID}] Masukkan pilihan (1/2/3): ")
    
    if pilihan == '1':
        test_tcp_http()
    elif pilihan == '2':
        test_udp_qos()
    elif pilihan == '3':
        test_tcp_http()
        time.sleep(1) # Memberi jeda agar log mudah dibaca
        test_udp_qos()
    else:
        print(f"[{CLIENT_ID}] Pilihan tidak valid, program dihentikan.")