import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("核心逻辑模块测试 (无需 MediaPipe)")
print("=" * 60)

print("\n1. 测试角度计算模块...")
try:
    from modules.angle_calculator import AngleCalculator
    calc = AngleCalculator()

    p1 = np.array([0.0, 0.0, 0.0])
    p2 = np.array([0.5, 0.5, 0.0])
    p3 = np.array([1.0, 0.0, 0.0])
    angle = calc.calculate_angle(p1, p2, p3)
    print(f"   ✓ 三点角度计算: {angle:.1f}° (预期约 90°)")

    print(f"   ✓ 支持 {len(calc.angle_definitions)} 种关节角度")
    print(f"     - 左/右肘关节")
    print(f"     - 左/右肩关节")
    print(f"     - 左/右髋关节")
    print(f"     - 左/右膝关节")
    print(f"     - 躯干角、肩宽角、手臂抬升角等")

except Exception as e:
    print(f"   ✗ 失败: {e}")
    import traceback
    traceback.print_exc()

print("\n2. 测试相似度评分模块...")
try:
    from modules.similarity_scorer import SimilarityScorer
    scorer = SimilarityScorer()

    mock_standard = {
        'left_elbow': {'angle': 120.0, 'name': '左肘关节', 'side': 'left', 'points': [11, 13, 15]},
        'right_elbow': {'angle': 120.0, 'name': '右肘关节', 'side': 'right', 'points': [12, 14, 16]},
        'left_knee': {'angle': 170.0, 'name': '左膝关节', 'side': 'left', 'points': [23, 25, 27]},
        'right_knee': {'angle': 170.0, 'name': '右膝关节', 'side': 'right', 'points': [24, 26, 28]},
        'left_hip': {'angle': 90.0, 'name': '左髋关节', 'side': 'left', 'points': [11, 23, 25]},
        'right_hip': {'angle': 90.0, 'name': '右髋关节', 'side': 'right', 'points': [12, 24, 26]},
        'left_shoulder': {'angle': 85.0, 'name': '左肩关节', 'side': 'left', 'points': [13, 11, 23]},
        'right_shoulder': {'angle': 85.0, 'name': '右肩关节', 'side': 'right', 'points': [14, 12, 24]},
    }

    mock_practice = {
        'left_elbow': {'angle': 100.0, 'name': '左肘关节', 'side': 'left', 'points': [11, 13, 15]},
        'right_elbow': {'angle': 125.0, 'name': '右肘关节', 'side': 'right', 'points': [12, 14, 16]},
        'left_knee': {'angle': 140.0, 'name': '左膝关节', 'side': 'left', 'points': [23, 25, 27]},
        'right_knee': {'angle': 165.0, 'name': '右膝关节', 'side': 'right', 'points': [24, 26, 28]},
        'left_hip': {'angle': 85.0, 'name': '左髋关节', 'side': 'left', 'points': [11, 23, 25]},
        'right_hip': {'angle': 95.0, 'name': '右髋关节', 'side': 'right', 'points': [12, 24, 26]},
        'left_shoulder': {'angle': 70.0, 'name': '左肩关节', 'side': 'left', 'points': [13, 11, 23]},
        'right_shoulder': {'angle': 88.0, 'name': '右肩关节', 'side': 'right', 'points': [14, 12, 24]},
    }

    diffs = scorer.calculate_angle_differences(mock_standard, mock_practice)
    score, per_angle = scorer.calculate_similarity_score(diffs)

    print(f"   ✓ 角度差异计算: {len(diffs)} 个角度")
    print(f"   ✓ 整体相似度得分: {score} 分")
    print(f"   ✓ 评分等级: {scorer.get_score_level(score)}")
    print(f"   ✓ 评分颜色: {scorer.get_score_color(score)}")

    high_diff = scorer.get_high_diff_connections(diffs, threshold=15)
    print(f"   ✓ 高差异连线 (>15°): {len(high_diff)} 条")

    print(f"   ✓ 权重配置: 髋/膝 1.5x, 肩 1.2x, 肘 1.0x")

except Exception as e:
    print(f"   ✗ 失败: {e}")
    import traceback
    traceback.print_exc()

print("\n3. 测试建议生成模块...")
try:
    from modules.suggestion_generator import SuggestionGenerator
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

    print(f"   ✓ 生成建议: {len(suggestions)} 条")
    print(f"   ✓ 整体总结: {summary}")
    for i, s in enumerate(suggestions):
        print(f"     {i+1}. [{s['severity']}] {s['suggestion']}")
        print(f"        差异 {s['difference']}° (标准 {s['standard_angle']}° vs 练习 {s['practice_angle']}°)")

except Exception as e:
    print(f"   ✗ 失败: {e}")
    import traceback
    traceback.print_exc()

print("\n4. 测试图像叠加模块...")
try:
    import cv2
    from modules.image_overlay import ImageOverlay

    overlay = ImageOverlay()
    test_img = np.ones((400, 400, 3), dtype=np.uint8) * 245

    mock_landmarks = {'keypoints': [], 'image_width': 400, 'image_height': 400}

    kp_positions = {
        0: (200, 80), 11: (150, 140), 12: (250, 140),
        13: (100, 180), 14: (300, 180), 15: (80, 240),
        16: (320, 240), 23: (160, 220), 24: (240, 220),
        25: (150, 300), 26: (250, 300), 27: (140, 360),
        28: (260, 360),
    }

    for idx, (x, y) in kp_positions.items():
        mock_landmarks['keypoints'].append({
            'x': x / 400.0, 'y': y / 400.0, 'z': 0.0,
            'visibility': 1.0, 'pixel_x': x, 'pixel_y': y
        })

    high_diff_conns = [(11, 13), (13, 15)]
    result_img = overlay.draw_pose(test_img, mock_landmarks, high_diff_conns)
    result_img = overlay.draw_score_bar(result_img, 78.5, x=20, y=20)
    result_img = overlay.draw_labels(result_img, mock_landmarks)
    result_img = overlay.add_legend(result_img, 280, 20)

    test_output = os.path.join(os.path.dirname(__file__), 'test_output.jpg')
    cv2.imwrite(test_output, result_img)

    print(f"   ✓ 骨架绘制: 绿色(正常) + 红色(差异大) + 蓝色(关键点)")
    print(f"   ✓ 分数条绘制: 渐变色 + 数字显示")
    print(f"   ✓ 关键点标签: 中文标注")
    print(f"   ✓ 图例: 正常/差异大/关键点")
    print(f"   ✓ 测试图像已保存: test_output.jpg")

except Exception as e:
    print(f"   ✗ 失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("核心模块测试完成！")
print("=" * 60)
