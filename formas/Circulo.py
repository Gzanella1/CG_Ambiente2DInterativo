# formas/Circulo.py
from formas.Forma import Forma
from OpenGL.GL import *
import numpy as np
import math

class Circulo(Forma):
    def __init__(self, centro, raio=0.0, cor=(1.0, 1.0, 1.0)):
        super().__init__(centro, cor)
        self.raio = raio

    def desenhar_corpo(self, modo):
        """ Helper para desenhar o círculo (preenchido ou linha). """
        glBegin(modo)
        for i in range(100):
            angulo = 2.0 * math.pi * i / 100.0
            x = self.raio * math.cos(angulo)
            y = self.raio * math.sin(angulo)
            glVertex2f(x, y)
        glEnd()

    def desenhar(self):
        glPushMatrix()
        self.aplicar_transformacoes() # Aplica translação/rotação/escala
        
        glColor3f(*self.cor)
        self.desenhar_corpo(GL_TRIANGLE_FAN) # Desenha preenchido
        
        glPopMatrix()
        
        # Desenha BBox e Handlers (fora da matriz de transformação da forma)
        self.desenhar_bounding_box()
        self.desenhar_handlers()


    def desenhar_preview(self):
        glPushMatrix()
        # O preview só precisa de translação, não de escala/rotação
        glTranslatef(self.centro[0], self.centro[1], 0.0)
        
        glColor3f(0.8, 0.8, 0.8) # Cor de preview
        
        # Simula tracejado com GL_LINE_LOOP
        glPushAttrib(GL_ENABLE_BIT)
        glLineStipple(1, 0xAAAA)
        glEnable(GL_LINE_STIPPLE)
        
        self.desenhar_corpo(GL_LINE_LOOP)
        
        glPopAttrib()
        glPopMatrix()

    def foi_clicada(self, ponto):
        # Transforma o ponto para o sistema de coordenadas local da forma
        # (Isso é complexo! Envolve matrizes inversas)
        
        # Versão simples sem rotação/escala:
        distancia = np.linalg.norm(np.array(ponto) - self.centro)
        return distancia <= (self.raio * max(self.escala)) # Considera escala
        
    def get_bounding_box(self):
        # Novamente, simplificado sem rotação
        raio_escalado_x = self.raio * self.escala[0]
        raio_escalado_y = self.raio * self.escala[1]
        min_x = self.centro[0] - raio_escalado_x
        min_y = self.centro[1] - raio_escalado_y
        max_x = self.centro[0] + raio_escalado_x
        max_y = self.centro[1] + raio_escalado_y
        return (min_x, min_y, max_x, max_y)
    

    # ... (fim do get_bounding_box) ...

    def is_valid(self):
        """ Um círculo é válido se seu raio for maior que um pixel. """
        return self.raio > 1
    

    # formas/Circulo.py
# ... (depois do método 'is_valid') ...

    def get_handlers(self):
        """ 
        Retorna os 4 cantos da Bounding Box do círculo.
        """
        # (Lógica copiada de 'get_bounding_box')
        raio_escalado_x = self.raio * self.escala[0]
        raio_escalado_y = self.raio * self.escala[1]
        min_x = self.centro[0] - raio_escalado_x
        min_y = self.centro[1] - raio_escalado_y
        max_x = self.centro[0] + raio_escalado_x
        max_y = self.centro[1] + raio_escalado_y
        
        # Retorna os 4 cantos
        return [
            (min_x, min_y), (max_x, min_y),
            (max_x, max_y), (min_x, max_y)
        ]

    def redimensionar(self, handler_index, novo_x_mundo, novo_y_mundo):
        """ 
        Para um círculo, qualquer handler que você puxar
        simplesmente redefine o raio com base na distância ao centro.
        """
        
        # Calcula o novo raio com base na distância do centro até o mouse
        dx = novo_x_mundo - self.centro[0]
        dy = novo_y_mundo - self.centro[1]
        
        novo_raio = np.linalg.norm((dx, dy))
        
        # (Bônus: Se estivéssemos fazendo escala não-uniforme, usaríamos o 
        # handler_index para saber qual 'self.escala' [x ou y] mudar)
        
        self.raio = novo_raio