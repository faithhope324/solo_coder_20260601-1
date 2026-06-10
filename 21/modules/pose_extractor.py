import os
import cv2
import numpy as np
from typing import Optional, Dict
import urllib.request
import socket


class PoseExtractor:
    MODEL_FILENAME = "pose_landmarker_full.task"
    MODEL_FILENAME_LITE = "pose_landmarker_lite.task"
    MODEL_SIZE_FULL = 9390340
    MODEL_SIZE_LITE = 4499236

    MIRROR_URLS = [
        {
            'name': 'ModelScope (国内镜像)',
            'url': 'https://modelscope.cn/models/mediapipe/pose_landmarker_full/resolve/master/pose_landmarker_full.task',
            'size': MODEL_SIZE_FULL
        },
        {
            'name': 'HF Mirror (国内镜像)',
            'url': 'https://hf-mirror.com/curt-park/mediapipe-pose-landmarker-full/resolve/main/pose_landmarker_full.task',
            'size': MODEL_SIZE_FULL
        },
        {
            'name': 'GitHub Raw',
            'url': 'https://raw.githubusercontent.com/google/mediapipe/master/mediapipe/modules/pose_landmark/pose_landmarker_full.task',
            'size': MODEL_SIZE_FULL
        },
        {
            'name': 'Google (官方源)',
            'url': 'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task',
            'size': MODEL_SIZE_FULL
        },
    ]

    def __init__(self, static_image_mode: bool = True, min_detection_confidence: float = 0.5,
                 model_path: Optional[str] = None, download_timeout: int = 60):
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision

        self.static_image_mode = static_image_mode
        self.min_detection_confidence = min_detection_confidence
        self.download_timeout = download_timeout

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

    def _get_cache_dir(self) -> str:
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cache_dir = os.path.join(project_dir, 'models')
        os.makedirs(cache_dir, exist_ok=True)
        return cache_dir

    def _get_or_download_model(self) -> str:
        cache_dir = self._get_cache_dir()
        model_path = os.path.join(cache_dir, self.MODEL_FILENAME)

        if self._is_model_valid(model_path, self.MODEL_SIZE_FULL):
            return model_path

        import tempfile
        temp_cache = os.path.join(tempfile.gettempdir(), 'mediapipe_models', self.MODEL_FILENAME)
        if self._is_model_valid(temp_cache, self.MODEL_SIZE_FULL):
            import shutil
            shutil.copy2(temp_cache, model_path)
            print(f"已从临时目录复制模型: {temp_cache} -> {model_path}")
            return model_path

        print(f"姿态检测模型未找到，正在下载: {self.MODEL_FILENAME}")
        print(f"将尝试 {len(self.MIRROR_URLS)} 个镜像源...\n")

        last_error = None
        for i, mirror in enumerate(self.MIRROR_URLS):
            print(f"[{i+1}/{len(self.MIRROR_URLS)}] 尝试: {mirror['name']}")
            try:
                self._download_with_progress(
                    mirror['url'], model_path, mirror.get('size'), self.download_timeout
                )
                if self._is_model_valid(model_path, mirror.get('size')):
                    print(f"\n✅ 模型下载成功: {model_path}")
                    return model_path
                else:
                    print(f"   ❌ 文件大小异常，尝试下一个镜像...")
                    if os.path.exists(model_path):
                        os.remove(model_path)
            except Exception as e:
                last_error = e
                print(f"   ❌ 下载失败: {str(e)[:80]}")
                print(f"   尝试下一个镜像...")
                if os.path.exists(model_path):
                    try:
                        os.remove(model_path)
                    except:
                        pass

        raise RuntimeError(
            f"\n所有镜像源下载均失败！\n"
            f"请手动下载模型文件并放置到以下路径:\n"
            f"  {model_path}\n\n"
            f"下载地址:\n"
            + "\n".join(f"  - {m['name']}: {m['url']}" for m in self.MIRROR_URLS)
            + (f"\n\n最后一次错误: {last_error}" if last_error else "")
        )

    def _is_model_valid(self, filepath: str, expected_size: Optional[int] = None) -> bool:
        if not os.path.exists(filepath):
            return False
        file_size = os.path.getsize(filepath)
        if file_size < 1000000:
            return False
        if expected_size and abs(file_size - expected_size) > 100000:
            return False
        return True

    def _download_with_progress(self, url: str, dest_path: str,
                                expected_size: Optional[int] = None, timeout: int = 60):
        socket.setdefaulttimeout(timeout)

        class ProgressHook:
            def __init__(self):
                self.last_percent = -1

            def __call__(self, block_num, block_size, total_size):
                if total_size <= 0:
                    total_size = expected_size or 0
                if total_size <= 0:
                    return
                downloaded = block_num * block_size
                percent = min(100, int(downloaded * 100 / total_size))
                if percent != self.last_percent:
                    self.last_percent = percent
                    bar_len = 20
                    filled = int(bar_len * percent / 100)
                    bar = '█' * filled + '░' * (bar_len - filled)
                    mb_downloaded = downloaded / (1024 * 1024)
                    mb_total = total_size / (1024 * 1024)
                    print(f"\r   {bar} {percent:3d}%  {mb_downloaded:.1f}/{mb_total:.1f} MB", end='', flush=True)

        hook = ProgressHook()
        urllib.request.urlretrieve(url, dest_path, reporthook=hook)
        print()

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
