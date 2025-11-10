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
        glVertex2f(self.x1, self.y1)
        glVertex2f(self.x2, self.y2)
        glEnd()
