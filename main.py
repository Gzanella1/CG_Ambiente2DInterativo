# main.py
import glfw
from janela import Janela

def main():
    if not glfw.init():
        print("Erro ao inicializar o GLFW")
        return

    # Instancia a janela principal, que agora controla tudo
    janela_principal = Janela(800, 600, "Paint 2D Interativo")
    
    # O loop principal agora está encapsulado dentro da classe Janela
    janela_principal.run()

    glfw.terminate()

if __name__ == "__main__":
    main()