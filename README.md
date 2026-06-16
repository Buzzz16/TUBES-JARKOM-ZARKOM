*** End Patch
# Zarkom Project

## Overview
Zarkom is a simple proxy server and web server application designed to facilitate HTTP requests and responses between clients and web servers. This project demonstrates the use of sockets in Python to create a functional proxy and web server.

## Features
- **Proxy Server**: Handles incoming requests from clients and forwards them to the appropriate web server.
- **Web Server**: Serves static files to clients, including HTML, CSS, and images.
- **Caching**: Implements a basic caching mechanism to store frequently requested files.

## Components
### 1. Client
The client connects to the proxy server and sends HTTP requests. It is designed to initiate requests for specific files and handle responses from the proxy.

```python
import socket
import time

PROXY_IP = '127.0.0.1'
PROXY_PORT = 8080

CLIENT_ID = "babas"

def test_tcp_http(filename="/index.html"):
    # Initiates HTTP TCP Request to Proxy
    ...
```

### 2. Proxy
The proxy server listens for incoming connections from clients, processes their requests, and forwards them to the web server. It also manages caching for efficiency.

```python
import socket
import threading
import os

PROXY_PORT = 8080
PROXY_HOST = '0.0.0.0'

def handle_client(client_socket, addr):
    # Handles client requests
    ...
```

### 3. Web Server
The web server serves static files to clients. It recognizes different MIME types to ensure proper file handling and response formatting.

```python
import socket
import threading
from datetime import datetime

TCP_PORT = 8000
HOST = '0.0.0.0'

MIME_TYPES = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css',
    ...
}
```

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Buzzz16/TUBES-JARKOM-ZARKOM.git
   ```
2. Navigate to the project directory:
   ```bash
   cd TUBES-JARKOM-ZARKOM
   ```
3. Run the web server:
   ```bash
   python webserver.py
   ```
4. Run the proxy server:
   ```bash
   python proxy.py
   ```
5. Run the client:
   ```bash
   python client.py
   ```

## Usage
- Open your browser and navigate to `http://127.0.0.1:8080` to interact with the proxy server.
- The client will initiate requests to the proxy, which will then fetch the requested resources from the web server.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

**Enjoy using Zarkom!**
