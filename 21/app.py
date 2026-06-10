import os
import io
import csv
import zipfile
import tempfile
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import base64

from modules.angle_calculator import AngleCalculator
from modules.similarity_scorer import SimilarityScorer
from modules.suggestion_generator import SuggestionGenerator
from modules.image_overlay import ImageOverlay

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['RESULTS_FOLDER'] = os.path.join(os.path.dirname(__file__), 'results')

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'webp'}
ALLOWED_ARCHIVE_EXTENSIONS = {'zip'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

_pose_extractor = None
angle_calculator = AngleCalculator()
similarity_scorer = SimilarityScorer()
suggestion_generator = SuggestionGenerator()
image_overlay = ImageOverlay()


def get_pose_extractor():
    global _pose_extractor
    if _pose_extractor is None:
        from modules.pose_extractor import PoseExtractor
        _pose_extractor = PoseExtractor()
    return _pose_extractor


def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def read_image_from_file(file_storage):
    file_data = file_storage.read()
    np_array = np.frombuffer(file_data, np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    return image


def image_to_base64(image):
    _, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 85])
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    return f'data:image/jpeg;base64,{img_base64}'


def evaluate_pose(standard_image, practice_image):
    extractor = get_pose_extractor()
    standard_landmarks = extractor.extract_landmarks(standard_image)
    if standard_landmarks is None:
        return {
            'success': False,
            'error': '未能在标准姿势图中检测到人体姿态'
        }

    practice_landmarks = extractor.extract_landmarks(practice_image)
    if practice_landmarks is None:
        return {
            'success': False,
            'error': '未能在练习图中检测到人体姿态'
        }

    standard_angles = angle_calculator.calculate_all_angles(standard_landmarks)
    practice_angles = angle_calculator.calculate_all_angles(practice_landmarks)

    angle_differences = similarity_scorer.calculate_angle_differences(
        standard_angles, practice_angles
    )

    score, per_angle_score = similarity_scorer.calculate_similarity_score(angle_differences)

    high_diff_connections = similarity_scorer.get_high_diff_connections(angle_differences)

    suggestions = suggestion_generator.generate_suggestions(angle_differences)
    summary = suggestion_generator.generate_summary(score, suggestions)

    standard_pose_img = image_overlay.draw_pose(
        standard_image, standard_landmarks, []
    )
    practice_pose_img = image_overlay.draw_pose(
        practice_image, practice_landmarks, high_diff_connections
    )

    practice_pose_img = image_overlay.draw_labels(
        practice_pose_img, practice_landmarks, angle_differences
    )

    practice_pose_img = image_overlay.draw_score_bar(
        practice_pose_img, score, x=20, y=30
    )

    score_color = similarity_scorer.get_score_color(score)
    score_level = similarity_scorer.get_score_level(score)

    return {
        'success': True,
        'score': score,
        'score_color': score_color,
        'score_level': score_level,
        'angle_differences': angle_differences,
        'per_angle_score': per_angle_score,
        'suggestions': suggestions,
        'summary': summary,
        'standard_image': image_to_base64(standard_image),
        'practice_image': image_to_base64(practice_image),
        'standard_pose_image': image_to_base64(standard_pose_img),
        'practice_pose_image': image_to_base64(practice_pose_img),
        'high_diff_connections': [list(c) for c in high_diff_connections]
    }


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/evaluate', methods=['POST'])
def api_evaluate():
    if 'standard' not in request.files or 'practice' not in request.files:
        return jsonify({
            'success': False,
            'error': '请同时上传标准姿势图和练习图'
        })

    standard_file = request.files['standard']
    practice_file = request.files['practice']

    if standard_file.filename == '' or practice_file.filename == '':
        return jsonify({
            'success': False,
            'error': '文件名为空'
        })

    if not allowed_file(standard_file.filename, ALLOWED_IMAGE_EXTENSIONS):
        return jsonify({
            'success': False,
            'error': '标准姿势图格式不支持，请上传 PNG、JPG 或 JPEG 格式'
        })

    if not allowed_file(practice_file.filename, ALLOWED_IMAGE_EXTENSIONS):
        return jsonify({
            'success': False,
            'error': '练习图格式不支持，请上传 PNG、JPG 或 JPEG 格式'
        })

    try:
        standard_image = read_image_from_file(standard_file)
        practice_image = read_image_from_file(practice_file)

        if standard_image is None or practice_image is None:
            return jsonify({
                'success': False,
                'error': '图像读取失败'
            })

        result = evaluate_pose(standard_image, practice_image)
        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'处理出错: {str(e)}'
        })


