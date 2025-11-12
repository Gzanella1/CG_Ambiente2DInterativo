from formas.Forma import Forma
from OpenGL.GL import *

class Quadrado(Forma):
    def __init__(self, lado: float):
        super().__init__("Quadrado")
        self.lado = lado

    def area(self):
        return self.lado ** 2

    def perimetro(self):
        return 4 * self.lado

    def desenhar(self, x=0, y=0):
        """Desenha o quadrado centrado em (x, y)."""
        half = self.lado / 2
        glBegin(GL_LINE_LOOP)
        glVertex2f(x - half, y - half)
        glVertex2f(x + half, y - half)
        glVertex2f(x + half, y + half)
        glVertex2f(x - half, y + half)
        glEnd()



# Implementação dos métodos abstratos para seleção
    def contem_ponto(self, x, y, cx, cy):
        half = self.lado / 2
        return (cx - half <= x <= cx + half) and (cy - half <= y <= cy + half)

    def get_vertices(self):
        h = self.lado / 2
        return [(-h, -h), (h, -h), (h, h), (-h, h)]
    


    def get_bounding_box(self, cx, cy):
        half = self.lado / 2
        return (cx - half, cy - half, cx + half, cy + half)
    

    def desenhar_bounding_box(self, cx, cy):
        """Desenha o contorno tracejado amarelo e os handles."""
        x_min, y_min, x_max, y_max = self.get_bounding_box(cx, cy)

        # --- Contorno tracejado amarelo ---
        glColor3f(1.0, 1.0, 0.0)  # amarelo
        glEnable(GL_LINE_STIPPLE)
        glLineStipple(1, 0xAAAA)
        glBegin(GL_LINE_LOOP)
        glVertex2f(x_min, y_min)
        glVertex2f(x_max, y_min)
        glVertex2f(x_max, y_max)
        glVertex2f(x_min, y_max)
        glEnd()
        glDisable(GL_LINE_STIPPLE)

        # --- Handles nos cantos ---
        glColor3f(1.0, 0.0, 0.0)  # vermelho
        tamanho = 5
        for (hx, hy) in [
            (x_min, y_min), (x_max, y_min),
            (x_max, y_max), (x_min, y_max)
        ]:
            glBegin(GL_QUADS)
            glVertex2f(hx - tamanho, hy - tamanho)
            glVertex2f(hx + tamanho, hy - tamanho)
            glVertex2f(hx + tamanho, hy + tamanho)
            glVertex2f(hx - tamanho, hy + tamanho)
            glEnd()


    