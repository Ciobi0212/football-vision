# football-vision

## Overview
This project leverages the power of YOLOv8 and OpenCV to process football video snippets, providing real-time player and ball tracking with insightful game analytics. Using machine learning algorithms such as KMeans clustering from scikit-learn, players are automatically recognized, tracked, and categorized based on their team's shirt color. Additionally, the project tracks the football throughout the game, providing live possession statistics and visual enhancements directly in the video stream.

## Features
- **Player and Ball Detection and Tracking:** Utilize YOLOv8 for cutting-edge object detection to identify and track players throughout the game.
- **Team Classification:** Apply KMeans clustering to determine player team affiliations based on shirt colors.
- **Live Statistics:** Display real-time ball possession percentanges.
- **Video Enhancement:** Enhance the video using OpenCV with graphical overlays for better visual comprehension.

## Technologies Used
- Python 3.8+
- YOLOv8
- OpenCV
- Supervision (for tracking the YOLO outputs)
- scikit-learn (for KMeans Clustering)

## Raw input (video)
![42ba34_1-ezgif com-video-to-gif-converter](https://github.com/Ciobi0212/football-vision/assets/147515963/8f0a4ff8-cc66-479b-a1c3-06c086b9cdfb)

## Output
![output-ezgif com-video-to-gif-converter](https://github.com/Ciobi0212/football-vision/assets/147515963/e54df164-e21d-4a53-ac06-3e34eefb486e)
