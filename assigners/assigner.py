from sklearn.cluster import KMeans
import cv2
import numpy as np
import matplotlib.pyplot as plt

class TeamAssigner:
    def __init__(self, player_tracks, frames):
        self.player_tracks = player_tracks
        self.first_frame = frames[0]
        self.kmeans = KMeans(n_clusters=2, init='k-means++', n_init=1)
        self.frames = frames

    def get_player_color(self, bbox, frame):
        x1, y1, x2, y2 = bbox

        # Get cropped image of the player
        player_img = frame[int(y1):int(y2), int(x1):int(x2)]

        # Get top half of the image
        player_img = player_img[:int(player_img.shape[0] / 2)]

        cv2.imwrite("player_half_img.jpg", player_img)
        # Resize the image to 2D array
        resized_player_img = np.reshape(player_img, (-1, 3))

        # Apply KMeans to get the dominant color
        kmeans = KMeans(n_clusters=2, init='k-means++', n_init=1).fit(resized_player_img)

        # Get labels of each pixel
        labels = kmeans.labels_

        # Get the clustered image
        clustered_img = np.reshape(labels, (player_img.shape[0], player_img.shape[1]))
        # clustered_img = np.uint8(255 * clustered_img / clustered_img.max())

        # cv2.imwrite("clustered_img.jpg", clustered_img)

        # Get the label of the bottom center pixel
        player_label = clustered_img[-1, int(clustered_img.shape[1] / 2)]
        # Get the player color
        player_color = kmeans.cluster_centers_[player_label]

        return player_color

    def get_team_colors(self):
        player_colors = []

        for player in self.player_tracks[0]: # Loop over the tracks in the first frame
            bbox = player['bbox'] # Bbox of the player in the first frame
            player_color = self.get_player_color(bbox, self.first_frame)
            player_colors.append(player_color)
            

        # Run self.kmeans on the player colors to get the team color clusters
        self.kmeans.fit(player_colors)

        print("Team colors: ", self.kmeans.cluster_centers_)
        team_0_color = self.kmeans.cluster_centers_[0]
        team_1_color = self.kmeans.cluster_centers_[1]

        return team_0_color, team_1_color

    def get_team_dic(self):
        self.get_team_colors()

        team_detections = [{}, {}]

        for frame_idx, frame in enumerate(self.frames):
            for player in self.player_tracks[frame_idx]:
                if frame_idx % 24 == 0:
                    bbox = player['bbox']
                    track_id = player['track_id']
                    player_color = self.get_player_color(bbox,frame)
                    team = self.kmeans.predict([player_color])[0]
                    if track_id not in team_detections[team].keys():
                        team_detections[team][track_id] = 0
                    
                    team_detections[team][track_id] += 1
                    

         # Assign team based on the most frequent team
        team_assignments = {
             0: set(),
             1: set()
        }

        for track_id, count in team_detections[0].items():
            if count > team_detections[1].get(track_id, 0):
                team_assignments[0].add(track_id)
            else:
                team_assignments[1].add(track_id)
        
        for track_id, count in team_detections[1].items():
            if count > team_detections[0].get(track_id, 0):
                team_assignments[1].add(track_id)
            else:
                team_assignments[0].add(track_id)

        return team_assignments
    

    def add_team_color_to_player_tracks(self):
        team_assignments = self.get_team_dic()

        for frame_idx, frame in enumerate(self.frames):
            for player in self.player_tracks[frame_idx]:
                track_id = player['track_id']
                if track_id in team_assignments[0]:
                    player['team_color'] = self.kmeans.cluster_centers_[0]
                    player['team'] = 0
                else:
                    player['team_color'] = self.kmeans.cluster_centers_[1]
                    player['team'] = 1

        team_0_color = self.kmeans.cluster_centers_[0]
        team_1_color = self.kmeans.cluster_centers_[1]

        return team_0_color, team_1_color

