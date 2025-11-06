import os
import subprocess
import platform

def run_command(command: str):
    command = command.lower().strip()

    if "vscode" in command:
        return open_vscode()
    elif "navegador" in command or "chrome" in command:
        return open_browser()
    elif "bloco" in command or "notas" in command:
        return open_notepad()
    elif "fechar" in command:
        return close_all()
    else:
        return f"❓ Comando não reconhecido: {command}"

def open_vscode():
    try:
        if platform.system() == "Windows":
            subprocess.Popen(["code"])
        else:
            subprocess.Popen(["code"])
        return "🧠 VSCode aberto com sucesso!"
    except Exception as e:
        return f"❌ Erro ao abrir VSCode: {e}"

def open_browser():
    try:
        if platform.system() == "Windows":
            os.startfile("https://www.google.com")
        else:
            subprocess.Popen(["xdg-open", "https://www.google.com"])
        return "🌐 Navegador aberto!"
    except Exception as e:
        return f"❌ Erro ao abrir navegador: {e}"

def open_notepad():
    try:
        if platform.system() == "Windows":
            subprocess.Popen(["notepad.exe"])
        else:
            subprocess.Popen(["gedit"])
        return "📝 Bloco de notas aberto!"
    except Exception as e:
        return f"❌ Erro ao abrir bloco de notas: {e}"

def close_all():
    try:
        if platform.system() == "Windows":
            os.system("taskkill /f /im code.exe")
            os.system("taskkill /f /im notepad.exe")
        return "🧹 Aplicações encerradas!"
    except Exception as e:
        return f"❌ Erro ao fechar: {e}"
