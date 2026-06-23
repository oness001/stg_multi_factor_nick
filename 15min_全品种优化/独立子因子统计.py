"""
策略因子统计分析脚本 - 函数式编程版本
核心逻辑：
1. 读取DataFrame
2. 计算排名分数（收益类正排，风险类逆排）
3. 解析策略名称为因子
4. 分组聚合统计
5. 输出最佳因子
"""

import pandas as pd
import numpy as np
import json,os
from pathlib import Path
from typing import Dict, List, Tuple
pd.set_option('display.max_rows', 10000)
pd.set_option('display.max_columns', 10000)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 1500)
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('expand_frame_repr', False)
pd.set_option('display.float_format', lambda x: '%.4f' % x)


# ==================== 配置 ====================

# 指标配置：列名 -> (方向, 权重)
# 方向: 'positive'=越大越好, 'negative'=越小越好
# 权重: 直接用于计算综合分的权重比例

# ==================== 数据加载 ====================

def load_data(file_path: str) -> pd.DataFrame:
    """加载CSV数据"""
    print(f"加载数据: {file_path}")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    df = pd.read_csv(file_path)
    print(f"加载完成，共 {len(df)} 行数据")
    return df


def get_strategy_column(df: pd.DataFrame) -> str:
    """获取策略名称列名"""
    for col in ['策略名称', 'strategy_name', 'StrategyName']:
        if col in df.columns:
            return col
    raise ValueError("找不到策略名称列")


def get_available_metrics(df: pd.DataFrame, config: Dict) -> Dict[str, Tuple[str, float]]:
    """获取数据中实际存在的指标"""
    available = {}

    for col, (direction, weight) in config.items():
        if col in df.columns:
            available[col] = (direction, weight)

    print(f"可用指标: {list(available.keys())}")
    return available


# ==================== 评分计算 ====================

def calculate_rank_score(series: pd.Series, direction: str) -> pd.Series:
    """
    计算排名分数（0-100）

    Args:
        series: 指标值序列
        direction: 'positive'=越大越好, 'negative'=越小越好

    Returns:
        归一化分数序列
    """
    n = len(series)
    if n <= 1:
        return pd.Series([50] * n, index=series.index)

    # 计算排名
    if direction == 'positive':
        ranks = series.rank(ascending=True, method='average')
    else:
        ranks = series.rank(ascending=False, method='average')

    # 归一化到0-100
    scores = (ranks - 1) / (n - 1) * 100
    return scores


def calculate_strategy_scores(df: pd.DataFrame, metrics_config: Dict) -> Tuple[pd.DataFrame, Dict]:
    """
    计算所有策略的评分

    Returns:
        (添加了评分列的DataFrame, 实际使用的指标字典)
    """
    df = df.copy()
    available_metrics = get_available_metrics(df, metrics_config)

    # 计算各项指标的排名分数
    for col, (direction, _) in available_metrics.items():
        df[f'{col}_score'] = calculate_rank_score(df[col], direction)

    # 计算综合得分 - 直接使用METRICS_CONFIG中的权重
    score_cols = [f'{col}_score' for col in available_metrics.keys()]
    weights = [weight for (_, weight) in available_metrics.values()]

    # 归一化权重
    weights_array = np.array(weights) / sum(weights)

    # 加权计算综合分
    df['composite_score'] = df[score_cols].mul(weights_array, axis=1).sum(axis=1)

    return df, available_metrics


# ==================== 策略解析 ====================

def parse_strategy_name(strategy_name: str) -> Tuple[List[str], List[str], List[str]]:
    """
    解析单个策略名称

    Returns:
        (过滤因子列表, 入场因子列表, 出场因子列表)
    """
    parts = strategy_name.split('&')

    if len(parts) >= 3:
        filters = parts[0].split('|') if parts[0] else []
        signals = parts[1].split('|') if parts[1] else []
        exits = parts[2].split('|') if parts[2] else []
    elif len(parts) == 2:
        filters = parts[0].split('|') if parts[0] else []
        signals = parts[1].split('|') if parts[1] else []
        exits = []
    else:
        filters = parts[0].split('|') if parts[0] else []
        signals = []
        exits = []

    # 过滤空字符串
    return [f for f in filters if f], [s for s in signals if s], [e for e in exits if e]


