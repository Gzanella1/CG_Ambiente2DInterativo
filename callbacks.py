# callbacks.py
import glfw

# Função para obter a instância da janela a partir do callback
def get_janela(window_ptr):
    return glfw.get_window_user_pointer(window_ptr)

def key_callback(window_ptr, key, scancode, action, mods):
    janela = get_janela(window_ptr)
    if action == glfw.PRESS:
        # Lógica de finalização ANTES de trocar de ferramenta
        if key != glfw.KEY_2 and janela.tool_manager.ferramenta_ativa == 'poligono':
             janela.tool_manager.finalizar_desenho()


        if key == glfw.KEY_1:
            janela.tool_manager.set_ferramenta('circulo')
        
        elif key == glfw.KEY_2:
            # Lógica do Polígono
            if janela.tool_manager.ferramenta_ativa != 'poligono':
                # Se não era polígono, ativa
                janela.tool_manager.set_ferramenta('poligono')
            else:
                # Se já era polígono, pressionar '2' de novo finaliza
                janela.tool_manager.finalizar_desenho()

        elif key == glfw.KEY_4:
            janela.tool_manager.set_ferramenta('quadrado')
        
        # --- NOSSA NOVA LÓGICA 'M' ---
        elif key == glfw.KEY_M:
            janela.selection_manager.toggle_multi_select_mode()
        # -----------------------------

        # --- ADICIONE ESTE ELIF ---
        elif key == glfw.KEY_BACKSPACE:
            janela.selection_manager.delete_selected()
        # ---------------------------

        elif key == glfw.KEY_ESCAPE:
            # ESC para limpar seleção e ferramenta
            janela.tool_manager.set_ferramenta(None)
            janela.selection_manager.desselecionar_tudo()
        elif key == glfw.KEY_3:
            janela.tool_manager.set_ferramenta('linha')
        
        elif key == glfw.KEY_5:
            janela.tool_manager.set_ferramenta('triangulo')
        # --------------------------

def mouse_button_callback(window_ptr, button, action, mods): # <--- PONTO 1: 'mods' TEM QUE ESTAR AQUI
    janela = get_janela(window_ptr)
    x, y = glfw.get_cursor_pos(window_ptr)
    x_mundo, y_mundo = janela.converter_coords_tela_para_mundo(x, y)

    action_str = "PRESS" if action == glfw.PRESS else "RELEASE"
    
    if button == glfw.MOUSE_BUTTON_LEFT:
        if janela.tool_manager.handle_click(x_mundo, y_mundo, action_str):
            return 
        
        # --- PONTO 2: 'mods' TEM QUE SER PASSADO AQUI ---
        janela.selection_manager.handle_click(x_mundo, y_mundo, action_str, mods)

def cursor_pos_callback(window_ptr, x, y):
    janela = get_janela(window_ptr)
    x_mundo, y_mundo = janela.converter_coords_tela_para_mundo(x, y)

    # 1. Tenta arrastar com a ferramenta de desenho
    if janela.tool_manager.handle_drag(x_mundo, y_mundo):
        return # Evento foi consumido

    # 2. Se não, tenta arrastar com o gerenciador de seleção
    janela.selection_manager.handle_drag(x_mundo, y_mundo)