"""
Filter 函数分类效果测试脚本 - 简化版

测试特定 filter 函数在不同参数下的分类效果

作者: Auto-Generated
日期: 2026-06-15
"""

import pandas as pd
from typing import Dict, List, Any
from datetime import datetime
import sys
import os
import matplotlib

matplotlib.use('tkAgg')
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 导入回测模块
sys.path.append(r'/')

# 导入 filter_pool
from cal_func.old.filter_pool import *

# 配置显示
pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000)

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

# ==================== 配置区域 ====================

frequency = "15min"
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

def basic_metrics(
        mkdf: pd.DataFrame,
        strategy_name: str,
        fees: float | int = 0.004,
        rf: float | int = 0.00,
        jz_mode: str = "d",
        time_start: pd.Timestamp = None,
        resample_rule = '1MS'
):
    def basic_metrics0(
            mkdf: pd.DataFrame,
            strategy_name: str,
            fees: float | int = 0.004,
            rf: float | int = 0.00,
            jz_mode: str = "d",
            time_start: pd.Timestamp = None,
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
            metrics = {**{"开始时间": time_series.iloc[0], "结束时间": time_series.iloc[-1]}, **metrics, **{"策略名称": strategy_name}}
        else:
            metrics = {f"{time_start:%Y-%m-%d}+{k}": v for k, v in metrics.items()}

        return jz_series, metrics

    all_metrics = {}
    jz,metrics = basic_metrics0(
                mkdf=mkdf,
                strategy_name=strategy_name,
                fees=fees,
                rf=rf,
                jz_mode=jz_mode,
                time_start=time_start
            )
    all_metrics.update(metrics)
    if resample_rule:
        for time_start, sub_df in mkdf.resample(resample_rule, on='datetime', closed="left", label="left"):
            _, sub_metrics = basic_metrics0(
                mkdf=sub_df,
                strategy_name=strategy_name,
                fees=fees,
                rf=rf,
                jz_mode=jz_mode,
                time_start=time_start
            )
            all_metrics.update(sub_metrics)

    return jz,all_metrics

# ==================== 核心功能 ====================

def generate_param_values(start: int, end: int, step: int) -> List[int]:
    """
    生成参数值列表

    Args:
        start: 起始值
        end: 结束值（包含）
        step: 步长

    Returns:
        List[int]: 参数值列表
    """
    return list(np.arange(start, end + 1*step, step))


def test_single_filter(
    market_df: pd.DataFrame,
    filter_func,
    filter_name: str,
    filter_params: Dict[str, Any],
    backtest_config: Dict = None,
) -> Dict[str, Any]:
    """
    测试单个 filter 函数的分类效果

    Args:
        market_df: 市场数据
        filter_func: filter 函数
        filter_name: 函数名
        filter_params: 参数字典
        backtest_config: 回测配置

    Returns:
        Dict: 回测指标
    """
    if backtest_config is None:
        backtest_config = {}
    backtest_config.setdefault('pos_mode', 1)
    try:
        # 调用 filter 函数
        filter_result = filter_func(market_df, **filter_params)

        if backtest_config['pos_mode'] == 1:
            position = np.where(filter_result, 1, 0)
        if backtest_config['pos_mode'] == -1:
            position = np.where(filter_result, 0, -1)
        if backtest_config['pos_mode'] == 9:
            position = np.where(filter_result, 1, -1)
        if backtest_config['pos_mode'] == -9:
            position = np.where(filter_result, -1, 1)

        position = np.roll(position, 1)
        position[0] = 0

        # 准备回测据
        mkdf = market_df.copy()
        mkdf["pos"] = position


        # mkdf .loc[ mkdf['pos'].diff()!=0,'s'] = mkdf['pos']
        # mkdf['s20'] = mkdf['s'].shift(20)
        # mkdf.loc[~mkdf['s20'].isna() ,'s'] = 0
        # mkdf["pos"] = mkdf["s"] .ffill().fillna(0)


        mkdf = mkdf[["datetime", "open", "high", "low", "close", "volume", "pos"]].copy()

        # 执行回测
        jz, metrics = basic_metrics(
                                    mkdf=mkdf,
                                    strategy_name=filter_name,
                                    fees=backtest_config.get("fees", 0.0004),
                                    rf=backtest_config.get("rf", 0.00),
                                    jz_mode=backtest_config.get("jz_mode", "d"),
                                    time_start=None
                                )
        mkdf['jz'] = jz
        # plt.plot(jz)
        # plt.plot(position)
        # plt.show()

        # 添加 filter 信息
        metrics["filter_name"] = filter_name
        metrics["filter_params"] = str(filter_params)

        # 提取参数值（用于分析）
        for key, value in filter_params.items():
            metrics[f"param_{key}"] = value

        return metrics,mkdf

    except Exception as e:
        print(f"  ✗ {filter_name} {filter_params} 失败: {e}")
        return None


def test_filter_function(
    market_df: pd.DataFrame,
    filter_name: str,
    filter_params_config: Dict[str, List[int]],
    backtest_config: Dict = None,
) -> pd.DataFrame:
    """
    测试单个 filter 函数的参数组合

    Args:
        market_df: 市场数据
        filter_name: 函数名
        filter_params_config: 参数配置 {参数名: [起始, 结束, 步长]}
        backtest_config: 回测配置

    Returns:
        pd.DataFrame: 测试结果
    """
    if backtest_config is None:
        backtest_config = {}

    # 获取函数
    filter_func = globals().get(filter_name)
    if filter_func is None:
        print(f"✗ 未找到函数: {filter_name}")
        return pd.DataFrame()

    # 生成参数组合
    param_combinations = []
    param_names = list(filter_params_config.keys())

    for param_name in param_names:
        start, end, step = filter_params_config[param_name]
        param_combinations.append(generate_param_values(start, end, step))

    # 生成所有组合
    import itertools
    results = []
    total_tests = 1
    for values in param_combinations:
        total_tests *= len(values)

    print(f"\n测试函数: {filter_name}")
    print(f"参数配置: {filter_params_config}")
    print(f"预计测试数量: {total_tests}")
    print("-" * 60)

    test_count = 0
    # plt.subplot(2, 1, 1)  # 添加子图1
    # plt.plot(mkdf['jz'])
    # plt.plot(mkdf['close']/mkdf['close'][0], color='r')
    # plt.subplot(2, 1, 2)  # 添加子图1
    # plt.plot(mkdf["pos"], color='g')
    # plt.show()

    for combo in itertools.product(*param_combinations):
        test_count += 1
        # 构建参数字典
        params = dict(zip(param_names, combo))

        # 执行测试
        metrics,df0 = test_single_filter(
            market_df=market_df,
            filter_func=filter_func,
            filter_name=filter_name,
            filter_params=params,
            backtest_config=backtest_config,
        )
        plt.plot(df0['jz'])
        if metrics is not None:
            results.append(metrics)
            print(f"  [{test_count}/{total_tests}] {params} → 收益率: {metrics['total+总收益率%']:.2f}%")
    plt.plot(df0['close']/df0['close'][0], color='black')

    plt.show()

    return pd.DataFrame(results)


def analyze_results(results_df: pd.DataFrame, filter_name: str) -> None:
    """
    分析测试结果

    Args:
        results_df: 测试结果
        filter_name: 函数名
    """
    if results_df.empty:
        print("✗ 没有有效的测试结果")
        return

    print("\n" + "=" * 80)
    print(f"分析结果: {filter_name}")
    print("=" * 80)

    # 基本统计
    print(f"\n有效测试数量: {len(results_df)}")
    print(f"盈利测试数: {(results_df['total+总收益率%'] > 0).sum()}")
    print(f"盈利占比: {(results_df['total+总收益率%'] > 0).sum() / len(results_df) * 100:.1f}%")

    # 按收益率排序
    print("\n" + "-" * 80)
    print("TOP 10 - 总收益率%")
    print("-" * 80)
    top_return = results_df.nlargest(10, 'total+总收益率%')
    print(top_return[['filter_params', 'total+总收益率%', 'total+年化收益率%', 'total+最大回撤%', 'total+sharpe比率']].to_string(index=False))

    # 按Sharpe排序
    print("\n" + "-" * 80)
    print("TOP 10 - Sharpe比率")
    print("-" * 80)
    top_sharpe = results_df.nlargest(10, 'total+sharpe比率')
    print(top_sharpe[['filter_params', 'total+总收益率%', 'total+sharpe比率', 'total+sortino比率', 'total+calmar比率']].to_string(index=False))

    # 按回撤排序（越小越好）
    print("\n" + "-" * 80)
    print("TOP 10 - 最大回撤% (最小)")
    print("-" * 80)
    low_drawdown = results_df.nsmallest(10, 'total+最大回撤%')
    print(low_drawdown[['filter_params', 'total+总收益率%', 'total+最大回撤%', 'total+calmar比率']].to_string(index=False))

    # 参数效果分析
    if 'param_timeperiod' in results_df.columns:
        print("\n" + "-" * 80)
        print("时间周期效果分析")
        print("-" * 80)
        period_stats = results_df.groupby('param_timeperiod').agg({
            'total+总收益率%': ['mean', 'std', 'min', 'max'],
            'total+sharpe比率': 'mean',
            'total+最大回撤%': 'mean',
        })
        period_stats.columns = ['平均收益', '收益标准差', '最小收益', '最大收益', '平均Sharpe', '平均回撤']
        print(period_stats)


def save_results(
    results_df: pd.DataFrame,
    filter_name: str,
    output_dir: str,
    code_id: str = "BTC",
) -> None:
    """
    保存测试结果

    Args:
        results_df: 测试结果
        filter_name: 函数名
        output_dir: 输出目录
        code_id: 品种代码
    """
    os.makedirs(output_dir, exist_ok=True)

    # 保存完整结果
    file_path = os.path.join(output_dir, f"{code_id}_{filter_name}_classification.csv")
    results_df.to_csv(file_path, index=False, encoding='utf-8-sig')
    print(f"\n✓ 已保存结果: {file_path}")

    # 保存排序结果
    for metric, ascending in [('total+总收益率%', False), ('total+sharpe比率', False), ('total+最大回撤%', True)]:
        ranked = results_df.sort_values(by=metric, ascending=ascending)
        safe_metric = metric.replace("%", "pct").replace("/", "_")
        rank_path = os.path.join(output_dir, f"{code_id}_{filter_name}_rank_by_{safe_metric}.csv")
        ranked.to_csv(rank_path, index=False, encoding='utf-8-sig')
        print(f"✓ 已保存排序: {rank_path}")


# ==================== 主程序 ====================

def main():
    """主程序入口"""

    # 测试时间范围
    TEST_START = datetime(2026, 1, 1)
    TEST_END = datetime(2026, 5, 31)


    TEST_FILTERS = {
        # 'roc_higher0': {
        #     'timeperiod': [10, 280, 10] , # 测试 20, 40, 60, ..., 280
        #     # 'N3': [0, 1, 1]  # 测试 20, 40, 60, ..., 280
        # },
        # 'tsi_higher_signal': {
        #                     'firstperiod': [40, 95, 5],  # 测试 20, 40, 60, ..., 280
        #                     'secondperiod': [40, 95, 5],
        #                     'signalperiod': [20, 60, 10]
        #                 },
        'supertrend_long_period': {
            'timeperiod': [20, 280, 10] , # 测试 20, 40, 60, ..., 280
            "multiplier" : [1.5, 5, 0.5]
        },
    }

    # 输出目录
    OUTPUT_DIR = r"D:\jason_src\策略多因子系统\filter_test_results"

    # 选择测试品种
    code_id = "GCmain"  # 可修改为 "ETH"
    # 回测配置
    BACKTEST_CONFIG = {
        "fees": 0.0004,
        "rf": 0.00,
        "jz_mode": "f",
        'pos_mode': 9,
    }
    print("=" * 80)
    print("Filter 函数分类效果测试")
    print("=" * 80)
    print(f"品种: {code_id}")
    print(f"时间: {TEST_START} 至 {TEST_END}")
    print(f"回测配置: {BACKTEST_CONFIG}")
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

    # 2. 遍历测试配置
    all_results = []

    for filter_name, filter_params_config in TEST_FILTERS.items():
        # 3. 测试单个函数
        print(f"\n[2/4] 测试函数: {filter_name}")
        results_df = test_filter_function(
            market_df=market_df,
            filter_name=filter_name,
            filter_params_config=filter_params_config,
            backtest_config=BACKTEST_CONFIG,
        )

        # results_df = results_df.sort_values(by='total+总收益率%', ascending=1)
        #
        # print(results_df)
        results_df0 = results_df[
            (results_df['total+总收益率%'] > results_df['total+总收益率%'].quantile(0.9)) | (results_df['total+sharpe比率'] > results_df['total+sharpe比率'].quantile(0.9))].reset_index(drop=1)
        filter_params_keys = list(filter_params_config.keys())
        param_column = f"param_{filter_params_keys[0]}"
        results_df00 = results_df0.groupby([param_column]).apply(lambda v: v[(v['total+总收益率%'] == v['total+总收益率%'].max()) | (v['2026-05-01+总收益率%'] == v['2026-05-01+总收益率%'].max())])
        results_df00 = results_df00.sort_values(by='total+总收益率%', ascending=1).tail(5)
        print(results_df00)

        if not results_df.empty:
            all_results.append(results_df00)


            # # 4. 分析结果
            # analyze_results(results_df, filter_name)

            # exit()
            # 5. 保存结果
            save_results(results_df00, filter_name, OUTPUT_DIR, code_id)

    # 汇总所有结果
    if all_results:
        combined_df = pd.concat(all_results, ignore_index=True)

        print("\n" + "=" * 80)
        print("汇总分析")
        print("=" * 80)

        # 保存汇总结果
        summary_path = os.path.join(OUTPUT_DIR, f"{code_id}_all_filters_summary.csv")
        combined_df.to_csv(summary_path, index=False, encoding='utf-8-sig')
        print(f"✓ 已保存汇总: {summary_path}")

        # 跨函数对比
        if len(all_results) > 1:
            print("\n" + "-" * 80)
            print("各函数最佳表现对比")
            print("-" * 80)
            best_by_func = combined_df.loc[combined_df.groupby('filter_name')['total+总收益率%'].idxmax()]
            print(best_by_func[['filter_name', 'filter_params', 'total+总收益率%', 'total+sharpe比率', 'total+最大回撤%']].to_string(index=False))

    print("\n" + "=" * 80)
    print("测试完成！")


if __name__ == "__main__":



    main()
