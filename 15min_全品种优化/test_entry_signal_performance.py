"""
Entry 信号点效果测试脚本 - 稳定性与样本外验证版本

核心逻辑：
1. 定义函数和变量取值范围
2. 读取数据，按月分割
3. 对每个参数组合计算：
   - 各窗口（20,40,60）的收益统计
   - 月度稳定性（变异系数）
   - 样本内外验证
4. 综合评分选出前10组参数
5. 输出格式：信号名称^参数1^参数2

作者: Auto-Generated
日期: 2026-06-15
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from datetime import datetime
import sys

# 导入回测模块
sys.path.append(r'/')
from 策略多因子系统.优化回测 import load_market_data
from cal_func.new.entry_pool import *
from cal_func.entry_signal_config import TEST_ENTRIES_LONG, get_entry_config, get_signal_categories

# 配置显示
pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000)


# ==================== 配置区域 ====================
frequency = "15min"

# 市场数据路径配置
MARKET_DATA_PATHS = {
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

# 测试时间范围
TEST_START = datetime(2025, 1, 1)  # 扩大时间范围以支持样本外验证
TEST_END = datetime(2026, 5, 31)

# 回测配置
BACKTEST_CONFIG = {
    "fees": 0.0004,
    "rf": 0.00,
}

# 统计窗口（信号点后的bar数量）
STAT_WINDOWS = [20, 40, 60]

# 验证配置
VALIDATION_CONFIG = {
    "min_samples_per_month": 10,      # 每月最少信号数
    "min_months_valid": 3,            # 至少有效月份数
    "stability_weight": 0.3,          # 稳定性权重
    "sample_out_weight": 0.3,          # 样本外权重
    "top_n": 30,                       # 每个信号返回前几组参数
    "window_weights": {20: 0.5, 40: 0.3, 60: 0.2},  # 加权平均
}

# 输出目录
OUTPUT_DIR = r"D:\jason_src\策略多因子系统\entry_test_results"

# ==================== 测试配置 ====================
# 从配置模块导入所有多头信号配置
TEST_ENTRIES = TEST_ENTRIES_LONG

# 可选：只测试特定分类的信号
# TEST_ENTRIES = {k: v for k, v in TEST_ENTRIES_LONG.items() if k.startswith('sma_')}



# ==================== 核心功能 ====================

def generate_param_values(start: int, end: int, step: float) -> List:
    """生成参数值列表"""
    if isinstance(step, int):
        return list(range(start, end + step, step))
    else:
        values = []
        current = start
        while current <= end + 0.001:
            values.append(round(current, 6))
            current += step
        return values


def split_data_by_month(
    market_df: pd.DataFrame,
    start_date: datetime,
    end_date: datetime
) -> List[Tuple[pd.DataFrame, str]]:
    """
    按月分割数据

    Returns:
        List of (月度数据, 年月标识)
    """
    monthly_data = []

    # 检查是否有时间列
    time_col = None
    for col in ['time', 'date', 'datetime', 'timestamp']:
        if col in market_df.columns:
            time_col = col
            break

    if time_col is None:
        # 如果没有时间列，按行数简单分割（假设数据连续）
        print("  警告: 未找到时间列，使用简单分割")
        total_bars = len(market_df)
        # 假设每个月大约相等数量的bar
        bars_per_month = total_bars // 12  # 粗略估计

        for i in range(12):
            start_idx = i * bars_per_month
            end_idx = (i + 1) * bars_per_month if i < 11 else total_bars

            month_df = market_df.iloc[start_idx:end_idx].copy()
            if len(month_df) > 0:
                # 估算年月
                year = 2025 + i // 12
                month = (i % 12) + 1
                month_key = f"{year}-{month:02d}"
                monthly_data.append((month_df, month_key))

        return monthly_data

    # 有时间列，按月分割
    current = start_date

    while current <= end_date:
        # 计算该月的起止
        year, month = current.year, current.month
        month_start = datetime(year, month, 1)

        if month == 12:
            month_end = datetime(year + 1, 1, 1) - pd.Timedelta(days=1)
        else:
            month_end = datetime(year, month + 1, 1) - pd.Timedelta(days=1)

        month_end = min(month_end, end_date)

        # 筛选该月数据
        month_df = market_df[
            (market_df[time_col] >= month_start) &
            (market_df[time_col] <= month_end)
        ].copy()

        if len(month_df) > 0:
            month_key = f"{year}-{month:02d}"
            monthly_data.append((month_df, month_key))

        # 下个月
        current = month_end + pd.Timedelta(days=1)

    return monthly_data


def calculate_signal_performance(
    market_df: pd.DataFrame,
    signal_points: np.ndarray,
    windows: List[int] = None,
) -> Dict[str, Any]:
    """计算信号点后的表现统计"""
    if windows is None:
        windows = STAT_WINDOWS

    close_prices = market_df['close'].values
    open_prices = market_df['open'].values
    high_prices = market_df['high'].values
    low_prices = market_df['low'].values

    n_signals = signal_points.sum()

    if n_signals == 0 or not np.any(signal_points[~np.isnan(signal_points)]):
        return {"信号数量": 0, "信号密度": 0}

    stats = {"信号数量": n_signals, "信号密度": n_signals / len(signal_points)}

    for window in windows:
        max_returns = []
        min_returns = []
        final_returns = []
        above_open_ratios = []

        signal_indices = np.where(signal_points)[0]

        for idx in signal_indices:
            if idx + window >= len(close_prices):
                continue

            entry_price = open_prices[idx + 1] if idx + 1 < len(open_prices) else close_prices[idx]
            window_high = high_prices[idx + 1: idx + window + 1]
            window_low = low_prices[idx + 1: idx + window + 1]
            window_close = close_prices[idx + window]

            if np.all(np.isnan(window_high)) or np.all(np.isnan(window_low)):
                continue

            max_return = (np.nanmax(window_high) - entry_price) / entry_price
            min_return = (np.nanmin(window_low) - entry_price) / entry_price
            final_return = (window_close - entry_price) / entry_price
            above_open_ratio = np.sum(window_high > entry_price) / window

            max_returns.append(max_return)
            min_returns.append(min_return)
            final_returns.append(final_return)
            above_open_ratios.append(above_open_ratio)

        prefix = f"w{window}_"

        if max_returns:
            stats.update({
                f"{prefix}信号数": len(max_returns),
                f"{prefix}最后收益_mean": np.mean(final_returns),
                f"{prefix}最后盈利占比": np.sum(np.array(final_returns) > 0) / len(final_returns),
                f"{prefix}盈亏比": np.mean(max_returns) / abs(np.mean(min_returns)) if np.mean(min_returns) < 0 else 0,
            })

    return stats


def calculate_stability_and_validation(
    monthly_data: List[Tuple[pd.DataFrame, str]],
    entry_func,
    entry_params: Dict[str, Any],
    windows: List[int] = None
) -> Dict[str, Any]:
    """
    计算稳定性和样本外验证指标

    Args:
        monthly_data: 按月分割的数据列表
        entry_func: 入场函数
        entry_params: 参数
        windows: 统计窗口

    Returns:
        Dict: 包含稳定性、样本内外的统计
    """
    if windows is None:
        windows = STAT_WINDOWS

    # 按月计算表现
    monthly_stats = []

    for month_df, month_key in monthly_data:
        try:
            signal_points = entry_func(month_df, **entry_params)

            if not isinstance(signal_points, np.ndarray):
                continue

            stats = calculate_signal_performance(month_df, signal_points, windows)
            stats['month'] = month_key
            monthly_stats.append(stats)

        except Exception as e:
            continue

    if len(monthly_stats) == 0:
        return None

    # 转换为DataFrame
    monthly_df = pd.DataFrame(monthly_stats)

    # 计算稳定性指标
    result = {
        '总月份数': len(monthly_stats),
        '有效月份数': 0,
    }

    for window in windows:
        col_mean = f'w{window}_最后收益_mean'
        col_signal = f'w{window}_信号数'

        # 检查列是否存在
        if col_mean not in monthly_df.columns or col_signal not in monthly_df.columns:
            result.update({
                f'w{window}_平均收益': 0,
                f'w{window}_稳定性': 0,
                f'w{window}_样本内收益': 0,
                f'w{window}_样本外收益': 0,
            })
            continue

        # 筛选有效月份（信号数足够）
        valid_months = monthly_df[
            (monthly_df[col_signal].notna()) &
            (monthly_df[col_signal] >= VALIDATION_CONFIG['min_samples_per_month']) &
            (monthly_df[col_mean].notna())
        ]

        n_valid = len(valid_months)
        result['有效月份数'] = max(result['有效月份数'], n_valid)

        if n_valid >= VALIDATION_CONFIG['min_months_valid']:
            returns = valid_months[col_mean].values

            # 稳定性指标（变异系数的倒数）
            mean_return = np.mean(returns)
            std_return = np.std(returns)

            if std_return > 0 and mean_return != 0:
                # 变异系数CV = std/mean，稳定性 = 1/CV = mean/std
                stability = abs(mean_return) / std_return
            else:
                stability = 0

            # 分割样本内外（最后1个月为样本外）
            if n_valid >= 4:
                in_sample = valid_months.iloc[:-1]
                out_sample = valid_months.iloc[-1:]

                in_return = in_sample[col_mean].mean()
                out_return = out_sample[col_mean].iloc[0] if len(out_sample) > 0 else 0

                # 样本外衰减率
                if in_return > 0:
                    decay_rate = out_return / in_return
                else:
                    decay_rate = 0
            else:
                in_return = mean_return
                out_return = 0
                decay_rate = 0

            result.update({
                f'w{window}_平均收益': mean_return,
                f'w{window}_收益标准差': std_return,
                f'w{window}_稳定性': stability,
                f'w{window}_样本内收益': in_return,
                f'w{window}_样本外收益': out_return,
                f'w{window}_样本外衰减率': decay_rate,
            })
        else:
            result.update({
                f'w{window}_平均收益': 0,
                f'w{window}_稳定性': 0,
                f'w{window}_样本内收益': 0,
                f'w{window}_样本外收益': 0,
            })

    return result


def calculate_composite_score(
    validation_result: Dict[str, Any],
    window: int = 20
) -> float:
    """
    计算综合评分

    公式：样本内收益 × (1 + 稳定性权重 × 稳定性系数) × (1 + 样本外权重 × 衰减率)
    """
    in_return = validation_result.get(f'w{window}_样本内收益', 0)
    stability = validation_result.get(f'w{window}_稳定性', 0)
    decay_rate = validation_result.get(f'w{window}_样本外衰减率', 0)

    w_stability = VALIDATION_CONFIG['stability_weight']
    w_sample_out = VALIDATION_CONFIG['sample_out_weight']

    # 稳定性奖励（标准化到0-1）
    stability_bonus = min(stability / 3, 1)  # 假设稳定性>3为优秀

    # 样本外奖励
    sample_out_bonus = max(min(decay_rate, 1), -1)  # 衰减率在[-1,1]之间

    # 综合评分
    if in_return > 0:
        score = in_return * (1 + w_stability * stability_bonus) * (1 + w_sample_out * sample_out_bonus)
    else:
        score = in_return  # 负收益直接用负值

    return score


def test_entry_function(
    monthly_data: List[Tuple[pd.DataFrame, str]],
    entry_name: str,
    entry_params_config: Dict[str, List],
    windows: List[int] = None,
) -> pd.DataFrame:
    """测试单个 entry 函数的所有参数组合"""
    if windows is None:
        windows = STAT_WINDOWS

    entry_func = globals().get(entry_name)
    if entry_func is None:
        print(f"✗ 未找到函数: {entry_name}")
        return pd.DataFrame()

    # 生成参数组合
    param_names = list(entry_params_config.keys())
    param_combinations = []

    for param_name in param_names:
        start, end, step = entry_params_config[param_name]
        param_combinations.append(generate_param_values(start, end, step))

    import itertools
    results = []
    total_tests = 1
    for values in param_combinations:
        total_tests *= len(values)

    print(f"\n测试函数: {entry_name}")
    print(f"参数配置: {entry_params_config}")
    print(f"预计测试数量: {total_tests}")
    print("-" * 60)

    test_count = 0
    valid_count = 0

    for combo in itertools.product(*param_combinations):
        test_count += 1
        params = dict(zip(param_names, combo))

        # 计算稳定性和验证指标
        validation_result = calculate_stability_and_validation(
            monthly_data, entry_func, params, windows
        )

        if validation_result and validation_result['有效月份数'] >= VALIDATION_CONFIG['min_months_valid']:
            valid_count += 1

            # 计算各窗口的综合评分
            for window in windows:
                score = calculate_composite_score(validation_result, window)

                result_entry = {
                    'entry_name': entry_name,
                    'entry_params': str(params),
                    'score': score,
                    'window': window,
                    'signal_id': generate_signal_id(entry_name, params),
                }

                # 添加参数列
                for key, value in params.items():
                    result_entry[f'param_{key}'] = value

                # 添加验证指标
                result_entry.update({
                    '有效月份数': validation_result['有效月份数'],
                    f'w{window}_平均收益': validation_result.get(f'w{window}_平均收益', 0),
                    f'w{window}_稳定性': validation_result.get(f'w{window}_稳定性', 0),
                    f'w{window}_样本内收益': validation_result.get(f'w{window}_样本内收益', 0),
                    f'w{window}_样本外收益': validation_result.get(f'w{window}_样本外收益', 0),
                    f'w{window}_样本外衰减率': validation_result.get(f'w{window}_样本外衰减率', 0),
                })

                results.append(result_entry)

                # 打印进度
                if test_count % 50 == 0 or test_count == total_tests:
                    print(f"  [{test_count}/{total_tests}] 有效: {valid_count}")

    print(f"\n有效测试: {valid_count}/{total_tests}")

    return pd.DataFrame(results)


def generate_signal_id(entry_name: str, params: Dict[str, Any]) -> str:
    """
    生成信号ID
    格式: 信号名称^参数1^参数2
    """
    # 按参数名排序，确保一致性
    sorted_params = sorted(params.items())
    param_str = '^'.join([str(v) for k, v in sorted_params])

    return f"{entry_name}^{param_str}"


def select_top_parameters(
    results_df: pd.DataFrame,
    entry_name: str,
    windows: List[int] = None,
    top_n: int = 10
) -> List[Dict]:
    """
    整合所有窗口的评分，选择前N组参数

    流程：
    1. 计算加权综合评分
    2. 按参数去重（同一组参数只保留最高分）
    3. 按综合评分排序，取前N名

    Returns:
        List[Dict]: topN_results
    """
    if windows is None:
        windows = STAT_WINDOWS

    weights = VALIDATION_CONFIG['window_weights']

    # 按参数组合，计算加权综合评分
    param_scores = {}  # {param_tuple: {各窗口数据, 综合评分}}

    for _, row in results_df.iterrows():
        # 提取参数（作为字典的键）
        params = {}
        for col in row.index:
            if col.startswith('param_'):
                param_name = col.replace('param_', '')
                params[param_name] = row[col]

        # 参数转元组作为key
        param_key = tuple(sorted(params.items()))
        window = row['window']
        score = row['score']

        if param_key not in param_scores:
            param_scores[param_key] = {
                'params': params,
                'scores': {},  # 各窗口评分
                '综合评分': 0,
                'metrics': {},  # 各窗口指标
                '有效月份数': row['有效月份数'],
            }

        param_scores[param_key]['scores'][window] = score

        # 保存该窗口的详细指标
        param_scores[param_key]['metrics'][f'w{window}_平均收益'] = float(row[f'w{window}_平均收益'])
        param_scores[param_key]['metrics'][f'w{window}_稳定性'] = float(row[f'w{window}_稳定性'])
        param_scores[param_key]['metrics'][f'w{window}_样本内收益'] = float(row[f'w{window}_样本内收益'])
        param_scores[param_key]['metrics'][f'w{window}_样本外收益'] = float(row[f'w{window}_样本外收益'])
        param_scores[param_key]['metrics'][f'w{window}_样本外衰减率'] = float(row[f'w{window}_样本外衰减率'])

    # 计算加权综合评分
    for param_key, data in param_scores.items():
        weighted_score = 0
        for window, weight in weights.items():
            if window in data['scores']:
                weighted_score += weight * data['scores'][window]
        data['综合评分'] = weighted_score

    # 按综合评分排序
    sorted_params = sorted(param_scores.items(), key=lambda x: x[1]['综合评分'], reverse=True)

    # 取前N名并转换为字典列表
    top_list = []
    for i, (param_key, data) in enumerate(sorted_params[:top_n]):
        result_dict = {
            'signal_id': generate_signal_id(entry_name, data['params']),
            'entry_name': entry_name,
            'params': data['params'],
            '综合评分': float(data['综合评分']),
            '有效月份数': int(data['有效月份数']),
            '各窗口评分': data['scores'],
            **data['metrics'],
        }
        top_list.append(result_dict)

    return top_list


def save_results(
    all_results: Dict[str, List[Dict]],
    output_dir: str,
    code_id: str = "GCmain",
    top_n: int = 10
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    保存结果为DataFrame

    Returns:
        Tuple: (完整结果DataFrame, TopN结果DataFrame)
    """
    os.makedirs(output_dir, exist_ok=True)

    # ==================== 构建完整结果DataFrame ====================
    full_df_rows = []

    for signal_name, top_list in all_results.items():
        for result in top_list:
            row = {
                '信号大类': signal_name,
                '信号具体Id': result['signal_id'],
                '综合评分': result['综合评分'],
                '有效月份数': result['有效月份数'],
            }

            # 添加各窗口评分
            for w in [20, 40, 60]:
                if w in result['各窗口评分']:
                    row[f'w{w}_评分'] = result['各窗口评分'][w]

            # 添加各窗口收益和指标
            for w in [20, 40, 60]:
                row[f'w{w}_平均收益'] = result.get(f'w{w}_平均收益', np.nan)
                row[f'w{w}_稳定性'] = result.get(f'w{w}_稳定性', np.nan)
                row[f'w{w}_样本内收益'] = result.get(f'w{w}_样本内收益', np.nan)
                row[f'w{w}_样本外收益'] = result.get(f'w{w}_样本外收益', np.nan)
                row[f'w{w}_样本外衰减率'] = result.get(f'w{w}_样本外衰减率', np.nan)

            full_df_rows.append(row)

    # 创建完整结果DataFrame
    full_result_df = pd.DataFrame(full_df_rows)

    # 按综合评分排序
    full_result_df = full_result_df.sort_values('综合评分', ascending=False)

    # 保存完整结果CSV
    full_csv_path = os.path.join(output_dir, f"{code_id}_entry_all_validated.csv")
    full_result_df.to_csv(full_csv_path, index=False, encoding='utf-8-sig')
    print(f"✓ 已保存完整结果: {full_csv_path}")
    print(f"  总计: {len(full_result_df)} 组参数")

    # ==================== 构建TopN结果DataFrame（只保留三列） ====================
    top_n_df = full_result_df[['信号大类', '信号具体Id', '综合评分']].head(top_n)

    # 保存TopN结果CSV
    top_csv_path = os.path.join(output_dir, f"{code_id}_entry_top{top_n}_validated.csv")
    top_n_df.to_csv(top_csv_path, index=False, encoding='utf-8-sig')
    print(f"✓ 已保存Top{top_n}结果: {top_csv_path}")

    # 打印全局前N名
    print("\n" + "=" * 80)
    print(f"全局前{top_n}组参数汇总（经稳定性与样本外验证，窗口加权整合）")
    print("综合评分 = 0.5×w20评分 + 0.3×w40评分 + 0.2×w60评分")
    print("=" * 80)

    for i, row in top_n_df.iterrows():
        print(f"\n#{i+1} {row['信号大类']} | {row['信号具体Id']} | 综合评分: {row['综合评分']:.4f}")

    return full_result_df, top_n_df


