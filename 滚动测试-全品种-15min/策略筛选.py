"""
策略筛选脚本 - 三阶段流程
1. 多维度筛选：从回测结果中筛选高质量策略
2. 单策略回测：对筛选出的策略进行逐个回测
3. 低相关性筛选：选择低相关性的策略组合
"""

import pandas as pd
import numpy as np
import json
import os
import sys
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
from loguru import logger
import matplotlib
import matplotlib.pyplot as plt
# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from 优化回测 import run_strategy_single, compute_backtest_metrics_with_jz

# matplotlib.use('Agg')
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 中文字体
matplotlib.rcParams['axes.unicode_minus'] = False    # 负号显示

# 配置 loguru 日志系统
logger.remove()  # 移除默认处理器
logger.add(
    sys.stderr,  # 输出到标准错误
    level="INFO",  # 日志级别
)


def metrics_from_jz(
        jz_series,
        time_series=None,
        strategy_name: str = "",
        rf: float | int = 0.00,
        time_start: pd.Timestamp = None,
        annual_days: int = 365,
) -> Dict[str, float]:
    """
    从累计净值曲线直接计算统计指标（无需 position 信息）

    与 basic_metrics 的区别：
        - 输入已是累计净值（jz_series），不再从 pos+open+close 推导
        - 因此无法计算依赖持仓的指标：交易次数/交易胜率/盈亏比/均持天数/总交易成本
        - 其余收益、风险、回撤、sharpe/sortino/calmar、bar胜率 均可计算

    Args:
        jz_series: 累计净值曲线（起始约为 1.0）。可为 pd.Series / list / np.ndarray
        time_series: 对应时间序列。
                     - 为 None 时，使用 jz_series 的 index（要求是 DatetimeIndex）
                     - 否则按位置与 jz_series 一一对应
        strategy_name: 策略名称
        rf: 无风险收益率（年化，例如 0.02 为百二）
        time_start: 子周期起始时间，决定输出 key 的前缀
                    - None  -> 前缀 "total+"
                    - 否则  -> 前缀 "{time_start:%Y-%m-%d}+"
        annual_days: 年化天数（默认 365）

    Returns:
        Dict[str, float]: 统计指标字典（格式与 basic_metrics 对齐）
    """
    # ---- 标准化输入 ----
    jz = pd.Series(jz_series, dtype="float64").reset_index(drop=True)
    if jz.isna().all() or len(jz) < 2:
        raise ValueError(f"jz_series 数据不足或全为 NaN，长度: {len(jz)}")

    if time_series is None:
        if isinstance(jz_series, pd.Series) and isinstance(jz_series.index, pd.DatetimeIndex):
            time_ser = pd.Series(jz_series.index)
        else:
            raise ValueError("time_series 为空，且 jz_series.index 不是 DatetimeIndex，无法推断时间")
    else:
        time_ser = pd.Series(time_series).reset_index(drop=True)

    # 期间总秒数 / 单步平均天数
    total_seconds = (pd.Timestamp(time_ser.iloc[-1]) - pd.Timestamp(time_ser.iloc[0])).total_seconds()
    count_days = total_seconds / (24 * 3600)
    delta_inv = (time_ser.diff().dropna().map(lambda x: x.total_seconds()).mean()) / (24 * 3600)
    if not np.isfinite(delta_inv) or delta_inv <= 0:
        delta_inv = 1.0  # 退化情况：按 1 步 = 1 天

    # ---- 收益 / 波动 ----
    per_jz = jz.pct_change().fillna(0)
    total_returns = jz.iloc[-1] - 1

    if total_returns >= 0:
        annualized_returns = (1 + total_returns) ** (annual_days / count_days) - 1
    else:
        annualized_returns = -((1 - total_returns) ** (annual_days / count_days) - 1)

    daily_std = np.nanstd(per_jz) * np.sqrt(1 / delta_inv)
    annualized_std = daily_std * (annual_days ** 0.5)

    # ---- 最大回撤 ----
    running_max = jz.cummax()
    drawdown = (running_max - jz) / running_max
    max_drawdown = drawdown.max()

    # ---- 风险调整收益 ----
    sharpe = (annualized_returns - rf) / annualized_std if annualized_std != 0 else 0.0

    negative_returns = per_jz[per_jz < 0]
    if len(negative_returns) == 0:
        sortino = 100.0
    else:
        year_downside_std = np.std(negative_returns) * np.sqrt(1 / delta_inv) * (annual_days ** 0.5)
        sortino = (annualized_returns - rf) / year_downside_std if year_downside_std != 0 else 0.0

    calmar = annualized_returns / max_drawdown if max_drawdown != 0 else 0.0

    # bar 胜率（净值视角：正收益 bar 占比）
    total_bars = len(per_jz)
    bar_win_rate = (per_jz > 0).sum() / total_bars if total_bars > 0 else 0.0

    metrics = {
        "总收益率%": float(round(total_returns * 100, 3)),
        "年化收益率%": float(round(annualized_returns * 100, 3)),
        "最大回撤%": float(round(max_drawdown * 100, 3)),
        "sharpe比率": float(round(sharpe, 3)),
        "sortino比率": float(round(sortino, 3)),
        "calmar比率": float(round(calmar, 3)),
        "年化波动率%": float(round(annualized_std * 100, 3)),
        "日波动率%": float(round(daily_std * 100, 3)),
        "bar胜率%": float(round(bar_win_rate * 100, 3)),
    }

    time_start = 'alltime' if time_start is None else f"{time_start:%Y-%m-%d}"
    metrics = {f"{k}": v for k, v in metrics.items()}
    metrics = {
        **{
            "標記": time_start,
            "策略名称": strategy_name,

        },
        **metrics,
        **{"days":count_days,
            "开始时间": pd.Timestamp(time_ser.iloc[0]).strftime("%Y-%m-%d"),
            "结束时间": pd.Timestamp(time_ser.iloc[-1]).strftime("%Y-%m-%d"),}
    }


    return metrics


