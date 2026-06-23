import numpy as np
import pandas as pd
from typing import List
import talib
# from numba import njit
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# ==================== 模块级缓存 ====================
_trail_stop_cache = {}  # key: (market_data_id, atr_length, direction_long) -> value: np.ndarray (ts_price)
_price_array_cache = {}  # key: market_data_id -> value: np.ndarray (close_array)


def clear_exit_cache():
    """清空出场信号缓存（切换品种或数据后调用）"""
    _trail_stop_cache.clear()
    _price_array_cache.clear()


# @njit
def for_bar_exit_signal_numba(
        ignore_new_entry: bool,
        direction_long: bool,
        close_array: np.ndarray,
        entry_signal_shift: np.ndarray,
        fb_array: np.ndarray,
        sl_price_array: np.ndarray,
        tp_price_array: np.ndarray,
        trail_stop_price_array: np.ndarray,
        exit_signal_array: np.ndarray
) -> np.ndarray:
    """
    close_array: 一维 float64
    entry_signal_shift: 一维 bool
    fb_array: 一维 int64
    sl_price_array: 二维 float64, shape=(len_array, len_sl)
    tp_price_array: 二维 float64, shape=(len_array, len_tp)
    trail_stop_price_array: 二维 float64, shape=(len_array, len_ts)
    exit_signal_array: 二维 bool, shape=(len_array, len_rules)
    """
    # 初始化出场信号 Series 和状态变量
    len_array = len(close_array)
    len_ts = trail_stop_price_array.shape[1]
    exit_signal = np.zeros(len_array, dtype=np.bool_)
    exit_signal[0] = True  # 初始化第一个时间点的 exit_signal 为 True
    entry_idx = -1  # 入场时的 bar 序号
    current_ts_price = np.zeros(len_ts, dtype=np.float64)
    in_position = False  # 当前持仓

    for i in range(len_array):
        exited = False
        # ==================== 1. 执行上个 bar 入场 ====================
        condition1 = ignore_new_entry and not in_position  # 只在无持仓时才更新出场条件
        condition2 = not ignore_new_entry  # 不论是否持仓，都会根据新的入场信号更新出场条件
        if entry_signal_shift[i] and (condition1 or condition2):
            in_position = True
            entry_idx = i
            for j in range(len_ts):
                current_ts_price[j] = trail_stop_price_array[i, j]

        # ==================== 2. 持仓时检查出场 ====================
        current_close = close_array[i]
        if in_position:
            if exit_signal_array[i]:  # 当前 bar 满足该条件
                exited = True

            # 持仓达到固定周期数后出场
            if not exited:
                for j in range(fb_array.shape[0]):
                    bars_held = i - entry_idx + 1
                    if bars_held >= fb_array[j]:
                        exited = True
                        break

            # 固定百分比止损
            if not exited:
                for j in range(sl_price_array.shape[1]):
                    current_sl_price = sl_price_array[i, j]
                    if (direction_long and current_close <= current_sl_price) or (not direction_long and current_close >= current_sl_price):
                        exited = True
                        break

            # 固定百分比止盈
            if not exited:
                for j in range(tp_price_array.shape[1]):
                    current_tp_price = tp_price_array[i, j]
                    if (direction_long and current_close >= current_tp_price) or (not direction_long and current_close <= current_tp_price):
                        exited = True
                        break

            # 移动止损，基于 ATR
            if not exited:
                for j in range(len_ts):
                    temp_ts_price = trail_stop_price_array[i, j]
                    if direction_long:  # 多头移动止损
                        current_ts_price[j] = max(temp_ts_price, current_ts_price[j])
                        if current_close <= current_ts_price[j]:
                            exited = True
                            break
                    else:  # 空头移动止损
                        current_ts_price[j] = min(temp_ts_price, current_ts_price[j])
                        if current_close >= current_ts_price[j]:
                            exited = True
                            break

            if exited:
                in_position = False
                exit_signal[i] = True

    return exit_signal


