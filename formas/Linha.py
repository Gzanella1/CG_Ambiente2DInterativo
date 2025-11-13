# formas/Linha.py
from formas.Forma import Forma
from OpenGL.GL import *
import numpy as np

class Linha(Forma):
    def __init__(self, centro, vetor_metade=np.array([0.0, 0.0]), cor=(1.0, 1.0, 1.0)):
        super().__init__(centro, cor)
        # 'vetor_metade' é o vetor do centro até uma das pontas
        self.vetor_metade = np.array(vetor_metade, dtype=np.float32)

    def get_endpoints_locais(self):
        """ Retorna os pontos inicial e final relativos ao centro (0,0) """
        p1 = -self.vetor_metade
        p2 = self.vetor_metade
        return p1, p2

    def desenhar_corpo(self, modo):
        p1, p2 = self.get_endpoints_locais()
        
        glBegin(modo)
        glVertex2f(*p1)
        glVertex2f(*p2)
        glEnd()

    def desenhar(self):
        glPushMatrix()
        self.aplicar_transformacoes() # Aplica translação/rotação/escala
        
        glColor3f(*self.cor)
        self.desenhar_corpo(GL_LINES)
        
        glPopMatrix()
        
        # Bounding box e handlers para a linha
        self.desenhar_bounding_box()
        self.desenhar_handlers()


    def desenhar_preview(self):
        glPushMatrix()
        glTranslatef(self.centro[0], self.centro[1], 0.0)
        
        glColor3f(0.8, 0.8, 0.8) # Cor de preview
        
        glPushAttrib(GL_ENABLE_BIT)
        glLineStipple(1, 0xAAAA) # Padrão de tracejado
        glEnable(GL_LINE_STIPPLE)
        
        self.desenhar_corpo(GL_LINES)
        
        glPopAttrib()
        glPopMatrix()

    def is_valid(self):
        """ Uma linha é válida se seu comprimento (2 * norma do vetor) for > 1 pixel """
        return np.linalg.norm(self.vetor_metade) > 0.5 # (norma > 0.5 = comprimento > 1)

    def foi_clicada(self, ponto):
        # ATENÇÃO: Detecção de clique em linha é complexa (distância ponto-segmento).
        # Vamos usar a Bounding Box como uma aproximação 'grosseira'.
        min_x, min_y, max_x, max_y = self.get_bounding_box()
        
        # Adiciona uma pequena "gordura" à BBox para facilitar o clique
        gordura = 5.0 
        return (min_x - gordura <= ponto[0] <= max_x + gordura) and \
               (min_y - gordura <= ponto[1] <= max_y + gordura)
        
    def get_bounding_box(self):
        # ATENÇÃO: Simplificado (não considera rotação/escala complexa)
        p1, p2 = self.get_endpoints_locais()
        
        # Aplica escala manualmente
        p1_scaled = p1 * self.escala
        p2_scaled = p2 * self.escala
        
        # (Rotação seria aplicada aqui com matrizes)

        # Adiciona a translação do centro
        p1_world = p1_scaled + self.centro
        p2_world = p2_scaled + self.centro

        min_x = min(p1_world[0], p2_world[0])
        min_y = min(p1_world[1], p2_world[1])
        max_x = max(p1_world[0], p2_world[0])
        max_y = max(p1_world[1], p2_world[1])
        
        return (min_x, min_y, max_x, max_y)
    


# formas/Linha.py
# ... (depois do método 'is_valid') ...

    def get_pontos_mundo(self):
        """ Helper que retorna as coordenadas globais das duas pontas """
        # ATENÇÃO: Ignorando self.escala e self.rotacao por simplicidade
        # A lógica correta exigiria multiplicação de matriz
        p1 = self.centro - self.vetor_metade
        p2 = self.centro + self.vetor_metade
        return p1, p2

    def get_handlers(self):
        """ 
        Os handlers da Linha são suas duas pontas.
        """
        p1, p2 = self.get_pontos_mundo()
        return [p1, p2]

    def redimensionar(self, handler_index, novo_x_mundo, novo_y_mundo):
        """ 
        Para uma Linha, o redimensionamento move uma ponta
        enquanto a outra fica fixa, re-calculando o centro.
        """
        p1, p2 = self.get_pontos_mundo()
        ponto_movel_novo = np.array([novo_x_mundo, novo_y_mundo])

        if handler_index == 0: # Clicou na ponta p1
            ponto_fixo = p2
        elif handler_index == 1: # Clicou na ponta p2
            ponto_fixo = p1
        else:
            return # Index de handler inválido

        # O novo centro da linha é o ponto médio entre 
        # a ponta fixa e a nova posição do mouse
        self.centro = (ponto_fixo + ponto_movel_novo) / 2.0
        
        # O novo vetor_metade é o vetor do novo centro
        # até a ponta que está sendo movida
        self.vetor_metade = ponto_movel_novo - self.centro