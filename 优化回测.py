"""
函数式策略回测系统 - 整合版（含单利/复利净值计算）

本文件在 opt_bt_pareto.py 的基础上，整合了 jz.py 中的高级净值计算功能：
1. 支持单利和复利两种净值计算模式
2. 更精细的交易成本计算（开仓+平仓分别计费）
3. 更准确的单笔交易统计

主要特点：
- 纯函数式设计：所有计算函数无副作用
- 分层架构：清晰的职责分离
- 多目标优化：使用 NSGA-II 算法
- 缓存机制：避免重复计算
- 类型提示：完整的类型注解
- 日志系统：使用 loguru 提供彩色输出

作者: 函数式重构 + jz.py 整合
日期: 2026-06-13
"""

# 标准库导入
import time  # 时间相关功能
import sys  # 系统相关功能
import os  # 操作系统接口
import json  # JSON 序列化
import traceback  # 异常跟踪和堆栈信息
from typing import Dict, List, Tuple, Union, Any, Optional  # 类型提示
from datetime import datetime  # 日期时间处理
from importlib import import_module  # 动态模块导入
from multiprocessing import Pool
from functools import partial  # 函数式编程工具：偏函数
# 第三方库导入
import numpy as np  # NumPy：科学计算基础库
import pandas as pd  # Pandas：数据分析和处理
from loguru import logger  # Loguru：现代化的日志记录库

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# 配置 loguru 日志系统
logger.remove()  # 移除默认处理器
logger.add(
    sys.stderr,  # 输出到标准错误
    level="INFO",  # 日志级别
)
pd.set_option('display.max_rows', 10000)
pd.set_option('display.max_columns', 10000)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 1500)
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('expand_frame_repr', False)
pd.set_option('display.float_format', lambda x: '%.4f' % x)

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('tkAgg')
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


# Pymoo 多目标优化库导入
from pymoo.core.problem import Problem  # 优化问题基类
from pymoo.algorithms.moo.nsga2 import NSGA2  # NSGA-II 多目标优化算法
from pymoo.optimize import minimize  # 优化执行函数
from pymoo.operators.sampling.rnd import BinaryRandomSampling  # 二进制随机采样初始化
from pymoo.operators.crossover.binx import BinomialCrossover  # 二项式交叉算子
from pymoo.operators.mutation.bitflip import BitflipMutation  # 位翻转变异算子
from pymoo.config import Config  # Pymoo 全局配置
from pymoo.termination import get_termination  # 优化终止条件

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 禁用 pymoo 编译警告（提高运行速度）
Config.warnings['not_compiled'] = False
# 第五步：计算出场信号
exit_module = import_module("cal_func.exit_pool")
EXIT_FUNC_G = getattr(exit_module, "generate_exit_signal")
CLEAR_EXIT_CACHE = getattr(exit_module, "clear_exit_cache", None)


if True:
    from typing import List, Tuple, Any


    def parse_params_to_types(params: List[str]) -> List[Any]:
        """将字符串参数转换为正确的类型（int, float, str），用于函数调用"""
        converted = []
        for param in params:
            # if isinstance(param, str) and not param.isdigit():
            #     converted.append(param)  # 保持字符串不变
            # elif isinstance(param, str) and param.isdigit():
            #     if float( param).is_integer():
            #         converted.append(int(param))
            #     else:
            #         converted.append(float(param))

            if "." in param:
                converted.append(round(float(param),5))
            elif param.isdigit() or ("-" in param and param.replace("-", "").isdigit()):
                converted.append(int(param))
            else:
                converted.append(param)  # 保持字符串不变

        return converted


    def parse_strategy_expression1(strategy_name: str) -> Tuple[str]:
        """将字符串解析分解为 3 个部分（入场过滤、入场信号和出场信号）"""
        entry_filter_name, entry_signal_name, exit_signal_name = strategy_name.split("&")
        return entry_filter_name, entry_signal_name, exit_signal_name


    def parse_strategy_expression2(signal_name: str) -> List[List[str]]:
        """将字符串解析分解"""
        comb_name_list = signal_name.split("|")
        comb_list = []
        for comb_name in comb_name_list:
            signal_name_list = comb_name.split("+")  # 将信号组合拆分为 m 个单一信号
            signal_list = []
            for signal_name in signal_name_list:
                # func_name, *func_params = signal_name.split("^")  # 将单一信号拆分为信号名称和参数
                signal_list.append(signal_name)
            comb_list.append(signal_list)
        return comb_list


    def parse_strategy_expression3(signal_name: str) -> Tuple[str]:
        """将字符串解析分解"""
        func_name, *func_params = signal_name.split("^")
        return func_name, *func_params


# ==================== 基础工具函数 ====================

def generate_parameter_space(config: List[Dict]) -> int:
    """
    计算决策变量空间的总大小（纯函数）

    Args:
        config: 策略参数配置 (STRATEGY_PARAMS_CONFIG)

    Returns:
        int: 决策变量的总数量（所有组的信号数量之和）
    """
    return sum(len(group["items"]) for group in config)


def decode_binary_vector(
        x: np.ndarray,
        config: List[Dict]
) -> Dict[str, List[str]]:
    """
    将 pymoo 的二进制决策向量解码为选定的策略组件（纯函数）

    Args:
        x: 二进制决策向量，长度为所有信号数量的总和
        config: 策略参数配置 (STRATEGY_PARAMS_CONFIG)

    Returns:
        Dict[str, List[str]]: 解码后的策略组件字典
    """
    offset = 0  # 当前在决策向量中的偏移位置
    result = {}  # 存储解码结果
    # 遍历每个信号组
    for group in config:
        group_items = group["items"]  # 当前组的所有信号项
        group_bits = x[offset:offset + len(group_items)]  # 提取当前组对应的二进制位

        # 选择所有被标记为 1 的信号
        selected = [group_items[i] for i, bit in enumerate(group_bits) if bit]
        result[group["name"]] = selected

        offset += len(group_items)  # 移动到下一组的起始位置

    return result

def encode_strategy_to_name(decoded: Dict[str, List[str]]) -> str:
    """
    将解码后的策略转换为可读的策略名称（纯函数）

    Args:
        decoded: 解码后的策略组件字典

    Returns:
        str: 策略名称字符串，格式为 "过滤器&信号&出场"
    """
    filters = "|".join(decoded.get("EntryFilters", ["_"]))
    signals = "|".join(decoded.get("EntrySignals", ["_"]))
    exits = "|".join(decoded.get("ExitSignals", ["_"]))
    return f"{filters}&{signals}&{exits}"


def collect_all_signals(config: List[Dict]) -> Dict[str, List[str]]:
    """
    从配置中收集所有信号名称用于预计算（纯函数）

    Args:
        config: 策略参数配置 (STRATEGY_PARAMS_CONFIG)

    Returns:
        Dict[str, List[str]]: 包含所有信号名称的字典
    """
    return {
        "filters": config[0]["items"],
        "signals": config[1]["items"],
        "exits": config[2]["items"]
    }


def print_search_space_stats(
        config: List[Dict],
        population_size: int = 100,
        n_generations: int = 50
) -> None:
    from math import comb

    total_combinations = 1

    for group in config:
        n_items = len(group["items"])
        n_select = group["select_count"]
        n_comb = comb(n_items, n_select)
        total_combinations *= n_comb
        logger.info(f"{group['name']}: C({n_items}, {n_select}) = {n_comb}")

    total_evaluations = population_size * n_generations
    coverage = (total_evaluations / total_combinations) * 100

    logger.info(f"总搜索空间: {total_combinations:,} | 覆盖率: {coverage:.6f}%")


# ==================== 预计算层 ====================
if True :
    def precompute_single_signal(
            market_df: pd.DataFrame,
            signal_name: str,
            pool_module: Any,
            pool_type: str
    ) -> np.ndarray:

        func_name, *func_params = parse_strategy_expression3(signal_name)

        if func_name == "_":
            if pool_type == "filter":
                return np.array([True] * len(market_df), dtype=bool)
            else:
                return np.array([False] * len(market_df), dtype=bool)

        func = getattr(pool_module, func_name)
        if func is None:
            raise ValueError(f"Function {func_name} not found")


        params = parse_params_to_types(func_params)
        logger.debug(signal_name)
        return func(market_df, *params)



    def precompute_all_signals(
            market_df: pd.DataFrame,
            signal_names: List[str],
            pool_path: str,
            pool_type: str,
            pool_concatenate: str,
            show_progress: bool = False
    ) -> Dict[str, np.ndarray]:
        pool_module = import_module(pool_path)

        if pool_type == "filter":
            res0 = np.array([True] * len(market_df), dtype=bool)
        else:
            res0 = np.array([False] * len(market_df), dtype=bool)

        extra_exit_names = ["trailing_stop", "fixed_bars", "stop_loss", "take_profit"]
        all_pre = {}

        # --- 在循环前包装 tqdm ---
        if show_progress:
            from tqdm import tqdm
            signal_names = tqdm(signal_names, desc=f"预计算 {pool_type} 信号")

        for name in signal_names:
            if "|" in name:
                names = name.split("|")
                name_res = []
                for name0 in names:
                    if ("^" not in name0) or name0.split("^")[0] in extra_exit_names:
                        res = res0
                    else:
                        res = precompute_single_signal(market_df, name0, pool_module, pool_type)
                        if res is None:
                            res = res0
                    name_res.append(res)

                if pool_concatenate == "or":
                    all_res = np.any(name_res, axis=0) # 1>t,-1 t 0 >f
                elif pool_concatenate == "and":
                    all_res = np.all(name_res, axis=0)
                else:
                    all_res = np.any(name_res, axis=0)
                all_pre[name] = all_res  # --- 修复：应该存到 all_pre 而非 name_res ---
            else:
                if ("^" not in name) or name.split("^")[0] in extra_exit_names:
                    res = res0
                else:
                    res = precompute_single_signal(market_df, name, pool_module, pool_type)
                all_pre[name] = res

        return all_pre


