# formas/Forma.py
from abc import ABC, abstractmethod # <-- TEM QUE TER OS DOIS!
import numpy as np
from OpenGL.GL import *
import math 

class Forma(ABC):
    def __init__(self, centro, cor=(1.0, 1.0, 1.0)):
        self.centro = np.array(centro, dtype=np.float32)
        self.cor = cor
        self.escala = np.array([1.0, 1.0], dtype=np.float32)
        self.rotacao = 0.0  # Em graus
        self.selecionada = False

    # --- MÉTODOS ABSTRATOS (OBRIGATÓRIOS) ---
    @abstractmethod
    def desenhar(self): pass

    @abstractmethod
    def desenhar_preview(self, mouse_pos_mundo=(0,0)): pass

    @abstractmethod # <-- SEM TYPO AQUI
    def is_valid(self): pass
        
    @abstractmethod
    def foi_clicada(self, ponto): pass

    @abstractmethod
    def get_bounding_box(self): pass

    @abstractmethod
    def get_handlers(self): pass

    @abstractmethod
    def redimensionar(self, handler_index, novo_x_mundo, novo_y_mundo): pass

    # --- MÉTODOS CONCRETOS (COMPARTILHADOS) ---
    def aplicar_transformacoes(self):
        glTranslatef(self.centro[0], self.centro[1], 0.0)
        glRotatef(self.rotacao, 0.0, 0.0, 1.0)
        glScalef(self.escala[0], self.escala[1], 1.0)
        
    def mover(self, dx, dy):
        self.centro += np.array([dx, dy])

    def desenhar_bounding_box(self):
        if not self.selecionada:
            return
            
        min_x, min_y, max_x, max_y = self.get_bounding_box()

        glColor3f(0.5, 0.5, 0.5) 
        glPushAttrib(GL_ENABLE_BIT)
        glLineStipple(1, 0xAAAA) 
        glEnable(GL_LINE_STIPPLE)
        
        glBegin(GL_LINE_LOOP)
        glVertex2f(min_x, min_y)
        glVertex2f(max_x, min_y)
        glVertex2f(max_x, max_y)
        glVertex2f(min_x, max_y)
        glEnd()
        
        glPopAttrib()
        glColor3f(1.0, 1.0, 1.0) 

    def desenhar_handlers(self):
        if not self.selecionada: return
        handlers = self.get_handlers() 
        if not handlers: return
            
        glColor3f(1.0, 0.0, 0.0)
        glPointSize(7.0) 
        glBegin(GL_POINTS)
        for h in handlers:
            glVertex2f(*h)
        glEnd()
        glColor3f(1.0, 1.0, 1.0) 

    def click_em_handler(self, x_mundo, y_mundo):
        if not self.selecionada: return None
        handlers = self.get_handlers()
        if not handlers: return None
        hitbox = 5.0 
        for i, handler_pos in enumerate(handlers):
            dist = np.linalg.norm(np.array((x_mundo, y_mundo)) - handler_pos)
            if dist <= hitbox:
                return i 
        return None

    # --- OS MÉTODOS "CÉREBRO" ---
    def transformar_ponto_local(self, ponto_local):
        rad = math.radians(self.rotacao)
        c, s = math.cos(rad), math.sin(rad)
        x, y = ponto_local
        
        x_scaled = x * self.escala[0]
        y_scaled = y * self.escala[1]
        
        x_rot = x_scaled * c - y_scaled * s
        y_rot = x_scaled * s + y_scaled * c
        
        x_mundo = x_rot + self.centro[0]
        y_mundo = y_rot + self.centro[1]
        
        return (x_mundo, y_mundo)

    def transformar_ponto_mundo_para_local(self, ponto_mundo):
        escala_x = self.escala[0] if self.escala[0] != 0 else 0.0001
        escala_y = self.escala[1] if self.escala[1] != 0 else 0.0001
        
        x_trans = ponto_mundo[0] - self.centro[0]
        y_trans = ponto_mundo[1] - self.centro[1]
        
        rad = math.radians(-self.rotacao) 
        c, s = math.cos(rad), math.sin(rad)
        
        x_rot = x_trans * c - y_trans * s
        y_rot = x_trans * s + y_trans * c
        
        x_local = x_rot / escala_x
        y_local = y_rot / escala_y
        
        return (x_local, y_local)