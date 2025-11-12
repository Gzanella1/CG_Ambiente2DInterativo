import math
from formas.Forma import Forma
from OpenGL.GL import *

class Circulo(Forma):
    def __init__(self, raio: float):
        super().__init__("Círculo")
        self.raio = raio

    def area(self):
        return math.pi * (self.raio ** 2)

    def perimetro(self):
        return 2 * math.pi * self.raio

    def desenhar(self, x=0, y=0):
        glBegin(GL_LINE_LOOP)
        for i in range(0, 360, 5):
            ang = math.radians(i)
            glVertex2f(x + self.raio * math.cos(ang), y + self.raio * math.sin(ang))
        glEnd()

    def contem_ponto(self, x, y, cx, cy):
        """Retorna True se o ponto (x, y) estiver dentro do círculo centrado em (cx, cy)."""
        dx = x - cx
        dy = y - cy
        return (dx ** 2 + dy ** 2) <= (self.raio ** 2)