if True :

    def precompute_single_signal0(
            market_df: pd.DataFrame,
            signal_name: str,
            pool_module: Any,
            pool_type: str
    ) -> np.ndarray:

        func_name, *func_params = parse_strategy_expression3(signal_name)

        if func_name == "_":
            if pool_type == "filter":
                return np.array([True] * len(market_df), dtype=bool)
            else:
                return np.array([False] * len(market_df), dtype=bool)

        func = getattr(pool_module, func_name)
        params = parse_params_to_types(func_params)
        return func(market_df, *params)


    def precompute_all_signals0(
            market_df: pd.DataFrame,
            signal_names: List[str],
            pool_path: str,
            pool_type: str,
            show_progress: bool = False
    ) -> Dict[str, np.ndarray]:

        pool_module = import_module(pool_path)
        extra_exit_names = ["trailing_stop", "fixed_bars", "stop_loss", "take_profit"]

        if show_progress:
            from tqdm import tqdm
            signal_names = tqdm(signal_names, desc=f"预计算 {pool_type} 信号")

        return {
            name: precompute_single_signal(market_df, name, pool_module, pool_type)
            for name in signal_names
            if name.split("^")[0] not in extra_exit_names
        }


    def generate_position_series(
            market_df: pd.DataFrame,
            entry_filter_combined: List[Tuple[str, np.ndarray]],
            entry_signal_combined: List[Tuple[str, np.ndarray]],
            exit_signal_combined: List[List[Tuple[str, np.ndarray]]],
            entry_filter_vote_size: List[int],
            ignore_new_entry: bool,
            direction_long: bool,
    ) -> Tuple[str, pd.Series]:
        """
        从过滤器和信号生成持仓序列（纯函数）

        Args:
            market_df: 市场数据 DataFrame
            entry_filter_combined: 入场过滤器组合列表
            entry_signal_combined: 入场信号组合列表
            exit_signal_combined: 出场信号组合列表
            entry_filter_vote_size: 每个过滤器组需要的投票数
            ignore_new_entry: 持仓时是否忽略新的入场条件
            direction_long: 交易方向（True=做多，False=做空）

        Returns:
            Tuple[str, pd.Series]: (策略名称, 持仓序列)
        """
        # 第一步：构建入场过滤条件
        entry_filter_names = []
        entry_filter_sum = []

        f_names, f_arrays = zip(*entry_filter_combined)
        entry_filter_names.append("|".join(f_names))
        entry_filter_sum.append(np.sum(f_arrays, axis=0) >= entry_filter_vote_size[0])
        entry_filter = np.all(entry_filter_sum, axis=0)
        # plt.plot(market_df["close"] / market_df["close"].iloc[0])
        # plt.plot(entry_filter.astype(int), color='red')
        # plt.show()


        # 第二步：构建入场信号条件
        entry_signal_names = []
        entry_signal_sum = []
        e_names, e_arrays = zip(*entry_signal_combined)
        entry_signal_names.append("|".join(e_names))
        entry_signal_sum.append(np.any(e_arrays, axis=0))

        entry_signal = np.any(entry_signal_sum, axis=0)

        # 第三步：整合入场条件（过滤 AND 信号）
        entry_signal = entry_filter & entry_signal
        # plt.plot(market_df["close"] / market_df["close"].iloc[0])
        # plt.plot(entry_signal.astype(int), color='red')
        # plt.show()
        # 第四步：构建出场点位
        exit_signal_combined0 = exit_signal_combined[0]
        x_name1 = list(exit_signal_combined[-1])
        if exit_signal_combined0:
            x_name0, x_array = zip(*exit_signal_combined0)
            exit_signal_array = list(x_array)
        else:
            x_name0 =[]
            exit_signal_array = []

        x_names = list(x_name0) + list(x_name1 ) # 简化版本 - exit_signal_combined 只有一个元素
        exit_signal_names = ["|".join(x_names)]
        # 转换为 numpy 数组
        exit_signal_array = np.any(exit_signal_array, axis=0).astype(np.bool_) if exit_signal_array else np.zeros(len(market_df), dtype=np.bool_)

        # 第五步：计算出场信号
        # exit_module = import_module("cal_func.exit_pool")
        # exit_func = getattr(exit_module, "generate_exit_signal")
        if x_name1:
            exit_signal = EXIT_FUNC_G(
                market_df=market_df,
                ignore_new_entry=ignore_new_entry,
                direction_long=direction_long,
                entry_signal=entry_signal,
                exit_signal_str=x_name1,
                exit_signal_array=exit_signal_array
            )
        else:
            exit_signal = entry_signal

        # 第六步：生成组合名称和持仓序列
        combo_name = f"{'|'.join(entry_filter_names)}&{'|'.join(entry_signal_names)}&{'|'.join(exit_signal_names)}"

        entry_signal = pd.Series(entry_signal, index=market_df.index, dtype=bool)
        exit_signal = pd.Series(exit_signal, index=market_df.index, dtype=bool)
        position_series = pd.Series(np.nan, index=market_df.index, dtype=int)

        position_series.loc[exit_signal] = 0
        position_series.loc[entry_signal] = 1
        position_series.ffill(inplace=True)
        market_df[combo_name] = position_series

        return combo_name, market_df

