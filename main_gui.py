import flet as ft
import speech_recognition as sr
from commands import run_command

def main(page: ft.Page):
    page.title = "Clap Assistant Pro"
    page.theme_mode = "dark"
    page.window_width = 500
    page.window_height = 600

    output = ft.Text("👋 Pronto para receber comandos.")
    command_box = ft.TextField(label="Digite um comando (ex: abrir vscode)", width=400, autofocus=True)

    def execute_command(cmd):
        response = run_command(cmd)
        output.value = response
        page.update()

    def handle_text_command(e):
        cmd = command_box.value.strip()
        if cmd:
            execute_command(cmd)
            command_box.value = ""
            page.update()

    def handle_voice_command(e):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            output.value = "🎙️ Ouvindo..."
            page.update()
            audio = recognizer.listen(source)
        try:
            cmd = recognizer.recognize_google(audio, language="pt-BR")
            output.value = f"🎧 Você disse: {cmd}"
            page.update()
            execute_command(cmd)
        except Exception as err:
            output.value = f"❌ Erro: {err}"
            page.update()

    page.add(
        ft.Column(
            [
                ft.Text("🤖 Clap Assistant Pro", size=24, weight="bold"),
                command_box,
                ft.Row(
                    [
                        ft.ElevatedButton("Enviar", on_click=handle_text_command),
                        ft.ElevatedButton("🎤 Falar", on_click=handle_voice_command),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Divider(),
                output,
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=20,
        )
    )

ft.app(target=main)
