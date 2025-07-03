import cv2
import numpy as np
import math
from shapely.geometry import Polygon
from PIL import Image
import requests
from io import BytesIO
import matplotlib.pyplot as plt

def visualize_polygon(coords, img_np=None):
    x = [pt[0] for pt in coords] + [coords[0][0]]
    y = [pt[1] for pt in coords] + [coords[0][1]]

    plt.figure(figsize=(8, 8))
    if img_np is not None:
        plt.imshow(img_np)
        plt.plot(x, y, 'r-', linewidth=2)
    else:
        plt.plot(x, y, 'bo-')

    plt.title("Polígono detectado")
    plt.gca().invert_yaxis()
    plt.axis('equal')
    plt.grid(True)
    plt.show()

def analyze_satellite_image(image_url):
    try:
        # Paso 1: Descargar imagen
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        img_np = np.array(img.convert("RGB"))

        # Paso 2: Preprocesamiento
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)

        # Paso 3: Contornos
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return {"error": "No contours found."}

        largest = max(contours, key=cv2.contourArea)

        # Paso 4: Aproximar contorno
        epsilon = 0.01 * cv2.arcLength(largest, True)
        approx = cv2.approxPolyDP(largest, epsilon, True)
        coords = [tuple(pt[0]) for pt in approx]

        if len(coords) < 3:
            return {"error": "Not enough points to form a polygon."}

        # 👇 Paso 2 (tu duda): esto es "usar la función"
        # Solo se ejecuta si corrés el script localmente, no en la API
        # visualizar_poligono(coords, img_np)

        # Paso 5: Orientación con PCA
        data_pts = np.array(coords, dtype=np.float64)
        mean, eigenvectors = cv2.PCACompute(data_pts, mean=np.array([]))
        angle_rad = math.atan2(eigenvectors[0, 1], eigenvectors[0, 0])
        orientation_deg = (math.degrees(angle_rad) + 360) % 360

        def deg_to_compass(deg):
            dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
            ix = round(deg / 45) % 8
            return dirs[ix]

        orientation_dir = deg_to_compass(orientation_deg)

        # Paso 6: Área y perímetro
        polygon = Polygon(coords)
        area_px = polygon.area
        perimeter_px = polygon.length

        # Paso 7: Conversión a metros
        meters_per_pixel = 0.2
        area_m2 = area_px * (meters_per_pixel ** 2)
        perimeter_m = perimeter_px * meters_per_pixel

        # Paso 8: Lados
        side_lengths = [
            float(np.linalg.norm(np.array(coords[i]) - np.array(coords[(i + 1) % len(coords)])) * meters_per_pixel)
            for i in range(len(coords))
        ]

        # Conversión de tipos para evitar error JSON
        cleaned_coords = [[int(x), int(y)] for (x, y) in coords]

        return {
            "orientation_degrees": round(float(orientation_deg), 2),
            "orientation_direction": orientation_dir,
            "perimeter_meters": round(float(perimeter_m), 1),
            "area_sqm": round(float(area_m2), 1),
            "side_lengths": [round(float(length), 1) for length in side_lengths],
            "polygon_coords": cleaned_coords
        }

    except Exception as e:
        return {"error": str(e)}
