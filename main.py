import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
from collections import deque

# === CONFIGURAÇÕES ===
DEBUG = False              # Mostra logs extras
MAX_HANDS = 1
SMOOTHING_FRAMES = 5       # Média móvel da posição do mouse
CLICK_DIST = 25            # Distância para "clicar"
RELEASE_DIST = 40          # Distância para "soltar"
MOVE_DURATION = 0.03       # Suavidade no movimento
INACTIVITY_TIMEOUT = 10    # Segundos antes de parar captura por inatividade

# === INICIALIZAÇÕES ===
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=MAX_HANDS, min_detection_confidence=0.6)
screen_w, screen_h = pyautogui.size()
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("❌ Erro: não foi possível acessar a webcam.")
    exit()

print("✅ Webcam conectada com sucesso!")
print("🖐️ Use o dedo indicador para mover o mouse.")
print("🤏 Junte polegar e indicador para clicar/arrastar.")
print("⏳ O programa pausa após inatividade.")
print("❎ Pressione ESC para sair.\n")

# === FUNÇÕES AUXILIARES ===
def distancia(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

# Fila para suavização do movimento
posicoes_x = deque(maxlen=SMOOTHING_FRAMES)
posicoes_y = deque(maxlen=SMOOTHING_FRAMES)

clicando = False
ultimo_movimento = time.time()

while True:
    success, img = cap.read()
    if not success:
        print("⚠️ Frame não capturado, tentando novamente...")
        continue

    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)
    h, w, _ = img.shape
    frame_time = time.time()

    if result.multi_hand_landmarks:
        ultimo_movimento = frame_time  # reset timeout
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            landmarks = hand_landmarks.landmark

            x1, y1 = int(landmarks[8].x * w), int(landmarks[8].y * h)
            x2, y2 = int(landmarks[4].x * w), int(landmarks[4].y * h)
            dist = distancia((x1, y1), (x2, y2))

            # Conversão para coordenadas de tela
            mouse_x = np.interp(x1, (0, w), (0, screen_w))
            mouse_y = np.interp(y1, (0, h), (0, screen_h))

            # Suavização de movimento
            posicoes_x.append(mouse_x)
            posicoes_y.append(mouse_y)
            avg_x = np.mean(posicoes_x)
            avg_y = np.mean(posicoes_y)

            pyautogui.moveTo(avg_x, avg_y, duration=MOVE_DURATION)

            if DEBUG:
                cv2.putText(img, f"Dist: {dist:.1f}", (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

            # Lógica de clique
            if dist < CLICK_DIST and not clicando:
                clicando = True
                pyautogui.mouseDown()
                cv2.putText(img, "🟢 CLICANDO", (x1 - 50, y1 - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            elif dist > RELEASE_DIST and clicando:
                clicando = False
                pyautogui.mouseUp()

    else:
        # Timeout de inatividade
        if frame_time - ultimo_movimento > INACTIVITY_TIMEOUT:
            cv2.putText(img, "⏸️ Mão não detectada - pausado", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        else:
            cv2.putText(img, "🔍 Procurando mão...", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

    cv2.imshow("🖐️ Gesture Mouse Controller", img)

    # Sai com ESC
    if cv2.waitKey(1) & 0xFF == 27:
        print("\n👋 Encerrando programa...")
        break

cap.release()
cv2.destroyAllWindows()
