"""验证优化: 最小车优先单装 + 自动升级 + 限高 + 多车兜底"""
import sys; sys.path.insert(0, '/Users/iric/PyCharmMiscProject/进仓单')
from ongoing.app import *

print('=== 测试1: 货少选小车 ===')
items = [CargoItem(f'A{i}',120,80,100,121.5,81.5,101.5,500,False,'箱车',i,3,0) for i in range(1,6)]
tpls = [
    VehicleTemplate('箱车', 680, 240, 260, 10000),
    VehicleTemplate('箱车', 960, 245, 270, 18000),
]
v, u = BinPacker().pack(items, tpls)
print(f'车辆数={len(v)} 未装载={len(u)}')
for vi in v: print(f'  {vi.display_name}: {len(vi.placed_items)}件 {vi.used_payload:.0f}kg')
ok1 = len(v) == 1 and '6.8' in v[0].display_name
print(f'结果: {"✅ 选了最小车(6.8m)" if ok1 else "❌"}')

print()
print('=== 测试2: 货多自动升级到9.6m(6.8m装不下) ===')
items2 = [CargoItem(f'B{i}',200,150,180,201.5,151.5,181.5,1200,False,'箱车',i,3,0) for i in range(1,11)]
tpls2 = [
    VehicleTemplate('箱车', 680, 240, 260, 10000),
    VehicleTemplate('箱车', 960, 245, 270, 18000),
]
v2, u2 = BinPacker().pack(items2, tpls2)
print(f'车辆数={len(v2)} 未装载={len(u2)}')
for vi in v2: print(f'  {vi.display_name}: {len(vi.placed_items)}件 {vi.used_payload:.0f}kg')
# 用了9.6m而非6.8m即升级成功
ok2 = len(v2) >= 1 and all('9.6' in vi.display_name for vi in v2)
print(f'结果: {"✅ 全部使用9.6m(升级成功)" if ok2 else "❌"}')

print()
print('=== 测试3: 平板3m限高 ===')
items3 = [CargoItem('H',200,150,310,201,151,311,500,True,'平板车',1,3,0)]
tpls3 = [VehicleTemplate('平板车',1370,250,OPEN_TOP_MAX_HEIGHT,30000)]
v3, u3 = BinPacker().pack(items3, tpls3)
print(f'车辆数={len(v3)} 未装载={len(u3)}')
ok3 = len(u3) == 1
print(f'结果: {"✅ 限高生效" if ok3 else "❌"}')

print()
print('=== 测试4: 不指定车型选最小兼容车 ===')
items4 = [
    CargoItem('X',120,80,100,121.5,81.5,101.5,500,False,'不指定',1,3,0),
    CargoItem('Y',120,80,100,121.5,81.5,101.5,500,False,'不指定',2,3,0),
]
tpls4 = [
    VehicleTemplate('飞翼车', 680, 240, 260, 8000),
    VehicleTemplate('箱车', 960, 245, 270, 18000),
    VehicleTemplate('平板车', 1370, 250, OPEN_TOP_MAX_HEIGHT, 30000),
]
v4, u4 = BinPacker().pack(items4, tpls4)
print(f'车辆数={len(v4)} 未装载={len(u4)}')
for vi in v4: print(f'  {vi.display_name}')
ok4 = len(v4) == 1 and '6.8' in v4[0].display_name
print(f'结果: {"✅ 选了6.8m飞翼车" if ok4 else "❌"}')

print()
print('=== 测试5: 多车兜底(最大车也装不下全部) ===')
items5 = [CargoItem(f'G{i}',200,150,180,201.5,151.5,181.5,6000,False,'箱车',i,3,0) for i in range(1,8)]
tpls5 = [
    VehicleTemplate('箱车', 680, 240, 260, 10000),
    VehicleTemplate('箱车', 960, 245, 270, 18000),
]
v5, u5 = BinPacker().pack(items5, tpls5)
print(f'车辆数={len(v5)} 未装载={len(u5)}')
for vi in v5: print(f'  {vi.display_name}: {len(vi.placed_items)}件 {vi.used_payload:.0f}kg')
# 7件*6000kg=42000kg > 18000 → 必须多车
ok5 = len(v5) >= 2 and all('9.6' in vi.display_name for vi in v5)
print(f'结果: {"✅ 多车兜底正确" if ok5 else "❌"}')

print()
if ok1 and ok2 and ok3 and ok4 and ok5:
    print('✅ 全部优化验证通过')
else:
    print('❌ 有测试失败')
