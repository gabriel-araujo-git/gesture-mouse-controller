# 🧠 Gesture Mouse Controller

Sistema experimental para **controlar o computador usando apenas gestos**, sem necessidade de mouse físico.  
Desenvolvido em **Python** com **OpenCV**, o projeto reconhece movimentos de mão via câmera e os traduz em ações do sistema.

---

## 🚀 Funcionalidades

- 🎥 Detecção em tempo real via webcam.  
- 🖱️ Controle suave do cursor e cliques simulados.  
- ⚙️ Ajuste de sensibilidade para melhor precisão.  
- 💡 Base para futuras expansões (como mover janelas e multitela).  

---

## 🧩 Estrutura atual

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
