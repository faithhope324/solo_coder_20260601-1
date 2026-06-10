import numpy as np
from typing import Dict, Optional, List, Tuple


class SimilarityScorer:
    def __init__(self):
        self.angle_weights = self._get_angle_weights()
        self.threshold = 15.0

    def _get_angle_weights(self) -> Dict[str, float]:
        return {
            'left_hip': 1.5,
            'right_hip': 1.5,
            'left_knee': 1.5,
            'right_knee': 1.5,
            'left_shoulder': 1.2,
            'right_shoulder': 1.2,
            'left_elbow': 1.0,
            'right_elbow': 1.0,
            'torso_left': 1.3,
            'torso_right': 1.3,
            'left_arm_raise': 0.8,
            'right_arm_raise': 0.8,
            'shoulder_width': 0.5
        }

    def calculate_angle_differences(
        self,
        standard_angles: Dict,
        practice_angles: Dict
    ) -> Dict:
        differences = {}

        all_angle_keys = set(list(standard_angles.keys()) + list(practice_angles.keys()))

        for angle_key in all_angle_keys:
            std_angle = standard_angles.get(angle_key, {}).get('angle')
            prac_angle = practice_angles.get(angle_key, {}).get('angle')
            name = standard_angles.get(angle_key, {}).get('name', angle_key)

            if std_angle is not None and prac_angle is not None:
                diff = abs(std_angle - prac_angle)
                differences[angle_key] = {
                    'standard': std_angle,
                    'practice': prac_angle,
                    'difference': diff,
                    'name': name,
                    'weight': self.angle_weights.get(angle_key, 1.0)
                }
            else:
                differences[angle_key] = {
                    'standard': std_angle,
                    'practice': prac_angle,
                    'difference': None,
                    'name': name,
                    'weight': self.angle_weights.get(angle_key, 1.0)
                }

        return differences

    def calculate_similarity_score(
        self,
        angle_differences: Dict
    ) -> Tuple[float, Dict]:
        total_weight = 0.0
        weighted_sum = 0.0
        valid_angles = 0

        per_angle_score = {}

        for angle_key, diff_info in angle_differences.items():
            if diff_info['difference'] is None:
                per_angle_score[angle_key] = {
                    'score': None,
                    'name': diff_info['name']
                }
                continue

            diff = diff_info['difference']
            weight = diff_info['weight']

            score = self._angle_diff_to_score(diff)

            weighted_sum += score * weight
            total_weight += weight
            valid_angles += 1

            per_angle_score[angle_key] = {
                'score': score,
                'difference': diff,
                'name': diff_info['name'],
                'weight': weight
            }

        if total_weight == 0:
            return 0.0, per_angle_score

        overall_score = (weighted_sum / total_weight) * 100
        overall_score = min(100.0, max(0.0, overall_score))

        return round(overall_score, 1), per_angle_score

    def _angle_diff_to_score(self, diff_degrees: float) -> float:
        if diff_degrees <= 5:
            return 1.0
        elif diff_degrees <= 15:
            return 1.0 - (diff_degrees - 5) / 10 * 0.3
        elif diff_degrees <= 30:
            return 0.7 - (diff_degrees - 15) / 15 * 0.4
        elif diff_degrees <= 45:
            return 0.3 - (diff_degrees - 30) / 15 * 0.2
        else:
            return max(0.0, 0.1 - (diff_degrees - 45) / 45 * 0.1)

    def get_high_diff_connections(
        self,
        angle_differences: Dict,
        threshold: Optional[float] = None
    ) -> List[Tuple[int, int]]:
        if threshold is None:
            threshold = self.threshold

        high_diff_connections = []

        for angle_key, diff_info in angle_differences.items():
            if diff_info['difference'] is not None and diff_info['difference'] > threshold:
                points = diff_info.get('points', [])
                if len(points) >= 2:
                    high_diff_connections.append((points[0], points[1]))
                    if len(points) >= 3:
                        high_diff_connections.append((points[1], points[2]))

        return high_diff_connections

    def get_score_level(self, score: float) -> str:
        if score >= 90:
            return 'excellent'
        elif score >= 75:
            return 'good'
        elif score >= 60:
            return 'fair'
        elif score >= 40:
            return 'poor'
        else:
            return 'very_poor'

    def get_score_color(self, score: float) -> str:
        if score >= 85:
            return '#22c55e'
        elif score >= 70:
            return '#84cc16'
        elif score >= 55:
            return '#eab308'
        elif score >= 40:
            return '#f97316'
        else:
            return '#ef4444'
