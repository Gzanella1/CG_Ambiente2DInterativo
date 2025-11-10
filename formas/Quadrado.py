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