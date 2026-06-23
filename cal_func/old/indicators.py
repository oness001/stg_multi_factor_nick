import numpy as np
import pandas as pd
import talib


def MA(
    array: np.ndarray,
    timeperiod: int,
    MA_Type: str
) -> np.ndarray:
    if  MA_Type== 'SMA':
        return talib.SMA(array, timeperiod=timeperiod)
    elif MA_Type == 'EMA':
        return talib.EMA(array, timeperiod=timeperiod)
    elif MA_Type == 'WMA':
        return talib.WMA(array, timeperiod=timeperiod)


def EMA_SLOPE(
    close: np.ndarray,
    timeperiod: int = 20
) -> np.ndarray:
    """
    均线斜率（EMA_SLOPE）
    计算方法：EMA_SLOPE = (Price_EMA - Price_EMA_shift) / 1
    其中 Price_EMA_shift 是 1 期前的价格
    """
    n = len(close)
    if n < timeperiod + 1:
        return np.full(n, np.nan, dtype=np.float64)
    
    ma = talib.EMA(close, timeperiod=timeperiod)
    ma_shift = np.concatenate(([np.nan], ma[:-1]))
    ma_slope = ma - ma_shift
    return ma_slope

def ATR(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    timeperiod: int = 14
) -> np.ndarray:
    """
    平均真实波动范围（Average True Range, ATR）
    talib.ATR(high, low, close, timeperiod=timeperiod)
    talib 默认使用 RMA
    """
    n = len(close)
    if n < timeperiod + 1:
        return np.full(n, np.nan, dtype=np.float64)

    prev_close = np.concatenate(([np.nan], close[:-1]))
    tr = np.maximum.reduce([
        high - low,
        np.abs(high - prev_close),
        np.abs(low - prev_close)
    ])
    atr = MA(tr, timeperiod, "EMA")

    return atr

def MASS(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    firstperiod: int = 9,
    secondperiod: int = 25
) -> np.ndarray:
    """
    梅斯线 (Mass Index)
    """
    n = len(close)
    if n < firstperiod + 1:
        return np.full(n, np.nan, dtype=np.float64)
    
    prev_close = np.concatenate(([np.nan], close[:-1]))
    tr = np.maximum.reduce([
        high - low,
        np.abs(high - prev_close),
        np.abs(low - prev_close)
    ])
    ma1 = MA(tr, firstperiod, "EMA")
    ma2 = MA(ma1, firstperiod, "EMA")
    mask = ma2 > 1e-12
    ratio = np.zeros_like(ma1, dtype=np.float64)
    ratio[mask] = ma1[mask] / ma2[mask]
    mass = MA(ratio, secondperiod, "EMA")
    
    return mass