# ==================== 主程序 ====================

def main(code_id = "CLmain"):
    """主程序入口"""


    print("=" * 80)
    print("Entry 信号稳定性与样本外验证测试")
    print("=" * 80)
    print(f"品种: {code_id}")
    print(f"时间: {TEST_START} 至 {TEST_END}")
    print(f"统计窗口: {STAT_WINDOWS}")
    print(f"验证配置: 最少月数={VALIDATION_CONFIG['min_months_valid']}, "
          f"稳定性权重={VALIDATION_CONFIG['stability_weight']}, "
          f"样本外权重={VALIDATION_CONFIG['sample_out_weight']}")
    print("=" * 80)

    # 1. 加载市场数据
    print("\n[1/4] 加载市场数据...")
    market_df = load_market_data(
        code_id=code_id,
        start=TEST_START,
        end=TEST_END,
        market_data_paths=MARKET_DATA_PATHS,
        HISTORICAL_BUFFER_DAYS=10
    )
    print(f"✓ 已加载 {len(market_df)} 条数据")

    # 2. 按月分割数据
    print("\n[2/4] 按月分割数据...")
    monthly_data = split_data_by_month(market_df, TEST_START, TEST_END)
    print(f"✓ 已分割为 {len(monthly_data)} 个月")

    for month_df, month_key in monthly_data[:3]:  # 显示前3个月
        print(f"  {month_key}: {len(month_df)} 条")
    if len(monthly_data) > 3:
        print(f"  ... 共 {len(monthly_data)} 个月")

    # 3. 测试各信号函数
    print("\n[3/4] 测试信号函数...")
    all_results = {}

    for entry_name, entry_params_config in TEST_ENTRIES.items():
        results_df = test_entry_function(
            monthly_data=monthly_data,
            entry_name=entry_name,
            entry_params_config=entry_params_config,
            windows=STAT_WINDOWS,
        )

        if not results_df.empty:
            # 4. 选择前10组参数（整合所有窗口）
            top_results = select_top_parameters(
                results_df,
                entry_name,
                STAT_WINDOWS,
                VALIDATION_CONFIG['top_n']
            )
            all_results[entry_name] = top_results

            # 保存单个函数的完整结果
            full_path = os.path.join(OUTPUT_DIR, f"{code_id}_{entry_name}_validation_full.csv")
            results_df.to_csv(full_path, index=False, encoding='utf-8-sig')
            print(f"✓ 已保存完整结果: {full_path}")

    # 5. 保存汇总结果 - 取全局前10名
    print("\n[4/4] 保存汇总结果（全局前10名）...")
    full_df, top_df = save_results(all_results, OUTPUT_DIR, code_id, VALIDATION_CONFIG['top_n'])

    # 返回完整结果供后续分析
    return full_df, top_df

    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)

    return all_results


if __name__ == "__main__":
    code_ids = ['GCmain']#'CLmain', 'SImain', 'HGmain',  'ZSmain', 'ZLmain', 'ZMmain', 'ZWmain', 'ZCmain',
    for code_id in code_ids:

        main(code_id)
