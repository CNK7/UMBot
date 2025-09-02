import logging
from telegram.ext import Application, CommandHandler
from bot.handlers import start, pay, check_payment, help_command, shop, buy_product, check_order, search_products, my_orders, check_bepusdt_order
from bot.member_handlers import (
    register_member, member_info, recharge_menu, custom_recharge,
    recharge_callback_handler, create_recharge_handler, check_recharge_handler
)
from config import TELEGRAM_TOKEN

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    start_handler = CommandHandler('start', start)
    pay_handler = CommandHandler('pay', pay)
    check_handler = CommandHandler('check', check_payment)
    help_handler = CommandHandler('help', help_command)
    shop_handler = CommandHandler('shop', shop)
    
    application.add_handler(start_handler)
    application.add_handler(pay_handler)
    application.add_handler(check_handler)
    application.add_handler(help_handler)
    application.add_handler(shop_handler)
    application.add_handler(CommandHandler("buy", buy_product))
    application.add_handler(CommandHandler("checkorder", check_order))
    application.add_handler(CommandHandler("search", search_products))
    application.add_handler(CommandHandler("myorders", my_orders))
    application.add_handler(CommandHandler("checkbepusdt", check_bepusdt_order))
    
    # 会员系统命令
    application.add_handler(CommandHandler("register", register_member))
    application.add_handler(CommandHandler("member", member_info))
    application.add_handler(CommandHandler("recharge", custom_recharge))
    application.add_handler(CommandHandler("rechargecenter", recharge_menu))
    
    # 会员系统回调处理器
    application.add_handler(recharge_callback_handler)
    application.add_handler(create_recharge_handler)
    application.add_handler(check_recharge_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
