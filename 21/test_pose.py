import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modules.pose_extractor import PoseExtractor
import numpy as np
import cv2

print("=" * 60)
print("姿态提取模块测试")
print("=" * 60)

print("\n1. 初始化 PoseExtractor...")
print("   (首次运行会下载模型文件，请耐心等待)")
try:
    extractor = PoseExtractor()
    print("   ✓ PoseExtractor 初始化成功")
except Exception as e:
    print(f"   ✗ 初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n2. 测试空白图像 (预期无检测结果)...")
blank_img = np.ones((400, 400, 3), dtype=np.uint8) * 255
result = extractor.extract_landmarks(blank_img)
if result is None:
    print("   ✓ 空白图像正确返回 None (无姿态)")
else:
    print(f"   ✗ 意外检测到 {result['num_keypoints']} 个关键点")

print("\n3. 验证关键点数量 (用简单的人形轮廓测试)...")
test_img = np.ones((600, 400, 3), dtype=np.uint8) * 245

cv2.circle(test_img, (200, 100), 30, (200, 150, 100), -1)

cv2.line(test_img, (200, 130), (200, 300), (200, 150, 100), 20)

cv2.line(test_img, (200, 160), (120, 240), (200, 150, 100), 15)
cv2.line(test_img, (200, 160), (280, 240), (200, 150, 100), 15)

cv2.line(test_img, (200, 300), (150, 480), (200, 150, 100), 18)
cv2.line(test_img, (200, 300), (250, 480), (200, 150, 100), 18)

result = extractor.extract_landmarks(test_img)
if result is not None:
    print(f"   ✓ 检测到 {result['num_keypoints']} 个关键点")
    print(f"   ✓ 图像尺寸: {result['image_width']}x{result['image_height']}")

    vis_count = sum(1 for kp in result['keypoints'] if kp['visibility'] > 0.5)
    print(f"   ✓ 可见关键点数量: {vis_count}")

    test_output = os.path.join(os.path.dirname(__file__), 'test_pose.jpg')
    from modules.image_overlay import ImageOverlay
    overlay = ImageOverlay()
    result_img = overlay.draw_pose(test_img, result, [])
    cv2.imwrite(test_output, result_img)
    print(f"   ✓ 姿态检测结果图已保存: test_pose.jpg")
else:
    print("   - 未能检测到姿态 (简单绘制的人形可能不够清晰)")
    print("   - 这是正常的，使用真实照片效果会更好")

extractor.close()

print("\n" + "=" * 60)
print("姿态提取模块测试完成!")
print("=" * 60)
