from typing import Union
import numpy as np
import pandas as pd
import talib

from indicators import *


def crossover(array1: np.ndarray, array2: Union[np.ndarray, float, int]) -> np.ndarray:
    array1_shift1 = np.concatenate(([np.nan], array1[:-1]))
    if isinstance(array2, np.ndarray):
        array2_shift1 = np.concatenate(([np.nan], array2[:-1]))
        return (array1 > array2) & (array1_shift1 <= array2_shift1)
    else:
        return (array1 > array2) & (array1_shift1 <= array2)

def crossunder(array1: np.ndarray, array2: Union[np.ndarray, float, int]) -> np.ndarray:
    array1_shift1 = np.concatenate(([np.nan], array1[:-1]))
    if isinstance(array2, np.ndarray):
        array2_shift1 = np.concatenate(([np.nan], array2[:-1]))
        return (array1 <= array2) & (array1_shift1 > array2_shift1)
    else:
        return (array1 <= array2) & (array1_shift1 > array2)

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

def start_increase(array: np.ndarray, timeperiod: int) -> np.ndarray:
    inc = increase(array, timeperiod)
    prev_inc = np.concatenate(([False], inc[:-1]))
    return inc & (~prev_inc)

def start_decrease(array: np.ndarray, timeperiod: int) -> np.ndarray:
    dec = decrease(array, timeperiod)
    prev_dec = np.concatenate(([False], dec[:-1]))
    return dec & (~prev_dec)

"""信号条件函数（入场和出场）"""
def no_signal(market_df: pd.DataFrame) -> np.ndarray:
    return np.array([False] * len(market_df))


