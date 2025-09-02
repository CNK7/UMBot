from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
import uuid
import json

class MemberLevel(Enum):
    """会员等级"""
    BRONZE = "bronze"      # 青铜会员
    SILVER = "silver"      # 白银会员
    GOLD = "gold"          # 黄金会员
    PLATINUM = "platinum"  # 铂金会员
    DIAMOND = "diamond"    # 钻石会员
    SUPREME = "supreme"    # 至尊会员

class RechargeActivityType(Enum):
    """充值活动类型"""
    BONUS = "bonus"        # 充值赠送
    DISCOUNT = "discount"  # 充值折扣
    FIRST_TIME = "first_time"  # 首充优惠
    LEVEL_UP = "level_up"  # 升级奖励

@dataclass
class User:
    """用户信息"""
    user_id: int                    # Telegram用户ID
    username: str                   # 用户名
    first_name: str                 # 名字
    last_name: Optional[str] = None # 姓氏
    balance: float = 0.0            # 账户余额（CNY）
    level: MemberLevel = MemberLevel.BRONZE  # 会员等级
    total_recharged: float = 0.0    # 累计充值金额
    total_spent: float = 0.0        # 累计消费金额
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    is_active: bool = True          # 账户状态
    referrer_id: Optional[int] = None  # 推荐人ID
    referral_code: str = field(default_factory=lambda: str(uuid.uuid4())[:8])  # 推荐码
    
    def get_level_benefits(self) -> Dict:
        """获取会员等级权益"""
        benefits = {
            MemberLevel.BRONZE: {
                "discount": 0.0,
                "recharge_bonus": 0.0,
                "name": "青铜会员",
                "emoji": "🥉"
            },
            MemberLevel.SILVER: {
                "discount": 0.05,
                "recharge_bonus": 0.02,
                "name": "白银会员",
                "emoji": "🥈"
            },
            MemberLevel.GOLD: {
                "discount": 0.10,
                "recharge_bonus": 0.05,
                "name": "黄金会员",
                "emoji": "🥇"
            },
            MemberLevel.PLATINUM: {
                "discount": 0.15,
                "recharge_bonus": 0.08,
                "name": "铂金会员",
                "emoji": "💎"
            },
            MemberLevel.DIAMOND: {
                "discount": 0.20,
                "recharge_bonus": 0.10,
                "name": "钻石会员",
                "emoji": "💍"
            },
            MemberLevel.SUPREME: {
                "discount": 0.25,
                "recharge_bonus": 0.15,
                "name": "至尊会员",
                "emoji": "👑"
            }
        }
        return benefits.get(self.level, benefits[MemberLevel.BRONZE])
    
    def update_level(self):
        """根据累计充值金额更新会员等级"""
        if self.total_recharged >= 30000:
            self.level = MemberLevel.SUPREME
        elif self.total_recharged >= 10000:
            self.level = MemberLevel.DIAMOND
        elif self.total_recharged >= 5000:
            self.level = MemberLevel.PLATINUM
        elif self.total_recharged >= 2000:
            self.level = MemberLevel.GOLD
        elif self.total_recharged >= 500:
            self.level = MemberLevel.SILVER
        else:
            self.level = MemberLevel.BRONZE

@dataclass
class RechargeRecord:
    """充值记录"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: int = 0
    amount: float = 0.0             # 充值金额（CNY）
    bonus_amount: float = 0.0       # 赠送金额
    payment_method: str = ""        # 支付方式
    payment_order_id: str = ""      # 支付订单ID
    status: str = "pending"         # pending, paid, failed, expired
    activity_id: Optional[str] = None  # 参与的活动ID
    created_at: datetime = field(default_factory=datetime.now)
    paid_at: Optional[datetime] = None
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=1))
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        return datetime.now() > self.expires_at and self.status == "pending"

@dataclass
class RechargeActivity:
    """充值活动"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""                  # 活动名称
    description: str = ""           # 活动描述
    activity_type: RechargeActivityType = RechargeActivityType.BONUS
    min_amount: float = 0.0         # 最低充值金额
    max_amount: Optional[float] = None  # 最高充值金额
    bonus_rate: float = 0.0         # 赠送比例（如0.1表示10%）
    discount_rate: float = 0.0      # 折扣比例（如0.1表示9折）
    fixed_bonus: float = 0.0        # 固定赠送金额
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=7))
    is_active: bool = True          # 活动状态
    max_participants: Optional[int] = None  # 最大参与人数
    current_participants: int = 0   # 当前参与人数
    user_limit: int = 1             # 每用户参与次数限制
    level_requirement: Optional[MemberLevel] = None  # 会员等级要求
    
    def is_valid(self) -> bool:
        """检查活动是否有效"""
        now = datetime.now()
        return (self.is_active and 
                self.start_time <= now <= self.end_time and
                (self.max_participants is None or self.current_participants < self.max_participants))
    
    def calculate_bonus(self, amount: float) -> float:
        """计算充值奖励"""
        if not self.is_valid() or amount < self.min_amount:
            return 0.0
        
        if self.max_amount and amount > self.max_amount:
            amount = self.max_amount
        
        if self.activity_type == RechargeActivityType.BONUS:
            return amount * self.bonus_rate + self.fixed_bonus
        elif self.activity_type == RechargeActivityType.DISCOUNT:
            return amount * self.discount_rate
        elif self.activity_type == RechargeActivityType.FIRST_TIME:
            return amount * self.bonus_rate + self.fixed_bonus
        
        return 0.0

