"""
clap_to_vscode.py - Assistente invisível de palmas 👏
----------------------------------------------------
Abre o Visual Studio Code quando detectar uma palma.
Roda em background, com logs leves e controle anti-duplicação.
"""

import sounddevice as sd
import numpy as np
import time
import subprocess
import os
import psutil
from datetime import datetime

# === CONFIGURAÇÕES ===
CLAP_THRESHOLD = 0.28
CLAP_COOLDOWN = 2.5
SAMPLERATE = 44100
CHUNK_DURATION = 0.1

LOG_PATH = os.path.join(os.getenv("TEMP"), "clap_to_vscode_log.txt")
VSCODE_PATHS = [
    r"C:\Users\dippf\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    r"C:\Program Files\Microsoft VS Code\Code.exe",
]

# === EVITAR DUPLICAÇÃO ===
for proc in psutil.process_iter(attrs=["pid", "cmdline"]):
    cmdline = " ".join(proc.info.get("cmdline") or [])
    if "clap_to_vscode" in cmdline and proc.pid != os.getpid():
        print("⚠️ Já existe uma instância rodando.")
        exit(0)

# === LOG ===
def log(msg: str):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now():%H:%M:%S}] {msg}\n")

log("🟢 Clap listener iniciado.")

last_clap_time = 0


def abrir_vscode():
    """Tenta abrir o VSCode."""
    for caminho in VSCODE_PATHS:
        if os.path.exists(caminho):
            subprocess.Popen([caminho])
            log("🚀 VS Code aberto com sucesso.")
            return
    log("❌ VSCode não encontrado.")


def callback(indata, frames, time_, status):
    """Callback de áudio — detecta palmas."""
    global last_clap_time
    volume = np.linalg.norm(indata)
    agora = time.time()

    if volume > CLAP_THRESHOLD and (agora - last_clap_time) > CLAP_COOLDOWN:
        last_clap_time = agora
        log(f"👏 Palma detectada! Volume={volume:.3f}")
        abrir_vscode()


def main():
    log("🎧 Escutando microfone...")
    try:
        with sd.InputStream(callback=callback, channels=1, samplerate=SAMPLERATE):
            while True:
                sd.sleep(int(CHUNK_DURATION * 1000))
    except Exception as e:
        log(f"❌ Erro: {e}")
        time.sleep(3)
        main()  # tenta reiniciar


if __name__ == "__main__":
    main()
