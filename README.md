# 🤖 UMBot - 智能电商机器人

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Telegram Bot API](https://img.shields.io/badge/Telegram%20Bot%20API-Latest-blue.svg)](https://core.telegram.org/bots/api)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> 🚀 基于 Telegram 的智能电商机器人，集成多支付系统、会员体系和商城功能

## 📖 项目简介

UMBot 是一个功能完整的 Telegram 电商机器人，为用户提供便捷的在线购物体验。机器人集成了先进的会员系统、多种支付方式和智能商城管理，让电商运营变得简单高效。

### ✨ 核心特色

- 🎯 **零门槛使用** - 无需下载APP，直接在Telegram中完成所有操作
- 💎 **完整会员体系** - 多级会员制度，享受专属权益和折扣
- 💰 **多元支付方式** - 支持加密货币和余额支付
- 🛒 **智能商城系统** - 商品管理、订单跟踪、自动发货
- 🎁 **丰富营销活动** - 首充双倍、充值赠送、会员折扣

## 🚀 功能特性

### 🤖 Telegram 机器人
- ✅ 完整的 Telegram Bot 框架
- ✅ 支持命令处理和回调查询
- ✅ 异步处理，高性能响应
- ✅ 完善的错误处理和日志记录
- ✅ 多语言支持和用户友好界面

### 👥 会员系统
- 🆔 **用户注册** - 支持推荐码注册，建立用户关系链
- 🏆 **会员等级** - 青铜、白银、黄金、铂金、钻石五级体系
- 💰 **余额管理** - 充值、消费、转账全流程管理
- 🎁 **充值活动** - 首充双倍、充值赠送、VIP折扣等多种活动
- 🎯 **会员权益** - 购物折扣、专属活动、推荐奖励
- 📊 **交易记录** - 完整的充值和消费历史记录

### 💰 多支付系统集成
- 🔸 **UMPay 支付** - 支持 USDT (TRC20) 和 TRX 支付
- 🔸 **BEpusdt 支付** - 支持多链 USDT 支付（TRC20、ERC20、BSC、Polygon）
- 🔸 **余额支付** - 会员可使用账户余额直接购买
- 🔸 **自动确认** - 支付状态自动同步，无需人工干预
- 🔸 **安全保障** - 多重签名验证，确保交易安全

### 🛒 商城系统
- 📦 **商品管理** - 支持商品增删改查，库存实时更新
- 🛍️ **购物体验** - 商品搜索、分类浏览、详情展示
- 📋 **订单系统** - 订单创建、状态跟踪、自动发货
- 💸 **会员折扣** - 根据会员等级自动应用折扣
- 🔍 **智能搜索** - 支持关键词搜索，快速找到商品

## 📋 机器人命令

### 🎯 基础命令
```
/start          - 🚀 启动机器人，显示欢迎信息
/help           - ❓ 显示帮助信息和所有可用命令
```

### 👤 会员系统
```
/register [推荐码]  - 📝 注册成为会员（可选推荐码）
/member            - 👤 查看会员信息和余额
/recharge          - 💰 充值中心，查看充值活动
/rechargecenter    - ⚡ 快速充值菜单
```

### 🛍️ 商城功能
```
/shop                      - 🛒 显示商城商品列表（含会员折扣）
/buy <商品ID> <支付方式>    - 💳 购买商品
/search <关键词>           - 🔍 搜索商品
/myorders                  - 📦 查看我的订单
```

### 🔍 支付查询
```
/checkorder <订单ID> <支付订单ID>  - 🔍 查询UMPay订单状态
/checkbepusdt <订单ID>            - 🔍 查询BEpusdt订单状态
```

## 💳 支付方式

| 支付方式 | 描述 | 特点 |
|---------|------|------|
| `balance` | 余额支付 | 🎯 会员专享，即时到账 |
| `USDT` | USDT (TRC20) | 🔸 低手续费，快速确认 |
| `TRX` | TRX 支付 | 🔸 波场原生代币 |
| `bepusdt` | BEpusdt多链 | 🔸 支持多条区块链 |

## 🎯 会员等级系统

### 🏆 会员等级

| 等级 | 图标 | 充值要求 | 购物折扣 | 特殊权益 |
|------|------|----------|----------|----------|
| 青铜会员 | 🥉 | 注册即得 | 无折扣 | 基础服务 |
| 白银会员 | 🥈 | 累计充值 ¥500 | 5% OFF | 优先客服 |
| 黄金会员 | 🥇 | 累计充值 ¥2000 | 10% OFF | 专属活动 |
| 铂金会员 | 💎 | 累计充值 ¥5000 | 15% OFF | VIP通道 |
| 钻石会员 | 💍 | 累计充值 ¥10000 | 20% OFF | 专属客服 |
| 至尊会员 | 👑 | 累计充值 ¥30000 | 25% OFF | 至尊特权 |

### 🎁 充值活动

#### 🌟 首充双倍
- 📝 **活动内容**：首次充值赠送 100% 额外余额
- 💰 **充值范围**：¥50 - ¥500
- 🎯 **参与条件**：新注册用户
- ⏰ **活动时间**：长期有效

#### 💰 充值赠送
- 📝 **活动内容**：单次充值满 ¥100 赠送 10% 额外余额
- 💰 **最低充值**：¥100
- 🎯 **参与次数**：每用户限10次
- ⏰ **活动时间**：30天

#### 🔥 VIP充值折扣
- 📝 **活动内容**：黄金及以上会员充值享受 5% 折扣
- 💰 **最低充值**：¥200
- 🎯 **参与条件**：黄金会员及以上
- ⏰ **活动时间**：60天

### 🎁 会员权益

- ✅ **余额支付功能** - 便捷的内部支付系统
- ✅ **购物专享折扣** - 根据等级享受不同折扣
- ✅ **充值活动参与** - 专属充值优惠活动
- ✅ **推荐好友奖励** - 推荐新用户获得奖励
- ✅ **完整交易记录** - 详细的消费和充值记录
- ✅ **优先客户服务** - 高等级会员享受优先服务

## 🛠️ 技术架构

### 📁 项目结构
```
umbot/
├── 📁 bot/                    # 机器人核心模块
│   ├── 🐍 main.py            # 主程序入口
│   ├── 🐍 handlers.py        # 基础命令处理器
│   └── 🐍 member_handlers.py # 会员系统处理器
├── 📁 store/                  # 商城和会员系统
│   ├── 🐍 shop.py            # 商城管理
│   ├── 🐍 member.py          # 会员系统
│   └── 🐍 models.py          # 数据模型
├── 📁 payments/               # 支付系统
│   ├── 🐍 umpay.py           # UMPay支付接口
│   └── 🐍 bepusdt.py         # BEpusdt支付接口
├── 📁 webhooks/               # 支付回调处理
│   ├── 🐍 member_callback.py # 会员充值回调
│   └── 🐍 bepusdt_callback.py# BEpusdt回调
├── 📁 docs/                   # 文档目录
│   ├── 📄 vercel-deployment.md
│   └── 📄 github-guide.md
├── 🐍 config.py              # 配置文件
├── 📄 requirements.txt       # 依赖包列表
├── 📄 vercel.json           # Vercel部署配置
└── 📄 .env                  # 环境变量配置
```

### 🔧 技术栈

- **🐍 Python 3.8+** - 主要开发语言
- **🤖 python-telegram-bot** - Telegram Bot API 封装
- **⚡ asyncio** - 异步编程支持
- **🌐 Vercel** - 无服务器部署平台
- **🔐 加密货币支付** - UMPay & BEpusdt 集成

## 🚀 快速开始

### 📋 环境要求

- Python 3.8 或更高版本
- Telegram Bot Token
- UMPay API 密钥（可选）
- BEpusdt API 密钥（可选）

### 🔧 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-username/umbot.git
cd umbot
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，填入必要的配置信息
```

4. **启动机器人**
```bash
python bot/main.py
```

### ⚙️ 环境变量配置

在 `.env` 文件中配置以下变量：

```env
# Telegram Bot 配置
TELEGRAM_TOKEN=your_bot_token_here

# UMPay 配置（可选）
UMPAY_API_KEY=your_umpay_api_key
UMPAY_SECRET=your_umpay_secret

# BEpusdt 配置（可选）
BEPUSDT_API_KEY=your_bepusdt_api_key
BEPUSDT_SECRET=your_bepusdt_secret

# 其他配置
DEBUG=False
LOG_LEVEL=INFO
```

## 🌐 部署指南

### 🚀 Vercel 部署

1. **Fork 项目到你的 GitHub**
2. **在 Vercel 中导入项目**
3. **配置环境变量**
4. **部署完成**

详细部署指南请参考：[Vercel 部署文档](docs/vercel-deployment.md)

### 🐳 Docker 部署

```bash
# 构建镜像
docker build -t umbot .

# 运行容器
docker run -d --name umbot --env-file .env umbot
```

## 📚 使用指南

### 🎯 用户使用流程

1. **注册会员** - 使用 `/register` 命令注册
2. **充值余额** - 使用 `/recharge` 查看充值选项
3. **浏览商城** - 使用 `/shop` 浏览商品
4. **购买商品** - 使用 `/buy` 命令购买
5. **查看订单** - 使用 `/myorders` 查看订单状态

### 🛠️ 管理员功能

- 商品管理（添加、编辑、删除商品）
- 订单管理（查看、处理订单）
- 用户管理（查看用户信息、余额）
- 活动管理（创建、编辑充值活动）

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 🐛 报告问题

如果你发现了 bug 或有功能建议，请：

1. 检查是否已有相关 issue
2. 创建新的 issue，详细描述问题
3. 提供复现步骤和环境信息

### 💡 提交代码

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系我们

- 📧 **邮箱**: support@umbot.com
- 💬 **Telegram**: [@UMBotSupport](https://t.me/UMBotSupport)
- 🐛 **问题反馈**: [GitHub Issues](https://github.com/your-username/umbot/issues)

## 🙏 致谢

感谢以下开源项目的支持：

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot API 封装
- [Vercel](https://vercel.com/) - 无服务器部署平台
- [UMPay](https://umpay.com/) - 加密货币支付解决方案
- [BEpusdt](https://bepusdt.com/) - 多链 USDT 支付服务

---

<div align="center">

**🌟 如果这个项目对你有帮助，请给我们一个 Star！🌟**

[⭐ Star 项目](https://github.com/your-username/umbot) | [🐛 报告问题](https://github.com/your-username/umbot/issues) | [💡 功能建议](https://github.com/your-username/umbot/issues/new)

</div>