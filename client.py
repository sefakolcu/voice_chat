import time
from pynput import keyboard
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

SERVER = '165.227.134.14'
PORT = 5000
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind(('', 0))

print("Client started, binding socket...")

# This flag will control whether audio is sent or not
is_sending_audio_event = threading.Event()

def on_press(key):
    if hasattr(key, 'char') and key.char == 'x':
        is_sending_audio_event.set()  # Start sending audio

def on_release(key):
    if hasattr(key, 'char') and key.char == 'x':
        is_sending_audio_event.clear()  # Stop sending audio
    if key == keyboard.Key.esc:
        # Stop listener
        return False

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

def send_audio():
    while True:
        is_sending_audio_event.wait()  # Wait for the 'x' key to be pressed before sending audio
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            if len(data) > 0:
                compressed_data = zlib.compress(data)
                client_socket.sendto(compressed_data, (SERVER, PORT))
        except Exception as e:
            print(f"Send Audio Error: {e}")
        time.sleep(0.01)  # A small delay to reduce CPU load when waiting for the keypress

def receive_audio():
    while True:
        try:
            data, _ = client_socket.recvfrom(20480)
            if len(data) > 0:
                try:
                    decompressed_data = zlib.decompress(data)
                    output.write(decompressed_data)
                    print("Received and playing audio...")
                except Exception as e:
                    print(f"Decompression failed: {e}")
        except Exception as e:
            print(f"Receive Audio Error: {e}")

print("Starting audio send/receive threads...")
threading.Thread(target=send_audio, daemon=True).start()
threading.Thread(target=receive_audio, daemon=True).start()

try:
    print("Client is running. Hold 'x' to send audio, press Ctrl+C to exit.")
    while True:
        time.sleep(0.1)  # Reduce CPU load in the main loop
except KeyboardInterrupt:
    print("Exiting...")
    client_socket.close()
    stream.close()
    audio.terminate()
    print("Client closed successfully.")
