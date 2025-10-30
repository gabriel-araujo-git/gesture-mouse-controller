import cv2
import numpy as np
import pyautogui
import time
from collections import deque
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import Image, ImageFormat

# === CONFIGURAÇÕES ===
DEBUG = False
SMOOTHING_FRAMES = 5
CLICK_DIST = 25
RELEASE_DIST = 40
MOVE_DURATION = 0      # 🔥 Movimento mais rápido
INACTIVITY_TIMEOUT = 10
SENSITIVITY = 1.9          # 🧭 Fator de velocidade do cursor (1.0 = normal)

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
print("🤏 Junte polegar e indicador para clicar/arrastar.")
print("❎ Pressione ESC para sair.\n")

# === FUNÇÕES AUXILIARES ===
def distancia(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

posicoes_x = deque(maxlen=SMOOTHING_FRAMES)
posicoes_y = deque(maxlen=SMOOTHING_FRAMES)

clicando = False
ultimo_movimento = time.time()

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
            # === Coordenadas dos dedos ===
            x1, y1 = int(hand_landmarks[8].x * w), int(hand_landmarks[8].y * h)  # Indicador
            x2, y2 = int(hand_landmarks[4].x * w), int(hand_landmarks[4].y * h)  # Polegar

            dist = distancia((x1, y1), (x2, y2))

            # === Conversão para tela com sensibilidade ===
            mouse_x = np.interp(x1, (0, w), (0, screen_w * SENSITIVITY))
            mouse_y = np.interp(y1, (0, h), (0, screen_h * SENSITIVITY))

            # Evita sair da tela
            mouse_x = min(max(mouse_x, 0), screen_w)
            mouse_y = min(max(mouse_y, 0), screen_h)

            # === Suavização ===
            posicoes_x.append(mouse_x)
            posicoes_y.append(mouse_y)
            avg_x = np.mean(posicoes_x)
            avg_y = np.mean(posicoes_y)

            pyautogui.moveTo(avg_x, avg_y, duration=MOVE_DURATION)

            # === HUD visual ===
            cv2.circle(frame, (x1, y1), 10, (0, 255, 255), -1)  # Indicador
            cv2.circle(frame, (x2, y2), 10, (0, 255, 0), -1)    # Polegar
            cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 0), 3)

            if dist < CLICK_DIST and not clicando:
                clicando = True
                pyautogui.mouseDown()
                cv2.putText(frame, "🟢 CLICANDO", (x1 - 50, y1 - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            elif dist > RELEASE_DIST and clicando:
                clicando = False
                pyautogui.mouseUp()

    else:
        if frame_time - ultimo_movimento > INACTIVITY_TIMEOUT:
            cv2.putText(frame, "⏸️ Mão não detectada - pausado", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        else:
            cv2.putText(frame, "🔍 Procurando mão...", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

    cv2.imshow("🖐️ Gesture Mouse Controller", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        print("\n👋 Encerrando programa...")
        break

cap.release()
cv2.destroyAllWindows()
