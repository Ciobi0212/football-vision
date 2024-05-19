import datetime
import supervision as sv
import pickle
from ultralytics import YOLO

class Tracker:
    def __init__(self, model_path: str):
        self.yolo = YOLO(model_path)
        self.tracker = sv.ByteTrack()

    def get_yolo_predictions(self, frames):
        frame_batch_size = 24
        frames_batches = [frames[i:i+frame_batch_size] for i in range(0, len(frames), frame_batch_size)]
        result = []

        for frames_batch in frames_batches:
            yolo_predictions = self.yolo.predict(frames_batch)
            result.extend(yolo_predictions)

        return result
    
    def get_tracks(self, read_from_path=False, read_path=None, frames=None):

        if read_from_path == True:
            with open(read_path, "rb") as f:
                return pickle.load(f)
            
        tracks_dic = {
            "players": [], 
            "referees": [],  # Tracks is a dictionary with keys as the class names, each value is a list 
            "ball": [],
        }
        # Get YOLO predictions 
        yolo_predictions = self.get_yolo_predictions(frames)

        for frame_idx, prediction in enumerate(yolo_predictions):
            # Convert YOLO predictions to Supervision detections
            prediction_sv = sv.Detections.from_ultralytics(prediction)
            
            # The class goalkepper is irrelevant, consider it as a player (Goalkeeper is class 1 and player is class 2 in the YOLO model)
            prediction_sv.class_id[prediction_sv.class_id == 1] = 2

            # Track detections
            tracks = self.tracker.update_with_detections(prediction_sv)
            
            # Add a frame to the tracks
            tracks_dic["ball"].append([])
            tracks_dic["players"].append([])
            tracks_dic["referees"].append([])

            # Populate the players and referees tracks
            for i in range(len(tracks.class_id)):
                if tracks.class_id[i] == 2:  # Player
                    bouding_box = tracks.xyxy[i]
                    track_id = tracks.tracker_id[i]
                    tracks_dic["players"][frame_idx].append({"bbox": bouding_box, "track_id": track_id})
                elif tracks.class_id[i] == 3:  # Referee
                    bouding_box = tracks.xyxy[i]
                    track_id = tracks.tracker_id[i]
                    tracks_dic["referees"][frame_idx].append({"bbox": bouding_box, "track_id": track_id})

            # Populate the ball tracks from the yolo predictions, no reason to track the ball
            for i in range(len(prediction_sv.class_id)):
                if prediction_sv.class_id[i] == 0:  # Ball
                    bouding_box = prediction_sv.xyxy[i]
                    track_id = 0
                    tracks_dic["ball"][frame_idx].append({"bbox": bouding_box, "track_id": track_id})

        

        # Save the tracks to current directory
        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        with open(f"track/saved_tracks/tracks_{current_time}.pkl", "wb") as f:
            pickle.dump(tracks_dic, f)
            
        return tracks_dic
    