import glfw
from OpenGL.GL import *
import math
from formas.Circulo import Circulo
from formas.Linha import Linha
from formas.PolignoNaoConvexo import PoligonoNaoConvexo
from formas.Quadrado import Quadrado

class JanelaGLFW:
    def __init__(self, largura=500, altura=500, left=-20, right=20, bottom=-20, top=20, titulo="Janela"):
        self.largura = largura
        self.altura = altura
        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top
        self.titulo = titulo

        self.formas = []
        self.current_tool = None
        self.drawing_state = 'idle'
        self.tentative = None
        self._window = None
        self._should_terminate = False

    # ---------------- Configuração da visualização ----------------
    def configure_visualization(self):
        width = max(1, self.largura)
        height = max(1, self.altura)
        glViewport(0, 0, width, height)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.left, self.right, self.bottom, self.top, -1.0, 1.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    # ---------------- Cancelar desenho ----------------
    def cancel_drawing(self):
        if self.drawing_state != 'idle':
            self.tentative = None
            self.drawing_state = 'idle'
            self.current_tool = None
            print("[tool] desenho cancelado.")
            return True
        return False

    # ---------------- Desenhar todas as formas ----------------
    def desenhar_formas(self):
        for item in list(self.formas):
            try:
                forma, x, y, color = item
                glColor3f(*color)
                forma.desenhar(x, y)
            except Exception:
                continue

        # ---- pré-visualização ----
        tent = getattr(self, 'tentative', None)
        if not tent:
            return

        glEnable(GL_LINE_STIPPLE)
        glLineStipple(1, 0x0F0F)
        glColor3f(0.6, 0.6, 0.6)

        if tent.get('tool') == 'circle':
            cx, cy = tent['center']
            r = tent.get('radius', 0)
            Circulo(r if r > 0 else 0.01).desenhar(x=cx, y=cy)

        elif tent.get('tool') == 'polygon':
            verts = tent.get('vertices', [])
            if len(verts) >= 2:
                glBegin(GL_LINE_STRIP)
                for vx, vy in verts:
                    glVertex2f(vx, vy)
                glEnd()

        elif tent.get('tool') == 'line':
            p1 = tent.get('p1')
            p2 = tent.get('p2')
            if p1 and p2:
                glBegin(GL_LINES)
                glVertex2f(*p1)
                glVertex2f(*p2)
                glEnd()


        elif tent.get('tool') == 'square':
            cx, cy = tent['center']
            lado = tent.get('lado', 0)
            if lado > 0:
                from formas.Quadrado import Quadrado
                Quadrado(lado).desenhar(x=cx, y=cy)


        elif tent.get('tool') == 'triangle':
            verts = tent.get('vertices', [])
            ptemp = tent.get('preview_point')
            if len(verts) >= 1:
                glBegin(GL_LINE_STRIP)
                for vx, vy in verts:
                    glVertex2f(vx, vy)
                if ptemp:
                    glVertex2f(*ptemp)
                glEnd()


        glDisable(GL_LINE_STIPPLE)
        glColor3f(1, 1, 1)

    # ---------------- Loop principal ----------------
    def run(self, render_fn, callback_handler=None):
        if not glfw.init():
            raise RuntimeError("Falha ao inicializar GLFW")

        self._window = glfw.create_window(self.largura, self.altura, self.titulo, None, None)
        if not self._window:
            glfw.terminate()
            raise RuntimeError("Falha ao criar janela GLFW")
        glfw.make_context_current(self._window)

        if callback_handler is not None:
            glfw.set_key_callback(self._window, callback_handler.on_key)
            glfw.set_mouse_button_callback(self._window, callback_handler.on_mouse)
            glfw.set_cursor_pos_callback(self._window, callback_handler.on_cursor_pos)
            glfw.set_window_size_callback(self._window, callback_handler.on_resize)

        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

        while not glfw.window_should_close(self._window) and not self._should_terminate:
            render_fn(self)
            glfw.swap_buffers(self._window)
            glfw.poll_events()

        glfw.terminate()

    def close(self):
        self._should_terminate = True
