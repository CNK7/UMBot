from flask import Flask, request, jsonify
import logging
from payments.bepusdt import BEpusdt
from store.shop import Shop
from config import BEPUSDT_API_URL, BEPUSDT_APP_ID, BEPUSDT_APP_SECRET

logger = logging.getLogger(__name__)

app = Flask(__name__)
shop = Shop()

# 初始化BEpusdt
bepusdt = None
if BEPUSDT_API_URL and BEPUSDT_APP_ID and BEPUSDT_APP_SECRET:
    bepusdt = BEpusdt(BEPUSDT_API_URL, BEPUSDT_APP_ID, BEPUSDT_APP_SECRET)

@app.route('/webhook/bepusdt', methods=['POST'])
def bepusdt_callback():
    """处理BEpusdt支付回调"""
    try:
        if not bepusdt:
            logger.error("BEpusdt未配置")
            return jsonify({'error': 'BEpusdt not configured'}), 400
        
        # 获取回调数据
        data = request.get_json()
        if not data:
            logger.error("无效的回调数据")
            return jsonify({'error': 'Invalid callback data'}), 400
        
        logger.info(f"收到BEpusdt回调: {data}")
        
        # 验证签名
        if not bepusdt.verify_callback_signature(data):
            logger.error("BEpusdt回调签名验证失败")
            return jsonify({'error': 'Invalid signature'}), 400
        
        # 获取订单信息
        order_id = data.get('order_id')
        status = data.get('status')
        amount = data.get('amount')
        currency = data.get('currency')
        tx_hash = data.get('tx_hash')
        
        if not order_id:
            logger.error("回调数据缺少订单ID")
            return jsonify({'error': 'Missing order_id'}), 400
        
        # 查找本地订单
        order = shop.orders.get(order_id)
        if not order:
            logger.error(f"订单不存在: {order_id}")
            return jsonify({'error': 'Order not found'}), 404
        
        # 处理支付状态
        if status == 'paid':
            # 支付成功，更新订单状态
            order.status = 'paid'
            order.payment_info = {
                'method': 'bepusdt',
                'amount': amount,
                'currency': currency,
                'tx_hash': tx_hash,
                'paid_at': data.get('paid_at')
            }
            
            # 自动发货
            try:
                shop.deliver_order(order)
                logger.info(f"订单 {order_id} 支付成功并已发货")
            except Exception as e:
                logger.error(f"订单 {order_id} 发货失败: {e}")
            
        elif status == 'expired':
            # 订单过期，恢复库存
            order.status = 'expired'
            for product in order.products:
                if product.id in shop.products:
                    shop.products[product.id].stock += 1
            logger.info(f"订单 {order_id} 已过期，库存已恢复")
        
        # 保存订单状态
        shop.orders[order_id] = order
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        logger.error(f"处理BEpusdt回调时出错: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=5000, debug=False)