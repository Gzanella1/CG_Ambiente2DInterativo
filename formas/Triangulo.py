from formas.Forma import Forma
from OpenGL.GL import *
import math

class Triangulo(Forma):
    def __init__(self, v1, v2, v3):
        super().__init__("Triângulo")
        self.v1, self.v2, self.v3 = v1, v2, v3

    def area(self):
        x1, y1 = self.v1
        x2, y2 = self.v2
        x3, y3 = self.v3
        return abs((x1*(y2 - y3) + x2*(y3 - y1) + x3*(y1 - y2)) / 2)

    def perimetro(self):
        return (
            math.dist(self.v1, self.v2) +
            math.dist(self.v2, self.v3) +
            math.dist(self.v3, self.v1)
        )

    def desenhar(self, x=0, y=0):
        glBegin(GL_LINE_LOOP)
        glVertex2f(self.v1[0] + x, self.v1[1] + y)
        glVertex2f(self.v2[0] + x, self.v2[1] + y)
        glVertex2f(self.v3[0] + x, self.v3[1] + y)
        glEnd()

    def contem_ponto(self, x, y, cx, cy):
        """Retorna True se o ponto (x, y) estiver dentro do triângulo deslocado por (cx, cy)."""
        # aplica deslocamento
        x1, y1 = self.v1[0] + cx, self.v1[1] + cy
        x2, y2 = self.v2[0] + cx, self.v2[1] + cy
        x3, y3 = self.v3[0] + cx, self.v3[1] + cy

        # área total do triângulo
        A = abs((x1*(y2 - y3) + x2*(y3 - y1) + x3*(y1 - y2)) / 2.0)
        # áreas parciais com o ponto
        A1 = abs((x*(y2 - y3) + x2*(y3 - y) + x3*(y - y2)) / 2.0)
        A2 = abs((x1*(y - y3) + x*(y3 - y1) + x3*(y1 - y)) / 2.0)
        A3 = abs((x1*(y2 - y) + x2*(y - y1) + x*(y1 - y2)) / 2.0)

        return abs(A - (A1 + A2 + A3)) < 1e-1  # tolerância numérica
