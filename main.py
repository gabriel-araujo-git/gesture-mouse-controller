# main_robusto.py
# Requisitos: opencv, numpy, pyautogui, mediapipe (tasks API)
# Ex.: pip install opencv-python numpy pyautogui mediapipe
#
# Suporte: movimento com indicador, pinch (indicador+polegar) = click/arrastar,
# pinch rápido = duplo clique, two-finger (indice+medio) = modo scroll,
# two-finger pinch = clique direito, 3 dedos = middle click,
# 5 dedos = abrir menu iniciar (Windows). Teclas:
#   ESC = sair
#   p   = pausar/resumir detecção
#   c   = recalibrar (central region)
#   + / - = ajustar sensibilidade
#
# Ajuste as constantes no bloco CONFIG conforme preferir.

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
SMOOTHING_FRAMES = 6
CLICK_DIST = 35          # distancia (px) para considerar pinch = click
RELEASE_DIST = 55        # distancia para soltar clique
MOVE_DURATION = 0        # 0 para mover instantâneo
INACTIVITY_TIMEOUT = 8   # segundos para mensagem "pausado"
SENSITIVITY = 1.6        # multiplicador da posição do cursor
DOUBLE_CLICK_MAX_INTERVAL = 0.35  # segundos
SCROLL_SENSITIVITY = 8   # quanto rola por unidade de movimento
MODEL_PATH = "hand_landmarker.task"  # seu modelo

# Mapeamento de gestos -> ações (padrões)
# Você pode alterar: 'five_open' por qualquer função que chame pyautogui
def default_gesture_actions():
    return {
        "pinch_left": lambda: pyautogui.mouseDown(),                # começar arrastar / clicar
        "pinch_left_up": lambda: pyautogui.mouseUp(),               # soltar arrastar
        "pinch_left_click": lambda: pyautogui.click(),              # click simples
        "pinch_left_double": lambda: pyautogui.doubleClick(),       # duplo click
        "pinch_right_click": lambda: pyautogui.click(button="right"),
        "three_fingers": lambda: pyautogui.click(button="middle"),
        "five_open": lambda: pyautogui.press("win"),                # abrir menu iniciar no Windows
        "scroll": lambda dx, dy: pyautogui.scroll(int(dy)),        # dy positivo = scroll up
    }

GESTURE_ACTIONS = default_gesture_actions()

# === SETUP MEDIAPIPE ===
BaseOptions = python.BaseOptions
VisionRunningMode = vision.RunningMode
HandLandmarker = vision.HandLandmarker
HandLandmarkerOptions = vision.HandLandmarkerOptions

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.IMAGE,
    num_hands=1
)
detector = HandLandmarker.create_from_options(options)

screen_w, screen_h = pyautogui.size()
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Erro: não foi possível acessar a webcam.")
    exit()

print("✅ Webcam conectada. Gestos ativos.")
print("Teclas: ESC sair | p pausar | c recalibrar | + / - ajuste sensibilidade\n")

