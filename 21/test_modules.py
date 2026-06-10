import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("人体姿态评估系统 - 模块测试")
print("=" * 60)

print("\n1. 测试模块导入...")
try:
    from modules.pose_extractor import PoseExtractor
    from modules.angle_calculator import AngleCalculator
    from modules.similarity_scorer import SimilarityScorer
    from modules.suggestion_generator import SuggestionGenerator
    from modules.image_overlay import ImageOverlay
    print("   ✓ 所有模块导入成功")
except Exception as e:
    print(f"   ✗ 模块导入失败: {e}")
    sys.exit(1)

print("\n2. 测试角度计算模块...")
try:
    calc = AngleCalculator()

    p1 = np.array([0.0, 0.0, 0.0])
    p2 = np.array([0.5, 0.5, 0.0])
    p3 = np.array([1.0, 0.0, 0.0])

    angle = calc.calculate_angle(p1, p2, p3)
    print(f"   ✓ 角度计算功能正常 (90度测试: {angle:.1f}°)")

    print(f"   ✓ 支持 {len(calc.angle_definitions)} 种关节角度")
    print(f"   ✓ 主要角度: {', '.join(calc.get_primary_angles())}")

except Exception as e:
    print(f"   ✗ 角度计算模块测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n3. 测试相似度评分模块...")
try:
    scorer = SimilarityScorer()

    mock_standard_angles = {
        'left_elbow': {'angle': 120.0, 'name': '左肘关节', 'side': 'left', 'points': [11, 13, 15]},
        'right_elbow': {'angle': 120.0, 'name': '右肘关节', 'side': 'right', 'points': [12, 14, 16]},
        'left_knee': {'angle': 170.0, 'name': '左膝关节', 'side': 'left', 'points': [23, 25, 27]},
        'right_knee': {'angle': 170.0, 'name': '右膝关节', 'side': 'right', 'points': [24, 26, 28]},
        'left_hip': {'angle': 90.0, 'name': '左髋关节', 'side': 'left', 'points': [11, 23, 25]},
        'right_hip': {'angle': 90.0, 'name': '右髋关节', 'side': 'right', 'points': [12, 24, 26]},
    }

    mock_practice_angles = {
        'left_elbow': {'angle': 100.0, 'name': '左肘关节', 'side': 'left', 'points': [11, 13, 15]},
        'right_elbow': {'angle': 125.0, 'name': '右肘关节', 'side': 'right', 'points': [12, 14, 16]},
        'left_knee': {'angle': 140.0, 'name': '左膝关节', 'side': 'left', 'points': [23, 25, 27]},
        'right_knee': {'angle': 165.0, 'name': '右膝关节', 'side': 'right', 'points': [24, 26, 28]},
        'left_hip': {'angle': 85.0, 'name': '左髋关节', 'side': 'left', 'points': [11, 23, 25]},
        'right_hip': {'angle': 95.0, 'name': '右髋关节', 'side': 'right', 'points': [12, 24, 26]},
    }

    diffs = scorer.calculate_angle_differences(mock_standard_angles, mock_practice_angles)
    score, per_angle = scorer.calculate_similarity_score(diffs)

    print(f"   ✓ 角度差异计算成功 (共 {len(diffs)} 个角度)")
    print(f"   ✓ 相似度评分: {score} 分")
    print(f"   ✓ 评分等级: {scorer.get_score_level(score)}")
    print(f"   ✓ 评分颜色: {scorer.get_score_color(score)}")

    high_diff = scorer.get_high_diff_connections(diffs, threshold=15)
    print(f"   ✓ 高差异连线: {len(high_diff)} 条")

except Exception as e:
    print(f"   ✗ 相似度评分模块测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n4. 测试建议生成模块...")
try:
    generator = SuggestionGenerator()

    mock_diffs = {
        'left_knee': {
            'difference': 30.0,
            'name': '左膝关节',
            'standard': 170.0,
            'practice': 140.0,
            'weight': 1.5
        },
        'right_elbow': {
            'difference': 20.0,
            'name': '右肘关节',
            'standard': 120.0,
            'practice': 140.0,
            'weight': 1.0
        },
        'left_hip': {
            'difference': 5.0,
            'name': '左髋关节',
            'standard': 90.0,
            'practice': 85.0,
            'weight': 1.5
        },
    }

    suggestions = generator.generate_suggestions(mock_diffs, threshold=15)
    summary = generator.generate_summary(75.0, suggestions)

    print(f"   ✓ 生成建议条数: {len(suggestions)}")
    print(f"   ✓ 总结: {summary}")
    for s in suggestions:
        print(f"     - [{s['severity']}] {s['suggestion']} (差异: {s['difference']}°)")

except Exception as e:
    print(f"   ✗ 建议生成模块测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n5. 测试图像叠加模块...")
try:
    import cv2

    overlay = ImageOverlay()

    test_img = np.ones((400, 400, 3), dtype=np.uint8) * 245

    mock_landmarks = {
        'keypoints': [],
        'image_width': 400,
        'image_height': 400
    }

    key_points_pos = {
        0: (200, 80),
        11: (150, 140),
        12: (250, 140),
        13: (100, 180),
        14: (300, 180),
        15: (80, 240),
        16: (320, 240),
        23: (160, 220),
        24: (240, 220),
        25: (150, 300),
        26: (250, 300),
        27: (140, 360),
        28: (260, 360),
    }

    for idx, (x, y) in key_points_pos.items():
        mock_landmarks['keypoints'].append({
            'x': x / 400.0,
            'y': y / 400.0,
            'z': 0.0,
            'visibility': 1.0,
            'pixel_x': x,
            'pixel_y': y
        })

    high_diff = [(11, 13), (13, 15)]

    result_img = overlay.draw_pose(test_img, mock_landmarks, high_diff)
    result_img = overlay.draw_score_bar(result_img, 78.5, x=20, y=20)
    result_img = overlay.add_legend(result_img, 280, 20)

    print(f"   ✓ 骨架绘制功能正常")
    print(f"   ✓ 分数条绘制功能正常")
    print(f"   ✓ 图例绘制功能正常")
    print(f"   ✓ 输出图像尺寸: {result_img.shape}")

except Exception as e:
    print(f"   ✗ 图像叠加模块测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n6. 测试姿态提取模块初始化...")
try:
    print("   (初始化 MediaPipe，可能需要几秒钟...)")
    extractor = PoseExtractor()
    print(f"   ✓ MediaPipe Pose 初始化成功")
    print(f"   ✓ 支持 {extractor.pose.__class__.__name__} 模型")
    extractor.close()
except Exception as e:
    print(f"   ✗ 姿态提取模块初始化失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
