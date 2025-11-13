# formas/Triangulo.py
from formas.Forma import Forma
from OpenGL.GL import *
import numpy as np
import math

class Triangulo(Forma):
    def __init__(self, centro, raio_circunscrito=0.0, cor=(1.0, 1.0, 1.0)):
        super().__init__(centro, cor)
        # Raio do círculo que circunscreve o triângulo
        self.raio_circunscrito = raio_circunscrito

    def get_vertices_locais(self):
        """ Retorna os 3 vértices (relativos ao centro 0,0) """
        r = self.raio_circunscrito
        
        # Pontos de um triângulo equilátero "para cima"
        # Usando radianos para os ângulos:
        # V1 (Topo): 90 graus (pi / 2)
        # V2 (Baixo-Esquerda): 210 graus (7 * pi / 6)
        # V3 (Baixo-Direita): 330 graus (11 * pi / 6)
        
        v1 = (r * math.cos(math.pi / 2), r * math.sin(math.pi / 2))
        v2 = (r * math.cos(7 * math.pi / 6), r * math.sin(7 * math.pi / 6))
        v3 = (r * math.cos(11 * math.pi / 6), r * math.sin(11 * math.pi / 6))
        
        return v1, v2, v3

    def desenhar_corpo(self, modo):
        v1, v2, v3 = self.get_vertices_locais()
        
        glBegin(modo)
        glVertex2f(*v1)
        glVertex2f(*v2)
        glVertex2f(*v3)
        glEnd()

    def desenhar(self):
        glPushMatrix()
        self.aplicar_transformacoes() # Aplica translação/rotação/escala
        
        glColor3f(*self.cor)
        self.desenhar_corpo(GL_TRIANGLES) # Desenha preenchido
        
        glPopMatrix()
        
        self.desenhar_bounding_box()
        self.desenhar_handlers()


    def desenhar_preview(self):
        glPushMatrix()
        glTranslatef(self.centro[0], self.centro[1], 0.0)
        
        glColor3f(0.8, 0.8, 0.8) # Cor de preview
        
        glPushAttrib(GL_ENABLE_BIT)
        glLineStipple(1, 0xAAAA)
        glEnable(GL_LINE_STIPPLE)
        
        self.desenhar_corpo(GL_LINE_LOOP) # Apenas contorno
        
        glPopAttrib()
        glPopMatrix()

    def is_valid(self):
        """ Válido se o raio for maior que 1 pixel """
        return self.raio_circunscrito > 1

    def foi_clicada(self, ponto):
        # ATENÇÃO: Lógica de Ponto-em-Triângulo é complexa.
        # Vamos usar a Bounding Box como aproximação.
        min_x, min_y, max_x, max_y = self.get_bounding_box()
        return (min_x <= ponto[0] <= max_x) and \
               (min_y <= ponto[1] <= max_y)
        
    def get_bounding_box(self):
        # ATENÇÃO: Simplificado (sem rotação/escala)
        r = self.raio_circunscrito
        
        # Baseado nos vértices (cos/sin) que calculamos
        min_x_local = r * math.cos(7 * math.pi / 6) # -0.866 * r
        max_x_local = r * math.cos(11 * math.pi / 6) # +0.866 * r
        min_y_local = r * math.sin(7 * math.pi / 6) # -0.5 * r
        max_y_local = r * math.sin(math.pi / 2) # +1.0 * r
        
        # Aplica escala
        min_x = (min_x_local * self.escala[0]) + self.centro[0]
        max_x = (max_x_local * self.escala[0]) + self.centro[0]
        min_y = (min_y_local * self.escala[1]) + self.centro[1]
        max_y = (max_y_local * self.escala[1]) + self.centro[1]
        
        return (min_x, min_y, max_x, max_y)
    

    


    # formas/Triangulo.py
# ... (depois do método 'is_valid') ...

    def get_handlers(self):
        """ 
        Retorna os 4 cantos da Bounding Box do triângulo.
        """
        # (Lógica copiada de 'get_bounding_box')
        r = self.raio_circunscrito
        
        min_x_local = r * math.cos(7 * math.pi / 6) # -0.866 * r
        max_x_local = r * math.cos(11 * math.pi / 6) # +0.866 * r
        min_y_local = r * math.sin(7 * math.pi / 6) # -0.5 * r
        max_y_local = r * math.sin(math.pi / 2) # +1.0 * r
        
        min_x = (min_x_local * self.escala[0]) + self.centro[0]
        max_x = (max_x_local * self.escala[0]) + self.centro[0]
        min_y = (min_y_local * self.escala[1]) + self.centro[1]
        max_y = (max_y_local * self.escala[1]) + self.centro[1]
        
        return [
            (min_x, min_y), (max_x, min_y),
            (max_x, max_y), (min_x, max_y)
        ]

    def redimensionar(self, handler_index, novo_x_mundo, novo_y_mundo):
        """ 
        Para um Triângulo, qualquer handler redefine o 'raio_circunscrito'
        com base na distância ao centro.
        """
        dx = novo_x_mundo - self.centro[0]
        dy = novo_y_mundo - self.centro[1]
        
        self.raio_circunscrito = np.linalg.norm((dx, dy))