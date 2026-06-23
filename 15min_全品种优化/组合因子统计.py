"""
策略部分统计分析脚本 - 函数式编程版本
核心逻辑：
1. 读取DataFrame
2. 计算排名分数（收益类正排，风险类逆排）
3. 将策略分为三个部分（过滤、入场、出场），每个部分作为整体因子
4. 分组聚合统计
5. 输出最佳部分组合
"""

import pandas as pd
import numpy as np
import json
import os
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
    raise ValueError(f"找不到策略名称列，数据列: {list(df.columns)}")


def get_available_metrics(df: pd.DataFrame, config: Dict) -> Dict[str, Tuple[str, float]]:
    """获取数据中实际存在的指标"""
    available = {}

    for col, (direction, weight) in config.items():
        if col in df.columns:
            available[col] = (direction, weight)

    if not available:
        raise ValueError(f"数据中未找到任何配置的指标列，数据列: {list(df.columns)}")

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

    # 计算综合得分 - 直接使用配置中的权重
    score_cols = [f'{col}_score' for col in available_metrics.keys()]
    weights = [weight for (_, weight) in available_metrics.values()]

    # 归一化权重
    weights_array = np.array(weights) / sum(weights)

    # 加权计算综合分
    df['composite_score'] = df[score_cols].mul(weights_array, axis=1).sum(axis=1)

    return df, available_metrics


# ==================== 策略解析（按部分整体） ====================

def parse_strategy_parts(strategy_name: str) -> Tuple[str, str, str]:
    """
    解析策略名称，返回三个部分的完整字符串

    Returns:
        (过滤部分整体, 入场部分整体, 出场部分整体)
    """
    parts = strategy_name.split('&')

    if len(parts) >= 3:
        filter_part = parts[0] if parts[0] else ''
        signal_part = parts[1] if parts[1] else ''
        exit_part = parts[2] if parts[2] else ''
    elif len(parts) == 2:
        filter_part = parts[0] if parts[0] else ''
        signal_part = parts[1] if parts[1] else ''
        exit_part = ''
    else:
        filter_part = parts[0] if parts[0] else ''
        signal_part = ''
        exit_part = ''

    return filter_part, signal_part, exit_part


def parse_all_strategies(df: pd.DataFrame, strategy_col: str) -> pd.DataFrame:
    """
    解析所有策略名称，生成部分数据表

    Returns:
        包含 index, part, part_type, strategy_name 列的DataFrame
    """
    print("解析策略名称（按部分整体）...")

    parsed_data = []

    for idx, row in df.iterrows():
        strategy_name = row[strategy_col]
        filter_part, signal_part, exit_part = parse_strategy_parts(strategy_name)

        if filter_part:
            parsed_data.append({
                'index': idx,
                'part': filter_part,
                'part_type': 'filter',
                'strategy_name': strategy_name
            })

        if signal_part:
            parsed_data.append({
                'index': idx,
                'part': signal_part,
                'part_type': 'signal',
                'strategy_name': strategy_name
            })

        if exit_part:
            parsed_data.append({
                'index': idx,
                'part': exit_part,
                'part_type': 'exit',
                'strategy_name': strategy_name
            })

    parts_df = pd.DataFrame(parsed_data)
    print(f"解析完成，共 {len(parts_df)} 个部分实例")
    return parts_df


# ==================== 数据合并 ====================

def merge_scores_with_parts(parts_df: pd.DataFrame,
                             scored_df: pd.DataFrame,
                             score_cols: List[str]) -> pd.DataFrame:
    """
    将评分数据合并到部分数据表

    Args:
        parts_df: 部分数据表
        scored_df: 包含评分的策略数据表
        score_cols: 需要合并的评分列名列表

    Returns:
        合并后的数据表
    """
    print("合并数据...")

    merged = parts_df.merge(
        scored_df[score_cols],
        left_on='index',
        right_index=True,
        how='left'
    )

    return merged


# ==================== 分组聚合 ====================

def aggregate_part_scores(merged_df: pd.DataFrame,
                          score_cols: List[str]) -> Dict[str, pd.DataFrame]:
    """
    按部分类型和部分内容分组聚合

    Returns:
        按part_type分组的聚合结果字典 {part_type: DataFrame}
    """
    print("\n按部分分组统计...")

    results = {}

    for part_type in ['filter', 'signal', 'exit']:
        type_df = merged_df[merged_df['part_type'] == part_type]

        if len(type_df) == 0:
            print(f"  {part_type}: 无数据")
            results[part_type] = pd.DataFrame()
            continue

        # 分组聚合
        agg_dict = {
            'composite_score': ['mean', 'std', 'count']
        }
        agg_dict.update({col: 'mean' for col in score_cols if col != 'composite_score'})

        grouped = type_df.groupby('part').agg(agg_dict).round(2)

        # 展平列名
        grouped.columns = ['_'.join(col).strip('_') for col in grouped.columns.values]
        grouped = grouped.reset_index()
        grouped = grouped.sort_values('composite_score_mean', ascending=False)

        print(f"  {part_type}: {len(grouped)} 个部分组合")
        results[part_type] = grouped

    return results


def filter_by_count(aggregated_dict: Dict[str, pd.DataFrame],
                    filter_config: Dict[str, int],
                    part_type_names: Dict[str, str]) -> Dict[str, pd.DataFrame]:
    """按filter_config保留每个部分的top部分"""
    print(f"\n按配置保留top部分:")

    results = {}
    for part_type, df in aggregated_dict.items():
        if len(df) == 0:
            results[part_type] = df
            continue

        top_n = filter_config.get(part_type, 10)
        filtered = df.head(top_n)
        results[part_type] = filtered

        print(f"  {part_type_names.get(part_type, part_type)}: "
              f"保留top {top_n}")

    return results