# ==================== 第一阶段：策略筛选 ====================

def load_and_prepare_data(file_path: str) -> pd.DataFrame:
    """加载并准备数据"""
    logger.info(f"加载数据: {file_path}")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")

    df = pd.read_csv(file_path)
    logger.info(f"加载完成，共 {len(df)} 行数据")
    return df


def get_strategy_column(df: pd.DataFrame) -> str:
    """获取策略名称列名"""
    for col in ['策略名称', 'strategy_name', 'StrategyName']:
        if col in df.columns:
            return col
    raise ValueError(f"找不到策略名称列，数据列: {list(df.columns)}")


def calculate_rank_score(series: pd.Series, direction: str) -> pd.Series:
    """计算排名分数（0-100）"""
    n = len(series)
    if n <= 1:
        return pd.Series([50] * n, index=series.index)

    if direction == 'positive':
        ranks = series.rank(ascending=True, method='average')
    else:
        ranks = series.rank(ascending=False, method='average')

    scores = (ranks - 1) / (n - 1) * 100
    return scores


def calculate_composite_score(df: pd.DataFrame, metrics_config: Dict) -> pd.DataFrame:
    """计算综合得分"""
    df = df.copy()

    # 计算各项指标的排名分数
    for col, (direction, _) in metrics_config.items():
        if col in df.columns:
            df[f'{col}_score'] = calculate_rank_score(df[col], direction)

    # 获取可用的指标
    available_cols = [col for col in metrics_config.keys() if col in df.columns]

    if not available_cols:
        raise ValueError("数据中未找到任何配置的指标列")

    # 计算综合得分
    score_cols = [f'{col}_score' for col in available_cols]
    weights = [metrics_config[col][1] for col in available_cols]
    weights_array = np.array(weights) / sum(weights)

    df['composite_score'] = df[score_cols].mul(weights_array, axis=1).sum(axis=1)

    return df


def screen_by_metric(df: pd.DataFrame, metric_col: str, direction: str, pct: float) -> set:
    """
    按单个指标筛选策略

    Args:
        df: 数据DataFrame
        metric_col: 指标列名
        direction: 'positive'=前pct, 'negative'=后pct
        pct: 筛选比例

    Returns:
        策略名称集合
    """
    if metric_col not in df.columns:
        logger.warning(f"指标 {metric_col} 不在数据中，跳过")
        return set()

    n = len(df)
    cutoff = int(n * pct)

    if direction == 'positive':
        # 取前pct%
        selected = df.nlargest(cutoff, metric_col)
    else:
        # 取后pct%（值最小的）
        selected = df.nsmallest(cutoff, metric_col)

    return set(selected['strategy_name'])


def multi_dimension_screening(df: pd.DataFrame,
                                metrics_config: Dict,
                                pct: float) -> set:
    """
    多维度筛选策略

    Returns:
        筛选出的策略名称集合
    """
    logger.info(f"\n开始多维度筛选，各维度取 {pct*100}%")

    all_selected = set()

    for metric_col, (direction, _) in metrics_config.items():
        if metric_col in df.columns:
            selected = screen_by_metric(df, metric_col, direction, pct)
            all_selected.update(selected)
            logger.info(f"  {metric_col}: 筛选出 {len(selected)} 个策略")

    logger.info(f"汇总去重后: {len(all_selected)} 个策略")
    return all_selected


def force_filter_strategies(df: pd.DataFrame,
                              force_config: Dict,
                              force_n: int) -> Tuple[pd.DataFrame, Dict]:
    """
    强制过滤：根据Force_CONFIG中的严格阈值筛选策略

    Args:
        df: 原始数据DataFrame
        force_config: 强制过滤配置 {指标名: (方向, 最小阈值)}
        force_n: 数量阈值，满足时提前跳出

    Returns:
        (过滤后的DataFrame, 过滤统计信息)
    """
    logger.info("\n" + "="*100)
    logger.info("强制过滤阶段")
    logger.info("="*100)

    df_original = df.copy()

    # 1. 先去重
    df_clean = df_original.drop_duplicates(subset=[list(force_config.keys())[0]])
    logger.info(f"去重前: {len(df_original)} 行, 去重后: {len(df_clean)} 行")

    # 2. 构建过滤条件（使用原始数据）
    condition = pd.Series([True] * len(df_clean), index=df_clean.index)

    for metric_col, (direction, threshold) in force_config.items():
        if metric_col not in df_clean.columns:
            logger.warning(f"指标 {metric_col} 不在数据中，跳过")
            continue


        if direction == 'positive':
            if threshold < 0:
                condition &= df_clean[metric_col] >= df_clean[metric_col].quantile(abs(threshold))
            if threshold > 0:
                condition &= df_clean[metric_col] >= threshold
        else:
            if threshold < 0:
                condition &= df_clean[metric_col] <= df_clean[metric_col].quantile(abs(threshold))
            if threshold > 0:
                condition &= df_clean[metric_col] <= threshold

        # 合并条件
        condition &= condition
        if df_clean[condition].shape[0] <= force_n:
            logger.warning(f"数量满足：{force_n}，跳出")
            break

    # 3. 应用过滤条件
    df_filtered = df_clean[condition].copy()
    logger.info(f"\n强制过滤完成: {len(df_original)} -> {len(df_filtered)} 个策略")

    return df_filtered


