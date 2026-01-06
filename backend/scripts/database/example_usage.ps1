# 数据库配置和seed脚本使用示例 (PowerShell)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "数据库配置和Seed脚本使用示例" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 示例1: 使用默认配置（开发环境）
Write-Host "示例1: 使用开发环境配置文件" -ForegroundColor Yellow
Write-Host "命令: uv run python scripts/database/seed_four_layer_data.py --env development" -ForegroundColor Green
Write-Host ""

# 示例2: 使用测试环境
Write-Host "示例2: 使用测试环境配置文件" -ForegroundColor Yellow
Write-Host "命令: uv run python scripts/database/seed_four_layer_data.py --env testing" -ForegroundColor Green
Write-Host ""

# 示例3: 使用环境变量覆盖
Write-Host "示例3: 使用环境变量覆盖配置" -ForegroundColor Yellow
Write-Host "`$env:DATABASE_URL='postgresql://user:pass@host:5432/db'" -ForegroundColor Green
Write-Host "uv run python scripts/database/seed_four_layer_data.py" -ForegroundColor Green
Write-Host ""

# 示例4: 完整的数据库设置流程
Write-Host "示例4: 完整的数据库设置流程" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
Write-Host "# 1. 创建数据库和用户 (使用 psql)" -ForegroundColor White
Write-Host "psql -U postgres -c `"CREATE USER morado WITH PASSWORD 'morado';`"" -ForegroundColor Green
Write-Host "psql -U postgres -c `"CREATE DATABASE morado_dev OWNER morado;`"" -ForegroundColor Green
Write-Host "psql -U postgres -c `"GRANT ALL PRIVILEGES ON DATABASE morado_dev TO morado;`"" -ForegroundColor Green
Write-Host ""
Write-Host "# 2. 运行数据库迁移" -ForegroundColor White
Write-Host "cd backend" -ForegroundColor Green
Write-Host "uv run alembic upgrade head" -ForegroundColor Green
Write-Host ""
Write-Host "# 3. 填充测试数据" -ForegroundColor White
Write-Host "uv run python scripts/database/seed_four_layer_data.py --env development" -ForegroundColor Green
Write-Host ""

# 示例5: 临时设置环境变量
Write-Host "示例5: 临时设置环境变量（当前会话）" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
Write-Host "`$env:DATABASE_URL = 'postgresql://morado:morado@localhost:5432/morado_dev'" -ForegroundColor Green
Write-Host "uv run python scripts/database/seed_four_layer_data.py" -ForegroundColor Green
Write-Host ""

# 示例6: 永久设置环境变量
Write-Host "示例6: 永久设置环境变量（当前用户）" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
Write-Host "[System.Environment]::SetEnvironmentVariable(" -ForegroundColor Green
Write-Host "    'DATABASE_URL'," -ForegroundColor Green
Write-Host "    'postgresql://morado:morado@localhost:5432/morado_dev'," -ForegroundColor Green
Write-Host "    'User'" -ForegroundColor Green
Write-Host ")" -ForegroundColor Green
Write-Host ""

# 示例7: 查看帮助
Write-Host "示例7: 查看命令帮助" -ForegroundColor Yellow
Write-Host "命令: uv run python scripts/database/seed_four_layer_data.py --help" -ForegroundColor Green
Write-Host ""

# 示例8: 验证配置
Write-Host "示例8: 验证当前数据库配置" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
Write-Host "# 查看配置文件" -ForegroundColor White
Write-Host "Get-Content backend/config/development.toml | Select-String 'database_url'" -ForegroundColor Green
Write-Host ""
Write-Host "# 查看环境变量" -ForegroundColor White
Write-Host "`$env:DATABASE_URL" -ForegroundColor Green
Write-Host ""

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "更多信息请查看:" -ForegroundColor Cyan
Write-Host "  - README.md - 完整文档" -ForegroundColor White
Write-Host "  - QUICK_SETUP.md - 快速配置指南" -ForegroundColor White
Write-Host "  - DATABASE_CONFIG_SUMMARY.md - 配置总结" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 提供交互式选项
Write-Host "是否要查看实际的配置文件内容? (Y/N)" -ForegroundColor Yellow
$response = Read-Host

if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host ""
    Write-Host "开发环境配置 (development.toml):" -ForegroundColor Cyan
    Write-Host "----------------------------------------" -ForegroundColor Gray
    if (Test-Path "backend/config/development.toml") {
        Get-Content "backend/config/development.toml" | Select-String -Pattern "database" -Context 0,2
    } else {
        Write-Host "配置文件不存在: backend/config/development.toml" -ForegroundColor Red
    }
    Write-Host ""
}