def BBANDS(
    close: np.ndarray,
    timeperiod: int = 20,
    nbdev: float = 2.0
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    布林带（Bollinger Bands）
    talib.BBANDS(close, timeperiod=timeperiod, nbdevup=nbdevup, nbdevdn=nbdevdn)
    talib 默认使用 SMA
    """
    n = len(close)
    if n < timeperiod:
        empty = np.full(n, np.nan, dtype=np.float64)
        return empty, empty, empty

    middle_band = talib.SMA(close, timeperiod=timeperiod)
    std = talib.STDDEV(close, timeperiod=timeperiod, nbdev=nbdev)

    upper_band = middle_band + std * nbdev
    lower_band = middle_band - std * nbdev

    return upper_band, middle_band, lower_band

def KChannels(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    timeperiod: int = 20,
    atr_timeperiod: int = 10,
    multiplier: float = 2.0
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    凯尔特通道（Keltner Channels）
    talib 的 ATR 默认使用 RMA
    """
    n = len(close)
    if n < timeperiod:
        empty = np.full(n, np.nan, dtype=np.float64)
        return empty, empty, empty
    
    middle_band = talib.EMA(close, timeperiod=timeperiod)
    atr =  talib.ATR(high, low, close, timeperiod=atr_timeperiod)  # ATR(high, low, close, timeperiod=atr_timeperiod)
    upper_band = middle_band + atr * multiplier
    lower_band = middle_band - atr * multiplier

    return upper_band, middle_band, lower_band

def ADX(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    timeperiod: int = 14
) -> np.ndarray:
    """
    平均趋向指标（Average Directional Index, ADX）
    talib.ADX(high, low, close, timeperiod=timeperiod)
    talib 默认使用 RMA
    """
    n = len(close)
    if n < timeperiod + 1:
        return np.full(n, np.nan, dtype=np.float64)

    # 计算 ATR
    atr = ATR(high, low, close, timeperiod)
    # 计算 +DM 和 -DM
    up = np.diff(high)
    down = - np.diff(low)
    plus_dm = np.where((up > down) & (up > 0), up, 0.0)
    minus_dm = np.where((down > up) & (down > 0), down, 0.0)
    plus_dm = np.concatenate(([np.nan], plus_dm))
    minus_dm = np.concatenate(([np.nan], minus_dm))
    # 计算 +DI 和 -DI
    plus_dm_ma = MA(plus_dm, timeperiod, "EMA")
    minus_dm_ma = MA(minus_dm, timeperiod, "EMA")
    mask = atr > 1e-12
    plus_di = np.zeros_like(plus_dm_ma, dtype=np.float64)
    plus_di[mask] = 100 * (plus_dm_ma[mask] / atr[mask])
    mask = atr > 1e-12
    minus_di = np.zeros_like(minus_dm_ma, dtype=np.float64)
    minus_di[mask] = 100 * (minus_dm_ma[mask] / atr[mask])
    # 计算 ADX
    dx = 100 * (np.abs(plus_di - minus_di) / (plus_di + minus_di))
    adx = MA(dx, timeperiod, "EMA")
    return [plus_di, minus_di, adx]

def TSI(
    close: np.ndarray,
    firstperiod: int = 25,
    secondperiod: int = 13,
    MA_Type: str = "EMA"
) -> np.ndarray:
    """
    真正强弱指标（True Strength Index, TSI）
    """
    n = len(close)
    if n < firstperiod + secondperiod + 1:
        return np.full(n, np.nan, dtype=np.float64)

    delta = np.diff(close, prepend=np.nan)
    abs_delta = np.abs(delta)
    
    first_delta = MA(delta, firstperiod, MA_Type)
    second_delta = MA(first_delta, secondperiod, MA_Type)
    
    first_abs_delta = MA(abs_delta, firstperiod, MA_Type)
    second_abs_delta = MA(first_abs_delta, secondperiod, MA_Type)

    mask = second_abs_delta > 1e-12
    tsi = np.zeros_like(second_delta, dtype=np.float64)
    tsi[mask] = 100 * (second_delta[mask] / second_abs_delta[mask])
    return tsi

def RSI(
    close: np.ndarray,
    timeperiod: int = 14
) -> np.ndarray:
    """
    相对强弱指数（Relative Strength Index, RSI）
    talib.RSI(close, timeperiod=timeperiod)
    talib 默认使用 RMA
    """
    n = len(close)
    if n < timeperiod + 1:
        return np.full(n, np.nan, dtype=np.float64)

    delta = np.diff(close, prepend=np.nan)
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)

    avg_gain = MA(gain, timeperiod, "EMA")
    avg_loss = MA(loss, timeperiod, "EMA")
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def CMO(
    close: np.ndarray,
    timeperiod: int = 14
) -> np.ndarray:
    """
    动量振荡器（Chande Momentum Oscillator, CMO）
    talib.CMO(close, timeperiod=timeperiod)
    talib 默认使用 RMA
    """
    n = len(close)
    if n < timeperiod + 1:
        return np.full(n, np.nan, dtype=np.float64)

    delta = np.diff(close)
    up = np.where(delta > 0, delta, 0.0)
    down = np.where(delta < 0, -delta, 0.0)
    up = np.concatenate(([np.nan], up))
    down = np.concatenate(([np.nan], down))

    sum_gain = MA(up, timeperiod, "EMA")
    sum_loss = MA(down, timeperiod, "EMA")
    cmo = 100 * (sum_gain - sum_loss) / (sum_gain + sum_loss)
    return cmo

