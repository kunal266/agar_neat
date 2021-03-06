import cv2
import numpy as np

import os

MAX_IMAGE_WIDTH = 750
PRINT_IMAGE = False

def hough_circles(image):
    height, width = image.shape

    original_image = None if (not PRINT_IMAGE) else image.copy()

    # Convert to high-contrast black and white
    width_resized = min(MAX_IMAGE_WIDTH, width);
    height_resized = round((width_resized / width) * height)
    image = cv2.resize(image, (width_resized, height_resized), 0, 0, cv2.INTER_AREA)

    resized_image = None if (not PRINT_IMAGE) else image.copy()

    # image = cv2.medianBlur(image, 3)
    image = cv2.blur(image, (3, 3), cv2.BORDER_DEFAULT)

    image = cv2.convertScaleAbs(image, alpha=0.7, beta=100.)
    image = cv2.threshold(image, 245, 255, cv2.THRESH_BINARY&cv2.THRESH_OTSU)
    image = image[1]

    high_contrast_image = None if (not PRINT_IMAGE) else image.copy()

    # Hough Circles: https://docs.opencv.org/3.4/d3/de5/tutorial_js_houghcircles.html
    # https://answers.opencv.org/question/214448/i-try-to-detect-circle-in-real-time-webcam-using-houghcircles-from-opencv-javascript/
    small_circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, 1, 5,
                                    param1=100, param2=5,
                                    minRadius=0, maxRadius=5)

    food = [] if ((small_circles is None) or (len(small_circles) == 0)) else list(small_circles[0])

    # Erase food points from image
    for (x, y, radius) in food:
        cv2.circle(image, (round(x), round(y)), round(radius) + 5, (255,255,255), -1)

    large_circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, 2, 15,
                                    param1=100, param2=35,
                                    minRadius=10, maxRadius=0)

    small_removed_image = None if (not PRINT_IMAGE) else image.copy()

    enemies = [] if ((large_circles is None) or (len(large_circles) == 0)) else list(large_circles[0])

    # Find and extract player
    MIN_PLAYER_DIST_SQUARED = 250
    min_dist_squared = float('inf')
    min_index = -1
    player = None
    for (index, enemy) in enumerate(enemies):
        x, y, radius = enemy
        dist_squared = ((width_resized / 2) - x) ** 2 + ((height_resized / 2) - y) ** 2

        # Keep player
        if (dist_squared < MIN_PLAYER_DIST_SQUARED) and (dist_squared < min_dist_squared):
            min_dist_squared = dist_squared
            min_index = index
            player = enemy

    # Remove any detected 'enemies' that are too close, as they are false positives
    filtered_enemies = []
    if player is None:
        filtered_enemies = enemies
    else:
        # Remove player from enemies list
        enemies.pop(min_index)
        _, _, player_radius = player
        for enemy in enemies:
            x, y, radius = enemy
            dist = (((width_resized / 2) - x) ** 2 + ((height_resized / 2) - y) ** 2) ** (1 / 2)

            if (dist - radius) > 0:
                filtered_enemies.append(enemy)

    if (not player is None) and PRINT_IMAGE:
        save_parsed_circles(original_image, resized_image, high_contrast_image, small_removed_image, player, filtered_enemies, food)

    def transform_origin(item):
        x, y, radius = item

        return (
            (x * (width / width_resized) - (width / 2)),
            -(y * (height / height_resized) - (height / 2)),
            radius
        )

    # Transform coordinates to center origin
    enemies = list(map(transform_origin, filtered_enemies))
    food = list(map(transform_origin, food))
    print("bruh enemies and player found",player,enemies,food)
    return player, enemies, food

def save_parsed_circles(image, resized_image, high_contrast_image, small_removed_image, player, enemies, food):
    cv2.imwrite('images/image.png', image)
    cv2.imwrite('images/image_resized.png', resized_image)
    cv2.imwrite('images/bw.png', high_contrast_image)
    cv2.imwrite('images/bw_removed.png', small_removed_image)
    colored_image = cv2.cvtColor(high_contrast_image, cv2.COLOR_GRAY2RGB)

    x, y, radius = player
    cv2.circle(colored_image, (round(x), round(y)), round(radius), (0,255,0), thickness=2)

    for circle in enemies:
        x, y, radius = circle
        cv2.circle(colored_image, (round(x), round(y)), round(radius), (0,0,255), thickness=2)

    for circle in food:
        x, y, radius = circle
        cv2.circle(colored_image, (round(x), round(y)), round(radius), (255,0,0), thickness=1)

    cv2.imwrite('images/bw_circles.png', colored_image)
