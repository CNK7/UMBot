import asyncio
from datetime import datetime
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from store.member import MemberSystem, User, RechargeRecord
from payments.umpay import UMPay
from payments.bepusdt import BEpusdt
import logging

logger = logging.getLogger(__name__)

# 全局会员系统实例
member_system = MemberSystem()

# 支付系统实例
umpay = UMPay()
bepusdt = BEpusdt()

async def register_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """注册会员"""
    user = update.effective_user
    if not user:
        await update.message.reply_text("❌ 无法获取用户信息")
        return
    
    # 检查是否已注册
    existing_user = member_system.get_user(user.id)
    if existing_user:
        await update.message.reply_text("✅ 您已经是会员了！")
        return
    
    # 处理推荐码
    referrer_id = None
    if context.args and len(context.args) > 0:
        try:
            referrer_id = int(context.args[0])
            referrer = member_system.get_user(referrer_id)
            if not referrer:
                referrer_id = None
        except ValueError:
            referrer_id = None
    
    # 注册用户
    new_user = member_system.register_user(
        user_id=user.id,
        username=user.username or "",
        first_name=user.first_name,
        last_name=user.last_name,
        referrer_id=referrer_id
    )
    
    benefits = new_user.get_level_benefits()
    welcome_text = f"""🎉 欢迎加入会员系统！

👤 用户信息：
• 用户名：{user.first_name}
• 会员等级：{benefits['emoji']} {benefits['name']}
• 账户余额：¥{new_user.balance:.2f}
• 推荐码：`{new_user.referral_code}`

💎 会员权益：
• 购物折扣：{benefits['discount']*100:.0f}%
• 充值赠送：{benefits['recharge_bonus']*100:.0f}%

📱 使用 /member 查看详细信息
💰 使用 /recharge 进行充值"""
    
    if referrer_id:
        welcome_text += f"\n\n🎁 感谢使用推荐码，推荐人已获得奖励！"
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def member_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看会员信息"""
    user = update.effective_user
    if not user:
        return
    
    member = member_system.get_user(user.id)
    if not member:
        await update.message.reply_text(
            "❌ 您还不是会员，请使用 /register 注册"
        )
        return
    
    benefits = member.get_level_benefits()
    
    # 获取最近的充值记录
    recent_recharges = member_system.get_user_recharge_history(user.id, 3)
    recharge_history = "\n".join([
        f"• {r.created_at.strftime('%m-%d %H:%M')} ¥{r.amount:.2f} ({r.status})"
        for r in recent_recharges
    ]) if recent_recharges else "暂无充值记录"
    
    info_text = f"""👤 会员信息

🆔 基本信息：
• 用户名：{member.first_name}
• 会员等级：{benefits['emoji']} {benefits['name']}
• 注册时间：{member.created_at.strftime('%Y-%m-%d')}
• 推荐码：`{member.referral_code}`

💰 账户信息：
• 当前余额：¥{member.balance:.2f}
• 累计充值：¥{member.total_recharged:.2f}
• 累计消费：¥{member.total_spent:.2f}

💎 会员权益：
• 购物折扣：{benefits['discount']*100:.0f}%
• 充值赠送：{benefits['recharge_bonus']*100:.0f}%

📊 最近充值：
{recharge_history}"""
    
    keyboard = [
        [InlineKeyboardButton("💰 充值", callback_data="recharge_menu")],
        [InlineKeyboardButton("📊 交易记录", callback_data="transaction_history")],
        [InlineKeyboardButton("🎁 推荐好友", callback_data="referral_info")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        info_text, 
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def recharge_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """充值菜单"""
    user = update.effective_user
    if not user:
        return
    
    member = member_system.get_user(user.id)
    if not member:
        await update.message.reply_text(
            "❌ 您还不是会员，请使用 /register 注册"
        )
        return
    
    # 获取当前活动
    activities = member_system.get_active_activities()
    activity_text = "\n".join([
        f"🎁 {a.name}：{a.description}"
        for a in activities[:3]
    ]) if activities else "暂无充值活动"
    
    recharge_text = f"""💰 充值中心

💎 当前余额：¥{member.balance:.2f}
🏆 会员等级：{member.get_level_benefits()['emoji']} {member.get_level_benefits()['name']}

🎉 当前活动：
{activity_text}

