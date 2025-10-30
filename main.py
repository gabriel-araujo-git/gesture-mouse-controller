import cv2
import numpy as np
import pyautogui
import time
from collections import deque
import pygetwindow as gw
import win32gui
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import Image, ImageFormat, solutions

# === CONFIGURAÇÕES ===
DEBUG = True
SMOOTHING_FRAMES = 5
CLICK_DIST = 25
RELEASE_DIST = 40
MOVE_DURATION = 0.03
INACTIVITY_TIMEOUT = 10

# === INICIALIZAÇÕES ===
model_path = "hand_landmarker.task"

BaseOptions = python.BaseOptions
VisionRunningMode = vision.RunningMode
HandLandmarker = vision.HandLandmarker
HandLandmarkerOptions = vision.HandLandmarkerOptions

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.IMAGE,
    num_hands=1
)
detector = HandLandmarker.create_from_options(options)

screen_w, screen_h = pyautogui.size()
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Erro: não foi possível acessar a webcam.")
    exit()

print("✅ Webcam conectada com sucesso!")
print("🖐️ Use o dedo indicador para mover o mouse.")
print("🤏 Junte polegar e indicador para arrastar janelas sob o cursor.")
print("❎ Pressione ESC para sair.\n")

# === FUNÇÕES AUXILIARES ===
def distancia(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

posicoes_x = deque(maxlen=SMOOTHING_FRAMES)
posicoes_y = deque(maxlen=SMOOTHING_FRAMES)

clicando = False
ultima_pos = None
ultimo_movimento = time.time()

def mover_janela_cursor(dx, dy):
    """Move a janela que está sob o cursor do mouse."""
    try:
        hwnd = win32gui.WindowFromPoint(pyautogui.position())
        rect = win32gui.GetWindowRect(hwnd)
        win32gui.MoveWindow(
            hwnd,
            rect[0] + int(dx),
            rect[1] + int(dy),
            rect[2] - rect[0],
            rect[3] - rect[1],
            True
        )
    except Exception:
        pass

# === LOOP PRINCIPAL ===
while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = Image(image_format=ImageFormat.SRGB, data=rgb)
    result = detector.detect(mp_image)
    h, w, _ = frame.shape
    frame_time = time.time()

    if result.hand_landmarks:
        ultimo_movimento = frame_time

        for hand_landmarks in result.hand_landmarks:
            # Pontos normalizados → pixels
            pontos = []
            for lm in hand_landmarks:
                cx, cy = int(lm.x * w), int(lm.y * h)
                pontos.append((cx, cy))

            # Índice e polegar
            x1, y1 = pontos[8]   # Indicador
            x2, y2 = pontos[4]   # Polegar
            dist = distancia((x1, y1), (x2, y2))

            # Conversão para tela
            mouse_x = np.interp(x1, (0, w), (0, screen_w))
            mouse_y = np.interp(y1, (0, h), (0, screen_h))

            # Suavização
            posicoes_x.append(mouse_x)
            posicoes_y.append(mouse_y)
            avg_x = np.mean(posicoes_x)
            avg_y = np.mean(posicoes_y)

            # === Desenhar a mão ===
            if DEBUG:
                # Desenhar conexões da mão
                for connection in solutions.hands.HAND_CONNECTIONS:
                    start = pontos[connection[0]]
                    end = pontos[connection[1]]
                    cv2.line(frame, start, end, (0, 255, 255), 2)

                # Desenhar pontos
                for (cx, cy) in pontos:
                    cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)

                cv2.putText(frame, f"Dist: {dist:.1f}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

            # === GESTOS ===
            if dist < CLICK_DIST and not clicando:
                clicando = True
                ultima_pos = (avg_x, avg_y)
                cv2.putText(frame, "🟢 SEGURANDO JANELA", (x1 - 70, y1 - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            elif clicando and dist < RELEASE_DIST:
                if ultima_pos:
                    dx = avg_x - ultima_pos[0]
                    dy = avg_y - ultima_pos[1]
                    mover_janela_cursor(dx, dy)
                    ultima_pos = (avg_x, avg_y)

            elif dist > RELEASE_DIST and clicando:
                clicando = False

            if not clicando:
                pyautogui.moveTo(avg_x, avg_y, duration=MOVE_DURATION)

    else:
        if frame_time - ultimo_movimento > INACTIVITY_TIMEOUT:
            cv2.putText(frame, "⏸️ Mão não detectada - pausado", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        else:
            cv2.putText(frame, "🔍 Procurando mão...", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

    cv2.imshow("🖐️ Gesture Window Mover", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        print("\n👋 Encerrando programa...")
        break

cap.release()
cv2.destroyAllWindows()
