import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class DataCleaner:
    def __init__(self, csv_path='data/orders.csv'):
        self.csv_path = csv_path
        self.df = None

    def load_data(self):
        self.df = pd.read_csv(self.csv_path, encoding='utf-8-sig')
        self.df['时间戳'] = pd.to_datetime(self.df['时间戳'])
        return self.df

    def clean(self):
        if self.df is None:
            self.load_data()

        initial_count = len(self.df)

        valid_lat_mask = (self.df['上车纬度'] >= -90) & (self.df['上车纬度'] <= 90)
        valid_lon_mask = (self.df['上车经度'] >= -180) & (self.df['上车经度'] <= 180)
        valid_dropoff_lat = (self.df['下车纬度'] >= -90) & (self.df['下车纬度'] <= 90)
        valid_dropoff_lon = (self.df['下车经度'] >= -180) & (self.df['下车经度'] <= 180)

        valid_distance = self.df['距离（公里）'] > 0
        valid_fare = self.df['车费（元）'] > 0

        mask = valid_lat_mask & valid_lon_mask & valid_dropoff_lat & valid_dropoff_lon & valid_distance & valid_fare
        self.df = self.df[mask].reset_index(drop=True)

        cleaned_count = initial_count - len(self.df)
        if cleaned_count > 0:
            print(f"数据清洗完成，移除 {cleaned_count} 条异常记录，剩余 {len(self.df)} 条有效数据")

        return self.df

    def filter_by_days(self, days):
        if self.df is None:
            self.clean()

        if days == 'all' or days is None:
            return self.df.copy()

        days = int(days)
        cutoff = datetime.now() - timedelta(days=days)
        filtered = self.df[self.df['时间戳'] >= cutoff].reset_index(drop=True)
        print(f"日期筛选：最近 {days} 天，共 {len(filtered)} 条订单")
        return filtered

    def get_city_center(self):
        if self.df is None:
            self.clean()
        return self.df['上车纬度'].mean(), self.df['上车经度'].mean()
