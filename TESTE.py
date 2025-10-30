import mediapipe as mp
import pyautogui
import cv2
import numpy as np
import time

# Inicialização
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
screen_w, screen_h = pyautogui.size()

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("❌ Erro: não foi possível acessar a câmera.")
    exit()

print("✅ Webcam ativa. Movimente a mão para controlar o mouse.")
print("🤏 Junte o polegar + indicador para clicar/arrastar.")
print("❎ Pressione CTRL+C no terminal para sair.")

# Suavização de movimento
prev_x, prev_y = 0, 0
smoothening = 7  # quanto maior, mais suave

clicando = False

def distancia(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

while True:
    success, img = cap.read()
    if not success:
        continue  # se frame não veio, tenta de novo

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)

    h, w, _ = img.shape
    if result.multi_hand_landmarks:
        for hand in result.multi_hand_landmarks:
            lm = hand.landmark
            # pontos da mão
            x1, y1 = int(lm[8].x * w), int(lm[8].y * h)  # indicador
            x2, y2 = int(lm[4].x * w), int(lm[4].y * h)  # polegar

            # mapeia para tela
            mouse_x = np.interp(x1, (0, w), (0, screen_w))
            mouse_y = np.interp(y1, (0, h), (0, screen_h))

            # suaviza
            curr_x = prev_x + (mouse_x - prev_x) / smoothening
            curr_y = prev_y + (mouse_y - prev_y) / smoothening
            prev_x, prev_y = curr_x, curr_y

            pyautogui.moveTo(curr_x, curr_y)

            # distância para detectar clique/arrastar
            dist = distancia((x1, y1), (x2, y2))
            if dist < 45 and not clicando:
                clicando = True
                pyautogui.mouseDown()
                print("🟢 Arrastando...")
            elif dist > 60 and clicando:
                clicando = False
                pyautogui.mouseUp()
                print("⚪ Soltei clique")

