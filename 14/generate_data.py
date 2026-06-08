import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

def generate_orders(num_orders=5000):
    np.random.seed(42)
    random.seed(42)

    center_lat = 39.9042
    center_lon = 116.4074

    lats_pickup = np.random.normal(center_lat, 0.05, num_orders)
    lons_pickup = np.random.normal(center_lon, 0.06, num_orders)

    lat_offset = np.random.normal(0, 0.03, num_orders)
    lon_offset = np.random.normal(0, 0.04, num_orders)
    lats_dropoff = lats_pickup + lat_offset
    lons_dropoff = lons_pickup + lon_offset

    distances = np.abs(np.random.exponential(6, num_orders))
    distances = np.clip(distances, 0.5, 35.0)

    base_fare = 13.0
    per_km = 2.5
    fares = base_fare + distances * per_km + np.random.normal(0, 3, num_orders)
    fares = np.clip(fares, 10, 200)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)
    timestamps = []
    for _ in range(num_orders):
        delta = end_date - start_date
        random_seconds = random.randint(0, int(delta.total_seconds()))
        timestamps.append(start_date + timedelta(seconds=random_seconds))

    lats_pickup[10] = 999.0
    lons_pickup[25] = -999.0
    lats_dropoff[100] = 1000.0
    distances[50] = -5.0

    df = pd.DataFrame({
        '上车纬度': lats_pickup,
        '上车经度': lons_pickup,
        '下车纬度': lats_dropoff,
        '下车经度': lons_dropoff,
        '车费（元）': fares.round(2),
        '距离（公里）': distances.round(2),
        '时间戳': timestamps
    })

    os.makedirs('data', exist_ok=True)
    df.to_csv('data/orders.csv', index=False, encoding='utf-8-sig')
    print(f"已生成 {num_orders} 条订单数据，保存至 data/orders.csv")
    print(f"时间范围: {df['时间戳'].min()} 至 {df['时间戳'].max()}")

if __name__ == '__main__':
    generate_orders()
