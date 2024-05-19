import cv2
import numpy as np

def get_center_of_circle(bbox):
    return int(bbox[0] + (bbox[2] - bbox[0]) / 2), int(bbox[3] - 10)
def get_width_height(bbox):
    return int(bbox[2] - bbox[0]), int(bbox[3] - bbox[1])

def draw_circle(frame, bbox, color, text):
    center = get_center_of_circle(bbox)
    width, height = get_width_height(bbox)
    axis1, axis2 = width, int(0.3 * height)
    cv2.ellipse(
        img=frame,
        center=center,
        axes=(axis1, axis2),
        angle=0,
        startAngle=30,
        endAngle=240,
        color=color,
        thickness=2
    )
    
    # Draw rectangle based on text length
    if(len(text) == 0):
        return
    
    if(len(text) == 1):
        rect_width = 10
    elif(len(text) == 2):
        rect_width = 15
    else:
        rect_width = 20

    point1 = int(center[0] - rect_width), int(center[1] + axis1/2)
    point2 = int(center[0] + rect_width), int(center[1] + axis1/2 + 25)

    cv2.rectangle(frame, point1, point2, color, -1)
    cv2.putText(frame, text, (point1[0] + 5, point1[1] + 17), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

def draw_triangle(frame, bbox, color):
    triangle = np.array([
        [int(bbox[0] + (bbox[2] - bbox[0]) / 2), int(bbox[1] - 3)],
        [int(bbox[0] - 1), int(bbox[1] - 20)],
        [int(bbox[2] + 1), int(bbox[1] - 20)]
    ], np.int32)

    cv2.drawContours(frame, [triangle], 0, color, cv2.FILLED)
    cv2.drawContours(frame, [triangle], 0, (0, 0, 0), 2)

def read_video(video_path: str):
    cap = cv2.VideoCapture(video_path)
    frames = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    return frames

def save_video(frames, output_path: str):
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, 30.0, (frames[0].shape[1], frames[0].shape[0]))
    for frame in frames:
        out.write(frame)
    out.release()

def draw_tracks(tracks, frames):
    for frame_idx, frame in enumerate(frames):
        for player in tracks["players"][frame_idx]:
            bbox = player["bbox"]
            track_id = player["track_id"]
            draw_circle(frame, bbox, (0, 0, 0), f"{track_id}")
        
        for ball in tracks["ball"][frame_idx]:
            bbox = ball["bbox"]
            track_id = ball["track_id"]
            draw_triangle(frame, bbox, (0, 255, 0))
        
        for referee in tracks["referees"][frame_idx]:
            bbox = referee["bbox"]
            track_id = referee["track_id"]
            draw_circle(frame, bbox, (255, 0, 0), "")

    return frames