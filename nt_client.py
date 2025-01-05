import time
from pynput import keyboard
import socket
import threading
import pyaudio
import zlib
import numpy as np

CHUNK = 3072
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
AMPLIFICATION_FACTOR = 2.5
PUSH_TO_TALK_KEY = 'x'
PUSH_TO_TALK_ACTIVE = True

audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
output = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)

SERVER = '165.227.134.14'
PORT = 5000
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind(('', 0))

print("Client started, binding socket...")

is_sending_audio = False
is_sending_audio_lock = threading.Lock()

def on_press(key):
    global is_sending_audio
    if hasattr(key, 'char') and key.char == PUSH_TO_TALK_KEY:
        with is_sending_audio_lock:
            is_sending_audio = True

def on_release(key):
    global is_sending_audio
    if hasattr(key, 'char') and key.char == PUSH_TO_TALK_KEY:
        with is_sending_audio_lock:
            is_sending_audio = False
    if key == keyboard.Key.esc:
        return False

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

def send_audio():
    while True:
        if PUSH_TO_TALK_ACTIVE:
            with is_sending_audio_lock:
                if not is_sending_audio:
                    time.sleep(0.01)
                    continue
        try:
            start_time = time.time()
            data = stream.read(CHUNK, exception_on_overflow=False)
            if len(data) > 0:
                compressed_data = zlib.compress(data)
                client_socket.sendto(compressed_data, (SERVER, PORT))
            elapsed_time = time.time() - start_time
            time.sleep(max(0, 0.01 - elapsed_time))
        except Exception as e:
            print(f"Send Audio Error: {e}")


def receive_audio():
    while True:
        try:
            data, _ = client_socket.recvfrom(20480)
            if len(data) > 0:
                try:
                    decompressed_data = zlib.decompress(data)
                    audio_data = np.frombuffer(decompressed_data, dtype=np.int16)
                    amplified_data = np.clip(audio_data * AMPLIFICATION_FACTOR, -32768, 32767).astype(np.int16)
                    output.write(amplified_data.tobytes())
                    print("Received and playing audio...")
                except Exception as e:
                    print(f"Decompression or amplification failed: {e}")
        except Exception as e:
            print(f"Receive Audio Error: {e}")

def manage_threads(target):
    while True:
        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        thread.join()
        print(f"Thread {target.__name__} has stopped unexpectedly. Restarting...")

print("Starting audio send/receive threads...")
threading.Thread(target=manage_threads, args=(send_audio,), daemon=True).start()
threading.Thread(target=manage_threads, args=(receive_audio,), daemon=True).start()

try:
    print("Client is running. Hold 'x' to send audio, press Ctrl+C to exit.")
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Exiting...")
    client_socket.close()
    stream.close()
    audio.terminate()
    print("Client closed successfully.")