# recognize.py
from manim import *
import cv2
import numpy as np
import os
import pytesseract

# 使用 Manim 找到頂點座標
class FindVertices(Scene):
    def __init__(self, shapes=None, **kwargs):
        """
        shapes: 一個包含 Manim mobject 的列表，
                每個 mobject 都應支援 get_vertices() 方法。
                若未提供則預設為 [Triangle()]。
        """
        super().__init__(**kwargs)
        self.shapes = shapes if shapes is not None else [Triangle()]

    def construct(self):
        for shape in self.shapes:
            # 將形狀加入場景，方便在影片中看到效果
            self.add(shape)
            vertices = shape.get_vertices()
            print(f"Manim vertices for {type(shape).__name__}:")
            for i, vertex in enumerate(vertices):
                print(f"  Vertex {i}: {vertex}")

def get_scene_vertices(scene):
    """
    從 scene 中搜尋所有具有 get_vertices() 方法的 mobject，
    並回傳一個頂點座標的列表。
    """
    vertices = []
    for mobject in scene.mobjects:
        if hasattr(mobject, 'get_vertices'):
            vertices.extend(mobject.get_vertices())
    return vertices

def convert_to_pixel_coordinates(vertices, image_shape, scene):
    """
    將 scene 中的座標轉換為圖像中像素的座標。
    
    :param vertices: 經由 get_vertices() 取得的頂點座標列表
    :param image_shape: 圖像尺寸，格式為 (height, width, channels)
    :param scene: 當前的 Manim scene，用於取得 camera.frame_width/height
    :return: 像素座標的列表，每個元素為 (pixel_x, pixel_y)
    """
    pixel_coords = []
    for vertex in vertices:
        x, y, _ = vertex
        pixel_x = int((x + scene.camera.frame_width / 2) / scene.camera.frame_width * image_shape[1])
        pixel_y = int((scene.camera.frame_height / 2 - y) / scene.camera.frame_height * image_shape[0])
        pixel_coords.append((pixel_x, pixel_y))
    return pixel_coords

def annotate_and_save_vertices(image, contours, output_path):
    """
    標註頂點並保存圖像。
    
    :param image: 原始圖像
    :param contours: 輪廓列表
    :param output_path: 保存圖像的路徑
    :param text_boxes: 文字框的列表，每個元素為 (x, y, w, h)
    """
    annotated_image = np.zeros_like(image)  # 創建一個黑色背景的圖像
    
    for i, contour in enumerate(contours):
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        if len(approx) >= 3:  # 只關心至少為多邊形的輪廓
            for vertex in approx:
                # 檢查頂點是否在文字框內
                # if any(x <= vertex[0][0] <= x + w and y <= vertex[0][1] <= y + h for (x, y, w, h) in text_boxes):
                #     continue
                cv2.circle(annotated_image, tuple(vertex[0]), 2, (0, 255, 255), -1)  # 標註頂點，黃色點
    
    # 保存標註後的圖像
    cv2.imwrite(output_path, annotated_image)
    print(f"標註結果已保存到 {output_path}")

def extract_text_boxes(image):
    """
    使用 OCR 提取圖像中的文字框。
    
    :param image: 原始圖像
    :return: 文字框的列表，每個元素為 (x, y, w, h)
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    d = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
    text_boxes = []
    n_boxes = len(d['level'])
    for i in range(n_boxes):
        (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
        text_boxes.append((x, y, w, h))
        # 列印辨識到的文字及其座標
        print(f"文字: {d['text'][i]}, 座標: ({x}, {y}, {w}, {h})")
    return text_boxes

def remove_text_boxes(image, text_boxes):
    """
    將圖像中的文字框部分填充為黑色。
    
    :param image: 原始圖像
    :param text_boxes: 文字框的列表，每個元素為 (x, y, w, h)
    :return: 去除文字框後的圖像
    """
    for (x, y, w, h) in text_boxes:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 0), -1)
    return image

# 使用 OpenCV 找到頂點座標
def find_vertices_with_opencv(image_path):
    """
    使用 OpenCV 從圖像中檢測所有多邊形，
    並列印出每個多邊形的頂點資訊。
    """
    image = cv2.imread(image_path)
    if image is None:
        print(f"無法在 {image_path} 找到圖像。")
        return

    # 提取文字框
    # text_boxes = extract_text_boxes(image)

    # 去除文字框部分
    # image = remove_text_boxes(image, text_boxes)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    
    # 使用形態學操作來去除小的輪廓
    kernel = np.ones((5, 5), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)
    edges = cv2.erode(edges, kernel, iterations=1)
    
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    for i, contour in enumerate(contours):
        # 過濾掉小的輪廓
        if cv2.contourArea(contour) < 900:  # 目前先用此方法來過濾小的輪廓 ( 角度標註引起的問題 )
            continue
        
        epsilon = 0.005 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        if len(approx) > 0:  # 只關心頂點數在 3 到 10 之間的多邊形輪廓
            print(f"OpenCV 找到形狀 {i}，頂點數：{len(approx)}，面積：{cv2.contourArea(contour)}")
            for j, vertex in enumerate(approx):
                print(f"  Vertex {j}: {vertex[0]}")
    
    # 標註頂點並保存圖像
    result_path = os.path.join(os.path.dirname(image_path), "result_opencv.png")
    annotate_and_save_vertices(image, contours, result_path)
