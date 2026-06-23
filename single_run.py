
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

pd.set_option('display.max_rows', 10000)
pd.set_option('display.max_columns', 10000)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 1500)
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('expand_frame_repr', False)
pd.set_option('display.float_format', lambda x: '%.4f' % x)

# import matplotlib
# import matplotlib.pyplot as plt
# matplotlib.use('tkAgg')
# matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
# matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

import_dir = 'all_cal_pool.'
# import_dir = 'cal_func.'
import_dir = ''

exit_module = import_module(f"{import_dir}exit_pool")
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
    # ==================== 主入口和结果保存 ====================
    def load_market_data(
            code_id: str,
            start: datetime,
            end: datetime,
            market_data_paths: Dict[str, str],
            HISTORICAL_BUFFER_DAYS=300
    ) -> pd.DataFrame:
        """加载并准备市场数据（纯函数）"""
        market_path = market_data_paths.get(code_id)
        if market_path is None:
            raise ValueError(f"未找到 {code_id} 的市场数据路径")

        market_df = pd.read_csv(market_path)
        if "candle_begin_time" not in market_df.columns:
            market_df.rename(columns={"datetime": "candle_begin_time"}, inplace=True)
        market_df["candle_begin_time"] = pd.to_datetime(market_df["candle_begin_time"],utc=True)
        market_df = market_df[["candle_begin_time", "open", "high", "low", "close", "volume"]].copy()

        start = pd.to_datetime(start,utc=True)
        end = pd.to_datetime(end,utc=True)
        buffer_start = start - pd.Timedelta(days=HISTORICAL_BUFFER_DAYS)
        market_df = market_df[(market_df["candle_begin_time"] >= buffer_start) & (market_df["candle_begin_time"] <= end)].reset_index(drop=True)

        return market_df


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
        time_series = mkdf["candle_begin_time"]
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
            resample_rule: str = ""
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
        mkdf = mkdf[["candle_begin_time", "open", "high", "low", "close", "volume", "pos"]].copy()
        mkdf["pos"] = mkdf["pos"].shift(1).fillna(0)

        # 计算全时段指标
        cum_curve, all_metrics = basic_metrics(
            mkdf=mkdf,
            strategy_name=combo_name,
            fees=transaction_cost,
            rf=rf,
            jz_mode=jz_mode,
            time_start=None
        )
        mkdf[combo_name] = cum_curve
        logger.debug(rf'{all_metrics}')
        # 计算子时段指标（如果需要）
        if resample_rule:
            for time_start, sub_df in mkdf.resample(resample_rule, on='candle_begin_time', closed="left", label="left"):
                _, sub_metrics = basic_metrics(
                    mkdf=sub_df,
                    strategy_name=combo_name,
                    fees=transaction_cost,
                    rf=rf,
                    jz_mode=jz_mode,
                    time_start=time_start
                )
                all_metrics.update(sub_metrics)

        return mkdf, all_metrics


if True :

    def run_single(
            market_df: pd.DataFrame,
            
            decoded_params: List[Dict],
            backtest_config: Dict,
            show_progress: bool = True,
    ):

        # 清除出场信号模块级缓存（防止不同品种间 shape 相同导致缓存污染）
        if CLEAR_EXIT_CACHE is not None:
            CLEAR_EXIT_CACHE()
            logger.warning(f"清除出场信号模块级缓存{len(decoded_params)}")

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
        logger.info(f"正在预计算所有信号...")
        precomputed_data_full = {
            "filters": precompute_all_signals(market_df, collect_all_signals_list_fro_precal["filters"], rf"{import_dir}filter_pool", "filter", show_progress
            ),
            "signals": precompute_all_signals(market_df, collect_all_signals_list_fro_precal["signals"], f"{import_dir}entry_pool", "entry", show_progress
            ),
            "exits": precompute_all_signals(market_df, collect_all_signals_list_fro_precal["exits"], f"{import_dir}entry_pool", "exit", show_progress
            )
        }
        logger.info(f"正在预计算所有信号...")


        precomputed_data = {
            "filters": {name: array for name, array in precomputed_data_full["filters"].items()},
            "signals": {name: array for name, array in precomputed_data_full["signals"].items()},
            "exits": {name: array for name, array in precomputed_data_full["exits"].items()},
        }

        all_metrics = []
        all_stg_names = []
        all_pos_df = pd.DataFrame()
        all_jz_df = pd.DataFrame()
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
                entry_filter_combined = [(name, precomputed_data["filters"][name]) for name in single_cl_params0["EntryFilters"]]

                # 构建入场信号组合
                entry_signal_combined = [(name, precomputed_data["signals"][name]) for name in single_cl_params0["EntrySignals"]]

                # 处理出场信号
                exit_combined = []
                exit_combined_trail = []
                extra_exit_names = ["trailing_stop", "fixed_bars", "stop_loss", "take_profit"]

                for name in single_cl_params0["ExitSignals"]:
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
                    entry_filter_vote_size=[len(single_cl_params0["EntryFilters"])],
                    ignore_new_entry=backtest_config.get("ignore_new_entry", True),
                    direction_long=backtest_config["direction_long"],
                )
                # 使用 jz.py 的 basic_metrics 计算指标
                market_df00 = market_df00.reset_index(drop=False)
                # market_df00[combo_name] = market_df00[combo_name].apply(lambda x: 1 if x > 0 else -1)
                if all_pos_df.empty:
                    all_pos_df = market_df00[["candle_begin_time",'open','close', combo_name]]
                else:
                    all_pos_df = pd.merge(all_pos_df, market_df00[["candle_begin_time", combo_name]], on="candle_begin_time", how="left")
                all_stg_names.append(combo_name)

                if True == 1:
                    market_df00, metrics = compute_backtest_metrics_with_jz(
                        market_df=market_df00,
                        position_series=market_df00[combo_name].values,
                        combo_name=combo_name,
                        transaction_cost=backtest_config["transaction_cost"],
                        rf=backtest_config.get("rf", 0.00),
                        jz_mode=backtest_config["jz_mode"],
                        resample_rule=backtest_config.get("resample_rule", "")
                    )


                    all_metrics.append(metrics)

                    if all_jz_df.empty:
                        all_jz_df = market_df00[["candle_begin_time",'open','close', combo_name]]
                    else:
                        all_jz_df = pd.merge(all_jz_df, market_df00[["candle_begin_time", combo_name]], on="candle_begin_time", how="left")

            except Exception as e:

                logger.error(f"策略回测失败：{e} ：{traceback.format_exc()}")
                raise e
                continue

    



        return (all_stg_names, all_pos_df,all_jz_df), all_metrics




