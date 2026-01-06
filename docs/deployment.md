# Morado 部署指南

本文档描述如何部署 Morado 测试平台到各种环境。

## 目录

1. [部署概述](#部署概述)
2. [环境要求](#环境要求)
3. [Docker 部署](#docker-部署)
4. [Kubernetes 部署](#kubernetes-部署)
5. [配置说明](#配置说明)
6. [数据库迁移](#数据库迁移)
7. [监控和日志](#监控和日志)
8. [故障排除](#故障排除)

## 部署概述

Morado 支持多种部署方式：

| 方式 | 适用场景 | 复杂度 |
|------|----------|--------|
| Docker Compose | 开发/测试/小规模生产 | 低 |
| Kubernetes | 大规模生产 | 高 |
| 手动部署 | 特殊环境 | 中 |

### 架构组件

```
┌─────────────────────────────────────────────────────────────┐
│                        负载均衡器                            │
│                    (Nginx / Ingress)                        │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │ Frontend │   │ Backend  │   │ Backend  │
    │ (Nginx)  │   │ (Pod 1)  │   │ (Pod 2)  │
    └──────────┘   └────┬─────┘   └────┬─────┘
                        │              │
                        └──────┬───────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
    ┌──────────┐        ┌──────────┐        ┌──────────┐
    │PostgreSQL│        │  Redis   │        │  存储    │
    └──────────┘        └──────────┘        └──────────┘
```

## 环境要求

### 硬件要求

| 组件 | 最低配置 | 推荐配置 |
|------|----------|----------|
| CPU | 2 核 | 4 核+ |
| 内存 | 4 GB | 8 GB+ |
| 磁盘 | 20 GB | 50 GB+ |

### 软件要求

- Docker 24.0+
- Docker Compose 2.20+
- Kubernetes 1.28+ (K8s 部署)
- kubectl 1.28+ (K8s 部署)

## Docker 部署

### 快速启动

```bash
# 克隆项目
git clone https://github.com/your-org/morado.git
cd morado

# 启动生产环境
cd deployment
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 开发环境

```bash
# 启动开发环境
docker-compose -f docker-compose.dev.yml up -d
```

### 服务说明

| 服务 | 端口 | 说明 |
|------|------|------|
| frontend | 80 | Vue.js 前端 (Nginx) |
| backend | 8000 | Python 后端 (Uvicorn) |
| postgres | 5432 | PostgreSQL 数据库 |
| redis | 6379 | Redis 缓存 |

### 构建镜像

```bash
# 构建后端镜像
docker build -f deployment/docker/Dockerfile.backend -t morado-backend:latest .

# 构建前端镜像
docker build -f deployment/docker/Dockerfile.frontend -t morado-frontend:latest .

# 或使用 docker-compose 构建
docker-compose build
```

### 环境变量

后端服务支持以下环境变量：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| APP_ENV | production | 运行环境 |
| DATABASE_URL | - | PostgreSQL 连接字符串 |
| REDIS_URL | - | Redis 连接字符串 |
| LOG_LEVEL | INFO | 日志级别 |
| WORKERS | 4 | Uvicorn worker 数量 |

### 数据持久化

Docker Compose 配置了以下数据卷：

```yaml
volumes:
  postgres-data:    # PostgreSQL 数据
  redis-data:       # Redis 数据
  backend-logs:     # 后端日志
  backend-data:     # 后端数据
```

### 健康检查

所有服务都配置了健康检查：

```bash
# 检查服务健康状态
docker-compose ps

# 手动检查后端健康
curl http://localhost:8000/health

# 手动检查前端健康
curl http://localhost/health
```

### 常用命令

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f backend

# 进入容器
docker-compose exec backend bash

# 重新构建并启动
docker-compose up -d --build

# 清理所有数据
docker-compose down -v
```

## Kubernetes 部署

### 前置条件

1. Kubernetes 集群 (1.28+)
2. kubectl 已配置
3. 镜像仓库访问权限

### 创建命名空间

```bash
kubectl create namespace morado
```

### 部署步骤

```bash
# 1. 部署 PostgreSQL
kubectl apply -f deployment/k8s/postgres-statefulset.yaml

# 2. 部署 Redis
kubectl apply -f deployment/k8s/redis-deployment.yaml

# 3. 部署后端
kubectl apply -f deployment/k8s/backend-deployment.yaml

# 4. 部署前端
kubectl apply -f deployment/k8s/frontend-deployment.yaml

# 5. 部署 Ingress
kubectl apply -f deployment/k8s/ingress.yaml
```

### 或使用 Kustomize

```bash
kubectl apply -k deployment/k8s/
```

### 资源配置

后端 Deployment 资源配置：

```yaml
resources:
  requests:
    cpu: "100m"
    memory: "256Mi"
  limits:
    cpu: "500m"
    memory: "512Mi"
```

### 自动扩缩容

HPA 配置：

```yaml
spec:
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

### 查看部署状态

```bash
# 查看所有资源
kubectl get all -n morado

# 查看 Pod 状态
kubectl get pods -n morado

# 查看 Pod 日志
kubectl logs -f deployment/morado-backend -n morado

# 查看 HPA 状态
kubectl get hpa -n morado

# 描述 Deployment
kubectl describe deployment morado-backend -n morado
```

### Ingress 配置

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: morado-ingress
  namespace: morado
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
    - host: morado.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: morado-frontend
                port:
                  number: 80
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: morado-backend
                port:
                  number: 8000
```

## 配置说明

### 后端配置文件

配置文件位于 `backend/config/` 目录：

```
backend/config/
├── development.toml    # 开发环境
├── production.toml     # 生产环境
├── testing.toml        # 测试环境
└── logging.toml        # 日志配置
```

### 生产环境配置示例

```toml
# backend/config/production.toml

[app]
name = "morado"
version = "0.1.0"
debug = false

[server]
host = "0.0.0.0"
port = 8000
workers = 4

[database]
url = "${DATABASE_URL}"
pool_size = 20
max_overflow = 10
echo = false

[redis]
url = "${REDIS_URL}"

[logging]
level = "INFO"
format = "json"
```

### 前端环境配置

```bash
# frontend/.env.production
VITE_API_BASE_URL=https://api.morado.example.com
VITE_APP_TITLE=Morado 测试平台
```

## 数据库迁移

### 初始化数据库

```bash
# Docker 环境
docker-compose exec backend alembic upgrade head

# Kubernetes 环境
kubectl exec -it deployment/morado-backend -n morado -- alembic upgrade head
```

### 创建新迁移

```bash
# 生成迁移脚本
alembic revision --autogenerate -m "description"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 填充测试数据

```bash
# Docker 环境
docker-compose exec backend python scripts/seed_data.py

# Kubernetes 环境
kubectl exec -it deployment/morado-backend -n morado -- python scripts/seed_data.py
```

## 监控和日志

### 日志收集

后端日志输出为 JSON 格式，便于日志聚合：

```json
{
  "timestamp": "2024-01-01T00:00:00.000Z",
  "level": "INFO",
  "logger": "morado.api",
  "message": "Request processed",
  "request_id": "req-uuid",
  "duration_ms": 45
}
```

### Prometheus 指标

后端暴露 Prometheus 指标端点：

```bash
curl http://localhost:8000/metrics
```

### 健康检查端点

| 端点 | 说明 |
|------|------|
| `/health` | 基本健康检查 |
| `/health/ready` | 就绪检查 |
| `/health/live` | 存活检查 |

### 日志级别

| 级别 | 说明 |
|------|------|
| DEBUG | 调试信息 |
| INFO | 一般信息 |
| WARNING | 警告信息 |
| ERROR | 错误信息 |
| CRITICAL | 严重错误 |

## 故障排除

### 常见问题

#### 1. 数据库连接失败

```bash
# 检查 PostgreSQL 状态
docker-compose ps postgres

# 查看 PostgreSQL 日志
docker-compose logs postgres

# 测试连接
docker-compose exec postgres psql -U morado -d morado -c "SELECT 1"
```

#### 2. Redis 连接失败

```bash
# 检查 Redis 状态
docker-compose ps redis

# 测试连接
docker-compose exec redis redis-cli ping
```

#### 3. 后端启动失败

```bash
# 查看后端日志
docker-compose logs backend

# 检查配置
docker-compose exec backend cat /app/backend/config/production.toml

# 检查环境变量
docker-compose exec backend env | grep -E "(DATABASE|REDIS)"
```

#### 4. 前端无法访问后端

```bash
# 检查网络
docker network ls
docker network inspect morado-network

# 检查后端健康
curl http://localhost:8000/health

# 检查 Nginx 配置
docker-compose exec frontend cat /etc/nginx/nginx.conf
```

### Kubernetes 故障排除

```bash
# 查看 Pod 事件
kubectl describe pod <pod-name> -n morado

# 查看 Pod 日志
kubectl logs <pod-name> -n morado

# 进入 Pod 调试
kubectl exec -it <pod-name> -n morado -- /bin/bash

# 查看服务端点
kubectl get endpoints -n morado

# 测试服务连通性
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://morado-backend:8000/health
```

### 性能调优

#### 后端调优

```toml
# 增加数据库连接池
[database]
pool_size = 30
max_overflow = 20

# 增加 worker 数量
[server]
workers = 8
```

#### PostgreSQL 调优

```sql
-- 查看连接数
SELECT count(*) FROM pg_stat_activity;

-- 查看慢查询
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;
```

#### Redis 调优

```bash
# 查看内存使用
redis-cli INFO memory

# 查看慢日志
redis-cli SLOWLOG GET 10
```

## 备份和恢复

### 数据库备份

```bash
# 备份
docker-compose exec postgres pg_dump -U morado morado > backup.sql

# 恢复
docker-compose exec -T postgres psql -U morado morado < backup.sql
```

### 定时备份

```bash
# 添加 cron 任务
0 2 * * * docker-compose -f /path/to/docker-compose.yml exec -T postgres pg_dump -U morado morado | gzip > /backups/morado_$(date +\%Y\%m\%d).sql.gz
```

## 相关文档

- [架构设计](architecture.md)
- [开发指南](development.md)
- [API 文档](api/)
