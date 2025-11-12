# selection_manager.py
from OpenGL.GL import *
import math

class SelectionManager:
    def __init__(self, janela):
        self.janela = janela
        self.forma_hover = None       # preview (mouse por cima)
        self.forma_selecionada = None # forma clicada
        self.arrastando = False
        self.offset = (0, 0)

    # ---------------- Detectar hover (preview) ----------------
    def verificar_hover(self, x, y):
        """Verifica se o mouse está sobre alguma forma"""
        self.forma_hover = None
        for item in reversed(self.janela.formas):
            forma, fx, fy, color = item
            if hasattr(forma, 'contem_ponto') and forma.contem_ponto(x, y, fx, fy):
                self.forma_hover = item
                break

    # ---------------- Selecionar ao clicar ----------------
    def selecionar_forma(self, x, y):
        """Seleciona uma forma ao clicar"""
        self.forma_selecionada = None
        for item in reversed(self.janela.formas):
            forma, fx, fy, color = item
            if hasattr(forma, 'contem_ponto') and forma.contem_ponto(x, y, fx, fy):
                self.forma_selecionada = item
                self.offset = (x - fx, y - fy)
                print(f"[seleção] {forma.__class__.__name__} selecionado.")
                return True
        print("[seleção] nenhuma forma.")
        return False

    # ---------------- Iniciar arraste ----------------
    def iniciar_arraste(self, x, y):
        if self.forma_selecionada:
            self.arrastando = True
            self.offset = (x - self.forma_selecionada[1], y - self.forma_selecionada[2])

    # ---------------- Atualizar arraste ----------------
    def mover_forma(self, x, y):
        if self.arrastando and self.forma_selecionada:
            forma, fx, fy, color = self.forma_selecionada
            novo_x = x - self.offset[0]
            novo_y = y - self.offset[1]
            self.forma_selecionada = (forma, novo_x, novo_y, color)

            # Atualiza lista original
            idx = self.janela.formas.index((forma, fx, fy, color))
            self.janela.formas[idx] = self.forma_selecionada

    # ---------------- Soltar mouse ----------------
    def finalizar_arraste(self):
        self.arrastando = False

  