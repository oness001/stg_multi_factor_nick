import numpy as np
import pandas as pd
import talib

from indicators import *


def increase(array: np.ndarray, timeperiod: int) -> np.ndarray:
    tp = max(1, round(timeperiod / 20))   # 大概取 13 ~ 21
    shift1 = np.concatenate(([np.nan], array[:-1]))
    shifttp = np.concatenate((np.full(tp, np.nan), array[:-tp]))
    return (array > shift1) & (array > shifttp)

def decrease(array: np.ndarray, timeperiod: int) -> np.ndarray:
    tp = max(1, round(timeperiod / 20))   # 大概取 13 ~ 21
    shift1 = np.concatenate(([np.nan], array[:-1]))
    shifttp = np.concatenate((np.full(tp, np.nan), array[:-tp]))
    return (array <= shift1) & (array <= shifttp)

def find_confirmed_swing_points(series: np.ndarray, lookback: int = 5, order: str = 'min') -> np.ndarray:
    """已确认的双侧极值点"""
    n = len(series)
    is_extreme = np.zeros(n, dtype=bool)
    
    for i in range(lookback, n-lookback):
        left_part = series[i-lookback: i]
        right_part = series[i+1: i+lookback+1]
        if order == 'min':  # 局部最低点
            if np.all(left_part >= series[i]) and np.all(right_part > series[i]):
                is_extreme[i] = True
        else:  # 局部最高点 order == 'max'
            if np.all(left_part <= series[i]) and np.all(right_part < series[i]):
                is_extreme[i] = True
    return is_extreme

def find_tentative_swing_points(series: np.ndarray, lookback: int = 5, order: str = 'min') -> np.ndarray:
    """潜在的单側尾部极值点"""
    n = len(series)
    is_extreme = np.zeros(n, dtype=bool)
    
    for i in range(lookback*2, n):
        left_part = series[i-lookback: i]  # 这里仅用到左侧数据（无未来数据），但需要使用 lookback 右侧窗口
        if order == 'min':  # 局部最低点
            if np.all(left_part >= series[i]):
                is_extreme[i] = True
        else:  # 局部最高点 order == 'max'
            if np.all(left_part <= series[i]):
                is_extreme[i] = True
    return is_extreme

def detect_bullish_divergence(
    price: np.ndarray,
    indicator: np.ndarray,
    lookback: int = 5
) -> np.ndarray:
    """
    检测底背离
    1=普通底背离, -1=隐藏底背离, 0=无信号
    """
    n = len(price)
    divergence = np.zeros(n, dtype=np.int8)
    
    # 寻找波谷（低点）
    price_swings_confirmed = find_confirmed_swing_points(price, lookback, 'min')
    ind_swings_confirmed = find_confirmed_swing_points(indicator, lookback, 'min')
    price_swings_tentative = find_tentative_swing_points(price, lookback, 'min')
    ind_swings_tentative = find_tentative_swing_points(indicator, lookback, 'min')

    psc_idx = np.where(price_swings_confirmed)[0]
    isc_idx = np.where(ind_swings_confirmed)[0]

    signal_countdown = 0  # 用于持续背离的窗口计数
    for i in range(lookback*2, n):

        if not (price_swings_tentative[i] or ind_swings_tentative[i]):  # 只在出现 tentative 时检查新信号
            continue

        # 获取历史已确认低点索引（i-lookback 之前为已确认的波谷）
        valid_psc_idx = psc_idx[psc_idx <= i-lookback]
        valid_isc_idx = isc_idx[isc_idx <= i-lookback]

        if len(valid_psc_idx) < 1 or len(valid_isc_idx) < 1:
            continue

        last_price_swing = price[i]
        prev_price_swing = min(price[valid_psc_idx[-1]], price[valid_isc_idx[-1]])  # 前一个波谷价格
        last_ind_swing = indicator[i]
        prev_ind_swing = min(indicator[valid_psc_idx[-1]], indicator[valid_isc_idx[-1]])  # 前一个波谷指标值

        if last_price_swing < prev_price_swing and last_ind_swing > prev_ind_swing:  # 底背离（看涨）
            divergence[i] = 1
            signal_countdown = lookback
        elif last_price_swing > prev_price_swing and last_ind_swing < prev_ind_swing:  # 隐形底背离（看跌）
            divergence[i] = -1
            signal_countdown = lookback
        elif signal_countdown > 0:  # 信号持续
            divergence[i] = divergence[i-1]
            signal_countdown -= 1

    return divergence