def generate_exit_signal(
    market_df: pd.DataFrame,
    ignore_new_entry: bool,
    direction_long: bool,
    entry_signal: np.ndarray,
    exit_signal_str: List[str],
    exit_signal_array: np.ndarray
) -> np.ndarray:
    """
    生成出场信号 Series（bool）
    
    参数说明：
        market_df: 行情 DataFrame，必须包含 ["datetime", "open", "high", "low", "close"]
        ignore_new_entry: 当存在持仓时，是否根据新开仓条件更新出场条件
        direction_long: 是否做多
        entry_signal: 入场信号（包含过滤） bool 一维数组，True是入场点，False是非入场点（index与market_df一致）
        exit_signal_str: 内置规则列表，例如 ["fixed_bars^10", "stop_loss^0.02", "trailing_stop^21^2.5"]
        exit_signal_array: 二维数组，预计算的出场信号条件组成的数组
    
    返回：exit_signal (bool Series)，满足任一出场条件时为 True，否则为 False
    """
    # 预先计算所需数据，并转换为 np.ndarray 用于 numba 加速
    close_array = market_df['close'].values
    entry_signal_shift = np.concatenate(([False], entry_signal[:-1]))

    # 缓存标识：同一份 market_df 数据 id
    data_id = market_df.shape
    if data_id not in _price_array_cache:
        _price_array_cache.clear()
        _price_array_cache[data_id] = close_array
    price = _price_array_cache[data_id]

    fb_array = []
    sl_price_array = []
    tp_price_array = []
    trail_stop_price_array = []

    for name in exit_signal_str:
        func_name, *func_params = name.split("^")
        if func_name == "fixed_bars":
            fixed_bars = int(func_params[0]) if func_params else 50  # 默认持仓 5 个 bar
            fb_array.append(fixed_bars)
        elif func_name == "stop_loss":
            sl_pct = float(func_params[0]) if func_params else 0.02  # 默认止损 2%
            sl_price = price * (1 - sl_pct) if direction_long else price * (1 + sl_pct)
            sl_price_array.append(sl_price)
        elif func_name == "take_profit":
            tp_pct = float(func_params[0]) if func_params else 0.05  # 默认止盈 5%
            tp_price = price * (1 + tp_pct) if direction_long else price * (1 - tp_pct)
            tp_price_array.append(tp_price)
        elif func_name == "trailing_stop":
            atr_length = int(func_params[0]) if len(func_params) > 0 else 21  # 默认 ATR 长度为 21
            atr_mult = float(func_params[1]) if len(func_params) > 1 else 2.0  # 默认 ATR 乘数为 2.0
            # 缓存 ATR + trail_stop_price 计算
            cache_key = (data_id, atr_length, direction_long)
            if cache_key not in _trail_stop_cache:
                atr = talib.ATR(market_df["high"].values, market_df["low"].values, market_df["close"].values, timeperiod=atr_length)
                _trail_stop_cache[cache_key] = atr
            else:
                atr = _trail_stop_cache[cache_key]

            ts_price = close_array - atr * atr_mult if direction_long else close_array + atr * atr_mult
            ts_price = np.where(np.isnan(ts_price), close_array * (1000 if direction_long else 0.001), ts_price)
            trail_stop_price_array.append(ts_price)
        else:
            raise ValueError("不支持的 exit_signal_str 类型")

    fb_array = np.array(fb_array).astype(np.int64) if fb_array else np.empty(0, dtype=np.int64)
    sl_price_array = np.stack(sl_price_array, axis=1).astype(np.float64) if sl_price_array else np.empty((len(market_df), 0), dtype=np.float64)
    tp_price_array = np.stack(tp_price_array, axis=1).astype(np.float64) if tp_price_array else np.empty((len(market_df), 0), dtype=np.float64)
    trail_stop_price_array = np.stack(trail_stop_price_array, axis=1).astype(np.float64) if trail_stop_price_array else np.empty((len(market_df), 0), dtype=np.float64)

    exit_signal = for_bar_exit_signal_numba(ignore_new_entry, direction_long,
                                            close_array, entry_signal_shift, fb_array,
                                            sl_price_array, tp_price_array, trail_stop_price_array, exit_signal_array)
    
    return exit_signal