<div align="center">

  ![Software Guard](https://img.shields.io/badge/Software_Guard-v1.0-blue)
  ![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
  ![Vue 3](https://img.shields.io/badge/Vue-3.3-brightgreen)
  ![License](https://img.shields.io/badge/License-MIT-yellow)

  # 🛡️ Software Guard

  **企业级软件分发管理平台**

  安全、高效的内部软件下载站，提供软件版本管理、漏洞追踪、下载统计和权限控制

  [功能特性](#-功能特性) • [快速开始](#-快速开始) • [技术架构](#-技术架构) • [API 文档](#-api-文档)

</div>

---

## 📋 项目简介

Software Guard 是一个功能完善的企业内部软件分发管理系统，旨在解决组织内部的软件分发、版本管理和安全漏洞追踪问题。系统采用现代化的前后端分离架构，提供直观的用户界面和强大的管理功能。

### 🎯 核心价值

- **安全可控** - 基于 JWT 的身份认证和细粒度的权限控制
- **漏洞追踪** - 及时发现和通知软件安全漏洞
- **审计合规** - 完整的操作日志和下载记录
- **用户友好** - 简洁直观的界面设计

---

## ✨ 功能特性

### 👤 用户功能

| 功能 | 描述 |
|------|------|
| 📦 软件浏览 | 支持分类浏览和关键词搜索 |
| ⬇️ 安全下载 | 下载行为记录，支持断点续传 |
| 📝 软件申请 | 一键申请未收录软件 |
| 📊 下载历史 | 查看个人下载记录 |

### 👨‍💻 运维管理

| 功能 | 描述 |
|------|------|
| 🚀 软件管理 | 添加、编辑软件及版本上传 |
| ✅ 申请审核 | 软件申请审批工作流 |
| 🛡️ 漏洞管理 | 漏洞信息录入与通知 |
| 📈 数据统计 | 下载量统计与趋势分析 |
| 👥 用户管理 | 用户权限与账号管理 |

### 🔒 安全特性

- 🔐 **JWT 认证** - 无状态身份验证
- 🎭 **RBAC 权限** - 用户/运维/管理员三角色
- ⚠️ **漏洞提醒** - 下载前安全检查
- 📝 **审计日志** - 完整操作追溯
- 🚦 **访问控制** - 接口级权限校验

---

## 🏗️ 技术架构

### 后端技术栈

<div align="center">

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   FastAPI   │────▶│  SQLAlchemy │────▶│  PostgreSQL │
│  Web 框架   │     │     ORM     │     │    数据库    │
└─────────────┘     └─────────────┘     └─────────────┘
       │                                      │
       ▼                                      ▼
┌─────────────┐                       ┌─────────────┐
│    JWT      │                       │   storage/  │
│  身份认证   │                       │  文件存储   │
└─────────────┘                       └─────────────┘
```

</div>

- **FastAPI** - 高性能异步 Web 框架，自动生成 OpenAPI 文档
- **SQLAlchemy** - Python SQL 工具包和 ORM
- **PostgreSQL** - 可靠的关系型数据库
- **Pydantic** - 数据验证和设置管理
- **uv** - 极速 Python 包管理器

### 前端技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **Ant Design Vue** - 企业级 UI 组件库
- **Vite** - 下一代前端构建工具
- **Pinia** - Vue 3 状态管理库
- **Axios** - HTTP 客户端
- **pnpm** - 快速的磁盘空间节约包管理器

---

## 📁 项目结构

```
software_guard/
├── 📂 backend/                    # 后端服务
│   ├── 📂 app/
│   │   ├── 📂 api/                # API 路由处理器
│   │   │   ├── auth.py            # 认证接口
│   │   │   ├── software.py        # 软件管理
│   │   │   ├── request.py         # 申请流程
│   │   │   ├── download.py        # 下载统计
│   │   │   └── vulnerability.py   # 漏洞管理
│   │   ├── 📂 core/               # 核心配置
│   │   │   ├── config.py          # 环境配置
│   │   │   ├── database.py        # 数据库连接
│   │   │   ├── security.py        # JWT/加密
│   │   │   └── deps.py            # 依赖注入
│   │   ├── 📂 models/             # SQLAlchemy 模型
│   │   ├── 📂 schemas/            # Pydantic 模式
│   │   └── 📂 utils/              # 工具函数
│   ├── 📂 storage/                # 软件文件存储
│   ├── main.py                    # 应用入口
│   └── pyproject.toml             # uv 依赖配置
│
└── 📂 frontend/                   # 前端项目
    ├── 📂 src/
    │   ├── 📂 api/                # API 请求封装
    │   ├── 📂 components/         # 公共组件
    │   ├── 📂 views/              # 页面视图
    │   │   ├── Login.vue          # 登录页
    │   │   ├── Layout.vue         # 主布局
    │   │   ├── Software/          # 软件相关页面
    │   │   └── Admin/             # 管理后台
    │   ├── 📂 router/             # 路由配置
    │   └── 📂 stores/             # Pinia 状态管理
    ├── package.json
    └── vite.config.js
```

---

## 🚀 快速开始

### 📦 前置要求

| 要求 | 版本 | 说明 |
|------|------|------|
| Python | 3.9+ | 后端运行环境 |
| Node.js | 16+ | 前端运行环境 |
| PostgreSQL | 12+ | 数据库 |
| uv | 最新 | Python 包管理器 |
| pnpm | 最新 | Node.js 包管理器 |

### 🔧 后端设置

```bash
# 1. 进入后端目录
cd backend

# 2. 安装依赖
uv sync

# 3. 配置环境变量 (.env)
DATABASE_URL=postgresql://user:password@localhost:5432/software_guard
SECRET_KEY=your-secret-key-here
STORAGE_PATH=./storage

# 4. 启动服务
uv run python main.py
```

后端服务运行在 **http://localhost:8000**

API 文档访问：**http://localhost:8000/docs** 📚

### 💻 前端设置

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
pnpm install

# 3. 启动开发服务器
pnpm dev
```

前端服务运行在 **http://localhost:5173**

### 👤 默认账号

首次启动自动创建管理员账号：

```
用户名: admin
密码: admin123
```

⚠️ **登录后请立即修改密码！**

---

## 📊 数据模型

| 表名 | 描述 |
|------|------|
| `users` | 用户信息与角色 |
| `software` | 软件基础信息 |
| `software_versions` | 软件版本详情 |
| `software_requests` | 软件申请记录 |
| `download_logs` | 下载行为日志 |
| `vulnerabilities` | 安全漏洞信息 |
| `audit_logs` | 操作审计记录 |

---

## 🔌 API 文档

### 认证接口
```http
POST   /api/auth/login      # 用户登录
POST   /api/auth/register   # 用户注册
GET    /api/auth/me         # 获取当前用户
```

### 软件管理
```http
GET    /api/software                    # 软件列表
GET    /api/software/{id}               # 软件详情
POST   /api/software                    # 创建软件
POST   /api/software/{id}/versions      # 上传版本
GET    /api/software/categories         # 分类列表
```

### 申请流程
```http
POST   /api/requests               # 创建申请
GET    /api/requests               # 申请列表
POST   /api/requests/{id}/review   # 审核申请
```

### 下载管理
```http
POST   /api/downloads/{version_id}  # 下载软件
GET    /api/downloads/logs          # 下载日志
GET    /api/downloads/stats         # 下载统计
```

### 漏洞管理
```http
POST   /api/vulnerabilities                           # 创建漏洞
GET    /api/vulnerabilities                           # 漏洞列表
GET    /api/vulnerabilities/check/{id}/{version}      # 检查漏洞
```

---

## 🔐 权限系统

### 角色定义

| 角色 | 权限 | 说明 |
|------|------|------|
| USER | 基础权限 | 浏览、下载、申请 |
| OPS | 运维权限 | + 软件管理、申请审核 |
| ADMIN | 管理员 | + 用户管理、系统配置 |

### 访问控制

- 后端：基于依赖注入的接口级权限校验
- 前端：路由守卫 + 组件级权限判断

---

## 🗺️ 开发路线图

### 已完成 ✅
- [x] 用户认证与权限系统
- [x] 软件版本管理
- [x] 下载统计与日志
- [x] 漏洞追踪与通知
- [x] 软件申请工作流

### 计划中 🚧
- [ ] 邮件通知功能
- [ ] 软件评分与评论
- [ ] 文件病毒扫描集成
- [ ] Docker 部署支持
- [ ] CI/CD 流水线
- [ ] 软件自动更新检测
- [ ] 移动端适配

---

## 📄 开源许可

本项目采用 **MIT License** 开源协议

---

<div align="center">

  **Made with ❤️ by Software Guard Team**

  [⭐ Star](../../stargazers) • [🐛 报告问题](../../issues) • [💡 功能建议](../../issues/new)

</div>
