# 📜 项目脚本目录

这个目录包含了所有用于启动、停止和管理FamilyBot项目的shell脚本。

## 🚀 启动脚本

| 脚本名称 | 功能描述 | 推荐使用场景 |
|---------|----------|-------------|
| `start-all.sh` | 启动所有服务（后端+AI Agent+前端） | **生产环境/演示** |
| `start-dev.sh` | 开发模式启动（后端后台+前端前台） | **日常开发** |
| `start-integrated.sh` | 集成模式启动（单端口统一服务） | **简化部署** |
| `start-single-port.sh` | 单端口模式启动 | **特殊网络环境** |
| `start.sh` | 基础启动脚本 | **自定义启动** |

## 🛑 停止脚本

| 脚本名称 | 功能描述 |
|---------|----------|
| `stop-all.sh` | 停止所有服务和进程 |
| `stop-integrated.sh` | 停止集成模式服务 |
| `stop-single-port.sh` | 停止单端口模式服务 |
| `stop.sh` | 基础停止脚本 |

## 📊 状态检查脚本

| 脚本名称 | 功能描述 |
|---------|----------|
| `status.sh` | 检查所有服务运行状态 |
| `status-integrated.sh` | 检查集成模式服务状态 |

## 💡 使用方法

```bash
# 进入脚本目录
cd /Users/jllulu/Desktop/familybot/scripts

# 启动所有服务
./start-all.sh

# 检查服务状态
./status.sh

# 停止所有服务
./stop-all.sh
```

## ⚠️ 注意事项

- 确保脚本有执行权限：`chmod +x *.sh`
- 运行前确保在项目根目录或scripts目录
- 某些脚本可能需要特定的环境配置
