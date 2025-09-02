# GitHub 使用指南

本指南将帮助您使用 GitHub 管理 UMBot 项目，包括代码版本控制、协作开发和项目维护。

## 前置要求

1. **GitHub 账户**：注册 [GitHub](https://github.com) 账户
2. **Git 工具**：安装 [Git](https://git-scm.com/)
3. **SSH 密钥**：配置 SSH 密钥（推荐）

## 初始设置

### 1. 创建仓库

**方法一：在 GitHub 网站创建**
1. 登录 GitHub
2. 点击右上角 "+" → "New repository"
3. 填写仓库信息：
   - Repository name: `umbot`
   - Description: `UMBot - Telegram商城机器人`
   - 选择 Public 或 Private
   - 勾选 "Add a README file"
   - 选择 Python .gitignore 模板
   - 选择合适的 License（如 MIT）

**方法二：从本地推送**
```bash
# 在项目目录初始化 Git
cd d:\umbot
git init

# 添加远程仓库
git remote add origin https://github.com/yourusername/umbot.git

# 添加所有文件
git add .

# 提交代码
git commit -m "Initial commit: UMBot project setup"

# 推送到 GitHub
git push -u origin main
```

### 2. 配置 Git

```bash
# 设置用户信息
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 设置默认分支名
git config --global init.defaultBranch main
```

### 3. SSH 密钥配置（推荐）

```bash
# 生成 SSH 密钥
ssh-keygen -t ed25519 -C "your.email@example.com"

# 添加到 SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# 复制公钥到剪贴板
cat ~/.ssh/id_ed25519.pub
```

然后在 GitHub Settings → SSH and GPG keys 中添加公钥。

## 基本工作流程

### 1. 克隆仓库

```bash
# HTTPS 方式
git clone https://github.com/yourusername/umbot.git

# SSH 方式（推荐）
git clone git@github.com:yourusername/umbot.git

cd umbot
```

### 2. 日常开发流程

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 创建功能分支
git checkout -b feature/new-payment-method

# 3. 进行开发...
# 编辑文件，添加新功能

# 4. 查看修改状态
git status

# 5. 添加修改的文件
git add .
# 或者添加特定文件
git add payments/new_payment.py

# 6. 提交修改
git commit -m "feat: add new payment method support"

# 7. 推送分支
git push origin feature/new-payment-method
```

### 3. 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```bash
# 功能添加
git commit -m "feat: add BEpusdt payment integration"

# 问题修复
git commit -m "fix: resolve telegram timeout issue"

# 文档更新
git commit -m "docs: update deployment guide"

# 代码重构
git commit -m "refactor: optimize shop class structure"

# 性能优化
git commit -m "perf: improve order processing speed"

# 测试相关
git commit -m "test: add unit tests for payment methods"
```

## 分支管理策略

### 1. 分支类型

- **main**: 主分支，生产环境代码
- **develop**: 开发分支，集成最新功能
- **feature/***: 功能分支，开发新功能
- **hotfix/***: 热修复分支，紧急修复
- **release/***: 发布分支，准备发布版本

### 2. 分支命名规范

```bash
# 功能分支
feature/payment-integration
feature/user-authentication

# 修复分支
hotfix/telegram-api-error
hotfix/database-connection

# 发布分支
release/v1.0.0
release/v1.1.0
```

### 3. 分支操作

```bash
# 创建并切换到新分支
git checkout -b feature/shop-enhancement

# 切换分支
git checkout main

# 合并分支
git checkout main
git merge feature/shop-enhancement

# 删除分支
git branch -d feature/shop-enhancement

# 删除远程分支
git push origin --delete feature/shop-enhancement
```

## Pull Request 工作流程

### 1. 创建 Pull Request

1. 推送功能分支到 GitHub
2. 在 GitHub 网站点击 "Compare & pull request"
3. 填写 PR 信息：
   - 标题：简洁描述修改内容
   - 描述：详细说明修改原因和内容
   - 关联 Issue（如果有）

### 2. PR 模板

创建 `.github/pull_request_template.md`：

```markdown
## 修改说明

### 修改类型
- [ ] 新功能
- [ ] 问题修复
- [ ] 文档更新
- [ ] 代码重构
- [ ] 性能优化

### 修改内容
- 

### 测试情况
- [ ] 已通过本地测试
- [ ] 已通过集成测试
- [ ] 需要额外测试

### 相关 Issue
Closes #

### 截图（如适用）

```

### 3. 代码审查

- 指定审查者
- 响应审查意见
- 修改代码并推送更新
- 获得批准后合并

## Issue 管理

### 1. 创建 Issue

用于跟踪：
- 功能需求
- Bug 报告
- 改进建议
- 文档更新

### 2. Issue 模板

创建 `.github/ISSUE_TEMPLATE/`：

**bug_report.md**:
```markdown
---
name: Bug 报告
about: 报告项目中的问题
title: '[BUG] '
labels: bug
assignees: ''
---

## 问题描述
简洁清晰地描述问题。

## 复现步骤
1. 执行 '...'
2. 点击 '....'
3. 滚动到 '....'
4. 看到错误

## 期望行为
描述您期望发生的情况。

## 实际行为
描述实际发生的情况。

## 环境信息
- OS: [e.g. Windows 10]
- Python 版本: [e.g. 3.9.0]
- 项目版本: [e.g. v1.0.0]
```

**feature_request.md**:
```markdown
---
name: 功能请求
about: 建议新功能
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

## 功能描述
简洁清晰地描述您想要的功能。

## 解决的问题
描述这个功能解决什么问题。

## 建议的解决方案
描述您希望如何实现这个功能。

## 替代方案
描述您考虑过的其他解决方案。
```

## GitHub Actions CI/CD

### 1. 基本工作流程

创建 `.github/workflows/ci.yml`：

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python -m pytest tests/
    
    - name: Code quality check
      run: |
        pip install flake8
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

### 2. 自动部署

```yaml
  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Vercel
      uses: amondnet/vercel-action@v20
      with:
        vercel-token: ${{ secrets.VERCEL_TOKEN }}
        vercel-org-id: ${{ secrets.ORG_ID }}
        vercel-project-id: ${{ secrets.PROJECT_ID }}
```

## 安全最佳实践

### 1. 敏感信息管理

- **永远不要**提交敏感信息到仓库
- 使用 `.env` 文件存储配置
- 确保 `.env` 在 `.gitignore` 中
- 使用 GitHub Secrets 存储 CI/CD 密钥

### 2. .gitignore 配置

```gitignore
# 环境变量
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# 日志文件
*.log
logs/

# 数据库
*.db
*.sqlite3

# 临时文件
.tmp/
temp/
```

## 项目维护

### 1. 版本管理

使用 [Semantic Versioning](https://semver.org/)：
- `1.0.0` - 主版本.次版本.修订版本
- `v1.0.0` - 创建 Git 标签

```bash
# 创建标签
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# 查看标签
git tag -l

# 删除标签
git tag -d v1.0.0
git push origin --delete v1.0.0
```

### 2. 发布管理

1. 在 GitHub 创建 Release
2. 选择对应的标签
3. 编写发布说明
4. 上传发布文件（如需要）

### 3. 项目文档

维护以下文档：
- `README.md` - 项目介绍和快速开始
- `CHANGELOG.md` - 版本更新日志
- `CONTRIBUTING.md` - 贡献指南
- `LICENSE` - 开源协议

## 协作开发

### 1. 团队权限管理

- **Owner**: 完全控制权限
- **Admin**: 管理仓库设置
- **Write**: 推送代码权限
- **Read**: 只读权限

### 2. 分支保护规则

在 Settings → Branches 中设置：
- 要求 PR 审查
- 要求状态检查通过
- 限制推送到主分支
- 要求分支为最新

### 3. 代码审查规范

- 审查代码逻辑和质量
- 检查安全问题
- 验证测试覆盖率
- 确保文档更新

## 常用命令速查

```bash
# 查看状态
git status
git log --oneline
git branch -a

# 撤销操作
git checkout -- file.py          # 撤销文件修改
git reset HEAD file.py           # 取消暂存
git reset --hard HEAD~1          # 撤销最后一次提交

# 远程操作
git remote -v                    # 查看远程仓库
git fetch origin                 # 获取远程更新
git pull origin main             # 拉取并合并
git push origin main             # 推送到远程

# 分支操作
git branch feature/new-feature   # 创建分支
git checkout feature/new-feature # 切换分支
git merge feature/new-feature    # 合并分支
git branch -d feature/new-feature # 删除分支
```

## 故障排除

### 常见问题

1. **推送被拒绝**
   ```bash
   git pull origin main
   git push origin main
   ```

2. **合并冲突**
   ```bash
   # 手动解决冲突后
   git add .
   git commit -m "resolve merge conflict"
   ```

3. **忘记添加 .gitignore**
   ```bash
   git rm -r --cached .
   git add .
   git commit -m "update .gitignore"
   ```

## 相关资源

- [Git 官方文档](https://git-scm.com/doc)
- [GitHub 官方指南](https://guides.github.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)

---

如有问题，请查看项目 Issues 或联系项目维护者。