@app.route('/api/batch-evaluate', methods=['POST'])
def api_batch_evaluate():
    if 'standard' not in request.files or 'practice_zip' not in request.files:
        return jsonify({
            'success': False,
            'error': '请同时上传标准姿势图和练习图 ZIP 压缩包'
        })

    standard_file = request.files['standard']
    practice_zip_file = request.files['practice_zip']

    if standard_file.filename == '' or practice_zip_file.filename == '':
        return jsonify({
            'success': False,
            'error': '文件名为空'
        })

    if not allowed_file(standard_file.filename, ALLOWED_IMAGE_EXTENSIONS):
        return jsonify({
            'success': False,
            'error': '标准姿势图格式不支持'
        })

    if not allowed_file(practice_zip_file.filename, ALLOWED_ARCHIVE_EXTENSIONS):
        return jsonify({
            'success': False,
            'error': '请上传 ZIP 格式的压缩包'
        })

    try:
        standard_image = read_image_from_file(standard_file)
        if standard_image is None:
            return jsonify({
                'success': False,
                'error': '标准姿势图读取失败'
            })

        extractor = get_pose_extractor()
        standard_landmarks = extractor.extract_landmarks(standard_image)
        if standard_landmarks is None:
            return jsonify({
                'success': False,
                'error': '未能在标准姿势图中检测到人体姿态'
            })

        standard_angles = angle_calculator.calculate_all_angles(standard_landmarks)

        zip_data = practice_zip_file.read()
        zip_buffer = io.BytesIO(zip_data)

        results = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        batch_folder = os.path.join(app.config['RESULTS_FOLDER'], f'batch_{timestamp}')
        os.makedirs(batch_folder, exist_ok=True)

        with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                if file_info.is_dir():
                    continue

                filename = file_info.filename
                if not allowed_file(filename, ALLOWED_IMAGE_EXTENSIONS):
                    continue

                base_name = os.path.basename(filename)
                if base_name.startswith('~$') or base_name.startswith('.'):
                    continue

                try:
                    file_data = zip_ref.read(filename)
                    np_array = np.frombuffer(file_data, np.uint8)
                    practice_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

                    if practice_image is None:
                        results.append({
                            'filename': filename,
                            'success': False,
                            'error': '图像读取失败'
                        })
                        continue

                    practice_landmarks = extractor.extract_landmarks(practice_image)
                    if practice_landmarks is None:
                        results.append({
                            'filename': filename,
                            'success': False,
                            'error': '未检测到人体姿态'
                        })
                        continue

                    practice_angles = angle_calculator.calculate_all_angles(practice_landmarks)

                    angle_differences = similarity_scorer.calculate_angle_differences(
                        standard_angles, practice_angles
                    )

                    score, per_angle_score = similarity_scorer.calculate_similarity_score(
                        angle_differences
                    )

                    high_diff_connections = similarity_scorer.get_high_diff_connections(
                        angle_differences
                    )

                    suggestions = suggestion_generator.generate_suggestions(angle_differences)

                    practice_pose_img = image_overlay.draw_pose(
                        practice_image, practice_landmarks, high_diff_connections
                    )
                    practice_pose_img = image_overlay.draw_score_bar(
                        practice_pose_img, score, x=20, y=30
                    )

                    safe_name = secure_filename(filename).replace('/', '_').replace('\\', '_')
                    output_path = os.path.join(batch_folder, f'annotated_{safe_name}')
                    cv2.imwrite(output_path, practice_pose_img)

                    results.append({
                        'filename': filename,
                        'success': True,
                        'score': score,
                        'score_level': similarity_scorer.get_score_level(score),
                        'suggestions': [s['suggestion'] for s in suggestions[:3]],
                        'annotated_image': f'results/batch_{timestamp}/annotated_{safe_name}'
                    })

                except Exception as e:
                    results.append({
                        'filename': filename,
                        'success': False,
                        'error': str(e)
                    })

        csv_path = os.path.join(batch_folder, 'evaluation_report.csv')
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([
                '文件名', '评分', '等级', '建议1', '建议2', '建议3', '状态'
            ])

            for r in results:
                if r['success']:
                    suggestions = r.get('suggestions', [])
                    writer.writerow([
                        r['filename'],
                        r['score'],
                        r['score_level'],
                        suggestions[0] if len(suggestions) > 0 else '',
                        suggestions[1] if len(suggestions) > 1 else '',
                        suggestions[2] if len(suggestions) > 2 else '',
                        '成功'
                    ])
                else:
                    writer.writerow([
                        r['filename'], '', '', '', '', '',
                        f'失败: {r.get("error", "未知错误")}'
                    ])

        success_count = sum(1 for r in results if r['success'])
        avg_score = 0
        if success_count > 0:
            avg_score = sum(r['score'] for r in results if r['success']) / success_count

        return jsonify({
            'success': True,
            'total_count': len(results),
            'success_count': success_count,
            'avg_score': round(avg_score, 1),
            'results': results,
            'csv_download_url': f'/results/batch_{timestamp}/evaluation_report.csv',
            'batch_folder': f'batch_{timestamp}'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'批量处理出错: {str(e)}'
        })


@app.route('/results/<path:filename>')
def download_result(filename):
    return send_from_directory(app.config['RESULTS_FOLDER'], filename, as_attachment=False)


@app.route('/download-csv/<batch_folder>')
def download_csv(batch_folder):
    csv_path = os.path.join(app.config['RESULTS_FOLDER'], batch_folder, 'evaluation_report.csv')
    if os.path.exists(csv_path):
        return send_file(csv_path, as_attachment=True,
                         download_name='evaluation_report.csv',
                         mimetype='text/csv')
    return jsonify({'error': '文件不存在'}), 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
