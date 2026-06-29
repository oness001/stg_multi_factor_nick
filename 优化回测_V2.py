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

# 禁用 pymoo 编译警告（提高运行速度）
Config.warnings['not_compiled'] = False

# ==================== 预先导入所有模块到 sys.modules ====================
# 提前导入所有需要的模块，避免运行时重复导入
CAL_DIR = 'cal_func.'

# logger.info("正在预先导入策略模块到 sys.modules...")

import_module(f"{CAL_DIR}indicators")

# sys.modules['indicators'] = sys.modules[f"{CAL_DIR}indicators"]

import_module(f"{CAL_DIR}filter_pool")
import_module(f"{CAL_DIR}entry_pool")
import_module(f"{CAL_DIR}exit_pool")
# logger.info("已预加载模块: indicators, filter_pool, entry_pool, exit_pool")

# ==================== 构建全局函数字典 ====================
# 一次性收集所有用户函数到全局字典，之后直接 O(1) 查找
_SIGNAL_FUNCTIONS = {}
for module_path in [f"{CAL_DIR}filter_pool", f"{CAL_DIR}entry_pool", f"{CAL_DIR}exit_pool"]:
    module = sys.modules[module_path]
    for name in dir(module):
        # 只收集用户定义的函数，排除内置函数
        if not name.startswith('_') and not name.startswith('builtins'):
            obj = getattr(module, name)
            # 只收集可调用的函数
            if callable(obj):
                _SIGNAL_FUNCTIONS[name] = obj
# 第五步：计算出场信号
exit_module = sys.modules[f"{CAL_DIR}exit_pool"]

EXIT_FUNC_G = _SIGNAL_FUNCTIONS["generate_exit_signal"]
CLEAR_EXIT_CACHE = _SIGNAL_FUNCTIONS["clear_exit_cache"]


# logger.info(f"已构建全局函数字典，共 {len(_SIGNAL_FUNCTIONS)} 个函数")

def get_signal_function(func_name: str) -> Any:
    if func_name in _SIGNAL_FUNCTIONS:
        return _SIGNAL_FUNCTIONS[func_name]

    raise ValueError(
        f"函数 '{func_name}' 未找到。\n"
        f"可用函数: {', '.join(list(_SIGNAL_FUNCTIONS.keys())[:20])}..."
    )


def precompute_all_signals(
        market_df: pd.DataFrame,
        signal_names: List[str],
        pool_type: str,
        pool_concatenate: str,
        show_progress: bool = False
) -> Dict[str, np.ndarray]:
    """
    快速预计算所有信号（自动从预加载模块查找函数）

    Args:
        market_df: 市场数据 DataFrame
        signal_names: 信号名称列表
        pool_type: 信号类型 ("filter", "entry", "exit")
        pool_concatenate: 组合方式 ("or", "and")
        show_progress: 是否显示进度条

    Returns:
        Dict[str, np.ndarray]: 信号名称到信号数组的映射
    """
    # 默认返回值
    if pool_type == "filter":
        res0 = np.array([True] * len(market_df), dtype=bool)
    else:
        res0 = np.array([False] * len(market_df), dtype=bool)

    # 特殊处理的退出信号名称
    extra_exit_names = {"trailing_stop", "fixed_bars", "stop_loss", "take_profit"}
    all_pre = {}

    # 进度条
    if show_progress:
        from tqdm import tqdm
        signal_names = tqdm(signal_names, desc=f"预计算 {pool_type} 信号")

    # 主循环：自动查找并调用函数
    for name in signal_names:
        if "|" in name:
            names = name.split("|")
            name_res = []
            for name0 in names:
                if ("^" not in name0) or name0.split("^")[0] in extra_exit_names:
                    res = res0
                else:
                    func_name, *func_params = parse_strategy_expression3(name0)
                    func = get_signal_function(func_name)  # 自动查找
                    params = parse_params_to_types(func_params)
                    res = func(market_df, *params)
                name_res.append(res)

            # 组合结果
            if pool_concatenate == "or":
                all_res = np.any(name_res, axis=0)
            elif pool_concatenate == "and":
                all_res = np.all(name_res, axis=0)
            else:
                all_res = np.any(name_res, axis=0)
            all_pre[name] = all_res
        else:
            if ("^" not in name) or name.split("^")[0] in extra_exit_names:
                res = res0
            else:
                func_name, *func_params = parse_strategy_expression3(name)
                func = get_signal_function(func_name)  # 自动查找
                params = parse_params_to_types(func_params)
                res = func(market_df, *params)
            all_pre[name] = res

    return all_pre


# ==================== 基础工具函数 ====================

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
        market_df["datetime"] = pd.to_datetime(market_df["candle_begin_time"]).dt.tz_localize(None)
        market_df = market_df[["datetime", "open", "high", "low", "close", "volume"]].copy()

        buffer_start = start - pd.Timedelta(days=HISTORICAL_BUFFER_DAYS)
        market_df = market_df[(market_df["datetime"] >= buffer_start) & (market_df["datetime"] <= end)].reset_index(
            drop=True)

        return market_df


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
                converted.append(round(float(param), 5))
            elif param.isdigit() or ("-" in param and param.replace("-", "").isdigit()):
                converted.append(int(param))
            else:
                converted.append(param)  # 保持字符串不变

        return converted


    def parse_strategy_expression3(signal_name: str) -> Tuple[str]:
        """将字符串解析分解"""
        func_name, *func_params = signal_name.split("^")
        return func_name, *func_params


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

