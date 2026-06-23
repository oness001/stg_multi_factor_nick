from typing import Union

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
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

if True:

    # 信号条件函数（点位）
    def roc_crossover0(market_df: pd.DataFrame, timeperiod: int) -> np.ndarray:
        price = market_df['close'].values
        roc = talib.ROC(price, timeperiod=timeperiod)
        return crossover(roc, 0)

    def aroon_diff_crossover0(market_df: pd.DataFrame, timeperiod: int) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        aroon_down, aroon_up = talib.AROON(high, low, timeperiod=timeperiod)
        aroon_diff = aroon_up - aroon_down
        return crossover(aroon_diff, 0)

    def price_crossover_sma(market_df: pd.DataFrame, timeperiod: int) -> np.ndarray:
        price = market_df['close'].values
        price_ma = talib.SMA(price, timeperiod)
        return crossover(price, price_ma)

    def price_crossover_sma_2(market_df: pd.DataFrame, timeperiod: int) -> np.ndarray:
        price = market_df['close'].values
        price_ma = talib.SMA(price, timeperiod)
        return (crossover(price, price_ma) & increase(price_ma, timeperiod)) | (start_increase(price_ma, timeperiod) & (price > price_ma))

    def sma_fast_crossover_slow(market_df: pd.DataFrame, fastperiod: int, slowperiod: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.SMA(price, fastperiod)
        slow_ma = talib.SMA(price, slowperiod)
        return crossover(fast_ma, slow_ma) & increase(fast_ma, fastperiod)

    def sma_fast_crossover_slow_2(market_df: pd.DataFrame, fastperiod: int, slowperiod: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.SMA(price, fastperiod)
        slow_ma = talib.SMA(price, slowperiod)
        return crossover(fast_ma, slow_ma) & increase(slow_ma, slowperiod)

    def sma_fast_crossover_slow_3(market_df: pd.DataFrame, fastperiod: int, slowperiod: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.SMA(price, fastperiod)
        slow_ma = talib.SMA(price, slowperiod)
        return (crossover(fast_ma, slow_ma) & increase(fast_ma, fastperiod)) | (start_increase(fast_ma, fastperiod) & (fast_ma > slow_ma))

    def sma_first_crossover_second(market_df: pd.DataFrame, firstperiod: int, secondperiod: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.SMA(price, firstperiod)
        slow_ma = talib.SMA(fast_ma, secondperiod)
        return crossover(fast_ma, slow_ma) & increase(fast_ma, firstperiod)

    def sma_first_crossover_second_2(market_df: pd.DataFrame, firstperiod: int, secondperiod: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.SMA(price, firstperiod)
        slow_ma = talib.SMA(fast_ma, secondperiod)
        return crossover(fast_ma, slow_ma) & increase(slow_ma, firstperiod+secondperiod)

    def sma_first_crossover_second_3(market_df: pd.DataFrame, firstperiod: int, secondperiod: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.SMA(price, firstperiod)
        slow_ma = talib.SMA(fast_ma, secondperiod)
        return (crossover(fast_ma, slow_ma) & increase(fast_ma, firstperiod)) | (start_increase(fast_ma, firstperiod) & (fast_ma > slow_ma))

    def price_crossover_ema(market_df: pd.DataFrame, timeperiod: int) -> np.ndarray:
        price = market_df['close'].values
        price_ma = talib.EMA(price, timeperiod)
        return crossover(price, price_ma)

    def ema_fast_crossover_slow(market_df: pd.DataFrame, fastperiod: int, slowperiod: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.EMA(price, fastperiod)
        slow_ma = talib.EMA(price, slowperiod)
        return crossover(fast_ma, slow_ma)

    def ema_first_crossover_second(market_df: pd.DataFrame, firstperiod: int, secondperiod: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.EMA(price, firstperiod)
        slow_ma = talib.EMA(fast_ma, secondperiod)
        return crossover(fast_ma, slow_ma)

    def smacd_start_increase(market_df: pd.DataFrame, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        return start_increase(macd_line, fastperiod)

    def smacd_crossover_signal(market_df: pd.DataFrame, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        return crossover(histogram, 0)

    def smacd_crossover_signal_2(market_df: pd.DataFrame, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        fast_ma = talib.SMA(price, fastperiod)
        return crossover(histogram, 0) & increase(fast_ma, fastperiod)

    def smacd_crossover_signal_3(market_df: pd.DataFrame, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        slow_ma = talib.SMA(price, slowperiod)
        return crossover(histogram, 0) & increase(slow_ma, slowperiod)

    def smacd_histogram_start_increase(market_df: pd.DataFrame, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        return start_increase(histogram, fastperiod)

    def smacd_histogram_start_increase_2(market_df: pd.DataFrame, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        fast_ma = talib.SMA(price, fastperiod)
        return (start_increase(histogram, fastperiod) & increase(fast_ma, fastperiod)) | (start_increase(fast_ma, fastperiod) & increase(histogram, fastperiod))

    def smacd2_start_increase(market_df: pd.DataFrame, firstperiod: int = 12, secondperiod: int = 12, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        fast_ma, slow_ma, macd_line, signal_line, histogram = SMACD_2(price, firstperiod=firstperiod, secondperiod=secondperiod, signalperiod=signalperiod)
        return start_increase(macd_line, firstperiod)

    def smacd2_crossover_signal(market_df: pd.DataFrame, firstperiod: int = 12, secondperiod: int = 12, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        fast_ma, slow_ma, macd_line, signal_line, histogram = SMACD_2(price, firstperiod=firstperiod, secondperiod=secondperiod, signalperiod=signalperiod)
        return crossover(histogram, 0)

    def smacd2_crossover_signal_2(market_df: pd.DataFrame, firstperiod: int = 12, secondperiod: int = 12, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        fast_ma, slow_ma, macd_line, signal_line, histogram = SMACD_2(price, firstperiod=firstperiod, secondperiod=secondperiod, signalperiod=signalperiod)
        return crossover(histogram, 0) & increase(fast_ma, firstperiod)

    def smacd2_crossover_signal_3(market_df: pd.DataFrame, firstperiod: int = 12, secondperiod: int = 12, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        fast_ma, slow_ma, macd_line, signal_line, histogram = SMACD_2(price, firstperiod=firstperiod, secondperiod=secondperiod, signalperiod=signalperiod)
        return crossover(histogram, 0) & increase(slow_ma, firstperiod+secondperiod)

    def smacd2_histogram_start_increase(market_df: pd.DataFrame, firstperiod: int = 12, secondperiod: int = 12, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        fast_ma, slow_ma, macd_line, signal_line, histogram = SMACD_2(price, firstperiod=firstperiod, secondperiod=secondperiod, signalperiod=signalperiod)
        return start_increase(histogram, firstperiod)

    def smacd2_histogram_start_increase_2(market_df: pd.DataFrame, firstperiod: int = 12, secondperiod: int = 12, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        fast_ma, slow_ma, macd_line, signal_line, histogram = SMACD_2(price, firstperiod=firstperiod, secondperiod=secondperiod, signalperiod=signalperiod)
        return (start_increase(histogram, firstperiod) & increase(fast_ma, firstperiod)) | (start_increase(fast_ma, firstperiod) & increase(histogram, firstperiod))

    def emacd_start_increase(market_df: pd.DataFrame, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        return start_increase(macd_line, fastperiod)

    def emacd_crossover_signal(market_df: pd.DataFrame, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        return crossover(histogram, 0)

    def emacd_crossover_signal_2(market_df: pd.DataFrame, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        fast_ma = talib.EMA(price, fastperiod)
        return crossover(histogram, 0) & increase(fast_ma, fastperiod)

    def emacd_crossover_signal_3(market_df: pd.DataFrame, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        slow_ma = talib.EMA(price, slowperiod)
        return crossover(histogram, 0) & increase(slow_ma, slowperiod)

    def emacd_histogram_start_increase(market_df: pd.DataFrame, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        return start_increase(histogram, fastperiod)

    def emacd_histogram_start_increase_2(market_df: pd.DataFrame, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        fast_ma = talib.EMA(price, fastperiod)
        return (start_increase(histogram, fastperiod) & increase(fast_ma, fastperiod)) | (start_increase(fast_ma, fastperiod) & increase(histogram, fastperiod))

    def emacd2_start_increase(market_df: pd.DataFrame, firstperiod: int = 12, secondperiod: int = 12, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        fast_ma, slow_ma, macd_line, signal_line, histogram = MACD_2(price, firstperiod=firstperiod, secondperiod=secondperiod, signalperiod=signalperiod)
        return start_increase(macd_line, firstperiod)

    def emacd2_crossover_signal(market_df: pd.DataFrame, firstperiod: int = 12, secondperiod: int = 12, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        fast_ma, slow_ma, macd_line, signal_line, histogram = MACD_2(price, firstperiod=firstperiod, secondperiod=secondperiod, signalperiod=signalperiod)
        return crossover(histogram, 0)

    def emacd2_crossover_signal_2(market_df: pd.DataFrame, firstperiod: int = 12, secondperiod: int = 12, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        fast_ma, slow_ma, macd_line, signal_line, histogram = MACD_2(price, firstperiod=firstperiod, secondperiod=secondperiod, signalperiod=signalperiod)
        return crossover(histogram, 0) & increase(fast_ma, firstperiod)

    def emacd2_crossover_signal_3(market_df: pd.DataFrame, firstperiod: int = 12, secondperiod: int = 12, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        fast_ma, slow_ma, macd_line, signal_line, histogram = MACD_2(price, firstperiod=firstperiod, secondperiod=secondperiod, signalperiod=signalperiod)
        return crossover(histogram, 0) & increase(slow_ma, firstperiod+secondperiod)

    def emacd2_histogram_start_increase(market_df: pd.DataFrame, firstperiod: int = 12, secondperiod: int = 12, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        fast_ma, slow_ma, macd_line, signal_line, histogram = MACD_2(price, firstperiod=firstperiod, secondperiod=secondperiod, signalperiod=signalperiod)
        return start_increase(histogram, firstperiod)

    def emacd2_histogram_start_increase_2(market_df: pd.DataFrame, firstperiod: int = 12, secondperiod: int = 12, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        fast_ma, slow_ma, macd_line, signal_line, histogram = MACD_2(price, firstperiod=firstperiod, secondperiod=secondperiod, signalperiod=signalperiod)
        return (start_increase(histogram, firstperiod) & increase(fast_ma, firstperiod)) | (start_increase(fast_ma, firstperiod) & increase(histogram, firstperiod))

    def trix_crossover0(market_df: pd.DataFrame, timeperiod: int = 12) -> np.ndarray:
        price = market_df['close'].values
        trix = talib.TRIX(price, timeperiod=timeperiod)
        return crossover(trix, 0)

    def trix_start_increase(market_df: pd.DataFrame, timeperiod: int = 12) -> np.ndarray:
        price = market_df['close'].values
        trix = talib.TRIX(price, timeperiod=timeperiod)
        return start_increase(trix, timeperiod)

    def bb_price_crossover_low(market_df: pd.DataFrame, timeperiod: int, nbdev: float) -> np.ndarray:
        price = market_df['close'].values
        upper_band, middle_band, lower_band = talib.BBANDS(price, timeperiod=timeperiod, nbdevup=nbdev, nbdevdn=nbdev)
        return crossover(price, lower_band)

    def bb_price_crossover_low_2(market_df: pd.DataFrame, timeperiod: int, nbdev: float) -> np.ndarray:
        price = market_df['close'].values
        upper_band, middle_band, lower_band = talib.BBANDS(price, timeperiod=timeperiod, nbdevup=nbdev, nbdevdn=nbdev)
        return crossover(price, lower_band) & increase(lower_band, timeperiod)

    def bb_price_crossover_high(market_df: pd.DataFrame, timeperiod: int, nbdev: float) -> np.ndarray:
        price = market_df['close'].values
        upper_band, middle_band, lower_band = talib.BBANDS(price, timeperiod=timeperiod, nbdevup=nbdev, nbdevdn=nbdev)
        return crossover(price, upper_band)

    def bb_price_crossover_high_2(market_df: pd.DataFrame, timeperiod: int, nbdev: float) -> np.ndarray:
        price = market_df['close'].values
        upper_band, middle_band, lower_band = talib.BBANDS(price, timeperiod=timeperiod, nbdevup=nbdev, nbdevdn=nbdev)
        return crossover(price, upper_band) & increase(upper_band, timeperiod)

    def kc_price_crossover_low(market_df: pd.DataFrame, timeperiod: int, atr_timeperiod: int, multiplier: float) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        upper_band, middle_band, lower_band = KChannels(high, low, close, timeperiod, atr_timeperiod, multiplier)
        return crossover(close, lower_band)

    def kc_price_crossover_low_2(market_df: pd.DataFrame, timeperiod: int, atr_timeperiod: int, multiplier: float) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        upper_band, middle_band, lower_band = KChannels(high, low, close, timeperiod, atr_timeperiod, multiplier)
        return crossover(close, lower_band) & increase(lower_band, timeperiod)

    def kc_price_crossover_high(market_df: pd.DataFrame, timeperiod: int, atr_timeperiod: int, multiplier: float) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        upper_band, middle_band, lower_band = KChannels(high, low, close, timeperiod, atr_timeperiod, multiplier)
        return crossover(close, upper_band)

    def kc_price_crossover_high_2(market_df: pd.DataFrame, timeperiod: int, atr_timeperiod: int, multiplier: float) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        upper_band, middle_band, lower_band = KChannels(high, low, close, timeperiod, atr_timeperiod, multiplier)
        return crossover(close, upper_band) & increase(upper_band, timeperiod)

    def mass_crossover1(market_df: pd.DataFrame, firstperiod: int, secondperiod: int) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        mass = MASS(high, low, close, firstperiod=firstperiod, secondperiod=secondperiod)
        return crossover(mass, 1)

    def mass_crossunder1(market_df: pd.DataFrame, firstperiod: int, secondperiod: int) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        mass = MASS(high, low, close, firstperiod=firstperiod, secondperiod=secondperiod)
        return crossunder(mass, 1)

    def stoch_k_crossover_d(market_df: pd.DataFrame, fastk_period: int = 5, slowk_period: int = 3, slowd_period: int = 3) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        slowk, slowd = talib.STOCH(high, low, close, fastk_period=fastk_period, slowk_period=slowk_period, slowd_period=slowd_period)
        return crossover(slowk, slowd)

    def stoch_k_crossover_d_2(market_df: pd.DataFrame, fastk_period: int = 5, slowk_period: int = 3, slowd_period: int = 3, oversold_threshold: float = 20.0) -> np.ndarray:
        """低于 oversold_threshold 就上膛，金叉后清膛"""
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        slowk, slowd = talib.STOCH(high, low, close, fastk_period=fastk_period, slowk_period=slowk_period, slowd_period=slowd_period)
        cross_signal = crossover(slowk, slowd)
        armed = slowk <= oversold_threshold
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

    def stoch_k_crossover_d_3(market_df: pd.DataFrame, fastk_period: int = 5, slowk_period: int = 3, slowd_period: int = 3) -> np.ndarray:
        close = market_df['close'].values
        ma_slope = EMA_SLOPE(close, timeperiod=fastk_period)
        slowk, slowd = talib.STOCH(ma_slope, ma_slope, ma_slope, fastk_period=fastk_period, slowk_period=slowk_period, slowd_period=slowd_period)
        return crossover(slowk, slowd)

    def stoch_k_crossover_d_4(market_df: pd.DataFrame, fastk_period: int = 5, slowk_period: int = 3, slowd_period: int = 3, oversold_threshold: float = 20.0) -> np.ndarray:
        """低于 oversold_threshold 就上膛，金叉后清膛"""
        close = market_df['close'].values
        ma_slope = EMA_SLOPE(close, timeperiod=fastk_period)
        slowk, slowd = talib.STOCH(ma_slope, ma_slope, ma_slope, fastk_period=fastk_period, slowk_period=slowk_period, slowd_period=slowd_period)
        cross_signal = crossover(slowk, slowd)
        armed = slowk <= oversold_threshold
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

    def kdj_k_crossover_d(market_df: pd.DataFrame, fastk_period: int = 5, slowk_period: int = 3, slowd_period: int = 3) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        k, d = talib.STOCH(high, low, close, fastk_period=fastk_period, slowk_period=slowk_period, slowk_matype=talib.MA_Type.EMA, slowd_period=slowd_period, slowd_matype=talib.MA_Type.EMA)
        return crossover(k, d)

    def kdj_k_crossover_d_2(market_df: pd.DataFrame, fastk_period: int = 5, slowk_period: int = 3, slowd_period: int = 3, oversold_threshold: float = 20.0) -> np.ndarray:
        """低于 oversold_threshold 就上膛，金叉后清膛"""
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        k, d = talib.STOCH(high, low, close, fastk_period=fastk_period, slowk_period=slowk_period, slowk_matype=talib.MA_Type.EMA, slowd_period=slowd_period, slowd_matype=talib.MA_Type.EMA)
        cross_signal = crossover(k, d)
        armed = k <= oversold_threshold
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

    def kdj_k_crossover_d_3(market_df: pd.DataFrame, fastk_period: int = 5, slowk_period: int = 3, slowd_period: int = 3) -> np.ndarray:
        close = market_df['close'].values
        ma_slope = EMA_SLOPE(close, timeperiod=fastk_period)
        k, d = talib.STOCH(ma_slope, ma_slope, ma_slope, fastk_period=fastk_period, slowk_period=slowk_period, slowk_matype=talib.MA_Type.EMA, slowd_period=slowd_period, slowd_matype=talib.MA_Type.EMA)
        return crossover(k, d)

    def kdj_k_crossover_d_4(market_df: pd.DataFrame, fastk_period: int = 5, slowk_period: int = 3, slowd_period: int = 3, oversold_threshold: float = 20.0) -> np.ndarray:
        """低于 oversold_threshold 就上膛，金叉后清膛"""
        close = market_df['close'].values
        ma_slope = EMA_SLOPE(close, timeperiod=fastk_period)
        k, d = talib.STOCH(ma_slope, ma_slope, ma_slope, fastk_period=fastk_period, slowk_period=slowk_period, slowk_matype=talib.MA_Type.EMA, slowd_period=slowd_period, slowd_matype=talib.MA_Type.EMA)
        cross_signal = crossover(k, d)
        armed = k <= oversold_threshold
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

    def smi_k_crossover_d(market_df: pd.DataFrame, fastk_period: int = 5, slowk_period: int = 3, slowd_period: int = 3) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        smi, slowd = SMI(high, low, close, fastk_period=fastk_period, slowk_period=slowk_period, slowd_period=slowd_period)
        return crossover(smi, slowd)

    def smi_k_crossover_d_2(market_df: pd.DataFrame, fastk_period: int = 5, slowk_period: int = 3, slowd_period: int = 3, oversold_threshold: float = -20.0) -> np.ndarray:
        """低于 oversold_threshold 就上膛，金叉后清膛"""
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        smi, slowd = SMI(high, low, close, fastk_period=fastk_period, slowk_period=slowk_period, slowd_period=slowd_period)
        cross_signal = crossover(smi, slowd)
        armed = smi <= oversold_threshold
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

    def smi_k_crossover_d_3(market_df: pd.DataFrame, fastk_period: int = 5, slowk_period: int = 3, slowd_period: int = 3) -> np.ndarray:
        close = market_df['close'].values
        ma_slope = EMA_SLOPE(close, timeperiod=fastk_period)
        smi, slowd = SMI(ma_slope, ma_slope, ma_slope, fastk_period=fastk_period, slowk_period=slowk_period, slowd_period=slowd_period)
        return crossover(smi, slowd)

    def smi_k_crossover_d_4(market_df: pd.DataFrame, fastk_period: int = 5, slowk_period: int = 3, slowd_period: int = 3, oversold_threshold: float = -20.0) -> np.ndarray:
        """低于 oversold_threshold 就上膛，金叉后清膛"""
        close = market_df['close'].values
        ma_slope = EMA_SLOPE(close, timeperiod=fastk_period)
        smi, slowd = SMI(ma_slope, ma_slope, ma_slope, fastk_period=fastk_period, slowk_period=slowk_period, slowd_period=slowd_period)
        cross_signal = crossover(smi, slowd)
        armed = smi <= oversold_threshold
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

    def rvi_crossover_signal(market_df: pd.DataFrame, firstperiod: int = 5, secondperiod: int = 3) -> np.ndarray:
        open = market_df['open'].values
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        rvi, signal_line = Relative_Vigor_Index(open, high, low, close, firstperiod=firstperiod, secondperiod=secondperiod)
        return crossover(rvi, signal_line)

    def adx_plus_crossover_minus(market_df: pd.DataFrame, timeperiod: int = 14) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        plus_di = talib.PLUS_DI(high, low, close, timeperiod=timeperiod)
        minus_di = talib.MINUS_DI(high, low, close, timeperiod=timeperiod)
        return crossover(plus_di, minus_di)

    def adx_plus_crossover_minus_and_ema_decrease(market_df: pd.DataFrame, timeperiod: int = 14, combo_mult: float = 1.618**3) -> np.ndarray:
        """两层组合信号"""
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        # 第一个信号
        plus_di = talib.PLUS_DI(high, low, close, timeperiod=timeperiod)
        minus_di = talib.MINUS_DI(high, low, close, timeperiod=timeperiod)
        # 第二个信号
        timeperiod2 = round(timeperiod * combo_mult)
        price_ma2 = talib.EMA(close, timeperiod2)
        return crossover(plus_di, minus_di) & decrease(price_ma2, timeperiod2)

    def tsi_crossover_signal(market_df: pd.DataFrame, firstperiod: int = 25, secondperiod: int = 13, signalperiod: int = 13) -> np.ndarray:
        close = market_df['close'].values
        tsi = TSI(close, firstperiod=firstperiod, secondperiod=secondperiod)
        signal_line = MA(tsi, signalperiod, "EMA")
        return crossover(tsi, signal_line)

    def rsi_fast_crossover_low(market_df: pd.DataFrame, fastperiod: int, slowperiod: int) -> np.ndarray:
        price = market_df['close'].values
        fast_rsi = talib.RSI(price, timeperiod=fastperiod)
        low_rsi = talib.RSI(price, timeperiod=slowperiod)
        return crossover(fast_rsi, low_rsi)

    def supertrend_long_signal(market_df: pd.DataFrame, timeperiod: int = 10, multiplier: int = 3) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        supertrend, trend = SuperTrend(high, low, close, timeperiod, multiplier)
        shift1 = np.concatenate(([np.nan], trend[:-1]))
        return (trend == 1) & (shift1 == -1)

    def second_wave_trend_1(market_df: pd.DataFrame, timeperiod: int = 8) -> np.ndarray:
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
        fast_ma = talib.EMA(price, timeperiod=timeperiod)
        slow_ma = talib.EMA(fast_ma, timeperiod=timeperiod)

        fast_ma_slope = np.diff(fast_ma, prepend=np.nan)
        slow_ma_slope = np.diff(slow_ma, prepend=np.nan)
        fast_ma_slope_abs = np.abs(fast_ma_slope)
        slow_ma_slope_abs = np.abs(slow_ma_slope)

        is_negative = slow_ma_slope <= 0
        cond0 = cond0_vectorized(is_negative, timeperiod)  # slow_ma 持续上涨
        cond1 = decrease(slow_ma_slope_abs, timeperiod*2)  # slow_ma 斜率变缓
        cond2 = fast_ma_slope <= 0                         # fast_ma 下跌
        cond3 = decrease(fast_ma_slope_abs, timeperiod)    # fast_ma 斜率变缓
        cond4 = increase(price, int(timeperiod/2))         # 价格 上涨

        entry_cond = cond0 & cond1 & cond2 & cond3 & cond4

        return entry_cond

    def second_wave_trend_2(market_df: pd.DataFrame, timeperiod: int = 8) -> np.ndarray:
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
        fast_ma = talib.EMA(price, timeperiod=timeperiod)
        slow_ma = talib.EMA(fast_ma, timeperiod=timeperiod)

        fast_ma_slope = np.diff(fast_ma, prepend=np.nan)
        slow_ma_slope = np.diff(slow_ma, prepend=np.nan)
        fast_ma_slope_abs = np.abs(fast_ma_slope)
        slow_ma_slope_abs = np.abs(slow_ma_slope)
        fast_ma_shift_slope = np.concatenate(([np.nan], fast_ma_slope[:-1]))
        slow_ma_shift_slope_abs = np.concatenate(([np.nan], slow_ma_slope_abs[:-1]))

        is_negative = slow_ma_slope <= 0
        cond0 = cond0_vectorized(is_negative, timeperiod)        # slow_ma 持续上涨
        cond1 = decrease(slow_ma_shift_slope_abs, timeperiod*2)  # slow_ma_shift 斜率变缓
        cond2 = fast_ma_shift_slope <= 0                         # fast_ma_shift 下跌
        cond3 = decrease(fast_ma_slope_abs, timeperiod)          # fast_ma 斜率变缓

        entry_cond = cond0 & cond1 & cond2 & cond3

        return entry_cond


    def roc_crossunder0(market_df: pd.DataFrame, timeperiod: int) -> np.ndarray:
        price = market_df['close'].values
        roc = talib.ROC(price, timeperiod=timeperiod)
        return crossunder(roc, 0)

    def aroon_diff_crossunder0(market_df: pd.DataFrame, timeperiod: int) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        aroon_down, aroon_up = talib.AROON(high, low, timeperiod=timeperiod)
        aroon_diff = aroon_up - aroon_down
        return crossunder(aroon_diff, 0)

    def price_crossunder_sma(market_df: pd.DataFrame, timeperiod: int) -> np.ndarray:
        price = market_df['close'].values
        price_ma = talib.SMA(price, timeperiod)
        return crossunder(price, price_ma)

    def price_crossunder_sma_2(market_df: pd.DataFrame, timeperiod: int) -> np.ndarray:
        price = market_df['close'].values
        price_ma = talib.SMA(price, timeperiod)
        return (crossunder(price, price_ma) & decrease(price_ma, timeperiod)) | (start_decrease(price_ma, timeperiod) & (price <= price_ma))

    def sma_fast_crossunder_slow(market_df: pd.DataFrame, fastperiod: int, slowperiod: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.SMA(price, fastperiod)
        slow_ma = talib.SMA(price, slowperiod)
        return crossunder(fast_ma, slow_ma) & decrease(fast_ma, fastperiod)

    def sma_fast_crossunder_slow_2(market_df: pd.DataFrame, fastperiod: int, slowperiod: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.SMA(price, fastperiod)
        slow_ma = talib.SMA(price, slowperiod)
        return crossunder(fast_ma, slow_ma) & decrease(slow_ma, slowperiod)

    def sma_fast_crossunder_slow_3(market_df: pd.DataFrame, fastperiod: int, slowperiod: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.SMA(price, fastperiod)
        slow_ma = talib.SMA(price, slowperiod)
        return (crossunder(fast_ma, slow_ma) & decrease(fast_ma, fastperiod)) | (start_decrease(fast_ma, fastperiod) & (fast_ma <= slow_ma))

    def sma_first_crossunder_second(market_df: pd.DataFrame, firstperiod: int, secondperiod: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.SMA(price, firstperiod)
        slow_ma = talib.SMA(fast_ma, secondperiod)
        return crossunder(fast_ma, slow_ma) & decrease(fast_ma, firstperiod)

    def sma_first_crossunder_second_2(market_df: pd.DataFrame, firstperiod: int, secondperiod: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.SMA(price, firstperiod)
        slow_ma = talib.SMA(fast_ma, secondperiod)
        return crossunder(fast_ma, slow_ma) & decrease(slow_ma, firstperiod+secondperiod)

    def sma_first_crossunder_second_3(market_df: pd.DataFrame, firstperiod: int, secondperiod: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.SMA(price, firstperiod)
        slow_ma = talib.SMA(fast_ma, secondperiod)
        return (crossunder(fast_ma, slow_ma) & decrease(fast_ma, firstperiod)) | (start_decrease(fast_ma, firstperiod) & (fast_ma <= slow_ma))

    def price_crossunder_ema(market_df: pd.DataFrame, timeperiod: int) -> np.ndarray:
        price = market_df['close'].values
        price_ma = talib.EMA(price, timeperiod)
        return crossunder(price, price_ma)

    def ema_fast_crossunder_slow(market_df: pd.DataFrame, fastperiod: int, slowperiod: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.EMA(price, fastperiod)
        slow_ma = talib.EMA(price, slowperiod)
        return crossunder(fast_ma, slow_ma)

    def ema_first_crossunder_second(market_df: pd.DataFrame, firstperiod: int, secondperiod: int) -> np.ndarray:
        price = market_df['close'].values
        fast_ma = talib.EMA(price, firstperiod)
        slow_ma = talib.EMA(fast_ma, secondperiod)
        return crossunder(fast_ma, slow_ma)

    def smacd_start_decrease(market_df: pd.DataFrame, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        return start_decrease(macd_line, fastperiod)

    def smacd_crossunder_signal(market_df: pd.DataFrame, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        return crossunder(histogram, 0)

    def smacd_crossunder_signal_2(market_df: pd.DataFrame, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        fast_ma = talib.SMA(price, fastperiod)
        return crossunder(histogram, 0) & decrease(fast_ma, fastperiod)

    def smacd_crossunder_signal_3(market_df: pd.DataFrame, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        slow_ma = talib.SMA(price, slowperiod)
        return crossunder(histogram, 0) & decrease(slow_ma, slowperiod)

    def smacd_histogram_start_decrease(market_df: pd.DataFrame, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        return start_decrease(histogram, fastperiod)

    def smacd_histogram_start_decrease_2(market_df: pd.DataFrame, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = SMACD(price, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        fast_ma = talib.SMA(price, fastperiod)
        return (start_decrease(histogram, fastperiod) & decrease(fast_ma, fastperiod)) | (start_decrease(fast_ma, fastperiod) & decrease(histogram, fastperiod))

    def smacd2_start_decrease(market_df: pd.DataFrame, firstperiod: int = 12, secondperiod: int = 12, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        fast_ma, slow_ma, macd_line, signal_line, histogram = SMACD_2(price, firstperiod=firstperiod, secondperiod=secondperiod, signalperiod=signalperiod)
        return start_decrease(macd_line, firstperiod)

    def smacd2_crossunder_signal(market_df: pd.DataFrame, firstperiod: int = 12, secondperiod: int = 12, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        fast_ma, slow_ma, macd_line, signal_line, histogram = SMACD_2(price, firstperiod=firstperiod, secondperiod=secondperiod, signalperiod=signalperiod)
        return crossunder(histogram, 0)

    def smacd2_crossunder_signal_2(market_df: pd.DataFrame, firstperiod: int = 12, secondperiod: int = 12, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        fast_ma, slow_ma, macd_line, signal_line, histogram = SMACD_2(price, firstperiod=firstperiod, secondperiod=secondperiod, signalperiod=signalperiod)
        return crossunder(histogram, 0) & decrease(fast_ma, firstperiod)

    def smacd2_crossunder_signal_3(market_df: pd.DataFrame, firstperiod: int = 12, secondperiod: int = 12, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        fast_ma, slow_ma, macd_line, signal_line, histogram = SMACD_2(price, firstperiod=firstperiod, secondperiod=secondperiod, signalperiod=signalperiod)
        return crossunder(histogram, 0) & decrease(slow_ma, firstperiod+secondperiod)

    def smacd2_histogram_start_decrease(market_df: pd.DataFrame, firstperiod: int = 12, secondperiod: int = 12, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        fast_ma, slow_ma, macd_line, signal_line, histogram = SMACD_2(price, firstperiod=firstperiod, secondperiod=secondperiod, signalperiod=signalperiod)
        return start_decrease(histogram, firstperiod)

    def smacd2_histogram_start_decrease_2(market_df: pd.DataFrame, firstperiod: int = 12, secondperiod: int = 12, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        fast_ma, slow_ma, macd_line, signal_line, histogram = SMACD_2(price, firstperiod=firstperiod, secondperiod=secondperiod, signalperiod=signalperiod)
        return (start_decrease(histogram, firstperiod) & decrease(fast_ma, firstperiod)) | (start_decrease(fast_ma, firstperiod) & decrease(histogram, firstperiod))

    def emacd_start_decrease(market_df: pd.DataFrame, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        return start_decrease(macd_line, fastperiod)

    def emacd_crossunder_signal(market_df: pd.DataFrame, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        return crossunder(histogram, 0)

    def emacd_crossunder_signal_2(market_df: pd.DataFrame, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        fast_ma = talib.EMA(price, fastperiod)
        return crossunder(histogram, 0) & decrease(fast_ma, fastperiod)

    def emacd_crossunder_signal_3(market_df: pd.DataFrame, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        slow_ma = talib.EMA(price, slowperiod)
        return crossunder(histogram, 0) & decrease(slow_ma, slowperiod)

    def emacd_histogram_start_decrease(market_df: pd.DataFrame, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        return start_decrease(histogram, fastperiod)

    def emacd_histogram_start_decrease_2(market_df: pd.DataFrame, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        macd_line, signal_line, histogram = talib.MACD(price, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        fast_ma = talib.EMA(price, fastperiod)
        return (start_decrease(histogram, fastperiod) & decrease(fast_ma, fastperiod)) | (start_decrease(fast_ma, fastperiod) & decrease(histogram, fastperiod))

    def emacd2_start_decrease(market_df: pd.DataFrame, firstperiod: int = 12, secondperiod: int = 12, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        fast_ma, slow_ma, macd_line, signal_line, histogram = MACD_2(price, firstperiod=firstperiod, secondperiod=secondperiod, signalperiod=signalperiod)
        return start_decrease(macd_line, firstperiod)

    def emacd2_crossunder_signal(market_df: pd.DataFrame, firstperiod: int = 12, secondperiod: int = 12, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        fast_ma, slow_ma, macd_line, signal_line, histogram = MACD_2(price, firstperiod=firstperiod, secondperiod=secondperiod, signalperiod=signalperiod)
        return crossunder(histogram, 0)

    def emacd2_crossunder_signal_2(market_df: pd.DataFrame, firstperiod: int = 12, secondperiod: int = 12, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        fast_ma, slow_ma, macd_line, signal_line, histogram = MACD_2(price, firstperiod=firstperiod, secondperiod=secondperiod, signalperiod=signalperiod)
        return crossunder(histogram, 0) & decrease(fast_ma, firstperiod)

    def emacd2_crossunder_signal_3(market_df: pd.DataFrame, firstperiod: int = 12, secondperiod: int = 12, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        fast_ma, slow_ma, macd_line, signal_line, histogram = MACD_2(price, firstperiod=firstperiod, secondperiod=secondperiod, signalperiod=signalperiod)
        return crossunder(histogram, 0) & decrease(slow_ma, firstperiod+secondperiod)

    def emacd2_histogram_start_decrease(market_df: pd.DataFrame, firstperiod: int = 12, secondperiod: int = 12, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        fast_ma, slow_ma, macd_line, signal_line, histogram = MACD_2(price, firstperiod=firstperiod, secondperiod=secondperiod, signalperiod=signalperiod)
        return start_decrease(histogram, firstperiod)

    def emacd2_histogram_start_decrease_2(market_df: pd.DataFrame, firstperiod: int = 12, secondperiod: int = 12, signalperiod: int = 9) -> np.ndarray:
        price = market_df['close'].values
        fast_ma, slow_ma, macd_line, signal_line, histogram = MACD_2(price, firstperiod=firstperiod, secondperiod=secondperiod, signalperiod=signalperiod)
        return (start_decrease(histogram, firstperiod) & decrease(fast_ma, firstperiod)) | (start_decrease(fast_ma, firstperiod) & decrease(histogram, firstperiod))

    def trix_crossunder0(market_df: pd.DataFrame, timeperiod: int = 12) -> np.ndarray:
        price = market_df['close'].values
        trix = talib.TRIX(price, timeperiod=timeperiod)
        return crossunder(trix, 0)

    def trix_start_decrease(market_df: pd.DataFrame, timeperiod: int = 12) -> np.ndarray:
        price = market_df['close'].values
        trix = talib.TRIX(price, timeperiod=timeperiod)
        return start_decrease(trix, timeperiod)

    def bb_price_crossunder_low(market_df: pd.DataFrame, timeperiod: int, nbdev: float) -> np.ndarray:
        price = market_df['close'].values
        upper_band, middle_band, lower_band = talib.BBANDS(price, timeperiod=timeperiod, nbdevup=nbdev, nbdevdn=nbdev)
        return crossunder(price, lower_band)

    def bb_price_crossunder_low_2(market_df: pd.DataFrame, timeperiod: int, nbdev: float) -> np.ndarray:
        price = market_df['close'].values
        upper_band, middle_band, lower_band = talib.BBANDS(price, timeperiod=timeperiod, nbdevup=nbdev, nbdevdn=nbdev)
        return crossunder(price, lower_band) & decrease(lower_band, timeperiod)

    def bb_price_crossunder_high(market_df: pd.DataFrame, timeperiod: int, nbdev: float) -> np.ndarray:
        price = market_df['close'].values
        upper_band, middle_band, lower_band = talib.BBANDS(price, timeperiod=timeperiod, nbdevup=nbdev, nbdevdn=nbdev)
        return crossunder(price, upper_band)

    def bb_price_crossunder_high_2(market_df: pd.DataFrame, timeperiod: int, nbdev: float) -> np.ndarray:
        price = market_df['close'].values
        upper_band, middle_band, lower_band = talib.BBANDS(price, timeperiod=timeperiod, nbdevup=nbdev, nbdevdn=nbdev)
        return crossunder(price, upper_band) & decrease(upper_band, timeperiod)

    def kc_price_crossunder_low(market_df: pd.DataFrame, timeperiod: int, atr_timeperiod: int, multiplier: float) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        upper_band, middle_band, lower_band = KChannels(high, low, close, timeperiod, atr_timeperiod, multiplier)
        return crossunder(close, lower_band)

    def kc_price_crossunder_low_2(market_df: pd.DataFrame, timeperiod: int, atr_timeperiod: int, multiplier: float) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        upper_band, middle_band, lower_band = KChannels(high, low, close, timeperiod, atr_timeperiod, multiplier)
        return crossunder(close, lower_band) & decrease(lower_band, timeperiod)

    def kc_price_crossunder_high(market_df: pd.DataFrame, timeperiod: int, atr_timeperiod: int, multiplier: float) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        upper_band, middle_band, lower_band = KChannels(high, low, close, timeperiod, atr_timeperiod, multiplier)
        return crossunder(close, upper_band)

    def kc_price_crossunder_high_2(market_df: pd.DataFrame, timeperiod: int, atr_timeperiod: int, multiplier: float) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        upper_band, middle_band, lower_band = KChannels(high, low, close, timeperiod, atr_timeperiod, multiplier)
        return crossunder(close, upper_band) & decrease(upper_band, timeperiod)

    def stoch_k_crossunder_d(market_df: pd.DataFrame, fastk_period: int = 5, slowk_period: int = 3, slowd_period: int = 3) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        slowk, slowd = talib.STOCH(high, low, close, fastk_period=fastk_period, slowk_period=slowk_period, slowd_period=slowd_period)
        return crossunder(slowk, slowd)

    def stoch_k_crossunder_d_2(market_df: pd.DataFrame, fastk_period: int = 5, slowk_period: int = 3, slowd_period: int = 3, overbought_threshold: float = 80.0) -> np.ndarray:
        """高于 overbought_threshold 就上膛，金叉后清膛"""
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        slowk, slowd = talib.STOCH(high, low, close, fastk_period=fastk_period, slowk_period=slowk_period, slowd_period=slowd_period)
        cross_signal = crossunder(slowk, slowd)
        armed = slowk > overbought_threshold
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

    def stoch_k_crossunder_d_3(market_df: pd.DataFrame, fastk_period: int = 5, slowk_period: int = 3, slowd_period: int = 3) -> np.ndarray:
        close = market_df['close'].values
        ma_slope = EMA_SLOPE(close, timeperiod=fastk_period)
        slowk, slowd = talib.STOCH(ma_slope, ma_slope, ma_slope, fastk_period=fastk_period, slowk_period=slowk_period, slowd_period=slowd_period)
        return crossunder(slowk, slowd)

    def stoch_k_crossunder_d_4(market_df: pd.DataFrame, fastk_period: int = 5, slowk_period: int = 3, slowd_period: int = 3, overbought_threshold: float = 80.0) -> np.ndarray:
        """高于 overbought_threshold 就上膛，金叉后清膛"""
        close = market_df['close'].values
        ma_slope = EMA_SLOPE(close, timeperiod=fastk_period)
        slowk, slowd = talib.STOCH(ma_slope, ma_slope, ma_slope, fastk_period=fastk_period, slowk_period=slowk_period, slowd_period=slowd_period)
        cross_signal = crossunder(slowk, slowd)
        armed = slowk > overbought_threshold
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

    def kdj_k_crossunder_d(market_df: pd.DataFrame, fastk_period: int = 5, slowk_period: int = 3, slowd_period: int = 3) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        k, d = talib.STOCH(high, low, close, fastk_period=fastk_period, slowk_period=slowk_period, slowk_matype=talib.MA_Type.EMA, slowd_period=slowd_period, slowd_matype=talib.MA_Type.EMA)
        return crossunder(k, d)

    def kdj_k_crossunder_d_2(market_df: pd.DataFrame, fastk_period: int = 5, slowk_period: int = 3, slowd_period: int = 3, overbought_threshold: float = 80.0) -> np.ndarray:
        """高于 overbought_threshold 就上膛，金叉后清膛"""
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        k, d = talib.STOCH(high, low, close, fastk_period=fastk_period, slowk_period=slowk_period, slowk_matype=talib.MA_Type.EMA, slowd_period=slowd_period, slowd_matype=talib.MA_Type.EMA)
        cross_signal = crossunder(k, d)
        armed = k > overbought_threshold
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

    def kdj_k_crossunder_d_3(market_df: pd.DataFrame, fastk_period: int = 5, slowk_period: int = 3, slowd_period: int = 3) -> np.ndarray:
        close = market_df['close'].values
        ma_slope = EMA_SLOPE(close, timeperiod=fastk_period)
        k, d = talib.STOCH(ma_slope, ma_slope, ma_slope, fastk_period=fastk_period, slowk_period=slowk_period, slowk_matype=talib.MA_Type.EMA, slowd_period=slowd_period, slowd_matype=talib.MA_Type.EMA)
        return crossunder(k, d)

    def kdj_k_crossunder_d_4(market_df: pd.DataFrame, fastk_period: int = 5, slowk_period: int = 3, slowd_period: int = 3, overbought_threshold: float = 80.0) -> np.ndarray:
        """高于 overbought_threshold 就上膛，金叉后清膛"""
        close = market_df['close'].values
        ma_slope = EMA_SLOPE(close, timeperiod=fastk_period)
        k, d = talib.STOCH(ma_slope, ma_slope, ma_slope, fastk_period=fastk_period, slowk_period=slowk_period, slowk_matype=talib.MA_Type.EMA, slowd_period=slowd_period, slowd_matype=talib.MA_Type.EMA)
        cross_signal = crossunder(k, d)
        armed = k > overbought_threshold
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

    def smi_k_crossunder_d(market_df: pd.DataFrame, fastk_period: int = 5, slowk_period: int = 3, slowd_period: int = 3) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        smi, slowd = SMI(high, low, close, fastk_period=fastk_period, slowk_period=slowk_period, slowd_period=slowd_period)
        return crossunder(smi, slowd)

    def smi_k_crossunder_d_2(market_df: pd.DataFrame, fastk_period: int = 5, slowk_period: int = 3, slowd_period: int = 3, overbought_threshold: float = 20.0) -> np.ndarray:
        """高于 overbought_threshold 就上膛，金叉后清膛"""
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        smi, slowd = SMI(high, low, close, fastk_period=fastk_period, slowk_period=slowk_period, slowd_period=slowd_period)
        cross_signal = crossunder(smi, slowd)
        armed = smi > overbought_threshold
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

    def smi_k_crossunder_d_3(market_df: pd.DataFrame, fastk_period: int = 5, slowk_period: int = 3, slowd_period: int = 3) -> np.ndarray:
        close = market_df['close'].values
        ma_slope = EMA_SLOPE(close, timeperiod=fastk_period)
        smi, slowd = SMI(ma_slope, ma_slope, ma_slope, fastk_period=fastk_period, slowk_period=slowk_period, slowd_period=slowd_period)
        return crossunder(smi, slowd)

    def smi_k_crossunder_d_4(market_df: pd.DataFrame, fastk_period: int = 5, slowk_period: int = 3, slowd_period: int = 3, overbought_threshold: float = 20.0) -> np.ndarray:
        """高于 overbought_threshold 就上膛，金叉后清膛"""
        close = market_df['close'].values
        ma_slope = EMA_SLOPE(close, timeperiod=fastk_period)
        smi, slowd = SMI(ma_slope, ma_slope, ma_slope, fastk_period=fastk_period, slowk_period=slowk_period, slowd_period=slowd_period)
        cross_signal = crossunder(smi, slowd)
        armed = smi > overbought_threshold
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

    def rvi_crossunder_signal(market_df: pd.DataFrame, firstperiod: int = 5, secondperiod: int = 3) -> np.ndarray:
        open = market_df['open'].values
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        rvi, signal_line = Relative_Vigor_Index(open, high, low, close, firstperiod=firstperiod, secondperiod=secondperiod)
        return crossunder(rvi, signal_line)

    def adx_plus_crossunder_minus(market_df: pd.DataFrame, timeperiod: int = 14) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        plus_di = talib.PLUS_DI(high, low, close, timeperiod=timeperiod)
        minus_di = talib.MINUS_DI(high, low, close, timeperiod=timeperiod)
        return crossunder(plus_di, minus_di)

    def tsi_crossunder_signal(market_df: pd.DataFrame, firstperiod: int = 25, secondperiod: int = 13, signalperiod: int = 13) -> np.ndarray:
        close = market_df['close'].values
        tsi = TSI(close, firstperiod=firstperiod, secondperiod=secondperiod)
        signal_line = MA(tsi, signalperiod, "EMA")
        return crossunder(tsi, signal_line)

    def rsi_fast_crossunder_low(market_df: pd.DataFrame, fastperiod: int, slowperiod: int) -> np.ndarray:
        price = market_df['close'].values
        fast_rsi = talib.RSI(price, timeperiod=fastperiod)
        low_rsi = talib.RSI(price, timeperiod=slowperiod)
        return crossunder(fast_rsi, low_rsi)

    def supertrend_short_signal(market_df: pd.DataFrame, timeperiod: int = 10, multiplier: int = 3) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        supertrend, trend = SuperTrend(high, low, close, timeperiod, multiplier)
        shift1 = np.concatenate(([np.nan], trend[:-1]))
        return (trend == -1) & (shift1 == 1)

    def ma_atr_short_signal(market_df: pd.DataFrame, ema_timeperiod: int = 140, atr_timeperiod: int = 70, threshold: float = 1.5) -> np.ndarray:
        high = market_df['high'].values
        low = market_df['low'].values
        close = market_df['close'].values
        direction = Ma_Atr_Direction(high, low, close, ema_timeperiod, atr_timeperiod, threshold)
        shift1 = np.concatenate(([np.nan], direction[:-1]))
        return (direction == -1) & (shift1 == 1)

if True:

    def tp_high_0(df,N1,N2=0):
        close = df['close']
        if N2 == 0:
            _close = df['close']
        elif N2 == 1:
            _close = df['high']
        else:
            _close = df['close']
        up = (talib.MAX(_close, timeperiod=N1)).shift(1)
        cross_signal = crossover(close, up)
        return cross_signal

    def tp_high_1(df,N1,N2=0):
        close = df['close']

        if N2 == 0:
            _close = df['close']
        elif N2 == 1:
            _close = df['high']
        else:
            _close = df['close']
        delta_val = df['high'] - df[['close','open']].max(axis=1)
        delta_val_ma = talib.SMA(delta_val, timeperiod=N1)
        up = (talib.MAX(_close, timeperiod=N1)+delta_val_ma).shift(1)
        cross_signal = crossover(close, up)
        return cross_signal

    def tp_high_2(df,N1,N3=0):
        close = df['close']

        if N3 == 0:
            _close = df['close']
        elif N3 == 1:
            _close = df['high']
        else:
            _close = df['close']

        delta_val = df['high'] - df[['close','open']].max(axis=1)
        delta_val_ma = talib.SMA(delta_val, timeperiod=N1)
        up = (talib.MAX(_close, timeperiod=N1)+delta_val_ma).shift(1)
        up = talib.SMA(up, timeperiod=N1)

        cross_signal = crossover(close, up)
        return cross_signal

    def s_tp_high_1(df,N1,N2=0,N3=0):
        close = df['close']
        low = df['low']

        if N2 == 0:
            _close = df['close']
        elif N2 == 1:
            _close = df['high']
        else:
            _close = df['close']
        up = talib.MAX(_close, timeperiod=N1).shift(1)

        if N3 == 0:
            cross_signal = tp_high_0(df,N1,N2)
        elif N3 == 1:
            cross_signal = tp_high_1(df, N1, N2)
        elif N3 == 2:
            cross_signal = tp_high_2(df, N1, N2)
        else:
            cross_signal =  _close >0
        signal_trigger = (talib.SUM(cross_signal.astype(int), timeperiod= N1) >0).astype(int)
        cross_signal = (close.diff().shift() < 0) & (close.diff() > 0)
        cross_signal |= ((close>up) & (low < up) & (close.diff() > 0))

        return cross_signal & signal_trigger

    def tp_low_0(df,N1,N2=0):
        close = df['close']
        if N2 == 0:
            _yz = df['close']
            _high = df['close']
        elif N2 == 1:
            _yz = df['low']
            _high = df['high']
        else:
            _yz = df['close']
            _high = df['close']

        dn = (talib.MIN(_yz, timeperiod=N1)).shift(N1) # N1*2周期内：前N1最低点 滑动N1周期
        up = (talib.MAX(_high, timeperiod=N1)).shift(1)
        dn_diff = talib.SMA(dn.diff(1), N1)# N1*2周期内：前N1最低点，变化率 平均值 >= 0
        cross_signal1 = crossover(close, dn)
        cross_signal2 = crossover(close, up)

        cross_signal = np.where(dn_diff >= 0, cross_signal1, cross_signal2)
        return cross_signal

    def tp_low_1(df,N1,N2=0):
        close = df['close']

        if N2 == 0:
            _yz = df['close']
            _high = df['close']
        elif N2 == 1:
            _yz = df['low']
            _high = df['high']
        else:
            _yz = df['close']
            _high = df['close']

        delta_val = df['low'] - df[['close','open']].min(axis=1)
        delta_val_ma = talib.SMA(delta_val, timeperiod=N1)
        delta_val_ma = talib.MAX(delta_val_ma, timeperiod=N1)
        dn = (talib.MIN(_yz, timeperiod=N1)+delta_val_ma).shift(N1)

        up = (talib.MAX(_high, timeperiod=N1)).shift(1)
        dn_diff = talib.SMA((dn.diff(1)>0).astype(float), N1)  # N1*2周期内：前N1最低点，变化率 平均值 >= 0
        cross_signal1 = crossover(close, dn)
        cross_signal2 = crossover(close, up)
        df['con'] = dn_diff >= 0
        df.loc[df['con'], 'cross_signal'] = cross_signal1
        df.loc[~df['con'], 'cross_signal'] = cross_signal2

        cross_signal = np.where(dn_diff >= 0,cross_signal1,cross_signal2)

        return cross_signal

    def tp_low_2(df,N1,N2=0):
        close = df['close']

        if N2 == 0:
            _yz = df['close']
            _high = df['close']
        elif N2 == 1:
            _yz = df['low']
            _high = df['high']
        else:
            _yz = df['close']
            _high = df['close']

        delta_val = df['low'] - df[['close','open']].min(axis=1)
        delta_val_ma = talib.SMA(delta_val, timeperiod=N1)
        dn = (talib.MIN(_yz+delta_val_ma, timeperiod=N1)).shift(1)
        dn = talib.SMA(dn, timeperiod=N1)

        up = (talib.MAX(_high, timeperiod=N1)).shift(1)
        dn_diff = talib.SMA(dn.diff(1), N1)  # N1*2周期内：前N1最低点，变化率 平均值 >= 0
        cross_signal1 = crossover(close, dn)
        cross_signal2 = crossover(close, up)
        cross_signal = np.where(dn_diff >= 0, cross_signal1, cross_signal2)
        return cross_signal

    def s_tp_low_1(df,N1,N2=0,N3=0):
        close = df['close']
        low = df['low']
        high = df['high']

        if N2 == 0:
            _close = df['close']
        elif N2 == 1:
            _close = df['high']
        else:
            _close = df['close']

        up = talib.MAX(_close, timeperiod=N1).shift(1)

        if N3 == 0:
            cross_signal = tp_low_0(df, N1, N2)
        elif N3 == 1:
            cross_signal = tp_low_1(df, N1, N2)
        elif N3 == 2:
            cross_signal = tp_low_2(df, N1, N2)
        else:
            cross_signal =  _close > 0
        

        # 修复：同样的问题也存在于这里
        signal_trigger = (talib.SUM(cross_signal.astype(float), timeperiod= N1) >0).astype(int)
        close_diff = close.diff()
        high_diff = high.diff()
        low_diff = low.diff()
        cross_signal = (close_diff.shift() < 0) & (close_diff > 0)
        cross_signal |= ((high_diff.shift() > 0) & (high_diff > 0))
        cross_signal |= ((low_diff.shift() < 0) & (low_diff > 0))
        cross_signal |= ((close>up) & (low < up) & ((close_diff > 0)|(high_diff > 0)|(low_diff > 0)))

        return cross_signal & signal_trigger


    #
    # def tp_low_0(df,N1,N2=0):
    #     close = df['close']
    #     if N2 == 0:
    #         _close = df['close']
    #     elif N2 == 1:
    #         _close = df['low']
    #     else:
    #         _close = df['close']
    #     down = (talib.MIN(_close, timeperiod=N1)).shift(1)
    #     cross_signal = crossunder(close, down)
    #     return cross_signal
    # def tp_low_1(df,N1,N2=0):
    #     close = df['close']
    #
    #     if N2 == 0:
    #         _close = df['close']
    #     elif N2 == 1:
    #         _close = df['low']
    #     else:
    #         _close = df['close']
    #     delta_val = df['low'] - df[['close','open']].min(axis=1)
    #     delta_val_ma = talib.SMA(delta_val, timeperiod=N1)
    #     down = (talib.MIN(_close, timeperiod=N1)-delta_val_ma).shift(1)
    #     cross_signal = crossunder(close, down)
    #     return cross_signal
    # def tp_low_2(df,N1,N2,N3=0):
    #     close = df['close']
    #
    #     if N3 == 0:
    #         _close = df['close']
    #     elif N3 == 1:
    #         _close = df['low']
    #     else:
    #         _close = df['close']
    #     delta_val = df['low'] - df[['close','open']].min(axis=1)
    #     delta_val_ma = talib.SMA(delta_val, timeperiod=N1)
    #     down = (talib.MIN(_close, timeperiod=N1)-delta_val_ma).shift(1)
    #     down = talib.SMA(down, timeperiod=N1)
    #
    #     cross_signal = crossunder(close, down)
    #     return cross_signal