def parse_all_strategies(df: pd.DataFrame, strategy_col: str) -> pd.DataFrame:
    """
    解析所有策略名称，生成因子数据表

    Returns:
        包含 index, factor, factor_type, strategy_name 列的DataFrame
    """
    print("解析策略名称...")

    parsed_data = []

    for idx, row in df.iterrows():
        strategy_name = row[strategy_col]
        filters, signals, exits = parse_strategy_name(strategy_name)

        for factor in filters:
            parsed_data.append({
                'index': idx,
                'factor': factor,
                'factor_type': 'filter',
                'strategy_name': strategy_name
            })

        for factor in signals:
            parsed_data.append({
                'index': idx,
                'factor': factor,
                'factor_type': 'signal',
                'strategy_name': strategy_name
            })

        for factor in exits:
            parsed_data.append({
                'index': idx,
                'factor': factor,
                'factor_type': 'exit',
                'strategy_name': strategy_name
            })

    factors_df = pd.DataFrame(parsed_data)
    print(f"解析完成，共 {len(factors_df)} 个因子实例")
    return factors_df


# ==================== 数据合并 ====================

def merge_scores_with_factors(factors_df: pd.DataFrame,
                              scored_df: pd.DataFrame,
                              score_cols: List[str]) -> pd.DataFrame:
    """
    将评分数据合并到因子数据表

    Args:
        factors_df: 因子数据表
        scored_df: 包含评分的策略数据表
        score_cols: 需要合并的评分列名列表

    Returns:
        合并后的数据表
    """
    print("合并数据...")

    merged = factors_df.merge(
        scored_df[score_cols],
        left_on='index',
        right_index=True,
        how='left'
    )

    return merged


# ==================== 分组聚合 ====================

def aggregate_factor_scores(merged_df: pd.DataFrame,
                             score_cols: List[str]) -> pd.DataFrame:
    """
    按因子类型和因子名分组聚合

    Returns:
        按factor_type分组的聚合结果字典 {factor_type: DataFrame}
    """
    print("\n按因子分组统计...")

    results = {}

    for factor_type in ['filter', 'signal', 'exit']:
        type_df = merged_df[merged_df['factor_type'] == factor_type]

        if len(type_df) == 0:
            print(f"  {factor_type}: 无数据")
            results[factor_type] = pd.DataFrame()
            continue

        # 分组聚合（去掉count统计）
        agg_dict = {
            'composite_score': ['mean', 'std']
        }
        agg_dict.update({col: 'mean' for col in score_cols if col != 'composite_score'})

        grouped = type_df.groupby('factor').agg(agg_dict).round(2)

        # 展平列名
        grouped.columns = ['_'.join(col).strip('_') for col in grouped.columns.values]
        grouped = grouped.reset_index()
        grouped = grouped.sort_values('composite_score_mean', ascending=False)

        print(f"  {factor_type}: {len(grouped)} 个因子")
        results[factor_type] = grouped

    return results


def filter_by_count(aggregated_dict: Dict[str, pd.DataFrame],
                    filter_config: Dict[str, int],
                    factor_type_names: Dict[str, str]) -> Dict[str, pd.DataFrame]:
    """按filter_config保留每个部分的top因子"""
    print(f"\n按配置保留top因子:")

    results = {}
    for factor_type, df in aggregated_dict.items():
        if len(df) == 0:
            results[factor_type] = df
            continue

        top_n = filter_config.get(factor_type, 10)
        filtered = df.head(top_n)
        results[factor_type] = filtered

        print(f"  {factor_type_names.get(factor_type, factor_type)}: "
              f"保留top {top_n}")

    return results


def get_top_n(aggregated_dict: Dict[str, pd.DataFrame],
              top_n: int) -> Dict[str, pd.DataFrame]:
    """获取每个类型的前N个因子"""
    results = {}
    for factor_type, df in aggregated_dict.items():
        results[factor_type] = df.head(top_n) if len(df) > 0 else df
    return results


# ==================== 原始指标统计 ====================

