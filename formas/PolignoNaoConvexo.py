import math
from formas.Forma import Forma
from OpenGL.GL import *

class PoligonoNaoConvexo(Forma):
    def __init__(self, vertices: list[tuple[float, float]]):
        super().__init__("Polígono Não Convexo")
        self.vertices = vertices

    def area(self):
        n = len(self.vertices)
        soma1 = sum(self.vertices[i][0] * self.vertices[(i+1) % n][1] for i in range(n))
        soma2 = sum(self.vertices[i][1] * self.vertices[(i+1) % n][0] for i in range(n))
        return abs(soma1 - soma2) / 2

    def perimetro(self):
        n = len(self.vertices)
        return sum(math.dist(self.vertices[i], self.vertices[(i+1) % n]) for i in range(n))

    def desenhar(self, x=0, y=0):
        glBegin(GL_LINE_LOOP)
        for vx, vy in self.vertices:
            glVertex2f(vx + x, vy + y)
        glEnd()

    def contem_ponto(self, x, y, cx, cy):
        """Verifica se o ponto (x, y) está dentro do polígono deslocado em (cx, cy)."""
        dentro = False
        n = len(self.vertices)
        for i in range(n):
            x1, y1 = self.vertices[i]
            x2, y2 = self.vertices[(i + 1) % n]

            # aplica deslocamento
            x1 += cx
            y1 += cy
            x2 += cx
            y2 += cy

            # checa interseção com a linha horizontal do ponto
            if ((y1 > y) != (y2 > y)) and \
               (x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-10) + x1):
                dentro = not dentro
        return dentro