# ==================== 单次回测层 ====================
if True:
    def basic_metrics(
            mkdf: pd.DataFrame,
            strategy_name: str,
            fees: float | int = 0.004,
            rf: float | int = 0.00,
            jz_mode: str = "d",
            time_start: pd.Timestamp = None
    ):
        """
        计算基础回测指标（整合自 jz.py，支持单利/复利模式）

        Args:
            mkdf: 行情数据以及回测中间数据，必须包含 pos, close, open, datetime 列
            strategy_name: 策略名称
            fees: 单边交易成本（例如 0.0004 为万四）
            rf: 无风险收益率（例如 0.02 为百二）
            jz_mode: 净值计算模式 ('f': 复利, 'd': 单利)
            time_start: 子周期的起始时间（可选）

        Returns:
            Tuple[pd.Series, Dict]: (累计净值曲线, 指标字典)
        """
        pos_series = mkdf["pos"]
        close_series = mkdf["close"]
        open_series = mkdf["open"]
        time_series = mkdf["datetime"]
        index_series = mkdf.index

        open_pos_con = (pos_series != pos_series.shift(1)) & (pos_series != 0)
        close_pos_con = (pos_series != pos_series.shift(-1)) & (pos_series != 0)
        trans_pos_con1 = (pos_series != pos_series.shift(1))
        # close_pos_con = (pos_series != pos_series.shift(-1))
        # ==================== 基础收益率计算 ====================
        # 交易成本
        fees_series = fees * (open_pos_con.astype(int) + close_pos_con.astype(int))*pos_series.abs()

        open_p_series = pd.Series(np.where(open_pos_con, open_series, np.nan), index=index_series).ffill()
        per_cum_jz_series = (close_series / open_p_series - 1) * pos_series

        if jz_mode :
            # 复利收益
            per_jz_nofee = close_series.pct_change(1).fillna(0) * pos_series
            per_jz_nofee[trans_pos_con1] = per_cum_jz_series

            per_jz_series = per_jz_nofee - fees_series

            jz_series = (per_jz_series + 1).cumprod()

            # plt.plot(jz_series)
        if jz_mode == 'd': #jz_mode == 'd'
            # 单利收益
            # 单利模式
            per_jz_nofee_2 = per_cum_jz_series.diff(1)
            per_jz_nofee_2[trans_pos_con1] = per_cum_jz_series
            jz_series = ((per_jz_nofee_2-fees_series).cumsum()  + 1).fillna(1)
            # jz_series = ((per_jz_nofee_2).cumsum()-(fees_series).cumsum()  + 1).fillna(1)
        #     plt.plot(jz_series)
        # plt.show()


        # ==================== 基础指标 ====================
        # 总收益率, 年化收益率, 年化波动率
        total_returns = jz_series.iloc[-1] - 1
        count_days = (time_series.iloc[-1] - time_series.iloc[0]).total_seconds() / (24 * 3600)
        delta_inv = (time_series.diff().mean().total_seconds()) / (24 * 3600)

        if total_returns >= 0:
            annualized_returns = (1 + total_returns) ** (365 / count_days) - 1
        else:
            annualized_returns = -((1 - total_returns) ** (365 / count_days) - 1)

        daily_std = np.nanstd(per_jz_series) * np.sqrt(1 / delta_inv)
        annualized_std = daily_std * (365 ** 0.5)

        # 最大回撤（正数）
        running_max = jz_series.cummax()
        drawdown = (running_max - jz_series) / running_max
        max_drawdown = drawdown.max()

        # sharpe 比率
        sharpe = (annualized_returns - rf) / annualized_std if annualized_std != 0 else 0.0

        # sortino 比率
        negative_returns = per_jz_series[per_jz_series < 0]
        if len(negative_returns) == 0:
            sortino = 100  # 给一个极大但不爆炸的值作为上限
        else:
            year_downside_std = np.std(negative_returns) * np.sqrt(1 / delta_inv) * (365 ** 0.5)
            sortino = (annualized_returns - rf) / year_downside_std if year_downside_std != 0 else 0.0

        # Calmar 比率
        calmar = annualized_returns / max_drawdown if max_drawdown != 0 else 0.0

        # 总交易成本
        total_cost = fees_series.sum()

        # bar 胜率
        total_hold_bars = (pos_series != 0).sum()
        bar_win_rate = (per_jz_series > 0).sum() / total_hold_bars if total_hold_bars > 0 else 0.0

        # ==================== 单笔交易统计 ====================
        # 每笔持仓
        bar_index_series = pd.Series(range(len(mkdf)), index=index_series)
        open_index_series = pd.Series(np.where(open_pos_con, bar_index_series, np.nan), index=index_series).ffill()
        per_hold_bars_series = pd.Series(
            np.where(close_pos_con, bar_index_series - open_index_series + 1, np.nan),
            index=index_series
        )

        # 交易次数
        trades_count = (per_hold_bars_series.notnull()).sum()

        if trades_count == 0:
            ave_hold_bars = 0.0
            trade_win_rate = 0.0
            profit_factor = 0.0
        else:
            # 平均持仓周期
            ave_hold_bars = np.sum(per_hold_bars_series) / trades_count * delta_inv

            # 交易胜率
            per_pnl_value = pd.Series(
                np.where(close_pos_con, per_cum_jz_series - 2 * fees, np.nan),
                index=index_series
            )
            profit_con = per_pnl_value > 0
            loss_con = per_pnl_value <= 0
            win_count = profit_con.sum()
            loss_count = loss_con.sum()
            trade_win_rate = win_count / trades_count

            # 盈亏比
            avg_win = np.mean(per_pnl_value[profit_con]) if win_count > 0 else 0.0
            avg_loss = np.mean(per_pnl_value[loss_con]) if loss_count > 0 else 0.0
            profit_factor = avg_win / abs(avg_loss) if avg_loss != 0 else 100

        # ==================== 组装结果 ====================
        metrics = {
            "总收益率%": float(round(total_returns * 100, 3)),
            "年化收益率%": float(round(annualized_returns * 100, 3)),
            "最大回撤%": float(round(max_drawdown * 100, 3)),
            "sharpe比率": float(round(sharpe, 3)),
            "sortino比率": float(round(sortino, 3)),
            "calmar比率": float(round(calmar, 3)),
            "年化波动率%": float(round(annualized_std * 100, 3)),
            "日波动率%": float(round(daily_std * 100, 3)),
            "均持天数": float(round(ave_hold_bars, 3)),
            "交易次数": float(trades_count),
            "交易胜率%": float(round(trade_win_rate * 100, 3)),
            "盈亏比": float(round(profit_factor, 3)),
            "bar胜率%": float(round(bar_win_rate * 100, 3)),
            "总交易成本%": float(round(total_cost * 100, 3))
        }

        if time_start is None:
            metrics = {f"total+{k}": v for k, v in metrics.items()}
            metrics = {**{ "开始时间": time_series.iloc[0], "结束时间": time_series.iloc[-1]}, **metrics,**{"策略名称": strategy_name}}
        else:
            metrics = {f"{time_start:%Y-%m-%d}+{k}": v for k, v in metrics.items()}

        return jz_series, metrics

    def compute_backtest_metrics_with_jz(
            market_df: pd.DataFrame,
            position_series: pd.Series,
            combo_name: str,
            transaction_cost: float = 0.0004,
            rf: float = 0.00,
            jz_mode: str = "d",
            resample_rule: str = "",
            direction_long =  True
    ) -> Tuple[pd.Series, Dict[str, float]]:
        """
        使用 jz.py 的 basic_metrics 计算完整回测指标

        Args:
            market_df: 市场数据 DataFrame，必须包含 OHLCV 数据
            position_series: 持仓序列（0=空仓，1=持仓）
            combo_name: 策略名称
            transaction_cost: 单边交易成本
            rf: 无风险利率
            jz_mode: 净值计算模式 ('f'=复利, 'd'=单利)
            resample_rule: 重采样规则（用于子时段指标）

        Returns:
            Tuple[pd.Series, Dict[str, float]]: (累计净值曲线, 指标字典)
        """
        # 准备数据
        mkdf = market_df.copy()
        mkdf["pos"] = position_series
        mkdf = mkdf[["datetime", "open", "high", "low", "close", "volume", "pos"]].copy()
        mkdf["pos"] = mkdf["pos"].shift(1).fillna(0)
        if direction_long:
            mkdf["pos"] = mkdf["pos"]
        if direction_long == False:
            mkdf["pos"] = mkdf["pos"]*-1
        # 计算全时段指标
        cum_curve, all_metrics = basic_metrics(
            mkdf=mkdf,
            strategy_name=combo_name,
            fees=transaction_cost,
            rf=rf,
            jz_mode=jz_mode,
            time_start=None
        )
        logger.debug(rf'{all_metrics}')
        # 计算子时段指标（如果需要）
        if resample_rule:
            for time_start, sub_df in mkdf.resample(resample_rule, on='datetime', closed="left", label="left"):
                _, sub_metrics = basic_metrics(
                    mkdf=sub_df,
                    strategy_name=combo_name,
                    fees=transaction_cost,
                    rf=rf,
                    jz_mode=jz_mode,
                    time_start=time_start
                )
                all_metrics.update(sub_metrics)

        return cum_curve, all_metrics


    def evaluate_single_strategy(
            market_df: pd.DataFrame,
            precomputed_data: Dict[str, Dict[str, np.ndarray]],
            backtest_config: Dict,
            decoded_params: Dict[str, List[str]],
    ) -> Tuple[Tuple[str, pd.DataFrame], Dict[str, float]]:
        """
        评估单个策略（使用 jz.py 的 basic_metrics）

        Args:
            market_df: 市场数据 DataFrame
            decoded_params: 解码后的策略参数字典
            precomputed_data: 预计算的信号数据字典
            backtest_config: 回测配置字典
            jz_mode: 净值计算模式 ('f'=复利, 'd'=单利)

        Returns:
            Tuple[Tuple[str, pd.DataFrame], Dict[str, float]]: ((策略名称, 市场数据), 指标字典)
        """
        market_df = market_df.copy()

        # 构建入场过滤器组合
        entry_filter_combined = [(name, precomputed_data["filters"][name]) for name in decoded_params["EntryFilters"]]

        # 构建入场信号组合
        entry_signal_combined = [(name, precomputed_data["signals"][name]) for name in decoded_params["EntrySignals"]]

        # 处理出场信号
        exit_combined = []
        exit_combined_trail = []
        extra_exit_names = ["trailing_stop", "fixed_bars", "stop_loss", "take_profit"]

        for name in decoded_params["ExitSignals"]:
            if name.split("^")[0] in extra_exit_names:
                exit_combined_trail.append(name)
            else:
                exit_combined.append((name, precomputed_data["exits"][name]))

        exit_signal_combined = [exit_combined, exit_combined_trail]

        # 生成持仓序列
        combo_name, market_df = generate_position_series(
            market_df=market_df,
            entry_filter_combined=entry_filter_combined,
            entry_signal_combined=entry_signal_combined,
            exit_signal_combined=exit_signal_combined,
            entry_filter_vote_size=[len(decoded_params["EntryFilters"])],
            ignore_new_entry=backtest_config.get("ignore_new_entry", True),
            direction_long=backtest_config["direction_long"],
        )

        # 使用 jz.py 的 basic_metrics 计算指标
        jz_series, metrics = compute_backtest_metrics_with_jz(
                    market_df=market_df,
                    position_series=market_df[combo_name].values,
                    combo_name=combo_name,
                    transaction_cost=backtest_config["transaction_cost"],
                    rf=backtest_config.get("rf", 0.00),
                    jz_mode=backtest_config["jz_mode"],
                    resample_rule=backtest_config.get("resample_rule", ""),
                    direction_long = backtest_config["direction_long"]
                )
        market_df['jz'] = jz_series


        return (combo_name, market_df.copy()), metrics


