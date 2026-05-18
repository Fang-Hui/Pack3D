# 3D 装箱系统 — Docker 部署指南

> 域名: **box.fang-hui.top**  
> SSL: Let's Encrypt (certbot 自动管理)  
> 架构: Nginx (HTTPS) → Streamlit (8501 内部端口)

---

## 架构概览

```
浏览器 HTTPS (443)
    │
    ▼
┌──────────────────────────────┐
│  Nginx (pack3d-nginx)        │  ← 443/80 暴露到宿主机
│  - SSL 终端                  │
│  - 反向代理 → app:8501       │
│  - certbot ACME 验证         │
└──────────┬───────────────────┘
           │ internal:8501
           ▼
┌──────────────────────────────┐
│  Streamlit (pack3d-app)      │  ← 仅内部网络，不暴露端口
│  - 3D 装箱算法               │
│  - Plotly / Matplotlib 可视化 │
└──────────────────────────────┘
```

---

## 第一步：前期准备

### 1.1 VPS 最低配置

- **OS**: Ubuntu 20.04+ / Debian 11+ / CentOS 7+（推荐 Ubuntu 22.04）
- **CPU**: 1 核+
- **内存**: 1 GB+（matplotlib 渲染图表需要内存）
- **磁盘**: 10 GB+

### 1.2 安装 Docker

```bash
# 官方一键安装脚本
curl -fsSL https://get.docker.com | sudo bash

# 将当前用户加入 docker 组（免 sudo）
sudo usermod -aG docker $USER

# 重新登录使权限生效
exit
```

重新 SSH 登录后验证：

```bash
docker --version          # Docker version 24+
docker compose version    # Docker Compose version v2+
```

### 1.3 DNS 解析

在域名 DNS 管理后台添加 A 记录：

| 类型 | 主机记录 | 记录值       | TTL  |
| ---- | -------- | ------------ | ---- |
| A    | box      | `你的VPS的IP` | 600  |

验证 DNS 生效：

```bash
# 在本地执行，等 1-5 分钟后应返回你的 VPS IP
nslookup box.fang-hui.top
```

---

## 第二步：上传项目文件

将 `ongoing/` 目录下所有文件上传到 VPS：

```bash
# 在本地 Mac 上执行
scp -r ongoing/ user@你的VPS的IP:/home/user/pack3d/

# 后续步骤全部在 VPS 上操作
ssh user@你的VPS的IP
cd ~/pack3d/ongoing/
```

确认文件齐全：

```bash
ls -la
# Dockerfile  docker-compose.yml  nginx.conf  app.py  requirements.txt  README.md
```

---

## 第三步：修改密码

编辑 `docker-compose.yml`，修改 `APP_PASSWORD` 为你的实际密码：

```bash
nano docker-compose.yml
```

找到这一行：

```yaml
- APP_PASSWORD=ChangeMe123    # ⚠️ 部署前改成你的实际密码
```

改为：

```yaml
- APP_PASSWORD=MySecureP@ss   # 你的密码
```

---

## 第四步：获取 SSL 证书

在**启动 Docker Compose 之前**，先用 certbot standalone 模式获取证书（需要 80 端口空闲）。

### 4.1 安装 certbot

```bash
# Ubuntu / Debian
sudo apt update && sudo apt install -y certbot

# CentOS 7
# sudo yum install -y epel-release && sudo yum install -y certbot
```

### 4.2 确保 80 端口空闲

```bash
# 检查是否有进程占用 80 端口
sudo lsof -i :80

# 如果有输出（如系统自带的 nginx/apache），先停掉
# sudo systemctl stop nginx
# sudo systemctl stop apache2
```

### 4.3 申请证书

```bash
sudo certbot certonly --standalone -d box.fang-hui.top
```

按提示输入邮箱（用于证书到期提醒），同意服务条款即可。

成功后输出示例：

```
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/box.fang-hui.top/fullchain.pem
```

### 4.4 验证证书路径

```bash
sudo ls -l /etc/letsencrypt/live/box.fang-hui.top/
# 应看到: fullchain.pem  privkey.pem  cert.pem  chain.pem  README
```

---

## 第五步：构建并启动

```bash
cd ~/pack3d/ongoing/

# 构建镜像 + 启动所有容器
docker compose up -d --build
```

首次构建约 2-5 分钟（需要下载 Python 镜像、中文字体、pip 依赖）。

### 查看状态

```bash
docker compose ps
```

期望输出：

```
NAME            STATUS                    PORTS
pack3d-app      Up (healthy)             8501/tcp
pack3d-nginx    Up                       0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
```

### 查看日志

```bash
# 应用日志
docker logs -f pack3d-app

# Nginx 日志
docker logs -f pack3d-nginx
```

