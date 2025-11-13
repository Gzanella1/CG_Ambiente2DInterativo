# formas/PolignoNaoConvexo.py
from formas.Forma import Forma
from OpenGL.GL import *
import numpy as np
import math
# NÓS NÃO PRECISAMOS DE 'abstractmethod' AQUI, PORQUE NÃO O USAMOS!

class PolignoNaoConvexo(Forma):

    # 1. __init__
    def __init__(self, centro, cor=(1.0, 1.0, 1.0)):
        super().__init__(centro, cor)
        self.vertices_locais = [np.array([0.0, 0.0])] 

    def adicionar_vertice_pelo_mundo(self, x_mundo, y_mundo):
        p_local = self.transformar_ponto_mundo_para_local((x_mundo, y_mundo))
        self.vertices_locais.append(p_local)

    def desenhar_corpo(self, modo):
        glBegin(modo)
        for v_local in self.vertices_locais:
            glVertex2f(v_local[0], v_local[1])
        glEnd()

    # 2. desenhar
    def desenhar(self):
        glPushMatrix()
        self.aplicar_transformacoes() # O método da "mãe" faz tudo
        glColor3f(*self.cor)
        self.desenhar_corpo(GL_LINE_LOOP) 
        glPopMatrix()
        
        self.desenhar_bounding_box()
        self.desenhar_handlers()

    # 3. desenhar_preview
    def desenhar_preview(self, mouse_pos_mundo=(0,1)):
        glPushMatrix()
        glColor3f(0.8, 0.8, 0.8)
        
        glPushAttrib(GL_ENABLE_BIT)
        glLineStipple(1, 0xAAAA)
        glEnable(GL_LINE_STIPPLE)

        glBegin(GL_LINE_LOOP)
        # Desenha os vértices já transformados no espaço do MUNDO
        for v_local in self.vertices_locais:
            v_mundo = self.transformar_ponto_local(v_local)
            glVertex2f(*v_mundo)
        
        # E a linha elástica até o mouse
        glVertex2f(*mouse_pos_mundo)
        glEnd()
        
        glPopAttrib()
        glPopMatrix()

    # 4. is_valid
    def is_valid(self):
        return len(self.vertices_locais) > 2 

    # 5. get_bounding_box
    def get_bounding_box(self):
        handlers = self.get_handlers() 
        if not handlers:
            p_mundo = self.transformar_ponto_local((0,0))
            return (p_mundo[0], p_mundo[1], p_mundo[0], p_mundo[1])

        x_coords = [h[0] for h in handlers]
        y_coords = [h[1] for h in handlers]
        
        return (min(x_coords), min(y_coords), max(x_coords), max(y_coords))

    # 6. get_handlers
    def get_handlers(self):
        return [self.transformar_ponto_local(v_local) for v_local in self.vertices_locais]

    # 7. redimensionar
    def redimensionar(self, handler_index, novo_x_mundo, novo_y_mundo):
        p_local = self.transformar_ponto_mundo_para_local((novo_x_mundo, novo_y_mundo))

        if handler_index == 0:
            antigo_p_mundo = self.transformar_ponto_local(self.vertices_locais[0])
            dx = novo_x_mundo - antigo_p_mundo[0]
            dy = novo_y_mundo - antigo_p_mundo[1]
            self.mover(dx, dy)
        else:
            if handler_index >= 0 and handler_index < len(self.vertices_locais):
                self.vertices_locais[handler_index] = p_local

    # 8. foi_clicada
    def foi_clicada(self, ponto_mundo):
        p_local = self.transformar_ponto_mundo_para_local(ponto_mundo)
        
        n = len(self.vertices_locais)
        if n < 3: return False 

        inside = False
        p_x, p_y = p_local

        j = n - 1 
        for i in range(n):
            vi_x, vi_y = self.vertices_locais[i]
            vj_x, vj_y = self.vertices_locais[j]
            
            if ((vi_y > p_y) != (vj_y > p_y)) and \
               (p_x < (vj_x - vi_x) * (p_y - vi_y) / (vj_y - vi_y) + vi_x):
                inside = not inside
            j = i 
        return inside