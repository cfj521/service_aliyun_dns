# 阿里云DNS自动更新脚本

这是一个用于自动更新阿里云DNS记录的Python脚本。当你的公网IP发生变化时，脚本会自动更新指定的DNS记录。

## 功能特点

- 自动检测公网IP变化
- 支持多个子域名同时更新
- 详细的日志记录
- 使用环境变量配置，安全可靠

## 安装步骤

1. 克隆项目到本地
2. 项目运行环境管理，需要安装好pyenv，poetry
3. 创建并配置好虚拟环境：
   ```bash
   poetry install --no-dev

## 配置

1. 复制 `.env.example` 文件为 `.env`：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填写以下信息：
- `ALIYUN_ACCESS_KEY_ID`: 阿里云访问密钥ID
- `ALIYUN_ACCESS_KEY_SECRET`: 阿里云访问密钥密码
- `ALIYUN_REGION_ID`: 阿里云区域ID（默认为cn-hangzhou）
- `DOMAIN_NAME`: 你的主域名
- `SUBDOMAINS`: 需要更新的子域名列表，用逗号分隔

## 使用方法

直接运行脚本：
```bash
python3 update_dns.py
```

```powershell
python update_dns.py
```

## 设置定时任务

### Linux/Mac (使用 crontab)
```bash
0 * * * * cd ~/service_aliyun_dns && poetry run python3 update_dns.py >> /var/log/dns_update.log 2>&1
```

### Windows (使用 PowerShell)
```powershell
# 创建定时任务
$Action = New-ScheduledTaskAction -Execute "poetry" -Argument "run python update_dns.py" -WorkingDirectory "D:\api\service_aliyun_dns"
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration ([TimeSpan]::MaxValue)
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd -RestartInterval (New-TimeSpan -Minutes 1) -RestartCount 3
Register-ScheduledTask -TaskName "AliyunDNSUpdater" -Action $Action -Trigger $Trigger -Settings $Settings -Description "每小时更新阿里云DNS记录" -Force

# 如果需要删除任务
# Unregister-ScheduledTask -TaskName "AliyunDNSUpdater" -Confirm:$false
```

## 注意事项

1. 确保你的阿里云账号有足够的权限管理DNS记录
2. 建议使用RAM子账号，并只授予DNS管理权限
3. 保护好你的 `.env` 文件，不要将其提交到版本控制系统
4. 定期轮换阿里云 AccessKey，提高安全性

## 日志

脚本会输出详细的日志信息，包括：
- IP地址变化情况
- DNS记录更新状态
- 错误信息（如果有） 