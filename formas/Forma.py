from abc import ABC, abstractmethod

class Forma(ABC):
    def __init__(self, nome: str):
        self.nome = nome

    @abstractmethod
    def area(self):
        pass

    @abstractmethod
    def perimetro(self):
        pass

    def __str__(self):
        return f"{self.nome}"



    def contem_ponto(self, x, y, cx, cy):
        # verificar se (x,y) está dentro
        pass

    def get_vertices(self):
        # retornar lista [(vx, vy), ...]
        pass
