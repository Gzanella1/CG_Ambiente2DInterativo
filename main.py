from OpenGL.GL import *
from janela import JanelaGLFW
from callbacks import Callbacks

def render(janela):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    janela.configure_visualization()
    janela.desenhar_formas()

if __name__ == "__main__":
    janela = JanelaGLFW(largura=800, altura=800, left=-20, right=20, bottom=-20, top=20, titulo="Desenhando Figuras")
    callbacks = Callbacks(janela)
    janela.run(render, callback_handler=callbacks)
