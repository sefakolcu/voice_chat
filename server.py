import socket
import zlib

HOST = '0.0.0.0'
PORT = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

print(f"Server listening on {HOST}:{PORT}")

clients = set()

while True:
    data, addr = server_socket.recvfrom(20480)

    if addr not in clients:
        clients.add(addr)
        print(f"New client connected: {addr}")

    if len(data) > 0:
        try:
            print(f"Received data from {addr}: {len(data)} bytes")
            data = zlib.decompress(data)
            print(f"Decompressed data from {addr}: {len(data)} bytes")
        except Exception as e:
            print(f"Decompression failed for {addr}: {e}")
            continue

        # Echo back to the sender (the client that sent the data)
        try:
            compressed_data = zlib.compress(data)
            server_socket.sendto(compressed_data, addr)  # Send back to the sender
            print(f"Echoed data back to {addr}: {len(compressed_data)} bytes")
        except Exception as e:
            print(f"Failed to send data back to {addr}: {e}")

        # Send the data to other clients
        for client in clients:
            if client != addr:
                try:
                    compressed_data = zlib.compress(data)
                    server_socket.sendto(compressed_data, client)
                    print(f"Sent data to {client}: {len(compressed_data)} bytes")
                except Exception as e:
                    print(f"Failed to send data to {client}: {e}")