# ==================== 输出 ====================

def save_results(results_dict: Dict[str, pd.DataFrame],
                 output_dir: Path,
                 symbol_code: str,
                 part_type_names: Dict[str, str]):
    """保存结果为JSON格式"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 部分类型到JSON字段的映射
    part_type_to_json_field = {
        'filter': 'EntryFilters',
        'signal': 'EntrySignals',
        'exit': 'ExitSignals'
    }

    # 部分组合方式
    part_combination = {
        'EntryFilters': 'and',
        'EntrySignals': 'or',
        'ExitSignals': 'or'
    }

    # 构建JSON结构
    json_result = []

    for part_type in ['filter', 'signal', 'exit']:
        df = results_dict.get(part_type, pd.DataFrame())
        json_field = part_type_to_json_field[part_type]

        # 提取部分列表（保持原始格式，不添加空格）
        items = []
        if len(df) > 0:
            items = df['part'].tolist()
        items_len = max([len(i0.split("|")) for i0 in items])

        res0 = {
            'name':json_field,
            'items': items,
            'select_count':items_len, #这里是数字
            'combination': part_combination[json_field]
        }
        json_result.append(res0)

    # 保存为JSON文件
    output_path = output_dir / f'{symbol_code}_parts_config.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({symbol_code: json_result}, f, indent=4)

    print(f"\n保存JSON配置: {output_path}")



def print_report(results_dict: Dict[str, pd.DataFrame],
                 part_type_names: Dict[str, str]):
    """打印分析报告"""
    print("\n" + "=" * 120)
    print("策略部分分析报告")
    print("=" * 120)

    for part_type, df in results_dict.items():
        if len(df) == 0:
            continue

        print(f"\n【{part_type_names.get(part_type, part_type)}】Top {len(df)} 部分组合:")
        print("-" * 120)

        # 选择显示列
        display_cols = ['part', 'composite_score_mean', 'composite_score_count']

        # 添加得分列
        for col in df.columns:
            if col.endswith('_score') and col != 'composite_score_mean' and 'composite' not in col:
                display_cols.append(col)

        # 创建显示DataFrame
        display_df = df[display_cols].copy()

        # 重命名列
        new_names = {
            'part': '部分组合',
            'composite_score_mean': '综合得分',
            'composite_score_count': '出现次数'
        }
        new_names.update({
            col: col.replace('_score_mean', '').replace('_total+', '').replace('%', '')
            for col in display_cols[3:]
        })

        display_df.columns = [new_names.get(col, col) for col in display_cols]

        print(display_df.to_string(index=False))
        print("-" * 120)


# ==================== 主流程 ====================

def analyze_parts(data_path: str,
                  output_dir: str = None,
                  symbol_code: str = 'result',
                  metrics_config: Dict = None,
                  part_type_names: Dict = None,
                  filter_config: Dict = None) -> Dict[str, pd.DataFrame]:
    """
    执行完整的部分分析流程

    Args:
        data_path: 原始数据文件路径
        output_dir: 结果输出目录
        symbol_code: 品种代码
        metrics_config: 指标配置
        part_type_names: 部分类型名称映射
        filter_config: 过滤配置

    Returns:
        分析结果字典 {part_type: DataFrame}
    """
    print(f"\n{'='*120}")
    print(f"开始处理品种（部分统计）: {symbol_code}")
    print(f"{'='*120}")

    try:
        # 1. 加载数据
        df = load_data(data_path)
        strategy_col = get_strategy_column(df)

        # 2. 计算评分
        print("\n计算策略评分...")
        scored_df, available_metrics = calculate_strategy_scores(df, metrics_config)
        score_cols = ['composite_score'] + [f'{col}_score' for col in available_metrics.keys()]

        # 3. 解析策略名称（按部分整体）
        parts_df = parse_all_strategies(scored_df, strategy_col)

        # 4. 合并数据
        merged_df = merge_scores_with_parts(parts_df, scored_df, score_cols)

        # 5. 分组聚合
        aggregated = aggregate_part_scores(merged_df, score_cols)

        # 6. 按配置过滤
        filtered = filter_by_count(aggregated, filter_config, part_type_names)

        # 7. 输出结果
        if output_dir is None:
            output_dir = Path(data_path).parent

        save_results(filtered, output_dir, symbol_code, part_type_names)
        print_report(filtered, part_type_names)

        return filtered

    except Exception as e:
        print(f"处理品种 {symbol_code} 时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return {}


def main():
    """主函数"""
    print("=" * 120)
    print("策略部分统计分析工具")
    print("=" * 120)

    # ==================== 配置区域 ====================

    # 指标配置：列名 -> (方向, 权重)
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

    # 部分类型名称映射
    part_type_names = {
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
    symbolist = ['GCmain', 'SImain', 'HGmain', 'CLmain', 'ZSmain', 'ZLmain', 'ZMmain', 'ZWmain', 'ZCmain'][:1]

    # 基础路径
    aim_dir = r'D:\jason_src\策略多因子系统\15min_全品种优化\backtest_result_data-f-2_s-2_e-2_jzmode-d_new'

    # ==================== 批量处理 ====================

    success_count = 0
    fail_count = 0

    for code0 in symbolist:
        data_path = os.path.join(aim_dir, f'optimization_{code0}', 'raw_evaluation_cache.csv')
        output_dir = os.path.join(aim_dir, f'optimization_{code0}')

        try:
            result = analyze_parts(
                data_path=data_path,
                output_dir=output_dir,
                symbol_code=code0,
                metrics_config=metrics_config,
                part_type_names=part_type_names,
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
    main()
