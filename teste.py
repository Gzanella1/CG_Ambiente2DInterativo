# main.py
import glfw
from OpenGL.GL import *
from math import sin, cos, radians, sqrt, atan2, degrees
import sys

WINDOW_W, WINDOW_H = 800, 600
HANDLER_SIZE = 8

# --- utilitários geométricos ---
def dist(a, b):
    return sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def point_in_circle(px, py, cx, cy, r):
    return (px-cx)**2 + (py-cy)**2 <= r*r

def rotate_point(x, y, ang_deg):
    a = radians(ang_deg)
    return x*cos(a) - y*sin(a), x*sin(a) + y*cos(a)

def inverse_transform_point(px, py, tx, ty, rot, sx, sy):
    # translate back
    x = px - tx
    y = py - ty
    # rotate inverse
    a = radians(-rot)
    xr = x * cos(a) - y * sin(a)
    yr = x * sin(a) + y * cos(a)
    # scale inverse (avoid div by zero)
    xr = xr / sx if sx != 0 else xr
    yr = yr / sy if sy != 0 else yr
    return xr, yr

# --- Shape base and subclasse simples ---
class Shape:
    def __init__(self):
        self.tx = 0.0
        self.ty = 0.0
        self.rot = 0.0    # degrees
        self.sx = 1.0
        self.sy = 1.0
        self.selected = False
        self.stroke_width = 3.0

    def draw(self):
        raise NotImplementedError

    def draw_preview(self):
        self.draw()

    def contains_point(self, x, y):
        # default: bounding-box check (override in subclasses)
        bx1, by1, bx2, by2 = self.get_bbox_world()
        return bx1 <= x <= bx2 and by1 <= y <= by2

    def get_bbox_local(self):
        # return minx,miny,maxx,maxy in local coords; override per shapeFr
        return (-10,-10,10,10)

    def get_bbox_world(self):
        lx1, ly1, lx2, ly2 = self.get_bbox_local()
        # sample four corners, transform by S,R,T
        corners_local = [(lx1,ly1),(lx1,ly2),(lx2,ly1),(lx2,ly2)]
        xs=[]
        ys=[]
        for x,y in corners_local:
            x *= self.sx; y *= self.sy
            xr, yr = rotate_point(x,y,self.rot)
            xs.append(xr + self.tx); ys.append(yr + self.ty)
        return min(xs), min(ys), max(xs), max(ys)

    def apply_transform(self):
        glTranslatef(self.tx, self.ty, 0)
        glRotatef(self.rot, 0,0,1)
        glScalef(self.sx, self.sy, 1)

class Circle(Shape):
    def __init__(self, radius=50):
        super().__init__()
        self.radius = radius

    def draw(self):
        glLineWidth(self.stroke_width)
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(0,0)
        steps = 48
        for i in range(steps+1):
            a = 2*3.1415926*i/steps
            glVertex2f(cos(a)*self.radius, sin(a)*self.radius)
        glEnd()

    def draw_outline(self):
        glLineWidth(self.stroke_width)
        steps = 64
        glBegin(GL_LINE_LOOP)
        for i in range(steps):
            a = 2*3.1415926*i/steps
            glVertex2f(cos(a)*self.radius, sin(a)*self.radius)
        glEnd()

    def contains_point(self, x, y):
        # transform point to local
        lx, ly = inverse_transform_point(x,y,self.tx,self.ty,self.rot,self.sx,self.sy)
        return lx*lx + ly*ly <= self.radius*self.radius

    def get_bbox_local(self):
        r = self.radius
        return (-r,-r,r,r)

class Square(Shape):
    def __init__(self, half=50):
        super().__init__()
        self.half = half

    def draw(self):
        glBegin(GL_QUADS)
        glVertex2f(-self.half, -self.half)
        glVertex2f(self.half, -self.half)
        glVertex2f(self.half, self.half)
        glVertex2f(-self.half, self.half)
        glEnd()

    def contains_point(self, x, y):
        lx, ly = inverse_transform_point(x,y,self.tx,self.ty,self.rot,self.sx,self.sy)
        return -self.half <= lx <= self.half and -self.half <= ly <= self.half

    def get_bbox_local(self):
        h = self.half
        return (-h,-h,h,h)

