#!/bin/bash
# 数据库配置和seed脚本使用示例

echo "=========================================="
echo "数据库配置和Seed脚本使用示例"
echo "=========================================="
echo ""

# 示例1: 使用默认配置（开发环境）
echo "示例1: 使用开发环境配置文件"
echo "命令: uv run python scripts/database/seed_four_layer_data.py --env development"
echo ""

# 示例2: 使用测试环境
echo "示例2: 使用测试环境配置文件"
echo "命令: uv run python scripts/database/seed_four_layer_data.py --env testing"
echo ""

# 示例3: 使用环境变量覆盖
echo "示例3: 使用环境变量覆盖配置"
echo "命令: DATABASE_URL='postgresql://user:pass@host:5432/db' \\"
echo "       uv run python scripts/database/seed_four_layer_data.py"
echo ""

# 示例4: 完整的数据库设置流程
echo "示例4: 完整的数据库设置流程"
echo "----------------------------------------"
echo "# 1. 创建数据库和用户"
echo "psql -U postgres << EOF"
echo "CREATE USER morado WITH PASSWORD 'morado';"
echo "CREATE DATABASE morado_dev OWNER morado;"
echo "GRANT ALL PRIVILEGES ON DATABASE morado_dev TO morado;"
echo "EOF"
echo ""
echo "# 2. 运行数据库迁移"
echo "cd backend"
echo "uv run alembic upgrade head"
echo ""
echo "# 3. 填充测试数据"
echo "uv run python scripts/database/seed_four_layer_data.py --env development"
echo ""

# 示例5: Docker环境
echo "示例5: 在Docker环境中使用"
echo "----------------------------------------"
echo "docker-compose exec backend bash -c \\"
echo "  'uv run python scripts/database/seed_four_layer_data.py --env development'"
echo ""

# 示例6: 查看帮助
echo "示例6: 查看命令帮助"
echo "命令: uv run python scripts/database/seed_four_layer_data.py --help"
echo ""

echo "=========================================="
echo "更多信息请查看:"
echo "  - README.md - 完整文档"
echo "  - QUICK_SETUP.md - 快速配置指南"
echo "  - DATABASE_CONFIG_SUMMARY.md - 配置总结"
echo "=========================================="