💳 请选择充值金额："""
    
    keyboard = [
        [InlineKeyboardButton("¥50", callback_data="recharge_50"),
         InlineKeyboardButton("¥100", callback_data="recharge_100")],
        [InlineKeyboardButton("¥200", callback_data="recharge_200"),
         InlineKeyboardButton("¥500", callback_data="recharge_500")],
        [InlineKeyboardButton("¥1000", callback_data="recharge_1000"),
         InlineKeyboardButton("¥2000", callback_data="recharge_2000")],
        [InlineKeyboardButton("💬 自定义金额", callback_data="recharge_custom")],
        [InlineKeyboardButton("🎁 查看活动详情", callback_data="activity_details")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        recharge_text,
        reply_markup=reply_markup
    )

async def handle_recharge_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理充值回调"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    if not user:
        return
    
    member = member_system.get_user(user.id)
    if not member:
        await query.edit_message_text("❌ 您还不是会员，请使用 /register 注册")
        return
    
    data = query.data
    
    if data == "recharge_menu":
        await recharge_menu(update, context)
        return
    
    if data == "transaction_history":
        await show_transaction_history(update, context)
        return
    
    if data == "referral_info":
        await show_referral_info(update, context)
        return
    
    if data == "activity_details":
        await show_activity_details(update, context)
        return
    
    if data.startswith("recharge_"):
        amount_str = data.replace("recharge_", "")
        if amount_str == "custom":
            await query.edit_message_text(
                "💬 请输入充值金额（最低50元）：\n\n发送格式：/recharge 金额"
            )
            return
        
        try:
            amount = float(amount_str)
            await process_recharge(query, user.id, amount)
        except ValueError:
            await query.edit_message_text("❌ 无效的充值金额")
    
    elif data.startswith("pay_"):
        # 处理支付方式选择
        parts = data.split("_")
        if len(parts) >= 3:
            record_id = parts[1]
            payment_method = parts[2]
            await process_payment(query, record_id, payment_method)

async def process_recharge(query, user_id: int, amount: float):
    """处理充值请求"""
    if amount < 50:
        await query.edit_message_text("❌ 最低充值金额为50元")
        return
    
    # 获取适用活动
    applicable_activities = member_system.get_user_applicable_activities(user_id, amount)
    
    activity_info = ""
    if applicable_activities:
        best_activity = applicable_activities[0]
        bonus = best_activity.calculate_bonus(amount)
        activity_info = f"\n🎁 活动奖励：+¥{bonus:.2f}\n💰 实际到账：¥{amount + bonus:.2f}"
    
    recharge_text = f"""💰 充值确认

💳 充值金额：¥{amount:.2f}{activity_info}

请选择支付方式："""
    
    keyboard = [
        [InlineKeyboardButton("🔷 USDT (TRC20)", callback_data=f"create_recharge_{amount}_usdt")],
        [InlineKeyboardButton("🔶 TRX", callback_data=f"create_recharge_{amount}_trx")],
        [InlineKeyboardButton("💎 BEpusdt", callback_data=f"create_recharge_{amount}_bepusdt")],
        [InlineKeyboardButton("⬅️ 返回", callback_data="recharge_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        recharge_text,
        reply_markup=reply_markup
    )

async def handle_create_recharge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理创建充值订单"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    if not user:
        return
    
    data = query.data
    if not data.startswith("create_recharge_"):
        return
    
    parts = data.replace("create_recharge_", "").split("_")
    if len(parts) != 2:
        return
    
    try:
        amount = float(parts[0])
        payment_method = parts[1]
    except ValueError:
        await query.edit_message_text("❌ 无效的充值参数")
        return
    
    # 创建充值订单
    record = member_system.create_recharge_order(user.id, amount, payment_method)
    if not record:
        await query.edit_message_text("❌ 创建充值订单失败")
        return
    
    # 根据支付方式创建支付订单
    if payment_method in ["usdt", "trx"]:
        await create_umpay_order(query, record, payment_method)
    elif payment_method == "bepusdt":
        await create_bepusdt_order(query, record)
    else:
        await query.edit_message_text("❌ 不支持的支付方式")

async def create_umpay_order(query, record: RechargeRecord, payment_method: str):
    """创建UMPay支付订单"""
    try:
        # 创建支付订单
        order_data = {
            "order_id": record.id,
            "amount": record.amount,
            "currency": payment_method.upper(),
            "notify_url": "https://your-domain.com/webhook/umpay",
            "return_url": "https://t.me/your_bot"
        }
        
        payment_info = umpay.create_order(order_data)
        
        if payment_info and payment_info.get("status") == "success":
            payment_text = f"""💰 充值订单已创建