@dataclass
class BalanceTransaction:
    """余额变动记录"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: int = 0
    amount: float = 0.0             # 变动金额（正数为增加，负数为减少）
    balance_before: float = 0.0     # 变动前余额
    balance_after: float = 0.0      # 变动后余额
    transaction_type: str = ""      # recharge, purchase, refund, bonus, admin
    description: str = ""           # 变动描述
    related_order_id: Optional[str] = None  # 关联订单ID
    created_at: datetime = field(default_factory=datetime.now)

class MemberSystem:
    """会员系统管理类"""
    
    def __init__(self):
        self.users: Dict[int, User] = {}  # 用户数据
        self.recharge_records: Dict[str, RechargeRecord] = {}  # 充值记录
        self.activities: Dict[str, RechargeActivity] = {}  # 充值活动
        self.transactions: Dict[str, BalanceTransaction] = {}  # 余额变动记录
        self.user_activity_count: Dict[tuple, int] = {}  # 用户参与活动次数统计
        
        # 初始化默认活动
        self._init_default_activities()
    
    def _init_default_activities(self):
        """初始化默认充值活动"""
        # 首充双倍活动
        first_recharge = RechargeActivity(
            name="首充双倍",
            description="首次充值享受100%赠送，充100送100！",
            activity_type=RechargeActivityType.FIRST_TIME,
            min_amount=50.0,
            max_amount=500.0,
            bonus_rate=1.0,
            end_time=datetime.now() + timedelta(days=365),
            user_limit=1
        )
        self.activities[first_recharge.id] = first_recharge
        
        # 充值赠送活动
        recharge_bonus = RechargeActivity(
            name="充值赠送",
            description="充值满100元赠送10%，多充多送！",
            activity_type=RechargeActivityType.BONUS,
            min_amount=100.0,
            bonus_rate=0.1,
            end_time=datetime.now() + timedelta(days=30),
            user_limit=10
        )
        self.activities[recharge_bonus.id] = recharge_bonus
        
        # VIP充值折扣
        vip_discount = RechargeActivity(
            name="VIP充值优惠",
            description="黄金及以上会员充值享受5%折扣！",
            activity_type=RechargeActivityType.DISCOUNT,
            min_amount=200.0,
            discount_rate=0.05,
            level_requirement=MemberLevel.GOLD,
            end_time=datetime.now() + timedelta(days=60)
        )
        self.activities[vip_discount.id] = vip_discount
    
    def register_user(self, user_id: int, username: str, first_name: str, 
                     last_name: Optional[str] = None, referrer_id: Optional[int] = None) -> User:
        """注册新用户"""
        if user_id in self.users:
            return self.users[user_id]
        
        user = User(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            referrer_id=referrer_id
        )
        
        self.users[user_id] = user
        
        # 推荐奖励
        if referrer_id and referrer_id in self.users:
            self._add_referral_bonus(referrer_id, user_id)
        
        return user
    
    def get_user(self, user_id: int) -> Optional[User]:
        """获取用户信息"""
        return self.users.get(user_id)
    
    def _add_referral_bonus(self, referrer_id: int, new_user_id: int):
        """添加推荐奖励"""
        referrer = self.users.get(referrer_id)
        if referrer:
            bonus_amount = 10.0  # 推荐奖励10元
            self.add_balance(referrer_id, bonus_amount, "referral", 
                           f"推荐用户 {new_user_id} 注册奖励")
    
    def add_balance(self, user_id: int, amount: float, transaction_type: str, 
                   description: str, related_order_id: Optional[str] = None) -> bool:
        """增加用户余额"""
        user = self.users.get(user_id)
        if not user:
            return False
        
        balance_before = user.balance
        user.balance += amount
        balance_after = user.balance
        
        # 记录余额变动
        transaction = BalanceTransaction(
            user_id=user_id,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            transaction_type=transaction_type,
            description=description,
            related_order_id=related_order_id
        )
        
        self.transactions[transaction.id] = transaction
        return True
    
    def deduct_balance(self, user_id: int, amount: float, transaction_type: str, 
                      description: str, related_order_id: Optional[str] = None) -> bool:
        """扣除用户余额"""
        user = self.users.get(user_id)
        if not user or user.balance < amount:
            return False
        
        balance_before = user.balance
        user.balance -= amount
        user.total_spent += amount
        balance_after = user.balance
        
        # 记录余额变动
        transaction = BalanceTransaction(
            user_id=user_id,
            amount=-amount,
            balance_before=balance_before,
            balance_after=balance_after,
            transaction_type=transaction_type,
            description=description,
            related_order_id=related_order_id
        )
        
        self.transactions[transaction.id] = transaction
        return True
    
    def create_recharge_order(self, user_id: int, amount: float, payment_method: str) -> Optional[RechargeRecord]:
        """创建充值订单"""
        user = self.users.get(user_id)
        if not user:
            return None
        
        # 查找适用的活动
        best_activity = self._find_best_activity(user_id, amount)
        bonus_amount = 0.0
        activity_id = None
        
        if best_activity:
            bonus_amount = best_activity.calculate_bonus(amount)
            activity_id = best_activity.id
        
        # 创建充值记录
        record = RechargeRecord(
            user_id=user_id,
            amount=amount,
            bonus_amount=bonus_amount,
            payment_method=payment_method,
            activity_id=activity_id
        )
        
        self.recharge_records[record.id] = record
        return record
    
    def _find_best_activity(self, user_id: int, amount: float) -> Optional[RechargeActivity]:
        """找到最优充值活动"""
        user = self.users.get(user_id)
        if not user:
            return None
        
        best_activity = None
        best_bonus = 0.0
        
        for activity in self.activities.values():
            if not activity.is_valid():
                continue
            
            # 检查会员等级要求
            if activity.level_requirement and user.level.value < activity.level_requirement.value:
                continue
            
            # 检查用户参与次数限制
            user_count = self.user_activity_count.get((user_id, activity.id), 0)
            if user_count >= activity.user_limit:
                continue
            
            # 检查首充活动
            if activity.activity_type == RechargeActivityType.FIRST_TIME and user.total_recharged > 0:
                continue
            
            bonus = activity.calculate_bonus(amount)
            if bonus > best_bonus:
                best_bonus = bonus
                best_activity = activity
        
        return best_activity
    
    def complete_recharge(self, record_id: str, payment_order_id: str) -> bool:
        """完成充值"""
        record = self.recharge_records.get(record_id)
        if not record or record.status != "pending":
            return False
        
        user = self.users.get(record.user_id)
        if not user:
            return False
        
        # 更新充值记录状态
        record.status = "paid"
        record.payment_order_id = payment_order_id
        record.paid_at = datetime.now()
        
        # 增加用户余额
        total_amount = record.amount + record.bonus_amount
        self.add_balance(record.user_id, total_amount, "recharge", 
                        f"充值 {record.amount} 元，赠送 {record.bonus_amount} 元")
        
        # 更新用户统计
        user.total_recharged += record.amount
        user.update_level()
        
        # 更新活动参与统计
        if record.activity_id:
            activity = self.activities.get(record.activity_id)
            if activity:
                activity.current_participants += 1
                key = (record.user_id, record.activity_id)
                self.user_activity_count[key] = self.user_activity_count.get(key, 0) + 1
        
        return True
    
    def get_user_recharge_history(self, user_id: int, limit: int = 10) -> List[RechargeRecord]:
        """获取用户充值历史"""
        records = [r for r in self.recharge_records.values() if r.user_id == user_id]
        records.sort(key=lambda x: x.created_at, reverse=True)
        return records[:limit]
    
    def get_user_transactions(self, user_id: int, limit: int = 20) -> List[BalanceTransaction]:
        """获取用户余额变动记录"""
        transactions = [t for t in self.transactions.values() if t.user_id == user_id]
        transactions.sort(key=lambda x: x.created_at, reverse=True)
        return transactions[:limit]
    
    def get_active_activities(self) -> List[RechargeActivity]:
        """获取当前有效的充值活动"""
        return [a for a in self.activities.values() if a.is_valid()]
    
    def get_user_applicable_activities(self, user_id: int, amount: float) -> List[RechargeActivity]:
        """获取用户可参与的充值活动"""
        user = self.users.get(user_id)
        if not user:
            return []
        
        applicable = []
        for activity in self.get_active_activities():
            # 检查金额要求
            if amount < activity.min_amount:
                continue
            
            # 检查会员等级要求
            if activity.level_requirement and user.level.value < activity.level_requirement.value:
                continue
            
            # 检查用户参与次数限制
            user_count = self.user_activity_count.get((user_id, activity.id), 0)
            if user_count >= activity.user_limit:
                continue
            
            # 检查首充活动
            if activity.activity_type == RechargeActivityType.FIRST_TIME and user.total_recharged > 0:
                continue
            
            applicable.append(activity)
        
        return applicable