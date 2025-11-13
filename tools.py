# tools.py
from formas.Circulo import Circulo
from formas.Quadrado import Quadrado # (Você precisa criar estes)
from formas.Quadrado import Quadrado 
from formas.Linha import Linha       # <-- ADICIONE
from formas.Triangulo import Triangulo # <-- ADICIONE
from formas.PolignoNaoConvexo import PolignoNaoConvexo # <--- CORRETO (com 'g')
# ... etc ...
import numpy as np

class ToolManager:
    def __init__(self, janela_pai):
        self.janela_pai = janela_pai # Referência à janela (para add formas)
        self.ferramenta_ativa = None  # 'circulo', 'quadrado', etc.
        self.desenhando = False
        self.forma_preview = None
        self.ponto_inicial = None

    def set_ferramenta(self, ferramenta):
        self.ferramenta_ativa = ferramenta
        self.desenhando = False
        self.forma_preview = None
        self.janela_pai.selection_manager.desselecionar_tudo()
        print(f"Ferramenta ativa: {ferramenta}")

# tools.py

    def handle_click(self, x, y, action):
        
        # --- LÓGICA ESPECIAL DO POLÍGONO ---
        if self.ferramenta_ativa == 'poligono':
            if action == "PRESS":
                
                # ### CORREÇÃO DA LINHA FANTASMA (1/2) ###
                # Atualiza a posição do mouse IMEDIATAMENTE no clique.
                self.ultimo_mouse_pos_mundo = (x, y) 
                
                if not self.desenhando:
                    # 1º clique: Inicia o polígono
                    self.desenhando = True
                    self.ponto_inicial = (x, y) 
                    self.forma_preview = PolignoNaoConvexo(centro=self.ponto_inicial) # <--- CORRETO (com 'g')
                else:
                    # 2º clique em diante:
                    dist_inicio = np.linalg.norm(np.array((x, y)) - self.ponto_inicial)
                    if dist_inicio < 10.0: # Hitbox de 10 pixels
                        self.finalizar_desenho()
                    else:
                        self.forma_preview.adicionar_vertice_pelo_mundo(x, y)
            
            return True 
        # --- FIM DA LÓGICA DO POLÍGONO ---

        if self.ferramenta_ativa is None:
            return False 

        # Lógica Clicar-Arrastar-Soltar (Circulo, Quadrado, etc.)
        if action == "PRESS" and not self.desenhando:
            self.desenhando = True
            self.ponto_inicial = (x, y)
            
            # ### CORREÇÃO DA LINHA FANTASMA (2/2) ###
            # Atualiza aqui também, para o caso de
            # você ter uma forma (ex: Linha) que usa
            # 'ultimo_mouse_pos_mundo' no seu preview.
            self.ultimo_mouse_pos_mundo = (x, y) 
            
            if self.ferramenta_ativa == 'circulo':
                self.forma_preview = Circulo(centro=self.ponto_inicial, raio=0.0)
            elif self.ferramenta_ativa == 'quadrado':
                self.forma_preview = Quadrado(centro=self.ponto_inicial, meio_lado=0.0)
            elif self.ferramenta_ativa == 'linha':
                self.forma_preview = Linha(centro=self.ponto_inicial)
            elif self.ferramenta_ativa == 'triangulo':
                self.forma_preview = Triangulo(centro=self.ponto_inicial, raio_circunscrito=0.0)
            
            return True

        elif action == "RELEASE" and self.desenhando:
            self.desenhando = False
            if self.forma_preview and self.forma_preview.is_valid():
                 self.janela_pai.adicionar_forma(self.forma_preview)
            
            self.forma_preview = None
            self.ponto_inicial = None
            return True
            
        return False


    def handle_drag(self, x, y):
        if self.desenhando and self.forma_preview:
            # Arrastar: Atualiza o tamanho da forma de preview
            dist_x = x - self.ponto_inicial[0]
            dist_y = y - self.ponto_inicial[1]

            raio = np.linalg.norm((dist_x, dist_y))
            
            if isinstance(self.forma_preview, Circulo):
                # Raio é a distância do centro ao mouse
                raio = np.linalg.norm(np.array((x, y)) - self.ponto_inicial)
                self.forma_preview.raio = raio
          
            # --- ADICIONE ESTE BLOCO ---
            elif isinstance(self.forma_preview, Quadrado):
                # O 'meio_lado' será o maior entre dx e dy
                # Isso faz um quadrado "perfeito"
                self.forma_preview.meio_lado = max(dist_x, dist_y)
            # ---------------------------
        # --- ADICIONE ESTES BLOCOS ---
            elif isinstance(self.forma_preview, Linha):
                # A linha usa o vetor (dx, dy) como seu 'vetor_metade'
                self.forma_preview.vetor_metade = np.array([dist_x, dist_y])
            
            elif isinstance(self.forma_preview, Triangulo):
                # O triângulo usa o 'raio' como o círculo
                self.forma_preview.raio_circunscrito = raio
            # -----------------------------
            
            return True # Evento consumido
        return False
    

# tools.py

    # ... (depois do handle_drag) ...

    def finalizar_desenho(self):
        """ Função especial para finalizar polígonos (pelo teclado) """
        if self.ferramenta_ativa == 'poligono' and self.desenhando:
            print("Finalizando polígono...")
            if self.forma_preview and self.forma_preview.is_valid():
                self.janela_pai.adicionar_forma(self.forma_preview)
            
            # Limpa o estado
            self.desenhando = False
            self.forma_preview = None
            self.ponto_inicial = None