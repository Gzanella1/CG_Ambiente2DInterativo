import math
from formas.Circulo import Circulo
from formas.PolignoNaoConvexo import PoligonoNaoConvexo
from formas.Linha import Linha
from formas.Quadrado import Quadrado
from formas.Triangulo import Triangulo

class ToolManager:
    def __init__(self, janela):
        self.janela = janela

    def activate_tool(self, tool_name):
        self.janela.current_tool = tool_name
        self.janela.drawing_state = 'await_first_point'
        self.janela.tentative = None
        print(f"[tool] {tool_name} ativada.")

    def handle_mouse_click(self, xw, yw, button):
        tool = self.janela.current_tool
        if tool == 'circle':
            self._handle_circle(xw, yw, button)
        elif tool == 'polygon':
            self._handle_polygon(xw, yw, button)
        elif tool == 'line':
            self._handle_line(xw, yw, button)
        elif tool == 'square':
            self._handle_square(xw, yw, button)
        elif tool == 'triangle':
            self._handle_triangle(xw, yw, button)


    def handle_mouse_move(self, xw, yw):
        tent = self.janela.tentative
        if not tent:
            return
        if tent['tool'] == 'circle' and tent['center']:
            cx, cy = tent['center']
            tent['radius'] = math.dist((cx, cy), (xw, yw))
        elif tent['tool'] == 'line' and tent.get('p1'):
            tent['p2'] = (xw, yw)
        elif tent['tool'] == 'square' and tent.get('center'):
            cx, cy = tent['center']
            dx = abs(xw - cx)
            dy = abs(yw - cy)
            tent['lado'] = 2 * max(dx, dy)
        elif tent['tool'] == 'triangle':
            verts = tent.get('vertices', [])
            if len(verts) >= 1:
                tent['preview_point'] = (xw, yw)


    # --------- Ferramentas ---------
    def _handle_circle(self, xw, yw, button):
        if button != 0:
            return
        if not self.janela.tentative:
            self.janela.tentative = {'tool': 'circle', 'center': (xw, yw), 'radius': 0}
            self.janela.drawing_state = 'adjusting'
            print(f"[circle] centro em ({xw:.2f},{yw:.2f})")
        else:
            self._finalize_circle()

    def _finalize_circle(self):
        t = self.janela.tentative
        if not t:
            return
        cx, cy = t['center']
        r = t['radius']
        if r > 0.01:
            circ = Circulo(r)
            self.janela.formas.append((circ, cx, cy, (0, 1, 0)))
            print(f"[circle] raio = {r:.2f}")
        self._reset()

    def _handle_polygon(self, xw, yw, button):
        if button != 0:
            return
        if not self.janela.tentative:
            self.janela.tentative = {'tool': 'polygon', 'vertices': [(xw, yw)]}
            print("[polygon] iniciando...")
        else:
            verts = self.janela.tentative['vertices']
            if len(verts) > 2 and math.dist(verts[0], (xw, yw)) < 0.5:
                poly = PoligonoNaoConvexo(verts)
                self.janela.formas.append((poly, 0, 0, (1, 0.8, 0)))
                print("[polygon] finalizado.")
                self._reset()
            else:
                verts.append((xw, yw))

    def _handle_line(self, xw, yw, button):
        if button != 0:
            return
        if not self.janela.tentative:
            self.janela.tentative = {'tool': 'line', 'p1': (xw, yw), 'p2': (xw, yw)}
        else:
            p1 = self.janela.tentative['p1']
            line = Linha(p1[0], p1[1], xw, yw)
            self.janela.formas.append((line, 0, 0, (0, 0.8, 1)))
            print("[line] finalizada.")
            self._reset()



    def _handle_square(self, xw, yw, button):
        if button != 0:
            return
        if not self.janela.tentative:
            # Primeiro clique: define o centro
            self.janela.tentative = {'tool': 'square', 'center': (xw, yw), 'lado': 0}
            self.janela.drawing_state = 'adjusting'
            print(f"[square] centro em ({xw:.2f},{yw:.2f})")
        else:
            self._finalize_square()

    def _finalize_square(self):
        t = self.janela.tentative
        if not t:
            return
        cx, cy = t['center']
        lado = t['lado']
        if lado > 0.01:
            sq = Quadrado(lado)
            self.janela.formas.append((sq, cx, cy, (1, 0, 1)))
            print(f"[square] lado = {lado:.2f}")
        self._reset()


    def _handle_triangle(self, xw, yw, button):
        if button != 0:
            return

        # Se ainda não começou, inicia lista de vértices
        if not self.janela.tentative:
            self.janela.tentative = {'tool': 'triangle', 'vertices': [(xw, yw)]}
            self.janela.drawing_state = 'adjusting'
            print(f"[triangle] vértice 1 = ({xw:.2f},{yw:.2f})")
            return

        tent = self.janela.tentative
        verts = tent['vertices']
        verts.append((xw, yw))

        if len(verts) == 2:
            print(f"[triangle] vértice 2 = ({xw:.2f},{yw:.2f})")
        elif len(verts) == 3:
            print(f"[triangle] vértice 3 = ({xw:.2f},{yw:.2f}) — finalizando.")
            tri = Triangulo(verts[0], verts[1], verts[2])
            self.janela.formas.append((tri, 0, 0, (1, 1, 0)))
            self._reset()

    def _finalize_triangle(self):
        """(opcional, se quiser chamar manualmente depois de 3 vértices)"""
        tent = self.janela.tentative
        if not tent:
            return
        verts = tent.get('vertices', [])
        if len(verts) == 3:
            tri = Triangulo(verts[0], verts[1], verts[2])
            self.janela.formas.append((tri, 0, 0, (1, 1, 0)))
            print("[triangle] finalizado.")
        self._reset()






    def _reset(self):
        self.janela.tentative = None
        self.janela.current_tool = None
        self.janela.drawing_state = 'idle'