if __name__ == "__main__":
    import redis
    import pandas as pd

    import matplotlib.pyplot as plt
    import matplotlib

    matplotlib.use('tkAgg')
    matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
    matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

    inv0 = '15min'
    data_redis_client = redis.Redis(
        host="47.83.140.255",
        port=6379,
        password="e7LpFUoMwBzjfPBvJW",
        decode_responses=True
    )
    s0 = "CLmain"
    kline_ = data_redis_client.hget(f"tiger_his_kline:{inv0}", s0)
    df0 = pd.read_json(kline_)

    df0['candle_begin_time'] = pd.to_datetime(df0['candle_begin_time'], utc=True)
    df0['candle_now_time'] = pd.to_datetime(time.time(), unit='s', utc=True)
    df0['is_over'] = (df0['candle_now_time'] + pd.Timedelta(seconds=10 * 2) > df0['candle_begin_time'] + pd.Timedelta(inv0)).astype(int)
    df0['candle_begin_time_BJ'] = pd.to_datetime(df0['candle_begin_time'], utc=True) + pd.Timedelta(hours=8)
    df0 = df0.sort_values('candle_begin_time')
    df0 = df0[['candle_begin_time_BJ', 'candle_begin_time', 'open', "high", 'low', 'close', 'volume',
               'candle_now_time', 'is_over']]
    logger.info(f"{s0}-{inv0}-数量：{df0.shape}，最后：is_over过滤：\n{df0.tail(3).to_string()}\n")
    df0 = df0[df0['is_over'] == 1].reset_index(drop=True)

    market_df_full = df0.copy()
    start, end = "2026-03-01", "2026-06-30"
    logger.info("正在过滤到目标回测时间段...")
    period_cond = (market_df_full["candle_begin_time"] >= pd.to_datetime(start, utc=True)) & (market_df_full["candle_begin_time"] <= pd.to_datetime(end, utc=True))
    market_df = market_df_full[period_cond].reset_index(drop=True)
    print(market_df.shape)
    print(market_df.head())
    print(market_df.tail())



    if 1:
        df = pd.read_csv(rf"C:/CTA_run/金银铜油-run-new02/one_stgcfg_choose_策略.csv")
        cl_names = df[df['coin_name']=='CL2608']['cl_name'].tolist()
        decoded_params = cl_names

        # 回测默认配置
        BACKTEST_CONFIG = {
            "transaction_cost": 0.0005,  # 单边交易成本（万三）
            "direction_long": True,  # 做多方向
            "ignore_new_entry": True,  # 持仓时不更新出场条件
            "resample_rule": "",  # 重采样规则（空字符串表示不重采样）
            "rf": 0.00,
            "jz_mode": "d"  # 无风险利率
        }
        code_id = s0

        (all_stg_names, all_pos_df, jz_df), all_metrics = run_single(market_df=market_df,decoded_params=decoded_params,backtest_config=BACKTEST_CONFIG,)

        logger.info(f"策略组合: {all_stg_names}\n{all_metrics}")
        plt.figure(figsize=(20, 10))
        plt.plot(jz_df[all_stg_names])
        plt.plot(jz_df['close']/jz_df['close'].iloc[0], label='close', color='black', linewidth=1.2)
        plt.xticks( jz_df.index[::100], jz_df["candle_begin_time"].iloc[::100],rotation=45)
        plt.legend('left')
        plt.show()

        logger.info(f"\n{pd.DataFrame(all_metrics)}")
