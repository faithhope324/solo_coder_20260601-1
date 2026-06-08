import sys
sys.path.insert(0, '.')
from app import app

client = app.test_client()

tests = [
    ('/', '首页'),
    ('/heatmap', '热力图(全部)'),
    ('/heatmap?days=7', '热力图(7天)'),
    ('/heatmap?days=30', '热力图(30天)'),
    ('/region', '区域统计'),
    ('/distance', '距离分布'),
]

print("=" * 60)
print("测试Flask路由测试")
print("=" * 60)
all_pass = True
for url, name in tests:
    try:
        resp = client.get(url)
        status = "PASS" if resp.status_code == 200 else "FAIL"
        if resp.status_code != 200:
            all_pass = False
        print(f"[{status}] {name:<20} -> {resp.status_code} ({len(resp.data)} bytes)")
    except Exception as e:
        all_pass = False
        print(f"[ERR ] {name:<20} -> {e}")

print("=" * 60)
if all_pass:
    print("✓ 所有测试通过！")
else:
    print("✗ 部分测试失败！")
