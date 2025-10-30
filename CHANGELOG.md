# 📘 Changelog — Gesture Mouse Controller

Todas as mudanças importantes deste projeto serão documentadas aqui.

## [0.2.0] - 2025-10-30
### 🚀 Melhorias
- Implementada **suavização de movimento** (média móvel) para reduzir tremores do cursor.  
- Adicionado **timeout de inatividade**: pausa automática quando a mão sai de cena por muito tempo.  
- Criado **modo DEBUG** para exibir distâncias e dados de diagnóstico.  
- Otimizado o controle de movimento com `MOVE_DURATION` para transições mais suaves.  
- Inseridas **mensagens de status visuais** na tela (“Procurando mão...”, “Clicando”, etc.).  
- Adicionadas **margens de tolerância no clique** (25px para clicar, 40px para soltar) — evita falsos positivos.  
- Melhorado o **tratamento de falhas da webcam** e reconexão automática.  
- Novo layout de mensagens no terminal, com ícones e instruções de uso.  
- Código reestruturado com comentários e constantes no início, facilitando manutenção.  

### 🧰 Refatorações
- Removida lógica redundante de print a cada frame.  
- Unificado o cálculo de distância entre dedos.  
- Centralizadas as configurações principais (detecção, suavização, distâncias).  
- Adicionado controle de versão semântica e padrões para futuras versões.

### ⚠️ Alterações comportamentais
- Clique agora exige uma distância menor para acionar e maior para liberar.  
- O cursor se move com leve atraso controlado (`duration=0.03`) para maior estabilidade.  
- Frames com falha não encerram o programa — apenas emitem aviso.

---

## [0.1.0] - 2025-10-29
### 🧩 Versão inicial
- Implementado controle básico do mouse via **OpenCV + MediaPipe**.  
- Mapeamento do dedo indicador para posição do cursor.  
- Reconhecimento de gesto de pinça (polegar + indicador) para **clicar e arrastar**.  
- Interface simples com feedback visual mínimo.  
- Compatibilidade básica com Windows (DirectShow).  

---

## 📅 Próximos passos (roadmap)
- [ ] Gesto de movimentar janelas entre monitores.  
- [ ] Reconhecimento de múltiplos gestos (fechar janela, minimizar, etc.).  
- [ ] Suporte multiplataforma (Linux/Mac).  
- [ ] Interface overlay visual com ponteiro customizado.  
- [ ] Detecção de múltiplas mãos e associação de gestos.  

---

✍️ **Autor:** Gabriel Araújo  
🗓️ **Última atualização:** 30/10/2025  
🔖 **Licença:** MIT