class Line(Shape):
    def __init__(self, x1=-50,y1=0,x2=50,y2=0, thickness=4):
        super().__init__()
        self.x1, self.y1, self.x2, self.y2 = x1,y1,x2,y2
        self.thickness = thickness

    def draw(self):
        glLineWidth(self.thickness)
        glBegin(GL_LINES)
        glVertex2f(self.x1, self.y1)
        glVertex2f(self.x2, self.y2)
        glEnd()

    def contains_point(self, x, y):
        # approximate distance to segment in world coords with inverse transform applied to shape? Simpler: transform mouse into local coords
        lx, ly = inverse_transform_point(x,y,self.tx,self.ty,self.rot,self.sx,self.sy)
        # distance from point to segment (x1,y1)-(x2,y2)
        x1,y1,x2,y2 = self.x1,self.y1,self.x2,self.y2
        dx = x2-x1; dy=y2-y1
        if dx==0 and dy==0:
            return dist((lx,ly),(x1,y1)) <= 6
        t = ((lx-x1)*dx + (ly-y1)*dy) / (dx*dx+dy*dy)
        t = max(0,min(1,t))
        px = x1 + t*dx; py = y1 + t*dy
        return dist((lx,ly),(px,py)) <= 8

    def get_bbox_local(self):
        minx = min(self.x1, self.x2); maxx=max(self.x1,self.x2)
        miny = min(self.y1, self.y2); maxy=max(self.y1,self.y2)
        return (minx-4,miny-4,maxx+4,maxy+4)

class PolygonNonConvex(Shape):
    def __init__(self, points=None):
        super().__init__()
        if points is None:
            points = [(-30,-20),(0,40),(30,-20),(10,0),(-10,0)]
        self.points = points

    def draw(self):
        glBegin(GL_POLYGON)
        for x,y in self.points:
            glVertex2f(x,y)
        glEnd()

    def contains_point(self, x, y):
        lx, ly = inverse_transform_point(x,y,self.tx,self.ty,self.rot,self.sx,self.sy)
        # ray-casting algorithm
        inside = False
        pts = self.points
        n = len(pts)
        for i in range(n):
            x1,y1 = pts[i]
            x2,y2 = pts[(i+1)%n]
            if ((y1>ly) != (y2>ly)) and (lx < (x2-x1)*(ly-y1)/(y2-y1)+x1):
                inside = not inside
        return inside

    def get_bbox_local(self):
        xs = [p[0] for p in self.points]; ys = [p[1] for p in self.points]
        return (min(xs), min(ys), max(xs), max(ys))

