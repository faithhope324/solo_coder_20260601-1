from typing import Dict, List, Optional


class SuggestionGenerator:
    def __init__(self):
        self.suggestion_templates = self._get_suggestion_templates()

    def _get_suggestion_templates(self) -> Dict:
        return {
            'left_elbow': {
                'more_bend': '左臂弯曲角度不足，请增加左臂弯曲度',
                'less_bend': '左臂过度弯曲，请适当伸直左臂',
                'general': '左肘关节角度需要调整'
            },
            'right_elbow': {
                'more_bend': '右臂弯曲角度不足，请增加右臂弯曲度',
                'less_bend': '右臂过度弯曲，请适当伸直右臂',
                'general': '右肘关节角度需要调整'
            },
            'left_shoulder': {
                'more_bend': '左肩角度需要调整，建议加大肩部展开',
                'less_bend': '左肩角度过大，建议放松肩部',
                'general': '左肩关节需要调整'
            },
            'right_shoulder': {
                'more_bend': '右肩角度需要调整，建议加大肩部展开',
                'less_bend': '右肩角度过大，建议放松肩部',
                'general': '右肩关节需要调整'
            },
            'left_hip': {
                'more_bend': '左髋弯曲不够，请加深髋部前屈',
                'less_bend': '左髋过度弯曲，请适当挺直',
                'general': '左髋关节角度需要调整'
            },
            'right_hip': {
                'more_bend': '右髋弯曲不够，请加深髋部前屈',
                'less_bend': '右髋过度弯曲，请适当挺直',
                'general': '右髋关节角度需要调整'
            },
            'left_knee': {
                'more_bend': '左膝弯曲角度不足，请加大膝盖弯曲',
                'less_bend': '左膝过度弯曲，请适当伸直腿部',
                'general': '左膝关节角度需要调整'
            },
            'right_knee': {
                'more_bend': '右膝弯曲角度不足，请加大膝盖弯曲',
                'less_bend': '右膝过度弯曲，请适当伸直腿部',
                'general': '右膝关节角度需要调整'
            },
            'torso_left': {
                'more_bend': '左侧躯干弯曲不足，背部不够挺直',
                'less_bend': '左侧躯干过度前屈',
                'general': '躯干姿态需要调整'
            },
            'torso_right': {
                'more_bend': '右侧躯干弯曲不足，背部不够挺直',
                'less_bend': '右侧躯干过度前屈',
                'general': '躯干姿态需要调整'
            },
            'left_arm_raise': {
                'more_bend': '左臂抬升高度不够，请将左臂举得更高',
                'less_bend': '左臂抬升过高，请适当降低',
                'general': '左臂高度需要调整'
            },
            'right_arm_raise': {
                'more_bend': '右臂抬升高度不够，请将右臂举得更高',
                'less_bend': '右臂抬升过高，请适当降低',
                'general': '右臂高度需要调整'
            }
        }

    def generate_suggestions(
        self,
        angle_differences: Dict,
        threshold: float = 15.0,
        max_suggestions: int = 5
    ) -> List[Dict]:
        suggestions = []

        sorted_diffs = sorted(
            angle_differences.items(),
            key=lambda x: x[1]['difference'] if x[1]['difference'] is not None else -1,
            reverse=True
        )

        for angle_key, diff_info in sorted_diffs:
            if diff_info['difference'] is None:
                continue

            if diff_info['difference'] < threshold:
                continue

            std_angle = diff_info.get('standard')
            prac_angle = diff_info.get('practice')
            diff = diff_info['difference']
            name = diff_info.get('name', angle_key)

            direction = self._determine_direction(
                angle_key, std_angle, prac_angle
            )

            template = self.suggestion_templates.get(angle_key, {})
            suggestion_text = template.get(direction, template.get('general', f'{name}需要调整'))

            severity = self._get_severity(diff)

            suggestions.append({
                'angle_key': angle_key,
                'angle_name': name,
                'difference': round(diff, 1),
                'standard_angle': round(std_angle, 1) if std_angle else None,
                'practice_angle': round(prac_angle, 1) if prac_angle else None,
                'suggestion': suggestion_text,
                'severity': severity,
                'direction': direction
            })

            if len(suggestions) >= max_suggestions:
                break

        return suggestions

    def _determine_direction(
        self,
        angle_key: str,
        std_angle: float,
        prac_angle: float
    ) -> str:
        if prac_angle < std_angle:
            return 'more_bend'
        elif prac_angle > std_angle:
            return 'less_bend'
        else:
            return 'general'

    def _get_severity(self, diff: float) -> str:
        if diff >= 30:
            return 'high'
        elif diff >= 15:
            return 'medium'
        else:
            return 'low'

    def generate_summary(self, score: float, suggestions: List[Dict]) -> str:
        if score >= 90:
            base = '动作非常标准，继续保持！'
        elif score >= 75:
            base = '整体表现不错，还有提升空间。'
        elif score >= 60:
            base = '动作基本到位，需要多加练习。'
        elif score >= 40:
            base = '动作偏差较大，建议从基础开始练习。'
        else:
            base = '动作需要大幅调整，建议在教练指导下练习。'

        if suggestions:
            high_count = sum(1 for s in suggestions if s['severity'] == 'high')
            if high_count > 0:
                base += f' 注意有{high_count}个部位需要重点调整。'

        return base
