# 3D 装箱系统 — 车辆配载与可视化

> 基于 Extreme Point 启发式的 3D Bin Packing 系统，专为物流行业设计。
> 上传货物清单与车型数据，自动计算最优装载方案，生成 3D 交互视图与 2D 工程三视图。

---

## 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [装箱算法与约束](#装箱算法与约束)
- [快速开始（本地运行）](#快速开始本地运行)
- [Docker 部署](#docker-部署)
- [项目结构](#项目结构)
- [技术栈](#技术栈)
- [开发与测试](#开发与测试)

---

## 项目简介

本项目解决物流行业的经典 3D Bin Packing 问题，同时满足以下实际业务需求：

- **多种车型**（箱车、飞翼车、平板车、高栏车）自动匹配
- **货物旋转约束**（固定底面货物仅允许水平旋转，非固定底面支持 6 方向全量旋转）
- **堆叠物理规则**（重不压轻、面积支撑比限制、最大叠放层数）
- **LIFO 卸货顺序**（箱车模式按后进先出排列货物位置）
- **平板/高栏车高度豁免**（无顶盖车型解除 Z 轴高度校验）
- **重量与载重限制**（单车不超最大载重量）

输出直观的 3D 交互装箱图 + 2D 工程三视图（俯视、正视、侧视），并可导出 Excel 明细和 PNG 图片，直接用于现场装车指导。

---

## 功能特性

### 算法核心

| 特性 | 说明 |
|------|------|
| Extreme Point 启发式 | 在每个已放置货物的极点位置尝试新货物，大幅减少搜索空间 |
| 尺寸膨胀缓冲 | 货物长宽高各加 buffer，模拟包装/托盘/防撞间隙，全局变量可调 |
| 重力方向旋转 | 固定底面货物 2 种方向，非固定底面 6 种全量旋转，正方体自动去重 |
| 重不压轻 | 上层货物重量 ≤ 下层货物重量 |
| 面积支撑比 | 上层货物底面积不超过下层支撑面的 4/3 |
| LIFO 装箱 | 箱车模式下，后卸货的放车厢深处，先卸货的放车门侧 |
| 平板车约束解除 | 平板/高栏车无车顶，Z 轴仅受 OPEN_TOP_MAX_HEIGHT 限制 |
| 多车自动扩展 | 一辆车装不下时自动分配后续车辆 |

### 用户界面

- **Excel 模板下载** — 预填示例数据的货物/车型模板，用户只需替换数值
- **文件上传与解析** — 拖拽或点击上传 xlsx 文件，自动校验数据完整性
- **3D 交互视图** — Plotly 渲染，支持拖拽旋转/滚轮缩放/右键平移，每个货物标注编号
- **2D 工程三视图** — Matplotlib 生成的俯视图/正视图/侧视图，可保存为 PNG 图片
- **汇总看板** — 总件数、已装载数、使用车辆数、装载率一目了然
- **明细导出** — 每件货物的放置坐标、尺寸、重量明细表格

---

## 装箱算法与约束

### 算法流程

```
货物数据 → 解析 (按 Quantity 展开, 加 Buffer)
    │
    ▼
按体积降序排列 (大件优先)
    │
    ▼
对每件货物:
    ├─ 遍历已有车辆的每个 Extreme Point
    │     ├─ 校验边界 (X/Y/Z 不超车厢)
    │     ├─ 校验碰撞 (不与已放置货物相交)
    │     ├─ 校验堆叠规则 (重量/面积支撑/层数)
    │     ├─ 校验旋转方向 (固定/非固定)
    │     └─ 得分最低的 EP → 放置
    └─ 若所有车都放不下 → 启用新车 (从模板选取最匹配车型)
    │
    ▼
输出: VehicleInstance[] + 未装载列表
```

### 约束速查

| 约束类型 | 规则 | 代码位置 |
|----------|------|----------|
| Buffer | Fixed_Bottom=是加 0cm，否加 0cm | `BUFFER_FIXED_BOTTOM` / `BUFFER_UNFIXED` |
| 旋转 | 固定底面仅 2 种水平旋转，非固定 6 方向 | `BinPacker.get_orientations()` |
| 重量 | 总毛重 ≤ 车型 Max_Payload | `VehicleInstance.remaining_payload` |
| 堆叠 | 上层重量 ≤ 下层，底面积比 ≤ 4/3 | `_check_stacking()` |
| LIFO | 箱车才启用，后排先装后卸 | `pack()` 中 LIFO 排序分支 |
| 高度豁免 | 平板/高栏车 Z 轴上限为 `OPEN_TOP_MAX_HEIGHT` | `_check_bounds()` + `is_open_top` |

---

## 快速开始（本地运行）

### 前置条件

- Python 3.9+
- pip

### 安装与运行

```bash
# 1. 进入项目目录
cd ongoing/

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动 Streamlit 应用
streamlit run app.py
```

浏览器打开 `http://localhost:8501`，默认无需密码（如配置了 `APP_PASSWORD` 环境变量则需输入密码）。

### 使用示例

项目附带测试数据：

```bash
# 使用 测试/ 目录下的示例 Excel 文件
# 打开浏览器后，在左侧控制面板上传：
#   - 货物: 测试/货物用例1.xlsx
#   - 车型: 测试/车辆用例1.xlsx
# 点击「开始装箱计算」
```

---

## Docker 部署

> 适用于生产环境部署。使用 Nginx 反向代理 + Let's Encrypt SSL。

### 架构概览

```
浏览器 HTTPS (443)
    │
    ▼
┌──────────────────────────────┐
│  Nginx (pack3d-nginx)        │  ← 443/80 暴露到宿主机
│  - SSL 终端                  │
│  - 反向代理 → app:8501       │
│  - WebSocket 支持            │
└──────────┬───────────────────┘
           │ internal:8501
           ▼
┌──────────────────────────────┐
│  Streamlit (pack3d-app)      │  ← 仅内部网络，不暴露端口
│  - 3D 装箱算法               │
│  - Plotly / Matplotlib 可视化 │
└──────────────────────────────┘
```

### 前置条件

- **VPS**: Ubuntu 20.04+ / Debian 11+（推荐 Ubuntu 22.04），1 核 / 1 GB 内存 / 10 GB 磁盘
- **Docker**: 24+，Docker Compose v2+
- **域名**: `box.fang-hui.top` 的 A 记录指向 VPS IP

### 部署步骤

#### 1. 安装 Docker

```bash
curl -fsSL https://get.docker.com | sudo bash
sudo usermod -aG docker $USER
exit  # 重新登录使权限生效
```

验证：

```bash
docker --version          # Docker version 24+
docker compose version    # Docker Compose version v2+
```

#### 2. DNS 解析

在域名 DNS 管理后台添加 A 记录：

| 类型 | 主机记录 | 记录值 | TTL |
|------|----------|--------|-----|
| A | box | `你的VPS的IP` | 600 |

验证：

```bash
nslookup box.fang-hui.top
```

#### 3. 上传项目文件

```bash
# 在本地 Mac 上执行
scp -r ongoing/ user@你的VPS的IP:/home/user/pack3d/

# 后续在 VPS 上操作
ssh user@你的VPS的IP
cd ~/pack3d/ongoing/
```

#### 4. 修改密码

编辑 `docker-compose.yml`，将 `APP_PASSWORD` 改为你的实际密码：

```bash
nano docker-compose.yml
# 修改: - APP_PASSWORD=你的密码
```

#### 5. 获取 SSL 证书

```bash
# 安装 certbot
sudo apt update && sudo apt install -y certbot

# 确保 80 端口空闲
sudo lsof -i :80

# 申请证书
sudo certbot certonly --standalone -d box.fang-hui.top
```

证书文件路径：`/etc/letsencrypt/live/box.fang-hui.top/fullchain.pem`

#### 6. 构建并启动

```bash
cd ~/pack3d/ongoing/
docker compose up -d --build
```

首次构建约 2-5 分钟。查看状态：

```bash
docker compose ps
```

期望输出：

```
NAME            STATUS                    PORTS
pack3d-app      Up (healthy)             8501/tcp
pack3d-nginx    Up                       0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
```

#### 7. 验证部署

浏览器访问 **https://box.fang-hui.top**，应看到系统登录页面。

健康检查：

```bash
curl -f http://localhost:8501/_stcore/health
curl -f -L http://localhost/
```

#### 8. SSL 证书自动续期

```bash
sudo crontab -e
# 添加（每天凌晨 3 点续期）：
0 3 * * * docker stop pack3d-nginx && certbot renew --quiet && docker start pack3d-nginx
```

### 运维命令速查

```bash
docker compose up -d          # 启动
docker compose down           # 停止
docker compose restart        # 重启
docker logs -f pack3d-app     # 应用日志
docker logs -f pack3d-nginx   # Nginx 日志
docker compose up -d --build  # 更新（重新构建）
docker exec -it pack3d-app bash  # 进入容器
```

### 故障排查

| 问题 | 原因 | 解决方法 |
|------|------|----------|
| nginx "cannot load certificate" | SSL 证书未申请 | 确认第五步已完成 |
| certbot "binding to port 80" | 端口被占用 | `sudo lsof -i :80` 停掉占用进程 |
| WebSocket 连接失败 | nginx 代理配置缺失 | 确认 nginx.conf 含 `proxy_set_header Upgrade` 和 `Connection "upgrade"` |
| 上传 Excel 提示过大 | 上传大小限制 | 检查 `client_max_body_size` 和 `STREAMLIT_SERVER_MAX_UPLOAD_SIZE` |
| 图表中文方块 | 中文字体未安装 | Dockerfile 已含 `fonts-wqy-microhei`，重新构建 |

### 自定义端口

编辑 `docker-compose.yml`：

```yaml
nginx:
  ports:
    - "8080:80"
    - "8443:443"
```

> ⚠️ 修改端口后，certbot standalone 续期会失败。建议使用 DNS 挑战模式，或在续期 cron 中先停止 nginx。

---

## 项目结构

```
ongoing/
├── app.py                 # Streamlit 主程序 + 3D 装箱算法（约 1100 行）
├── requirements.txt       # Python 依赖
├── Dockerfile             # 应用镜像构建
├── docker-compose.yml     # 容器编排（app + nginx）
├── nginx.conf             # Nginx 反向代理 + SSL 配置
├── 3D装箱系统需求.md       # 原始需求文档
├── README.md              # 本文件
├── test_algo.py           # 算法单元测试（运行: python test_algo.py）
├── test_optimize.py       # 优化测试
├── test_stack.py          # 堆叠规则测试
└── 测试/
    ├── 货物用例1.xlsx       # 示例货物数据
    └── 车辆用例1.xlsx       # 示例车型数据
```

---

## 技术栈

| 层次 | 技术 |
|------|------|
| 算法 | Python, Extreme Point 启发式 |
| Web 框架 | Streamlit |
| 3D 可视化 | Plotly |
| 2D 可视化 | Matplotlib |
| 数据处理 | Pandas, NumPy |
| Excel 读写 | Openpyxl |
| 部署 | Docker, Docker Compose, Nginx, Let's Encrypt |

---

## 开发与测试

```bash
# 运行算法单元测试
cd ongoing/
python test_algo.py

# 运行优化测试
python test_optimize.py

# 运行堆叠测试
python test_stack.py

# 手动启动应用
streamlit run app.py --server.port=8501
```

测试数据位于 `测试/` 目录，包含一个完整用例的货物清单和车型清单。

---

## License

本项目代码仅供学习和内部使用。
