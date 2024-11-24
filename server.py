import socket
import zlib

HOST = '0.0.0.0'
PORT = 5000
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

print(f"Server listening on {HOST}:{PORT}")

while True:
    data, addr = server_socket.recvfrom(20480)
    
    if len(data) > 0:
        try:
            data = zlib.decompress(data)
        except Exception as e:
            print(f"Decompression failed: {e}")
        
        try:
            compressed_data = zlib.compress(data)
            server_socket.sendto(compressed_data, addr)
        except Exception as e:
            print(f"Failed to send data back to {addr}: {e}")