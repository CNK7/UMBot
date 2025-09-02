# Vercel 部署指南

本指南将帮助您将 UMBot 项目部署到 Vercel 平台，主要用于部署 BEpusdt 支付回调服务。

## 前置要求

1. **Vercel 账户**：注册 [Vercel](https://vercel.com) 账户
2. **GitHub 仓库**：将项目代码推送到 GitHub
3. **环境变量**：准备好所需的环境变量

## 部署步骤

### 1. 准备项目

确保项目根目录包含以下文件：
- `vercel.json` - Vercel 配置文件
- `requirements.txt` - Python 依赖
- `webhooks/bepusdt_callback.py` - 回调服务

### 2. 连接 GitHub

1. 登录 [Vercel Dashboard](https://vercel.com/dashboard)
2. 点击 "New Project"
3. 选择 "Import Git Repository"
4. 连接您的 GitHub 账户并选择 UMBot 仓库

### 3. 配置环境变量

在 Vercel 项目设置中添加以下环境变量：

```bash
# Telegram Bot Token
TELEGRAM_TOKEN=your_telegram_bot_token

# BEpusdt 配置
BEPUSDT_API_URL=https://your-bepusdt-domain.com
BEPUSDT_APP_ID=your_app_id
BEPUSDT_APP_SECRET=your_app_secret
BEPUSDT_NOTIFY_URL=https://your-vercel-domain.vercel.app/webhook/bepusdt
```

**设置步骤：**
1. 进入项目 Settings → Environment Variables
2. 逐一添加上述环境变量
3. 确保所有变量都设置正确

### 4. 部署配置

项目已包含 `vercel.json` 配置文件：

```json
{
  "version": 2,
  "builds": [
    {
      "src": "webhooks/bepusdt_callback.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/webhook/bepusdt",
      "dest": "webhooks/bepusdt_callback.py"
    },
    {
      "src": "/health",
      "dest": "webhooks/bepusdt_callback.py"
    }
  ]
}
```

### 5. 部署项目

1. 点击 "Deploy" 按钮
2. Vercel 将自动构建和部署项目
3. 部署完成后，您将获得一个 `.vercel.app` 域名

## 部署后配置

### 1. 更新 BEpusdt 回调地址

将您的 Vercel 域名设置为 BEpusdt 的回调地址：
```
https://your-project-name.vercel.app/webhook/bepusdt
```

### 2. 测试回调服务

访问健康检查接口确认服务正常：
```
https://your-project-name.vercel.app/health
```

应该返回：
```json
{"status": "ok"}
```

### 3. 更新机器人配置

在本地 `.env` 文件中更新回调地址：
```bash
BEPUSDT_NOTIFY_URL=https://your-project-name.vercel.app/webhook/bepusdt
```

## 常见问题

### Q: 部署失败怎么办？

A: 检查以下几点：
1. 确保 `requirements.txt` 包含所有依赖
2. 检查 `vercel.json` 配置是否正确
3. 查看 Vercel 部署日志中的错误信息

### Q: 回调接口返回 500 错误？

A: 可能的原因：
1. 环境变量未正确设置
2. BEpusdt 配置错误
3. 检查 Vercel Function 日志

### Q: 如何查看日志？

A: 在 Vercel Dashboard 中：
1. 进入项目页面
2. 点击 "Functions" 标签
3. 选择对应的函数查看日志

### Q: 如何更新部署？

A: 推送代码到 GitHub 主分支，Vercel 会自动重新部署。

## 安全建议

1. **环境变量安全**：
   - 不要在代码中硬编码敏感信息
   - 使用 Vercel 环境变量管理

2. **域名安全**：
   - 考虑使用自定义域名
   - 启用 HTTPS（Vercel 默认支持）

3. **访问控制**：
   - 验证回调签名
   - 限制访问来源（如果需要）

## 监控和维护

1. **监控回调**：
   - 定期检查回调服务状态
   - 监控支付成功率

2. **日志分析**：
   - 定期查看 Vercel 函数日志
   - 关注错误和异常

3. **性能优化**：
   - 监控函数执行时间
   - 优化代码性能

## 相关链接

- [Vercel 官方文档](https://vercel.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [BEpusdt 项目](https://github.com/bepusdt/bepusdt)

---

如有问题，请查看项目 Issues 或联系开发者。