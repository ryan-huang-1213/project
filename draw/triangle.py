from manim import *
import cv2
import numpy as np
import os
import sys

# 如果 recognize.py 與此檔案在同一目錄下，可將當前目錄加入 sys.path（視情況可省略）
current_dir = os.path.dirname(os.path.realpath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 正確引用 recognize.py 中的功能
from recognize import FindVertices, find_vertices_with_opencv

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

        # 標註頂點座標和字母
        label_a = Text("A (0, 0)").next_to(point_a, DOWN + LEFT)
        label_b = Text("B (3, 0)").next_to(point_b, DOWN + RIGHT)
        label_c = Text("C (0, 4)").next_to(point_c, UP)

        # 添加到場景
        self.add(triangle, label_a, label_b, label_c)

        # 畫角度標註
        self.drawAngle(point_a, point_b, point_c, is_right_angle=True)
        self.drawAngle(point_b, point_c, point_a)
        self.drawAngle(point_c, point_a, point_b)

        print("Using Manim to find vertices:")
        shapes = [triangle]
        manim_scene = FindVertices(shapes=shapes)
        manim_scene.construct()

        print("Using OpenCV to find vertices:")
        current_file_name = os.path.splitext(os.path.basename(__file__))[0]
        image_path = os.path.join(".", "media", "images", current_file_name, "output.png")
        find_vertices_with_opencv(image_path)

    def drawAngle(self, vertex, point1, point2, is_right_angle=False):
        line1 = Line(vertex, point1, color=YELLOW)
        line2 = Line(vertex, point2, color=YELLOW)
        self.add(line1, line2)
        
        if is_right_angle:
            angle = RightAngle(line1, line2, length=0.4, quadrant=(1, 1))
        else:
            angle = Angle(line1, line2, radius=0.4, other_angle=False)
        
        self.add(angle)

# 要執行的命令：
# manim -pql triangle.py DrawTriangle
