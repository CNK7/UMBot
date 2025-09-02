from typing import Dict, List, Optional
from decimal import Decimal
import uuid
from datetime import datetime
from .models import Product, Order, PaymentMethod, PaymentStatus
from payments.umpay import UMPay
from payments.bepusdt import BEpusdt
from config import BEPUSDT_API_URL, BEPUSDT_APP_ID, BEPUSDT_APP_SECRET, BEPUSDT_NOTIFY_URL
from store.member import MemberSystem

class Shop:
    """商城管理系统"""
    
    def __init__(self, member_system: Optional[MemberSystem] = None):
        self.products: Dict[str, Product] = {}
        self.orders: Dict[str, Order] = {}
        self.member_system = member_system or MemberSystem()
        self.umpay = UMPay(network='mainnet')
        
        # 初始化BEpusdt（如果配置了）
        if BEPUSDT_API_URL and BEPUSDT_APP_ID and BEPUSDT_APP_SECRET:
            self.bepusdt = BEpusdt(BEPUSDT_API_URL, BEPUSDT_APP_ID, BEPUSDT_APP_SECRET)
        else:
            self.bepusdt = None
            
        # 初始化一些示例商品
        self._init_sample_products()
    
    def _init_sample_products(self):
        """初始化示例商品"""
        sample_products = [
            Product(
                id="prod_001",
                name="🎮 Steam游戏激活码",
                description="热门游戏激活码，支持全球激活",
                price=Decimal('15.99'),
                stock=50
            ),
            Product(
                id="prod_002",
                name="📱 手机充值卡",
                description="支持移动、联通、电信充值",
                price=Decimal('10.00'),
                stock=100
            ),
            Product(
                id="prod_003",
                name="🎵 音乐会员月卡",
                description="QQ音乐/网易云音乐会员",
                price=Decimal('8.00'),
                stock=30
            ),
            Product(
                id="prod_004",
                name="📺 视频会员季卡",
                description="爱奇艺/腾讯视频/优酷会员",
                price=Decimal('25.00'),
                stock=20
            ),
            Product(
                id="prod_005",
                name="☁️ 云存储空间",
                description="100GB云存储空间，1年有效期",
                price=Decimal('12.00'),
                stock=80
            )
        ]
        
        for product in sample_products:
            self.products[product.id] = product
    
    def get_all_products(self) -> List[Product]:
        """获取所有商品"""
        return list(self.products.values())
    
    def get_product(self, product_id: str) -> Optional[Product]:
        """根据ID获取商品"""
        return self.products.get(product_id)
    
    def get_available_products(self) -> List[Product]:
        """获取有库存的商品"""
        return [product for product in self.products.values() if product.stock > 0]
    
    def create_order(self, user_id: str, product_id: str, payment_method: str) -> Optional[Dict]:
        """创建订单
        
        Args:
            user_id: 用户ID
            product_id: 商品ID
            payment_method: 支付方式 ('USDT', 'TRX', 或 'balance')
            
        Returns:
            订单信息字典或None（如果失败）
        """
        product = self.get_product(product_id)
        if not product:
            return None
        
        if product.stock <= 0:
            return None
        
        # 计算原价
        original_amount = product.price
        total_amount = original_amount
        
        # 应用会员折扣
        discount_amount = Decimal('0.0')
        if self.member_system:
            user = self.member_system.get_user(int(user_id))
            if user:
                benefits = user.get_level_benefits()
                discount_rate = benefits.get('discount', 0.0)
                if discount_rate > 0:
                    discount_amount = original_amount * Decimal(str(discount_rate))
                    total_amount = original_amount - discount_amount
        
        # 如果是余额支付，检查余额是否充足
        if payment_method.lower() == 'balance':
            if not self.can_use_balance_payment(int(user_id), float(total_amount)):
                return None
        
        # 创建订单
        order_id = str(uuid.uuid4())
        
        try:
            if payment_method.lower() == 'balance':
                payment_method_enum = PaymentMethod.USDT  # 使用USDT作为默认枚举值
            else:
                payment_method_enum = PaymentMethod(payment_method.lower())
        except ValueError:
            return None
        
        order = Order(
            id=order_id,
            user_id=user_id,
            products=[product],
            total_amount=total_amount,
            payment_method=payment_method_enum,
            payment_status=PaymentStatus.PENDING
        )
        
        # 添加折扣信息到订单备注
        if discount_amount > 0:
            order.notes = f"会员折扣：-¥{discount_amount:.2f}"
        
        # 如果是余额支付，直接完成支付
        if payment_method.lower() == 'balance':
            success = self.member_system.deduct_balance(
                int(user_id),
                float(total_amount),
                "purchase",
                f"购买商品：{product.name}",
                order_id
            )
            if success:
                order.payment_status = PaymentStatus.COMPLETED
                order.completed_at = datetime.now()
                # 减少库存
                product.stock -= 1
                # 存储订单
                self.orders[order_id] = order
                # 处理发货
                self._process_order_fulfillment(order)
                return {
                    'order': order,
                    'payment_order': {'status': 'completed', 'method': 'balance'}
                }
            else:
                return None
        
        # 创建支付订单
        payment_order = self.umpay.create_payment_order(
            amount=float(total_amount),
            currency=payment_method.upper()
        )
        
        # 存储订单
        self.orders[order_id] = order
        
        # 减少库存
        product.stock -= 1
        
        return {
            'order': order,
            'payment_order': payment_order
        }
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """获取订单"""
        return self.orders.get(order_id)
    
    def check_order_payment(self, order_id: str, payment_order_id: str) -> Dict:
        """检查订单支付状态
        
        Args:
            order_id: 商城订单ID
            payment_order_id: 支付订单ID
            
        Returns:
            支付状态信息
        """
        order = self.get_order(order_id)
        if not order:
            return {'error': '订单不存在'}
        
        # 检查支付状态
        payment_result = self.umpay.check_payment_status(payment_order_id)
        
        if 'error' in payment_result:
            return payment_result
        
        # 更新订单状态
        if payment_result['status'] == 'completed' and order.payment_status == PaymentStatus.PENDING:
            order.payment_status = PaymentStatus.COMPLETED
            order.completed_at = datetime.now()
            
            # 这里可以添加发货逻辑
            self._process_order_fulfillment(order)
        
        elif payment_result['status'] == 'expired':
            order.payment_status = PaymentStatus.FAILED
            # 恢复库存
            for product in order.products:
                if product.id in self.products:
                    self.products[product.id].stock += 1
        
        return {
            'order': order,
            'payment_status': payment_result
        }
    
    def _process_order_fulfillment(self, order: Order):
        """处理订单发货
        
        Args:
            order: 已完成支付的订单
        """
        # 这里可以实现具体的发货逻辑
        # 例如：发送激活码、充值卡号等
        print(f"订单 {order.id} 已完成支付，开始发货...")
        
        # 示例：为不同商品类型生成不同的交付内容
        for product in order.products:
            if "激活码" in product.name:
                # 生成游戏激活码
                activation_code = self._generate_activation_code()
                print(f"游戏激活码: {activation_code}")
            elif "充值卡" in product.name:
                # 生成充值卡号和密码
                card_number, card_password = self._generate_recharge_card()
                print(f"充值卡号: {card_number}, 密码: {card_password}")
            elif "会员" in product.name:
                # 生成会员兑换码
                member_code = self._generate_member_code()
                print(f"会员兑换码: {member_code}")
    
    def _generate_activation_code(self) -> str:
        """生成游戏激活码"""
        import random
        import string
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    
    def _generate_recharge_card(self) -> tuple:
        """生成充值卡号和密码"""
        import random
        card_number = ''.join([str(random.randint(0, 9)) for _ in range(16)])
        card_password = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        return card_number, card_password
    
    def _generate_member_code(self) -> str:
        """生成会员兑换码"""
        import random
        import string
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    
    def get_user_orders(self, user_id: str) -> List[Order]:
        """获取用户的所有订单"""
        return [order for order in self.orders.values() if order.user_id == user_id]
    
    def can_use_balance_payment(self, user_id: int, amount: float) -> bool:
        """检查用户是否可以使用余额支付"""
        if not self.member_system:
            return False
        
        user = self.member_system.get_user(user_id)
        return user is not None and user.balance >= amount
    
    def get_user_discount_info(self, user_id: int) -> Dict:
        """获取用户折扣信息"""
        if not self.member_system:
            return {"discount_rate": 0.0, "level_name": "非会员", "level_emoji": ""}
        
        user = self.member_system.get_user(user_id)
        if not user:
            return {"discount_rate": 0.0, "level_name": "非会员", "level_emoji": ""}
        
        benefits = user.get_level_benefits()
        return {
            "discount_rate": benefits.get('discount', 0.0),
            "level_name": benefits.get('name', ''),
            "level_emoji": benefits.get('emoji', '')
        }
    
    def search_products(self, keyword: str) -> List[Product]:
        """搜索商品
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的商品列表
        """
        keyword = keyword.lower()
        results = []
        
        for product in self.products.values():
            if (keyword in product.name.lower() or 
                keyword in product.description.lower()):
                results.append(product)
        
        return results
    
    def create_bepusdt_order(self, user_id: str, product_id: str, payment_method: str) -> Optional[Dict]:
        """
        使用BEpusdt创建支付订单
        
        Args:
            user_id: 用户ID
            product_id: 商品ID
            payment_method: 支付方式 (USDT_TRC20, TRX, USDT_ERC20等)
            
        Returns:
            订单创建结果
        """
        if not self.bepusdt:
            return None
            
        try:
            # 获取商品信息
            product = self.get_product(product_id)
            if not product or product.stock <= 0:
                return None
            
            # 创建订单ID
            order_id = str(uuid.uuid4())
            
            # 映射支付方式
            trade_type_mapping = {
                'USDT_TRC20': 'usdt.trc20',
                'TRX': 'tron.trx',
                'USDT_ERC20': 'usdt.erc20',
                'USDT_BSC': 'usdt.bsc',
                'USDT_POLYGON': 'usdt.polygon'
            }
            
            trade_type = trade_type_mapping.get(payment_method, 'usdt.trc20')
            
            # 创建BEpusdt订单
            result = self.bepusdt.create_order(
                order_id=order_id,
                amount=product.price,  # 假设价格是CNY
                trade_type=trade_type,
                notify_url=BEPUSDT_NOTIFY_URL,
                timeout=1800  # 30分钟
            )
            
            if not result.get('success'):
                return None
            
            # 创建本地订单
            payment_method_enum = PaymentMethod.USDT if 'usdt' in trade_type else PaymentMethod.TRX
            
            order = Order(
                id=order_id,
                user_id=user_id,
                products=[product],
                total_amount=product.price,
                payment_method=payment_method_enum,
                payment_status=PaymentStatus.PENDING
            )
            
            # 减少库存
            product.stock -= 1
            
            # 保存订单
            self.orders[order_id] = order
            
            return {
                'order': order,
                'payment_data': result['data']
            }
            
        except Exception as e:
            print(f"创建BEpusdt订单失败: {e}")
            return None
    
    def check_bepusdt_payment(self, order_id: str) -> Dict:
        """
        检查BEpusdt订单支付状态
        
        Args:
            order_id: 订单ID
            
        Returns:
            支付状态信息
        """
        if not self.bepusdt:
            return {'error': 'BEpusdt未配置'}
            
        try:
            # 查询BEpusdt订单状态
            result = self.bepusdt.query_order(order_id)
            
            if not result.get('success'):
                return {'error': result.get('message', '查询失败')}
            
            order_data = result['data']
            
            # 更新本地订单状态
            if order_id in self.orders:
                order = self.orders[order_id]
                
                # 根据BEpusdt状态更新订单
                if order_data.get('status') == 'paid':
                    order.payment_status = PaymentStatus.COMPLETED
                    order.completed_at = datetime.now()
                    # 处理发货
                    self._process_order_fulfillment(order)
                elif order_data.get('status') == 'expired':
                    order.payment_status = PaymentStatus.FAILED
                    # 恢复库存
                    for product in order.products:
                        if product.id in self.products:
                            self.products[product.id].stock += 1
            
            return {
                'status': order_data.get('status', 'unknown'),
                'amount': order_data.get('amount'),
                'currency': order_data.get('currency'),
                'created_at': order_data.get('created_at'),
                'paid_at': order_data.get('paid_at'),
                'expires_at': order_data.get('expires_at')
            }
            
        except Exception as e:
            print(f"检查BEpusdt支付状态失败: {e}")
            return {'error': f'查询异常: {str(e)}'}
    
    def get_supported_payment_methods(self) -> List[str]:
        """
        获取支持的支付方式列表
        
        Returns:
            支持的支付方式列表
        """
        methods = ['USDT', 'TRX']  # UMPay支持的方式
        
        # 添加余额支付
        if self.member_system:
            methods.append('balance')
        
        if self.bepusdt:
            # 添加BEpusdt支持的方式
            bepusdt_methods = [
                'USDT_TRC20',
                'USDT_ERC20', 
                'USDT_BSC',
                'USDT_POLYGON',
                'TRX'
            ]
            methods.extend(bepusdt_methods)
        
        return list(set(methods))  # 去重
    
    def format_payment_amount(self, cny_amount: float, payment_method: str) -> str:
        """
        格式化支付金额显示
        
        Args:
            cny_amount: 人民币金额
            payment_method: 支付方式
            
        Returns:
            格式化后的金额字符串
        """
        if self.bepusdt and payment_method in ['USDT_TRC20', 'USDT_ERC20', 'USDT_BSC', 'USDT_POLYGON']:
            return self.bepusdt.format_amount_for_display(cny_amount, payment_method.lower().replace('_', '.'))
        else:
            # 使用UMPay或默认显示
            return f"{cny_amount:.2f} CNY"
    
    def deliver_order(self, order):
        """自动发货"""
        try:
            # 更新订单状态为已发货
            order.status = 'delivered'
            
            # 这里可以添加具体的发货逻辑
            # 例如：发送商品信息、激活码、下载链接等
            
            # 示例：如果是虚拟商品，可以在这里生成激活码
            delivery_info = []
            for product in order.products:
                if hasattr(product, 'category') and product.category == 'digital':
                    # 生成虚拟商品的激活码或下载链接
                    activation_code = f"ACT-{order.id[:8]}-{product.id}"
                    delivery_info.append({
                        'product_name': product.name,
                        'activation_code': activation_code,
                        'instructions': '请妥善保管您的激活码'
                    })
                else:
                    # 物理商品的发货信息
                    delivery_info.append({
                        'product_name': product.name,
                        'tracking_number': f"TRK-{order.id[:8]}",
                        'instructions': '商品将在1-3个工作日内发货'
                    })
            
            order.delivery_info = delivery_info
            print(f"订单 {order.id} 发货成功")
            
        except Exception as e:
            print(f"订单 {order.id} 发货失败: {e}")
            raise e