# ==================== 优化层（Pymoo）====================
class StrategyOptimizationProblem(Problem):
    """
    多目标策略优化问题（Pymoo Problem 子类）

    整合了 jz.py 的 basic_metrics 进行策略评估
    """

    def __init__(
            self,
            market_df: pd.DataFrame,
            strategy_config: List[Dict],
            objectives_config: List[Dict],
            precomputed_data: Dict[str, Dict[str, np.ndarray]],
            backtest_config: Dict,
            output_dir: str,
            save_raw_force_filter = {}
    ):
        """
        初始化优化问题

        Args:
            market_df: 市场数据 DataFrame
            strategy_config: 策略参数配置
            objectives_config: 优化目标配置
            precomputed_data: 预计算的信号数据字典
            backtest_config: 回测配置字典
            output_dir: 输出目录
            jz_mode: 净值计算模式 ('f'=复利, 'd'=单利)
        """
        n_var = sum(len(g["items"]) for g in strategy_config)
        n_obj = len(objectives_config)
        n_constr = len(strategy_config)

        super().__init__(
            n_var=n_var,
            n_obj=n_obj,
            n_constr=n_constr,
            xl=0,
            xu=1,
            vtype=bool
        )

        self.market_df = market_df
        self.strategy_config = strategy_config
        self.objectives_config = objectives_config
        self.precomputed_data = precomputed_data
        self.backtest_config = backtest_config
        self.save_raw_force_filter = save_raw_force_filter

        self.output_dir = output_dir
        self.save_path = os.path.join(self.output_dir, "raw_evaluation_cache.csv")
        
        if os.path.exists(self.save_path):
            os.remove(self.save_path)
            print(f"Deleted old cache file: {self.save_path}")

        self.evaluation_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0

    def _evaluate(self, X, out, *args, **kwargs):
        """
        评估一组策略（Pymoo 核心评估函数）
        """
        global direction
        n = X.shape[0]
        F = np.zeros((n, self.n_obj))
        G = np.zeros((n, self.n_constr))

        st = time.time()
        for i, x in enumerate(X):
            # 解码二进制决策向量
            decoded = decode_binary_vector(x, self.strategy_config)

            # 计算约束违反程度
            for j, group in enumerate(self.strategy_config):
                expected = group["select_count"]
                actual = len(decoded[group["name"]])
                G[i, j] = abs(actual - expected)

            # 如果约束不满足，跳过评估
            if np.any(G[i] > 0):
                F[i, :] = np.inf
                continue

            # 生成策略键
            strategy_key = encode_strategy_to_name(decoded)

            # 从缓存中查找或执行策略评估
            if strategy_key in self.evaluation_cache:
                metrics = self.evaluation_cache[strategy_key]
                self.cache_hits += 1
            else:
                try:

                    _, metrics = evaluate_single_strategy(
                        market_df=self.market_df,
                        decoded_params=decoded,
                        precomputed_data=self.precomputed_data,
                        backtest_config=self.backtest_config,
                    )
                    self.evaluation_cache[strategy_key] = metrics
                    self.cache_misses += 1
                except Exception as e:
                    traceback.print_exc()
                    logger.warning(f"策略评估失败 {strategy_key}: {e}")
                    F[i, :] = np.inf
                    continue

            # 提取优化目标的值
            direction_map = {"max": -1, "min": 1}
            for obj_idx, obj_config in enumerate(self.objectives_config):
                metric_name = f"{obj_config['name']}"
                if 'optimize' in obj_config.keys():
                    direction = direction_map[obj_config["optimize"]]
                if 'direction' in obj_config.keys():
                    direction = obj_config["direction"]
                value = metrics.get(metric_name, 0)
                F[i, obj_idx] = value * direction

        # 保存缓存到 CSV
        raw_df = pd.DataFrame(self.evaluation_cache.values())
        if not raw_df.empty:
            save_raw_force_filter = self.save_raw_force_filter
            force_con = 1
            for col in save_raw_force_filter.keys():
                if col not in raw_df.columns:
                    logger.error(rf"{col} not in raw_df.columns")
                    continue

                if "最大回撤" in col:
                    force_con &= raw_df[col]<abs(save_raw_force_filter[col])
                else:
                    force_con &= raw_df[col]>save_raw_force_filter[col]

            raw_df = raw_df[force_con]
            raw_df.sort_values('total+总收益率%', ascending=1, inplace=True)
            raw_df.to_csv(self.save_path, header=not os.path.exists(self.save_path), index=False, mode="a")
            self.get_raw_data()

        out["F"] = F
        out["G"] = G

    def get_cache_stats(self) -> Dict[str, int]:
        """返回缓存统计信息"""
        raw_df = pd.read_csv(self.save_path)

        raw_df = raw_df.drop_duplicates(['策略名称'],keep='last')
        raw_df.sort_values('total+总收益率%', ascending=1, inplace=True)

        raw_df.to_csv(self.save_path,  index=False, mode="w")
        logger.info(f"保存了 {len(raw_df)} 个raw策略到 {self.save_path}")

        return {
            "hits": self.cache_hits,
            "misses": self.cache_misses,
            "size": len(self.evaluation_cache)
        }
    def get_raw_data(self) -> Dict[str, int]:
            """返回缓存统计信息"""
            raw_df = pd.read_csv(self.save_path)

            raw_df = raw_df.drop_duplicates(['策略名称'],keep='last')
            raw_df.sort_values('total+总收益率%', ascending=1, inplace=True)
            raw_df.to_csv(self.save_path,  index=False, mode="w")
            logger.info(f"保存了 {len(raw_df)} 个raw策略到 {self.save_path}")



# ==================== 主入口和结果保存 ====================
def load_market_data(
        code_id: str,
        start: datetime,
        end: datetime,
        market_data_paths: Dict[str, str],
        HISTORICAL_BUFFER_DAYS = 300
) -> pd.DataFrame:
    """加载并准备市场数据（纯函数）"""
    market_path = market_data_paths.get(code_id)
    if market_path is None:
        raise ValueError(f"未找到 {code_id} 的市场数据路径")

    market_df = pd.read_csv(market_path)
    market_df["datetime"] = pd.to_datetime(market_df["candle_begin_time"]).dt.tz_localize(None)
    market_df = market_df[["datetime", "open", "high", "low", "close", "volume"]].copy()

    buffer_start = start - pd.Timedelta(days=HISTORICAL_BUFFER_DAYS)
    market_df = market_df[(market_df["datetime"] >= buffer_start) & (market_df["datetime"] <= end)].reset_index(drop=True)

    return market_df


