from manim import *

class DrawTriangle(Scene):
    def construct(self):
        # 定義三角形的三個頂點
        point_a = ORIGIN          # (0, 0)
        point_b = point_a + 3 * RIGHT  # (3, 0)
        point_c = point_a + 4 * UP     # (0, 4)

        # 創建三角形
        triangle = Polygon(point_a, point_b, point_c, color=BLUE)
        
        # 將三角形移動到畫面中心
        triangle.move_to(ORIGIN)

        # 更新頂點位置
        point_a = triangle.get_vertices()[0]
        point_b = triangle.get_vertices()[1]
        point_c = triangle.get_vertices()[2]

        # 標註頂點座標
        label_a = Text("A (0, 0)").next_to(point_a, DOWN + LEFT)
        label_b = Text("B (3, 0)").next_to(point_b, DOWN + RIGHT)
        label_c = Text("C (0, 4)").next_to(point_c, UP)

        # 添加到場景
        self.add(triangle, label_a, label_b, label_c)

        # 畫角度標註
        self.drawAngle(point_a, point_b, point_c, is_right_angle=True)
        self.drawAngle(point_b, point_c, point_a)
        self.drawAngle(point_c, point_a, point_b)

        # 計算內接圓的圓心和半徑
        incenter = self.get_incenter(point_a, point_b, point_c)
        inradius = self.get_inradius(point_a, point_b, point_c, incenter)

        # 畫內接圓
        incircle = Circle(radius=inradius, color=RED).move_to(incenter)
        self.add(incircle)

    def drawAngle(self, vertex, point1, point2, is_right_angle=False):
        line1 = Line(vertex, point1, color=YELLOW)
        line2 = Line(vertex, point2, color=YELLOW)
        self.add(line1, line2)
        
        if is_right_angle:
            angle = RightAngle(line1, line2, length=0.4, quadrant=(1, 1))
        else:
            angle = Angle(line1, line2, radius=0.4, other_angle=False)
        
        self.add(angle)

    def get_incenter(self, a, b, c):
        # 計算三角形內心
        ax, ay = a[:2]
        bx, by = b[:2]
        cx, cy = c[:2]
        d = 2 * (ax*(by - cy) + bx*(cy - ay) + cx*(ay - by))
        ux = ((ax**2 + ay**2)*(by - cy) + (bx**2 + by**2)*(cy - ay) + (cx**2 + cy**2)*(ay - by)) / d
        uy = ((ax**2 + ay**2)*(cx - bx) + (bx**2 + by**2)*(ax - cx) + (cx**2 + cy**2)*(bx - ax)) / d
        return np.array([ux, uy, 0])

    def get_inradius(self, a, b, c, incenter):
        # 計算三角形內接圓半徑
        side_a = np.linalg.norm(b - c)
        side_b = np.linalg.norm(a - c)
        side_c = np.linalg.norm(a - b)
        s = (side_a + side_b + side_c) / 2
        area = np.sqrt(s * (s - side_a) * (s - side_b) * (s - side_c))
        inradius = area / s
        return inradius