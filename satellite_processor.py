import cv2
import numpy as np
import math
from shapely.geometry import Polygon
from PIL import Image
import requests
from io import BytesIO

def analyze_satellite_image(image_url):
    try:
        # Step 1: Download image from URL
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        img_np = np.array(img.convert("RGB"))

        # Step 2: Preprocess (grayscale + edge detection)
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)

        # Step 3: Find largest contour (most likely the house/lot)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return {"error": "No contours found."}

        largest = max(contours, key=cv2.contourArea)

        # Step 4: Approximate the contour to a polygon
        epsilon = 0.01 * cv2.arcLength(largest, True)
        approx = cv2.approxPolyDP(largest, epsilon, True)
        coords = [tuple(pt[0]) for pt in approx]

        if len(coords) < 3:
            return {"error": "Not enough points to form a polygon."}

        # Step 5: Calculate orientation using PCA
        data_pts = np.array(coords, dtype=np.float64)
        mean, eigenvectors = cv2.PCACompute(data_pts, mean=np.array([]))
        angle_rad = math.atan2(eigenvectors[0, 1], eigenvectors[0, 0])
        orientation_deg = (math.degrees(angle_rad) + 360) % 360

        def deg_to_compass(deg):
            dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
            ix = round(deg / 45) % 8
            return dirs[ix]

        orientation_dir = deg_to_compass(orientation_deg)

        # Step 6: Calculate area and perimeter (in pixels)
        polygon = Polygon(coords)
        area_px = polygon.area
        perimeter_px = polygon.length

        # Step 7: Convert pixels to meters (assume 0.2 m per px for now — tweak as needed)
        meters_per_pixel = 0.2
        area_m2 = area_px * (meters_per_pixel ** 2)
        perimeter_m = perimeter_px * meters_per_pixel

        # Step 8: Compute side lengths
        side_lengths = [
            np.linalg.norm(np.array(coords[i]) - np.array(coords[(i + 1) % len(coords)])) * meters_per_pixel
            for i in range(len(coords))
        ]

        # Return analysis result
        return {
            "orientation_degrees": round(orientation_deg, 2),
            "orientation_direction": orientation_dir,
            "perimeter_meters": round(perimeter_m, 1),
            "area_sqm": round(area_m2, 1),
            "side_lengths": [round(length, 1) for length in side_lengths],
            "polygon_coords": coords
        }

    except Exception as e:
        return {"error": str(e)}
