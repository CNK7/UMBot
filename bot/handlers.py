import asyncio
import datetime
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from payments.umpay import UMPay
from store.shop import Shop
from store.member import MemberSystem

# Initialize UMPay and Shop
umpay = UMPay(network='mainnet')
member_system = MemberSystem()
shop = Shop(member_system)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    welcome_text = (
        "🤖 欢迎使用 UMBot！\n\n"
        "我是您的专属购物助手，支持以下功能：\n\n"
        "💰 支付功能：\n"
        "/pay <金额> <货币> - 创建支付订单\n"
        "/check <订单ID> - 查询支付状态\n\n"
        "🛍️ 商城功能：\n"
        "/shop - 浏览商品\n"
        "/help - 查看帮助信息\n\n"
        "支持的加密货币：USDT、TRX"
    )
    await update.message.reply_text(welcome_text)

async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Create a payment order."""
    try:
        if len(context.args) < 2:
            await update.message.reply_text(
                "❌ 用法错误！\n\n"
                "正确用法：/pay <金额> <货币>\n"
                "示例：/pay 10 USDT 或 /pay 100 TRX"
            )
            return
        
        amount = float(context.args[0])
        currency = context.args[1].upper()
        
        if currency not in ['USDT', 'TRX']:
            await update.message.reply_text(
                "❌ 不支持的货币类型！\n\n"
                "支持的货币：USDT、TRX"
            )
            return
        
        if amount <= 0:
            await update.message.reply_text("❌ 金额必须大于0！")
            return
        
        # 创建支付订单
        order = umpay.create_payment_order(amount, currency)
        
        order_text = (
            f"💳 支付订单已创建\n\n"
            f"📋 订单ID：`{order['order_id']}`\n"
            f"💰 金额：{order['amount']} {order['currency']}\n"
            f"📍 收款地址：`{order['receiving_address']}`\n"
            f"⏰ 有效期：1小时\n\n"
            f"请向上述地址转账 {order['amount']} {order['currency']}\n"
            f"转账完成后使用 /check {order['order_id']} 查询状态"
        )
        
        await update.message.reply_text(order_text, parse_mode='Markdown')
        
    except ValueError:
        await update.message.reply_text("❌ 金额格式错误！请输入有效的数字。")
    except Exception as e:
        logger.error(f"创建支付订单时出错: {e}")
        await update.message.reply_text("❌ 创建支付订单失败，请稍后重试。")

async def check_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check payment status."""
    try:
        if len(context.args) < 1:
            await update.message.reply_text(
                "❌ 用法错误！\n\n"
                "正确用法：/check <订单ID>\n"
                "示例：/check 12345678-1234-1234-1234-123456789012"
            )
            return
        
        order_id = context.args[0]
        
        # 检查支付状态
        result = umpay.check_payment_status(order_id)
        
        if 'error' in result:
            await update.message.reply_text(f"❌ {result['error']}")
            return
        
        status_emoji = {
            'pending': '⏳',
            'completed': '✅',
            'expired': '❌'
        }
        
        status_text = {
            'pending': '等待支付',
            'completed': '支付完成',
            'expired': '订单过期'
        }
        
        emoji = status_emoji.get(result['status'], '❓')
        status = status_text.get(result['status'], '未知状态')
        
        order_text = (
            f"{emoji} 订单状态查询\n\n"
            f"📋 订单ID：`{result['order_id']}`\n"
            f"💰 金额：{result['amount']} {result['currency']}\n"
            f"📊 状态：{status}\n"
        )
        
        if result['status'] == 'completed':
            completed_time = result.get('completed_at', 0)
            completed_str = datetime.datetime.fromtimestamp(completed_time).strftime('%Y-%m-%d %H:%M:%S')
            order_text += f"✅ 完成时间：{completed_str}\n"
        elif result['status'] == 'pending':
            order_text += f"📍 收款地址：`{result['receiving_address']}`\n"
            expires_time = result.get('expires_at', 0)
            expires_str = datetime.datetime.fromtimestamp(expires_time).strftime('%Y-%m-%d %H:%M:%S')
            order_text += f"⏰ 过期时间：{expires_str}\n"
        
        await update.message.reply_text(order_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"查询支付状态时出错: {e}")
        await update.message.reply_text("❌ 查询支付状态失败，请稍后重试。")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help information."""
    help_text = (
        "🤖 UMBot 帮助信息\n\n"
        "📋 基本命令：\n"
        "/start - 显示欢迎信息\n"
        "/help - 显示此帮助信息\n\n"
        "👤 会员系统：\n"
        "/register - 注册成为会员\n"
        "/member - 查看会员信息\n"
        "/recharge <金额> - 充值余额\n"
        "/rechargecenter - 充值中心\n\n"
        "💰 支付功能：\n"
        "/pay <金额> <货币> - 创建支付订单\n"
        "  示例：/pay 10 USDT\n"
        "  示例：/pay 100 TRX\n\n"
        "/check <订单ID> - 查询支付状态\n"
        "  示例：/check 12345678-1234-1234-1234-123456789012\n\n"
        "/checkorder <订单ID> <支付订单ID> - 查询订单详情\n"
        "/checkbepusdt <订单ID> - 查询BEpusdt订单\n\n"
        "🛍️ 商城功能：\n"
        "/shop - 浏览商品\n"
        "/buy <商品ID> <支付方式> - 购买商品\n"
        "/search <关键词> - 搜索商品\n"
        "/myorders - 我的订单\n\n"
        "💎 会员权益：\n"
        "• 青铜会员：基础服务\n"
        "• 白银会员：5%折扣 + 2%充值赠送\n"
        "• 黄金会员：10%折扣 + 5%充值赠送\n"
        "• 铂金会员：15%折扣 + 8%充值赠送\n"
        "• 钻石会员：20%折扣 + 10%充值赠送\n\n"
        "🎁 充值活动：\n"
        "• 首充双倍：首次充值100%赠送\n"
        "• 充值赠送：满100元赠送10%\n"
        "• VIP优惠：黄金以上会员享5%折扣\n\n"
        "💡 使用提示：\n"
        "• 支持USDT(TRC20)、TRX和BEpusdt支付\n"
        "• 订单有效期为1小时\n"
        "• 推荐好友注册可获得奖励\n"
        "• 如有问题请联系客服\n"
        "⚡ 基于波场(TRON)网络，转账快速且费用低廉"
    )
    await update.message.reply_text(help_text)

async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show shop with products."""
    user = update.effective_user
    if not user:
        return
    
    try:
        # 获取可用商品
        products = shop.get_available_products()
        
        if not products:
            await update.message.reply_text(
                "🛍️ 商城暂时没有可用商品\n\n"
                "请稍后再来查看！"
            )
            return
        
        # 获取用户折扣信息
        discount_info = shop.get_user_discount_info(user.id)
        member = member_system.get_user(user.id)
        
        # 构建商品列表消息
        shop_text = "🛍️ **UMBot 商城** 🛍️\n\n"
        
        # 显示会员信息
        if member:
            shop_text += f"👤 {discount_info['level_emoji']} {discount_info['level_name']}\n"
            shop_text += f"💰 余额：¥{member.balance:.2f}\n"
            if discount_info['discount_rate'] > 0:
                shop_text += f"🎁 专享折扣：{discount_info['discount_rate']*100:.0f}% OFF\n"
            shop_text += "\n"
        else:
            shop_text += "💡 使用 /register 注册会员享受更多优惠\n\n"
        
        shop_text += "📦 **可购买商品：**\n\n"
        
        # 创建内联键盘
        keyboard = []
        
        for i, product in enumerate(products[:10], 1):  # 限制显示前10个商品
            original_price = float(product.price)
            
            shop_text += f"{i}. **{product.name}**\n"
            
            # 显示价格和折扣
            if discount_info['discount_rate'] > 0 and member:
                discounted_price = original_price * (1 - discount_info['discount_rate'])
                shop_text += f"   💰 原价：¥{original_price:.2f}\n"
                shop_text += f"   🎁 会员价：¥{discounted_price:.2f}\n"
            else:
                shop_text += f"   💰 价格：¥{original_price:.2f}\n"
            
            shop_text += f"   📝 {product.description}\n"
            shop_text += f"   📦 库存：{product.stock}\n\n"
            
            # 添加购买按钮
            keyboard.append([
                InlineKeyboardButton(
                    f"💳 购买 {product.name}",
                    callback_data=f"buy_{product.id}"
                )
            ])
        
        # 添加其他功能按钮
        keyboard.extend([
            [InlineKeyboardButton("🔍 搜索商品", callback_data="search_products")],
            [InlineKeyboardButton("📋 我的订单", callback_data="my_orders")],
            [InlineKeyboardButton("❓ 购买帮助", callback_data="buy_help")]
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # 显示可用支付方式
        available_methods = shop.get_available_payment_methods()
        methods_text = ", ".join(available_methods)
        
        shop_text += "💡 **使用说明：**\n"
        shop_text += "• 点击商品下方的购买按钮开始购买\n"
        shop_text += f"• 支持支付方式：{methods_text}\n"
        shop_text += "• 支付完成后自动发货\n"
        
        await update.message.reply_text(
            shop_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"显示商城时出错: {e}")
        await update.message.reply_text("❌ 加载商城失败，请稍后重试。")

async def buy_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle product purchase."""
    user = update.effective_user
    if not user:
        return
    
    try:
        if len(context.args) < 2:
            # 显示可用的支付方式
            available_methods = shop.get_available_payment_methods()
            methods_text = ", ".join(available_methods)
            
            await update.message.reply_text(
                f"❌ 使用格式：/buy <商品ID> <支付方式>\n"
                f"支付方式：{methods_text}"
            )
            return
        
        product_id = context.args[0]
        payment_method = context.args[1].lower()
        
        # 验证支付方式
        available_methods = [method.lower() for method in shop.get_available_payment_methods()]
        if payment_method not in available_methods:
            methods_text = ", ".join(shop.get_available_payment_methods())
            await update.message.reply_text(
                f"❌ 不支持的支付方式\n"
                f"支持的支付方式：{methods_text}"
            )
            return
        
        # 获取商品信息和用户折扣信息
        product = shop.get_product(product_id)
        if not product:
            await update.message.reply_text("❌ 商品不存在")
            return
        
        discount_info = shop.get_user_discount_info(user.id)
        
        result = shop.create_order(user.id, product_id, payment_method)
        
        if not result:
            if payment_method == 'balance':
                member = member_system.get_user(user.id)
                if not member:
                    await update.message.reply_text("❌ 您还不是会员，请先使用 /register 注册")
                else:
                    await update.message.reply_text(f"❌ 余额不足\n当前余额：¥{member.balance:.2f}\n商品价格：¥{product.price:.2f}")
            else:
                await update.message.reply_text("❌ 创建订单失败，商品可能不存在或库存不足")
            return
        
        order = result['order']
        payment_order = result.get('payment_order')
        
        # 构建订单信息
        order_text = f"""📋 订单创建成功

🆔 订单ID：`{order.id}`
🛍️ 商品：{product.name}
💰 原价：¥{product.price:.2f}"""
        
        # 显示会员折扣信息
        if discount_info['discount_rate'] > 0:
            discount_amount = float(product.price) * discount_info['discount_rate']
            order_text += f"\n🎁 {discount_info['level_emoji']} {discount_info['level_name']}折扣：-¥{discount_amount:.2f}"
        
        order_text += f"\n💳 实付金额：¥{order.total_amount:.2f}"
        order_text += f"\n💳 支付方式：{payment_method.upper()}"
        order_text += f"\n⏰ 创建时间：{order.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        
        # 余额支付已完成
        if payment_method == 'balance' and payment_order.get('status') == 'completed':
            order_text += "\n\n✅ 余额支付成功，订单已完成！"
            await update.message.reply_text(order_text, parse_mode='Markdown')
            return
        
        if not payment_order:
            await update.message.reply_text("❌ 创建支付订单失败")
            return
        
        if payment_method == 'bepusdt':
            # BEpusdt支付
            if 'pay_url' in payment_order:
                order_text += f"\n💳 支付链接：{payment_order['pay_url']}"
                keyboard = [
                    [InlineKeyboardButton("💳 去支付", url=payment_order['pay_url'])],
                    [InlineKeyboardButton("🔍 查询状态", callback_data=f"check_order_{order.id}")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(order_text, parse_mode='Markdown', reply_markup=reply_markup)
            else:
                await update.message.reply_text(f"{order_text}\n❌ 获取支付链接失败", parse_mode='Markdown')
        else:
            # UMPay支付（USDT/TRX）
            if payment_order.get('status') == 'success':
                order_text += f"\n💰 支付金额：{payment_order.get('amount', 'N/A')} {payment_method.upper()}"
                order_text += f"\n📍 收款地址：`{payment_order.get('address', 'N/A')}`"
                order_text += f"\n⏰ 订单有效期：1小时"
                
                keyboard = [
                    [InlineKeyboardButton("🔍 查询状态", callback_data=f"check_order_{order.id}")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(order_text, parse_mode='Markdown', reply_markup=reply_markup)
            else:
                await update.message.reply_text(f"{order_text}\n❌ 创建支付订单失败", parse_mode='Markdown')
    
    except Exception as e:
        logger.error(f"购买商品异常: {e}")
        await update.message.reply_text("❌ 系统错误，请稍后重试")

async def check_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check order status."""
    try:
        if len(context.args) < 2:
            await update.message.reply_text(
                "❌ 用法错误！\n\n"
                "正确用法：/checkorder <订单ID> <支付订单ID>\n"
                "示例：/checkorder 12345678-1234-1234-1234-123456789012 87654321-4321-4321-4321-210987654321"
            )
            return
        
        order_id = context.args[0]
        payment_order_id = context.args[1]
        
        # 检查订单状态
        result = shop.check_order_payment(order_id, payment_order_id)
        
        if 'error' in result:
            await update.message.reply_text(f"❌ {result['error']}")
            return
        
        order = result['order']
        payment_status = result['payment_status']
        
        status_emoji = {
            'pending': '⏳',
            'completed': '✅',
            'expired': '❌'
        }
        
        status_text = {
            'pending': '等待支付',
            'completed': '支付完成',
            'expired': '订单过期'
        }
        
        emoji = status_emoji.get(payment_status['status'], '❓')
        status = status_text.get(payment_status['status'], '未知状态')
        
        order_text = (
            f"{emoji} **订单状态查询**\n\n"
            f"📋 **订单ID：** `{order.id}`\n"
            f"📦 **商品：** {order.products[0].name}\n"
            f"💰 **金额：** {order.total_amount} {order.payment_method.value.upper()}\n"
            f"📊 **状态：** {status}\n"
        )
        
        if payment_status['status'] == 'completed':
            completed_time = payment_status.get('completed_at', 0)
            completed_str = datetime.datetime.fromtimestamp(completed_time).strftime('%Y-%m-%d %H:%M:%S')
            order_text += f"✅ **完成时间：** {completed_str}\n"
            order_text += f"🎉 **订单已完成，商品已发货！**\n"
        elif payment_status['status'] == 'pending':
            order_text += f"📍 **收款地址：** `{payment_status['receiving_address']}`\n"
            expires_time = payment_status.get('expires_at', 0)
            expires_str = datetime.datetime.fromtimestamp(expires_time).strftime('%Y-%m-%d %H:%M:%S')
            order_text += f"⏰ **过期时间：** {expires_str}\n"
        elif payment_status['status'] == 'expired':
            order_text += f"❌ **订单已过期，库存已恢复**\n"
        
        await update.message.reply_text(order_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"查询订单状态时出错: {e}")
        await update.message.reply_text("❌ 查询订单状态失败，请稍后重试。")

async def search_products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Search products."""
    try:
        if len(context.args) < 1:
            await update.message.reply_text(
                "❌ 用法错误！\n\n"
                "正确用法：/search <关键词>\n"
                "示例：/search 游戏"
            )
            return
        
        keyword = ' '.join(context.args)
        products = shop.search_products(keyword)
        
        if not products:
            await update.message.reply_text(
                f"🔍 没有找到包含 '{keyword}' 的商品\n\n"
                "请尝试其他关键词或使用 /shop 查看所有商品"
            )
            return
        
        search_text = f"🔍 **搜索结果：'{keyword}'**\n\n"
        
        for i, product in enumerate(products, 1):
            search_text += (
                f"{i}. **{product.name}**\n"
                f"   💰 价格：{product.price} USDT\n"
                f"   📝 {product.description}\n"
                f"   📦 库存：{product.stock}\n"
                f"   🛒 购买：/buy {product.id} USDT\n\n"
            )
        
        await update.message.reply_text(search_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"搜索商品时出错: {e}")
        await update.message.reply_text("❌ 搜索失败，请稍后重试。")

async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user's orders."""
    try:
        user_id = str(update.effective_user.id)
        orders = shop.get_user_orders(user_id)
        
        if not orders:
            await update.message.reply_text(
                "📋 您还没有任何订单\n\n"
                "使用 /shop 开始购物吧！"
            )
            return
        
        orders_text = "📋 **我的订单**\n\n"
        
        for order in orders[-10:]:  # 显示最近10个订单
            status_emoji = {
                'PENDING': '⏳',
                'COMPLETED': '✅',
                'FAILED': '❌'
            }
            
            emoji = status_emoji.get(order.payment_status.name, '❓')
            product_name = order.products[0].name if order.products else '未知商品'
            
            orders_text += (
                f"{emoji} **{product_name}**\n"
                f"   💰 {order.total_amount} {order.payment_method.value.upper()}\n"
                f"   📅 {order.created_at.strftime('%Y-%m-%d %H:%M')}\n"
                f"   📋 `{order.id}`\n\n"
            )
        
        await update.message.reply_text(orders_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"查询用户订单时出错: {e}")
        await update.message.reply_text("❌ 查询订单失败，请稍后重试。")

async def check_bepusdt_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check BEpusdt order status."""
    try:
        if len(context.args) < 1:
            await update.message.reply_text(
                "❌ 用法错误！\n\n"
                "正确用法：/checkbepusdt <订单ID>\n"
                "示例：/checkbepusdt 12345678-1234-1234-1234-123456789012"
            )
            return
        
        order_id = context.args[0]
        
        # 检查BEpusdt订单状态
        result = shop.check_bepusdt_payment(order_id)
        
        if 'error' in result:
            await update.message.reply_text(f"❌ {result['error']}")
            return
        
        # 获取本地订单信息
        order = shop.orders.get(order_id)
        if not order:
            await update.message.reply_text("❌ 订单不存在！")
            return
        
        status_emoji = {
            'pending': '⏳',
            'paid': '✅',
            'expired': '❌',
            'unknown': '❓'
        }
        
        status_text = {
            'pending': '等待支付',
            'paid': '支付完成',
            'expired': '订单过期',
            'unknown': '未知状态'
        }
        
        status = result.get('status', 'unknown')
        emoji = status_emoji.get(status, '❓')
        status_name = status_text.get(status, '未知状态')
        
        order_text = (
            f"{emoji} **BEpusdt订单状态查询**\n\n"
            f"📋 **订单ID：** `{order.id}`\n"
            f"📦 **商品：** {order.products[0].name}\n"
            f"💰 **金额：** {result.get('amount', order.total_amount)} {result.get('currency', 'CNY')}\n"
            f"📊 **状态：** {status_name}\n"
        )
        
        if status == 'paid':
            paid_time = result.get('paid_at')
            if paid_time:
                order_text += f"✅ **支付时间：** {paid_time}\n"
            order_text += f"🎉 **订单已完成，商品已发货！**\n"
        elif status == 'pending':
            expires_time = result.get('expires_at')
            if expires_time:
                order_text += f"⏰ **过期时间：** {expires_time}\n"
            order_text += f"💡 **请及时完成支付**\n"
        elif status == 'expired':
            order_text += f"❌ **订单已过期，库存已恢复**\n"
        
        await update.message.reply_text(order_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"查询BEpusdt订单状态时出错: {e}")
        await update.message.reply_text("❌ 查询BEpusdt订单状态失败，请稍后重试。")