def detect_bearish_divergence(
    price: np.ndarray,
    indicator: np.ndarray,
    lookback: int = 5
) -> np.ndarray:
    """
    检测顶背离（看跌背离）
    -1=普通顶背离, 1=隐藏顶背离, 0=无信号
    """
    n = len(price)
    divergence = np.zeros(n, dtype=np.int8)
    
    # 寻找波峰（高点）
    price_swings_confirmed = find_confirmed_swing_points(price, lookback, 'max')
    ind_swings_confirmed = find_confirmed_swing_points(indicator, lookback, 'max')
    price_swings_tentative = find_tentative_swing_points(price, lookback, 'max')
    ind_swings_tentative = find_tentative_swing_points(indicator, lookback, 'max')

    psc_idx = np.where(price_swings_confirmed)[0]
    isc_idx = np.where(ind_swings_confirmed)[0]

    signal_countdown = 0  # 用于持续背离的窗口计数
    for i in range(lookback*2, n):

        if not (price_swings_tentative[i] or ind_swings_tentative[i]):  # 只在出现 tentative 时检查新信号
            continue

        # 获取历史已确认低点索引（i-lookback 之前为已确认的波峰）
        valid_psc_idx = psc_idx[psc_idx <= i-lookback]
        valid_isc_idx = isc_idx[isc_idx <= i-lookback]

        if len(valid_psc_idx) < 1 or len(valid_isc_idx) < 1:
            continue

        last_price_swing = price[i]
        prev_price_swing = max(price[valid_psc_idx[-1]], price[valid_isc_idx[-1]])  # 前一个波峰价格
        last_ind_swing = indicator[i]
        prev_ind_swing = max(indicator[valid_psc_idx[-1]], indicator[valid_isc_idx[-1]])  # 前一个波峰指标值

        if last_price_swing > prev_price_swing and last_ind_swing < prev_ind_swing:  # 顶背离（看跌）
            divergence[i] = -1
            signal_countdown = lookback
        elif last_price_swing < prev_price_swing and last_ind_swing > prev_ind_swing:  # 隐形顶背离（看涨）
            divergence[i] = 1
            signal_countdown = lookback
        elif signal_countdown > 0:  # 信号持续
            divergence[i] = divergence[i-1]
            signal_countdown -= 1

    return divergence

"""过滤条件函数"""
def no_filter(market_df: pd.DataFrame) -> np.ndarray:
    return np.array([True] * len(market_df))


