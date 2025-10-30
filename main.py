import cv2
import numpy as np
import pyautogui
import time
from collections import deque
import pygetwindow as gw
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import Image, ImageFormat

# === CONFIGURAÇÕES ===
DEBUG = False
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
print("🤏 Junte polegar e indicador para arrastar janelas.")
print("❎ Pressione ESC para sair.\n")

# === FUNÇÕES AUXILIARES ===
def distancia(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

posicoes_x = deque(maxlen=SMOOTHING_FRAMES)
posicoes_y = deque(maxlen=SMOOTHING_FRAMES)

clicando = False
ultima_pos = None
janela_ativa = None
ultimo_movimento = time.time()

def mover_janela_ativa(dx, dy):
    """Move a janela atualmente ativa pelo deslocamento (dx, dy)."""
    try:
        janela = gw.getActiveWindow()
        if janela:
            janela.move(janela.left + dx, janela.top + dy)
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
            # Pontos dos dedos (normalizados 0–1 → pixels)
            x1, y1 = int(hand_landmarks[8].x * w), int(hand_landmarks[8].y * h)  # Indicador
            x2, y2 = int(hand_landmarks[4].x * w), int(hand_landmarks[4].y * h)  # Polegar

            dist = distancia((x1, y1), (x2, y2))

            # Conversão para coordenadas de tela
            mouse_x = np.interp(x1, (0, w), (0, screen_w))
            mouse_y = np.interp(y1, (0, h), (0, screen_h))

            # Suavização
            posicoes_x.append(mouse_x)
            posicoes_y.append(mouse_y)
            avg_x = np.mean(posicoes_x)
            avg_y = np.mean(posicoes_y)

            if DEBUG:
                cv2.putText(frame, f"Dist: {dist:.1f}", (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

            # === GESTOS ===

            # 🤏 Juntou os dedos → iniciar arrasto de janela
            if dist < CLICK_DIST and not clicando:
                clicando = True
                janela_ativa = gw.getActiveWindow()
                ultima_pos = (avg_x, avg_y)
                cv2.putText(frame, "🟢 SEGURANDO JANELA", (x1 - 70, y1 - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Mantém arrastando enquanto os dedos estiverem juntos
            elif clicando and dist < RELEASE_DIST:
                if ultima_pos and janela_ativa:
                    dx = avg_x - ultima_pos[0]
                    dy = avg_y - ultima_pos[1]
                    mover_janela_ativa(int(dx), int(dy))
                    ultima_pos = (avg_x, avg_y)

            # 🖐️ Separou os dedos → soltar janela
            elif dist > RELEASE_DIST and clicando:
                clicando = False
                janela_ativa = None

            # 🖱️ Se não está clicando, apenas mover o cursor
            if not clicando:
                pyautogui.moveTo(avg_x, avg_y, duration=MOVE_DURATION)

    else:
        # Nenhuma mão detectada
        if frame_time - ultimo_movimento > INACTIVITY_TIMEOUT:
            cv2.putText(frame, "⏸️ Mão não detectada - pausado", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        else:
            cv2.putText(frame, "🔍 Procurando mão...", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

    cv2.imshow("🖐️ Gesture Window Controller", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        print("\n👋 Encerrando programa...")
        break

cap.release()
cv2.destroyAllWindows()
