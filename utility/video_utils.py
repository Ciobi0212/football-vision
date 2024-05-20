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
    cv2.putText(frame, text, (point1[0] + 5, point1[1] + 17), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

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
            team_color = player["team_color"] if "team_color" in player else (0, 0, 0)
            draw_circle(frame, bbox, team_color, f"{track_id}")

            if player.get("has_ball", False):
                draw_triangle(frame, bbox, (255, 0, 0))
        
        for ball in tracks["ball"][frame_idx]:
            bbox = ball["bbox"]
            track_id = ball["track_id"]
            draw_triangle(frame, bbox, (0, 255, 0))
        
        for referee in tracks["referees"][frame_idx]:
            bbox = referee["bbox"]
            track_id = referee["track_id"]
            draw_circle(frame, bbox, (255, 0, 0), "")

    return frames

def get_current_possession_percetanges(current_frames_idx, frames, possession):
    possession_percentage = {
        0: 0,
        1: 0
    }

    possession_frames = 0

    for frame_idx in range(current_frames_idx + 1):
        if possession[frame_idx] != -1:
            possession_percentage[possession[frame_idx]] += 1
            possession_frames += 1

    possession_percentage[0] = possession_percentage[0] / possession_frames * 100 if possession_frames > 0 else 0
    possession_percentage[1] = possession_percentage[1] / possession_frames * 100 if possession_frames > 0 else 0

    return possession_percentage

def draw_ball_possession(frames, ball_possession, team_0_color, team_1_color):
    for frame_idx in range(len(frames)):
        current_possession = get_current_possession_percetanges(frame_idx, frames, ball_possession)
        team_0_percentage = current_possession[0]
        team_1_percentage = current_possession[1]
        
        frame_width = frames[frame_idx].shape[1]
        frame_height = frames[frame_idx].shape[0]

        bottom_left_corner1 = (0 + 40 , frame_height - 150)
        bottom_left_corner2 = (0 + 40 , frame_height - 100)

        overlay = frames[frame_idx].copy()

        # Draw semi-transparent rectangle 
        cv2.rectangle(overlay, (20, frame_height - 200), (430, frame_height - 50), (255, 255, 255), -1)

        # Apply the overlay with a specified alpha value to create transparency
        alpha = 0.55  # Transparency factor
        cv2.addWeighted(overlay, alpha, frames[frame_idx], 1 - alpha, 0, frames[frame_idx])

        cv2.putText(frames[frame_idx], "Ball Possession", (100, frame_height - 170), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
         

        # Draw team 0 possesion as a progress bar in the bottom left right corner
        cv2.rectangle(frames[frame_idx], bottom_left_corner1, (int(40 + team_0_percentage * 3), frame_height - 120), team_0_color, -1)
        cv2.putText(frames[frame_idx], f"{int(team_0_percentage)}%", (int(50 + team_0_percentage * 3), frame_height - 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        # Draw team 1 possesion as a progress bar in the bottom left corner, above team 0
        cv2.rectangle(frames[frame_idx], bottom_left_corner2, (int(40 + team_1_percentage * 3), frame_height - 70), team_1_color, -1)
        cv2.putText(frames[frame_idx], f"{int(team_1_percentage)}%", (int(50 + team_1_percentage * 3), frame_height - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    return frames