import socket
import threading
import pyaudio
import zlib

CHUNK = 3072
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
output = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)

SERVER = '164.92.237.144'
PORT = 5000
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind(('', 0))

def send_audio():
    while True:
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            if len(data) > 0:
                compressed_data = zlib.compress(data)
                client_socket.sendto(compressed_data, (SERVER, PORT))
        except Exception as e:
            print(f"Send Audio Error: {e}")

def receive_audio():
    while True:
        try:
            data, _ = client_socket.recvfrom(20480)
            if len(data) > 0:
                try:
                    decompressed_data = zlib.decompress(data)
                    output.write(decompressed_data)
                except Exception as e:
                    print(f"Decompression failed: {e}")
        except Exception as e:
            print(f"Receive Audio Error: {e}")

threading.Thread(target=send_audio, daemon=True).start()
threading.Thread(target=receive_audio, daemon=True).start()

try:
    while True:
        pass
except KeyboardInterrupt:
    print("Exiting...")
    client_socket.close()
    stream.close()
    audio.terminate()