from flask import Flask, render_template, request
from modules.data_cleaning import DataCleaner
from modules.region_aggregation import RegionAggregator
from modules.map_generator import MapGenerator
from modules.chart_generator import ChartGenerator

app = Flask(__name__)

cleaner = DataCleaner('data/orders.csv')
cleaner.clean()


def get_filtered_data(days):
    return cleaner.filter_by_days(days)


@app.route('/')
def index():
    return heatmap()


@app.route('/heatmap')
def heatmap():
    days = request.args.get('days', default='all', type=str)
    df = get_filtered_data(days)

    map_gen = MapGenerator(df)
    heatmap_html = map_gen.get_heatmap_html()

    stats = {
        'total_orders': len(df),
        'total_fare': round(df['车费（元）'].sum(), 2),
        'avg_fare': round(df['车费（元）'].mean(), 2),
        'avg_distance': round(df['距离（公里）'].mean(), 2)
    }

    return render_template(
        'heatmap.html',
        heatmap_html=heatmap_html,
        stats=stats,
        current_page='heatmap',
        current_days=days
    )


@app.route('/region')
def region():
    days = request.args.get('days', default='all', type=str)
    df = get_filtered_data(days)

    region_agg = RegionAggregator(df)
    region_stats = region_agg.get_region_stats()

    chart_gen = ChartGenerator(region_stats)
    bar_chart_json = chart_gen.generate_region_bar_chart()

    stats = {
        'total_orders': len(df),
        'total_fare': round(df['车费（元）'].sum(), 2),
        'avg_fare': round(df['车费（元）'].mean(), 2),
        'avg_distance': round(df['距离（公里）'].mean(), 2)
    }

    region_stats_list = region_stats.to_dict('records')

    return render_template(
        'region.html',
        bar_chart_json=bar_chart_json,
        region_stats=region_stats_list,
        stats=stats,
        current_page='region',
        current_days=days
    )


@app.route('/distance')
def distance():
    days = request.args.get('days', default='all', type=str)
    df = get_filtered_data(days)

    region_agg = RegionAggregator(df)
    dist_stats = region_agg.get_distance_bins()

    chart_gen = ChartGenerator(None)
    hist_chart_json = chart_gen.generate_distance_histogram(dist_stats)

    stats = {
        'total_orders': len(df),
        'total_fare': round(df['车费（元）'].sum(), 2),
        'avg_fare': round(df['车费（元）'].mean(), 2),
        'avg_distance': round(df['距离（公里）'].mean(), 2)
    }

    dist_stats_list = dist_stats.to_dict('records')

    return render_template(
        'distance.html',
        hist_chart_json=hist_chart_json,
        dist_stats=dist_stats_list,
        stats=stats,
        current_page='distance',
        current_days=days
    )


if __name__ == '__main__':
    print("已注册的路由:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint}")
    app.run(debug=False, host='0.0.0.0', port=5000)