# 多头趋势入场
if True:

    def roc_crossover0(market_df: pd.DataFrame, N1: int) -> np.ndarray:
        price = market_df['close'].values
        roc = talib.ROC(price, timeperiod=N1)
        return crossover(roc, 0)

    def aroon_diff_crossover0(market_df: pd.DataFrame, N1: int) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        aroon_down, aroon_up = talib.AROON(high, low, timeperiod=N1)
        aroon_diff = aroon_up - aroon_down
        return crossover(aroon_diff, 0)

    def price_crossover_sma(market_df: pd.DataFrame, N1: int) -> np.ndarray:
        price = market_df['close'].values
        price_ma = talib.SMA(price, N1)
        return crossover(price, price_ma)

    def price_crossover_sma_2(market_df: pd.DataFrame, N1: int) -> np.ndarray:
        price = market_df['close'].values
        price_ma = talib.SMA(price, N1)
        return (crossover(price, price_ma) & increase(price_ma, N1)) | (start_increase(price_ma, N1) & (price > price_ma))

    def price_crossover_ema(market_df: pd.DataFrame, N1: int) -> np.ndarray:
        price = market_df['close'].values
        price_ma = talib.EMA(price, N1)
        return crossover(price, price_ma)

    def sma_fast_crossover_slow(market_df: pd.DataFrame, N1: int, N2: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.SMA(price, N1)
        slow_ma = talib.SMA(price, N2)
        return crossover(fast_ma, slow_ma) & increase(fast_ma, N1)

    def sma_fast_crossover_slow_2(market_df: pd.DataFrame, N1: int, N2: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.SMA(price, N1)
        slow_ma = talib.SMA(price, N2)
        return crossover(fast_ma, slow_ma) & increase(slow_ma, N2)

    def sma_fast_crossover_slow_3(market_df: pd.DataFrame, N1: int, N2: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.SMA(price, N1)
        slow_ma = talib.SMA(price, N2)
        return (crossover(fast_ma, slow_ma) & increase(fast_ma, N1)) | (start_increase(fast_ma, N1) & (fast_ma > slow_ma))

    def ema_fast_crossover_slow(market_df: pd.DataFrame, N1: int, N2: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.EMA(price, N1)
        slow_ma = talib.EMA(price, N2)
        return crossover(fast_ma, slow_ma)

    def smacd_start_increase(market_df: pd.DataFrame, N1: int = 12, N2: int = 26) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=N1, slowperiod=N2, signalperiod=9)
        return start_increase(macd_line, N1)

    def smacd_histogram_start_increase(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=N1, slowperiod=N2, signalperiod=N3)
        return start_increase(histogram, N1)

    def smacd_histogram_start_increase_2(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=N1, slowperiod=N2, signalperiod=N3)
        fast_ma = talib.SMA(price, N1)
        return (start_increase(histogram, N1) & increase(fast_ma, N1)) | (start_increase(fast_ma, N1) & increase(histogram, N1))

    def smacd_crossover_signal(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=N1, slowperiod=N2, signalperiod=N3)
        return crossover(histogram, 0)

    def smacd_crossover_signal_2(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=N1, slowperiod=N2, signalperiod=N3)
        fast_ma = talib.SMA(price, N1)
        return crossover(histogram, 0) & increase(fast_ma, N1)

    def smacd_crossover_signal_3(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=N1, slowperiod=N2, signalperiod=N3)
        slow_ma = talib.SMA(price, N2)
        return crossover(histogram, 0) & increase(slow_ma, N2)

    def emacd_start_increase(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=N1, slowperiod=N2, signalperiod=N3)
        return start_increase(macd_line, N1)

    def emacd_histogram_start_increase(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=N1, slowperiod=N2, signalperiod=N3)
        return start_increase(histogram, N1)

    def emacd_histogram_start_increase_2(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=N1, slowperiod=N2, signalperiod=N3)
        fast_ma = talib.EMA(price, N1)
        return (start_increase(histogram, N1) & increase(fast_ma, N1)) | (start_increase(fast_ma, N1) & increase(histogram, N1))

    def emacd_crossover_signal(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=N1, slowperiod=N2, signalperiod=N3)
        return crossover(histogram, 0)

    def emacd_crossover_signal_2(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=N1, slowperiod=N2, signalperiod=N3)
        fast_ma = talib.EMA(price, N1)
        return crossover(histogram, 0) & increase(fast_ma, N1)

    def emacd_crossover_signal_3(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=N1, slowperiod=N2, signalperiod=N3)
        slow_ma = talib.EMA(price, N2)
        return crossover(histogram, 0) & increase(slow_ma, N2)

    def trix_crossover0(market_df: pd.DataFrame, N1: int = 12) -> np.ndarray:
        price = market_df['close'].values
        trix = talib.TRIX(price, timeperiod=N1)
        return crossover(trix, 0)

    def trix_start_increase(market_df: pd.DataFrame, N1: int = 12) -> np.ndarray:
        price = market_df['close'].values
        trix = talib.TRIX(price, timeperiod=N1)
        return start_increase(trix, N1)

    def trix_crossover_signal(market_df: pd.DataFrame, N1: int = 12, N2: int = 12) -> np.ndarray:
        price = market_df['close'].values
        trix = talib.TRIX(price, timeperiod=N1)
        signal_line = talib.EMA(trix, timeperiod=N2)
        return crossover(trix, signal_line)

    def adx_plus_crossover_minus(market_df: pd.DataFrame, N1: int = 14) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        plus_di = talib.PLUS_DI(high, low, close, timeperiod=N1)
        minus_di = talib.MINUS_DI(high, low, close, timeperiod=N1)
        return crossover(plus_di, minus_di)

    def tsi_crossover_signal(market_df: pd.DataFrame, N1: int = 25, N2: int = 13, N3: int = 13, T4: str = "EMA") -> np.ndarray:
        close = market_df['close'].values
        tsi = TSI(close, firstperiod=N1, secondperiod=N2, MA_Type=T4)
        signal_line = MA(tsi, N3, T4)
        return crossover(tsi, signal_line)

    def rsi_fast_crossover_slow(market_df: pd.DataFrame, N1: int, N2: int) -> np.ndarray:
        price = market_df['close'].values
        fast_rsi = talib.RSI(price, timeperiod=N1)
        slow_rsi = talib.RSI(price, timeperiod=N2)
        return crossover(fast_rsi, slow_rsi)

    def supertrend_long_signal(market_df: pd.DataFrame, N1: int = 10, N2: int = 3) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        supertrend, trend = SuperTrend(high, low, close, int(N1), N2)
        shift1 = np.concatenate(([np.nan], trend[:-1]))
        return (trend == 1) & (shift1 == -1)

    def ma_atr_long_signal(market_df: pd.DataFrame, N1: int = 140, N2: int = 70, N3: float = 1.5) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        direction = Ma_Atr_Direction(high, low, close, N1, N2, N3)
        shift1 = np.concatenate(([np.nan], direction[:-1]))
        return (direction == 1) & (shift1 == -1)

    def second_wave_trend_1(market_df: pd.DataFrame, N1: int = 8) -> np.ndarray:
        """
        自定义趋势第二波段入场指标 1
        """

        def cond0_vectorized(is_negative: np.ndarray, window_size: int):
            """
            使用累积和完全向量化，无任何循环
            等价于 is_negative.rolling(window_size).sum() == 0
            """
            # 计算前缀和
            prefix_sum = np.cumsum(is_negative)
            
            # 初始化结果数组
            result = np.zeros(len(is_negative), dtype=bool)
            
            # 前 window_size-1 个位置：直接检查前缀和
            valid_indices = np.arange(min(window_size - 1, len(is_negative)))
            result[valid_indices] = prefix_sum[valid_indices] == 0
            
            # 后续位置：窗口和 = prefix_sum[i] - prefix_sum[i-window_size]
            if len(is_negative) >= window_size:
                window_sums = prefix_sum[window_size-1:] - np.concatenate(([0], prefix_sum[:-window_size]))
                result[window_size-1:] = window_sums == 0
            
            return result
        
        price = market_df['close'].values
        fast_ma = talib.EMA(price, timeperiod=N1)
        slow_ma = talib.EMA(fast_ma, timeperiod=N1)

        fast_ma_slope = np.diff(fast_ma, prepend=np.nan)
        slow_ma_slope = np.diff(slow_ma, prepend=np.nan)
        fast_ma_slope_abs = np.abs(fast_ma_slope)
        slow_ma_slope_abs = np.abs(slow_ma_slope)

        is_negative = slow_ma_slope <= 0
        cond0 = cond0_vectorized(is_negative, N1)  # slow_ma 持续上涨
        cond1 = decrease(slow_ma_slope_abs, N1*2)  # slow_ma 斜率变缓
        cond2 = fast_ma_slope <= 0                         # fast_ma 下跌
        cond3 = decrease(fast_ma_slope_abs, N1)    # fast_ma 斜率变缓
        cond4 = increase(price, int(N1/2))         # 价格 上涨
        
        entry_cond = cond0 & cond1 & cond2 & cond3 & cond4
        
        return entry_cond

    def second_wave_trend_2(market_df: pd.DataFrame, N1: int = 8) -> np.ndarray:
        """
        自定义趋势第二波段入场指标 2
        相比指标 1 ，指标 2 的入场条件更宽松，交易次数大约翻倍
        """

        def cond0_vectorized(is_negative: np.ndarray, window_size: int):
            """
            使用累积和完全向量化，无任何循环
            等价于 is_negative.rolling(window_size).sum() == 0
            """
            # 计算前缀和
            prefix_sum = np.cumsum(is_negative)
            
            # 初始化结果数组
            result = np.zeros(len(is_negative), dtype=bool)
            
            # 前 window_size-1 个位置：直接检查前缀和
            valid_indices = np.arange(min(window_size - 1, len(is_negative)))
            result[valid_indices] = prefix_sum[valid_indices] == 0
            
            # 后续位置：窗口和 = prefix_sum[i] - prefix_sum[i-window_size]
            if len(is_negative) >= window_size:
                window_sums = prefix_sum[window_size-1:] - np.concatenate(([0], prefix_sum[:-window_size]))
                result[window_size-1:] = window_sums == 0
            
            return result
        
        price = market_df['close'].values
        fast_ma = talib.EMA(price, timeperiod=N1)
        slow_ma = talib.EMA(fast_ma, timeperiod=N1)

        fast_ma_slope = np.diff(fast_ma, prepend=np.nan)
        slow_ma_slope = np.diff(slow_ma, prepend=np.nan)
        fast_ma_slope_abs = np.abs(fast_ma_slope)
        slow_ma_slope_abs = np.abs(slow_ma_slope)
        fast_ma_shift_slope = np.concatenate(([np.nan], fast_ma_slope[:-1]))
        slow_ma_shift_slope_abs = np.concatenate(([np.nan], slow_ma_slope_abs[:-1]))

        is_negative = slow_ma_slope <= 0
        cond0 = cond0_vectorized(is_negative, N1)        # slow_ma 持续上涨
        cond1 = decrease(slow_ma_shift_slope_abs, N1*2)  # slow_ma_shift 斜率变缓
        cond2 = fast_ma_shift_slope <= 0                         # fast_ma_shift 下跌
        cond3 = decrease(fast_ma_slope_abs, N1)          # fast_ma 斜率变缓
        
        entry_cond = cond0 & cond1 & cond2 & cond3
        
        return entry_cond

    def bb_price_crossover_low(market_df: pd.DataFrame, N1: int, N2: float) -> np.ndarray:
        price = market_df['close'].values
        upper_band, middle_band, lower_band = talib.BBANDS(price, timeperiod=N1, nbdevup=N2, nbdevdn=N2)
        return crossover(price, lower_band)

    def bb_price_crossover_low_2(market_df: pd.DataFrame, N1: int, N2: float) -> np.ndarray:
        price = market_df['close'].values
        upper_band, middle_band, lower_band = talib.BBANDS(price, timeperiod=N1, nbdevup=N2, nbdevdn=N2)
        return crossover(price, lower_band) & increase(lower_band, N1)

    def bb_price_crossover_high(market_df: pd.DataFrame, N1: int, N2: float) -> np.ndarray:
        price = market_df['close'].values
        upper_band, middle_band, lower_band = talib.BBANDS(price, timeperiod=N1, nbdevup=N2, nbdevdn=N2)
        return crossover(price, upper_band)

    def bb_price_crossover_high_2(market_df: pd.DataFrame, N1: int, N2: float) -> np.ndarray:
        price = market_df['close'].values
        upper_band, middle_band, lower_band = talib.BBANDS(price, timeperiod=N1, nbdevup=N2, nbdevdn=N2)
        return crossover(price, upper_band) & increase(upper_band, N1)

    def kc_price_crossover_low(market_df: pd.DataFrame, N1: int, N2: int, N3: float) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        upper_band, middle_band, lower_band = KChannels(high, low, close, N1, N2, N3)
        return crossover(close, lower_band)

    def kc_price_crossover_low_2(market_df: pd.DataFrame, N1: int, N2: int, N3: float) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        upper_band, middle_band, lower_band = KChannels(high, low, close, N1, N2, N3)
        return crossover(close, lower_band) & increase(lower_band, N1)

    def kc_price_crossover_high(market_df: pd.DataFrame, N1: int, N2: int, N3: float) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        upper_band, middle_band, lower_band = KChannels(high, low, close, N1, N2, N3)
        return crossover(close, upper_band)

    def kc_price_crossover_high_2(market_df: pd.DataFrame, N1: int, N2: int, N3: float) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        upper_band, middle_band, lower_band = KChannels(high, low, close, N1, N2, N3)
        return crossover(close, upper_band) & increase(upper_band, N1)

    def stoch_k_crossover_d(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        slowk, slowd = talib.STOCH(high, low, close, fastk_period=N1, slowk_period=N2, slowd_period=N3)
        return crossover(slowk, slowd)

    def stoch_k_crossover_d_2(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3, N4: float = 20.0) -> np.ndarray:
        """低于 oversold_threshold 就上膛，金叉后清膛"""
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        slowk, slowd = talib.STOCH(high, low, close, fastk_period=N1, slowk_period=N2, slowd_period=N3)
        cross_signal = crossover(slowk, slowd)
        armed = slowk <= N4
        state = np.zeros_like(slowk, dtype=bool)   # 状态向量：False 未上膛， True 已上膛
        final_signal = np.zeros_like(cross_signal, dtype=bool)
        for i in range(len(slowk)):
            if i == 0:
                state[i] = True if armed[i] else False
            else:
                # 遇到金叉且当前已上膛 → 触发信号后清膛
                if cross_signal[i] and state[i-1]:
                    state[i] = False  # 清膛
                    final_signal[i] = True
                elif armed[i]:
                    state[i] = True  # 上膛
                else:
                    state[i] = state[i-1]
        return final_signal

    def stoch_k_crossover_d_3(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3, N4: int = 5) -> np.ndarray:
        close = market_df['close'].values
        ma_slope = EMA_SLOPE(close, timeperiod=N4)
        slowk, slowd = talib.STOCH(ma_slope, ma_slope, ma_slope, fastk_period=N1, slowk_period=N2, slowd_period=N3)
        return crossover(slowk, slowd)

    def stoch_k_crossover_d_4(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3, N4: int = 5, N5: float = 20.0) -> np.ndarray:
        """低于 oversold_threshold 就上膛，金叉后清膛"""
        close = market_df['close'].values
        ma_slope = EMA_SLOPE(close, timeperiod=N4)
        slowk, slowd = talib.STOCH(ma_slope, ma_slope, ma_slope, fastk_period=N1, slowk_period=N2, slowd_period=N3)
        cross_signal = crossover(slowk, slowd)
        armed = slowk <= N5
        state = np.zeros_like(slowk, dtype=bool)   # 状态向量：False 未上膛， True 已上膛
        final_signal = np.zeros_like(cross_signal, dtype=bool)
        for i in range(len(slowk)):
            if i == 0:
                state[i] = True if armed[i] else False
            else:
                # 遇到金叉且当前已上膛 → 触发信号后清膛
                if cross_signal[i] and state[i-1]:
                    state[i] = False  # 清膛
                    final_signal[i] = True
                elif armed[i]:
                    state[i] = True  # 上膛
                else:
                    state[i] = state[i-1]
        return final_signal

    def kdj_k_crossover_d(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        k, d = talib.STOCH(high, low, close, fastk_period=N1, slowk_period=N2, slowk_matype=talib.MA_Type.EMA, slowd_period=N3, slowd_matype=talib.MA_Type.EMA)
        return crossover(k, d)

    def kdj_k_crossover_d_2(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3, N4: float = 20.0) -> np.ndarray:
        """低于 oversold_threshold 就上膛，金叉后清膛"""
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        k, d = talib.STOCH(high, low, close, fastk_period=N1, slowk_period=N2, slowk_matype=talib.MA_Type.EMA, slowd_period=N3, slowd_matype=talib.MA_Type.EMA)
        cross_signal = crossover(k, d)
        armed = k <= N4
        state = np.zeros_like(k, dtype=bool)   # 状态向量：False 未上膛， True 已上膛
        final_signal = np.zeros_like(cross_signal, dtype=bool)
        for i in range(len(k)):
            if i == 0:
                state[i] = True if armed[i] else False
            else:
                # 遇到金叉且当前已上膛 → 触发信号后清膛
                if cross_signal[i] and state[i-1]:
                    state[i] = False  # 清膛
                    final_signal[i] = True
                elif armed[i]:
                    state[i] = True  # 上膛
                else:
                    state[i] = state[i-1]
        return final_signal

    def kdj_k_crossover_d_3(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3, N4: int = 5) -> np.ndarray:
        close = market_df['close'].values
        ma_slope = EMA_SLOPE(close, timeperiod=N4)
        k, d = talib.STOCH(ma_slope, ma_slope, ma_slope, fastk_period=N1, slowk_period=N2, slowk_matype=talib.MA_Type.EMA, slowd_period=N3, slowd_matype=talib.MA_Type.EMA)
        return crossover(k, d)

    def kdj_k_crossover_d_4(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3, N4: int = 5, N5: float = 20.0) -> np.ndarray:
        """低于 oversold_threshold 就上膛，金叉后清膛"""
        close = market_df['close'].values
        ma_slope = EMA_SLOPE(close, timeperiod=N4)
        k, d = talib.STOCH(ma_slope, ma_slope, ma_slope, fastk_period=N1, slowk_period=N2, slowk_matype=talib.MA_Type.EMA, slowd_period=N3, slowd_matype=talib.MA_Type.EMA)
        cross_signal = crossover(k, d)
        armed = k <= N5
        state = np.zeros_like(k, dtype=bool)   # 状态向量：False 未上膛， True 已上膛
        final_signal = np.zeros_like(cross_signal, dtype=bool)
        for i in range(len(k)):
            if i == 0:
                state[i] = True if armed[i] else False
            else:
                # 遇到金叉且当前已上膛 → 触发信号后清膛
                if cross_signal[i] and state[i-1]:
                    state[i] = False  # 清膛
                    final_signal[i] = True
                elif armed[i]:
                    state[i] = True  # 上膛
                else:
                    state[i] = state[i-1]
        return final_signal

    def smi_k_crossover_d(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        smi, slowd = SMI(high, low, close, fastk_period=N1, slowk_period=N2, slowd_period=N3)
        return crossover(smi, slowd)

    def smi_k_crossover_d_2(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3, N4: float = -20.0) -> np.ndarray:
        """低于 oversold_threshold 就上膛，金叉后清膛"""
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        smi, slowd = SMI(high, low, close, fastk_period=N1, slowk_period=N2, slowd_period=N3)
        cross_signal = crossover(smi, slowd)
        armed = smi <= N4
        state = np.zeros_like(smi, dtype=bool)   # 状态向量：False 未上膛， True 已上膛
        final_signal = np.zeros_like(cross_signal, dtype=bool)
        for i in range(len(smi)):
            if i == 0:
                state[i] = True if armed[i] else False
            else:
                # 遇到金叉且当前已上膛 → 触发信号后清膛
                if cross_signal[i] and state[i-1]:
                    state[i] = False  # 清膛
                    final_signal[i] = True
                elif armed[i]:
                    state[i] = True  # 上膛
                else:
                    state[i] = state[i-1]
        return final_signal

    def smi_k_crossover_d_3(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3, N4: int = 5) -> np.ndarray:
        close = market_df['close'].values
        ma_slope = EMA_SLOPE(close, timeperiod=N4)
        smi, slowd = SMI(ma_slope, ma_slope, ma_slope, fastk_period=N1, slowk_period=N2, slowd_period=N3)
        return crossover(smi, slowd)

    def smi_k_crossover_d_4(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3, N4: int = 5, N5: float = -20.0) -> np.ndarray:
        """低于 oversold_threshold 就上膛，金叉后清膛"""
        close = market_df['close'].values
        ma_slope = EMA_SLOPE(close, timeperiod=N4)
        smi, slowd = SMI(ma_slope, ma_slope, ma_slope, fastk_period=N1, slowk_period=N2, slowd_period=N3)
        cross_signal = crossover(smi, slowd)
        armed = smi <= N5
        state = np.zeros_like(smi, dtype=bool)   # 状态向量：False 未上膛， True 已上膛
        final_signal = np.zeros_like(cross_signal, dtype=bool)
        for i in range(len(smi)):
            if i == 0:
                state[i] = True if armed[i] else False
            else:
                # 遇到金叉且当前已上膛 → 触发信号后清膛
                if cross_signal[i] and state[i-1]:
                    state[i] = False  # 清膛
                    final_signal[i] = True
                elif armed[i]:
                    state[i] = True  # 上膛
                else:
                    state[i] = state[i-1]
        return final_signal

    def rvi_crossover_signal(market_df: pd.DataFrame, N1: int = 5, N2: int = 3) -> np.ndarray:
        open = market_df['open'].values
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        rvi, signal_line = Relative_Vigor_Index(open, high, low, close, firstperiod=N1, secondperiod=N2)
        return crossover(rvi, signal_line)

    def tsi_crossover0(market_df: pd.DataFrame, N1: int = 25, N2: int = 13, T3: str = "EMA") -> np.ndarray:
        price = market_df['close'].values
        tsi = TSI(price, firstperiod=N1, secondperiod=N2, MA_Type=T3)
        return crossover(tsi, 0)

    def rsi_crossover50(market_df: pd.DataFrame, N1: int) -> np.ndarray:
        price = market_df['close'].values
        rsi = talib.RSI(price, timeperiod=N1)
        return crossover(rsi, 50)

    def stoch_k_crossover50(market_df: pd.DataFrame, N1: int = 5, N2: int = 3) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        slowk, _ = talib.STOCH(high, low, close, fastk_period=N1, slowk_period=N2, slowd_period=3)
        return crossover(slowk, 50)

    def stoch_d_crossover50(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        _, slowd = talib.STOCH(high, low, close, fastk_period=N1, slowk_period=N2, slowd_period=N3)
        return crossover(slowd, 50)

    def kdj_k_crossover50(market_df: pd.DataFrame, N1: int = 5, N2: int = 3) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        k , _ = talib.STOCH(high, low, close, fastk_period=N1, slowk_period=N2, slowk_matype=talib.MA_Type.EMA, slowd_period=3, slowd_matype=talib.MA_Type.EMA)
        return crossover(k, 50)

    def kdj_d_crossover50(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        _, d = talib.STOCH(high, low, close, fastk_period=N1, slowk_period=N2, slowk_matype=talib.MA_Type.EMA, slowd_period=N3, slowd_matype=talib.MA_Type.EMA)
        return crossover(d, 50)

    def smi_k_crossover0(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, T3: str = "EMA") -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        smi, _ = SMI(high, low, close, fastk_period=N1, slowk_period=N2, slowd_period=3, MA_Type=T3)
        return crossover(smi, 0)

    def smi_d_crossover0(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3, T4: str = "EMA") -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        _, slowd = SMI(high, low, close, fastk_period=N1, slowk_period=N2, slowd_period=N3, MA_Type=T4)
        return crossover(slowd, 0)

    def rvi_crossover0(market_df: pd.DataFrame, N1: int = 5, T2: str = "EMA") -> np.ndarray:
        open = market_df['open'].values
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        rvi, _ = Relative_Vigor_Index(open, high, low, close, firstperiod=N1, secondperiod=3, MA_Type=T2)
        return crossover(rvi, 0)

    def rvi_signal_crossover0(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, T3: str = "EMA") -> np.ndarray:
        open = market_df['open'].values
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        _, signal_line = Relative_Vigor_Index(open, high, low, close, firstperiod=N1, secondperiod=N2, MA_Type=T3)
        return crossover(signal_line, 0)


# 空头趋势入场
if True:

    def roc_crossunder0(market_df: pd.DataFrame, N1: int) -> np.ndarray:
        price = market_df['close'].values
        roc = talib.ROC(price, timeperiod=N1)
        return crossunder(roc, 0)

    def aroon_diff_crossunder0(market_df: pd.DataFrame, N1: int) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        aroon_down, aroon_up = talib.AROON(high, low, timeperiod=N1)
        aroon_diff = aroon_up - aroon_down
        return crossunder(aroon_diff, 0)

    def price_crossunder_sma(market_df: pd.DataFrame, N1: int) -> np.ndarray:
        price = market_df['close'].values
        price_ma = talib.SMA(price, N1)
        return crossunder(price, price_ma)

    def price_crossunder_sma_2(market_df: pd.DataFrame, N1: int) -> np.ndarray:
        price = market_df['close'].values
        price_ma = talib.SMA(price, N1)
        return (crossunder(price, price_ma) & decrease(price_ma, N1)) | (start_decrease(price_ma, N1) & (price <= price_ma))

    def price_crossunder_ema(market_df: pd.DataFrame, N1: int) -> np.ndarray:
        price = market_df['close'].values
        price_ma = talib.EMA(price, N1)
        return crossunder(price, price_ma)

    def sma_fast_crossunder_slow(market_df: pd.DataFrame, N1: int, N2: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.SMA(price, N1)
        slow_ma = talib.SMA(price, N2)
        return crossunder(fast_ma, slow_ma) & decrease(fast_ma, N1)

    def sma_fast_crossunder_slow_2(market_df: pd.DataFrame, N1: int, N2: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.SMA(price, N1)
        slow_ma = talib.SMA(price, N2)
        return crossunder(fast_ma, slow_ma) & decrease(slow_ma, N2)

    def sma_fast_crossunder_slow_3(market_df: pd.DataFrame, N1: int, N2: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.SMA(price, N1)
        slow_ma = talib.SMA(price, N2)
        return (crossunder(fast_ma, slow_ma) & decrease(fast_ma, N1)) | (start_decrease(fast_ma, N1) & (fast_ma <= slow_ma))

    def ema_fast_crossunder_slow(market_df: pd.DataFrame, N1: int, N2: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.EMA(price, N1)
        slow_ma = talib.EMA(price, N2)
        return crossunder(fast_ma, slow_ma)

    def smacd_start_decrease(market_df: pd.DataFrame, N1: int = 12, N2: int = 26) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=N1, slowperiod=N2, signalperiod=9)
        return start_decrease(macd_line, N1)

    def smacd_histogram_start_decrease(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=N1, slowperiod=N2, signalperiod=N3)
        return start_decrease(histogram, N1)

    def smacd_histogram_start_decrease_2(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=N1, slowperiod=N2, signalperiod=N3)
        fast_ma = talib.SMA(price, N1)
        return (start_decrease(histogram, N1) & decrease(fast_ma, N1)) | (start_decrease(fast_ma, N1) & decrease(histogram, N1))

    def smacd_crossunder_signal(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=N1, slowperiod=N2, signalperiod=N3)
        return crossunder(histogram, 0)

    def smacd_crossunder_signal_2(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=N1, slowperiod=N2, signalperiod=N3)
        fast_ma = talib.SMA(price, N1)
        return crossunder(histogram, 0) & decrease(fast_ma, N1)

    def smacd_crossunder_signal_3(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=N1, slowperiod=N2, signalperiod=N3)
        slow_ma = talib.SMA(price, N2)
        return crossunder(histogram, 0) & decrease(slow_ma, N2)

    def emacd_start_decrease(market_df: pd.DataFrame, N1: int = 12, N2: int = 26) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=N1, slowperiod=N2, signalperiod=9)
        return start_decrease(macd_line, N1)

    def emacd_histogram_start_decrease(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=N1, slowperiod=N2, signalperiod=N3)
        return start_decrease(histogram, N1)

    def emacd_histogram_start_decrease_2(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=N1, slowperiod=N2, signalperiod=N3)
        fast_ma = talib.EMA(price, N1)
        return (start_decrease(histogram, N1) & decrease(fast_ma, N1)) | (start_decrease(fast_ma, N1) & decrease(histogram, N1))

    def emacd_crossunder_signal(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=N1, slowperiod=N2, signalperiod=N3)
        return crossunder(histogram, 0)

    def emacd_crossunder_signal_2(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=N1, slowperiod=N2, signalperiod=N3)
        fast_ma = talib.EMA(price, N1)
        return crossunder(histogram, 0) & decrease(fast_ma, N1)

    def emacd_crossunder_signal_3(market_df: pd.DataFrame, N1: int = 12, N2: int = 26, N3: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=N1, slowperiod=N2, signalperiod=N3)
        slow_ma = talib.EMA(price, N2)
        return crossunder(histogram, 0) & decrease(slow_ma, N2)

    def trix_crossunder0(market_df: pd.DataFrame, N1: int = 12) -> np.ndarray:
        price = market_df['close'].values
        trix = talib.TRIX(price, timeperiod=N1)
        return crossunder(trix, 0)

    def trix_start_decrease(market_df: pd.DataFrame, N1: int = 12) -> np.ndarray:
        price = market_df['close'].values
        trix = talib.TRIX(price, timeperiod=N1)
        return start_decrease(trix, N1)

    def trix_crossunder_signal(market_df: pd.DataFrame, N1: int = 12, N2: int = 12) -> np.ndarray:
        price = market_df['close'].values
        trix = talib.TRIX(price, timeperiod=N1)
        signal_line = talib.EMA(trix, timeperiod=N2)
        return crossunder(trix, signal_line)

    def adx_plus_crossunder_minus(market_df: pd.DataFrame, N1: int = 14) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        plus_di = talib.PLUS_DI(high, low, close, timeperiod=N1)
        minus_di = talib.MINUS_DI(high, low, close, timeperiod=N1)
        return crossunder(plus_di, minus_di)

    def tsi_crossunder_signal(market_df: pd.DataFrame, N1: int = 25, N2: int = 13, N3: int = 13, T4: str = "EMA") -> np.ndarray:
        close = market_df['close'].values
        tsi = TSI(close, firstperiod=N1, secondperiod=N2)
        signal_line = MA(tsi, N3, T4)
        return crossunder(tsi, signal_line)

    def rsi_fast_crossunder_slow(market_df: pd.DataFrame, N1: int, N2: int) -> np.ndarray:
        price = market_df['close'].values
        fast_rsi = talib.RSI(price, timeperiod=N1)
        slow_rsi = talib.RSI(price, timeperiod=N2)
        return crossunder(fast_rsi, slow_rsi)

    def supertrend_short_signal(market_df: pd.DataFrame, N1: int = 10, N2: int = 3) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        supertrend, trend = SuperTrend(high, low, close, int(N1), N2)
        shift1 = np.concatenate(([np.nan], trend[:-1]))
        return (trend == -1) & (shift1 == 1)

    def ma_atr_short_signal(market_df: pd.DataFrame, N1: int = 140, N2: int = 70, N3: float = 1.5) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        direction = Ma_Atr_Direction(high, low, close, N1, N2, N3)
        shift1 = np.concatenate(([np.nan], direction[:-1]))
        return (direction == -1) & (shift1 == 1)

    def bb_price_crossunder_low(market_df: pd.DataFrame, N1: int, N2: float) -> np.ndarray:
        price = market_df['close'].values
        upper_band, middle_band, lower_band = talib.BBANDS(price, timeperiod=N1, nbdevup=N2, nbdevdn=N2)
        return crossunder(price, lower_band)

    def bb_price_crossunder_low_2(market_df: pd.DataFrame, N1: int, N2: float) -> np.ndarray:
        price = market_df['close'].values
        upper_band, middle_band, lower_band = talib.BBANDS(price, timeperiod=N1, nbdevup=N2, nbdevdn=N2)
        return crossunder(price, lower_band) & decrease(lower_band, N1)

    def bb_price_crossunder_high(market_df: pd.DataFrame, N1: int, N2: float) -> np.ndarray:
        price = market_df['close'].values
        upper_band, middle_band, lower_band = talib.BBANDS(price, timeperiod=N1, nbdevup=N2, nbdevdn=N2)
        return crossunder(price, upper_band)

    def bb_price_crossunder_high_2(market_df: pd.DataFrame, N1: int, N2: float) -> np.ndarray:
        price = market_df['close'].values
        upper_band, middle_band, lower_band = talib.BBANDS(price, timeperiod=N1, nbdevup=N2, nbdevdn=N2)
        return crossunder(price, upper_band) & decrease(upper_band, N1)

    def kc_price_crossunder_low(market_df: pd.DataFrame, N1: int, N2: int, N3: float) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        upper_band, middle_band, lower_band = KChannels(high, low, close, N1, N2, N3)
        return crossunder(close, lower_band)

    def kc_price_crossunder_low_2(market_df: pd.DataFrame, N1: int, N2: int, N3: float) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        upper_band, middle_band, lower_band = KChannels(high, low, close, N1, N2, N3)
        return crossunder(close, lower_band) & decrease(lower_band, N1)

    def kc_price_crossunder_high(market_df: pd.DataFrame, N1: int, N2: int, N3: float) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        upper_band, middle_band, lower_band = KChannels(high, low, close, N1, N2, N3)
        return crossunder(close, upper_band)

    def kc_price_crossunder_high_2(market_df: pd.DataFrame, N1: int, N2: int, N3: float) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        upper_band, middle_band, lower_band = KChannels(high, low, close, N1, N2, N3)
        return crossunder(close, upper_band) & decrease(upper_band, N1)

    def stoch_k_crossunder_d(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        slowk, slowd = talib.STOCH(high, low, close, fastk_period=N1, slowk_period=N2, slowd_period=N3)
        return crossunder(slowk, slowd)

    def stoch_k_crossunder_d_2(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3, N4: float = 80.0) -> np.ndarray:
        """高于 overbought_threshold 就上膛，金叉后清膛"""
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        slowk, slowd = talib.STOCH(high, low, close, fastk_period=N1, slowk_period=N2, slowd_period=N3)
        cross_signal = crossunder(slowk, slowd)
        armed = slowk > N4
        state = np.zeros_like(slowk, dtype=bool)   # 状态向量：False 未上膛， True 已上膛
        final_signal = np.zeros_like(cross_signal, dtype=bool)
        for i in range(len(slowk)):
            if i == 0:
                state[i] = True if armed[i] else False
            else:
                # 遇到金叉且当前已上膛 → 触发信号后清膛
                if cross_signal[i] and state[i-1]:
                    state[i] = False  # 清膛
                    final_signal[i] = True
                elif armed[i]:
                    state[i] = True  # 上膛
                else:
                    state[i] = state[i-1]
        return final_signal

    def stoch_k_crossunder_d_3(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3, N4: int = 5) -> np.ndarray:
        close = market_df['close'].values
        ma_slope = EMA_SLOPE(close, timeperiod=N4)
        slowk, slowd = talib.STOCH(ma_slope, ma_slope, ma_slope, fastk_period=N1, slowk_period=N2, slowd_period=N3)
        return crossunder(slowk, slowd)

    def stoch_k_crossunder_d_4(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3, N4: int = 5, N5: float = 80.0) -> np.ndarray:
        """高于 overbought_threshold 就上膛，金叉后清膛"""
        close = market_df['close'].values
        ma_slope = EMA_SLOPE(close, timeperiod=N4)
        slowk, slowd = talib.STOCH(ma_slope, ma_slope, ma_slope, fastk_period=N1, slowk_period=N2, slowd_period=N3)
        cross_signal = crossunder(slowk, slowd)
        armed = slowk > N5
        state = np.zeros_like(slowk, dtype=bool)   # 状态向量：False 未上膛， True 已上膛
        final_signal = np.zeros_like(cross_signal, dtype=bool)
        for i in range(len(slowk)):
            if i == 0:
                state[i] = True if armed[i] else False
            else:
                # 遇到金叉且当前已上膛 → 触发信号后清膛
                if cross_signal[i] and state[i-1]:
                    state[i] = False  # 清膛
                    final_signal[i] = True
                elif armed[i]:
                    state[i] = True  # 上膛
                else:
                    state[i] = state[i-1]
        return final_signal

    def kdj_k_crossunder_d(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        k, d = talib.STOCH(high, low, close, fastk_period=N1, slowk_period=N2, slowk_matype=talib.MA_Type.EMA, slowd_period=N3, slowd_matype=talib.MA_Type.EMA)
        return crossunder(k, d)

    def kdj_k_crossunder_d_2(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3, N4: float = 80.0) -> np.ndarray:
        """高于 overbought_threshold 就上膛，金叉后清膛"""
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        k, d = talib.STOCH(high, low, close, fastk_period=N1, slowk_period=N2, slowk_matype=talib.MA_Type.EMA, slowd_period=N3, slowd_matype=talib.MA_Type.EMA)
        cross_signal = crossunder(k, d)
        armed = k > N4
        state = np.zeros_like(k, dtype=bool)   # 状态向量：False 未上膛， True 已上膛
        final_signal = np.zeros_like(cross_signal, dtype=bool)
        for i in range(len(k)):
            if i == 0:
                state[i] = True if armed[i] else False
            else:
                # 遇到金叉且当前已上膛 → 触发信号后清膛
                if cross_signal[i] and state[i-1]:
                    state[i] = False  # 清膛
                    final_signal[i] = True
                elif armed[i]:
                    state[i] = True  # 上膛
                else:
                    state[i] = state[i-1]
        return final_signal

    def kdj_k_crossunder_d_3(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3, N4: int = 5) -> np.ndarray:
        close = market_df['close'].values
        ma_slope = EMA_SLOPE(close, timeperiod=N4)
        k, d = talib.STOCH(ma_slope, ma_slope, ma_slope, fastk_period=N1, slowk_period=N2, slowk_matype=talib.MA_Type.EMA, slowd_period=N3, slowd_matype=talib.MA_Type.EMA)
        return crossunder(k, d)

    def kdj_k_crossunder_d_4(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3, N4: int = 5, N5: float = 80.0) -> np.ndarray:
        """高于 overbought_threshold 就上膛，金叉后清膛"""
        close = market_df['close'].values
        ma_slope = EMA_SLOPE(close, timeperiod=N4)
        k, d = talib.STOCH(ma_slope, ma_slope, ma_slope, fastk_period=N1, slowk_period=N2, slowk_matype=talib.MA_Type.EMA, slowd_period=N3, slowd_matype=talib.MA_Type.EMA)
        cross_signal = crossunder(k, d)
        armed = k > N5
        state = np.zeros_like(k, dtype=bool)   # 状态向量：False 未上膛， True 已上膛
        final_signal = np.zeros_like(cross_signal, dtype=bool)
        for i in range(len(k)):
            if i == 0:
                state[i] = True if armed[i] else False
            else:
                # 遇到金叉且当前已上膛 → 触发信号后清膛
                if cross_signal[i] and state[i-1]:
                    state[i] = False  # 清膛
                    final_signal[i] = True
                elif armed[i]:
                    state[i] = True  # 上膛
                else:
                    state[i] = state[i-1]
        return final_signal

    def smi_k_crossunder_d(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        smi, slowd = SMI(high, low, close, fastk_period=N1, slowk_period=N2, slowd_period=N3)
        return crossunder(smi, slowd)

    def smi_k_crossunder_d_2(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3, N4: float = 20.0) -> np.ndarray:
        """高于 overbought_threshold 就上膛，金叉后清膛"""
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        smi, slowd = SMI(high, low, close, fastk_period=N1, slowk_period=N2, slowd_period=N3)
        cross_signal = crossunder(smi, slowd)
        armed = smi > N4
        state = np.zeros_like(smi, dtype=bool)   # 状态向量：False 未上膛， True 已上膛
        final_signal = np.zeros_like(cross_signal, dtype=bool)
        for i in range(len(smi)):
            if i == 0:
                state[i] = True if armed[i] else False
            else:
                # 遇到金叉且当前已上膛 → 触发信号后清膛
                if cross_signal[i] and state[i-1]:
                    state[i] = False  # 清膛
                    final_signal[i] = True
                elif armed[i]:
                    state[i] = True  # 上膛
                else:
                    state[i] = state[i-1]
        return final_signal

    def smi_k_crossunder_d_3(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3, N4: int = 5) -> np.ndarray:
        close = market_df['close'].values
        ma_slope = EMA_SLOPE(close, timeperiod=N4)
        smi, slowd = SMI(ma_slope, ma_slope, ma_slope, fastk_period=N1, slowk_period=N2, slowd_period=N3)
        return crossunder(smi, slowd)

    def smi_k_crossunder_d_4(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3, N4: int = 5, N5: float = 20.0) -> np.ndarray:
        """高于 overbought_threshold 就上膛，金叉后清膛"""
        close = market_df['close'].values
        ma_slope = EMA_SLOPE(close, timeperiod=N4)
        smi, slowd = SMI(ma_slope, ma_slope, ma_slope, fastk_period=N1, slowk_period=N2, slowd_period=N3)
        cross_signal = crossunder(smi, slowd)
        armed = smi > N5
        state = np.zeros_like(smi, dtype=bool)   # 状态向量：False 未上膛， True 已上膛
        final_signal = np.zeros_like(cross_signal, dtype=bool)
        for i in range(len(smi)):
            if i == 0:
                state[i] = True if armed[i] else False
            else:
                # 遇到金叉且当前已上膛 → 触发信号后清膛
                if cross_signal[i] and state[i-1]:
                    state[i] = False  # 清膛
                    final_signal[i] = True
                elif armed[i]:
                    state[i] = True  # 上膛
                else:
                    state[i] = state[i-1]
        return final_signal

    def rvi_crossunder_signal(market_df: pd.DataFrame, N1: int = 5, N2: int = 3) -> np.ndarray:
        open = market_df['open'].values
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        rvi, signal_line = Relative_Vigor_Index(open, high, low, close, firstperiod=N1, secondperiod=N2)
        return crossunder(rvi, signal_line)

    def tsi_crossunder0(market_df: pd.DataFrame, N1: int = 25, N2: int = 13, T3: str = "EMA") -> np.ndarray:
        price = market_df['close'].values
        tsi = TSI(price, firstperiod=N1, secondperiod=N2, MA_Type=T3)
        return crossunder(tsi, 0)

    def rsi_crossunder50(market_df: pd.DataFrame, N1: int) -> np.ndarray:
        price = market_df['close'].values
        rsi = talib.RSI(price, timeperiod=N1)
        return crossunder(rsi, 50)

    def stoch_k_crossunder50(market_df: pd.DataFrame, N1: int = 5, N2: int = 3) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        slowk, _ = talib.STOCH(high, low, close, fastk_period=N1, slowk_period=N2, slowd_period=3)
        return crossunder(slowk, 50)

    def stoch_d_crossunder50(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        _, slowd = talib.STOCH(high, low, close, fastk_period=N1, slowk_period=N2, slowd_period=N3)
        return crossunder(slowd, 50)

    def kdj_k_crossunder50(market_df: pd.DataFrame, N1: int = 5, N2: int = 3) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        k , _ = talib.STOCH(high, low, close, fastk_period=N1, slowk_period=N2, slowk_matype=talib.MA_Type.EMA, slowd_period=3, slowd_matype=talib.MA_Type.EMA)
        return crossunder(k, 50)

    def kdj_d_crossunder50(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        _, d = talib.STOCH(high, low, close, fastk_period=N1, slowk_period=N2, slowk_matype=talib.MA_Type.EMA, slowd_period=N3, slowd_matype=talib.MA_Type.EMA)
        return crossunder(d, 50)

    def smi_k_crossunder0(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, T3: str = "EMA") -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        smi, _ = SMI(high, low, close, fastk_period=N1, slowk_period=N2, slowd_period=3, MA_Type=T3)
        return crossunder(smi, 0)

    def smi_d_crossunder0(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, N3: int = 3, T4: str = "EMA") -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        _, slowd = SMI(high, low, close, fastk_period=N1, slowk_period=N2, slowd_period=N3, MA_Type=T4)
        return crossunder(slowd, 0)

    def rvi_crossunder0(market_df: pd.DataFrame, N1: int = 5, T2: str = "EMA") -> np.ndarray:
        open = market_df['open'].values
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        rvi, _ = Relative_Vigor_Index(open, high, low, close, firstperiod=N1, secondperiod=3, MA_Type=T2)
        return crossunder(rvi, 0)

    def rvi_signal_crossunder0(market_df: pd.DataFrame, N1: int = 5, N2: int = 3, T3: str = "EMA") -> np.ndarray:
        open = market_df['open'].values
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        _, signal_line = Relative_Vigor_Index(open, high, low, close, firstperiod=N1, secondperiod=N2, MA_Type=T3)
        return crossunder(signal_line, 0)


# 基于波动大小入场
if True:
    def mass_crossover1(market_df: pd.DataFrame, N1: int, N2: int) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        mass = MASS(high, low, close, firstperiod=N1, secondperiod=N2)
        return crossover(mass, 1)

    def mass_crossunder1(market_df: pd.DataFrame, N1: int, N2: int) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        mass = MASS(high, low, close, firstperiod=N1, secondperiod=N2)
        return crossunder(mass, 1)

    def adx_crossover_threshold(market_df: pd.DataFrame, N1: int = 14, N2: float = 25) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        adx = talib.ADX(high, low, close, timeperiod=N1)
        return crossover(adx, N2)

    def adx_crossunder_threshold(market_df: pd.DataFrame, N1: int = 14, N2: float = 25) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        adx = talib.ADX(high, low, close, timeperiod=N1)
        return crossunder(adx, N2)