---

## 第六步：验证部署

在浏览器访问：

- **https://box.fang-hui.top** — 应看到 Streamlit 3D 装箱系统界面，地址栏显示 🔒 锁
- **http://box.fang-hui.top** — 应自动 301 跳转到 https

### 健康检查

```bash
# 应用内部健康检查
curl -f http://localhost:8501/_stcore/health

# 通过 nginx 访问
curl -f -L http://localhost/
```

---

## 第七步：SSL 证书自动续期

Let's Encrypt 证书有效期 90 天。配置 cron 自动续期。

### 7.1 添加续期定时任务

```bash
sudo crontab -e
```

添加以下行（每天凌晨 3:00 检查，续期时短暂停止 nginx）：

```
0 3 * * * docker stop pack3d-nginx && certbot renew --quiet && docker start pack3d-nginx
```

### 7.2 手动测试续期

```bash
# 模拟续期（不会真正续期，仅测试流程）
sudo certbot renew --dry-run
```

---

## 常用运维命令

```bash
# ========== 启动 / 停止 ==========
docker compose up -d          # 启动
docker compose down           # 停止并删除容器
docker compose restart        # 重启

# ========== 查看日志 ==========
docker logs -f pack3d-app     # 应用实时日志
docker logs --tail 50 pack3d-nginx  # Nginx 最近 50 行

# ========== 更新应用 ==========
docker compose down
git pull   # 或用 scp 上传新版本
docker compose up -d --build  # 重新构建

# ========== 进入容器调试 ==========
docker exec -it pack3d-app bash
docker exec -it pack3d-nginx sh

# ========== 检查证书有效期 ==========
sudo certbot certificates
```

---

## 自定义端口（可选）

如果你不想使用标准 80/443 端口，编辑 `docker-compose.yml`：

```yaml
nginx:
  ports:
    - "8080:80"      # HTTP 改为 8080
    - "8443:443"     # HTTPS 改为 8443
```

然后访问 `https://box.fang-hui.top:8443`。

> **⚠️ 注意**: 修改端口后，certbot standalone 续期会失败（因为宿主机 80 端口不再有 nginx 监听）。你需要：
> 1. 改用 certbot DNS 挑战模式（推荐，但需要 DNS API 凭证）
> 2. 或者在续期 cron 中先 `docker stop pack3d-nginx`，再运行 certbot（certbot standalone 会临时绑定 80 端口）

---

## 故障排查

### 问题 1: 容器启动后 nginx 报错 "cannot load certificate"

**原因**: SSL 证书尚未申请或路径不对。

**解决**: 确认第四步已完成，且证书文件存在：

```bash
sudo cat /etc/letsencrypt/live/box.fang-hui.top/fullchain.pem
```

### 问题 2: certbot standalone 报错 "Problem binding to port 80"

**原因**: 80 端口被占用。

**解决**:

```bash
sudo lsof -i :80           # 查看谁占用了 80
sudo systemctl stop nginx  # 示例：停掉系统 nginx
```

### 问题 3: 页面加载但 WebSocket 连接失败

**原因**: nginx WebSocket 代理配置丢失。

**解决**: 确认 `nginx.conf` 中包含：

```nginx
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

### 问题 4: 上传 Excel 提示文件过大

**原因**: 上传大小限制。

**解决**: 检查 `nginx.conf` 的 `client_max_body_size`（当前 50M），以及 docker-compose.yml 的 `STREAMLIT_SERVER_MAX_UPLOAD_SIZE`。

### 问题 5: 图表中文显示为方块

**原因**: 中文字体未安装。

**解决**: Dockerfile 中已安装 `fonts-wqy-microhei`，确认构建时没有报错：

```bash
docker compose build --no-cache app
```

---

## 文件清单

| 文件                | 用途                          |
| ------------------- | ----------------------------- |
| `app.py`            | Streamlit 主程序 + 3D 装箱算法 |
| `Dockerfile`        | 应用镜像构建（含中文字体）     |
| `docker-compose.yml`| 容器编排（app + nginx）        |
| `nginx.conf`        | Nginx 反向代理 + SSL          |
| `requirements.txt`  | Python 依赖                   |
| `test_*.py`         | 算法单元测试（本地运行）       |

---

## 安全建议

1. **防火墙**: 仅开放 80/443 端口（以及 22 SSH）
   ```bash
   sudo ufw allow 22
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```

2. **密码**: 设置强密码（`docker-compose.yml` 中 `APP_PASSWORD`）

3. **定期更新**: 保持 Docker 镜像和系统更新
   ```bash
   sudo apt update && sudo apt upgrade -y
   docker compose pull    # 检查基础镜像更新
   ```
