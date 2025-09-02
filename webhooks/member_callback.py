from flask import Flask, request, jsonify
import hashlib
import hmac
import json
import logging
from datetime import datetime
from store.member import MemberSystem
from payments.umpay import UMPay
from payments.bepusdt import BEpusdt
from config import UMPAY_SECRET_KEY, BEPUSDT_APP_SECRET

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化系统
member_system = MemberSystem()
umpay = UMPay()
bepusdt = BEpusdt()

@app.route('/webhook/member/umpay', methods=['POST'])
def umpay_member_callback():
    """UMPay会员充值回调"""
    try:
        data = request.get_json()
        if not data:
            logger.error("UMPay回调：未收到数据")
            return jsonify({"status": "error", "message": "No data received"}), 400
        
        logger.info(f"UMPay会员充值回调数据: {data}")
        
        # 验证签名
        if not verify_umpay_signature(data):
            logger.error("UMPay回调：签名验证失败")
            return jsonify({"status": "error", "message": "Invalid signature"}), 400
        
        # 获取订单信息
        order_id = data.get('order_id')
        status = data.get('status')
        payment_order_id = data.get('payment_order_id', '')
        
        if not order_id:
            logger.error("UMPay回调：缺少订单ID")
            return jsonify({"status": "error", "message": "Missing order_id"}), 400
        
        # 查找充值记录
        record = member_system.recharge_records.get(order_id)
        if not record:
            logger.error(f"UMPay回调：未找到充值记录 {order_id}")
            return jsonify({"status": "error", "message": "Order not found"}), 404
        
        # 处理支付成功
        if status == 'paid' and record.status == 'pending':
            success = member_system.complete_recharge(order_id, payment_order_id)
            if success:
                logger.info(f"UMPay会员充值成功: {order_id}, 用户: {record.user_id}, 金额: {record.amount}")
                
                # 发送通知给用户（这里需要集成Telegram Bot API）
                send_recharge_success_notification(record)
                
                return jsonify({"status": "success", "message": "Payment processed"})
            else:
                logger.error(f"UMPay会员充值处理失败: {order_id}")
                return jsonify({"status": "error", "message": "Failed to process payment"}), 500
        
        # 处理支付失败或过期
        elif status in ['failed', 'expired']:
            record.status = status
            logger.info(f"UMPay会员充值{status}: {order_id}")
            return jsonify({"status": "success", "message": f"Order {status}"})
        
        else:
            logger.warning(f"UMPay回调：未处理的状态 {status} for order {order_id}")
            return jsonify({"status": "success", "message": "Status noted"})
    
    except Exception as e:
        logger.error(f"UMPay会员充值回调处理异常: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500

@app.route('/webhook/member/bepusdt', methods=['POST'])
def bepusdt_member_callback():
    """BEpusdt会员充值回调"""
    try:
        data = request.get_json()
        if not data:
            logger.error("BEpusdt回调：未收到数据")
            return jsonify({"status": "error", "message": "No data received"}), 400
        
        logger.info(f"BEpusdt会员充值回调数据: {data}")
        
        # 验证签名
        if not verify_bepusdt_signature(data):
            logger.error("BEpusdt回调：签名验证失败")
            return jsonify({"status": "error", "message": "Invalid signature"}), 400
        
        # 获取订单信息
        order_id = data.get('order_id')
        status = data.get('status')
        payment_order_id = data.get('payment_order_id', '')
        
        if not order_id:
            logger.error("BEpusdt回调：缺少订单ID")
            return jsonify({"status": "error", "message": "Missing order_id"}), 400
        
        # 查找充值记录
        record = member_system.recharge_records.get(order_id)
        if not record:
            logger.error(f"BEpusdt回调：未找到充值记录 {order_id}")
            return jsonify({"status": "error", "message": "Order not found"}), 404
        
        # 处理支付成功
        if status == 'paid' and record.status == 'pending':
            success = member_system.complete_recharge(order_id, payment_order_id)
            if success:
                logger.info(f"BEpusdt会员充值成功: {order_id}, 用户: {record.user_id}, 金额: {record.amount}")
                
                # 发送通知给用户
                send_recharge_success_notification(record)
                
                return jsonify({"status": "success", "message": "Payment processed"})
            else:
                logger.error(f"BEpusdt会员充值处理失败: {order_id}")
                return jsonify({"status": "error", "message": "Failed to process payment"}), 500
        
        # 处理支付失败或过期
        elif status in ['failed', 'expired']:
            record.status = status
            logger.info(f"BEpusdt会员充值{status}: {order_id}")
            return jsonify({"status": "success", "message": f"Order {status}"})
        
        else:
            logger.warning(f"BEpusdt回调：未处理的状态 {status} for order {order_id}")
            return jsonify({"status": "success", "message": "Status noted"})
    
    except Exception as e:
        logger.error(f"BEpusdt会员充值回调处理异常: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500

def verify_umpay_signature(data):
    """验证UMPay签名"""
    try:
        received_signature = data.pop('signature', '')
        if not received_signature:
            return False
        
        # 构建签名字符串
        sorted_params = sorted(data.items())
        sign_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
        sign_string += f"&key={UMPAY_SECRET_KEY}"
        
        # 计算签名
        calculated_signature = hashlib.md5(sign_string.encode()).hexdigest().upper()
        
        return hmac.compare_digest(received_signature.upper(), calculated_signature)
    
    except Exception as e:
        logger.error(f"UMPay签名验证异常: {e}")
        return False

def verify_bepusdt_signature(data):
    """验证BEpusdt签名"""
    try:
        received_signature = data.pop('signature', '')
        if not received_signature:
            return False
        
        # 构建签名字符串
        sorted_params = sorted(data.items())
        sign_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
        sign_string += f"&key={BEPUSDT_APP_SECRET}"
        
        # 计算签名
        calculated_signature = hashlib.sha256(sign_string.encode()).hexdigest()
        
        return hmac.compare_digest(received_signature, calculated_signature)
    
    except Exception as e:
        logger.error(f"BEpusdt签名验证异常: {e}")
        return False

def send_recharge_success_notification(record):
    """发送充值成功通知"""
    try:
        # 这里需要集成Telegram Bot API来发送消息
        # 由于在webhook环境中，我们需要使用HTTP请求而不是直接调用bot
        import requests
        from config import TELEGRAM_TOKEN
        
        user = member_system.get_user(record.user_id)
        if not user:
            return
        
        benefits = user.get_level_benefits()
        
        message = f"""✅ 充值成功通知

💰 充值详情：
• 充值金额：¥{record.amount:.2f}
• 赠送金额：¥{record.bonus_amount:.2f}
• 当前余额：¥{user.balance:.2f}
• 会员等级：{benefits['emoji']} {benefits['name']}

📅 充值时间：{record.paid_at.strftime('%Y-%m-%d %H:%M:%S')}
💳 支付方式：{record.payment_method.upper()}

感谢您的充值！🎉"""
        
        # 发送消息
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": record.user_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            logger.info(f"充值成功通知已发送给用户 {record.user_id}")
        else:
            logger.error(f"发送充值成功通知失败: {response.text}")
    
    except Exception as e:
        logger.error(f"发送充值成功通知异常: {e}")

@app.route('/health/member', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "service": "member_callback",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

@app.route('/stats/member', methods=['GET'])
def member_stats():
    """会员系统统计"""
    try:
        total_users = len(member_system.users)
        total_recharges = len([r for r in member_system.recharge_records.values() if r.status == 'paid'])
        total_amount = sum(r.amount for r in member_system.recharge_records.values() if r.status == 'paid')
        active_activities = len(member_system.get_active_activities())
        
        # 会员等级分布
        level_distribution = {}
        for user in member_system.users.values():
            level = user.level.value
            level_distribution[level] = level_distribution.get(level, 0) + 1
        
        return jsonify({
            "total_users": total_users,
            "total_recharges": total_recharges,
            "total_amount": total_amount,
            "active_activities": active_activities,
            "level_distribution": level_distribution,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"获取会员统计异常: {e}")
        return jsonify({"status": "error", "message": "Failed to get stats"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)