# formas/Quadrado.py
from formas.Forma import Forma
from OpenGL.GL import *
import numpy as np

class Quadrado(Forma):
    def __init__(self, centro, meio_lado=0.0, cor=(1.0, 1.0, 1.0)):
        super().__init__(centro, cor)
        # 'meio_lado' é a distância do centro a uma das arestas.
        self.meio_lado = meio_lado

    def desenhar_corpo(self, modo):
        """ Helper para desenhar o quadrado (preenchido ou linha). """
        
        # Vértices relativos ao centro (0,0)
        ml = self.meio_lado # Apelido curto
        
        glBegin(modo)
        glVertex2f(-ml, -ml) # Canto inferior esquerdo
        glVertex2f( ml, -ml) # Canto inferior direito
        glVertex2f( ml,  ml) # Canto superior direito
        glVertex2f(-ml,  ml) # Canto superior esquerdo
        glEnd()

    def desenhar(self):
        glPushMatrix()
        self.aplicar_transformacoes() # Aplica translação/rotação/escala
        
        glColor3f(*self.cor)
        # Usamos GL_QUADS para um quadrado preenchido
        self.desenhar_corpo(GL_QUADS) 
        
        glPopMatrix()
        
        # Desenha BBox e Handlers (fora da matriz de transformação da forma)
        self.desenhar_bounding_box()
        self.desenhar_handlers()


    def desenhar_preview(self):
        glPushMatrix()
        # O preview só precisa de translação
        glTranslatef(self.centro[0], self.centro[1], 0.0)
        
        glColor3f(0.8, 0.8, 0.8) # Cor de preview
        
        glPushAttrib(GL_ENABLE_BIT)
        glLineStipple(1, 0xAAAA) # Padrão de tracejado
        glEnable(GL_LINE_STIPPLE)
        
        # Usamos GL_LINE_LOOP para o contorno
        self.desenhar_corpo(GL_LINE_LOOP)
        
        glPopAttrib()
        glPopMatrix()

    def foi_clicada(self, ponto):
        # ATENÇÃO: Lógica simplificada que NÃO considera rotação.
        # A lógica correta exige transformar o 'ponto' para o 
        # sistema de coordenadas local do quadrado (matriz inversa).
        
        # Versão simples (Axis-Aligned Bounding Box):
        meio_lado_x = self.meio_lado * self.escala[0]
        meio_lado_y = self.meio_lado * self.escala[1]
        
        min_x = self.centro[0] - meio_lado_x
        max_x = self.centro[0] + meio_lado_x
        min_y = self.centro[1] - meio_lado_y
        max_y = self.centro[1] + meio_lado_y

        return (min_x <= ponto[0] <= max_x) and \
               (min_y <= ponto[1] <= max_y)
        
    def get_bounding_box(self):
        # ATENÇÃO: Simplificado, não considera rotação.
        # A BBox de um quadrado rotacionado é maior que o quadrado.
        
        meio_lado_x = self.meio_lado * self.escala[0]
        meio_lado_y = self.meio_lado * self.escala[1]
        
        min_x = self.centro[0] - meio_lado_x
        min_y = self.centro[1] - meio_lado_y
        max_x = self.centro[0] + meio_lado_x
        max_y = self.centro[1] + meio_lado_y
        return (min_x, min_y, max_x, max_y)
    


    # ... (fim do get_bounding_box) ...

    def is_valid(self):
        """ Um quadrado é válido se seu 'meio_lado' for maior que um pixel. """
        return self.meio_lado > 1
    


    # formas/Quadrado.py
# ... (depois do método 'is_valid') ...

    def get_handlers(self):
        """ 
        Retorna os 4 cantos da Bounding Box.
        """
        # (Lógica copiada de 'get_bounding_box')
        meio_lado_x = self.meio_lado * self.escala[0]
        meio_lado_y = self.meio_lado * self.escala[1]
        
        min_x = self.centro[0] - meio_lado_x
        max_x = self.centro[0] + meio_lado_x
        min_y = self.centro[1] - meio_lado_y
        max_y = self.centro[1] + meio_lado_y

        return [
            (min_x, min_y), (max_x, min_y),
            (max_x, max_y), (min_x, max_y)
        ]

    def redimensionar(self, handler_index, novo_x_mundo, novo_y_mundo):
        """ 
        Para um Quadrado, qualquer handler redefine o 'meio_lado'
        com base na maior distância (X ou Y) ao centro.
        """
        # Distância do centro ao mouse
        dx = novo_x_mundo - self.centro[0]
        dy = novo_y_mundo - self.centro[1]
        
        # Para manter um quadrado perfeito, usamos a maior distância
        self.meio_lado = max(abs(dx), abs(dy))