# 优化类定义
if True:

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
            direction_long=backtest_config["direction_long"]
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
                save_raw_force_filter={}
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
            X_len = len(X)
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
                        force_con &= raw_df[col] < abs(save_raw_force_filter[col])
                    else:
                        force_con &= raw_df[col] > save_raw_force_filter[col]

                raw_df = raw_df[force_con]
                raw_df.drop_duplicates(['total+总收益率%'], inplace=True)
                raw_df.sort_values('total+总收益率%', ascending=1, inplace=True)
                raw_df = raw_df.iloc[-1 * int(X_len * 0.3):]
                raw_df.reset_index(drop=True, inplace=True)
                raw_df.to_csv(self.save_path, header=not os.path.exists(self.save_path), index=False, mode="a")
                # self.get_raw_data()

            out["F"] = F
            out["G"] = G

        def get_cache_stats(self) -> Dict[str, int]:
            """返回缓存统计信息"""
            raw_df = pd.read_csv(self.save_path)

            raw_df = raw_df.drop_duplicates(['策略名称'], keep='last')
            raw_df = raw_df.drop_duplicates(['total+总收益率%'], keep='last')
            raw_df.sort_values('total+总收益率%', ascending=1, inplace=True)

            raw_df.to_csv(self.save_path, index=False, mode="w")
            logger.info(f"保存了 {len(raw_df)} 个raw策略到 {self.save_path}")

            return {
                "hits": self.cache_hits,
                "misses": self.cache_misses,
                "size": len(self.evaluation_cache)
            }

        def get_raw_data(self) -> Dict[str, int]:
            """返回缓存统计信息"""
            raw_df = pd.read_csv(self.save_path)
            raw_df = raw_df.drop_duplicates(['策略名称'], keep='last')
            raw_df.sort_values('total+总收益率%', ascending=1, inplace=True)
            raw_df.to_csv(self.save_path, index=False, mode="w")
            logger.info(f"保存了 {len(raw_df)} 个raw策略到 {self.save_path}")


    def ffill_numpy(arr: np.ndarray) -> np.ndarray:
        """Numpy 版前向填充（等效于 pandas ffill）

        对 NaN 值用最近的有效值填充；全 NaN 的前缀部分保留 NaN。

        Args:
            arr: 含 NaN 的 numpy 数组

        Returns:
            前向填充后的数组副本
        """
        mask = np.isnan(arr)
        if not mask.any():
            return arr.copy()

        idx = np.arange(len(arr))
        last_valid = np.where(~mask, idx, 0)
        np.maximum.accumulate(last_valid, out=last_valid)
        result = arr[last_valid]

        # 全 NaN 前缀保留 NaN
        first_valid = int(np.argmax(~mask))
        if first_valid > 0 and mask[0]:
            result[:first_valid] = np.nan
        return result


    def cal_jz(
            mkdf: pd.DataFrame,
            fees: float | int = 0.004,
            jz_mode: str = "d",
            pos_col='pos',
            close_col='close',
            open_col='open',
    ):

        pos_series = mkdf[pos_col]
        close_series = mkdf[close_col]
        open_series = mkdf[open_col]
        index_series = mkdf.index

        open_pos_con = (pos_series != pos_series.shift(1)) & (pos_series != 0)
        close_pos_con = (pos_series != pos_series.shift(-1)) & (pos_series != 0)
        trans_pos_con1 = (pos_series != pos_series.shift(1))
        # ==================== 基础收益率计算 ====================
        # 交易成本
        fees_series = fees * (open_pos_con.astype(int) + close_pos_con.astype(int)) * pos_series.abs()

        open_p_series = pd.Series(np.where(open_pos_con, open_series, np.nan), index=index_series).ffill()
        per_cum_jz_series = (close_series / open_p_series - 1) * pos_series

        if jz_mode:
            # 复利收益
            per_jz_nofee = close_series.pct_change(1).fillna(0) * pos_series
            per_jz_nofee[trans_pos_con1] = per_cum_jz_series

            per_jz_series = per_jz_nofee - fees_series

            jz_series = (per_jz_series + 1).cumprod()

            # plt.plot(jz_series)
        if jz_mode == 'd':  # jz_mode == 'd'
            # 单利收益
            # 单利模式
            per_jz_nofee_2 = per_cum_jz_series.diff(1)
            per_jz_nofee_2[trans_pos_con1] = per_cum_jz_series
            jz_series = ((per_jz_nofee_2 - fees_series).cumsum() + 1).fillna(1)

        return jz_series,


    def basic_metrics(
            positions: np.ndarray,
            close: np.ndarray,
            open_: np.ndarray,
            datetime_arr: np.ndarray,
            strategy_name: str,
            fees: float = 0.004,
            rf: float = 0.00,
            jz_mode: str = "d",
            time_start: pd.Timestamp | None = None,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Numpy 优化版回测指标计算

        Args:
            positions: 持仓序列（1=多头, -1=空头, 0=空仓）
            close: 收盘价序列
            open_: 开盘价序列
            datetime_arr: 时间序列（pd.Timestamp 的 numpy 数组）
            strategy_name: 策略名称标识
            fees: 单边交易成本比例
            rf: 无风险收益率
            jz_mode: 净值模式 ('f'=复利, 'd'=单利)
            time_start: 子周期起始时间（None 表示全时段）

        Returns:
            (净值曲线数组, 指标字典)
        """
        n = len(positions)
        if n == 0:
            return np.array([]), {}

        pos = positions.astype(np.float64)

        # --- 前后位移持仓，用于检测开仓/平仓 ---
        prev_position = np.empty(n, dtype=np.float64)
        prev_position[0] = 0.0
        prev_position[1:] = pos[:-1]

        next_position = np.empty(n, dtype=np.float64)
        next_position[:-1] = pos[1:]
        next_position[-1] = 0.0

        is_open_pos = (pos != prev_position) & (pos != 0)
        is_close_pos = (pos != next_position) & (pos != 0)
        is_pos_changed = pos != prev_position

        # --- 交易成本 ---
        fee_arr = fees * (
                is_open_pos.astype(np.float64) + is_close_pos.astype(np.float64)
        ) * np.abs(pos)

        # --- 复利收益 ---
        pct_chg = np.empty(n, dtype=np.float64)
        pct_chg[0] = 0.0
        pct_chg[1:] = (close[1:] - close[:-1]) / close[:-1]
        raw_return = pct_chg * pos
        raw_return[is_open_pos] = (
                (close[is_open_pos] / open_[is_open_pos] - 1) * pos[is_open_pos]
        )
        net_return = raw_return - fee_arr

        # --- 单利收益 ---
        open_price = np.where(is_open_pos, open_, np.nan)
        open_price = ffill_numpy(open_price)
        with np.errstate(divide='ignore', invalid='ignore'):
            cum_return_no_fee = (close / open_price - 1) * pos

        # --- 累计净值 ---
        if jz_mode == 'f':
            jz_arr = np.cumprod(net_return + 1)
        elif jz_mode == 'd':
            daily_raw_return = np.empty(n, dtype=np.float64)
            daily_raw_return[0] = np.nan
            daily_raw_return[1:] = cum_return_no_fee[1:] - cum_return_no_fee[:-1]
            daily_raw_return[is_pos_changed] = cum_return_no_fee[is_pos_changed]
            cumsum_input = daily_raw_return - fee_arr
            nan_mask = np.isnan(cumsum_input)
            cumsum_input = np.where(nan_mask, 0.0, cumsum_input)
            jz_arr = np.cumsum(cumsum_input) + 1
            jz_arr[nan_mask] = 1.0
        else:
            raise ValueError(f"无效的 jz_mode: {jz_mode}")

        # --- 基础指标 ---
        total_return = jz_arr[-1] - 1
        total_days = (
                (datetime_arr[-1] - datetime_arr[0]).astype('timedelta64[s]')
                .astype(np.float64) / (24 * 3600)
        )
        time_diffs_s = (
            np.diff(datetime_arr).astype('timedelta64[s]').astype(np.float64)
        )
        days_per_bar = np.nanmean(time_diffs_s) / (24 * 3600)

        if total_return >= 0:
            annualized_return = (1 + total_return) ** (365 / total_days) - 1
        else:
            annualized_return = -((1 - total_return) ** (365 / total_days) - 1)

        daily_std = np.nanstd(net_return) * np.sqrt(1 / days_per_bar)
        annualized_std = daily_std * (365 ** 0.5)

        # 最大回撤（正数）
        running_max = np.maximum.accumulate(jz_arr)
        with np.errstate(divide='ignore', invalid='ignore'):
            drawdown = (running_max - jz_arr) / running_max
        max_drawdown = np.nanmax(drawdown)

        # Sharpe / Sortino / Calmar
        sharpe = (
            (annualized_return - rf) / annualized_std
            if annualized_std != 0 else 0.0
        )
        negative_returns = net_return[net_return < 0]
        if len(negative_returns) == 0:
            sortino = 100
        else:
            year_downside_std = (
                    np.std(negative_returns) * np.sqrt(1 / days_per_bar) * (365 ** 0.5)
            )
            sortino = (
                (annualized_return - rf) / year_downside_std
                if year_downside_std != 0 else 0.0
            )
        calmar = annualized_return / max_drawdown if max_drawdown != 0 else 0.0

        # 总交易成本 & bar 胜率
        total_cost = np.sum(fee_arr)
        total_hold_bars = np.sum(pos != 0)
        bar_win_rate = (
            np.sum(net_return > 0) / total_hold_bars
            if total_hold_bars > 0 else 0.0
        )

        # --- 单笔交易统计 ---
        bar_index = np.arange(n)
        open_index_arr = np.where(is_open_pos, bar_index, np.nan)
        open_index_arr = ffill_numpy(open_index_arr)
        # 安全地处理 NaN 值：将 NaN 替换为 0（这些位置不会被用于计算）
        open_index_arr = np.nan_to_num(open_index_arr, nan=0.0).astype(np.int64)
        trade_duration = np.where(
            is_close_pos, bar_index - open_index_arr + 1, np.nan
        )
        trades_count = int(np.sum(~np.isnan(trade_duration)))

        if trades_count == 0:
            avg_hold_days = 0.0
            trade_win_rate = 0.0
            profit_factor = 0.0
        else:
            avg_hold_days = np.nansum(trade_duration) / trades_count * days_per_bar
            trade_pnl = np.where(
                is_close_pos, cum_return_no_fee - 2 * fees, np.nan
            )
            valid_mask = ~np.isnan(trade_pnl)
            is_profit = (trade_pnl > 0) & valid_mask
            is_loss = (trade_pnl <= 0) & valid_mask
            win_count = int(np.sum(is_profit))
            loss_count = int(np.sum(is_loss))
            trade_win_rate = win_count / trades_count
            avg_win = np.mean(trade_pnl[is_profit]) if win_count > 0 else 0.0
            avg_loss = np.mean(trade_pnl[is_loss]) if loss_count > 0 else 0.0
            profit_factor = -avg_win / avg_loss if avg_loss != 0 else 100

        # --- 组装结果 ---
        metrics = {
            "总收益率%": float(round(total_return * 100, 3)),
            "年化收益率%": float(round(annualized_return * 100, 3)),
            "最大回撤%": float(round(max_drawdown * 100, 3)),
            "sharpe比率": float(round(sharpe, 3)),
            "sortino比率": float(round(sortino, 3)),
            "calmar比率": float(round(calmar, 3)),
            "年化波动率%": float(round(annualized_std * 100, 3)),
            "日波动率%": float(round(daily_std * 100, 3)),
            "均持天数": float(round(avg_hold_days, 3)),
            "交易次数": float(trades_count),
            "交易胜率%": float(round(trade_win_rate * 100, 3)),
            "盈亏比": float(round(profit_factor, 3)),
            "bar胜率%": float(round(bar_win_rate * 100, 3)),
            "总交易成本%": float(round(total_cost * 100, 3)),
        }

        if time_start is None:
            metrics = {f"total+{k}": v for k, v in metrics.items()}
            metrics = {
                **{
                    "策略名称": strategy_name,
                    "开始时间": datetime_arr[0],
                    "结束时间": datetime_arr[-1],
                },
                **metrics,
            }
        else:
            metrics = {f"{time_start:%Y-%m-%d}+{k}": v for k, v in metrics.items()}

        return jz_arr, metrics


    def basic_metrics0(
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
        fees_series = fees * (open_pos_con.astype(int) + close_pos_con.astype(int)) * pos_series.abs()

        open_p_series = pd.Series(np.where(open_pos_con, open_series, np.nan), index=index_series).ffill()
        per_cum_jz_series = (close_series / open_p_series - 1) * pos_series

        if jz_mode == f'f':
            # 复利收益
            per_jz_nofee = close_series.pct_change(1).fillna(0) * pos_series
            per_jz_nofee[trans_pos_con1] = per_cum_jz_series
            per_jz_series = per_jz_nofee - fees_series

            jz_series = (per_jz_series + 1).cumprod()

            # plt.plot(jz_series)
        if jz_mode == 'd':  # jz_mode == 'd'
            # 单利收益
            # 单利模式
            per_jz_nofee_2 = per_cum_jz_series.diff(1)
            per_jz_nofee_2[trans_pos_con1] = per_cum_jz_series
            jz_series = ((per_jz_nofee_2 - fees_series).cumsum() + 1).fillna(1)

        per_jz_series = jz_series.pct_change().fillna(0)

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
            metrics = {**{"开始时间": time_series.iloc[0], "结束时间": time_series.iloc[-1]}, **metrics,
                       **{"策略名称": strategy_name}}
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
            direction_long=True
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
            mkdf["pos"] = mkdf["pos"] * -1
        # plt.plot(mkdf["pos"])
        # plt.show()
        # 计算全时段指标
        # cum_curve, all_metrics = basic_metrics0(
        #     mkdf=mkdf,
        #     strategy_name=combo_name,
        #     fees=transaction_cost,
        #     rf=rf,
        #     jz_mode=jz_mode,
        #     time_start=None
        # )
        cum_curve, all_metrics = basic_metrics(
            positions=mkdf["pos"].to_numpy(),
            close=mkdf["close"].to_numpy(),
            open_=mkdf["open"].to_numpy(),
            datetime_arr=mkdf["datetime"].to_numpy(),
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
        entry_filter = np.all(entry_filter_sum, axis=0)  # t\f
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
            x_name0 = []
            exit_signal_array = []

        x_names = list(x_name0) + list(x_name1)  # 简化版本 - exit_signal_combined 只有一个元素
        exit_signal_names = ["|".join(x_names)]
        # 转换为 numpy 数组
        exit_signal_array = np.any(exit_signal_array, axis=0).astype(np.bool_) if exit_signal_array else np.zeros(
            len(market_df), dtype=np.bool_)

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
            exit_signal = exit_signal_array

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

# 批量运行优化
if True:

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
                                              "filter", "and",
                                              show_progress),

            "signals": precompute_all_signals(market_df_full, all_signals["signals"],
                                              "entry", "or", show_progress),

            "exits": precompute_all_signals(market_df_full, all_signals["exits"],
                                            "exit", "or", show_progress)
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
        res = minimize(problem,
                       algorithm,
                       termination=get_termination("n_gen", n_generations),
                       seed=42,
                       verbose=False
                       )

        # 输出缓存统计
        cache_stats = problem.get_cache_stats()
        logger.info(
            f"缓存统计 - 命中: {cache_stats['hits']}, 未命中: {cache_stats['misses']}, 大小: {cache_stats['size']}")

        # 保存优化结果
        logger.info("正在保存优化结果...")
        # res = save_optimization_results(res, code_id, output_dir, strategy_config, objectives_config)

        return res


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
            save_raw_force_filter_config=save_raw_force_filter_config,
            market_data_paths=market_data_paths,
            output_dir=output_dir,
            population_size=population_size,
            n_generations=n_generations,
        )


    # run_optimization_for_single_code 多个运行
    def run_optimization_batch(
            code_ids: List[str],
            start: datetime,
            end: datetime,
            output_dir: str,
            market_data_paths: Dict[str, str],
            strategy_config: Optional[List[Dict]] = None,
            objectives_config: Optional[List[Dict]] = None,
            backtest_config: Optional[Dict] = None,
            save_raw_force_filter_config={},
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
                save_raw_force_filter_config=save_raw_force_filter_config,
                population_size=population_size,
                n_generations=n_generations,
            )

            # 多进程并行计算
            for code_id in code_ids:
                p00.apply_async(worker_func, args=(code_id,),
                                callback=lambda v: logger.warning(f"{v}"),
                                error_callback=lambda e: logger.error(f"Error occurred: {e}", exc_info=True), )

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
                        save_raw_force_filter_config=save_raw_force_filter_config,
                        population_size=population_size,
                        n_generations=n_generations,
                    )
                    results.append({"code_id": code_id, "status": "success", **result})
                except Exception as e:
                    logger.error(f"{code_id} 优化失败: {e}")
                    traceback.print_exc()
                    results.append({"code_id": code_id, "status": "failed", "error": str(e)})

        return results

if True:

    def run_single_with_pre_cal_data(
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
                EntryFilters, EntrySignals, ExitSignals = [i for i in EntryFilters.split('|')], [i for i in
                                                                                                 EntrySignals.split(
                                                                                                     '|')], [i for i in
                                                                                                             ExitSignals.split(
                                                                                                                 '|')]
            else:
                EntryFilters, EntrySignals, ExitSignals = single_cl_params0.get("EntryFilters"), single_cl_params0.get(
                    "EntrySignals"), single_cl_params0.get("ExitSignals")

            single_cl_params0 = {"EntryFilters": EntryFilters, "EntrySignals": EntrySignals, "ExitSignals": ExitSignals}
            all_cl_params.append(single_cl_params0)

            collect_all_signals_list_fro_precal["filters"].extend(EntryFilters)
            collect_all_signals_list_fro_precal["signals"].extend(EntrySignals)
            collect_all_signals_list_fro_precal["exits"].extend(ExitSignals)

        # 预计算所有信号
        logger.info("正在预计算所有信号...")
        precomputed_data_full = {
            "filters": precompute_all_signals(
                market_df_full, collect_all_signals_list_fro_precal["filters"], "filter", "and", show_progress
            ),
            "signals": precompute_all_signals(
                market_df_full, collect_all_signals_list_fro_precal["signals"], "entry", "or", show_progress
            ),
            "exits": precompute_all_signals(
                market_df_full, collect_all_signals_list_fro_precal["exits"], "exit", "or", show_progress
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
                entry_filter_combined = [(name, precomputed_data["filters"][name]) for name in
                                         decoded_params["EntryFilters"]]

                # 构建入场信号组合
                entry_signal_combined = [(name, precomputed_data["signals"][name]) for name in
                                         decoded_params["EntrySignals"]]

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

                # 使用 jz.py 的 basic_metrics 计算指标
                jz, metrics = compute_backtest_metrics_with_jz(
                    market_df=market_df00,
                    position_series=market_df00[combo_name].values,
                    combo_name=combo_name,
                    transaction_cost=backtest_config["transaction_cost"],
                    rf=backtest_config.get("rf", 0.00),
                    jz_mode=backtest_config["jz_mode"],
                    resample_rule=backtest_config.get("resample_rule", ""),
                    direction_long=backtest_config["direction_long"]

                )



            except Exception as e:
                print(e)
                print(traceback.format_exc())
                logger.error(f"策略回测失败：{raw_strategy_key}", exc_info=True)
                continue

            res = {**metrics}
            all_metrics.append(res)
            all_stg_names.append(combo_name)

            if all_pos_df.empty:
                all_pos_df = market_df00
            else:
                all_pos_df = pd.merge(all_pos_df, market_df00[["datetime", combo_name]], on="datetime", how="left")

        return (all_stg_names, all_pos_df), all_metrics


    def run_strategy_single(
            code_id: str,
            start: datetime,
            end: datetime,
            decoded_params: List[Dict],
            backtest_config: Dict,
            market_data_paths: Dict[str, str],
            show_progress: bool = True,
    ):
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
                EntryFilters, EntrySignals, ExitSignals = [i for i in EntryFilters.split('|')], [i for i in
                                                                                                 EntrySignals.split(
                                                                                                     '|')], [i for i in
                                                                                                             ExitSignals.split(
                                                                                                                 '|')]
            else:
                EntryFilters, EntrySignals, ExitSignals = single_cl_params0.get("EntryFilters"), single_cl_params0.get(
                    "EntrySignals"), single_cl_params0.get("ExitSignals")

            single_cl_params0 = {"EntryFilters": EntryFilters, "EntrySignals": EntrySignals, "ExitSignals": ExitSignals}
            all_cl_params.append(single_cl_params0)

            collect_all_signals_list_fro_precal["filters"].extend(EntryFilters)
            collect_all_signals_list_fro_precal["signals"].extend(EntrySignals)
            collect_all_signals_list_fro_precal["exits"].extend(ExitSignals)

        # 预计算所有信号
        logger.info("正在预计算所有信号...")
        precomputed_data_full = {
            "filters": precompute_all_signals(
                market_df_full, collect_all_signals_list_fro_precal["filters"], "filter", "and", show_progress
            ),
            "signals": precompute_all_signals(
                market_df_full, collect_all_signals_list_fro_precal["signals"], "entry", "or", show_progress
            ),
            "exits": precompute_all_signals(
                market_df_full, collect_all_signals_list_fro_precal["exits"], "exit", "or", show_progress
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
                                   backtest_config, )

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
                logger.error(f"策略回测失败：{raw_strategy_key}", exc_info=True)
                continue

            res = {**metrics}
            all_metrics.append(res)
            all_stg_names.append(combo_name)

            if all_pos_df.empty:
                all_pos_df = market_df[['datetime', 'open', 'high', 'low', 'close', 'volume', combo_name]]
            else:
                all_pos_df = pd.merge(all_pos_df, market_df[["datetime", combo_name]], on="datetime", how="left")

            if all_jz_df.empty:
                market_df[combo_name] = market_df['jz']
                all_jz_df = market_df[['datetime', 'open', 'high', 'low', 'close', 'volume', combo_name]]
            else:
                market_df[combo_name] = market_df['jz']
                all_jz_df = pd.merge(all_jz_df, market_df[["datetime", combo_name]], on="datetime", how="left")

        return (all_stg_names, all_pos_df, all_jz_df), all_metrics


    def run_batch_single_stg(
            market_df: pd.DataFrame,
            precomputed_data: Dict[str, Dict[str, np.ndarray]],
            filters: List[str],
            signals: List[str],
            exits: List[str],
            backtest_config: Dict,
            select_counts: Dict[str, int],
            show_progress: bool = True,
            cpu_n=1
    ) -> Tuple[pd.DataFrame, List[Dict]]:
        """
        批量回测策略组合（直接使用预计算信号）

        Args:
            market_df: 市场数据 DataFrame
            precomputed_data: 预计算的信号数据字典 {"filters": {...}, "signals": {...}, "exits": {...}}
            filters: 可选过滤器名称列表
            signals: 可选信号名称列表
            exits: 可选退出信号名称列表
            backtest_config: 回测配置字典
            select_counts: 选择数量 {"filters": 2, "signals": 2, "exits": 2}
            show_progress: 是否显示进度条

        Returns:
            Tuple[pd.DataFrame, List[Dict]]: (结果DataFrame按收益率排序, 所有策略指标列表)
        """
        from itertools import combinations
        from math import comb

        # 计算总组合数
        n_filters = comb(len(filters), select_counts["filters"])
        n_signals = comb(len(signals), select_counts["signals"])
        n_exits = comb(len(exits), select_counts["exits"])
        total_combinations = n_filters * n_signals * n_exits

        logger.info(f"开始批量回测 - 过滤器: C({len(filters)}, {select_counts['filters']}) = {n_filters}, "
                    f"信号: C({len(signals)}, {select_counts['signals']}) = {n_signals}, "
                    f"退出: C({len(exits)}, {select_counts['exits']}) = {n_exits}, "
                    f"总组合数: {total_combinations:,}")

        all_metrics = []
        market_df0 = market_df.copy()

        # 创建进度条
        if show_progress:
            from tqdm import tqdm
            pbar = tqdm(total=total_combinations, desc="批量回测进度")
        all_param_list = []
        # 生成所有可能的组合
        for filters_combo in combinations(filters, select_counts["filters"]):
            for signals_combo in combinations(signals, select_counts["signals"]):
                for exits_combo in combinations(exits, select_counts["exits"]):
                    # 解码参数
                    decoded_params = {
                        "EntryFilters": list(filters_combo),
                        "EntrySignals": list(signals_combo),
                        "ExitSignals": list(exits_combo)
                    }
                    all_param_list.append(decoded_params)
        if cpu_n == 1:
            try:
                # 评估策略
                _, metrics = evaluate_single_strategy(
                    market_df=market_df0,
                    precomputed_data=precomputed_data,
                    backtest_config=backtest_config,
                    decoded_params=decoded_params,
                )

                all_metrics.append(metrics)

                if show_progress:
                    pbar.update(1)
                    pbar.set_postfix({"收益率": f"{metrics.get('total+总收益率%', 0):.2f}%"})

            except Exception as e:
                logger.warning(f"策略回测失败: {filters_combo}&{signals_combo}&{exits_combo} - {e}")
                if show_progress:
                    pbar.update(1)
        else:

            p00 = Pool(processes=cpu_n)

            worker_func = partial(evaluate_single_strategy,
                                  market_df0,
                                  precomputed_data,
                                  backtest_config,
                                  )

            # 多进程并行计算
            for decoded_params in all_param_list:
                p00.apply_async(worker_func, args=(decoded_params,),
                                callback=lambda v: all_metrics.append(v[-1]),
                                error_callback=lambda e: logger.error(f"Error occurred: {e}", exc_info=True), )

            p00.close()
            p00.join()

        if show_progress:
            pbar.close()
        # 转换为 DataFrame 并排序
        results_df = pd.DataFrame(all_metrics)
        if not results_df.empty:
            results_df = results_df.sort_values('total+总收益率%', ascending=False).reset_index(drop=True)
            logger.info(f"批量回测完成！成功回测 {len(all_metrics)} 个策略")
            logger.info(
                f"最佳策略: {results_df.iloc[0]['策略名称']} (收益率: {results_df.iloc[0]['total+总收益率%']:.2f}%)")

        return results_df, all_metrics

if __name__ == "__main__":
    if 0:  # 原始测试
        frequency = "15min"
        MK_DATA_PATHS = {
            "GCmain": rf"D:\贵金属_data\comex_{frequency}\comex_GCmain_{frequency}.csv",
            "SImain": rf"D:\贵金属_data\comex_{frequency}\comex_SImain_{frequency}.csv",
            "CLmain": rf"D:\贵金属_data\comex_{frequency}\comex_CLmain_{frequency}.csv",
            "HGmain": rf"D:\贵金属_data\comex_{frequency}\comex_HGmain_{frequency}.csv",
            "ZSmain": rf"D:\贵金属_data\comex_{frequency}\comex_ZSmain_{frequency}.csv",
            "ZLmain": rf"D:\贵金属_data\comex_{frequency}\comex_ZLmain_{frequency}.csv",
            "ZMmain": rf"D:\贵金属_data\comex_{frequency}\comex_ZMmain_{frequency}.csv",
            "ZWmain": rf"D:\贵金属_data\comex_{frequency}\comex_ZWmain_{frequency}.csv",
            "ZRmain": rf"D:\贵金属_data\comex_{frequency}\comex_ZRmain_{frequency}.csv",
            "ZCmain": rf"D:\贵金属_data\comex_{frequency}\comex_ZCmain_{frequency}.csv",
        }
        df = pd.read_csv(
            rf"D:\jason_src\策略多因子系统\15min_全品种优化\backtest_result_data-f-2_s-3_e-2_jzmode-d_new\optimization_GCmain\raw_evaluation_cache.csv").tail(
            30)
        cl_names = df['策略名称'].tolist()
        decoded_params = cl_names
        # [
        #     "aroon_diff_higher0^21|emacd_higher_signal^89^178^89|aroon_diff_higher0^89&"
        #     "adx_plus_crossover_minus^34|tp_low_1^15^0|s_tp_low_1^15^0^2&"
        #     "trailing_stop^34^3.5|emacd_histogram_start_decrease^55^110^55",
        # ]
        # 回测默认配置
        BACKTEST_CONFIG = {
            "transaction_cost": 0.0005,  # 单边交易成本（万三）
            "direction_long": True,  # 做多方向
            "ignore_new_entry": True,  # 持仓时不更新出场条件
            "resample_rule": "",  # 重采样规则（空字符串表示不重采样）
            "rf": 0.00,
            "jz_mode": "d"  # 无风险利率
        }
        (combo_name, market_df0, market_jz), metrics = run_strategy_single(
            code_id="GCmain",
            start=datetime(2026, 2, 1),
            end=datetime(2026, 6, 18),
            market_data_paths=MK_DATA_PATHS,
            decoded_params=decoded_params,
            backtest_config=BACKTEST_CONFIG,
        )

        logger.info(f"策略组合: {combo_name}\n{metrics}")

        logger.info(f"\n{pd.DataFrame(metrics)}")
        print(market_df0.keys())

        all_ms = []
        for clname in combo_name:
            cum_curve, all_metrics = compute_backtest_metrics_with_jz(
                market_df=market_df0[['datetime', 'open', 'high', 'low', 'close', 'volume', clname]],
                position_series=market_df0[clname],
                combo_name=combo_name,
                transaction_cost=0.0005,
                rf=0.00,
                jz_mode="d",
                resample_rule="",
                direction_long=1,
            )
            all_ms.append(all_metrics)
            plt.plot(cum_curve)
        plt.plot(market_df0['close'] / market_df0['close'].iloc[0], 'r')
        print(pd.DataFrame(all_ms))
        plt.show()
        exit()

    if 1:  # 批量回测测试
        frequency = "15min"
        MK_DATA_PATHS = {
            "GCmain": rf"D:\贵金属_data\comex_{frequency}\comex_GCmain_{frequency}.csv",
            "SImain": rf"D:\贵金属_data\comex_{frequency}\comex_SImain_{frequency}.csv",
            "CLmain": rf"D:\贵金属_data\comex_{frequency}\comex_CLmain_{frequency}.csv",
        }

        # 回测配置
        BACKTEST_CONFIG = {
            "transaction_cost": 0.0005,
            "direction_long": True,
            "ignore_new_entry": True,
            "resample_rule": "",
            "rf": 0.00,
            "jz_mode": "d"
        }

        # 定义可选的过滤器、信号、退出
        FILTERS = [
            'roc_higher0^18', 'roc_higher0^16', 'aroon_diff_higher0^16', 'aroon_diff_higher0^25',
            'roc_higher0^38', 'roc_higher0^26', 'aroon_diff_higher0^56', 'aroon_diff_higher0^35',
            'price_higher_sma^10', 'aroon_diff_higher0^45', 'price_higher_sma^50',
            'price_higher_sma^40', 'aroon_diff_higher0^75', 'price_higher_sma^70',
        ]

        SIGNALS = [
            'stoch_k_crossover_d_2^240^168^72^15', 'stoch_k_crossover_d_2^210^147^105^15',
            'bb_price_crossover_low_2^55.0^1.9',
            'bb_price_crossover_high_2^25.0^3.8',
            'bb_price_crossover_high_2^25.0^2.8',
            'bb_price_crossover_high^25.0^3.8', 'sma_fast_crossover_slow_3^130^234', 'aroon_diff_crossover0^90',
        ]

        EXITS = [
            'smi_k_crossover0^210^105^EMA', 'stoch_k_crossover_d^40^55^55',
            'smacd_histogram_start_increase_2^70^442^119', 'stoch_k_crossover_d^110^55^55',
            'smacd_histogram_start_increase_2^170^442^119',
        ]

        # 选择数量
        SELECT_COUNTS = {
            "filters": 3,
            "signals": 6,
            "exits": 2
        }

        # 加载市场数据
        code_id = "GCmain"
        logger.info(f"正在加载 {code_id} 市场数据...")
        market_df_full = load_market_data(
            code_id=code_id,
            start=datetime(2026, 2, 1),
            end=datetime(2026, 6, 18),
            market_data_paths=MK_DATA_PATHS
        )

        # 收集所有信号
        all_signals = {
            "filters": FILTERS,
            "signals": SIGNALS,
            "exits": EXITS
        }

        # 预计算所有信号
        logger.info("正在预计算所有信号...")
        precomputed_data_full = {
            "filters": precompute_all_signals(market_df_full, all_signals["filters"], "filter", "and",
                                              show_progress=True),
            "signals": precompute_all_signals(market_df_full, all_signals["signals"], "entry", "or",
                                              show_progress=True),
            "exits": precompute_all_signals(market_df_full, all_signals["exits"], "exit", "or", show_progress=True)
        }

        # 过滤到目标回测时间段
        start = datetime(2026, 2, 1)
        end = datetime(2026, 6, 18)
        period_cond = (market_df_full["datetime"] >= start) & (market_df_full["datetime"] <= end)
        market_df = market_df_full[period_cond].reset_index(drop=True)
        period_cond_np = period_cond.values
        precomputed_data = {
            "filters": {name: array[period_cond_np] for name, array in precomputed_data_full["filters"].items()},
            "signals": {name: array[period_cond_np] for name, array in precomputed_data_full["signals"].items()},
            "exits": {name: array[period_cond_np] for name, array in precomputed_data_full["exits"].items()},
        }

        # 批量回测
        results_df, all_metrics = run_batch_single_stg(
            market_df=market_df,
            precomputed_data=precomputed_data,
            filters=FILTERS,
            signals=SIGNALS,
            exits=EXITS,
            backtest_config=BACKTEST_CONFIG,
            select_counts=SELECT_COUNTS,
            show_progress=True,
            cpu_n=10

        )

        # 显示结果
        logger.info("\n=== 批量回测结果 ===")
        print(results_df.head(10))
        results_df = results_df.iloc[-10:]
        # 绘制最佳策略净值曲线
        if not results_df.empty:
            for i in range(len(results_df)):
                best_strategy_name = results_df.iloc[i]['策略名称']
                logger.info(f"\n最佳策略: {best_strategy_name}")

                # 重新运行最佳策略以获取净值数据
                EntryFilters, EntrySignals, ExitSignals = best_strategy_name.split('&')
                EntryFilters = [i for i in EntryFilters.split('|')]
                EntrySignals = [i for i in EntrySignals.split('|')]
                ExitSignals = [i for i in ExitSignals.split('|')]

                (combo_name, market_df0, market_jz), metrics = run_strategy_single(
                    code_id=code_id,
                    start=start,
                    end=end,
                    market_data_paths=MK_DATA_PATHS,
                    decoded_params=[
                        {"EntryFilters": EntryFilters, "EntrySignals": EntrySignals, "ExitSignals": ExitSignals}],
                    backtest_config=BACKTEST_CONFIG,
                    show_progress=False,
                )

                plt.plot(market_jz[best_strategy_name], label='best_strategy_name')

            plt.plot(market_jz['close'] / market_jz['close'].iloc[0], label='基准净值', color='black')
            plt.xticks(market_jz.index[::100], market_jz["datetime"].iloc[::100], rotation=45)
            plt.xlabel('时间')
            plt.ylabel('净值')
            plt.title(f'最佳策略净值曲线 - {best_strategy_name}')
            plt.legend()
            # plt.grid(True)
            plt.show()

        exit()