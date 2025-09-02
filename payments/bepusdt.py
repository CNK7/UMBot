import hashlib
import hmac
import json
import time
import uuid
from typing import Dict, Optional, Any
import requests
import logging

logger = logging.getLogger(__name__)

class BEpusdt:
    """BEpusdt 支付系统集成类"""
    
    def __init__(self, api_url: str, app_id: str, app_secret: str):
        """
        初始化 BEpusdt 支付系统
        
        Args:
            api_url: BEpusdt API 基础URL
            app_id: 应用ID
            app_secret: 应用密钥
        """
        self.api_url = api_url.rstrip('/')
        self.app_id = app_id
        self.app_secret = app_secret
        self.session = requests.Session()
        self.session.timeout = 30
        
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """
        生成签名
        
        Args:
            params: 参数字典
            
        Returns:
            签名字符串
        """
        # 按键名排序
        sorted_params = sorted(params.items())
        
        # 构建签名字符串
        sign_str = '&'.join([f"{k}={v}" for k, v in sorted_params if v is not None and v != ''])
        sign_str += f"&key={self.app_secret}"
        
        # 生成MD5签名
        signature = hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()
        
        logger.debug(f"签名字符串: {sign_str}")
        logger.debug(f"生成签名: {signature}")
        
        return signature
    
    def create_order(self, order_id: str, amount: float, trade_type: str = "usdt.trc20", 
                    notify_url: str = None, redirect_url: str = None, 
                    timeout: int = 1800, address: str = None) -> Dict[str, Any]:
        """
        创建支付订单
        
        Args:
            order_id: 商户订单号
            amount: 支付金额（CNY）
            trade_type: 支付类型 (usdt.trc20, tron.trx, usdt.polygon等)
            notify_url: 回调通知地址
            redirect_url: 支付成功跳转地址
            timeout: 超时时间（秒）
            address: 收款地址（可选）
            
        Returns:
            创建订单的响应结果
        """
        try:
            # 构建请求参数
            params = {
                'app_id': self.app_id,
                'order_id': order_id,
                'amount': amount,
                'trade_type': trade_type,
                'timeout': timeout
            }
            
            # 添加可选参数
            if notify_url:
                params['notify_url'] = notify_url
            if redirect_url:
                params['redirect_url'] = redirect_url
            if address:
                params['address'] = address
                
            # 生成签名
            params['signature'] = self._generate_signature(params)
            
            # 发送请求
            url = f"{self.api_url}/api/order/create-order"
            response = self.session.post(url, json=params)
            
            logger.info(f"创建订单请求: {url}")
            logger.debug(f"请求参数: {params}")
            logger.info(f"响应状态: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"创建订单成功: {result}")
                return {
                    'success': True,
                    'data': result
                }
            else:
                logger.error(f"创建订单失败: HTTP {response.status_code}")
                return {
                    'success': False,
                    'error': f"HTTP错误: {response.status_code}",
                    'message': response.text
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"创建订单网络错误: {e}")
            return {
                'success': False,
                'error': '网络请求失败',
                'message': str(e)
            }
        except Exception as e:
            logger.error(f"创建订单异常: {e}")
            return {
                'success': False,
                'error': '系统异常',
                'message': str(e)
            }
    
    def query_order(self, order_id: str) -> Dict[str, Any]:
        """
        查询订单状态
        
        Args:
            order_id: 商户订单号
            
        Returns:
            订单查询结果
        """
        try:
            # 构建请求参数
            params = {
                'app_id': self.app_id,
                'order_id': order_id
            }
            
            # 生成签名
            params['signature'] = self._generate_signature(params)
            
            # 发送请求
            url = f"{self.api_url}/api/order/query-order"
            response = self.session.post(url, json=params)
            
            logger.info(f"查询订单请求: {url}")
            logger.debug(f"请求参数: {params}")
            logger.info(f"响应状态: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"查询订单成功: {result}")
                return {
                    'success': True,
                    'data': result
                }
            else:
                logger.error(f"查询订单失败: HTTP {response.status_code}")
                return {
                    'success': False,
                    'error': f"HTTP错误: {response.status_code}",
                    'message': response.text
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"查询订单网络错误: {e}")
            return {
                'success': False,
                'error': '网络请求失败',
                'message': str(e)
            }
        except Exception as e:
            logger.error(f"查询订单异常: {e}")
            return {
                'success': False,
                'error': '系统异常',
                'message': str(e)
            }
    
    def verify_callback(self, callback_data: Dict[str, Any]) -> bool:
        """
        验证回调签名
        
        Args:
            callback_data: 回调数据
            
        Returns:
            签名验证结果
        """
        try:
            # 提取签名
            received_signature = callback_data.get('signature', '')
            if not received_signature:
                logger.error("回调数据中缺少签名")
                return False
            
            # 移除签名字段
            params = {k: v for k, v in callback_data.items() if k != 'signature'}
            
            # 生成预期签名
            expected_signature = self._generate_signature(params)
            
            # 验证签名
            is_valid = received_signature.upper() == expected_signature.upper()
            
            if is_valid:
                logger.info("回调签名验证成功")
            else:
                logger.error(f"回调签名验证失败: 接收到 {received_signature}, 期望 {expected_signature}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"验证回调签名异常: {e}")
            return False
    
    def get_supported_currencies(self) -> list:
        """
        获取支持的币种列表
        
        Returns:
            支持的币种列表
        """
        return [
            'usdt.trc20',  # USDT (TRC20)
            'tron.trx',    # TRX
            'usdt.polygon', # USDT (Polygon)
            'usdt.erc20',  # USDT (ERC20)
            'usdt.bsc',    # USDT (BSC)
            'usdt.arbitrum', # USDT (Arbitrum)
            'usdc.polygon', # USDC (Polygon)
            'usdc.erc20'   # USDC (ERC20)
        ]
    
    def get_exchange_rate(self, from_currency: str = 'CNY', to_currency: str = 'USDT') -> Optional[float]:
        """
        获取汇率（如果BEpusdt支持）
        
        Args:
            from_currency: 源币种
            to_currency: 目标币种
            
        Returns:
            汇率或None
        """
        try:
            # 构建请求参数
            params = {
                'app_id': self.app_id,
                'from': from_currency,
                'to': to_currency
            }
            
            # 生成签名
            params['signature'] = self._generate_signature(params)
            
            # 发送请求
            url = f"{self.api_url}/api/exchange/rate"
            response = self.session.post(url, json=params)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result.get('data', {}).get('rate')
            
            return None
            
        except Exception as e:
            logger.error(f"获取汇率异常: {e}")
            return None
    
    def format_amount_for_display(self, cny_amount: float, currency: str) -> str:
        """
        格式化显示金额
        
        Args:
            cny_amount: 人民币金额
            currency: 目标币种
            
        Returns:
            格式化后的金额字符串
        """
        if currency in ['usdt.trc20', 'usdt.erc20', 'usdt.bsc', 'usdt.polygon', 'usdt.arbitrum']:
            # USDT相关币种，获取汇率转换
            rate = self.get_exchange_rate('CNY', 'USDT')
            if rate:
                usdt_amount = cny_amount / rate
                return f"{usdt_amount:.2f} USDT"
            else:
                return f"{cny_amount:.2f} CNY"
        elif currency == 'tron.trx':
            # TRX，获取汇率转换
            rate = self.get_exchange_rate('CNY', 'TRX')
            if rate:
                trx_amount = cny_amount / rate
                return f"{trx_amount:.2f} TRX"
            else:
                return f"{cny_amount:.2f} CNY"
        else:
            return f"{cny_amount:.2f} CNY"