def save_optimization_results(
        result,
        code_id: str,
        output_dir: str,
        strategy_config: List[Dict],
        objectives_config: List[Dict]
) -> Dict:
    """保存帕累托最优解到 JSON 和 CSV 文件"""
    os.makedirs(output_dir, exist_ok=True)

    if result.X is None or result.F is None:
        error_msg = "优化未找到任何满足约束条件的解。请尝试增大种群大小或调整 select_count 参数。"
        logger.error(error_msg)

        json_path = os.path.join(output_dir, f"{code_id}_pareto_solutions.json")
        csv_path = os.path.join(output_dir, f"{code_id}_pareto_metrics.csv")

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({"error": error_msg, "n_solutions": 0}, f, indent=2, ensure_ascii=False)

        pd.DataFrame({"error": [error_msg]}).to_csv(csv_path, index=False, encoding='utf-8-sig')

        return {
            "solutions": [],
            "json_path": json_path,
            "csv_path": csv_path,
            "n_solutions": 0,
            "error": error_msg
        }

    # 解码所有帕累托最优解
    solutions = []
    for i, (x, f) in enumerate(zip(result.X, result.F)):
        decoded = decode_binary_vector(x, strategy_config)
        strategy_name = encode_strategy_to_name(decoded)

        solution = {
            "rank": i,
            "strategy_name": strategy_name,
            "entry_filters": decoded["EntryFilters"],
            "entry_signals": decoded["EntrySignals"],
            "exit_signals": decoded["ExitSignals"],
            "objectives": {
                obj["name"]: float(f[idx] * obj["direction"])
                for idx, obj in enumerate(objectives_config)
            }
        }
        solutions.append(solution)

    # 保存 JSON 文件
    json_path = os.path.join(output_dir, f"{code_id}_pareto_solutions.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(solutions, f, indent=2, ensure_ascii=False)

    # 保存 CSV 文件
    df = pd.DataFrame([
        {**s["objectives"], "strategy_name": s["strategy_name"]}
        for s in solutions
    ])
    df = df.drop_duplicates(subset=['strategy_name'], keep='last')
    df = df.sort_values(by=f"total+总收益率%")
    csv_path = os.path.join(output_dir, f"{code_id}_pareto_metrics.csv")
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')

    logger.info(f"已保存 {len(solutions)} 个策略解到 {json_path} 和 {csv_path}\n{df.tail()}")

    return {
        "solutions": solutions,
        "json_path": json_path,
        "csv_path": csv_path,
        "n_solutions": len(solutions)
    }



def run_strategy_optimization(
        code_id: str,
        start: datetime,
        end: datetime,
        strategy_config: List[Dict],
        objectives_config: List[Dict],
        backtest_config: Dict,
        save_raw_force_filter_config: Dict,
        market_data_paths: Dict[str, str],
        output_dir: str,
        population_size: int = 100,
        n_generations: int = 50,
        show_progress: bool = True,
) -> Dict:
    """
    Args:
        code_id: 品种代码
        start: 优化开始日期
        end: 优化结束日期
        strategy_config: 策略参数配置
        objectives_config: 优化目标配置
        backtest_config: 回测配置
        market_data_paths: 市场数据文件路径字典
        output_dir: 结果输出目录
        population_size: 种群大小
        n_generations: 迭代代数
        show_progress: 是否显示进度条
        jz_mode: 净值计算模式 ('f'=复利, 'd'=单利)

    Returns:
        Dict: 优化结果字典
    """
    logger.info(f"开始优化 {code_id} ({start} 至 {end})，净值模式: {backtest_config.get('jz_mode')}")


    # 加载市场数据
    logger.info("正在加载市场数据...")
    market_df_full = load_market_data(code_id, start, end, market_data_paths)

    # 收集所有信号名称
    all_signals = collect_all_signals(strategy_config)

    # 预计算所有信号
    logger.info("正在预计算所有信号...")


    precomputed_data_full = {
        "filters": precompute_all_signals(market_df_full, all_signals["filters"],
                                          "cal_func.filter_pool",
                                          "filter","and",
                                          show_progress),

        "signals": precompute_all_signals(market_df_full, all_signals["signals"],
                                          "cal_func.entry_pool",
                                          "entry", "or",show_progress),

        "exits": precompute_all_signals(market_df_full, all_signals["exits"],
                                        "cal_func.entry_pool",
                                        "exit","or", show_progress)
    }

    # 过滤到目标回测时间段
    logger.info("正在过滤到目标回测时间段...")
    period_cond = (market_df_full["datetime"] >= start) & (market_df_full["datetime"] <= end)
    market_df = market_df_full[period_cond].reset_index(drop=True)

    period_cond_np = period_cond.values
    precomputed_data = {
        "filters": {name: array[period_cond_np] for name, array in precomputed_data_full["filters"].items()},
        "signals": {name: array[period_cond_np] for name, array in precomputed_data_full["signals"].items()},
        "exits": {name: array[period_cond_np] for name, array in precomputed_data_full["exits"].items()},
    }

    # 创建优化问题实例
    logger.info("正在创建优化项目...")
    problem = StrategyOptimizationProblem(
                        market_df=market_df,
                        strategy_config=strategy_config,
                        objectives_config=objectives_config,
                        precomputed_data=precomputed_data,
                        backtest_config=backtest_config,
                        output_dir=output_dir,
                        save_raw_force_filter=save_raw_force_filter_config
                    )

    # 配置 NSGA-II 算法
    algorithm = NSGA2(
        pop_size=population_size,
        sampling=BinaryRandomSampling(),
        crossover=BinomialCrossover(prob=0.9),
        mutation=BitflipMutation(prob=0.1),
        eliminate_duplicates=True
    )

    # 运行优化
    logger.info(f"正在运行优化 (种群大小={population_size}, 迭代代数={n_generations})...")
    print_search_space_stats(strategy_config, population_size, n_generations)
    res = minimize( problem,
                    algorithm,
                    termination=get_termination("n_gen", n_generations),
                    seed=42,
                    verbose=True
                )

    # 输出缓存统计
    cache_stats = problem.get_cache_stats()
    logger.info(f"缓存统计 - 命中: {cache_stats['hits']}, 未命中: {cache_stats['misses']}, 大小: {cache_stats['size']}")

    # 保存优化结果
    logger.info("正在保存优化结果...")
    res = save_optimization_results(res, code_id, output_dir, strategy_config, objectives_config)

    return res


def run_strategy_single(
        code_id: str,
        start: datetime,
        end: datetime,
        decoded_params: List[Dict],
        backtest_config: Dict,
        market_data_paths: Dict[str, str],
        show_progress: bool = True,
) :

    # 清除出场信号模块级缓存（防止不同品种间 shape 相同导致缓存污染）
    if CLEAR_EXIT_CACHE is not None:
        CLEAR_EXIT_CACHE()

    collect_all_signals_list_fro_precal = {
        "filters": [],
        "signals": [],
        "exits": []
    }
    
    logger.info("正在加载市场数据...")
    market_df_full = load_market_data(code_id, start, end, market_data_paths)
    
    all_cl_params = []
    for single_cl_params0 in decoded_params:
        if isinstance(single_cl_params0, str) or single_cl_params0 is None:
            EntryFilters, EntrySignals, ExitSignals = single_cl_params0.split('&')
            EntryFilters, EntrySignals, ExitSignals = [i for i in EntryFilters.split('|')], [i for i in EntrySignals.split('|')], [i for i in ExitSignals.split('|')]
        else:
            EntryFilters, EntrySignals, ExitSignals = single_cl_params0.get("EntryFilters"), single_cl_params0.get("EntrySignals"), single_cl_params0.get("ExitSignals")

        single_cl_params0 = {"EntryFilters": EntryFilters, "EntrySignals": EntrySignals, "ExitSignals": ExitSignals}
        all_cl_params.append(single_cl_params0)

        collect_all_signals_list_fro_precal["filters"].extend(EntryFilters)
        collect_all_signals_list_fro_precal["signals"].extend(EntrySignals)
        collect_all_signals_list_fro_precal["exits"].extend(ExitSignals)

    # 预计算所有信号
    logger.info("正在预计算所有信号...")
    precomputed_data_full = {
        "filters": precompute_all_signals(
            market_df_full, collect_all_signals_list_fro_precal["filters"], "cal_func.filter_pool", "filter", show_progress
        ),
        "signals": precompute_all_signals(
            market_df_full, collect_all_signals_list_fro_precal["signals"], "cal_func.entry_pool", "entry", show_progress
        ),
        "exits": precompute_all_signals(
            market_df_full, collect_all_signals_list_fro_precal["exits"], "cal_func.entry_pool", "exit", show_progress
        )
    }
    
    logger.info("正在过滤到目标回测时间段...")
    period_cond = (market_df_full["datetime"] >= start) & (market_df_full["datetime"] <= end)
    market_df = market_df_full[period_cond].reset_index(drop=True)
    
    period_cond_np = period_cond.values
    precomputed_data = {
        "filters": {name: array[period_cond_np] for name, array in precomputed_data_full["filters"].items()},
        "signals": {name: array[period_cond_np] for name, array in precomputed_data_full["signals"].items()},
        "exits": {name: array[period_cond_np] for name, array in precomputed_data_full["exits"].items()},
    }
    
    all_metrics = []
    all_stg_names = []
    all_pos_df = pd.DataFrame()
    all_jz_df = pd.DataFrame()
    processed_raw_strategies = set()
    market_df0 = market_df.copy()
    run_single_func0 = partial(evaluate_single_strategy,
                               market_df0,
                               precomputed_data,
                               backtest_config,)

    for idx, single_cl_params0 in enumerate(all_cl_params):
        filters_str = '|'.join(single_cl_params0.get("EntryFilters", []))
        signals_str = '|'.join(single_cl_params0.get("EntrySignals", []))
        exits_str = '|'.join(single_cl_params0.get("ExitSignals", []))
        raw_strategy_key = f"{filters_str}&{signals_str}&{exits_str}"

        if raw_strategy_key in processed_raw_strategies:
            print(f"  → 跳过重复策略（索引{idx}）: {raw_strategy_key[:50]}...")
            continue

        processed_raw_strategies.add(raw_strategy_key)

        try:
            (combo_name, market_df), metrics = run_single_func0(decoded_params=single_cl_params0)

        except Exception as e:
            print(e)
            print(traceback.format_exc())
            logger.error(f"策略回测失败：{raw_strategy_key}",exc_info=True)
            continue

        res = { **metrics}
        all_metrics.append(res)
        all_stg_names.append(combo_name)
        
        if all_pos_df.empty:
            all_pos_df = market_df[['datetime', 'open', 'high', 'low', 'close', 'volume',combo_name]]
        else:
            all_pos_df = pd.merge(all_pos_df, market_df[["datetime", combo_name]], on="datetime", how="left")

        if all_jz_df.empty:
            market_df[combo_name] = market_df['jz']
            all_jz_df = market_df[['datetime', 'open', 'high', 'low', 'close', 'volume',combo_name]]
        else:
            market_df[combo_name] = market_df['jz']
            all_jz_df = pd.merge(all_jz_df, market_df[["datetime", combo_name]], on="datetime", how="left")



    return (all_stg_names, all_pos_df, all_jz_df), all_metrics

# ==================== 预计算层 ====================
if True :
    def precompute_single_signal(
            market_df: pd.DataFrame,
            signal_name: str,
            pool_module: Any,
            pool_type: str
    ) -> np.ndarray:

        func_name, *func_params = parse_strategy_expression3(signal_name)

        if func_name == "_":
            if pool_type == "filter":
                return np.array([True] * len(market_df), dtype=bool)
            else:
                return np.array([False] * len(market_df), dtype=bool)

        func = getattr(pool_module, func_name)
        if func is None:
            raise ValueError(f"Function {func_name} not found")


        params = parse_params_to_types(func_params)
        logger.debug(signal_name)
        return func(market_df, *params)

    def precompute_all_signals(
            market_df: pd.DataFrame,
            signal_names: List[str],
            pool_path: str,
            pool_type: str,
            pool_concatenate: str,
            show_progress: bool = False
    ) -> Dict[str, np.ndarray]:
        pool_module = import_module(pool_path)

        if pool_type == "filter":
            res0 = np.array([True] * len(market_df), dtype=bool)
        else:
            res0 = np.array([False] * len(market_df), dtype=bool)

        extra_exit_names = ["trailing_stop", "fixed_bars", "stop_loss", "take_profit"]
        all_pre = {}

        # --- 在循环前包装 tqdm ---
        if show_progress:
            from tqdm import tqdm
            signal_names = tqdm(signal_names, desc=f"预计算 {pool_type} 信号")

        for name in signal_names:
            if "|" in name:
                names = name.split("|")
                name_res = []
                for name0 in names:
                    if ("^" not in name0) or name0.split("^")[0] in extra_exit_names:
                        res = res0
                    else:
                        res = precompute_single_signal(market_df, name0, pool_module, pool_type)
                        if res is None:
                            res = res0
                    name_res.append(res)

                if pool_concatenate == "or":
                    all_res = np.any(name_res, axis=0)
                elif pool_concatenate == "and":
                    all_res = np.all(name_res, axis=0)
                else:
                    all_res = np.any(name_res, axis=0)
                all_pre[name] = all_res  # --- 修复：应该存到 all_pre 而非 name_res ---
            else:
                if ("^" not in name) or name.split("^")[0] in extra_exit_names:
                    res = res0
                else:
                    res = precompute_single_signal(market_df, name, pool_module, pool_type)
                all_pre[name] = res

        return all_pre

    def basic_metrics(
            mkdf: pd.DataFrame,
            strategy_name: str,
            fees: float | int = 0.004,
            rf: float | int = 0.00,
            jz_mode: str = "d",
            time_start: pd.Timestamp = None
    ):
        """
        计算基础回测指标（整合自 jz.py，支持单利/复利模式）

        Args:
            mkdf: 行情数据以及回测中间数据，必须包含 pos, close, open, datetime 列
            strategy_name: 策略名称
            fees: 单边交易成本（例如 0.0004 为万四）
            rf: 无风险收益率（例如 0.02 为百二）
            jz_mode: 净值计算模式 ('f': 复利, 'd': 单利)
            time_start: 子周期的起始时间（可选）

        Returns:
            Tuple[pd.Series, Dict]: (累计净值曲线, 指标字典)
        """
        pos_series = mkdf["pos"]
        close_series = mkdf["close"]
        open_series = mkdf["open"]
        time_series = mkdf["datetime"]
        index_series = mkdf.index

        open_pos_con = (pos_series != pos_series.shift(1)) & (pos_series != 0)
        close_pos_con = (pos_series != pos_series.shift(-1)) & (pos_series != 0)
        trans_pos_con1 = (pos_series != pos_series.shift(1))
        # close_pos_con = (pos_series != pos_series.shift(-1))
        # ==================== 基础收益率计算 ====================
        # 交易成本
        fees_series = fees * (open_pos_con.astype(int) + close_pos_con.astype(int))*pos_series.abs()

        open_p_series = pd.Series(np.where(open_pos_con, open_series, np.nan), index=index_series).ffill()
        per_cum_jz_series = (close_series / open_p_series - 1) * pos_series

        if jz_mode :
            # 复利收益
            per_jz_nofee = close_series.pct_change(1).fillna(0) * pos_series
            per_jz_nofee[trans_pos_con1] = per_cum_jz_series

            per_jz_series = per_jz_nofee - fees_series

            jz_series = (per_jz_series + 1).cumprod()

            # plt.plot(jz_series)
        if jz_mode == 'd': #jz_mode == 'd'
            # 单利收益
            # 单利模式
            per_jz_nofee_2 = per_cum_jz_series.diff(1)
            per_jz_nofee_2[trans_pos_con1] = per_cum_jz_series
            jz_series = ((per_jz_nofee_2-fees_series).cumsum()  + 1).fillna(1)
            # jz_series = ((per_jz_nofee_2).cumsum()-(fees_series).cumsum()  + 1).fillna(1)
        #     plt.plot(jz_series)
        # plt.show()


        # ==================== 基础指标 ====================
        # 总收益率, 年化收益率, 年化波动率
        total_returns = jz_series.iloc[-1] - 1
        count_days = (time_series.iloc[-1] - time_series.iloc[0]).total_seconds() / (24 * 3600)
        delta_inv = (time_series.diff().mean().total_seconds()) / (24 * 3600)

        if total_returns >= 0:
            annualized_returns = (1 + total_returns) ** (365 / count_days) - 1
        else:
            annualized_returns = -((1 - total_returns) ** (365 / count_days) - 1)

        daily_std = np.nanstd(per_jz_series) * np.sqrt(1 / delta_inv)
        annualized_std = daily_std * (365 ** 0.5)

        # 最大回撤（正数）
        running_max = jz_series.cummax()
        drawdown = (running_max - jz_series) / running_max
        max_drawdown = drawdown.max()

        # sharpe 比率
        sharpe = (annualized_returns - rf) / annualized_std if annualized_std != 0 else 0.0

        # sortino 比率
        negative_returns = per_jz_series[per_jz_series < 0]
        if len(negative_returns) == 0:
            sortino = 100  # 给一个极大但不爆炸的值作为上限
        else:
            year_downside_std = np.std(negative_returns) * np.sqrt(1 / delta_inv) * (365 ** 0.5)
            sortino = (annualized_returns - rf) / year_downside_std if year_downside_std != 0 else 0.0

        # Calmar 比率
        calmar = annualized_returns / max_drawdown if max_drawdown != 0 else 0.0

        # 总交易成本
        total_cost = fees_series.sum()

        # bar 胜率
        total_hold_bars = (pos_series != 0).sum()
        bar_win_rate = (per_jz_series > 0).sum() / total_hold_bars if total_hold_bars > 0 else 0.0

        # ==================== 单笔交易统计 ====================
        # 每笔持仓
        bar_index_series = pd.Series(range(len(mkdf)), index=index_series)
        open_index_series = pd.Series(np.where(open_pos_con, bar_index_series, np.nan), index=index_series).ffill()
        per_hold_bars_series = pd.Series(
            np.where(close_pos_con, bar_index_series - open_index_series + 1, np.nan),
            index=index_series
        )

        # 交易次数
        trades_count = (per_hold_bars_series.notnull()).sum()

        if trades_count == 0:
            ave_hold_bars = 0.0
            trade_win_rate = 0.0
            profit_factor = 0.0
        else:
            # 平均持仓周期
            ave_hold_bars = np.sum(per_hold_bars_series) / trades_count * delta_inv

            # 交易胜率
            per_pnl_value = pd.Series(
                np.where(close_pos_con, per_cum_jz_series - 2 * fees, np.nan),
                index=index_series
            )
            profit_con = per_pnl_value > 0
            loss_con = per_pnl_value <= 0
            win_count = profit_con.sum()
            loss_count = loss_con.sum()
            trade_win_rate = win_count / trades_count

            # 盈亏比
            avg_win = np.mean(per_pnl_value[profit_con]) if win_count > 0 else 0.0
            avg_loss = np.mean(per_pnl_value[loss_con]) if loss_count > 0 else 0.0
            profit_factor = avg_win / abs(avg_loss) if avg_loss != 0 else 100

        # ==================== 组装结果 ====================
        metrics = {
            "总收益率%": float(round(total_returns * 100, 3)),
            "年化收益率%": float(round(annualized_returns * 100, 3)),
            "最大回撤%": float(round(max_drawdown * 100, 3)),
            "sharpe比率": float(round(sharpe, 3)),
            "sortino比率": float(round(sortino, 3)),
            "calmar比率": float(round(calmar, 3)),
            "年化波动率%": float(round(annualized_std * 100, 3)),
            "日波动率%": float(round(daily_std * 100, 3)),
            "均持天数": float(round(ave_hold_bars, 3)),
            "交易次数": float(trades_count),
            "交易胜率%": float(round(trade_win_rate * 100, 3)),
            "盈亏比": float(round(profit_factor, 3)),
            "bar胜率%": float(round(bar_win_rate * 100, 3)),
            "总交易成本%": float(round(total_cost * 100, 3))
        }

        if time_start is None:
            metrics = {f"total+{k}": v for k, v in metrics.items()}
            metrics = {**{ "开始时间": time_series.iloc[0], "结束时间": time_series.iloc[-1]}, **metrics,**{"策略名称": strategy_name}}
        else:
            metrics = {f"{time_start:%Y-%m-%d}+{k}": v for k, v in metrics.items()}

        return jz_series, metrics

    def compute_backtest_metrics_with_jz(
            market_df: pd.DataFrame,
            position_series: pd.Series,
            combo_name: str,
            transaction_cost: float = 0.0004,
            rf: float = 0.00,
            jz_mode: str = "d",
            resample_rule: str = "",
            direction_long =  True
    ) -> Tuple[pd.Series, Dict[str, float]]:
        """
        使用 jz.py 的 basic_metrics 计算完整回测指标

        Args:
            market_df: 市场数据 DataFrame，必须包含 OHLCV 数据
            position_series: 持仓序列（0=空仓，1=持仓）
            combo_name: 策略名称
            transaction_cost: 单边交易成本
            rf: 无风险利率
            jz_mode: 净值计算模式 ('f'=复利, 'd'=单利)
            resample_rule: 重采样规则（用于子时段指标）

        Returns:
            Tuple[pd.Series, Dict[str, float]]: (累计净值曲线, 指标字典)
        """
        # 准备数据
        mkdf = market_df.copy()
        mkdf["pos"] = position_series
        mkdf = mkdf[["datetime", "open", "high", "low", "close", "volume", "pos"]].copy()
        mkdf["pos"] = mkdf["pos"].shift(1).fillna(0)
        # plt.plot(mkdf["pos"])
        # plt.show()
        if direction_long:
            mkdf["pos"] = mkdf["pos"]
        if not direction_long:
            mkdf["pos"] = mkdf["pos"]*-1
        # plt.plot(mkdf["pos"])
        # plt.show()
        # 计算全时段指标
        cum_curve, all_metrics = basic_metrics(
            mkdf=mkdf,
            strategy_name=combo_name,
            fees=transaction_cost,
            rf=rf,
            jz_mode=jz_mode,
            time_start=None
        )
        # plt.plot(cum_curve)
        # plt.plot(mkdf["close"]/mkdf["close"].iloc[0],color="r")
        # plt.show()
        logger.debug(rf'{all_metrics}')
        # 计算子时段指标（如果需要）
        if resample_rule:
            for time_start, sub_df in mkdf.resample(resample_rule, on='datetime', closed="left", label="left"):
                _, sub_metrics = basic_metrics(
                    mkdf=sub_df,
                    strategy_name=combo_name,
                    fees=transaction_cost,
                    rf=rf,
                    jz_mode=jz_mode,
                    time_start=time_start
                )
                all_metrics.update(sub_metrics)

        return cum_curve, all_metrics

    def generate_position_series(
            market_df: pd.DataFrame,
            entry_filter_combined: List[Tuple[str, np.ndarray]],
            entry_signal_combined: List[Tuple[str, np.ndarray]],
            exit_signal_combined: List[List[Tuple[str, np.ndarray]]],
            entry_filter_vote_size: List[int],
            ignore_new_entry: bool,
            direction_long: bool,
    ) -> Tuple[str, pd.Series]:
        """
        从过滤器和信号生成持仓序列（纯函数）

        Args:
            market_df: 市场数据 DataFrame
            entry_filter_combined: 入场过滤器组合列表
            entry_signal_combined: 入场信号组合列表
            exit_signal_combined: 出场信号组合列表
            entry_filter_vote_size: 每个过滤器组需要的投票数
            ignore_new_entry: 持仓时是否忽略新的入场条件
            direction_long: 交易方向（True=做多，False=做空）

        Returns:
            Tuple[str, pd.Series]: (策略名称, 持仓序列)
        """
        # 第一步：构建入场过滤条件
        entry_filter_names = []
        entry_filter_sum = []

        f_names, f_arrays = zip(*entry_filter_combined)
        entry_filter_names.append("|".join(f_names))
        entry_filter_sum.append(np.sum(f_arrays, axis=0) >= entry_filter_vote_size[0])
        entry_filter = np.all(entry_filter_sum, axis=0) # t\f
        # plt.plot(market_df["close"] / market_df["close"].iloc[0])
        # plt.plot(entry_filter.astype(int), color='red')
        # plt.show()


        # 第二步：构建入场信号条件
        entry_signal_names = []
        entry_signal_sum = []
        e_names, e_arrays = zip(*entry_signal_combined)
        entry_signal_names.append("|".join(e_names))
        entry_signal_sum.append(np.any(e_arrays, axis=0))

        entry_signal = np.any(entry_signal_sum, axis=0)

        # 第三步：整合入场条件（过滤 AND 信号）
        entry_signal = entry_filter & entry_signal
        # plt.plot(market_df["close"] / market_df["close"].iloc[0])
        # plt.plot(entry_signal.astype(int), color='red')
        # plt.show()
        # 第四步：构建出场点位
        exit_signal_combined0 = exit_signal_combined[0]
        x_name1 = list(exit_signal_combined[-1])
        if exit_signal_combined0:
            x_name0, x_array = zip(*exit_signal_combined0)
            exit_signal_array = list(x_array)
        else:
            x_name0 =[]
            exit_signal_array = []

        x_names = list(x_name0) + list(x_name1 ) # 简化版本 - exit_signal_combined 只有一个元素
        exit_signal_names = ["|".join(x_names)]
        # 转换为 numpy 数组
        exit_signal_array = np.any(exit_signal_array, axis=0).astype(np.bool_) if exit_signal_array else np.zeros(len(market_df), dtype=np.bool_)

        # 第五步：计算出场信号
        # exit_module = import_module("cal_func.exit_pool")
        # exit_func = getattr(exit_module, "generate_exit_signal")
        if x_name1:
            exit_signal = EXIT_FUNC_G(
                market_df=market_df,
                ignore_new_entry=ignore_new_entry,
                direction_long=direction_long,
                entry_signal=entry_signal,
                exit_signal_str=x_name1,
                exit_signal_array=exit_signal_array
            )
        else:
            exit_signal = entry_signal

        # 第六步：生成组合名称和持仓序列
        combo_name = f"{'|'.join(entry_filter_names)}&{'|'.join(entry_signal_names)}&{'|'.join(exit_signal_names)}"

        entry_signal = pd.Series(entry_signal, index=market_df.index, dtype=bool)
        exit_signal = pd.Series(exit_signal, index=market_df.index, dtype=bool)
        position_series = pd.Series(np.nan, index=market_df.index, dtype=int)

        position_series.loc[exit_signal] = 0
        position_series.loc[entry_signal] = 1
        position_series.ffill(inplace=True)
        market_df[combo_name] = position_series

        return combo_name, market_df

    def run_single(
            market_df: pd.DataFrame,
            decoded_params: List[Dict],
            backtest_config: Dict,
            show_progress: bool = True,
    ) -> Tuple[Tuple[List, pd.DataFrame], Any]:
        import_dir = 'all_cal_pool.'

        collect_all_signals_list_fro_precal = {
            "filters": [],
            "signals": [],
            "exits": []
        }

        all_cl_params = []
        for single_cl_params0 in decoded_params:
            if isinstance(single_cl_params0, str) or single_cl_params0 is None:
                EntryFilters, EntrySignals, ExitSignals = single_cl_params0.split('&')
                EntryFilters, EntrySignals, ExitSignals = [i for i in EntryFilters.split('|')], [i for i in EntrySignals.split('|')], [i for i in ExitSignals.split('|')]
            else:
                EntryFilters, EntrySignals, ExitSignals = single_cl_params0.get("EntryFilters"), single_cl_params0.get("EntrySignals"), single_cl_params0.get("ExitSignals")

            single_cl_params0 = {"EntryFilters": EntryFilters, "EntrySignals": EntrySignals, "ExitSignals": ExitSignals}
            all_cl_params.append(single_cl_params0)

            collect_all_signals_list_fro_precal["filters"].extend(EntryFilters)
            collect_all_signals_list_fro_precal["signals"].extend(EntrySignals)
            collect_all_signals_list_fro_precal["exits"].extend(ExitSignals)

        # 预计算所有信号
        logger.info("正在预计算所有信号...")
        precomputed_data_full = {
            "filters": precompute_all_signals(
                market_df_full, collect_all_signals_list_fro_precal["filters"], rf"{import_dir}filter_pool", "filter", show_progress
            ),
            "signals": precompute_all_signals(
                market_df_full, collect_all_signals_list_fro_precal["signals"], f"{import_dir}entry_pool", "entry", show_progress
            ),
            "exits": precompute_all_signals(
                market_df_full, collect_all_signals_list_fro_precal["exits"], f"{import_dir}entry_pool", "exit", show_progress
            )
        }


        period_cond_np = period_cond.values
        precomputed_data = {
            "filters": {name: array[period_cond_np] for name, array in precomputed_data_full["filters"].items()},
            "signals": {name: array[period_cond_np] for name, array in precomputed_data_full["signals"].items()},
            "exits": {name: array[period_cond_np] for name, array in precomputed_data_full["exits"].items()},
        }

        all_metrics = []
        all_stg_names = []
        all_pos_df = pd.DataFrame()
        processed_raw_strategies = set()
        market_df0 = market_df.copy()

        for idx, single_cl_params0 in enumerate(all_cl_params):
            filters_str = '|'.join(single_cl_params0.get("EntryFilters", []))
            signals_str = '|'.join(single_cl_params0.get("EntrySignals", []))
            exits_str = '|'.join(single_cl_params0.get("ExitSignals", []))
            raw_strategy_key = f"{filters_str}&{signals_str}&{exits_str}"

            if raw_strategy_key in processed_raw_strategies:
                logger.warning(f"  → 跳过重复策略: {raw_strategy_key}")
                continue

            processed_raw_strategies.add(raw_strategy_key)

            try:
                # 构建入场过滤器组合
                entry_filter_combined = [(name, precomputed_data["filters"][name]) for name in decoded_params["EntryFilters"]]

                # 构建入场信号组合
                entry_signal_combined = [(name, precomputed_data["signals"][name]) for name in decoded_params["EntrySignals"]]

                # 处理出场信号
                exit_combined = []
                exit_combined_trail = []
                extra_exit_names = ["trailing_stop", "fixed_bars", "stop_loss", "take_profit"]

                for name in decoded_params["ExitSignals"]:
                    if name.split("^")[0] in extra_exit_names:
                        exit_combined_trail.append(name)
                    else:
                        exit_combined.append((name, precomputed_data["exits"][name]))

                exit_signal_combined = [exit_combined, exit_combined_trail]

                # 生成持仓序列
                combo_name, market_df00 = generate_position_series(
                                            market_df=market_df0.copy(),
                                            entry_filter_combined=entry_filter_combined,
                                            entry_signal_combined=entry_signal_combined,
                                            exit_signal_combined=exit_signal_combined,
                                            entry_filter_vote_size=[len(decoded_params["EntryFilters"])],
                                            ignore_new_entry=backtest_config.get("ignore_new_entry", True),
                                            direction_long=backtest_config["direction_long"],
                                        )
                print(backtest_config)
                input()
                # 使用 jz.py 的 basic_metrics 计算指标
                jz, metrics = compute_backtest_metrics_with_jz(
                    market_df=market_df00,
                    position_series=market_df00[combo_name].values,
                    combo_name=combo_name,
                    transaction_cost=backtest_config["transaction_cost"],
                    rf=backtest_config.get("rf", 0.00),
                    jz_mode=backtest_config["jz_mode"],
                    resample_rule=backtest_config.get("resample_rule", ""),
                    direction_long = backtest_config["direction_long"]

                )



            except Exception as e:
                print(e)
                print(traceback.format_exc())
                logger.error(f"策略回测失败：{raw_strategy_key}",exc_info=True)
                continue

            res = { **metrics}
            all_metrics.append(res)
            all_stg_names.append(combo_name)

            if all_pos_df.empty:
                all_pos_df = market_df00
            else:
                all_pos_df = pd.merge(all_pos_df, market_df00[["datetime", combo_name]], on="datetime", how="left")



        return (all_stg_names, all_pos_df), all_metrics



def run_optimization_for_single_code(
        code_id: str,
        start: datetime,
        end: datetime,
        output_dir: str,
        market_data_paths: Dict[str, str],
        strategy_config: Optional[List[Dict]] = None,
        objectives_config: Optional[List[Dict]] = None,
        backtest_config: Optional[Dict] = None,
        save_raw_force_filter_config: Optional[Dict] = None,
        population_size: int = 100,
        n_generations: int = 50,
) -> Dict:
    """
    单品种优化便捷函数

    Args:
        jz_mode: 净值计算模式 ('f'=复利, 'd'=单利)
    """
    logger.info(f"正在处理品种 {code_id}...")

    output_dir = os.path.join(output_dir, f"optimization_{code_id}")
    os.makedirs(output_dir, exist_ok=True)

    stf_config = strategy_config.get(code_id)
    objectives = objectives_config
    backtest = backtest_config
    save_raw_force_filter_config = save_raw_force_filter_config or {}
    return run_strategy_optimization(
                code_id=code_id,
                start=start,
                end=end,
                strategy_config=stf_config,
                objectives_config=objectives,
                backtest_config=backtest,
                save_raw_force_filter_config = save_raw_force_filter_config,
                market_data_paths=market_data_paths,
                output_dir=output_dir,
                population_size=population_size,
                n_generations=n_generations,
            )


def run_optimization_batch(
        code_ids: List[str],
        start: datetime,
        end: datetime,
        output_dir: str,
        market_data_paths: Dict[str, str],
        strategy_config: Optional[List[Dict]] = None,
        objectives_config: Optional[List[Dict]] = None,
        backtest_config: Optional[Dict] = None,
        save_raw_force_filter_config = {},
        population_size: int = 100,
        n_generations: int = 50,
        num_processes=6
) -> List[Dict]:
    results = []
    logger.info(f"正在优化 {len(code_ids)} 个品种...")
    if num_processes > 1:

        p00 = Pool(processes=num_processes)

        worker_func = partial(
                    run_optimization_for_single_code,
                    start=start,
                    end=end,
                    output_dir=output_dir,
                    market_data_paths=market_data_paths,
                    strategy_config=strategy_config,
                    objectives_config=objectives_config,
                    backtest_config=backtest_config,
                    save_raw_force_filter_config = save_raw_force_filter_config,
                    population_size=population_size,
                    n_generations=n_generations,
        )

        # 多进程并行计算
        for code_id in code_ids:
            p00.apply_async(worker_func, args=(code_id,),
                            callback=lambda v: logger.warning(f"{v}"),
                            error_callback=lambda e: logger.error(f"Error occurred: {e}",exc_info=True),)

        p00.close()
        p00.join()
    else:
        for code_id in code_ids:
            try:
                result = run_optimization_for_single_code(
                    code_id=code_id,
                    start=start,
                    end=end,
                    output_dir=output_dir,
                    market_data_paths=market_data_paths,
                    strategy_config=strategy_config,
                    objectives_config=objectives_config,
                    backtest_config=backtest_config,
                    save_raw_force_filter_config = save_raw_force_filter_config,
                    population_size=population_size,
                    n_generations=n_generations,
                )
                results.append({"code_id": code_id, "status": "success", **result})
            except Exception as e:
                logger.error(f"{code_id} 优化失败: {e}")
                traceback.print_exc()
                results.append({"code_id": code_id, "status": "failed", "error": str(e)})

    return results


if __name__ == "__main__":
    if 1:
        decoded_params = [
            "aroon_diff_higher0^21|emacd_higher_signal^89^178^89|aroon_diff_higher0^89&"
            "adx_plus_crossover_minus^34|tp_low_1^15^0|s_tp_low_1^15^0^2&"
            "trailing_stop^34^3.5|emacd_histogram_start_decrease^55^110^55",
        ]
        # 回测默认配置
        BACKTEST_CONFIG = {
            "transaction_cost": 0.0000,  # 单边交易成本（万三）
            "direction_long": True,  # 做多方向
            "ignore_new_entry": True,  # 持仓时不更新出场条件
            "resample_rule": "",  # 重采样规则（空字符串表示不重采样）
            "rf": 0.00,
            "jz_mode": "d"  # 无风险利率
        }

        logger.info("正在加载市场数据...")
        market_df_full = load_market_data(code_id, start, end, market_data_paths)
        logger.info("正在过滤到目标回测时间段...")
        period_cond = (market_df_full["datetime"] >= start) & (market_df_full["datetime"] <= end)
        market_df = market_df_full[period_cond].reset_index(drop=True)

        (combo_name, market_df0), metrics = run_single(market_df=market_df,decoded_params=decoded_params,backtest_config=BACKTEST_CONFIG,)

        logger.info(f"策略组合: {combo_name}\n{metrics}")

        logger.info(f"\n{pd.DataFrame(metrics)}")
