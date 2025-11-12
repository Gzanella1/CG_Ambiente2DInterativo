from formas.Forma import Forma
from OpenGL.GL import *
import math

class Linha(Forma):
    def __init__(self, x1: float, y1: float, x2: float, y2: float):
        super().__init__("Linha")
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2

    def area(self):
        return 0.0

    def perimetro(self):
        return math.dist((self.x1, self.y1), (self.x2, self.y2))

    def desenhar(self, x=0, y=0):
        glBegin(GL_LINES)
        glVertex2f(self.x1 + x, self.y1 + y)
        glVertex2f(self.x2 + x, self.y2 + y)
        glEnd()

    def contem_ponto(self, x, y, cx, cy):
        """Verifica se o ponto (x, y) está próximo da linha (x1, y1)-(x2, y2) deslocada por (cx, cy)."""
        # deslocar a linha
        x1, y1 = self.x1 + cx, self.y1 + cy
        x2, y2 = self.x2 + cx, self.y2 + cy

        # calcular distância ponto-linha (fórmula da distância entre ponto e segmento)
        dx = x2 - x1
        dy = y2 - y1
        if dx == dy == 0:
            return math.dist((x, y), (x1, y1)) < 5  # ponto único
        t = ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)
        t = max(0, min(1, t))
        px = x1 + t * dx
        py = y1 + t * dy
        distancia = math.dist((x, y), (px, py))

        # tolerância de clique
        return distancia <= 5.0