📋 订单信息：
• 订单号：`{record.id}`
• 充值金额：¥{record.amount:.2f}
• 赠送金额：¥{record.bonus_amount:.2f}
• 实际到账：¥{record.amount + record.bonus_amount:.2f}
• 支付方式：{payment_method.upper()}

💳 支付信息：
• 收款地址：`{payment_info.get('address', '')}`
• 支付金额：{payment_info.get('crypto_amount', '')} {payment_method.upper()}
• 订单有效期：1小时

⚠️ 请在1小时内完成支付，逾期订单将自动取消"""
            
            keyboard = [
                [InlineKeyboardButton("🔍 查询订单状态", callback_data=f"check_recharge_{record.id}")],
                [InlineKeyboardButton("❌ 取消订单", callback_data=f"cancel_recharge_{record.id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                payment_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_text("❌ 创建支付订单失败，请稍后重试")
    
    except Exception as e:
        logger.error(f"创建UMPay订单失败: {e}")
        await query.edit_message_text("❌ 创建支付订单失败，请稍后重试")

async def create_bepusdt_order(query, record: RechargeRecord):
    """创建BEpusdt支付订单"""
    try:
        # 创建支付订单
        order_data = {
            "order_id": record.id,
            "amount": record.amount,
            "notify_url": "https://your-domain.com/webhook/bepusdt"
        }
        
        payment_info = bepusdt.create_order(order_data)
        
        if payment_info and payment_info.get("status") == "success":
            payment_text = f"""💰 充值订单已创建

📋 订单信息：
• 订单号：`{record.id}`
• 充值金额：¥{record.amount:.2f}
• 赠送金额：¥{record.bonus_amount:.2f}
• 实际到账：¥{record.amount + record.bonus_amount:.2f}
• 支付方式：BEpusdt

💳 支付信息：
• 支付链接：{payment_info.get('pay_url', '')}
• 订单有效期：1小时

⚠️ 请在1小时内完成支付，逾期订单将自动取消"""
            
            keyboard = [
                [InlineKeyboardButton("💳 去支付", url=payment_info.get('pay_url', ''))],
                [InlineKeyboardButton("🔍 查询订单状态", callback_data=f"check_recharge_{record.id}")],
                [InlineKeyboardButton("❌ 取消订单", callback_data=f"cancel_recharge_{record.id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                payment_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_text("❌ 创建支付订单失败，请稍后重试")
    
    except Exception as e:
        logger.error(f"创建BEpusdt订单失败: {e}")
        await query.edit_message_text("❌ 创建支付订单失败，请稍后重试")

async def check_recharge_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查询充值状态"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if not data.startswith("check_recharge_"):
        return
    
    record_id = data.replace("check_recharge_", "")
    record = member_system.recharge_records.get(record_id)
    
    if not record:
        await query.edit_message_text("❌ 订单不存在")
        return
    
    if record.is_expired():
        record.status = "expired"
        await query.edit_message_text("❌ 订单已过期")
        return
    
    status_text = {
        "pending": "⏳ 等待支付",
        "paid": "✅ 支付成功",
        "failed": "❌ 支付失败",
        "expired": "⏰ 订单过期"
    }
    
    status_info = f"""🔍 订单状态查询

📋 订单信息：
• 订单号：`{record.id}`
• 充值金额：¥{record.amount:.2f}
• 赠送金额：¥{record.bonus_amount:.2f}
• 支付方式：{record.payment_method}
• 订单状态：{status_text.get(record.status, record.status)}
• 创建时间：{record.created_at.strftime('%Y-%m-%d %H:%M:%S')}"""
    
    if record.paid_at:
        status_info += f"\n• 支付时间：{record.paid_at.strftime('%Y-%m-%d %H:%M:%S')}"
    
    keyboard = []
    if record.status == "pending":
        keyboard.append([InlineKeyboardButton("🔄 刷新状态", callback_data=f"check_recharge_{record_id}")])
        keyboard.append([InlineKeyboardButton("❌ 取消订单", callback_data=f"cancel_recharge_{record_id}")])
    
    keyboard.append([InlineKeyboardButton("⬅️ 返回", callback_data="recharge_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        status_info,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def show_transaction_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """显示交易记录"""
    query = update.callback_query
    user = update.effective_user
    
    if not user:
        return
    
    transactions = member_system.get_user_transactions(user.id, 10)
    
    if not transactions:
        history_text = "📊 交易记录\n\n暂无交易记录"
    else:
        history_text = "📊 最近交易记录\n\n"
        for t in transactions:
            amount_str = f"+¥{t.amount:.2f}" if t.amount > 0 else f"-¥{abs(t.amount):.2f}"
            history_text += f"• {t.created_at.strftime('%m-%d %H:%M')} {amount_str} ({t.description})\n"
    
    keyboard = [[InlineKeyboardButton("⬅️ 返回", callback_data="member_info")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        history_text,
        reply_markup=reply_markup
    )

async def show_referral_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """显示推荐信息"""
    query = update.callback_query
    user = update.effective_user
    
    if not user:
        return
    
    member = member_system.get_user(user.id)
    if not member:
        return
    
    referral_text = f"""🎁 推荐好友