# 多头趋势过滤
if True:

    def roc_higher0(market_df: pd.DataFrame, N1: int) -> np.ndarray:
        price = market_df['close'].values
        roc = talib.ROC(price, timeperiod=N1)
        return roc > 0

    def aroon_diff_higher0(market_df: pd.DataFrame, N1: int) -> np.ndarray:
        """AROON 指标通过最高价/最低价的时间距离当前的时间来判断趋势方向，差值大于0表示多头趋势，差值小于0表示空头趋势"""
        high = market_df['high'].values
        low = market_df['low'].values
        aroon_down, aroon_up = talib.AROON(high, low, timeperiod=N1)
        aroon_diff = aroon_up - aroon_down
        return aroon_diff > 0

    def price_higher_sma(market_df: pd.DataFrame, N1: int) -> np.ndarray:
        price = market_df['close'].values
        price_ma = talib.SMA(price, N1)
        return price > price_ma

    def price_higher_sma_and_increase(market_df: pd.DataFrame, N1: int) -> np.ndarray:
        price = market_df['close'].values
        price_ma = talib.SMA(price, N1)
        return (price > price_ma) & increase(price_ma, N1)

    def price_higher_sma_or_increase(market_df: pd.DataFrame, N1: int) -> np.ndarray:
        price = market_df['close'].values
        price_ma = talib.SMA(price, N1)
        return (price > price_ma) | increase(price_ma, N1)

    def price_higher_ema(market_df: pd.DataFrame, N1: int) -> np.ndarray:
        price = market_df['close'].values
        price_ma = talib.EMA(price, N1)
        return price > price_ma

    def sma_fast_higher_slow(market_df: pd.DataFrame, N1: int, N2: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.SMA(price, N1)
        slow_ma = talib.SMA(price, N2)
        return fast_ma > slow_ma

    def sma_fast_higher_slow_and_increase(market_df: pd.DataFrame, N1: int, N2: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.SMA(price, N1)
        slow_ma = talib.SMA(price, N2)
        macd_line = fast_ma - slow_ma
        return (fast_ma > slow_ma) & increase(macd_line, N1)

    def sma_fast_higher_slow_or_increase(market_df: pd.DataFrame, N1: int, N2: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.SMA(price, N1)
        slow_ma = talib.SMA(price, N2)
        macd_line = fast_ma - slow_ma
        return (fast_ma > slow_ma) | increase(macd_line, N1)

    def ema_fast_higher_slow(market_df: pd.DataFrame, N1: int, N2: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.EMA(price, N1)
        slow_ma = talib.EMA(price, N2)
        return fast_ma > slow_ma

    def ema_fast_higher_slow_and_increase(market_df: pd.DataFrame, N1: int, N2: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.EMA(price, N1)
        slow_ma = talib.EMA(price, N2)
        macd_line = fast_ma - slow_ma
        return (fast_ma > slow_ma) & increase(macd_line, N1)

    def ema_fast_higher_slow_or_increase(market_df: pd.DataFrame, N1: int, N2: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.EMA(price, N1)
        slow_ma = talib.EMA(price, N2)
        macd_line = fast_ma - slow_ma
        return (fast_ma > slow_ma) | increase(macd_line, N1)

    def smacd_increase(market_df: pd.DataFrame, N1: int = 12, N2: int = 26) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=N1, slowperiod=N2,  signalperiod=9)
        return increase(macd_line, N1)

    def smacd_histogram_increase(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=N1, slowperiod=N2,  signalperiod=N3)
        return increase(histogram, N1)

    def smacd_higher_signal(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=N1, slowperiod=N2,  signalperiod=N3)
        return histogram > 0

    def smacd_higher_signal_and_increase(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=N1, slowperiod=N2,  signalperiod=N3)
        return (histogram > 0) & increase(histogram, N1)

    def smacd_higher_signal_or_increase(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=N1, slowperiod=N2,  signalperiod=N3)
        return (histogram > 0) | increase(histogram, N1)

    def emacd_increase(market_df: pd.DataFrame, N1: int = 12, N2: int = 26) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=N1, slowperiod=N2,  signalperiod=9)
        return increase(macd_line, N1)

    def emacd_histogram_increase(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=N1, slowperiod=N2,  signalperiod=N3)
        return increase(histogram, N1)

    def emacd_higher_signal(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=N1, slowperiod=N2,  signalperiod=N3)
        return histogram > 0

    def emacd_higher_signal_and_increase(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=N1, slowperiod=N2,  signalperiod=N3)
        return (histogram > 0) & increase(histogram, N1)

    def emacd_higher_signal_or_increase(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=N1, slowperiod=N2,  signalperiod=N3)
        return (histogram > 0) | increase(histogram, N1)

    def trix_higher0(market_df: pd.DataFrame, N1: int = 12) -> np.ndarray:
        """TRIX 指标是一个基于三重指数移动平均的动量指标，TRIX 大于0表示多头趋势，TRIX 小于0表示空头趋势"""
        price = market_df['close'].values
        trix = talib.TRIX(price, timeperiod=N1)
        return trix > 0

    def trix_increase(market_df: pd.DataFrame, N1: int = 12) -> np.ndarray:
        price = market_df['close'].values
        trix = talib.TRIX(price, timeperiod=N1)
        return increase(trix, N1)

    def trix_higher_signal(market_df: pd.DataFrame, N1: int = 12, N2: int = 12) -> np.ndarray:
        price = market_df['close'].values
        trix = talib.TRIX(price, timeperiod=N1)
        signal_line = talib.EMA(trix, timeperiod=N2)
        return trix > signal_line

    def trix_higher_signal_and_increase(market_df: pd.DataFrame, N1: int = 12, N2: int = 12) -> np.ndarray:
        price = market_df['close'].values
        trix = talib.TRIX(price, timeperiod=N1)
        signal_line = talib.EMA(trix, timeperiod=N2)
        return (trix > signal_line) & increase(trix, N1)

    def trix_higher_signal_or_increase(market_df: pd.DataFrame, N1: int = 12, N2: int = 12) -> np.ndarray:
        price = market_df['close'].values
        trix = talib.TRIX(price, timeperiod=N1)
        signal_line = talib.EMA(trix, timeperiod=N2)
        return (trix > signal_line) | increase(trix, N1)

    def adx_plus_higher_minus(market_df: pd.DataFrame, N1: int = 14) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        plus_di = talib.PLUS_DI(high, low, close, timeperiod=N1)
        minus_di = talib.MINUS_DI(high, low, close, timeperiod=N1)
        return plus_di > minus_di

    def tsi_higher_signal(market_df: pd.DataFrame, N1: int = 25, N2: int = 13, N3: int = 13, T4: str = "EMA") -> np.ndarray:
        close = market_df['close'].values
        tsi = TSI(close, firstperiod=N1, secondperiod=N2, MA_Type=T4)
        signal_line = MA(tsi, N3, T4)
        return tsi > signal_line

    def rsi_fast_higher_slow(market_df: pd.DataFrame, N1: int, N2: int) -> np.ndarray:
        price = market_df['close'].values
        fast_rsi = talib.RSI(price, timeperiod=N1)
        slow_rsi = talib.RSI(price, timeperiod=N2)
        return fast_rsi > slow_rsi

    def supertrend_long_period(market_df: pd.DataFrame, N1: int = 10, N2: int = 3) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        supertrend, trend = SuperTrend(high, low, close, int(N1), N2)
        return trend == 1

    def ma_atr_long_period(market_df: pd.DataFrame, N1: int = 140, N2: int = 70, N3: float = 1.5) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        direction = Ma_Atr_Direction(high, low, close, N1, N2, N3)
        return direction == 1

    def stoch_k_higher_d(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        slowk, slowd = talib.STOCH(high, low, close, fastk_period=N1, slowk_period=N2, slowd_period=N3)
        return slowk > slowd

    def kdj_k_higher_d(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        k, d = talib.STOCH(high, low, close, fastk_period=N1, slowk_period=N2, slowk_matype=talib.MA_Type.EMA, slowd_period=N3, slowd_matype=talib.MA_Type.EMA)
        return k > d

    def smi_k_higher_d(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3, T4: str = "EMA") -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        smi, slowd = SMI(high, low, close, fastk_period=N1, slowk_period=N2, slowd_period=N3, MA_Type=T4)
        return smi > slowd

    def rvi_higher_signal(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, T3: str = "EMA") -> np.ndarray:
        open = market_df['open'].values
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        rvi, signal_line = Relative_Vigor_Index(open, high, low, close, firstperiod=N1, secondperiod=N2, MA_Type=T3)
        return rvi > signal_line

    def rsi_bullish_divergence(market_df: pd.DataFrame, N1: int = 14) -> np.ndarray:
        """RSI底背离"""
        price = market_df['close'].values
        rsi = talib.RSI(price, timeperiod=N1)
        return detect_bullish_divergence(price, rsi, lookback=N1) == 1

    def rsi_bearish_divergence(market_df: pd.DataFrame, N1: int = 14) -> np.ndarray:
        """RSI顶背离"""
        price = market_df['close'].values
        rsi = talib.RSI(price, timeperiod=N1)
        return detect_bearish_divergence(price, rsi, lookback=N1) == 1

    def rsi_divergence(market_df: pd.DataFrame, N1: int = 14) -> np.ndarray:
        """RSI背离"""
        price = market_df['close'].values
        rsi = talib.RSI(price, timeperiod=N1)
        return (detect_bullish_divergence(price, rsi, lookback=N1) == 1) | (detect_bearish_divergence(price, rsi, lookback=N1) == 1)

    def macd_bullish_divergence(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        """MACD底背离"""
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=N1, slowperiod=N2,  signalperiod=N3)
        return detect_bullish_divergence(price, macd_line, lookback=N1) == 1

    def macd_bearish_divergence(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        """MACD顶背离"""
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=N1, slowperiod=N2,  signalperiod=N3)
        return detect_bearish_divergence(price, macd_line, lookback=N1) == 1

    def macd_divergence(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        """MACD背离"""
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=N1, slowperiod=N2,  signalperiod=N3)
        return (detect_bullish_divergence(price, macd_line, lookback=N1) == 1) | (detect_bearish_divergence(price, macd_line, lookback=N1) == 1)

    def macd_histogram_bullish_divergence(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        """MACD底背离"""
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=N1, slowperiod=N2,  signalperiod=N3)
        return detect_bullish_divergence(price, histogram, lookback=N1) == 1

    def macd_histogram_bearish_divergence(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        """MACD顶背离"""
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=N1, slowperiod=N2,  signalperiod=N3)
        return detect_bearish_divergence(price, histogram, lookback=N1) == 1

    def macd_histogram_divergence(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        """MACD背离"""
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=N1, slowperiod=N2,  signalperiod=N3)
        return (detect_bullish_divergence(price, histogram, lookback=N1) == 1) | (detect_bearish_divergence(price, histogram, lookback=N1) == 1)

    def ema_slope_bullish_divergence(market_df: pd.DataFrame, N1: int = 14) -> np.ndarray:
        price = market_df['close'].values
        ma_slope = EMA_SLOPE(price, timeperiod=N1)
        divergence_period = round(N1 / 2)
        return detect_bullish_divergence(price, ma_slope, lookback=divergence_period) == 1

    def ema_slope_bearish_divergence(market_df: pd.DataFrame, N1: int = 14) -> np.ndarray:
        price = market_df['close'].values
        ma_slope = EMA_SLOPE(price, timeperiod=N1)
        divergence_period = round(N1 / 2)
        return detect_bearish_divergence(price, ma_slope, lookback=divergence_period) == 1

    def ema_slope_divergence(market_df: pd.DataFrame, N1: int = 14) -> np.ndarray:
        price = market_df['close'].values
        ma_slope = EMA_SLOPE(price, timeperiod=N1)
        divergence_period = round(N1 / 2)
        return (detect_bullish_divergence(price, ma_slope, lookback=divergence_period) == 1) | (detect_bearish_divergence(price, ma_slope, lookback=divergence_period) == 1)


# 空头趋势过滤
if True:
    
    def roc_lower0(market_df: pd.DataFrame, N1: int) -> np.ndarray:
        price = market_df['close'].values
        roc = talib.ROC(price, timeperiod=N1)
        return roc <= 0

    def aroon_diff_lower0(market_df: pd.DataFrame, N1: int) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        aroon_down, aroon_up = talib.AROON(high, low, timeperiod=N1)
        aroon_diff = aroon_up - aroon_down
        return aroon_diff <= 0

    def price_lower_sma(market_df: pd.DataFrame, N1: int) -> np.ndarray:
        price = market_df['close'].values
        price_ma = talib.SMA(price, N1)
        return price <= price_ma

    def price_lower_sma_and_decrease(market_df: pd.DataFrame, N1: int) -> np.ndarray:
        price = market_df['close'].values
        price_ma = talib.SMA(price, N1)
        return (price <= price_ma) & decrease(price_ma, N1)

    def price_lower_sma_or_decrease(market_df: pd.DataFrame, N1: int) -> np.ndarray:
        price = market_df['close'].values
        price_ma = talib.SMA(price, N1)
        return (price <= price_ma) | decrease(price_ma, N1)

    def price_lower_ema(market_df: pd.DataFrame, N1: int) -> np.ndarray:
        price = market_df['close'].values
        price_ma = talib.EMA(price, N1)
        return price <= price_ma

    def sma_fast_lower_slow(market_df: pd.DataFrame, N1: int, N2: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.SMA(price, N1)
        slow_ma = talib.SMA(price, N2)
        return fast_ma <= slow_ma

    def sma_fast_lower_slow_and_decrease(market_df: pd.DataFrame, N1: int, N2: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.SMA(price, N1)
        slow_ma = talib.SMA(price, N2)
        macd_line = fast_ma - slow_ma
        return (fast_ma <= slow_ma) & decrease(macd_line, N1)

    def sma_fast_lower_slow_or_decrease(market_df: pd.DataFrame, N1: int, N2: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.SMA(price, N1)
        slow_ma = talib.SMA(price, N2)
        macd_line = fast_ma - slow_ma
        return (fast_ma <= slow_ma) | decrease(macd_line, N1)

    def ema_fast_lower_slow(market_df: pd.DataFrame, N1: int, N2: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.EMA(price, N1)
        slow_ma = talib.EMA(price, N2)
        return fast_ma <= slow_ma

    def ema_fast_lower_slow_and_decrease(market_df: pd.DataFrame, N1: int, N2: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.EMA(price, N1)
        slow_ma = talib.EMA(price, N2)
        macd_line = fast_ma - slow_ma
        return (fast_ma <= slow_ma) & decrease(macd_line, N1)

    def ema_fast_lower_slow_or_decrease(market_df: pd.DataFrame, N1: int, N2: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.EMA(price, N1)
        slow_ma = talib.EMA(price, N2)
        macd_line = fast_ma - slow_ma
        return (fast_ma <= slow_ma) | decrease(macd_line, N1)

    def smacd_decrease(market_df: pd.DataFrame, N1: int = 12, N2: int = 26) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=N1, slowperiod=N2,  signalperiod=9)
        return decrease(macd_line, N1)

    def smacd_histogram_decrease(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=N1, slowperiod=N2,  signalperiod=N3)
        return decrease(histogram, N1)

    def smacd_lower_signal(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=N1, slowperiod=N2,  signalperiod=N3)
        return histogram <= 0

    def smacd_lower_signal_and_decrease(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=N1, slowperiod=N2,  signalperiod=N3)
        return (histogram <= 0) & decrease(histogram, N1)

    def smacd_lower_signal_or_decrease(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=N1, slowperiod=N2,  signalperiod=N3)
        return (histogram <= 0) | decrease(histogram, N1)

    def emacd_decrease(market_df: pd.DataFrame, N1: int = 12, N2: int = 26) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=N1, slowperiod=N2,  signalperiod=9)
        return decrease(macd_line, N1)

    def emacd_histogram_decrease(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=N1, slowperiod=N2,  signalperiod=N3)
        return decrease(histogram, N1)

    def emacd_lower_signal(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=N1, slowperiod=N2,  signalperiod=N3)
        return histogram <= 0

    def emacd_lower_signal_and_decrease(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=N1, slowperiod=N2,  signalperiod=N3)
        return (histogram <= 0) & decrease(histogram, N1)

    def emacd_lower_signal_or_decrease(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=N1, slowperiod=N2,  signalperiod=N3)
        return (histogram <= 0) | decrease(histogram, N1)

    def trix_lower0(market_df: pd.DataFrame, N1: int = 12) -> np.ndarray:
        """TRIX 指标是一个基于三重指数移动平均的动量指标，TRIX 大于0表示多头趋势，TRIX 小于0表示空头趋势"""
        price = market_df['close'].values
        trix = talib.TRIX(price, timeperiod=N1)
        return trix <= 0

    def trix_decrease(market_df: pd.DataFrame, N1: int = 12) -> np.ndarray:
        price = market_df['close'].values
        trix = talib.TRIX(price, timeperiod=N1)
        return decrease(trix, N1)

    def trix_lower_signal(market_df: pd.DataFrame, N1: int = 12, N2: int = 12) -> np.ndarray:
        price = market_df['close'].values
        trix = talib.TRIX(price, timeperiod=N1)
        signal_line = talib.EMA(trix, timeperiod=N2)
        return trix <= signal_line

    def trix_lower_signal_and_increase(market_df: pd.DataFrame, N1: int = 12, N2: int = 12) -> np.ndarray:
        price = market_df['close'].values
        trix = talib.TRIX(price, timeperiod=N1)
        signal_line = talib.EMA(trix, timeperiod=N2)
        return (trix <= signal_line) & increase(trix, N1)

    def trix_lower_signal_or_increase(market_df: pd.DataFrame, N1: int = 12, N2: int = 12) -> np.ndarray:
        price = market_df['close'].values
        trix = talib.TRIX(price, timeperiod=N1)
        signal_line = talib.EMA(trix, timeperiod=N2)
        return (trix <= signal_line) | increase(trix, N1)

    def adx_plus_lower_minus(market_df: pd.DataFrame, N1: int = 14) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        plus_di = talib.PLUS_DI(high, low, close, timeperiod=N1)
        minus_di = talib.MINUS_DI(high, low, close, timeperiod=N1)
        return plus_di <= minus_di

    def tsi_lower_signal(market_df: pd.DataFrame, N1: int = 25, N2: int = 13, N3: int = 13, T4: str = "EMA") -> np.ndarray:
        close = market_df['close'].values
        tsi = TSI(close, firstperiod=N1, secondperiod=N2, MA_Type=T4)
        signal_line = MA(tsi, N3, T4)
        return tsi <= signal_line

    def rsi_fast_lower_slow(market_df: pd.DataFrame, N1: int, N2: int) -> np.ndarray:
        price = market_df['close'].values
        fast_rsi = talib.RSI(price, timeperiod=N1)
        slow_rsi = talib.RSI(price, timeperiod=N2)
        return fast_rsi <= slow_rsi

    def supertrend_short_period(market_df: pd.DataFrame, N1: int = 10, N2: int = 3) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        supertrend, trend = SuperTrend(high, low, close, int(N1), N2)
        return trend == -1

    def ma_atr_short_period(market_df: pd.DataFrame, N1: int = 140, N2: int = 70, N3: float = 1.5) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        direction = Ma_Atr_Direction(high, low, close, N1, N2, N3)
        return direction == -1


# 基于超买超卖过滤
if True:
    def bb_neutral(market_df: pd.DataFrame, N1: int, N2: float) -> np.ndarray:
        price = market_df['close'].values
        upper_band, middle_band, lower_band = talib.BBANDS(price, timeperiod=N1, nbdevup=N2, nbdevdn=N2)
        return (price <= upper_band) & (price > lower_band)

    def bb_overbought(market_df: pd.DataFrame, N1: int, N2: float) -> np.ndarray:
        price = market_df['close'].values
        upper_band, middle_band, lower_band = talib.BBANDS(price, timeperiod=N1, nbdevup=N2, nbdevdn=N2)
        return price > upper_band

    def bb_oversold(market_df: pd.DataFrame, N1: int, N2: float) -> np.ndarray:
        price = market_df['close'].values
        upper_band, middle_band, lower_band = talib.BBANDS(price, timeperiod=N1, nbdevup=N2, nbdevdn=N2)
        return price <= lower_band

if True:
    def kc_neutral(market_df: pd.DataFrame, N1: int, N2: int, N3: float) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        upper_channel, middle_band, lower_channel = KChannels(high, low, close, N1, N2, N3)
        return (close <= upper_channel) & (close > lower_channel)

    def kc_overbought(market_df: pd.DataFrame, N1: int, N2: int, N3: float) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        upper_channel, middle_band, lower_channel = KChannels(high, low, close, N1, N2, N3)
        return close > upper_channel

    def kc_oversold(market_df: pd.DataFrame, N1: int, N2: int, N3: float) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        upper_channel, middle_band, lower_channel = KChannels(high, low, close, N1, N2, N3)
        return close <= lower_channel

if True:
    def tsi_neutral(market_df: pd.DataFrame, N1: int = 25, N2: int = 13, N3: float = 25, N4: float = -25, T5: str = "EMA") -> np.ndarray:
        price = market_df['close'].values
        tsi = TSI(price, firstperiod=N1, secondperiod=N2, MA_Type=T5)
        return (tsi <= N3) & (tsi > N4)

    def tsi_overbought(market_df: pd.DataFrame, N1: int = 25, N2: int = 13, N3: float = 25, T4: str = "EMA") -> np.ndarray:
        price = market_df['close'].values
        tsi = TSI(price, firstperiod=N1, secondperiod=N2, MA_Type=T4)
        return tsi > N3

    def tsi_oversold(market_df: pd.DataFrame, N1: int = 25, N2: int = 13, N3: float = -25, T4: str = "EMA") -> np.ndarray:
        price = market_df['close'].values
        tsi = TSI(price, firstperiod=N1, secondperiod=N2, MA_Type=T4)
        return tsi <= N3

if True:
    def rsi_neutral(market_df: pd.DataFrame, N1: int, N2: float = 70, N3: float = 30) -> np.ndarray:
        price = market_df['close'].values
        rsi = talib.RSI(price, timeperiod=N1)
        return (rsi <= N2) & (rsi > N3)

    def rsi_overbought(market_df: pd.DataFrame, N1: int, N2: float = 70) -> np.ndarray:
        price = market_df['close'].values
        rsi = talib.RSI(price, timeperiod=N1)
        return rsi > N2

    def rsi_oversold(market_df: pd.DataFrame, N1: int, N2: float = 30) -> np.ndarray:
        price = market_df['close'].values
        rsi = talib.RSI(price, timeperiod=N1)
        return rsi <= N2

if True:
    def stoch_k_neutral(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: float = 80, N4: float = 20) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        slowk, _ = talib.STOCH(high, low, close, fastk_period=N1, slowk_period=N2, slowd_period=3)
        return (slowk <= N3) & (slowk > N4)

    def stoch_k_overbought(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: float = 80) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        slowk, _ = talib.STOCH(high, low, close, fastk_period=N1, slowk_period=N2, slowd_period=3)
        return slowk > N3

    def stoch_k_oversold(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: float = 20) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        slowk, _ = talib.STOCH(high, low, close, fastk_period=N1, slowk_period=N2, slowd_period=3)
        return slowk <= N3

    def stoch_d_neutral(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3, N4: float = 80, N5: float = 20) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        _, slowd = talib.STOCH(high, low, close, fastk_period=N1, slowk_period=N2, slowd_period=N3)
        return (slowd <= N4) & (slowd > N5)

    def stoch_d_overbought(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3, N4: float = 80) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        _, slowd = talib.STOCH(high, low, close, fastk_period=N1, slowk_period=N2, slowd_period=N3)
        return slowd > N4

    def stoch_d_oversold(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3, N4: float = 20) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        _, slowd = talib.STOCH(high, low, close, fastk_period=N1, slowk_period=N2, slowd_period=N3)
        return slowd <= N4

if True:
    def kdj_k_neutral(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: float = 80, N4: float = 20) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        k, _ = talib.STOCH(high, low, close, fastk_period=N1, slowk_period=N2, slowk_matype=talib.MA_Type.EMA, slowd_period=3, slowd_matype=talib.MA_Type.EMA)
        return (k <= N3) & (k > N4)

    def kdj_k_overbought(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: float = 80) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        k , _ = talib.STOCH(high, low, close, fastk_period=N1, slowk_period=N2, slowk_matype=talib.MA_Type.EMA, slowd_period=3, slowd_matype=talib.MA_Type.EMA)
        return k > N3

    def kdj_k_oversold(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: float = 20) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        k, _ = talib.STOCH(high, low, close, fastk_period=N1, slowk_period=N2, slowk_matype=talib.MA_Type.EMA, slowd_period=3, slowd_matype=talib.MA_Type.EMA)
        return k <= N3

    def kdj_d_neutral(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3, N4: float = 80, N5: float = 20) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        _, d = talib.STOCH(high, low, close, fastk_period=N1, slowk_period=N2, slowk_matype=talib.MA_Type.EMA, slowd_period=N3, slowd_matype=talib.MA_Type.EMA)
        return (d <= N4) & (d > N5)

    def kdj_d_overbought(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3, N4: float = 80) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        _, d = talib.STOCH(high, low, close, fastk_period=N1, slowk_period=N2, slowk_matype=talib.MA_Type.EMA, slowd_period=N3, slowd_matype=talib.MA_Type.EMA)
        return d > N4

    def kdj_d_oversold(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3, N4: float = 20) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        _, d = talib.STOCH(high, low, close, fastk_period=N1, slowk_period=N2, slowk_matype=talib.MA_Type.EMA, slowd_period=N3, slowd_matype=talib.MA_Type.EMA)
        return d <= N4

if True:
    def smi_neutral(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: float = 20, N4: float = -20, T5: str = "EMA") -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        smi, _ = SMI(high, low, close, fastk_period=N1, slowk_period=N2, slowd_period=3, MA_Type=T5)
        return (smi <= N3) & (smi > N4)

    def smi_overbought(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: float = 20, T4: str = "EMA") -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        smi, _ = SMI(high, low, close, fastk_period=N1, slowk_period=N2, slowd_period=3, MA_Type=T4)
        return smi > N3

    def smi_oversold(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: float = -20, T4: str = "EMA") -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        smi, _ = SMI(high, low, close, fastk_period=N1, slowk_period=N2, slowd_period=3, MA_Type=T4)
        return smi <= N3

    def smi_d_neutral(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3, N4: float = 20, N5: float = -20, T6: str = "EMA") -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        _, slowd = SMI(high, low, close, fastk_period=N1, slowk_period=N2, slowd_period=N3, MA_Type=T6)
        return (slowd <= N4) & (slowd > N5)

    def smi_d_overbought(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3, N4: float = 20, T5: str = "EMA") -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        _, slowd = SMI(high, low, close, fastk_period=N1, slowk_period=N2, slowd_period=N3, MA_Type=T5)
        return slowd > N4

    def smi_d_oversold(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3, N4: float = -20, T5: str = "EMA") -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        _, slowd = SMI(high, low, close, fastk_period=N1, slowk_period=N2, slowd_period=N3, MA_Type=T5)
        return slowd <= N4

    def smi_std_n(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3, N4: float = -20, T5: str = "EMA") -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        smi, slowd = SMI(high, low, close, fastk_period=N1, slowk_period=N2, slowd_period=N3, MA_Type=T5)
        up,me,dn = talib.BBANDS(smi,N3,N4,N4)
        return  smi >= dn and smi <= up
    
if True:
    def rvi_neutral(market_df: pd.DataFrame, N1: int = 5, N2: float = 20, N3: float = -20, T4: str = "EMA") -> np.ndarray:
        open = market_df['open'].values
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        rvi, _ = Relative_Vigor_Index(open, high, low, close, firstperiod=N1, secondperiod=3, MA_Type=T4)
        return (rvi <= N2) & (rvi > N3)

    def rvi_overbought(market_df: pd.DataFrame, N1: int = 5, N2: float = 20, T3: str = "EMA") -> np.ndarray:
        open = market_df['open'].values
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        rvi, _ = Relative_Vigor_Index(open, high, low, close, firstperiod=N1, secondperiod=3, MA_Type=T3)
        return rvi > N2

    def rvi_oversold(market_df: pd.DataFrame, N1: int = 5, N2: float = -20, T3: str = "EMA") -> np.ndarray:
        open = market_df['open'].values
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        rvi, _ = Relative_Vigor_Index(open, high, low, close, firstperiod=N1, secondperiod=3, MA_Type=T3)
        return rvi <= N2

    def rvi_signal_neutral(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: float = 20, N4: float = -20, T5: str = "EMA") -> np.ndarray:
        open = market_df['open'].values
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        _, signal_line = Relative_Vigor_Index(open, high, low, close, firstperiod=N1, secondperiod=N2, MA_Type=T5)
        return (signal_line <= N3) & (signal_line > N4)

    def rvi_signal_overbought(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: float = 20, T4: str = "EMA") -> np.ndarray:
        open = market_df['open'].values
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        _, signal_line = Relative_Vigor_Index(open, high, low, close, firstperiod=N1, secondperiod=N2, MA_Type=T4)
        return signal_line > N3

    def rvi_signal_oversold(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: float = -20, T4: str = "EMA") -> np.ndarray:
        open = market_df['open'].values
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        _, signal_line = Relative_Vigor_Index(open, high, low, close, firstperiod=N1, secondperiod=N2, MA_Type=T4)
        return signal_line <= N3


# 基于波动大小过滤
if True:

    def mass_higher1(market_df: pd.DataFrame, N1: int, N2: int) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        mass = MASS(high, low, close, firstperiod=N1, secondperiod=N2)
        return mass > 1

    def mass_lower1(market_df: pd.DataFrame, N1: int, N2: int) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        mass = MASS(high, low, close, firstperiod=N1, secondperiod=N2)
        return mass <= 1

    def adx_higher_threshold(market_df: pd.DataFrame, N1: int = 14, N2: float = 25) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        adx = talib.ADX(high, low, close, timeperiod=N1)
        return adx > N2

    def adx_lower_threshold(market_df: pd.DataFrame, N1: int = 14, N2: float = 25) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        adx = talib.ADX(high, low, close, timeperiod=N1)
        return adx <= N2

    def atr_fast_higher_slow(market_df: pd.DataFrame, N1: int, N2: int) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        fast_atr = talib.ATR(high, low, close, timeperiod=N1)
        slow_atr = talib.ATR(high, low, close, timeperiod=N2)
        return fast_atr > slow_atr

    def atr_fast_lower_slow(market_df: pd.DataFrame, N1: int, N2: int) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        fast_atr = talib.ATR(high, low, close, timeperiod=N1)
        slow_atr = talib.ATR(high, low, close, timeperiod=N2)
        return fast_atr <= slow_atr

    def skew_positive(market_df: pd.DataFrame, N1: int, T2: str = "EMA") -> np.ndarray:
        price = market_df['close'].values
        skewness = Skew(price, timeperiod=N1, MA_Type=T2)
        return skewness > 0

    def skew_negative(market_df: pd.DataFrame, N1: int, T2: str = "EMA") -> np.ndarray:
        price = market_df['close'].values
        skewness = Skew(price, timeperiod=N1, MA_Type=T2)
        return skewness <= 0

    def convexity_higher1(market_df: pd.DataFrame, N1: int, T2: str = "SMA") -> np.ndarray:
        price = market_df['close'].values
        convexity = Convexity(price, timeperiod=N1, MA_Type=T2)
        return convexity > 1

    def convexity_lower1(market_df: pd.DataFrame, N1: int, T2: str = "SMA") -> np.ndarray:
        price = market_df['close'].values
        convexity = Convexity(price, timeperiod=N1, MA_Type=T2)
        return convexity <= 1

