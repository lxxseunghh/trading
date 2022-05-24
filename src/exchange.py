import ccxt
import math
import datetime


class Exchange:
    def __init__(self) -> None:
        self.binance = None
        self.symbol = 'ETH/USDT'
        self.balance = 0
        self.leverage = 5
        self.position_type = None
        self.position_amount = 0
        self.target_price = [0, 0]
        self.k = 0.5
        self.portion = 0.25

        self.set_binance()
        self.set_leverage(self.leverage)
        self.update_target()
        self.update_balance()

    def set_binance(self) -> None:
        with open('./token/key.txt') as f:
            api_key = f.readline().strip()
            secret = f.readline().strip()
        self.binance = ccxt.binance(config={
            'apiKey': api_key,
            'secret': secret,
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}})

    def set_leverage(self, leverage) -> None:
        self.leverage = leverage
        self.binance.load_markets()
        market = self.binance.market(self.symbol)
        self.binance.fapiPrivate_post_leverage({
            'symbol': market['id'],
            'leverage': leverage})

    def get_cur_price(self) -> float:
        return self.binance.fetch_ticker(self.symbol)['last']

    def update_target(self) -> None:
        ohlcv = self.binance.fetch_ohlcv(
            symbol=self.symbol,
            timeframe='1d',
            since=None,
            limit=10)
        distance = (ohlcv[-2][2] - ohlcv[-2][3]) * self.k
        long_target = ohlcv[-1][1] + distance
        short_target = ohlcv[-1][1] - distance
        self.target_price = [long_target, short_target]

    def update_balance(self) -> None:
        self.balance = self.binance.fetch_balance()['total']['USDT']

    def enter_position(self) -> bool:
        precision = 1000
        self.update_balance()
        cur_price = self.get_cur_price()
        amount = self.balance * self.portion * precision
        amount = (amount * self.leverage) / cur_price
        amount = math.floor(amount) / precision
        if cur_price > self.target_price[0]:
            self.binance.create_market_buy_order(
                symbol=self.symbol, amount=amount)
            self.position_type = 'long'
            self.position_amount = amount
            return True
        elif cur_price < self.target_price[1]:
            self.binance.create_market_sell_order(
                symbol=self.symbol, amount=amount)
            self.position_type = 'short'
            self.position_amount = amount
            return True
        return False

    def clear_position(self) -> None:
        if self.position_type == 'long':
            self.binance.create_market_sell_order(
                symbol=self.symbol, amount=self.position_amount)
            self.position_type = None
            self.position_amount = 0
        elif self.position_type == 'short':
            self.binance.create_market_buy_order(
                symbol=self.symbol, amount=self.position_amount)
            self.position_type = None
            self.position_amount = 0

    def __str__(self) -> str:
        self.update_balance()
        text = '###### Current  Info #####\n' + \
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n' + \
            'symbol: {}\n'.format(self.symbol) + \
            'balance: {}\n'.format(self.balance) + \
            'leverage: {}\n'.format(self.leverage) + \
            'position_type: {}\n'.format(self.position_type) + \
            'position_amount: {}\n'.format(self.position_amount) + \
            'price_long: {}\n'.format(self.target_price[0]) + \
            'price_curr: {}\n'.format(self.get_cur_price()) + \
            'price_shrt: {}'.format(self.target_price[1])
        return text