👥 您的推荐码：`{member.referral_code}`

💰 推荐奖励：
• 好友注册：¥10
• 好友首充：¥20

📱 推荐链接：
https://t.me/your_bot?start={member.user_id}

📋 使用方法：
1. 分享推荐链接给好友
2. 好友点击链接注册会员
3. 自动获得推荐奖励"""
    
    keyboard = [[InlineKeyboardButton("⬅️ 返回", callback_data="member_info")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        referral_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def show_activity_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """显示活动详情"""
    query = update.callback_query
    
    activities = member_system.get_active_activities()
    
    if not activities:
        activity_text = "🎁 充值活动\n\n暂无进行中的活动"
    else:
        activity_text = "🎁 当前充值活动\n\n"
        for i, activity in enumerate(activities[:5], 1):
            activity_text += f"{i}. **{activity.name}**\n"
            activity_text += f"   {activity.description}\n"
            activity_text += f"   最低金额：¥{activity.min_amount:.0f}\n"
            if activity.max_amount:
                activity_text += f"   最高金额：¥{activity.max_amount:.0f}\n"
            activity_text += f"   结束时间：{activity.end_time.strftime('%Y-%m-%d %H:%M')}\n\n"
    
    keyboard = [[InlineKeyboardButton("⬅️ 返回", callback_data="recharge_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        activity_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def custom_recharge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """自定义充值金额"""
    user = update.effective_user
    if not user:
        return
    
    member = member_system.get_user(user.id)
    if not member:
        await update.message.reply_text(
            "❌ 您还不是会员，请使用 /register 注册"
        )
        return
    
    if not context.args or len(context.args) == 0:
        await update.message.reply_text(
            "💬 请输入充值金额\n\n使用格式：/recharge 金额\n例如：/recharge 100"
        )
        return
    
    try:
        amount = float(context.args[0])
        if amount < 50:
            await update.message.reply_text("❌ 最低充值金额为50元")
            return
        
        # 获取适用活动
        applicable_activities = member_system.get_user_applicable_activities(user.id, amount)
        
        activity_info = ""
        if applicable_activities:
            best_activity = applicable_activities[0]
            bonus = best_activity.calculate_bonus(amount)
            activity_info = f"\n🎁 活动奖励：+¥{bonus:.2f}\n💰 实际到账：¥{amount + bonus:.2f}"
        
        recharge_text = f"""💰 充值确认

💳 充值金额：¥{amount:.2f}{activity_info}

请选择支付方式："""
        
        keyboard = [
            [InlineKeyboardButton("🔷 USDT (TRC20)", callback_data=f"create_recharge_{amount}_usdt")],
            [InlineKeyboardButton("🔶 TRX", callback_data=f"create_recharge_{amount}_trx")],
            [InlineKeyboardButton("💎 BEpusdt", callback_data=f"create_recharge_{amount}_bepusdt")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            recharge_text,
            reply_markup=reply_markup
        )
        
    except ValueError:
        await update.message.reply_text("❌ 请输入有效的数字金额")

# 回调查询处理器
recharge_callback_handler = CallbackQueryHandler(
    handle_recharge_callback,
    pattern=r"^(recharge_|transaction_history|referral_info|activity_details|check_recharge_|cancel_recharge_|create_recharge_|pay_)"
)

create_recharge_handler = CallbackQueryHandler(
    handle_create_recharge,
    pattern=r"^create_recharge_"
)

check_recharge_handler = CallbackQueryHandler(
    check_recharge_status,
    pattern=r"^check_recharge_"
)