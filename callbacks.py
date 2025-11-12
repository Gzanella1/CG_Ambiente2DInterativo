import glfw
from tools import ToolManager
from selection_manager import SelectionManager

class Callbacks:


    def __init__(self, janela):
        self.janela = janela
        self.tools = ToolManager(janela)
        self.selection = SelectionManager(janela)
        janela.callbacks = self  # permite janela acessar seleção no desenho


    def window_to_world(self, x, y):
        xw = self.janela.left + (x / max(1, self.janela.largura)) * (self.janela.right - self.janela.left)
        yw = self.janela.top - (y / max(1, self.janela.altura)) * (self.janela.top - self.janela.bottom)
        return xw, yw

    def on_resize(self, win, width, height):
        self.janela.largura, self.janela.altura = max(1, width), max(1, height)
        print(f"[resize] {width}x{height}")


    def on_mouse(self, win, button, action, mods):
        mx, my = glfw.get_cursor_pos(win)
        xw, yw = self.window_to_world(mx, my)

        if button == glfw.MOUSE_BUTTON_LEFT:
            if action == glfw.PRESS:
                # Se não estiver desenhando, tenta selecionar
                if not self.janela.current_tool:
                    if self.selection.selecionar_forma(xw, yw):
                        self.selection.iniciar_arraste(xw, yw)
                    else:
                        # Clique fora limpa a seleção
                        self.selection.forma_selecionada = None
                else:
                    self.tools.handle_mouse_click(xw, yw, button)

            elif action == glfw.RELEASE:
                self.selection.finalizar_arraste()

    def on_cursor_pos(self, win, xpos, ypos):
        xw, yw = self.window_to_world(xpos, ypos)

        # arraste ativo
        if self.selection.arrastando:
            self.selection.mover_forma(xw, yw)
        # hover (preview)
        elif not self.janela.current_tool:
            self.selection.verificar_hover(xw, yw)
        # modo desenho
        elif self.janela.tentative:
            self.tools.handle_mouse_move(xw, yw)


    def on_key(self, win, key, scancode, action, mods):
        if action != glfw.PRESS:
            return

        if key == glfw.KEY_ESCAPE:
            if not self.janela.cancel_drawing():
                glfw.set_window_should_close(win, True)

        elif key == glfw.KEY_C:
            self.janela.formas.clear()
            print("[debug] formas limpas.")

        elif key == glfw.KEY_1:
            self.tools.activate_tool('circle')

        elif key == glfw.KEY_2:
            self.tools.activate_tool('polygon')

        elif key == glfw.KEY_3:
            self.tools.activate_tool('line')

        elif key == glfw.KEY_4:
            self.tools.activate_tool('square')

        elif key == glfw.KEY_5:
            self.tools.activate_tool('triangle')