def calculate_original_metrics(factors_df: pd.DataFrame,
                                 original_df: pd.DataFrame,
                                 strategy_col: str,
                                 metrics_dict: Dict) -> Dict[str, pd.DataFrame]:
    """
    计算每个因子的原始指标平均值

    Returns:
        {factor_type: 包含原始指标统计的DataFrame}
    """
    print("\n计算原始指标平均值...")

    results = {}

    for factor_type in ['filter', 'signal', 'exit']:
        type_df = factors_df[factors_df['factor_type'] == factor_type]

        if len(type_df) == 0:
            results[factor_type] = pd.DataFrame()
            continue

        # 获取该类型所有唯一因子
        unique_factors = type_df['factor'].unique()

        factor_stats = []

        for factor in unique_factors:
            # 获取包含该因子的策略
            factor_strategies = type_df[type_df['factor'] == factor]['strategy_name'].unique()

            # 从原始数据中获取这些策略的指标
            strategy_data = original_df[original_df[strategy_col].isin(factor_strategies)]

            if len(strategy_data) > 0:
                stats = {'factor': factor}
                for metric_col in metrics_dict.keys():
                    if metric_col in original_df.columns:
                        stats[f'avg_{metric_col}'] = strategy_data[metric_col].mean()
                factor_stats.append(stats)

        results[factor_type] = pd.DataFrame(factor_stats)

    return results


