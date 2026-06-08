import pandas as pd
import numpy as np
import math


class RegionAggregator:
    REGIONS = ['东', '南', '西', '北', '中', '东北']

    def __init__(self, df):
        self.df = df
        self.center_lat = df['上车纬度'].mean()
        self.center_lon = df['上车经度'].mean()

        lat_std = df['上车纬度'].std()
        lon_std = df['上车经度'].std()
        self.radius = min(lat_std, lon_std) * 0.6

    def assign_region(self, lat, lon):
        lat_diff = lat - self.center_lat
        lon_diff = lon - self.center_lon

        distance = math.sqrt(lat_diff ** 2 + lon_diff ** 2)

        if distance < self.radius:
            return '中'

        angle = math.degrees(math.atan2(lat_diff, lon_diff))

        if -22.5 <= angle < 22.5:
            return '东'
        elif 22.5 <= angle < 67.5:
            return '东北'
        elif 67.5 <= angle < 112.5:
            return '北'
        elif 112.5 <= angle < 157.5:
            return '西北'
        elif -67.5 <= angle < -22.5:
            return '东南'
        elif -112.5 <= angle < -67.5:
            return '南'
        elif -157.5 <= angle < -112.5:
            return '西南'
        else:
            return '西'

    def add_region_column(self):
        self.df['区域'] = self.df.apply(
            lambda row: self.assign_region(row['上车纬度'], row['上车经度']),
            axis=1
        )

        region_counts = self.df['区域'].value_counts()

        def remap_region(r):
            if r == '西北':
                return '西'
            elif r == '东南':
                return '南'
            elif r == '西南':
                return '西'
            return r

        self.df['区域'] = self.df['区域'].apply(remap_region)

        return self.df

    def get_region_stats(self):
        if '区域' not in self.df.columns:
            self.add_region_column()

        stats = self.df.groupby('区域').agg(
            订单数=('区域', 'count'),
            平均车费=('车费（元）', 'mean'),
            平均距离=('距离（公里）', 'mean'),
            总车费=('车费（元）', 'sum'),
            总距离=('距离（公里）', 'sum')
        ).reset_index()

        stats['平均车费'] = stats['平均车费'].round(2)
        stats['平均距离'] = stats['平均距离'].round(2)
        stats['总车费'] = stats['总车费'].round(2)
        stats['总距离'] = stats['总距离'].round(2)

        region_order = ['东', '南', '西', '北', '中', '东北']
        stats['区域'] = pd.Categorical(stats['区域'], categories=region_order, ordered=True)
        stats = stats.sort_values('区域').reset_index(drop=True)

        return stats

    def get_distance_bins(self):
        bins = [0, 5, 10, 15, 20, float('inf')]
        labels = ['0-5km', '5-10km', '10-15km', '15-20km', '20km+']

        df_copy = self.df.copy()
        df_copy['距离区间'] = pd.cut(
            df_copy['距离（公里）'],
            bins=bins,
            labels=labels,
            include_lowest=True,
            right=False
        )

        dist_stats = df_copy.groupby('距离区间', observed=False).agg(
            订单数=('距离区间', 'count'),
            平均车费=('车费（元）', 'mean')
        ).reset_index()

        dist_stats['平均车费'] = dist_stats['平均车费'].round(2)

        return dist_stats
