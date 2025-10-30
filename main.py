import cv2
import numpy as np
import pyautogui
import time
import keyboard
from collections import deque
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import Image, ImageFormat

# === CONFIGURAÇÕES ===
SMOOTHING_FRAMES = 5
MOVE_DURATION = 0.02
INACTIVITY_TIMEOUT = 10
GESTO_COOLDOWN = 1.0  # segundos entre ativações do mesmo gesto

# === MODELO ===
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

print("✅ Gesture Controller iniciado com HUD visual!")
print("🖐️ Indicador move o mouse")
print("🤏 Pinça = clique/arrastar")
print("✌️ Dois dedos = Alt+Tab")
print("👍 Joinha = Volume + / 👎 = Volume -")
print("✊ Fechar a mão = ESC\n")
print("❎ Pressione ESC para sair.")

# === AUXILIARES ===
def distancia(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

def proporcao_mao(hand_landmarks, w, h):
    x_min = min(lm.x for lm in hand_landmarks) * w
    x_max = max(lm.x for lm in hand_landmarks) * w
    y_min = min(lm.y for lm in hand_landmarks) * h
    y_max = max(lm.y for lm in hand_landmarks) * h
    return x_max - x_min, y_max - y_min

tempo_gesto = {}
def gesto_detectado(nome, intervalo=0.5):
    agora = time.time()
    if nome not in tempo_gesto:
        tempo_gesto[nome] = agora
        return False
    if agora - tempo_gesto[nome] >= intervalo:
        tempo_gesto[nome] = agora + GESTO_COOLDOWN
        return True
    return False

# === CONTROLE DE MOVIMENTO ===
posicoes_x = deque(maxlen=SMOOTHING_FRAMES)
posicoes_y = deque(maxlen=SMOOTHING_FRAMES)
clicando = False
ultimo_movimento = time.time()
hud_text = ""
hud_color = (255, 255, 255)
hud_timer = 0

# === LOOP ===
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
            index = (int(hand_landmarks[8].x * w), int(hand_landmarks[8].y * h))
            thumb = (int(hand_landmarks[4].x * w), int(hand_landmarks[4].y * h))
            middle = (int(hand_landmarks[12].x * w), int(hand_landmarks[12].y * h))
            ring = (int(hand_landmarks[16].x * w), int(hand_landmarks[16].y * h))
            pinky = (int(hand_landmarks[20].x * w), int(hand_landmarks[20].y * h))

            largura_mao, altura_mao = proporcao_mao(hand_landmarks, w, h)
            base_dist = np.hypot(largura_mao, altura_mao) / 4

            dist_thumb_index = distancia(index, thumb)
            dist_index_middle = distancia(index, middle)
            dist_ring_pinky = distancia(ring, pinky)

            # Movimento do mouse
            mouse_x = np.interp(index[0], (0, w), (0, screen_w))
            mouse_y = np.interp(index[1], (0, h), (0, screen_h))
            posicoes_x.append(mouse_x)
            posicoes_y.append(mouse_y)
            avg_x = np.mean(posicoes_x)
            avg_y = np.mean(posicoes_y)
            pyautogui.moveTo(avg_x, avg_y, duration=MOVE_DURATION)

            # === GESTOS ===
            # 🤏 Clique / arrastar
            if dist_thumb_index < 0.25 * base_dist and not clicando:
                clicando = True
                pyautogui.mouseDown()
                hud_text, hud_color = "🟢 Clique / Arrastar", (0, 255, 0)
                hud_timer = time.time()

            elif dist_thumb_index > 0.35 * base_dist and clicando:
                clicando = False
                pyautogui.mouseUp()
                hud_text, hud_color = "🔵 Soltar", (255, 255, 0)
                hud_timer = time.time()

            # ✌️ Alt+Tab
            if dist_index_middle < 0.25 * base_dist and gesto_detectado("alt_tab"):
                keyboard.press_and_release('alt+tab')
                hud_text, hud_color = "🔄 ALT + TAB", (255, 0, 255)
                hud_timer = time.time()

            # 👍 Volume +
            if thumb[1] < min(index[1], middle[1], ring[1], pinky[1]) - 40:
                if gesto_detectado("vol_up"):
                    keyboard.press_and_release('volume up')
                    hud_text, hud_color = "🔊 Volume +", (0, 255, 255)
                    hud_timer = time.time()

            # 👎 Volume -
            if thumb[1] > max(index[1], middle[1], ring[1], pinky[1]) + 40:
                if gesto_detectado("vol_down"):
                    keyboard.press_and_release('volume down')
                    hud_text, hud_color = "🔉 Volume -", (0, 165, 255)
                    hud_timer = time.time()

            # ✊ ESC
            if dist_ring_pinky < 0.2 * base_dist and gesto_detectado("esc"):
                keyboard.press_and_release('esc')
                hud_text, hud_color = "🚪 ESC", (0, 0, 255)
                hud_timer = time.time()

            # === HUD Visual ===
            for lm in hand_landmarks:
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)
            cv2.line(frame, index, thumb, (255, 0, 0), 2)
            cv2.line(frame, index, middle, (0, 255, 255), 2)

    else:
        if frame_time - ultimo_movimento > INACTIVITY_TIMEOUT:
            hud_text, hud_color = "⏸️ Pausado - mão fora de vista", (0, 0, 255)
            hud_timer = time.time()

    # Exibir HUD (texto com fade)
    if time.time() - hud_timer < 1.5:
        cv2.putText(frame, hud_text, (40, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, hud_color, 3)

    cv2.imshow("🖐️ Gesture Controller (HUD Mode)", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        print("\n👋 Encerrando...")
        break

cap.release()
cv2.destroyAllWindows()
