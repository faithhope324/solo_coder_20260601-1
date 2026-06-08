import folium
from folium.plugins import HeatMap
import os


class MapGenerator:
    def __init__(self, df):
        self.df = df
        self.center_lat = df['上车纬度'].mean()
        self.center_lon = df['上车经度'].mean()

    def generate_heatmap(self, output_path='templates/heatmap_map.html'):
        m = folium.Map(
            location=[self.center_lat, self.center_lon],
            zoom_start=12,
            tiles='CartoDB positron'
        )

        heat_data = [
            [row['上车纬度'], row['上车经度']]
            for _, row in self.df.iterrows()
        ]

        gradient = {
            0.2: '#fee5d9',
            0.4: '#fcae91',
            0.6: '#fb6a4a',
            0.8: '#de2d26',
            1.0: '#a50f15'
        }

        HeatMap(
            heat_data,
            min_opacity=0.3,
            radius=18,
            blur=22,
            gradient=gradient,
            max_zoom=15
        ).add_to(m)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        m.save(output_path)
        print(f"热力地图已生成: {output_path}，包含 {len(heat_data)} 个数据点")
        return output_path

    def get_heatmap_html(self):
        m = folium.Map(
            location=[self.center_lat, self.center_lon],
            zoom_start=12,
            tiles='CartoDB positron'
        )

        heat_data = [
            [row['上车纬度'], row['上车经度']]
            for _, row in self.df.iterrows()
        ]

        gradient = {
            0.2: '#fee5d9',
            0.4: '#fcae91',
            0.6: '#fb6a4a',
            0.8: '#de2d26',
            1.0: '#a50f15'
        }

        HeatMap(
            heat_data,
            min_opacity=0.3,
            radius=18,
            blur=22,
            gradient=gradient,
            max_zoom=15
        ).add_to(m)

        return m._repr_html_()
