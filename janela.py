# janela.py
import glfw
from OpenGL.GL import *
import callbacks # Importa o módulo de callbacks
from tools import ToolManager
from selection_manager import SelectionManager

class Janela:
    def __init__(self, width, height, title):
        self.width = width
        self.height = height
        self.window = glfw.create_window(width, height, title, None, None)
        if not self.window:
            glfw.terminate()
            raise Exception("Falha ao criar janela GLFW")

        glfw.make_context_current(self.window)
        # Define o ponteiro do usuário para esta instância da classe
        glfw.set_window_user_pointer(self.window, self)
        
        # Configura a projeção ortográfica 2D
        self.setup_projection()

        # Estado da aplicação
        self.formas = [] # Lista de todas as formas desenhadas
        
        # Inicializa os gerenciadores
        self.tool_manager = ToolManager(self)
        self.selection_manager = SelectionManager(self)
        
        # Configura os callbacks
        self.set_callbacks()

    def set_callbacks(self):
        glfw.set_key_callback(self.window, callbacks.key_callback)
        glfw.set_mouse_button_callback(self.window, callbacks.mouse_button_callback)
        glfw.set_cursor_pos_callback(self.window, callbacks.cursor_pos_callback)
        # (Callback de redimensionamento também é importante)
        glfw.set_framebuffer_size_callback(self.window, self.framebuffer_size_callback)

    def setup_projection(self):
        glViewport(0, 0, self.width, self.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # Mapeia coordenadas do mundo (0,0) no canto inferior esquerdo
        # e (width, height) no canto superior direito
        glOrtho(0, self.width, 0, self.height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
    def converter_coords_tela_para_mundo(self, x_tela, y_tela):
        # Em nossa projeção glOrtho simples, y precisa ser invertido
        x_mundo = x_tela
        y_mundo = self.height - y_tela # GLFW (0,0) é topo-esquerda
        return x_mundo, y_mundo

    def adicionar_forma(self, forma):
        self.formas.append(forma)

    def framebuffer_size_callback(self, window, width, height):
        if height == 0: return # Evita divisão por zero
        self.width = width
        self.height = height
        self.setup_projection() # Reconfigura a projeção com o novo tamanho

    def run(self):
        while not glfw.window_should_close(self.window):
            # Limpa a tela
            glClear(GL_COLOR_BUFFER_BIT)
            glClearColor(0.1, 0.1, 0.1, 1.0) # Fundo escuro
            
            # 1. Desenha todas as formas finalizadas
            for forma in self.formas:
                forma.desenhar()

            # 2. Desenha o preview da ferramenta ativa (se houver)
            if self.tool_manager.forma_preview:
                self.tool_manager.forma_preview.desenhar_preview()
            
            # (Note: O SelectionManager desenha seus visuais
            # dentro do método `forma.desenhar()`)

            # Troca os buffers e processa eventos
            glfw.swap_buffers(self.window)
            glfw.poll_events()




            # --- ADICIONE ESTE MÉTODO ---
    def remover_forma(self, forma):
        """ Remove uma forma da lista principal de renderização. """
        if forma in self.formas:
            self.formas.remove(forma)
        else:
            print("Aviso: Tentativa de remover forma que não está na lista.")
    # -----------------------------