def AROON(high, low, period=14):
    """
    AROON 指标
    talib.AROON(high, low, timeperiod=period)
    """
    high = np.asarray(high, dtype=float)
    low = np.asarray(low, dtype=float)
    
    if len(high) <= period:
        return np.full_like(high, np.nan), np.full_like(low, np.nan)
    
    # 初始化结果数组
    aroon_up = np.full_like(high, np.nan)
    aroon_down = np.full_like(low, np.nan)
    
    # 使用滑动窗口
    for i in range(period, len(high)):
        window_high = high[i - period : i + 1]
        window_low = low[i - period : i + 1]
        
        max_idx = np.argmax(window_high)          # 窗口内最高价的索引
        min_idx = np.argmin(window_low)           # 窗口内最低价的索引
        
        pos_max = period - max_idx  # 距离当前bar的距离
        pos_min = period - min_idx
        
        aroon_up[i] = (period - pos_max) / period * 100
        aroon_down[i] = (period - pos_min) / period * 100
    
    return aroon_down, aroon_up

def MACD(
    close: np.ndarray,
    fastperiod: int = 12,
    slowperiod: int = 26,
    signalperiod: int = 9
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    平滑异同移动平均线（Moving Average Convergence Divergence, MACD）
    talib.MACD(close, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
    talib 默认使用 EMA
    """
    n = len(close)
    if n < slowperiod:
        empty = np.full(n, np.nan, dtype=np.float64)
        return empty, empty, empty

    fast_ma = talib.EMA(close, timeperiod=fastperiod)
    slow_ma = talib.EMA(close, timeperiod=slowperiod)
    macd_line = fast_ma - slow_ma
    signal_line = talib.EMA(macd_line, timeperiod=signalperiod)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def MACD_2(
    close: np.ndarray,
    firstperiod: int = 12,
    secondperiod: int = 12,
    signalperiod: int = 9
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    平滑异同移动平均线（Moving Average Convergence Divergence, MACD）
    """
    n = len(close)
    if n < secondperiod:
        empty = np.full(n, np.nan, dtype=np.float64)
        return empty, empty, empty

    fast_ma = talib.EMA(close, timeperiod=firstperiod)
    slow_ma = talib.EMA(fast_ma, timeperiod=secondperiod)
    macd_line = fast_ma - slow_ma
    signal_line = talib.EMA(macd_line, timeperiod=signalperiod)
    histogram = macd_line - signal_line
    return fast_ma, slow_ma, macd_line, signal_line, histogram

def SMACD(
    close: np.ndarray,
    fastperiod: int = 12,
    slowperiod: int = 26,
    signalperiod: int = 9
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    平滑异同移动平均线（Moving Average Convergence Divergence, MACD）
    """
    n = len(close)
    if n < slowperiod:
        empty = np.full(n, np.nan, dtype=np.float64)
        return empty, empty, empty

    fast_ma = talib.SMA(close, timeperiod=fastperiod)
    slow_ma = talib.SMA(close, timeperiod=slowperiod)
    macd_line = fast_ma - slow_ma
    signal_line = talib.SMA(macd_line, timeperiod=signalperiod)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def SMACD_2(
    close: np.ndarray,
    firstperiod: int = 12,
    secondperiod: int = 12,
    signalperiod: int = 9
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    平滑异同移动平均线（Moving Average Convergence Divergence, MACD）
    """
    n = len(close)
    if n < secondperiod:
        empty = np.full(n, np.nan, dtype=np.float64)
        return empty, empty, empty

    fast_ma = talib.SMA(close, timeperiod=firstperiod)
    slow_ma = talib.SMA(fast_ma, timeperiod=secondperiod)
    macd_line = fast_ma - slow_ma
    signal_line = talib.SMA(macd_line, timeperiod=signalperiod)
    histogram = macd_line - signal_line
    return fast_ma, slow_ma, macd_line, signal_line, histogram

def STOCH(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    fastk_period: int = 9,
    slowk_period: int = 3,
    slowd_period: int = 3,
) -> tuple[np.ndarray, np.ndarray]:
    """
    随机振荡器（Stochastic Oscillator, STOCH）
    talib.STOCH(high, low, close, fastk_period=fastk_period, slowk_period=slowk_period, slowd_period=slowd_period)
    talib 默认使用 SMA
    是 KDJ 的基础指标， KDJ 常使用 EMA/RMA
    """
    n = len(close)
    if n < fastk_period:
        empty = np.full(n, np.nan, dtype=np.float64)
        return empty, empty

    h_max = talib.MAX(high, timeperiod=fastk_period)
    l_min = talib.MIN(low, timeperiod=fastk_period)
    rsv = 100 * (close - l_min) / (h_max - l_min)   # Williams %R = rsv - 100
    slowk = MA(rsv, slowk_period, "EMA")
    slowd = MA(slowk, slowd_period, "EMA")

    return slowk, slowd

def SMI(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    fastk_period: int = 9,
    slowk_period: int = 3,
    slowd_period: int = 3,
    MA_Type: str = "EMA"
) -> tuple[np.ndarray, np.ndarray]:
    """
    随机动量指标（Stochastic Momentum Index, SMI）
    """
    n = len(close)
    if n < fastk_period:
        empty = np.full(n, np.nan, dtype=np.float64)
        return empty, empty

    h_max = talib.MAX(high, timeperiod=fastk_period)
    l_min = talib.MIN(low, timeperiod=fastk_period)
    high_low_range = h_max - l_min
    relative_range = close - (h_max + l_min) / 2
    slowk_high_low_range = MA(MA(high_low_range, slowk_period, MA_Type), slowk_period, MA_Type)
    slowk_relative_range = MA(MA(relative_range, slowk_period, MA_Type), slowk_period, MA_Type)
    smi = 100 * slowk_relative_range / slowk_high_low_range
    slowd = MA(smi, slowd_period, MA_Type)

    return smi, slowd

def Relative_Vigor_Index(
    open: np.ndarray,
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    firstperiod: int,
    secondperiod: int,
    MA_Type: str = "EMA"
) -> np.ndarray:
    ""
    n = len(close)
    if n < firstperiod:
        empty = np.full(n, np.nan, dtype=np.float64)
        return empty, empty

    co_diff = MA(close-open, firstperiod, MA_Type)
    hl_diff = MA(high-low, firstperiod, MA_Type)
    rvi = 100 * co_diff / hl_diff
    signal_line = MA(rvi, secondperiod, MA_Type)
    return rvi, signal_line

def SuperTrend(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    timeperiod: int = 10,
    multiplier: float = 3
) -> np.ndarray:
    """
    超级趋势（SuperTrend）
    talib 的 ATR 默认使用 RMA
    """
    n = len(close)
    if n < timeperiod:
        empty = np.full(n, np.nan, dtype=np.float64)
        return empty, empty

    n = len(close)
    hl2 = (high + low) / 2
    atr = talib.ATR(high, low, close, timeperiod=timeperiod)  # ATR(high, low, close, timeperiod=timeperiod)
    upper_band = hl2 + atr * multiplier
    lower_band = hl2 - atr * multiplier
    supertrend = np.full(n, np.nan, dtype=np.float64)
    direction = np.zeros(n, dtype=np.int8)     # 1=多头，-1=空头
    # 初始值（默认从多头开始）
    start = timeperiod - 1
    direction[start] = 1
    supertrend[start] = lower_band[start]
    # 后续值
    for i in range(timeperiod, n):
        if direction[i-1] == 1:                # 上一个 bar 是多头
            final_lower = max(lower_band[i], supertrend[i-1])
            if close[i] <= final_lower:        # 反转为空头
                direction[i] = -1
                supertrend[i] = upper_band[i]
            else:                              # 保持多头
                direction[i] = 1
                supertrend[i] = final_lower
        else:                                  # 上一个 bar 是空头
            final_upper = min(upper_band[i], supertrend[i-1])
            if close[i] >= final_upper:        # 反转为多头
                direction[i] = 1
                supertrend[i] = lower_band[i]
            else:                              # 保持空头
                direction[i] = -1
                supertrend[i] = final_upper
    return supertrend, direction

def RMS(
    close: np.ndarray,
    timeperiod: int,
    MA_Type: str = "EMA"
) -> np.ndarray:
    """
    均方根收益率（Root Mean Square, RMS）
    和标准差有些类似，区别在于均方根收益率不需要每个元素减平均值
    """
    if len(close) < 2:
        return np.full(len(close), np.nan, dtype=np.float64)
    
    # 一阶差分的二次幂
    delta = np.diff(close, prepend=np.nan)
    delta_pow = delta ** 2
    
    delta_variance = MA(delta_pow, timeperiod, MA_Type)
    mask = delta_variance > 1e-12
    delta_rms = np.zeros_like(delta_variance, dtype=np.float64)
    delta_rms[mask] = np.sqrt(delta_variance[mask])
    return delta_rms

def Skew(
    close: np.ndarray,
    timeperiod: int,
    MA_Type: str = "EMA"
) -> np.ndarray:
    """
    偏度（Skewness），基于 RMS 的思路
    """
    delta_skew = pd.Series(close).rolling(timeperiod,min_periods=2).skew()

    # if len(close) < 2:
    #     return np.full(len(close), np.nan, dtype=np.float64)
    #
    # # 一阶差分的三次幂
    # delta = np.diff(close, prepend=np.nan)
    # delta_pow3 = delta ** 3
    #
    # delta_skew_ma = MA(delta_pow3, timeperiod, MA_Type)
    # delta_rms = RMS(close, timeperiod, MA_Type)
    #
    # delta_rms_pow3 = delta_rms ** 3
    #
    # mask = delta_rms_pow3 > 1e-12
    # delta_skew = np.zeros_like(delta_skew_ma, dtype=np.float64)
    # delta_skew[mask] = delta_skew_ma[mask] / delta_rms_pow3[mask]
    return delta_skew.values

def Convexity(
    close: np.ndarray,
    timeperiod: int,
    MA_Type: str = "SMA"
) -> np.ndarray:
    """
    根据波动率在不同时间尺度下的表现特征，构建 vol_skew 因子（即波动率凸性）
    VAR(T) = (Price_S - Price_0) ^ 2 / T
    VAR(1) = RMS(Delta(Price))
    Convexity = STD(T) / STD(1)
    """

    if len(close) < timeperiod + 1:
        return np.full(len(close), np.nan, dtype=np.float64)
    
    delta_rms = RMS(close, timeperiod, MA_Type)
    # 每 timeperiod 期的收益率
    delta_n = np.diff(close, n=timeperiod, prepend=[np.nan]*timeperiod)
    # VAR(T) 的平方根
    volatility_t = np.sqrt(delta_n ** 2 / timeperiod)
    # Convexity = STD(T) / STD(1)
    mask = delta_rms > 1e-12
    convexity = np.zeros_like(volatility_t, dtype=np.float64)
    convexity[mask] = volatility_t[mask] / delta_rms[mask]

    return convexity

def Ma_Atr_Direction(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    ema_timeperiod: int = 140,
    atr_timeperiod: int = 70,
    threshold: float = 1.5
) -> np.ndarray:
    "自定义看涨跌指标"
    n = len(close)
    if n < ema_timeperiod:
        empty = np.full(n, np.nan, dtype=np.float64)
        return empty

    price_ma = talib.EMA(close, ema_timeperiod)
    bias = close - price_ma
    atr = talib.ATR(high, low, close, timeperiod=atr_timeperiod)
    mask = atr > 1e-12
    bias_standard = np.zeros_like(bias, dtype=np.float64)
    bias_standard[mask] = np.abs(bias[mask]) / atr[mask]
    bias_timeperiod = max(2, round(ema_timeperiod / 20))   # 大概取 13 ~ 21
    bias_standard_ma = talib.EMA(bias_standard, bias_timeperiod)

    long_cond  = (bias_standard_ma > threshold) & (bias_standard > bias_standard_ma) & (close > price_ma)
    short_cond = (bias_standard_ma > threshold) & (bias_standard > bias_standard_ma) & (close < price_ma)
    direction = np.zeros(len(close), dtype=np.int8)  # 1=多头, -1=空头, 0=无信号
    direction[long_cond]  = 1
    direction[short_cond] = -1
    direction = np.where(direction != 0, direction, np.nan)    # 把 0 转为 nan
    direction = pd.Series(direction).ffill().fillna(0).values  # 向前填充，最后转为 numpy 数组
    return direction
