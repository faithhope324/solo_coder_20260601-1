import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple


class ImageOverlay:
    def __init__(self):
        self.green_color = (34, 197, 94)
        self.red_color = (239, 68, 68)
        self.yellow_color = (234, 179, 8)
        self.blue_color = (59, 130, 246)
        self.white_color = (255, 255, 255)

        self.pose_connections = [
            (11, 12),
            (11, 13),
            (13, 15),
            (12, 14),
            (14, 16),
            (11, 23),
            (12, 24),
            (23, 24),
            (23, 25),
            (25, 27),
            (24, 26),
            (26, 28),
            (0, 11),
            (0, 12),
            (27, 31),
            (28, 32),
            (15, 17),
            (15, 19),
            (16, 18),
            (16, 20)
        ]

    def draw_pose(
        self,
        image: np.ndarray,
        landmarks: Dict,
        high_diff_connections: Optional[List[Tuple[int, int]]] = None,
        line_thickness: int = 3,
        point_radius: int = 5
    ) -> np.ndarray:
        if image is None or landmarks is None:
            return image

        result_image = image.copy()
        keypoints = landmarks.get('keypoints', [])

        if not keypoints:
            return result_image

        if high_diff_connections is None:
            high_diff_connections = []

        high_diff_set = set()
        for conn in high_diff_connections:
            high_diff_set.add(tuple(sorted(conn)))

        for start_idx, end_idx in self.pose_connections:
            if start_idx >= len(keypoints) or end_idx >= len(keypoints):
                continue

            start_kp = keypoints[start_idx]
            end_kp = keypoints[end_idx]

            if start_kp.get('visibility', 0) < 0.3 or end_kp.get('visibility', 0) < 0.3:
                continue

            start_point = (start_kp['pixel_x'], start_kp['pixel_y'])
            end_point = (end_kp['pixel_x'], end_kp['pixel_y'])

            conn_key = tuple(sorted((start_idx, end_idx)))

            if conn_key in high_diff_set:
                color = self.red_color
            else:
                color = self.green_color

            cv2.line(
                result_image,
                start_point,
                end_point,
                color,
                line_thickness,
                lineType=cv2.LINE_AA
            )

        for idx, kp in enumerate(keypoints):
            if kp.get('visibility', 0) < 0.3:
                continue

            point = (kp['pixel_x'], kp['pixel_y'])

            cv2.circle(
                result_image,
                point,
                point_radius,
                self.blue_color,
                -1,
                lineType=cv2.LINE_AA
            )
            cv2.circle(
                result_image,
                point,
                point_radius + 2,
                self.white_color,
                1,
                lineType=cv2.LINE_AA
            )

        return result_image

    def draw_score_bar(
        self,
        image: np.ndarray,
        score: float,
        x: int = 20,
        y: int = 50,
        width: int = 200,
        height: int = 30
    ) -> np.ndarray:
        result_image = image.copy()

        score_ratio = score / 100.0

        cv2.rectangle(
            result_image,
            (x, y),
            (x + width, y + height),
            (200, 200, 200),
            -1
        )

        fill_width = int(width * score_ratio)
        color = self._get_score_color_bgr(score)

        cv2.rectangle(
            result_image,
            (x, y),
            (x + fill_width, y + height),
            color,
            -1
        )

        cv2.rectangle(
            result_image,
            (x, y),
            (x + width, y + height),
            (100, 100, 100),
            2
        )

        text = f'{score:.1f} 分'
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        thickness = 2

        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        text_x = x + (width - text_size[0]) // 2
        text_y = y + height + text_size[1] + 5

        cv2.putText(
            result_image,
            text,
            (text_x, text_y),
            font,
            font_scale,
            (50, 50, 50),
            thickness,
            lineType=cv2.LINE_AA
        )

        return result_image

    def draw_labels(
        self,
        image: np.ndarray,
        landmarks: Dict,
        angle_differences: Optional[Dict] = None,
        font_scale: float = 0.5,
        thickness: int = 1
    ) -> np.ndarray:
        result_image = image.copy()
        keypoints = landmarks.get('keypoints', [])

        if not keypoints:
            return result_image

        label_points = {
            11: '左肩',
            12: '右肩',
            13: '左肘',
            14: '右肘',
            15: '左腕',
            16: '右腕',
            23: '左髋',
            24: '右髋',
            25: '左膝',
            26: '右膝',
            27: '左踝',
            28: '右踝'
        }

        for idx, label in label_points.items():
            if idx >= len(keypoints):
                continue
            kp = keypoints[idx]
            if kp.get('visibility', 0) < 0.3:
                continue

            point = (kp['pixel_x'] + 8, kp['pixel_y'] - 8)

            cv2.putText(
                result_image,
                label,
                point,
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale,
                (255, 255, 255),
                thickness + 1,
                lineType=cv2.LINE_AA
            )
            cv2.putText(
                result_image,
                label,
                point,
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale,
                (0, 0, 0),
                thickness,
                lineType=cv2.LINE_AA
            )

        return result_image

    def _get_score_color_bgr(self, score: float) -> Tuple[int, int, int]:
        if score >= 85:
            return (94, 197, 34)
        elif score >= 70:
            return (22, 204, 132)
        elif score >= 55:
            return (8, 179, 234)
        elif score >= 40:
            return (22, 115, 249)
        else:
            return (68, 68, 239)

    def add_legend(self, image: np.ndarray, x: int, y: int) -> np.ndarray:
        result_image = image.copy()

        items = [
            ('正常', self.green_color),
            ('差异大', self.red_color),
            ('关键点', self.blue_color)
        ]

        current_y = y

        for label, color in items:
            cv2.circle(
                result_image,
                (x + 10, current_y),
                6,
                color,
                -1
            )
            cv2.putText(
                result_image,
                label,
                (x + 25, current_y + 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (50, 50, 50),
                1,
                lineType=cv2.LINE_AA
            )
            current_y += 25

        return result_image

    def create_comparison_view(
        self,
        standard_img: np.ndarray,
        practice_img: np.ndarray,
        standard_pose: np.ndarray,
        practice_pose: np.ndarray
    ) -> np.ndarray:
        h1, w1 = standard_img.shape[:2]
        h2, w2 = practice_img.shape[:2]

        target_h = max(h1, h2)
        target_w = max(w1, w2)

        def resize_pad(img, target_w, target_h):
            h, w = img.shape[:2]
            scale = min(target_w / w, target_h / h)
            new_w = int(w * scale)
            new_h = int(h * scale)
            resized = cv2.resize(img, (new_w, new_h))

            result = np.ones((target_h, target_w, 3), dtype=np.uint8) * 245
            y_off = (target_h - new_h) // 2
            x_off = (target_w - new_w) // 2
            result[y_off:y_off + new_h, x_off:x_off + new_w] = resized
            return result

        std_resized = resize_pad(standard_img, target_w, target_h)
        prac_resized = resize_pad(practice_img, target_w, target_h)
        std_pose_resized = resize_pad(standard_pose, target_w, target_h)
        prac_pose_resized = resize_pad(practice_pose, target_w, target_h)

        top_row = np.hstack([std_resized, prac_resized])
        bottom_row = np.hstack([std_pose_resized, prac_pose_resized])

        combined = np.vstack([top_row, bottom_row])

        label_h = 40
        full_h = combined.shape[0] + label_h * 2
        full_w = combined.shape[1]
        result = np.ones((full_h, full_w, 3), dtype=np.uint8) * 255

        result[label_h:label_h + combined.shape[0], :] = combined

        labels = ['标准姿势 (原图)', '练习姿势 (原图)', '标准姿势 (骨架)', '练习姿势 (骨架)']
        positions = [
            (target_w // 2, label_h // 2 + 5),
            (target_w + target_w // 2, label_h // 2 + 5),
            (target_w // 2, label_h + target_h * 2 + label_h // 2 + 5),
            (target_w + target_w // 2, label_h + target_h * 2 + label_h // 2 + 5)
        ]

        for label, (px, py) in zip(labels, positions):
            cv2.putText(
                result,
                label,
                (px - 60, py),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (50, 50, 50),
                2,
                lineType=cv2.LINE_AA
            )

        return result
