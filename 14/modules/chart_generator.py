import plotly.graph_objects as go
import plotly.io as pio
import json


class ChartGenerator:
    def __init__(self, region_stats, dist_stats=None):
        self.region_stats = region_stats
        self.dist_stats = dist_stats

    def _fig_to_json(self, fig):
        json_str = pio.to_json(fig)
        data = json.loads(json_str)
        return json.dumps(data, ensure_ascii=False)

    def generate_region_bar_chart(self):
        fig = go.Figure()

        x_vals = self.region_stats['区域'].astype(str).tolist()
        fare_vals = self.region_stats['平均车费'].astype(float).tolist()
        dist_vals = self.region_stats['平均距离'].astype(float).tolist()

        fig.add_trace(go.Bar(
            x=x_vals,
            y=fare_vals,
            name='平均车费（元）',
            marker_color='#FF6B6B',
            opacity=0.85,
            hovertemplate='区域: %{x}<br>平均车费: ¥%{y:.2f}<extra></extra>',
            yaxis='y'
        ))

        fig.add_trace(go.Bar(
            x=x_vals,
            y=dist_vals,
            name='平均距离（公里）',
            marker_color='#4ECDC4',
            opacity=0.85,
            hovertemplate='区域: %{x}<br>平均距离: %{y:.2f} km<extra></extra>',
            yaxis='y2'
        ))

        fig.update_layout(
            title=dict(
                text='各区域平均车费与平均距离对比',
                font=dict(size=20, family='Microsoft YaHei'),
                x=0.5
            ),
            xaxis=dict(
                title='区域',
                title_font=dict(size=14, family='Microsoft YaHei'),
                tickfont=dict(size=12, family='Microsoft YaHei')
            ),
            yaxis=dict(
                title=dict(text='平均车费（元）', font=dict(color='#FF6B6B', family='Microsoft YaHei')),
                tickfont=dict(color='#FF6B6B', family='Microsoft YaHei'),
                side='left'
            ),
            yaxis2=dict(
                title=dict(text='平均距离（公里）', font=dict(color='#4ECDC4', family='Microsoft YaHei')),
                tickfont=dict(color='#4ECDC4', family='Microsoft YaHei'),
                side='right',
                overlaying='y',
                showgrid=False
            ),
            barmode='group',
            legend=dict(
                x=0.01,
                y=0.99,
                bgcolor='rgba(255,255,255,0.8)',
                font=dict(family='Microsoft YaHei')
            ),
            height=600,
            template='plotly_white',
            margin=dict(l=60, r=60, t=80, b=60)
        )

        return self._fig_to_json(fig)

    def generate_distance_histogram(self, dist_stats):
        self.dist_stats = dist_stats

        x_vals = self.dist_stats['距离区间'].astype(str).tolist()
        y_vals = self.dist_stats['订单数'].astype(int).tolist()
        custom_vals = self.dist_stats['平均车费'].astype(float).tolist()

        colors = ['#FFE66D', '#FF6B6B', '#4ECDC4', '#95E1D3', '#A06CD5']

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=x_vals,
            y=y_vals,
            marker_color=colors,
            opacity=0.85,
            text=y_vals,
            textposition='outside',
            hovertemplate='距离区间: %{x}<br>订单数: %{y}<br>平均车费: ¥%{customdata:.2f}<extra></extra>',
            customdata=custom_vals
        ))

        fig.update_layout(
            title=dict(
                text='订单距离分布',
                font=dict(size=20, family='Microsoft YaHei'),
                x=0.5
            ),
            xaxis=dict(
                title='距离区间',
                title_font=dict(size=14, family='Microsoft YaHei'),
                tickfont=dict(size=12, family='Microsoft YaHei')
            ),
            yaxis=dict(
                title=dict(text='订单数量', font=dict(size=14, family='Microsoft YaHei')),
                tickfont=dict(size=12, family='Microsoft YaHei')
            ),
            height=600,
            template='plotly_white',
            margin=dict(l=60, r=60, t=80, b=60),
            showlegend=False
        )

        return self._fig_to_json(fig)
