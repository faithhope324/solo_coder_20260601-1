import os
import cv2
import numpy as np
from typing import Optional, Dict
import urllib.request
import tempfile


class PoseExtractor:
    MODEL_URL = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task"
    MODEL_FILENAME = "pose_landmarker_full.task"

    def __init__(self, static_image_mode: bool = True, min_detection_confidence: float = 0.5,
                 model_path: Optional[str] = None):
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision

        self.static_image_mode = static_image_mode
        self.min_detection_confidence = min_detection_confidence

        if model_path is None:
            model_path = self._get_or_download_model()

        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_poses=1,
            min_pose_detection_confidence=min_detection_confidence,
            min_pose_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            output_segmentation_masks=False
        )

        self.detector = vision.PoseLandmarker.create_from_options(options)
        self.mp = __import__('mediapipe')

    def _get_or_download_model(self) -> str:
        cache_dir = os.path.join(tempfile.gettempdir(), 'mediapipe_models')
        os.makedirs(cache_dir, exist_ok=True)

        model_path = os.path.join(cache_dir, self.MODEL_FILENAME)

        if not os.path.exists(model_path):
            print(f"下载姿态检测模型: {self.MODEL_FILENAME} ...")
            try:
                urllib.request.urlretrieve(self.MODEL_URL, model_path)
                print(f"模型下载完成: {model_path}")
            except Exception as e:
                raise RuntimeError(f"模型下载失败: {e}")

        return model_path

    def extract_landmarks(self, image: np.ndarray) -> Optional[Dict]:
        if image is None:
            return None

        from mediapipe import Image as MPImage
        from mediapipe import ImageFormat

        h, w = image.shape[:2]

        mp_image = MPImage(image_format=ImageFormat.SRGB, data=cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        detection_result = self.detector.detect(mp_image)

        if not detection_result.pose_landmarks or len(detection_result.pose_landmarks) == 0:
            return None

        landmarks = detection_result.pose_landmarks[0]

        keypoints = []
        for idx, landmark in enumerate(landmarks):
            keypoints.append({
                'x': landmark.x,
                'y': landmark.y,
                'z': landmark.z,
                'visibility': landmark.visibility if hasattr(landmark, 'visibility') else 1.0,
                'pixel_x': int(landmark.x * w),
                'pixel_y': int(landmark.y * h)
            })

        return {
            'keypoints': keypoints,
            'image_width': w,
            'image_height': h,
            'num_keypoints': len(keypoints)
        }

    def extract_from_file(self, image_path: str) -> Optional[Dict]:
        image = cv2.imread(image_path)
        if image is None:
            return None
        return self.extract_landmarks(image)

    def get_normalized_coords(self, landmarks: Dict) -> np.ndarray:
        if not landmarks or 'keypoints' not in landmarks:
            return None

        keypoints = landmarks['keypoints']
        coords = []
        for kp in keypoints:
            coords.append([kp['x'], kp['y'], kp['z']])

        return np.array(coords)

    def close(self):
        if hasattr(self, 'detector') and self.detector:
            try:
                self.detector.close()
            except:
                pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