# === HELPERS ===
def distancia(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

# determina quais dedos estão "up"
# landmarks: lista de landmarks com atributos .x, .y (normalized)
def fingers_up(landmarks, img_w, img_h):
    # tip indices
    tips = [4, 8, 12, 16, 20]
    pip = [3, 6, 10, 14, 18]  # use "pip" or ip joint for comparison
    states = []
    # para polegar, comparar em x (pois polegar abre lateralmente). Depende de mão.
    # Como a imagem foi flipada (espelhada), tentaremos inferir pela posição relativa do polegar.
    # Simples heurística: se tip.x < pip.x -> polegar "aberto" (apontando pra esquerda na imagem espelhada)
    for i, t in enumerate(tips):
        tip = landmarks[t]
        base = landmarks[pip[i]]
        if i == 0:
            # polegar
            states.append(tip.x < base.x)  # True = aberto
        else:
            # dedos: comparando y (na imagem, y menor = dedo erguido)
            states.append(tip.y < base.y)
    return states  # [thumb, index, middle, ring, pinky] -> booleans

# smooth queue
pos_x = deque(maxlen=SMOOTHING_FRAMES)
pos_y = deque(maxlen=SMOOTHING_FRAMES)

# estado
clicando = False
paused = False
ultimo_movimento = time.time()
last_pinch_time = 0
last_pinched = False
last_left_click_time = 0
last_scroll_y = None
calib_offset = (0, 0)
sensitivity = SENSITIVITY

# calibragem: define offset (centro neutro) com a mão em posição desejada
def recalibrate(center_x, center_y):
    global calib_offset, pos_x, pos_y
    calib_offset = (center_x, center_y)
    pos_x.clear()
    pos_y.clear()
    print(f"🔧 Recalibrado para offset {calib_offset}")

# Função utilitária para invocar ação de scroll com dx/dy
def do_scroll(delta_y):
    # maior delta -> mais scroll. Ajuste SCROLL_SENSITIVITY
    # pyautogui.scroll expects positive integers to scroll up.
    steps = int(delta_y * SCROLL_SENSITIVITY)
    if steps != 0:
        GESTURE_ACTIONS["scroll"](0, steps)

# === LOOP PRINCIPAL ===
while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)  # espelhar para comportamento tipo espelho
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = Image(image_format=ImageFormat.SRGB, data=rgb)
    result = detector.detect(mp_image)
    h, w, _ = frame.shape
    now = time.time()

    if paused:
        cv2.putText(frame, "⏸️ PAUSADO (pressione 'p' para continuar)", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 200), 2)
        last_scroll_y = None
    else:
        if result.hand_landmarks:
            ultimo_movimento = now
            for hand_landmarks in result.hand_landmarks:
                lm = hand_landmarks
                # converter landmarks normalizados para coordenadas de imagem
                lms = [(int(pt.x * w), int(pt.y * h)) for pt in lm]
                # Pega pontos relevantes
                idx_tip = lms[8]
                thumb_tip = lms[4]
                mid_tip = lms[12]

                # detectar dedos up via lógica simples (usa normalized coords)
                # precisamos da versão normalizada para fingers_up
                normalized = lm
                fstates = fingers_up(normalized, w, h)  # [thumb, index, middle, ring, pinky]

                # DISTÂNCIAS
                d_thumb_index = distancia(idx_tip, thumb_tip)
                d_index_middle = distancia(idx_tip, mid_tip)

                # === MAPEAMENTO DE GESTOS ===
                # 1 dedo (index) -> mover cursor
                if fstates[1] and not any([fstates[2], fstates[3], fstates[4]]):
                    # mover
                    # convert index tip x (imagem) para coordenadas de tela
                    raw_x = idx_tip[0]
                    raw_y = idx_tip[1]
                    # ajuste sensibilidade e calibragem
                    # normaliza em relação ao frame e aplica multiplicador
                    mouse_x = np.interp(raw_x, (0, w), (0, screen_w * sensitivity)) - calib_offset[0]
                    mouse_y = np.interp(raw_y, (0, h), (0, screen_h * sensitivity)) - calib_offset[1]
                    # clamp
                    mouse_x = min(max(mouse_x, 0), screen_w)
                    mouse_y = min(max(mouse_y, 0), screen_h)
                    # suaviza
                    pos_x.append(mouse_x)
                    pos_y.append(mouse_y)
                    avg_x = np.mean(pos_x)
                    avg_y = np.mean(pos_y)
                    pyautogui.moveTo(avg_x, avg_y, duration=MOVE_DURATION)
                    cv2.putText(frame, "✋ MOVER", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 0), 2)
                    last_scroll_y = None

                # 1.1 pinch index+thumb -> left click / drag
                if d_thumb_index < CLICK_DIST:
                    # se não estava clicando, e pinch rápido recente -> double click
                    if not clicando:
                        # checar intervalo para duplo clique
                        if now - last_pinch_time < DOUBLE_CLICK_MAX_INTERVAL:
                            # duplo clique
                            try:
                                GESTURE_ACTIONS["pinch_left_double"]()
                            except Exception:
                                pass
                            cv2.putText(frame, "⚡ DUplo Clique", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                            last_pinch_time = 0
                        else:
                            # começar clique/arrastar
                            try:
                                GESTURE_ACTIONS["pinch_left"]()
                            except Exception:
                                pass
                            clicando = True
                            last_pinch_time = now
                            cv2.putText(frame, "🟢 PINCH - CLICANDO/ARRASTANDO", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    else:
                        # já clicando -> mantém mouseDown (arrastar)
                        cv2.putText(frame, "🟢 ARRASTANDO", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                else:
                    # se soltou o pinch
                    if clicando:
                        try:
                            GESTURE_ACTIONS["pinch_left_up"]()
                        except Exception:
                            pass
                        clicando = False
                        cv2.putText(frame, "🔴 SOLTOU", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 100, 255), 2)

                # 2 dedos (index+middle up) -> modo rolagem
                if fstates[1] and fstates[2] and not fstates[3]:
                    cv2.putText(frame, "↕️ MODO ROLAGEM", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (180, 180, 0), 2)
                    # track movimento vertical do ponto médio dos dois dedos
                    mid_x = int((idx_tip[0] + mid_tip[0]) / 2)
                    mid_y = int((idx_tip[1] + mid_tip[1]) / 2)
                    if last_scroll_y is None:
                        last_scroll_y = mid_y
                    else:
                        dy = last_scroll_y - mid_y  # mover a mão pra cima = dy positivo -> scroll up
                        do_scroll(dy / 20.0)  # normaliza um pouco
                        last_scroll_y = mid_y
                else:
                    last_scroll_y = None

                # two-finger pinch (index+middle bem próximos) -> clique direito
                if fstates[1] and fstates[2] and distancia(idx_tip, mid_tip) < 40:
                    # clique direito "instantâneo"
                    cv2.putText(frame, "🔘 CLIQUE DIREITO", (10, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 50, 255), 2)
                    # agir apenas quando detectar a transição (para não spam)
                    if not last_pinched:
                        try:
                            GESTURE_ACTIONS["pinch_right_click"]()
                        except Exception:
                            pass
                        last_pinched = True
                else:
                    last_pinched = False

                # 3 dedos abertos -> middle click
                if fstates[1] and fstates[2] and fstates[3] and not fstates[4]:
                    cv2.putText(frame, "🟣 3 DEDOS - MIDDLE CLICK", (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 100, 200), 2)
                    # trigger apenas na transição
                    if not getattr(do_three_click := globals().get("_three_triggered", False), "value", False):
                        try:
                            GESTURE_ACTIONS["three_fingers"]()
                        except Exception:
                            pass
                        globals()["_three_triggered"] = True
                else:
                    globals()["_three_triggered"] = False

                # 5 dedos abertos -> ação especial (ex: abrir start)
                if all(fstates):
                    cv2.putText(frame, "⭐ 5 DEDOS - AÇÃO ESPECIAL", (10, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 255, 100), 2)
                    # trigger na transição
                    if not getattr(globals().get("_five_triggered", False), "value", False):
                        try:
                            GESTURE_ACTIONS["five_open"]()
                        except Exception:
                            pass
                        globals()["_five_triggered"] = True
                else:
                    globals()["_five_triggered"] = False

                # HUD: desenha pontos importantes
                cv2.circle(frame, idx_tip, 8, (0, 255, 255), -1)
                cv2.circle(frame, thumb_tip, 8, (0, 200, 0), -1)
                cv2.circle(frame, mid_tip, 6, (255, 100, 0), -1)
                cv2.line(frame, idx_tip, thumb_tip, (255, 255, 0), 2)

        else:
            # mão não detectada
            if now - ultimo_movimento > INACTIVITY_TIMEOUT:
                cv2.putText(frame, "⏸️ Mão não detectada - aguardando...", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            else:
                cv2.putText(frame, "🔍 Procurando mão...", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

    # mostra configurações atuais em tela
    cv2.putText(frame, f"SENS: {sensitivity:.2f}  |  SMOOTH: {SMOOTHING_FRAMES}", (10, frame.shape[0]-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 220, 220), 1)

    cv2.imshow("Gesture Control - Robust", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC
        print("👋 Encerrando...")
        break
    elif key == ord('p'):
        paused = not paused
        print("⏸️ Pausado" if paused else "▶️ Retomado")
    elif key == ord('c'):
        # recalibra com centro da tela atual do cursor (usuário posiciona a mão no centro do frame e pressiona c)
        recalibrate(0, 0)  # aqui usamos 0/0 pois já mapearmos absoluto; mantive placeholder
    elif key == ord('+') or key == ord('='):
        sensitivity += 0.1
        print(f"🔧 Sensibilidade: {sensitivity:.2f}")
    elif key == ord('-') or key == ord('_'):
        sensitivity = max(0.3, sensitivity - 0.1)
        print(f"🔧 Sensibilidade: {sensitivity:.2f}")

cap.release()
cv2.destroyAllWindows()
