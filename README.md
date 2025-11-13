# Gesture Mouse Controller

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)](#)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.7-blue?logo=opencv&logoColor=white)](#)
[![PyAutoGUI](https://img.shields.io/badge/PyAutoGUI-0.9.53-lightgrey)](#)
[![Version](https://img.shields.io/badge/Version-0.2-green)](#)
[![Status](https://img.shields.io/badge/Status-Experimental-orange)](#)
[![License](https://img.shields.io/badge/License-OpenSource-lightgrey)](#)
[![Author](https://img.shields.io/badge/Author-Gabriel_Araujo-blueviolet)](#)
[![Last Update](https://img.shields.io/badge/Updated-Oct_2025-lightgrey)](#)

---

## Visão Geral

Sistema experimental para **controlar o computador usando gestos**, sem necessidade de mouse físico.  
Desenvolvido em **Python** com **OpenCV** e **PyAutoGUI**, o projeto reconhece movimentos de mão via câmera e os traduz em ações do sistema.

---

## Funcionalidades

- Detecção em tempo real via webcam.  
- Controle de cursor e cliques simulados.  
- Ajuste de sensibilidade para melhor precisão.  
- Base para futuras expansões, como movimentação de janelas e gestos personalizados.

---
```
GESTURE-MOUSE-CONTROLLER/
│
├── main.py         # Código principal do sistema (loop de detecção)
├── TESTE.py        # Arquivo de testes e experimentos
├── CHANGELOG.md    # Histórico de versões
├── README.md       # Documentação do projeto
└── .gitignore      # Arquivos a serem ignorados pelo Git
```

---

## ⚡ Como executar

1. Clone o repositório:
   ```bash
   git clone https://github.com/seuusuario/GESTURE-MOUSE-CONTROLLER.git
   cd GESTURE-MOUSE-CONTROLLER
   ```

2. Instale as dependências:
   ```bash
   pip install opencv-python pyautogui
   ```

3. Execute o programa principal:
   ```bash
   python main.py
   ```

---

## 🧪 Versões

| Versão | Data | Alterações principais |
|--------|------|-----------------------|
| 0.1 | 29/10/2025 | Primeira versão funcional |
| 0.2 | 30/10/2025 | Movimento suave e melhor precisão |

---

## 🧭 Próximos passos

- Adicionar **gesto para mover janelas entre monitores**.  
- Implementar **interface de calibração**.  
- Criar **módulo de logging** e métricas de uso.  

---

## 📄 Licença

Projeto de código aberto para estudo e experimentação.  
Feito com 🧠 por **Gabriel Araújo**.

---

> 💡 *“Caro eu do futuro: se você está aqui, é porque temos problemas.  
> Felizmente, deixei algo pronto para ajudar.”*
