class BallAssigner:
    def __init__(self, ball_tracks, player_tracks, min_tolerated_distance=60):
        self.ball_tracks = ball_tracks
        self.player_tracks = player_tracks
        self.min_tolerated_distance = min_tolerated_distance
    
    def get_distance(self, p1, p2):
        return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5
    
    def get_center_of_bbox(self, bbox):
        return (bbox[0] + (bbox[2] - bbox[0]) / 2), (bbox[1] + (bbox[3] - bbox[1]) / 2)

    def assign_ball_to_player(self):
        for frame_idx in range(len(self.player_tracks)):
            min_found_distance = 1000000
            best_fit_idx = -1

            if len(self.ball_tracks[frame_idx]) > 0: # If there is ball detection in the frame
                ball_bbox = self.ball_tracks[frame_idx][0]['bbox']
                print(ball_bbox)
                ball_center = self.get_center_of_bbox(ball_bbox)

                for player_idx, player in enumerate(self.player_tracks[frame_idx]):
                    player_bbox = player['bbox']
                    player_left_foot = (player_bbox[0], player_bbox[3])
                    player_right_foot = (player_bbox[2], player_bbox[3])

                    distance_to_left_foot = self.get_distance(ball_center, player_left_foot)
                    distance_to_right_foot = self.get_distance(ball_center, player_right_foot)

                    if distance_to_left_foot < self.min_tolerated_distance or distance_to_right_foot < self.min_tolerated_distance:
                        if distance_to_left_foot < min_found_distance:
                            min_found_distance = distance_to_left_foot
                            best_fit_idx = player_idx

                        if distance_to_right_foot < min_found_distance:
                            min_found_distance = distance_to_right_foot
                            best_fit_idx = player_idx

            for player in self.player_tracks[frame_idx]:
                player['has_ball'] = False

            if best_fit_idx != -1:
                self.player_tracks[frame_idx][best_fit_idx]['has_ball'] = True
                

    