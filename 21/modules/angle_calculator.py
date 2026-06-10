import numpy as np
from typing import Dict, Optional


class AngleCalculator:
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    NOSE = 0
    LEFT_EAR = 7
    RIGHT_EAR = 8

    def __init__(self):
        self.angle_definitions = self._get_angle_definitions()

    def _get_angle_definitions(self) -> Dict:
        return {
            'left_elbow': {
                'points': [self.LEFT_SHOULDER, self.LEFT_ELBOW, self.LEFT_WRIST],
                'name': '左肘关节',
                'side': 'left'
            },
            'right_elbow': {
                'points': [self.RIGHT_SHOULDER, self.RIGHT_ELBOW, self.RIGHT_WRIST],
                'name': '右肘关节',
                'side': 'right'
            },
            'left_shoulder': {
                'points': [self.LEFT_ELBOW, self.LEFT_SHOULDER, self.LEFT_HIP],
                'name': '左肩关节',
                'side': 'left'
            },
            'right_shoulder': {
                'points': [self.RIGHT_ELBOW, self.RIGHT_SHOULDER, self.RIGHT_HIP],
                'name': '右肩关节',
                'side': 'right'
            },
            'left_hip': {
                'points': [self.LEFT_SHOULDER, self.LEFT_HIP, self.LEFT_KNEE],
                'name': '左髋关节',
                'side': 'left'
            },
            'right_hip': {
                'points': [self.RIGHT_SHOULDER, self.RIGHT_HIP, self.RIGHT_KNEE],
                'name': '右髋关节',
                'side': 'right'
            },
            'left_knee': {
                'points': [self.LEFT_HIP, self.LEFT_KNEE, self.LEFT_ANKLE],
                'name': '左膝关节',
                'side': 'left'
            },
            'right_knee': {
                'points': [self.RIGHT_HIP, self.RIGHT_KNEE, self.RIGHT_ANKLE],
                'name': '右膝关节',
                'side': 'right'
            },
            'torso_left': {
                'points': [self.LEFT_SHOULDER, self.LEFT_HIP, self.LEFT_ANKLE],
                'name': '左躯干角',
                'side': 'left'
            },
            'torso_right': {
                'points': [self.RIGHT_SHOULDER, self.RIGHT_HIP, self.RIGHT_ANKLE],
                'name': '右躯干角',
                'side': 'right'
            },
            'shoulder_width': {
                'points': [self.LEFT_SHOULDER, self.NOSE, self.RIGHT_SHOULDER],
                'name': '肩宽角',
                'side': 'center'
            },
            'left_arm_raise': {
                'points': [self.LEFT_HIP, self.LEFT_SHOULDER, self.LEFT_WRIST],
                'name': '左臂抬升角',
                'side': 'left'
            },
            'right_arm_raise': {
                'points': [self.RIGHT_HIP, self.RIGHT_SHOULDER, self.RIGHT_WRIST],
                'name': '右臂抬升角',
                'side': 'right'
            }
        }

    def calculate_angle(self, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
        v1 = p1 - p2
        v2 = p3 - p2

        dot = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)

        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0

        cos_angle = dot / (norm_v1 * norm_v2)
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        angle = np.degrees(np.arccos(cos_angle))

        return float(angle)

    def calculate_all_angles(self, landmarks: Dict) -> Optional[Dict]:
        if not landmarks or 'keypoints' not in landmarks:
            return None

        keypoints = landmarks['keypoints']
        angles = {}

        for angle_key, definition in self.angle_definitions.items():
            point_indices = definition['points']

            points = []
            valid = True
            for idx in point_indices:
                if idx >= len(keypoints):
                    valid = False
                    break
                kp = keypoints[idx]
                if kp.get('visibility', 0) < 0.3:
                    valid = False
                    break
                points.append(np.array([kp['x'], kp['y'], kp.get('z', 0)]))

            if valid and len(points) == 3:
                angle = self.calculate_angle(points[0], points[1], points[2])
                angles[angle_key] = {
                    'angle': angle,
                    'name': definition['name'],
                    'side': definition['side'],
                    'points': point_indices
                }
            else:
                angles[angle_key] = {
                    'angle': None,
                    'name': definition['name'],
                    'side': definition['side'],
                    'points': point_indices
                }

        return angles

    def get_primary_angles(self) -> list:
        return [
            'left_elbow', 'right_elbow',
            'left_shoulder', 'right_shoulder',
            'left_hip', 'right_hip',
            'left_knee', 'right_knee'
        ]
