import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

# Inicialização
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1)
screen_w, screen_h = pyautogui.size()

# Tenta abrir a câmera com DirectShow (melhor no Windows)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Verificação de câmera
if not cap.isOpened():
    print("❌ Erro: não foi possível acessar a webcam.")
    print("👉 Verifique se ela está conectada e não está sendo usada por outro programa.")
    exit()

print("✅ Webcam conectada com sucesso!")
print("🖐️ Mova o dedo indicador para controlar o mouse.")
print("🤏 Junte o polegar e o indicador para clicar/arrastar.")
print("❎ Pressione ESC para sair.")

# Função auxiliar: distância entre pontos
def distancia(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

clicando = False  # estado atual do clique
ultimo_tempo = time.time()

while True:
    success, img = cap.read()
    if not success:
        print("⚠️ Frame não capturado. Tentando novamente...")
        continue

    img = cv2.flip(img, 1)  # espelha a imagem
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)

    h, w, _ = img.shape
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            landmarks = hand_landmarks.landmark

            # Dedo indicador (8) e polegar (4)
            x1, y1 = int(landmarks[8].x * w), int(landmarks[8].y * h)
            x2, y2 = int(landmarks[4].x * w), int(landmarks[4].y * h)

            # Converte coordenadas da câmera para tela
            mouse_x = np.interp(x1, (0, w), (0, screen_w))
            mouse_y = np.interp(y1, (0, h), (0, screen_h))

            # Move o mouse suavemente
            pyautogui.moveTo(mouse_x, mouse_y, duration=0.05)

            # Calcula a distância entre polegar e indicador
            dist = distancia((x1, y1), (x2, y2))

            # Se juntarem = clica e segura
            if dist < 25 and not clicando:
                clicando = True
                pyautogui.mouseDown()
                cv2.putText(img, "🟢 Arrastando...", (x1 - 50, y1 - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            # Se afastarem = solta o clique
            elif dist > 35 and clicando:
                clicando = False
                pyautogui.mouseUp()

    cv2.imshow("Hand Drag Controller", img)

    # Sai com ESC
    if cv2.waitKey(1) & 0xFF == 27:
        print("\n👋 Encerrando programa...")
        break

cap.release()
cv2.destroyAllWindows()
