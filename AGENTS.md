# AGENTS.md

本文件为本仓库内 AI 编码代理提供最小可执行指引，帮助快速理解并安全修改项目。

## 1. 项目定位与边界

- 这是一个面向 OpenList/AList v3+ 的自动化同步工具，后端 Python Tornado，前端 Vue2，存储为 SQLite。
- 本项目不内置 OpenList/AList，开发与联调默认依赖外部可访问的 OpenList/AList 服务。
- 产品与运维背景、功能说明优先阅读 [README.md](README.md)。

## 2. 代码结构与职责

- 后端入口: [main.py](main.py)。
- Web 控制层: [controller/](controller/)。
- 业务层: [service/](service/)。
- 数据访问层: [mapper/](mapper/)。
- 公共能力与配置/数据库初始化: [common/](common/)。
- 前端工程: [frontend/](frontend/)（页面在 [frontend/src/views/](frontend/src/views/)）。

修改建议:
- 接口行为变更优先落在 controller + service，避免把业务逻辑塞进 handler。
- 数据结构/SQL 变更需要同时检查初始化和迁移逻辑（见第 6 节）。

## 3. 常用开发命令

后端:
- 安装依赖: pip install -r requirements.txt
- 本地启动: python main.py

前端:
- 安装依赖并开发: cd frontend && npm install && npm run dev
- 构建: cd frontend && npm install && npm run build

打包与容器:
- PyInstaller: pyinstaller taoSync.spec
- Docker: docker build -t dr34m/tao-sync:latest .

补充说明:
- 本仓库当前无标准自动化测试命令；改动后至少进行手工冒烟验证（登录、引擎管理、作业创建/执行、通知配置）。

## 4. 启动与运行关键事实

- 启动会执行 [service/system/onStart.py](service/system/onStart.py): 创建 data 目录、初始化日志、初始化数据库、恢复并启动任务。
- 配置优先级: data/config.ini > 环境变量 > 默认值（实现见 [common/config.py](common/config.py)）。
- 首次启动会生成 admin 随机密码并写日志；若涉及登录问题，先查 data/log 下系统日志。
- 默认端口为 8023；容器运行时同样使用该端口映射。

## 5. 前后端协作约定

- 后端无需鉴权接口以 /svr/noAuth 开头（见 [main.py](main.py) 路由定义）。
- 前端 API 按业务拆分在 [frontend/src/api/](frontend/src/api/)，请求公共处理在 [frontend/src/utils/request.js](frontend/src/utils/request.js)。
- 涉及任务状态展示时，需同步核对后端状态语义与前端状态映射，避免仅改一侧。

## 6. 数据库与迁移注意事项

- SQLite 文件默认位于 data/taoSync.db。
- 初始化与版本迁移由 [common/sqlInit.py](common/sqlInit.py) 管理。
- 新增表/字段时:
  1) 更新初始化 SQL；
  2) 更新版本迁移分支；
  3) 验证老库升级路径与新装路径均可用。

## 7. 打包与 CI 约定

- PyInstaller 依赖前端构建产物 frontend/dist，定义见 [taoSync.spec](taoSync.spec)。
- CI 在 [version.txt](version.txt) 变更时触发构建，流程见 [.github/workflows/build.yml](.github/workflows/build.yml)。
- CI 会将版本号注入前端设置页占位符后再构建前端；不要跳过该步骤。

## 8. 文档链接（优先引用，不在此重复）

- 项目总览与部署: [README.md](README.md)
- 后端打包与镜像命令: [doc/后端.md](doc/%E5%90%8E%E7%AB%AF.md)
- 配置示例: [doc/config.ini](doc/config.ini)
- 前端说明: [frontend/README.md](frontend/README.md)
- 版本变更记录: [doc/changelog/](doc/changelog/)

## 9. 代理工作建议

- 优先做最小变更，避免无关重构。
- 修改配置、任务调度、数据库相关代码后，必须补充验证步骤到变更说明。
- 如需新增协作规范:
  - 全局约束写入 AGENTS.md；
  - 仅某类文件生效的约束放到 .github/instructions/*.instructions.md。