def merge_original_metrics(aggregated_dict: Dict[str, pd.DataFrame],
                            original_metrics_dict: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """将原始指标合并到聚合结果"""
    results = {}
    for factor_type in aggregated_dict.keys():
        agg_df = aggregated_dict[factor_type]
        orig_df = original_metrics_dict.get(factor_type, pd.DataFrame())

        if len(agg_df) == 0 or len(orig_df) == 0:
            results[factor_type] = agg_df
        else:
            results[factor_type] = agg_df.merge(orig_df, on='factor', how='left')

    return results


# ==================== 输出 ====================

def save_results(results_dict: Dict[str, pd.DataFrame],
                 output_dir: Path,
                 factor_type_names: Dict[str, str]):
    """保存结果为JSON格式"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 因子类型到JSON字段的映射
    factor_type_to_json_field = {
        'filter': 'EntryFilters',
        'signal': 'EntrySignals',
        'exit': 'ExitSignals'
    }

    # 因子组合方式
    factor_combination = {
        'EntryFilters': 'and',
        'EntrySignals': 'or',
        'ExitSignals': 'or'
    }

    # 构建JSON结构
    json_result = {}

    for factor_type in ['filter', 'signal', 'exit']:
        df = results_dict.get(factor_type, pd.DataFrame())
        json_field = factor_type_to_json_field[factor_type]

        items = df['factor'].tolist() if len(df) > 0 else []

        json_result[json_field] = {
            'items': items,
            'select_count': len(items),
            'combination': factor_combination[json_field]
        }

    # 从路径提取品种代码
    symbol_code = output_dir.name.replace('optimization_', '')

    # 保存为JSON文件
    output_path = output_dir / f'{symbol_code}_stg_config.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({symbol_code: json_result}, f, ensure_ascii=False, indent=2)

    print(f"\n保存JSON配置: {output_path}")

    # 打印配置内容
    print("\n生成的配置:")
    for json_field, config in json_result.items():
        print(f"  {json_field} ({config['select_count']}个, {config['combination']}组合):")
        for i, item in enumerate(config['items'], 1):
            print(f"    {i}. {item}")


def print_report(results_dict: Dict[str, pd.DataFrame],
                 factor_type_names: Dict[str, str]):
    """打印分析报告"""
    print("\n" + "=" * 120)
    print("因子分析报告")
    print("=" * 120)

    for factor_type, df in results_dict.items():
        if len(df) == 0:
            continue

        print(f"\n【{factor_type_names.get(factor_type, factor_type)}】Top {len(df)} 因子:")
        print("-" * 120)

        # 选择显示列
        display_cols = ['factor', 'composite_score_mean']

        # 添加得分列
        for col in df.columns:
            if col.endswith('_score') and col != 'composite_score_mean':
                display_cols.append(col)

        # 创建显示DataFrame
        display_df = df[display_cols].copy()

        # 重命名列
        new_names = {
            'factor': '因子名称',
            'composite_score_mean': '综合得分'
        }
        new_names.update({
            col: col.replace('_score_mean', '').replace('_total+', '').replace('%', '')
            for col in display_cols[2:]
        })

        display_df.columns = [new_names.get(col, col) for col in display_cols]

        print(display_df.to_string(index=False))
        print("-" * 120)


# ==================== 主流程 ====================

def analyze_factors(data_path: str,
                    output_dir: str = None,
                    metrics_config: Dict = None,
                    factor_type_names: Dict = None,
                    filter_config: Dict = None) -> Dict[str, pd.DataFrame]:
    """
    执行完整的因子分析流程

    Args:
        data_path: 原始数据文件路径
        output_dir: 结果输出目录
        metrics_config: 指标配置
        factor_type_names: 因子类型名称映射
        filter_config: 过滤配置

    Returns:
        分析结果字典 {factor_type: DataFrame}
    """
    try:
        # 1. 加载数据
        df = load_data(data_path)
        strategy_col = get_strategy_column(df)

        # 2. 计算评分
        print("\n计算策略评分...")
        scored_df, available_metrics = calculate_strategy_scores(df, metrics_config)
        score_cols = ['composite_score'] + [f'{col}_score' for col in available_metrics.keys()]

        # 3. 解析策略名称
        factors_df = parse_all_strategies(scored_df, strategy_col)

        # 4. 合并数据
        merged_df = merge_scores_with_factors(factors_df, scored_df, score_cols)

        # 5. 分组聚合
        aggregated = aggregate_factor_scores(merged_df, score_cols)

        # 6. 按配置过滤
        filtered = filter_by_count(aggregated, filter_config, factor_type_names)

        # 7. 输出结果
        if output_dir is None:
            output_dir = Path(data_path).parent

        save_results(filtered, output_dir, factor_type_names)
        print_report(filtered, factor_type_names)

        return filtered

    except Exception as e:
        print(f"处理文件 {data_path} 时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return {}


def main_filter():
    """主函数"""
    # 1. 确定数据文件夹路径
    # 2.确定去读取数据文件前缀或标签。
    #确定对应的具体文件后，进行配置项的配置。
    # 运行脚本，输出结果到数据文件同级别的文件夹中

    # ==================== 配置区域 ====================

    # 指标配置：列名 -> (方向, 权重)
    # 方向: 'positive'=越大越好, 'negative'=越小越好
    # 权重: 直接用于计算综合分的权重比例
    metrics_config = {
        'total+总收益率%': ('positive', 3),
        'total+交易胜率%': ('positive', 2),
        'total+盈亏比': ('positive', 1.5),
        'total+sharpe比率': ('positive', 1.5),
        'total+calmar比率': ('positive', 1.5),
        'total+bar胜率%': ('positive', 1),
        'total+交易次数': ('positive', 0.5),
        'total+最大回撤%': ('negative', 2),
    }

    # 因子类型名称映射
    factor_type_names = {
        'filter': '过滤部分',
        'signal': '入场部分',
        'exit': '出场部分'
    }

    # 每个部分保留top数量
    filter_config = {
        'filter': 30,
        'signal': 10,
        'exit': 5
    }

    # 品种列表
    symbolist = ['GCmain', 'SImain', 'HGmain', 'CLmain', 'ZSmain', 'ZLmain', 'ZMmain', 'ZWmain', 'ZCmain']

    # 基础路径
    aim_dir = r'D:\jason_src\策略多因子系统\15min_全品种优化\backtest_result_data-f-2_s-2_e-2_jzmode-d'

    # ==================== 批量处理 ====================

    success_count = 0
    fail_count = 0

    for code0 in symbolist:
        data_path = os.path.join(aim_dir, f'optimization_{code0}', 'raw_evaluation_cache.csv')
        output_dir = os.path.join(aim_dir, f'optimization_{code0}')

        try:
            print(f"\n{'='*120}")
            print(f"开始处理品种: {code0}")
            print(f"{'='*120}")

            result = analyze_factors(
                data_path=data_path,
                output_dir=output_dir,
                metrics_config=metrics_config,
                factor_type_names=factor_type_names,
                filter_config=filter_config
            )

            if result:
                success_count += 1
            else:
                fail_count += 1

        except Exception as e:
            print(f"处理品种 {code0} 失败: {str(e)}")
            fail_count += 1

    print("\n" + "=" * 120)
    print(f"批量处理完成！成功: {success_count}, 失败: {fail_count}")
    print("=" * 120)


if __name__ == '__main__':
    main_filter()
