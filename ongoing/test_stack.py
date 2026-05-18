"""堆叠规则专项测试"""
import sys; sys.path.insert(0, '/Users/iric/PyCharmMiscProject/进仓单')
from ongoing.app import *

# 测试: 重物在下(H) + 轻物在上(L) → 应堆叠
# 反例: 轻物在下 + 重物在上 → 不应堆叠
items = [
    CargoItem('H',200,150,50,201.5,151.5,51.5, 500, False, '箱车', 1, 3, 0),
    CargoItem('L',100,80,40,101.5,81.5,41.5, 300, False, '箱车', 2, 3, 0),
]
tpl = [VehicleTemplate('箱车', 960, 245, 270, 5000)]
v, u = BinPacker().pack(items, tpl)
print('车辆数:', len(v), '未装载:', len(u))
for vi in v:
    for p in vi.placed_items:
        print(f'  {p.cargo_item.display_id} {p.cargo_item.weight}kg @ ({p.x:.0f},{p.y:.0f},{p.z:.0f}) size({p.placed_l:.0f},{p.placed_w:.0f},{p.placed_h:.0f})')
    # 检查堆叠
    for a in vi.placed_items:
        for b in vi.placed_items:
            if a is b: continue
            if abs(b.z - a.z2) < 0.2:  # b坐在a上面
                ok_w = b.cargo_item.weight <= a.cargo_item.weight
                ok_a = b.cargo_item.base_area <= a.cargo_item.base_area * 4/3
                print(f'  堆叠: {b.cargo_item.display_id}({b.cargo_item.weight}kg) on {a.cargo_item.display_id}({a.cargo_item.weight}kg) → 重量OK={ok_w} 面积OK={ok_a}')

# 测试2: 重物在上(应该被禁止)
print()
print('--- 测试反向堆叠(应禁止) ---')
items2 = [
    CargoItem('L',100,80,40,101.5,81.5,41.5, 300, False, '箱车', 1, 3, 0),  # 轻物uo=1
    CargoItem('H',200,150,50,201.5,151.5,51.5, 500, False, '箱车', 2, 3, 0),  # 重物uo=2
]
v2, u2 = BinPacker().pack(items2, tpl)
print('车辆数:', len(v2), '未装载:', len(u2))
for vi in v2:
    for p in vi.placed_items:
        print(f'  {p.cargo_item.display_id} {p.cargo_item.weight}kg @ ({p.x:.0f},{p.y:.0f},{p.z:.0f}) z2={p.z2:.0f}')
print('预期: H(重物)不应压在L(轻物)上面')
