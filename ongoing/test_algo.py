"""算法单元测试"""
import sys
sys.path.insert(0, '/Users/iric/PyCharmMiscProject/进仓单')
from ongoing.app import (
    BinPacker, CargoItem, VehicleTemplate, VehicleInstance,
    BUFFER_FIXED_BOTTOM, BUFFER_UNFIXED, AREA_SUPPORT_RATIO,
)

print('=== 全局参数 ===')
print(f'BUFFER_FIXED: {BUFFER_FIXED_BOTTOM}')
print(f'BUFFER_UNFIXED: {BUFFER_UNFIXED}')
print(f'AREA_RATIO: {AREA_SUPPORT_RATIO}')

print('\n=== 货物旋转方向 ===')
items = [
    CargoItem('A001', 120,80,100, 121.5,81.5,101.5, 500, False, '箱车', 1, 3, 0),
    CargoItem('A002', 200,150,50, 201,151,51, 800, True, '箱车', 2, 2, 0),
]
for it in items:
    orients = BinPacker().get_orientations(it)
    print(f'{it.display_id} fixed={it.fixed_bottom} → {len(orients)}种方向')

print('\n=== 装箱测试 ===')
templates = [
    VehicleTemplate('箱车', 960, 245, 270, 18000),
    VehicleTemplate('平板车', 1370, 250, float('inf'), 30000),
]
packer = BinPacker()
vehicles, unplaced = packer.pack(items, templates)

print(f'车辆数: {len(vehicles)}, 未装载: {len(unplaced)}')
for i, v in enumerate(vehicles):
    print(f'车辆{i+1}: {v.display_name} 件数={len(v.placed_items)} 重量={v.used_payload:.0f}kg')
    for p in v.placed_items:
        print(f'  {p.cargo_item.display_id} ({p.placed_l:.0f}x{p.placed_w:.0f}x{p.placed_h:.0f}) @ ({p.x:.0f},{p.y:.0f},{p.z:.0f})')

# 重叠检查
print('\n=== 重叠检查 ===')
ok = True
for v in vehicles:
    items_list = v.placed_items
    for i in range(len(items_list)):
        for j in range(i+1, len(items_list)):
            a, b = items_list[i], items_list[j]
            overlap = not (a.x2<=b.x or b.x2<=a.x or a.y2<=b.y or b.y2<=a.y or a.z2<=b.z or b.z2<=a.z)
            if overlap:
                print(f'OVERLAP: {a.cargo_item.display_id} vs {b.cargo_item.display_id}')
                ok = False
print(f'重叠冲突: {"无" if ok else "有!"}')

# 边界检查
print('\n=== 边界检查 ===')
for v in vehicles:
    tl, tw, th = v.template.internal_l, v.template.internal_w, v.template.internal_h
    for p in v.placed_items:
        if p.x+p.placed_l > tl+0.1 or p.y+p.placed_w > tw+0.1:
            print(f'XY越界: {p.cargo_item.display_id}')
            ok = False
        if not v.is_open_top and p.z+p.placed_h > th+0.1:
            print(f'Z越界: {p.cargo_item.display_id}')
            ok = False
print(f'边界违规: {"无" if ok else "有!"}')

print('\n✅ 全部测试通过' if ok else '\n❌ 测试失败')