def filter_by_count_and_score(df: pd.DataFrame,
                                selected_set: set,
                                limit_n: int) -> pd.DataFrame:
    """
    按数量和得分筛选

    Args:
        df: 原始数据
        selected_set: 筛选出的策略集合
        limit_n: 最终数量限制

    Returns:
        筛选后的DataFrame
    """
    # 筛选出的策略
    filtered_df = df[df['strategy_name'].isin(selected_set)].copy()

    # 按综合得分排序
    filtered_df = filtered_df.sort_values('composite_score', ascending=1)

    # 取前limit_n个
    result = filtered_df.tail(limit_n)

    logger.info(f"按综合得分排序，取前 {limit_n} 个策略")
    logger.info(f"最终筛选出 {len(result)} 个策略")
    logger.info(f"最终筛选出\n {result.tail()}")

    return result


def stage1_strategy_screening(file_path: str,
                              SYMBOL_CODE: str,
                              metrics_config: Dict,
                              force_config: Dict,
                              pct_n: float,
                              force_n: int,
                              limit_n: int,
                              low_corr_n: int) -> pd.DataFrame:
    """
    第一阶段：策略筛选

    Args:
        file_path: 数据文件路径
        SYMBOL_CODE: 品种代码
        metrics_config: 指标权重配置
        force_config: 强制过滤配置
        pct_n: 多维度筛选比例
        force_n: 强制过滤数量阈值
        limit_n: 综合得分取前N个
        low_corr_n: 低相关性策略目标数量

    Returns:
        筛选后的策略DataFrame
    """
    logger.info("\n" + "="*100)
    logger.info("第一阶段：策略筛选")
    logger.info("="*100)

    # 1. 加载数据
    df = load_and_prepare_data(file_path)
    if len(df) == 0:
        logger.warning("数据为空，返回空DataFrame")
        df = pd.read_csv(os.path.join(os.path.dirname(file_path),rf'{SYMBOL_CODE}_pareto_metrics.csv'))

    if len(df) == 0:
        raise ValueError("数据为空")
        return {}

    # 获取策略名称列
    strategy_col = get_strategy_column(df)

    df = df.rename(columns={strategy_col: 'strategy_name'})

    # 1.5 强制过滤
    df = force_filter_strategies(df, force_config, force_n)
    if len(df) >= force_n:
        df = df.sort_values('total+总收益率%', ascending=1)
        df = df.iloc[-500:]
    if len(df) == 0:
        logger.warning("强制过滤后无策略剩余，返回空DataFrame")
        return pd.DataFrame()

    if True:
        cl_names = df['strategy_name'].tolist()
        cl_names = set(cl_names)
        cl_name_factor = [
            {'name': 'EntryFilters', 'select_count': "n1", 'combination': 'and',
             'items': []},
            {'name': 'EntrySignals', 'select_count': "n2", 'combination': 'or',
             'items': []},
            {'name': 'ExitSignals', 'select_count': "n3", 'combination': 'or',
             'items': []}
        ]

        f_set = set()
        s_set = set()
        e_set = set()
        for cl0 in cl_names:
            f, ins, outs = cl0.split("&")
            f = f.split("|")
            ins = ins.split("|")
            outs = outs.split("|")
            for f0 in f:
                f_set.add(f0)
            for ins0 in ins:
                s_set.add(ins0)
            for outs0 in outs:
                e_set.add(outs0)

        cl_name_factor[0]['items'].extend(f_set)
        cl_name_factor[1]['items'].extend(s_set)
        cl_name_factor[2]['items'].extend(e_set)

        # print(cl_name_factor)
        cl_cfg_factor = {SYMBOL_CODE: cl_name_factor}

        json_path = file_path.replace(".csv", f'_force_filtered.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(cl_cfg_factor, f, ensure_ascii=False, indent=2)

        # exit()


    if len(df) <= low_corr_n:
        logger.info(f"策略数量不足 {low_corr_n}，返回")
        return df


    df.to_csv(file_path.replace('.csv', '_force_filtered.csv'), index=False,mode = 'w')
    # 2. 计算综合得分
    logger.info("\n计算综合得分...")
    df = calculate_composite_score(df, metrics_config)

    # 3. 多维度筛选
    selected_set = multi_dimension_screening(df, metrics_config, pct_n)

    # 4. 数量限制
    result = filter_by_count_and_score(df, selected_set, limit_n)


    return result


# ==================== 第二阶段：单策略回测 ====================

def stage2_single_backtest(strategies: List[str],
                           code_id: str,
                           start_date: datetime,
                           end_date: datetime,
                           backtest_config: dict) -> Dict[str, dict]:
    """
    第二阶段：单个策略回测

    Args:
        strategies: 策略名称列表
        code_id: 品种代码
        start_date: 开始日期
        end_date: 结束日期
        backtest_config: 回测配置

    Returns:
        {策略名: {equity_curve, positions, metrics}}
    """
    logger.info("\n" + "="*100)
    logger.info("第二阶段：单个策略回测")
    logger.info("="*100)

    try:

        # 市场数据路径配置
        MK_DATA_PATHS = backtest_config.get("mk_data_paths", {})

    except ImportError as e:
        logger.error(f"导入回测模块失败: {e}")
        logger.info("请确保优化回测模块可用，或者使用模拟回测")
        return simulate_backtest(strategies)

    results = {}
    met_results = {}
    total = len(strategies)

    try:
        logger.info(f"开始批量回测，策略数量: {total}")

        # 直接传入策略列表进行回测
        (all_stg_names, df_pos,df_jz), all_metrics = run_strategy_single(
                        code_id=code_id,
                        start=start_date,
                        end=end_date,
                        market_data_paths=MK_DATA_PATHS,
                        decoded_params=strategies,  # 直接传入整个列表
                        backtest_config=backtest_config,
                    )

        # 处理回测结果 - 提取每个策略的净值曲线、持仓和指标
        logger.info(f"回测完成，共 {len(all_stg_names)} 个策略")
        logger.info(f"\n{pd.DataFrame(all_metrics).tail()}")
        # logger.info(f"\n{market_df0.tail()}")

        # market_df0_out = market_df0[['datetime', 'open', 'high', 'low', 'close', 'volume']]
        # for idx, strategy_name in enumerate(all_stg_names):
        #     if strategy_name not in market_df0.columns:
        #         logger.warning(f"策略 {strategy_name} 不在市场数据中，跳过")
        #         continue
        #
        #     # 重新计算净值曲线
        #     btdf = market_df0[['datetime', 'open', 'high', 'low', 'close', 'volume', strategy_name]].copy()
        #     equity_curve, metrics = compute_backtest_metrics_with_jz(
        #         market_df=btdf,
        #         position_series=market_df0[strategy_name].copy(),
        #         combo_name=strategy_name,
        #         transaction_cost=backtest_config.get("transaction_cost", 0.0005),
        #         rf=backtest_config.get("rf", 0.00),
        #         jz_mode=backtest_config.get("jz_mode", "d"),
        #         resample_rule=backtest_config.get("resample_rule", "")
        #     )
        #     btdf['equity_curve'] = equity_curve
        #     btdf['positions'] = btdf[strategy_name].copy()
        #     btdf[['datetime', 'open', 'high', 'low', 'close', 'volume', 'positions','equity_curve']].copy()


            # 提取指标

        results={'df_jz':df_jz,'df_pos':df_pos, 'metrics':all_metrics}

    except Exception as e:
        logger.error(f"批量回测失败: {e}")
        import traceback
        traceback.print_exc()
        raise e
        # logger.info("尝试使用模拟回测模式")
        # return simulate_backtest(strategies)

    logger.info(f"回测完成，成功回测 {len(results)}/{total} 个策略")

    return results


def simulate_backtest(strategies: List[str]) -> Dict[str, dict]:
    """
    模拟回测（用于测试）

    Args:
        strategies: 策略列表

    Returns:
        模拟的回测结果
    """
    logger.warning("使用模拟回测模式")

    results = {}
    np.random.seed(42)

    for strategy_name in strategies:
        # 生成模拟净值曲线
        n_points = 100
        returns = np.random.normal(0.001, 0.02, n_points)
        equity_curve = (1 + pd.Series(returns)).cumprod() * 100000

        # 生成模拟持仓
        positions = np.random.randint(-1, 2, n_points)

        results[strategy_name] = {
            'equity_curve': equity_curve.tolist(),
            'positions': positions.tolist(),
            'metrics': {
                '总收益率': f"{(equity_curve.iloc[-1] / equity_curve.iloc[0] - 1) * 100:.2f}",
                '胜率': f"{np.random.randint(40, 70)}",
                '最大回撤': f"{np.random.uniform(3, 15):.2f}"
            }
        }

    return results

# ==================== 第三阶段：低相关性筛选 ====================

def calculate_correlation_matrix(results: Dict[str, dict],corr_mode='positions') -> pd.DataFrame:
    """
    计算策略间相关性矩阵

    Args:
        results: 回测结果字典
        corr_mode: 相关性计算模式 ('positions' 或 'equity_curve')

    Returns:
        相关性矩阵DataFrame
    """
    logger.info("\n计算策略间相关性矩阵...")

    # 提取数据序列
    equity_curves = {}
    min_length = float('inf')
    skipped = 0

    for strategy_name, data in results.items():
        if corr_mode not in data:
            logger.warning(f"策略 {strategy_name} 没有 {corr_mode} 数据，跳过")
            skipped += 1
            continue

        equity = np.array(data[corr_mode])

        # 检查数据有效性
        if len(equity) <= 1:
            logger.warning(f"策略 {strategy_name} 的 {corr_mode} 数据长度不足 ({len(equity)})，跳过")
            skipped += 1
            continue

        if np.all(equity == equity[0]):
            logger.warning(f"策略 {strategy_name} 的 {corr_mode} 数据全相同，跳过")
            skipped += 1
            continue

        # 转换为收益率
        returns = pd.Series(equity).pct_change().dropna()
        if len(returns) >= 2 and not returns.isna().all():
            equity_curves[strategy_name] = returns
            min_length = min(min_length, len(returns))
        else:
            skipped += 1

    logger.info(f"有效策略数: {len(equity_curves)}, 跳过: {skipped}, 最短序列长度: {min_length}")

    if len(equity_curves) < 2:
        raise ValueError(f"有效策略数不足 ({len(equity_curves)})，无法计算相关性，至少需要2个策略")

    # 对齐序列长度
    aligned_data = {}
    for name, returns in equity_curves.items():
        aligned_data[name] = returns.tail(min_length).values

    # 构建DataFrame并计算相关性
    df_returns = pd.DataFrame(aligned_data)

    # 检查是否有 NaN 或 Inf
    if df_returns.isna().any().any() or np.isinf(df_returns.values).any():
        logger.warning("数据中存在 NaN 或 Inf，尝试清理")
        df_returns = df_returns.fillna(0).replace([np.inf, -np.inf], 0)

    corr_matrix = df_returns.corr()

    # 检查相关性矩阵是否有效
    if corr_matrix.isna().all().all():
        logger.error("相关性矩阵全为 NaN")
        logger.debug(f"df_returns 统计:\n{df_returns.describe()}")
        raise ValueError("相关性矩阵计算失败，结果全为 NaN")

    logger.info(f"相关性矩阵计算完成，形状: {corr_matrix.shape}")
    return corr_matrix


def select_low_correlation_strategies(corr_matrix: pd.DataFrame,
                                     n: int,
                                     threshold: float) -> List[str]:
    """
    选择低相关性策略组合

    Args:
        corr_matrix: 相关性矩阵
        n: 目标策略数量
        threshold: 相关性阈值

    Returns:
        选择的策略名称列表
    """
    logger.info(f"\n选择 {n} 个低相关性策略（相关系数阈值 < {threshold}）")

    strategies = list(corr_matrix.index)
    if len(strategies) <= n:
        logger.info(f"策略总数 {len(strategies)} 少于目标数量 {n}，返回全部策略")
        return strategies
    for i in range(5):
        # 使用贪心算法选择低相关性组合
        selected = []
        available = strategies.copy()

        # 首先选择平均相关性最低的策略作为起点
        avg_corr = corr_matrix.mean(axis=1)

        # 检查 avg_corr 是否有效
        if avg_corr.isna().all():
            logger.warning("相关性矩阵全为 NaN，改用随机选择起点")
            first_strategy = strategies[0] if strategies else None
        else:
            first_strategy = avg_corr.idxmin()

        if first_strategy is None or first_strategy not in available:
            logger.warning(f"起点策略 {first_strategy} 无效，使用第一个策略")
            first_strategy = strategies[0] if strategies else None

        if first_strategy:
            selected.append(first_strategy)
            if first_strategy in available:
                available.remove(first_strategy)

        # 贪心选择
        while len(selected) < n and available:
            best_candidate = None
            best_max_corr = float('inf')

            for candidate in available:
                # 计算与已选策略的最大相关性
                max_corr_with_selected = max([
                    abs(corr_matrix.loc[candidate, s])
                    for s in selected
                ])

                # 如果与所有已选策略的相关性都低于阈值，优先选择
                if max_corr_with_selected < threshold:
                    if max_corr_with_selected < best_max_corr:
                        best_max_corr = max_corr_with_selected
                        best_candidate = candidate
                # 如果没有满足阈值的，选择相关性最低的
                elif best_candidate is None:
                    if max_corr_with_selected < best_max_corr:
                        best_max_corr = max_corr_with_selected
                        best_candidate = candidate

            if best_candidate:
                selected.append(best_candidate)
                available.remove(best_candidate)
                # logger.info(f"  选择第 {len(selected)} 个策略: {best_candidate}, "
                #            f"最大相关性: {best_max_corr:.4f}")
            else:
                logger.warning(f"无法找到满足条件的策略，当前已选 {len(selected)} 个")
                break

        logger.info(f"最终选择了 {len(selected)} 个策略")
        if len(selected) > 0:
            break
        else:
            threshold += 0.05

    return selected


# ==================== 主流程 ====================
def plot_equity_curves(df_jz, symbol_code, result_dir, all_result_dir=None,
                       start_time=None, end_time=None):

    config = {
        'figsize': (18, 12),
        'linewidth_strategy': 0.8,
        'linewidth_benchmark': 1.5,
        'xtick_interval': 200,
        'grid_alpha': 0.3,
        'benchmark_color': 'red',
        'vline_start_color': 'green',
        'vline_end_color': 'purple',
    }

    # 筛选策略列（包含 "|" 的列名）
    strategy_cols = [col for col in df_jz.columns if ( "|" in col) & ( "&" in col)]

    if not strategy_cols and 'close' not in df_jz.columns:
        logger.warning(f"没有可绘制的数据: {symbol_code}")
        return

    # 创建图表
    fig, axs = plt.subplots(3,1,height_ratios=[1,0.5,0.5],figsize=config['figsize'])
    ax,ax2,ax3 = axs

    # 绘制各策略曲线
    for col in strategy_cols:
        ax.plot(df_jz[col], label=col, linewidth=config['linewidth_strategy'])

    df_jz['meanjz'] = df_jz[strategy_cols].mean(axis=1)
    df_jz['meanjz'] = df_jz['meanjz']/df_jz['meanjz'].iloc[0]
    res = metrics_from_jz(
        df_jz['meanjz'],
        time_series=df_jz['datetime'],
        strategy_name = "meanjz",
        time_start = None,
        annual_days = 365
        )
    # 去掉 "total+" / "{date}+" 前缀，让所有行共享同一组列名
    res = {k.split('+', 1)[1] if '+' in k else k: v for k, v in res.items()}
    res = {"標記": "alltime", **res}
    res_jz = [res]
    for st,df00 in df_jz.resample('1MS',on='datetime'):
        df00 = df00.reset_index(drop=True).copy()
        df00['meanjz'] = df00['meanjz']/df00['meanjz'].iloc[0]
        res = metrics_from_jz(
            df00['meanjz'],
            time_series=df00['datetime'],
            strategy_name="meanjz",
            time_start=st,
            annual_days=365
        )
        res = {k.split('+', 1)[1] if '+' in k else k: v for k, v in res.items()}
        res = {"標記": st.strftime("%Y-%m-%d"), **res}
        res_jz.append(res)
    period_df = pd.DataFrame(res_jz)
    period_df_str = period_df.to_string()
    print(period_df_str)
    def signed_bars(ax, x, vals, cmap_pos='#4C9F70', cmap_neg='#D62828', base='#3D5A80'):
        vals = pd.Series(vals, dtype=float)
        x_tick_label = [i for i in range(0, len(x))]
        ax.set_xticks(x_tick_label)
        ax.set_xticklabels(x, ha='right')
        colors = [cmap_pos if v >= 0 else cmap_neg for v in vals]

        ax.bar(x_tick_label, vals, color=colors,width =0.5)
        ax.axhline(0, color='black', linewidth=0.6)
        return ax

    period_df = period_df.iloc[1:]
    ax2 = signed_bars(ax2, period_df['標記'].tolist(), period_df['总收益率%'].tolist(), cmap_pos='#4C9F70', cmap_neg='#D62828')
    ax3.text(0.1, 0.1, period_df_str, transform=ax3.transAxes,fontsize=12)
    # input()

    # 绘制基准线
    if 'close' in df_jz.columns:
        benchmark = df_jz['close'] / df_jz['close'].iloc[0]
        ax.plot(benchmark, label='基准收益',
                color=config['benchmark_color'],
                linewidth=config['linewidth_benchmark'])
        ax.plot(df_jz['meanjz'], label='策略平均收益',color='black', linewidth=1.5)

    # 绘制 start_time / end_time 分割竖线
    if 'datetime' in df_jz.columns:
        dt_series = pd.to_datetime(df_jz['datetime'], errors='coerce')
        for t, color, label in [
            (start_time, config['vline_start_color'], 'start_time'),
            (end_time,   config['vline_end_color'],   'end_time'),
        ]:
            if t is None:
                continue
            t_pd = pd.to_datetime(t, errors='coerce')
            if pd.isna(t_pd):
                logger.warning(f"{label} 无法解析为时间: {t}")
                continue
            pos = (dt_series - t_pd).abs().argmin()
            ax.axvline(pos, color=color, linestyle='--', linewidth=1.5, alpha=0.8,
                       label=f'{label}: {t_pd.strftime("%Y-%m-%d")}')

    # 设置标题和样式
    ax.set_title(f'{symbol_code} 选中策略净值曲线（归一化）', fontsize=16)
    ax.grid(True, alpha=config['grid_alpha'])
    ax.set_xlabel('时间', fontsize=12)

    # 设置 x 轴刻度
    xtick_indices = range(0, len(df_jz), config['xtick_interval'])
    xtick_labels = df_jz['datetime'].astype(str).str[:10].iloc[xtick_indices]

    ax.set_xticks(xtick_indices)
    ax.set_xticklabels(xtick_labels, rotation=90)

    # 调整布局防止标签被截断
    fig.tight_layout()

    # 保存图片
    fig_path = Path(result_dir) / f'{symbol_code}_equity_curves.png'
    try:
        fig.savefig(fig_path, dpi=100, bbox_inches='tight')
        logger.info(f"保存净值曲线图: {fig_path}")
    except Exception as e:
        logger.error(f"保存图片失败 {fig_path}: {e}")
    finally:
        plt.close(fig)

    # 复制到汇总目录
    if all_result_dir is not None:
        dest_path = Path(all_result_dir) / f'{symbol_code}_equity_curves.png'
        try:
            shutil.copy(fig_path, dest_path)
        except Exception as e:
            logger.warning(f"复制图片到汇总目录失败: {e}")

def save_final_results(strategies: List[str],
                       output_dir: str,
                       symbol_code: str,
                       df_metrics0: pd.DataFrame,
                       df_jz0: pd.DataFrame = None,
                       df_position0: pd.DataFrame = None,
                       all_result_dir: str = None,
                       pct_n: float = None,
                       limit_n: int = None,
                       low_corr_n: int = None,
                       limit_corr_val: float = None,
                       start_time=None,
                       end_time=None):
    """保存最终结果，包括JSON、CSV、持仓、净值曲线和图表"""
    # 创建汇总文件夹：选中策略情况
    result_dir = Path(output_dir) / '选中策略情况'
    result_dir.mkdir(parents=True, exist_ok=True)

    # 创建总结果文件夹
    if all_result_dir is not None:
        all_result_base = Path(all_result_dir)
        all_result_base.mkdir(parents=True, exist_ok=True)

    df_jz = df_jz0.copy()
    df_pos = df_position0.copy()
    df_metrics = df_metrics0.copy()
    # 1. 保存策略列表为JSON
    result = {
        symbol_code: {
            'strategies': strategies,
            'count': len(strategies),
            'selection_config': {
                'pct_n': pct_n,
                'limit_n': limit_n,
                'low_corr_n': low_corr_n,
                'limit_corr_val': limit_corr_val
            }
        }
    }

    json_path = result_dir / f'{symbol_code}_筛选策略.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    logger.info(f"\n保存筛选结果: {json_path}")
    # 复制到all_result文件夹
    if all_result_dir is not None:
        shutil.copy(json_path, Path(all_result_dir) / f'{symbol_code}_筛选策略.json')

    # 2. 保存metrics为CSV
    metrics_path = result_dir / f'{symbol_code}_筛选策略metrics.csv'
    df_metrics.to_csv(metrics_path, index=False, encoding='utf-8-sig')
    logger.info(f"保存策略metrics: {metrics_path}")
    # 复制到all_result文件夹
    if all_result_dir is not None:
        shutil.copy(metrics_path, Path(all_result_dir) / f'{symbol_code}_筛选策略metrics.csv')
    cols = ["coin_name", "inv0", "cl_name", "cl_canshu", "is_run", "cl_id", "cl_index"]
    df_metrics['coin_name'] = symbol_code
    df_metrics['inv0'] = '15min'
    df_metrics['cl_name'] = df_metrics['策略名称']
    df_metrics['cl_canshu'] = 0
    df_metrics['is_run'] = 1
    df_metrics['cl_id'] = df_metrics['策略名称']
    df_metrics['cl_index'] = df_metrics['策略名称']
    real_metrics_path = result_dir / f'{symbol_code}_实盘参数.csv'
    df_real_metrics = df_metrics[cols]

    df_real_metrics.to_csv(real_metrics_path, index=False, encoding='utf-8')
    # 复制到all_result文件夹
    if all_result_dir is not None:
        shutil.copy(real_metrics_path, Path(all_result_dir) / f'{symbol_code}_实盘参数.csv')

    if not df_pos.empty:
        pos_path = result_dir / f'{symbol_code}_all_position.csv'
        df_pos.to_csv(pos_path, index=False, encoding='utf-8-sig')
        logger.info(f"保存持仓数据: {pos_path}")
    # 3. 保存持仓数据和净值曲线（如果有回测结果）
    strategy_cols = [col for col in df_jz.columns if "|" in col]

    # df_jz['meanjz'] = df_jz[strategy_cols].mean(axis=1)  # 计算策略组合
    # res = metrics_from_jz(
    #     df_jz['meanjz'],
    #     time_series=df_jz['datetime'],
    #     strategy_name = "meanjz",
    #     time_start = None,
    #     annual_days = 365
    #     )
    # print(res)
    # input()

    if not df_jz.empty:
        # --- 净值收益图 ---
        plot_equity_curves(df_jz, symbol_code, result_dir, all_result_dir,
                           start_time=start_time, end_time=end_time)

        eq_path = result_dir / f'{symbol_code}_all_equity_curve.csv'
        df_jz.to_csv(eq_path, index=False, encoding='utf-8-sig')
        logger.info(f"保存净值曲线: {eq_path}")

        # 复制到all_result文件夹
        if all_result_dir is not None:
            shutil.copy(eq_path, Path(all_result_dir) / f'{symbol_code}_all_equity_curve.csv')



    # 打印结果
    logger.info(f"\n所有文件已保存到: {result_dir}")
    # logger.info("\n最终筛选的策略:")
    # for i, strategy in enumerate(strategies, 1):
    #     logger.info(f"  {i}. {strategy}")


def main(SYMBOL_CODE,BASE_DIR, METRICS_CONFIG, Force_CONFIG, PCT_N,
         Force_N, LIMIT_N, LOW_CORR_N, LIMIT_CORR_VAL,BACKTEST_CONFIG,
         start_time=None, end_time=None):
    """主函数"""
    # global METRICS_CONFIG, Force_CONFIG, PCT_N, Force_N, LIMIT_N, LOW_CORR_N, LIMIT_CORR_VAL,BACKTEST_CONFIG

    # 数据文件路径
    DATA_FILE = os.path.join(BASE_DIR, f'optimization_{SYMBOL_CODE}', 'raw_evaluation_cache.csv')
    # DATA_FILE = os.path.join(BASE_DIR, f'optimization_{SYMBOL_CODE}', f'{SYMBOL_CODE}_pareto_metrics.csv')
    OUTPUT_DIR = os.path.join(BASE_DIR, f'optimization_{SYMBOL_CODE}')
    corr_mode = 'equity_curve'  # 使用净值曲线计算相关性
    # ==================== 执行三阶段流程 ====================
    try:
        # 第一阶段：策略筛选
        logger.info(f"开始执行策略筛选{DATA_FILE}")
        screened_strategies_df = stage1_strategy_screening(
            DATA_FILE, SYMBOL_CODE,
            METRICS_CONFIG, Force_CONFIG, PCT_N, Force_N, LIMIT_N, LOW_CORR_N
        )
        strategy_list = screened_strategies_df['strategy_name'].tolist()

        # 第二阶段：单策略回测
        start_date = BACKTEST_CONFIG.get('start_date')
        end_date = BACKTEST_CONFIG.get('end_date')
        backtest_results = stage2_single_backtest(
                                        strategies=strategy_list,
                                        code_id=SYMBOL_CODE,
                                        start_date=start_date,
                                        end_date=end_date,
                                        backtest_config=BACKTEST_CONFIG  # 用户配置
                                    )
        df_jz_end = pd.DataFrame(backtest_results.get('df_jz'))
        df_pos_end = pd.DataFrame(backtest_results.get('df_pos'))
        df_metrics_end = pd.DataFrame(backtest_results.get('metrics'))

        # # 第三阶段：低相关性筛选
        # 计算相关性矩阵

        corr_matrix = df_jz_end[[i for i in df_jz_end.columns if "|" in i]].corr()
        # 选择低相关性策略
        selected_strategies = select_low_correlation_strategies(
            corr_matrix,
            LOW_CORR_N,
            LIMIT_CORR_VAL
        )

        logger.success(f"保存净值曲线图: \n{df_jz_end.tail()} \n")


        # 转换为DataFrame
        df_metrics = df_metrics_end[df_metrics_end['策略名称'].isin(selected_strategies)]

        # 保存结果
        ALL_RESULT_DIR = os.path.join(BASE_DIR, 'allresult')


        save_final_results(
            selected_strategies, OUTPUT_DIR, SYMBOL_CODE,
            df_metrics, df_jz_end, df_pos_end, ALL_RESULT_DIR,
            pct_n=PCT_N, limit_n=LIMIT_N,
            low_corr_n=LOW_CORR_N, limit_corr_val=LIMIT_CORR_VAL,
            start_time=start_time, end_time=end_time
        )

        # logger.info("\n" + "="*100)
        # logger.info("策略筛选完成！")
        # logger.info("="*100)
        # # logger.info(rf'{selected_strategies}')

    except Exception as e:
        logger.error(f"策略筛选失败: {e}")
        import traceback
        traceback.print_exc()

    return logger.info("策略筛选完成！")


if __name__ == '__main__':
    if True:
        frequency = "15min"
        # ==================== 配置区域 ====================
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
        # 回测配置（用户自行配置）
        START_DATE = datetime(2026, 2, 1)
        END_DATE = datetime(2026, 6, 20)


        # 回测默认配置
        BACKTEST_CONFIG = {
            "transaction_cost": 0.0005,  # 单边交易成本（万三）
            "direction_long": False,  # 做多方向
            "ignore_new_entry": True,  # 持仓时不更新出场条件
            "resample_rule": "",  # 重采样规则（空字符串表示不重采样）
            "rf": 0.00,
            "jz_mode": "d"  ,
            'mk_data_paths':MK_DATA_PATHS,
            'start_date': START_DATE,
            'end_date': END_DATE,
        }
    # ==================== 配置参数 ====================
    # 筛选参数
    PCT_N = 0.1  # 各维度筛选前/后10%
    Force_N = 200
    LIMIT_N = 80  # 最终数量限制500个
    LOW_CORR_N = 20  # 低相关性策略选50个
    LIMIT_CORR_VAL = 0.1  # 相关系数阈值0.5

    # 指标配置：列名 -> (方向, 权重)
    # 方向: 'positive'=越大越好, 'negative'=越小越好
    METRICS_CONFIG = {
        'total+总收益率%': ('positive', 5),
        'total+交易胜率%': ('positive', 2),
        'total+盈亏比': ('positive', 2),
        'total+sharpe比率': ('positive', 1.5),
        'total+calmar比率': ('positive', 2.5),
        # 'total+bar胜率%': ('positive', 1),
        # 'total+交易次数': ('positive', 0.5),
        'total+最大回撤%': ('negative', 4),
    }
    Force_CONFIG = {
        'total+总收益率%': ('positive', 10.5),      # 总收益率至少20%
        'total+交易次数': ('positive', 3),  # calmar至少0.5
        'total+calmar比率': ('positive', -0.5),  # calmar至少0.5
        # 'total+年化收益率%': ('positive', 20),      # 总收益率至少20%
        'total+交易胜率%': ('positive', 50),     # 交易胜率至少45%
        'total+盈亏比': ('positive', 1.85),       # 盈亏比至少1.5
        'total+sharpe比率': ('positive', 2.5),  # sharpe至少1.0
        'total+最大回撤%': ('negative', 10),     # 最大回撤不超过30%
    }

    # 数据路径配置
    BASE_DIRs = [

        # r'D:\nick01\stg_multi_factor_nick\15min_全品种优化_short\backtest_result_data-f-3_s-3_e-2_jzmode-d',
        # r'D:\nick01\stg_multi_factor_nick\15min_全品种优化_short\backtest_result_data-f-2_s-4_e-2_jzmode-d',
        r'D:\nick01\stg_multi_factor_nick\15min_全品种优化_short\backtest_result_data-f-4_s-2_e-2_jzmode-d',

    ]
    symbolist = ['GCmain']
    symbolist = [ 'CLmain','GCmain', 'SImain', 'HGmain', 'ZSmain', 'ZLmain', 'ZMmain', 'ZWmain', 'ZCmain'][:]

    # 净值曲线图上的分割竖线（可选；不画传 None）
    START_TIME = datetime(2026, 3, 1)
    END_TIME   = datetime(2026, 5, 1)

    for BASE_DIR in BASE_DIRs:
        for SYMBOL_CODE in symbolist:

            main(SYMBOL_CODE,BASE_DIR, METRICS_CONFIG, Force_CONFIG, PCT_N, Force_N, LIMIT_N, LOW_CORR_N, LIMIT_CORR_VAL,BACKTEST_CONFIG,
                 start_time=START_TIME, end_time=END_TIME)
