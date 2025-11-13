# selection_manager.py
import numpy as np
import math  # <--- IMPORTANTE! Precisamos de 'atan2' e 'degrees'
import glfw  # <--- IMPORTANTE! Precisamos checar o 'Shift' no drag

class SelectionManager:
    def __init__(self, janela_pai):
        self.janela_pai = janela_pai 
        self.formas_selecionadas = [] 
        self.acao_atual = 'IDLE' 
        self.ultimo_mouse_pos = (0, 0)
        
        self.multi_select_mode = False 
        
        # Variáveis de transformação (só afetam 1 forma)
        self.angulo_inicial_mouse = 0.0
        self.rotacao_original = 0.0
    
    def desselecionar_tudo(self):
        """ Limpa a lista e atualiza o estado de todas as formas. """
        for forma in self.formas_selecionadas:
            forma.selecionada = False
        self.formas_selecionadas.clear()
        self.acao_atual = 'IDLE' # Sempre reseta a ação

    def get_pivo(self):
        """ Retorna a forma "pivô" (para Rotação/Redimensionamento) """
        if len(self.formas_selecionadas) == 1:
            return self.formas_selecionadas[0]
        return None

    def toggle_multi_select_mode(self):
        """ Esta é a função chamada pela tecla 'M' """
        self.multi_select_mode = not self.multi_select_mode
        self.acao_atual = 'IDLE' # Cancela qualquer ação ao trocar de modo
        
        if self.multi_select_mode:
            print("[MODO] Multi-Seleção: ATIVADO (Clique para adicionar/remover)")
        else:
            print("[MODO] Multi-Seleção: DESATIVADO (Clique e arraste para mover)")
            # Ao sair do modo 'M', não limpamos a seleção.
            # Ela fica pronta para ser movida.

    def handle_click(self, x, y, action, mods):
        if action != "PRESS":
            if action == "RELEASE":
                self.acao_atual = 'IDLE'
            return False

        # --- Lógica de Clique (PRESS) ---
        self.ultimo_mouse_pos = (x, y)
        is_shift_pressed = (mods & glfw.MOD_SHIFT) 
        
        # 1. Tenta achar uma forma no clique
        forma_clicada = None
        for forma in reversed(self.janela_pai.formas): 
            if forma.foi_clicada((x, y)):
                forma_clicada = forma
                break

        # --- O CÉREBRO DA NOVA LÓGICA ---
        if self.multi_select_mode:
            # --- MODO 'M' LIGADO: SÓ SELECIONA ---
            if forma_clicada:
                # Achou uma forma. Faz o "toggle".
                if forma_clicada in self.formas_selecionadas:
                    forma_clicada.selecionada = False
                    self.formas_selecionadas.remove(forma_clicada)
                else:
                    forma_clicada.selecionada = True
                    self.formas_selecionadas.append(forma_clicada)
            
            self.acao_atual = 'IDLE' # NUNCA move no modo M
            return True
        
        else:
            # --- MODO 'M' DESLIGADO: AGE (MOVE, GIRA, ETC) ---
            
            # 1. Ações Especiais (Rotação/Resize - só com 1 forma)
            pivo = self.get_pivo()
            if pivo:
                handler_clicado = pivo.click_em_handler(x, y)
                # 1a. ROTAÇÃO (Shift + Clique)
                if is_shift_pressed and handler_clicado is None and forma_clicada == pivo:
                    self.acao_atual = 'ROTATING'
                    self.rotacao_original = pivo.rotacao
                    centro_forma = pivo.centro
                    dx = x - centro_forma[0]; dy = y - centro_forma[1]
                    self.angulo_inicial_mouse = math.atan2(dy, dx)
                    return True
                
                # 1b. REDIMENSIONAMENTO (Clique em handler)
                if handler_clicado is not None:
                    self.acao_atual = ('RESIZING', handler_clicado) 
                    return True
            
            # 2. Lógica de SELEÇÃO/MOVIMENTO
            if forma_clicada:
                if forma_clicada not in self.formas_selecionadas:
                    # Clicou em algo novo, sem Shift/M
                    self.desselecionar_tudo()
                    forma_clicada.selecionada = True
                    self.formas_selecionadas.append(forma_clicada)
                
                # Prepara para mover (seja 1 ou um grupo)
                self.acao_atual = 'MOVING'
                return True
            
            # 3. Clicou no nada
            self.desselecionar_tudo()
            return False
        
    def handle_drag(self, x, y):
        dx = x - self.ultimo_mouse_pos[0]
        dy = y - self.ultimo_mouse_pos[1]
        
        # Se estiver no Modo M, NUNCA faz nada
        if self.multi_select_mode:
            self.ultimo_mouse_pos = (x, y)
            return False

        pivo = self.get_pivo()

        # 1. Está ROTACIONANDO?
        if self.acao_atual == 'ROTATING' and pivo:
            # (Lógica de rotação - sem mudanças)
            shift_held = glfw.get_key(self.janela_pai.window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS or \
                         glfw.get_key(self.janela_pai.window, glfw.KEY_RIGHT_SHIFT) == glfw.PRESS
            if shift_held:
                centro_forma = pivo.centro; dx_atual = x - centro_forma[0]; dy_atual = y - centro_forma[1]
                angulo_atual_mouse = math.atan2(dy_atual, dx_atual)
                delta_angulo_rad = angulo_atual_mouse - self.angulo_inicial_mouse
                pivo.rotacao = self.rotacao_original + math.degrees(delta_angulo_rad)
                self.ultimo_mouse_pos = (x, y); return True
            else:
                self.acao_atual = 'IDLE'
            
        # 2. Está REDIMENSIONANDO?
        elif isinstance(self.acao_atual, tuple) and self.acao_atual[0] == 'RESIZING' and pivo:
            # (Lógica de redimensionar - sem mudanças)
            handler_index = self.acao_atual[1]
            pivo.redimensionar(handler_index, x, y)
            self.ultimo_mouse_pos = (x, y); return True 
            
        # 3. Está MOVENDO? (A Mágica)
        elif self.acao_atual == 'MOVING' and self.formas_selecionadas:
            for forma in self.formas_selecionadas:
                forma.mover(dx, dy)
            self.ultimo_mouse_pos = (x, y); return True 
            
        self.ultimo_mouse_pos = (x, y) 
        return False
  

  # --- ADICIONE ESTE MÉTODO ---
    def delete_selected(self):
        """ Deleta todas as formas atualmente na lista de seleção. """
        
        # Pega uma cópia da lista de formas a deletar
        formas_para_deletar = list(self.formas_selecionadas)
        
        if not formas_para_deletar:
            print("Nada selecionado para deletar.")
            return

        print(f"Deletando {len(formas_para_deletar)} formas...")

        # 1. Limpa a seleção (esvazia self.formas_selecionadas)
        self.desselecionar_tudo()
        
        # 2. Agora, deleta as formas da lista principal da janela
        for forma in formas_para_deletar:
            self.janela_pai.remover_forma(forma)
    # -----------------------------