# --- scene manager / selection logic ---
class Scene:
    def __init__(self):
        self.shapes = []
        self.current_tool = 'circle'  # circle, poly, line, square, tri
        self.drawing = False
        self.temp_shape = None
        self.draw_stage = 0  # 0=no center, 1=dragging
        self.selected = None
        # interaction state
        self.dragging = False
        self.drag_start = (0,0)
        self.orig_tx_ty = (0,0)
        self.handler_active = None
        self.rotate_active = False

    def add_shape(self, shape):
        self.shapes.append(shape)

    def set_tool_from_key(self, k):
        if k=='1': self.current_tool='circle'
        if k=='2': self.current_tool='poly'
        if k=='3': self.current_tool='line'
        if k=='4': self.current_tool='square'
        if k=='5': self.current_tool='tri'

    def start_drawing(self, x, y):
        self.drawing = True
        self.draw_stage = 1
        # create temp shape centered at x,y with size 1
        if self.current_tool == 'circle':
            s = Circle(1)
        elif self.current_tool == 'square':
            s = Square(1)
        elif self.current_tool == 'line':
            s = Line(-1,0,1,0)
            # set center at x,y via tx,ty
        elif self.current_tool == 'poly':
            s = PolygonNonConvex()
        elif self.current_tool == 'tri':
            s = PolygonNonConvex(points=[(-30,-20),(0,40),(30,-20)])
        else:
            s = Circle(1)
        s.tx = x; s.ty = y
        self.temp_shape = s

    def update_preview(self, x, y):
        if not self.drawing or self.temp_shape is None: return
        s = self.temp_shape
        # scale to match distance from center to mouse
        dx = x - s.tx; dy = y - s.ty
        r = sqrt(dx*dx + dy*dy)
        if isinstance(s, Circle):
            s.radius = max(4, r)
        elif isinstance(s, Square):
            s.half = max(4, r)
        elif isinstance(s, Line):
            # create line from center to mouse mirrored
            s.x1, s.y1 = -dx, -dy
            s.x2, s.y2 = dx, dy
        else:
            # scale the shape uniformly based on r
            # compute bounding radius from local bbox and set sx so that local extents * sx ~ r
            lx1,ly1,lx2,ly2 = s.get_bbox_local()
            local_radius = max(abs(lx1),abs(ly1),abs(lx2),abs(ly2))
            if local_radius == 0: local_radius = 1
            factor = r/local_radius
            s.sx = s.sy = factor

    def finish_drawing(self, x, y):
        if not self.drawing: return
        self.update_preview(x,y)
        self.add_shape(self.temp_shape)
        self.temp_shape = None
        self.drawing = False
        self.draw_stage = 0

    def pick_shape(self, x, y):
        # pick topmost shape containing point (iterate reverse)
        for shp in reversed(self.shapes):
            if shp.contains_point(x,y):
                return shp
        return None

    def select(self, shape):
        if self.selected: self.selected.selected=False
        self.selected = shape
        if shape: shape.selected=True

    def start_drag(self, x, y):
        # if selected and clicked on handler -> start handler operation
        if self.selected:
            h = self._hit_handler(self.selected, x, y)
            if h is not None:
                self.handler_active = h
                self.dragging = True
                self.drag_start = (x,y)
                self.orig_tx_ty = (self.selected.tx, self.selected.ty, self.selected.sx, self.selected.sy, self.selected.rot)
                return
            # check rotate handle
            if self._hit_rotate_handle(self.selected, x, y):
                self.rotate_active = True
                self.dragging = True
                self.drag_start = (x,y)
                self.orig_tx_ty = (self.selected.tx, self.selected.ty, self.selected.sx, self.selected.sy, self.selected.rot)
                return
        # otherwise if clicked inside shape -> move
        shp = self.pick_shape(x,y)
        if shp:
            self.select(shp)
            self.dragging = True
            self.drag_start = (x,y)
            self.orig_tx_ty = (shp.tx, shp.ty, shp.sx, shp.sy, shp.rot)
        else:
            self.select(None)

    def drag_to(self, x, y):
        if not self.dragging: return
        dx = x - self.drag_start[0]; dy = y - self.drag_start[1]
        if self.handler_active and self.selected:
            # handle scaling based on handler id
            _,_,orig_sx, orig_sy, _ = self.orig_tx_ty
            # we'll scale uniformly based on dx,dy magnitude
            # simple approach: compute scale factor from movement along handler direction
            if self.handler_active in ('left','right'):
                # horizontal scale
                factor = 1 + dx / 100.0
            elif self.handler_active in ('top','bottom'):
                factor = 1 - dy / 100.0
            else:
                factor = 1 + (dx+dy)/200.0
            factor = max(0.05, factor)
            self.selected.sx = orig_sx * factor
            self.selected.sy = orig_sy * factor
            return
        if self.rotate_active and self.selected:
            # compute angle change by comparing angle from center to mouse
            cx, cy = self.selected.tx, self.selected.ty
            ox, oy = self.drag_start
            a0 = atan2(oy-cy, ox-cx)
            a1 = atan2(y-cy, x-cx)
            delta = degrees(a1 - a0)
            _,_,_,_,orig_rot = self.orig_tx_ty
            self.selected.rot = orig_rot + delta
            return
        # moving shape
        if self.selected:
            orig_tx, orig_ty, _,_,_ = self.orig_tx_ty
            self.selected.tx = orig_tx + dx
            self.selected.ty = orig_ty + dy

    def end_drag(self, x, y):
        self.dragging = False
        self.handler_active = None
        self.rotate_active = False

    # --- handlers drawing/hit detection ---
    def draw_handlers_for(self, shp):
        bx1,by1,bx2,by2 = shp.get_bbox_world()
        # draw dashed rectangle
        glLineWidth(1)
        glEnable(GL_LINE_STIPPLE)
        glLineStipple(1, 0xF0F0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(bx1, by1); glVertex2f(bx2, by1)
        glVertex2f(bx2, by2); glVertex2f(bx1, by2)
        glEnd()
        glDisable(GL_LINE_STIPPLE)

        # draw handlers (squares) in corners and midpoints
        handles = self._bbox_handles(bx1,by1,bx2,by2)
        for (hx,hy), name in handles:
            self._draw_handler_square(hx,hy)

        # draw rotate handle a bit above top-center
        rx = (bx1+bx2)/2
        ry = by2 + 20
        self._draw_handler_square(rx, ry, filled=False)
        # draw a line to rotate handle
        glBegin(GL_LINES)
        glVertex2f((bx1+bx2)/2, by2)
        glVertex2f(rx, ry)
        glEnd()

    def _draw_handler_square(self, x, y, filled=True):
        s = HANDLER_SIZE
        if filled:
            glBegin(GL_QUADS)
        else:
            glLineWidth(2); glBegin(GL_LINE_LOOP)
        glVertex2f(x-s, y-s)
        glVertex2f(x+s, y-s)
        glVertex2f(x+s, y+s)
        glVertex2f(x-s, y+s)
        glEnd()

    def _bbox_handles(self, bx1,by1,bx2,by2):
        # returns list ((x,y),name)
        mx = (bx1+bx2)/2; my=(by1+by2)/2
        return [((bx1,by1),'bottom-left'), ((mx,by1),'bottom'), ((bx2,by1),'bottom-right'),
                ((bx1,my),'left'), ((mx,my),'center'), ((bx2,my),'right'),
                ((bx1,by2),'top-left'), ((mx,by2),'top'), ((bx2,by2),'top-right')]

    def _hit_handler(self, shp, x, y):
        bx1,by1,bx2,by2 = shp.get_bbox_world()
        for (hx,hy), name in self._bbox_handles(bx1,by1,bx2,by2):
            if abs(x-hx)<=HANDLER_SIZE and abs(y-hy)<=HANDLER_SIZE:
                return name
        return None

    def _hit_rotate_handle(self, shp, x, y):
        bx1,by1,bx2,by2 = shp.get_bbox_world()
        rx = (bx1+bx2)/2; ry = by2 + 20
        return abs(x-rx)<=HANDLER_SIZE and abs(y-ry)<=HANDLER_SIZE

    # --- drawing scene ---
    def render(self):
        # draw shapes
        for shp in self.shapes:
            glPushMatrix()
            glTranslatef(shp.tx, shp.ty, 0)
            glRotatef(shp.rot, 0,0,1)
            glScalef(shp.sx, shp.sy, 1)
            # fill
            if shp is self.selected:
                glColor4f(0.2,0.6,0.9,0.5)
            else:
                glColor4f(0.4,0.4,0.8,1.0)
            shp.draw()
            glPopMatrix()
            # outline
            glPushMatrix()
            glTranslatef(shp.tx, shp.ty, 0)
            glRotatef(shp.rot, 0,0,1)
            glScalef(shp.sx, shp.sy, 1)
            glColor3f(0,0,0)
            if isinstance(shp, Circle):
                shp.draw_outline()
            else:
                # draw a simple black outline around bbox local for clarity (or shape-specific)
                lx1,ly1,lx2,ly2 = shp.get_bbox_local()
                glBegin(GL_LINE_LOOP)
                glVertex2f(lx1,ly1); glVertex2f(lx2,ly1)
                glVertex2f(lx2,ly2); glVertex2f(lx1,ly2)
                glEnd()
            glPopMatrix()

        # draw temp preview shape if drawing
        if self.temp_shape:
            glPushAttrib(GL_ENABLE_BIT)
            glEnable(GL_LINE_STIPPLE)
            glLineStipple(1, 0xAAAA)
            glColor3f(0.0,0.0,0.0)
            glPushMatrix()
            glTranslatef(self.temp_shape.tx, self.temp_shape.ty, 0)
            glRotatef(self.temp_shape.rot,0,0,1)
            glScalef(self.temp_shape.sx, self.temp_shape.sy, 1)
            # draw outline only
            if isinstance(self.temp_shape, Circle):
                self.temp_shape.draw_outline()
            else:
                lx1,ly1,lx2,ly2 = self.temp_shape.get_bbox_local()
                glBegin(GL_LINE_LOOP)
                glVertex2f(lx1,ly1); glVertex2f(lx2,ly1)
                glVertex2f(lx2,ly2); glVertex2f(lx1,ly2)
                glEnd()
            glPopMatrix()
            glPopAttrib()

        # draw handlers if selected
        if self.selected:
            glColor3f(0,0,0)
            self.draw_handlers_for(self.selected)

scene = Scene()

# --- GLFW callbacks and main loop ---
def cursor_pos_callback(window, xpos, ypos):
    # convert to world coords (center origin)
    x = xpos - WINDOW_W/2
    y = (WINDOW_H - ypos) - WINDOW_H/2
    if scene.drawing:
        scene.update_preview(x,y)
    if scene.dragging:
        scene.drag_to(x,y)

def mouse_button_callback(window, button, action, mods):
    xpos, ypos = glfw.get_cursor_pos(window)
    x = xpos - WINDOW_W/2
    y = (WINDOW_H - ypos) - WINDOW_H/2
    if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
        # If currently drawing -> if first click started drawing, second click finalize
        if not scene.drawing and (glfw.get_key(window, glfw.KEY_LEFT_SHIFT) != glfw.PRESS):
            # starting drawing or selecting
            # if holding ctrl maybe start different behavior; here: try selection first
            picked = scene.pick_shape(x,y)
            if picked:
                scene.select(picked)
                scene.start_drag(x,y)
            else:
                # start new drawing
                scene.start_drawing(x,y)
        elif scene.drawing:
            # finish drawing
            scene.finish_drawing(x,y)
    if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.RELEASE:
        scene.end_drag(x,y)

def key_callback(window, key, scancode, action, mods):
    if action == glfw.PRESS:
        if key == glfw.KEY_1:
            scene.set_tool_from_key('1')
            print("Tool: Círculo")
        if key == glfw.KEY_2:
            scene.set_tool_from_key('2')
            print("Tool: Polígono")
        if key == glfw.KEY_3:
            scene.set_tool_from_key('3')
            print("Tool: Linha")
        if key == glfw.KEY_4:
            scene.set_tool_from_key('4')
            print("Tool: Quadrado")
        if key == glfw.KEY_5:
            scene.set_tool_from_key('5')
            print("Tool: Triângulo")
        if key == glfw.KEY_DELETE or key == glfw.KEY_BACKSPACE:
            if scene.selected and scene.selected in scene.shapes:
                scene.shapes.remove(scene.selected)
                scene.selected = None

def init_scene():
    # add an initial sample shape for testing
    c = Circle(60); c.tx = -100; c.ty = 50
    sq = Square(40); sq.tx=120; sq.ty=-30; sq.rot=15
    ln = Line(-40,0,40,0); ln.tx=0; ln.ty=0
    poly = PolygonNonConvex()
    poly.tx = -50; poly.ty=-120
    scene.add_shape(c); scene.add_shape(sq); scene.add_shape(ln); scene.add_shape(poly)

def main():
    if not glfw.init():
        print("Falha ao inicializar GLFW")
        return
    window = glfw.create_window(WINDOW_W, WINDOW_H, "Mini Paint OpenGL", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_cursor_pos_callback(window, cursor_pos_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_key_callback(window, key_callback)

    glViewport(0,0,WINDOW_W, WINDOW_H)
    glMatrixMode(GL_PROJECTION); glLoadIdentity()
    # simple orthographic projection centered at (0,0)
    glOrtho(-WINDOW_W/2, WINDOW_W/2, -WINDOW_H/2, WINDOW_H/2, -1, 1)
    glMatrixMode(GL_MODELVIEW); glLoadIdentity()

    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    init_scene()

    while not glfw.window_should_close(window):
        glClearColor(1,1,1,1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        scene.render()

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
