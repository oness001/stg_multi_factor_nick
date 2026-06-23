

import os
import warnings
from datetime import datetime
from typing import Dict, Tuple

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

matplotlib.use('tkAgg')
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)


# ==================== 默认回测配置 ====================
DEFAULT_BACKTEST_CONFIG = {
    "ignore_new_entry": True,       # True: 持仓时不更新出场条件；False: 持仓时也更新出场条件
    "transaction_cost": 0.0004,     # 单边交易成本（0.0004 = 万四，即0.04%）
    "direction_long": True,         # True: 做多；False: 做空
    "resample_rule": "1MS",         # 重采样规则：1MS = 按月重采样（用于计算月度指标）
}


# ==================== 1. 资金净值计算 ====================
def pos_2_zjjz(df, long_rate=1, short_rate=1, open_p_col="open", close_p_col="close",
               pos_col="pos", fees=0.001, jz_mode='d'):
    """
    将持仓转化为资金净值

    参数:
        df          : 含 pos/open/close/candle_begin_time 列的 DataFrame
        long_rate   : 多头仓位倍率
        short_rate  : 空头仓位倍率
        open_p_col  : 开盘价列名
        close_p_col : 收盘价列名
        pos_col     : 持仓列名
        fees        : 单边手续费率
        jz_mode     : 'd' 单利净值, 'f' 复利净值
    返回:
        包含 资金净值/资金净值_nofee/资金净值(单利)/每笔盈亏/fl_jz 等列的 DataFrame
    """

    def cal_jz_with_pos(df, pos_col, open_p_col, close_p_col, time_col, fees=0.001, jz_mode='d'):
        # 开仓 / 平仓标记
        open_pos_con = (df[pos_col] != df[pos_col].shift(1))
        close_pos_con = (df[pos_col] != df[pos_col].shift(-1))

        # 信号计算
        df['signal'] = np.nan
        df['pos'] = df[pos_col]
        df.loc[close_pos_con, 'signal'] = df['pos'].shift(-1)

        # 手续费
        df["fees"] = 0.0
        df.loc[open_pos_con, "fees"] = fees * df["pos"].abs()
        df.loc[close_pos_con, "fees"] = fees * df["pos"].abs()
        df["fees"] = df["fees"].fillna(0.0)

        # 开仓价 / 时间（向前填充）
        df.loc[open_pos_con, 'open_p'] = df[open_p_col]
        df.loc[open_pos_con, 'open_time'] = df[time_col]
        df['open_p'] = df['open_p'].ffill()
        df['open_time'] = df['open_time'].ffill()

        # ---- 复利净值 ----
        df["per_资金变化率"] = df[close_p_col].pct_change(1) * df['pos']
        df.loc[open_pos_con, "per_资金变化率"] = df['pos'] * (df[close_p_col] / df[open_p_col] - 1)
        df.loc[df["pos"] == 0, "per_资金变化率"] = 0
        df["per_资金变化率"] = df["per_资金变化率"].fillna(0)
        df['资金净值_nofee'] = (df["per_资金变化率"] + 1).cumprod()
        df['资金净值f'] = (df["per_资金变化率"] + 1 - df["fees"].abs()).cumprod()

        # ---- 单利净值 ----
        df.loc[df["pos"] != 0, "per_开仓累计资金率"] = (df[close_p_col] / df['open_p'] - 1) * df['pos']
        df.loc[df["pos"] == 0, "per_开仓累计资金率"] = 0
        df["per_持仓资金变化"] = df['per_开仓累计资金率'].diff(1)
        df.loc[df["pos"] == 0, "per_持仓资金变化"] = 0
        df.loc[open_pos_con, "per_持仓资金变化"] = df["per_开仓累计资金率"]
        df['资金净值d'] = (df['per_持仓资金变化'].cumsum() - df["fees"].cumsum() + 1).ffill().fillna(1)

        # ---- 每笔盈亏 ----
        df['每笔盈亏'] = np.nan
        df.loc[close_pos_con, "每笔盈亏"] = df["per_开仓累计资金率"] - 2 * fees * df["pos"].abs()
        df['fl_jz'] = (df['每笔盈亏'].fillna(0) + 1).cumprod()
        df['资金净值(单利)'] = (df['每笔盈亏'].cumsum() + 1).ffill().fillna(1)

        # 按 jz_mode 选择净值
        if jz_mode == 'f':
            df['资金净值'] = df['资金净值f']
        else:  # 'd' 单利
            df['资金净值'] = df['资金净值d']

        # 清理中间列
        for col in ['fees', 'per_开仓累计资金率', 'per_资金变化率', 'per_持仓资金变化', '资金净值f', '资金净值d']:
            if col in df.columns:
                del df[col]

        return df

    df0 = df.copy()
    df0.loc[df0.index[0], "pos"] = 0
    df0.loc[df0.index[-1], "pos"] = 0
    df0.loc[df0["pos"] > 0, "pos"] = df0["pos"] * long_rate
    df0.loc[df0["pos"] < 0, "pos"] = -1 * abs(df0["pos"]) * short_rate
    time_col = 'candle_begin_time'
    df0 = cal_jz_with_pos(df0, pos_col, open_p_col, close_p_col, time_col, fees=fees, jz_mode=jz_mode)

    return df0

# ==================== 1. 资金净值计算 ====================
def pos_2_zjjz(df, long_rate=1, short_rate=1, open_p_col="open", close_p_col="close",
               pos_col="pos", fees=0.001, jz_mode='d'):

    def cal_jz_with_pos(df, pos_col, open_p_col, close_p_col, fees=0.001, jz_mode='d'):

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
            pos_series = df[pos_col]
            close_series = df[close_p_col]
            open_series = df[open_p_col]
            index_series = df.index

            open_pos_con = (pos_series != pos_series.shift(1)) & (pos_series != 0)
            close_pos_con = (pos_series != pos_series.shift(-1)) & (pos_series != 0)
            trans_pos_con1 = (pos_series != pos_series.shift(1))
            # ==================== 基础收益率计算 ====================
            # 交易成本
            fees_series = fees * (open_pos_con.astype(int) + close_pos_con.astype(int)) * pos_series.abs()

            open_p_series = pd.Series(np.where(open_pos_con, open_series, np.nan), index=index_series).ffill()
            per_cum_jz_series = (close_series / open_p_series - 1) * pos_series

            if jz_mode=='f':
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

            per_trade_series = np.zeros(len(per_cum_jz_series))*np.nan
            per_trade_series[close_pos_con] = per_cum_jz_series-fees_series
            df['资金净值'] = jz_series
            df['每笔盈亏'] = per_trade_series
            return df

    df0 = df.copy()
    df0.loc[df0.index[0], "pos"] = 0
    df0.loc[df0.index[-1], "pos"] = 0
    df0.loc[df0["pos"] > 0, "pos"] = df0["pos"] * long_rate
    df0.loc[df0["pos"] < 0, "pos"] = -1 * abs(df0["pos"]) * short_rate
    df0 = cal_jz_with_pos(df0, pos_col, open_p_col, close_p_col,  fees=fees, jz_mode=jz_mode)

    return df0


# ==================== 2. 策略绩效评估（含交易详情） ====================
def strategies_evaluate_period_diy(df, jz_col="", tj_invs=["3MS"], flag_id='', trade_info=True):
    """
    分段评估策略绩效（含交易详情统计）

    参数:
        df          : 含 jz_col / candle_begin_time / pos / 每笔盈亏 等列的 DataFrame
        jz_col      : 资金净值列名
        tj_invs     : 分段重采样规则列表，如 ["3MS", "all"]
        flag_id     : 结果前缀标识
        trade_info  : 是否计算交易详情（盈亏比、连续盈亏等）
    返回:
        绩效指标字典
    """

    def get_res(res, flag='all'):
        return {flag + k: round(float(v), 3) if isinstance(v, (int, float)) else v
                for k, v in res.items()}

    def strategies_evaluate_new(df0, trade_info=True):
        """计算策略绩效指标"""
        result = {}
        df0 = df0.reset_index(drop=True)

        df0['open_time'] = pd.to_datetime(df0['open_time'], utc=True)
        df0["candle_begin_time"] = pd.to_datetime(df0["candle_begin_time"], utc=True)
        interval_days = (df0['candle_begin_time'].iloc[-1] - df0['candle_begin_time'].iloc[-2]).total_seconds() / (24 * 3600)
        annual_factor = 365 / interval_days
        df0['trade_hour'] = (df0['candle_begin_time'] - df0['open_time']).apply(lambda x: x.total_seconds() / 3600)
        all_days = (df0['candle_begin_time'].iloc[-1] - df0['candle_begin_time'].iloc[0]).total_seconds() / (24 * 3600)
        all_days = 1 if all_days <= 1 else all_days

        df0["资金净值"] /= df0["资金净值"].iloc[0]
        end_rtn = df0["资金净值"].iloc[-1] - 1
        year_ret = df0["资金净值"].iloc[-1] ** (365 / all_days) - 1
        month_ret = df0["资金净值"].iloc[-1] ** (30 / all_days) - 1
        df0["回撤净值%"] = ((df0["资金净值"].cummax() - df0["资金净值"]) / df0["资金净值"].cummax())
        mmd = df0["回撤净值%"].max()

        result["all_days"] = int(all_days)
        result["start_time"] = df0['candle_begin_time'].iloc[0].strftime('%Y-%m-%d')
        result["end_time"] = df0['candle_begin_time'].iloc[-1].strftime('%Y-%m-%d')
        result["复利收益率%"] = end_rtn * 100
        result["年化收益率%"] = year_ret * 100
        result["mmd%"] = mmd * 100
        result["月化收益率%"] = month_ret * 100

        pct_d = df0["资金净值"].pct_change(1, fill_method=None)
        bdl = np.nanstd(pct_d)
        bdl_dn = np.nanstd(pct_d[pct_d < 0])
        ret_d = np.nanmean(pct_d)
        sharp_ratio = (ret_d / bdl) * (annual_factor ** 0.5) if bdl > 0 else 0
        stn_ratio = (ret_d / bdl_dn) * (annual_factor ** 0.5) if bdl_dn > 0 else 0
        year_vol = bdl * (annual_factor ** 0.5)

        result["年化波动率%"] = year_vol * 100
        result["卡玛比_d"] = year_ret / mmd if mmd > 0 else 0
        result["夏普_d"] = sharp_ratio
        result["索提诺_d"] = stn_ratio

        con_trade = (df0["pos"].shift(1) == 0) & (df0["pos"] != 0)
        trade_count = df0[con_trade].shape[0]
        sl = df0[df0[jz_col].diff() > 0].shape[0] / df0[jz_col].shape[0] if df0[jz_col].shape[0] > 0 else 0
        result["交易次数"] = trade_count
        result["胜率"] = sl * 100

        if trade_info:
            try:
                trade_log = (~df0['每笔盈亏'].isnull()) & (df0["pos"] != 0)
                tradetime_df = df0[trade_log]['trade_hour']
                hour_sum = np.nansum(tradetime_df)
                pnl_df = df0[trade_log]['每笔盈亏']
                trade_count = pnl_df.count()
                trade_sl = 100 * pnl_df[pnl_df >= 0].count() / trade_count if trade_count > 0 else 0
                trade_pl_ratio = pnl_df[pnl_df >= 0].sum() / abs(pnl_df[pnl_df < 0].sum()) if abs(
                    pnl_df[pnl_df < 0].sum()) > 0 else 99
                pnl_df0 = df0[trade_log][['每笔盈亏', 'open_time', "pos"]]
                pnl_df0["fx"] = np.sign(pnl_df0['每笔盈亏'])
                pnl_df0.loc[pnl_df0["fx"] != pnl_df0["fx"].shift(), 'bt_time'] = pnl_df0['open_time']
                pnl_df0['bt_time'] = pnl_df0['bt_time'].ffill()
                trade00 = pnl_df0.groupby(['bt_time'])[["fx", '每笔盈亏']].apply(np.sum)
                trade00 = trade00.sort_values(["fx", '每笔盈亏'], ascending=True)
                if not trade00.empty:
                    mul_loss_st = trade00.index[0]
                    mul_loss_count = trade00.iloc[0]['fx']
                    mul_loss_sum = trade00.iloc[0]['每笔盈亏']
                    mul_profit_count = trade00.iloc[-1]['fx']
                    mul_profit_sum = trade00.iloc[-1]['每笔盈亏']
                else:
                    mul_loss_st = '00:00:00'
                    mul_loss_count = mul_loss_sum = mul_profit_count = mul_profit_sum = 0
                result["交易次数"] = trade_count
                result["胜率"] = trade_sl
                result["盈亏比"] = trade_pl_ratio
                result["连续盈利次数"] = mul_profit_count
                result["连续盈利%"] = 100 * mul_profit_sum
                result["连续亏损次数"] = mul_loss_count
                result["连续亏损%"] = 100 * mul_loss_sum
                result["最大连亏亏损开始"] = mul_loss_st
                result["每笔持仓时间hour"] = hour_sum / trade_count if trade_count > 0 else 0
                result["日均交易次数"] = trade_count / all_days if all_days > 0 else 0
                result["月均交易次数"] = 30 * (trade_count / all_days) if all_days > 0 else 0
            except Exception:
                pass
        return result

    df[jz_col] = df[jz_col].ffill().bfill()
    tj_res = {'id': flag_id}
    for tjinv0 in tj_invs:
        format0 = "%Y" if "Y" in tjinv0 else "%Y-%m-%d"
        if "all" in tjinv0:
            res = strategies_evaluate_new(df, trade_info)
            tj_res.update(get_res(res, ""))
            continue
        groups = list(df.resample(rule=tjinv0, on="candle_begin_time", label='left', closed='left'))
        for k, v in reversed(groups):
            if v.empty or v.shape[0] < 2:
                continue
            df0 = v.reset_index(drop=True)
            df0[jz_col] = df0[jz_col] / df0[jz_col].iloc[0]
            res = strategies_evaluate_new(df0, trade_info)
            f0 = pd.to_datetime(k, format="%Y-%m-%d", utc=True).strftime(format0) + "+"
            tj_res.update(get_res(res, f0))
    return tj_res


# ==================== 3. 策略绩效评估（简洁版，无交易详情） ====================
def all_evaluate_period_diy(df, jz_col="", tj_invs=["3MS"], flag_id='', trade_info=True):
    """
    分段评估策略绩效（简洁版，仅含基础指标）

    参数同 strategies_evaluate_period_diy
    返回:
        绩效指标字典（不含交易详情）
    """
    df['资金净值'] = df[jz_col]

    def get_res(res, flag='all'):
        return {flag + k: round(float(v), 3) if isinstance(v, (int, float)) else v
                for k, v in res.items()}

    def strategies_evaluate_new(df0, trade_info=True):
        result = {}
        df0 = df0.reset_index(drop=True)
        df0["candle_begin_time"] = pd.to_datetime(df0["candle_begin_time"], utc=True)
        interval_days = (df0['candle_begin_time'].iloc[-1] - df0['candle_begin_time'].iloc[-2]).total_seconds() / (24 * 3600)
        annual_factor = 365 / interval_days
        all_days = (df0['candle_begin_time'].iloc[-1] - df0['candle_begin_time'].iloc[0]).total_seconds() / (24 * 3600)
        all_days = 1 if all_days <= 1 else all_days

        df0["资金净值"] /= df0["资金净值"].iloc[0]
        end_rtn = df0["资金净值"].iloc[-1] - 1
        year_ret = df0["资金净值"].iloc[-1] ** (365 / all_days) - 1
        month_ret = df0["资金净值"].iloc[-1] ** (30 / all_days) - 1
        df0["回撤净值%"] = ((df0["资金净值"].cummax() - df0["资金净值"]) / df0["资金净值"].cummax())
        mmd = df0["回撤净值%"].max()

        result["all_days"] = int(all_days)
        result["start_time"] = df0['candle_begin_time'].iloc[0].strftime('%Y-%m-%d')
        result["end_time"] = df0['candle_begin_time'].iloc[-1].strftime('%Y-%m-%d')
        result["复利收益率%"] = end_rtn * 100
        result["年化收益率%"] = year_ret * 100
        result["mmd%"] = mmd * 100
        result["月化收益率%"] = month_ret * 100

        pct_d = df0["资金净值"].pct_change(1, fill_method=None)
        bdl = np.nanstd(pct_d)
        bdl_dn = np.nanstd(pct_d[pct_d < 0])
        ret_d = np.nanmean(pct_d)
        sharp_ratio = (ret_d / bdl) * (annual_factor ** 0.5) if bdl > 0 else 0
        stn_ratio = (ret_d / bdl_dn) * (annual_factor ** 0.5) if bdl_dn > 0 else 0
        year_vol = bdl * (annual_factor ** 0.5)

        result["年化波动率%"] = year_vol * 100
        result["卡玛比_d"] = year_ret / mmd if mmd > 0 else 0
        result["夏普_d"] = sharp_ratio
        result["索提诺_d"] = stn_ratio

        con_trade = (df0["资金净值"].shift(1) != df0["资金净值"])
        df0 = df0[con_trade]
        sl = df0[(df0[jz_col].diff() > 0)].shape[0] / df0[jz_col].shape[0] if df0[jz_col].shape[0] > 0 else 0
        result["胜率"] = sl * 100
        return result

    df[jz_col] = df[jz_col].ffill().bfill()
    tj_res = {'id': flag_id}
    for tjinv0 in tj_invs:
        format0 = "%Y" if "Y" in tjinv0 else "%Y-%m-%d"
        if "all" in tjinv0:
            res = strategies_evaluate_new(df, trade_info)
            tj_res.update(get_res(res, ""))
            continue
        groups = list(df.resample(rule=tjinv0, on="candle_begin_time", label='left', closed='left'))
        for k, v in reversed(groups):
            if v.empty or v.shape[0] < 2:
                continue
            df0 = v.reset_index(drop=True)
            df0[jz_col] = df0[jz_col] / df0[jz_col].iloc[0]
            res = strategies_evaluate_new(df0, trade_info)
            f0 = pd.to_datetime(k, format="%Y-%m-%d", utc=True).strftime(format0) + "+"
            tj_res.update(get_res(res, f0))
    return tj_res


# ==================== 4. 基础回测指标计算 ====================
def basic_metrics(
        mkdf: pd.DataFrame,
        combo_name: str,
        time_start: pd.Timestamp = None
) -> Tuple[pd.Series, Dict[str, float]]:
    """
    计算基础回测指标（累计曲线、回撤、Sharpe/Sortino/Calmar、交易统计等）

    参数:
        mkdf        : 含 datetime/strategy_return/cost/position_diff_shift/position_shift 列的 DataFrame
        combo_name  : 策略名称
        time_start  : 分段起始时间，None 表示全时段
    返回:
        (cum_curve, metrics_dict)
    """
    rf = 0.02
    all_days = (mkdf["datetime"].iloc[-1] - mkdf["datetime"].iloc[0]).total_seconds() / (24 * 3600)
    delta_inv = (mkdf["datetime"].diff().mean().total_seconds()) / (24 * 3600)

    # 累计曲线
    cum_curve = (1 + mkdf["strategy_return"]).cumprod()
    year_ret = (cum_curve.iloc[-1]) ** (365 / all_days) - 1
    daily_std = np.nanstd(mkdf["strategy_return"]) * np.sqrt(1 / delta_inv)
    year_std = daily_std * (365 ** 0.5)

    # 最大回撤（正数）
    running_max = cum_curve.cummax()
    drawdown = (running_max - cum_curve) / running_max
    max_drawdown = drawdown.max()

    # 总收益率
    total_return = cum_curve.iloc[-1] - 1

    # sharpe 比率
    sharpe = (year_ret - rf) / year_std if year_std != 0 else 0.0

    # sortino 比率
    negative_returns = mkdf.loc[mkdf["strategy_return"] < 0, "strategy_return"]
    if len(negative_returns) == 0:
        sortino = 10
    else:
        year_downside_std = np.std(negative_returns) * np.sqrt(1 / delta_inv) * (365 ** 0.5)
        sortino = (year_ret - rf) / year_downside_std if year_downside_std != 0 else 0.0

    # Calmar 比率
    calmar = year_ret / max_drawdown if max_drawdown != 0 else 0.0

    # 总交易成本
    total_cost = mkdf["cost"].sum()

    # 交易次数与 bar 胜率
    num_trades = (mkdf["position_diff_shift"] < 0).sum()
    win_rate = (mkdf["strategy_return"] > 0).sum() / (mkdf["strategy_return"] != 0).sum() \
        if (mkdf["strategy_return"] != 0).sum() > 0 else 0.0

    # 单笔交易统计（向量加速运算）
    if num_trades == 0:
        ave_hold_bars = trade_win_rate = avg_win = avg_loss = profit_factor = 0.0
    else:
        entry_mask = mkdf["position_diff_shift"] > 0
        trade_id = entry_mask.cumsum()
        trade_id = trade_id.where(mkdf["position_shift"] > 0, 0)
        trade_ret_series = ((1 + mkdf["strategy_return"].where(trade_id > 0)).groupby(trade_id).prod() - 1)
        trade_ret_series = trade_ret_series.iloc[1:num_trades + 1]
        winning = trade_ret_series[trade_ret_series > 0]
        losing = trade_ret_series[trade_ret_series <= 0]
        trade_win_rate = len(winning) / num_trades
        avg_win = np.mean(winning) if len(winning) > 0 else 0.0
        avg_loss = np.mean(losing) if len(losing) > 0 else 0.0
        profit_factor = -avg_win / avg_loss if avg_loss != 0 else 10
        hold_bars_per_trade = (trade_id > 0).groupby(trade_id).sum()
        hold_bars_per_trade = hold_bars_per_trade.iloc[1:num_trades + 1]
        ave_hold_bars = np.mean(hold_bars_per_trade) * delta_inv

    # 组装结果
    metrics = {
        "总收益率%": float(round(total_return * 100, 3)),
        "年化收益率%": float(round(year_ret * 100, 3)),
        "最大回撤%": float(round(max_drawdown * 100, 3)),
        "sharpe比率": float(round(sharpe, 3)),
        "calmar比率": float(round(calmar, 3)),
        "交易次数": float(num_trades),
        "交易胜率%": float(round(trade_win_rate * 100, 3)),
        "盈亏比": float(round(profit_factor, 3)),
        "bar胜率%": float(round(win_rate * 100, 3)),
        "均持天数": float(round(ave_hold_bars, 3)),
        "总交易成本%": float(round(total_cost * 100, 3)),
        "sortino比率": float(round(sortino, 3)),
        "年化波动率%": float(round(year_std * 100, 3)),
        "日波动率%": float(round(daily_std * 100, 3)),
    }
    if time_start is None:
        metrics = {f"total+{k}": v for k, v in metrics.items()}
        metrics = {**{"开始时间": mkdf["datetime"].iloc[0], "结束时间": mkdf["datetime"].iloc[-1]},
                   **metrics, **{"策略名称": combo_name}}
    else:
        metrics = {f"{time_start:%Y-%m-%d}+{k}": v for k, v in metrics.items()}

    return cum_curve, metrics


def compute_backtest_metrics(
        market_df: pd.DataFrame,
        transaction_cost: float,
        direction_long: bool,
        combo_name: str,
        position_series: pd.Series,
        resample_rule: str = "1MS"
) -> Tuple[pd.Series, Dict[str, float]]:
    """
    根据持仓序列 position_series 计算完整回测指标（假设初始金额为 1）

    参数:
        market_df       : 行情数据（需含 open/close/datetime 列）
        transaction_cost: 单边交易成本
        direction_long  : 交易方向（True=做多）
        combo_name      : 策略名称
        position_series : 0/1 持仓序列
        resample_rule   : 分段重采样规则
    返回:
        (cum_curve, metrics_dict)
    """
    if 'close' not in market_df.columns or 'open' not in market_df.columns:
        raise ValueError("market_df 必须包含 'open' 和 'close' 列")

    mk_df = market_df.copy()
    mk_df["position"] = position_series

    # 基础收益率与成本计算
    price_change = mk_df['close'].pct_change().fillna(0)
    price_change_o = (mk_df['close'] / mk_df['open'] - 1).fillna(0)

    mk_df["position_shift"] = mk_df["position"].shift(1).fillna(0)
    mk_df["position_diff"] = mk_df["position"].diff().fillna(0)
    mk_df["position_diff_shift"] = mk_df["position_diff"].shift(1).fillna(0)

    mk_df["cost"] = 0.0
    mk_df.loc[mk_df["position_diff_shift"] > 0, "cost"] += transaction_cost * abs(mk_df["position_diff_shift"])
    mk_df.loc[mk_df["position_diff"] < 0, "cost"] += transaction_cost * abs(mk_df["position_diff"])

    price_change = price_change if direction_long else -price_change
    mk_df["strategy_return"] = mk_df["position_shift"] * price_change
    mk_df.loc[mk_df["position_diff_shift"] != 0, "strategy_return"] = mk_df["position_shift"] * price_change_o
    mk_df["strategy_return"] -= mk_df["cost"]

    # 全时段指标
    cum_curve, all_metrics = basic_metrics(mk_df, combo_name)
    # 分时段指标
    mk_df['datetime'] = pd.to_datetime(mk_df['datetime'])
    for time_start, sub_df in mk_df.resample(resample_rule, on='datetime', closed="left", label="left"):
        _, sub_metrics = basic_metrics(sub_df, combo_name, time_start)
        all_metrics.update(sub_metrics)

    return cum_curve, all_metrics


# ==================== 5. 信号函数 ====================
def simple_signal(df, params=[200, 0.5, 0.3]):
    """
    带 EMA 趋势过滤的信号函数

    参数:
        df    : 含 pos/close 列的 DataFrame
        params: [N1_rolling, upper_threshold, lower_threshold]
    逻辑:
        - 用 EMA(55) 判断趋势方向
        - z-score 标准化后 >= up → 做多(1)
        - z-score < dn 且 趋势向下 → 做空(-1)
        - z-score < dn 且 趋势向上 → 平仓(0)
    """
    try:
        import talib
    except ImportError:
        raise ImportError("simple_signal 需要 talib 库，请安装后使用")

    N1, N2, N3 = params
    df['pos'] = df['pos'].ffill().fillna(0)
    df['close'] = df['close'].ffill()
    df['trend'] = df['close'] > talib.EMA(df['close'], timeperiod=55)

    df['yz'] = df['pos']
    df['up'], df['dn'] = N2, N3
    me = df['yz'].rolling(N1, min_periods=1).mean()
    std0 = df['yz'].rolling(N1, min_periods=2).std()
    max_range = me + 3 * std0
    min_range = me - 3 * std0
    df.loc[df['yz'] < min_range, 'yz'] = min_range
    df.loc[df['yz'] > max_range, 'yz'] = max_range
    df['yz'] = (df['yz'] - me) / std0

    yz_pos = 'pos0'
    df.loc[(df['yz'] >= df['up']), yz_pos] = 1
    df.loc[(df['yz'] < df['dn']) & (df['trend'] == 1), yz_pos] = 0
    df.loc[(df['yz'] < df['dn']) & (df['trend'] == 0), yz_pos] = -1
    df['pos'] = df[yz_pos].ffill().fillna(0)
    df.loc[df["pos"] > 0, "pos"] = 1
    df.loc[df["pos"] <= 0, "pos"] = -1

    return df


def simple_signal_basic(df, params=[200, 0.5, 0.3]):
    """
    基础信号函数（无趋势过滤，含 3σ 截断）

    参数:
        df    : 含 pos/close 列的 DataFrame
        params: [N1_rolling, upper_threshold, lower_threshold]
    逻辑:
        - z-score 标准化后 >= up → 做多(1)
        - z-score < dn → 做空(-1)
    """
    N1, N2, N3 = params
    df['pos'] = df['pos'].ffill().fillna(0)
    df['close'] = df['close'].ffill()
    df['yz'] = df['pos']
    df['up'], df['dn'] = N2, N3
    me = df['yz'].rolling(N1, min_periods=1).mean()
    std0 = df['yz'].rolling(N1, min_periods=2).std()
    max_range = me + 3 * std0
    min_range = me - 3 * std0
    df.loc[df['yz'] < min_range, 'yz'] = min_range
    df.loc[df['yz'] > max_range, 'yz'] = max_range
    df['yz'] = (df['yz'] - me) / std0

    yz_pos = 'pos0'
    df.loc[(df['yz'] >= df['up']), yz_pos] = 1
    df.loc[(df['yz'] < df['dn']), yz_pos] = 0
    df['pos'] = df[yz_pos].ffill().fillna(0)
    df.loc[df["pos"] > 0, "pos"] = 1
    df.loc[df["pos"] <= 0, "pos"] = -1

    return df


def simple_signal_raw(df, params=[200, 0.5, 0.3]):
    """
    原始信号函数（无 3σ 截断，无趋势过滤）

    参数:
        df    : 含 pos/close 列的 DataFrame
        params: [N1_rolling, upper_threshold, lower_threshold]
    逻辑:
        - z-score 标准化后 >= up → 做多(1)
        - z-score < dn → 做空(-1)
        - 不做 3σ 截断处理
    """
    N1, N2, N3 = params
    df['pos'] = df['pos'].ffill().fillna(0)
    df['close'] = df['close'].ffill()
    df['yz'] = df['pos']
    df['up'], df['dn'] = N2, N3

    yz_pos = 'pos0'
    df.loc[(df['yz'] >= df['up']), yz_pos] = 1
    df.loc[(df['yz'] < df['dn']), yz_pos] = 0
    df['pos'] = df[yz_pos].ffill().fillna(0)
    df.loc[df["pos"] > 0, "pos"] = 1
    df.loc[df["pos"] <= 0, "pos"] = -1

    return df


# ==================== 6. 绘图辅助函数 ====================
def plot_backtest_result(axs, res, symbol, strategy_count=0, show_trade_info=False):
    """
    在右侧子图绘制回测结果指标

    参数:
        axs           : matplotlib 子图数组，axs[1] 用于绘制指标
        res           : 绩效指标字典
        symbol        : 品种代码
        strategy_count: 策略数量（0 则不显示）
        show_trade_info: 是否显示交易统计信息
    """
    axs[1].axis('off')
    y_pos = 0.95
    line_height = 0.08

    # 标题
    title = f"{symbol} 回测结果"
    if strategy_count > 0:
        title += f"：策略数量：{strategy_count}"
    axs[1].text(0.05, y_pos, title, transform=axs[1].transAxes,
                fontsize=12, fontweight='bold', verticalalignment='top')
    y_pos -= line_height * 1.2

    # 时间信息
    axs[1].text(0.05, y_pos, "─" * 5 + "总天数：" + f"{res.get('all_days', '')}" + "─" * 5,
                transform=axs[1].transAxes, fontsize=10, verticalalignment='top')
    y_pos -= line_height * 0.9
    axs[1].text(0.05, y_pos, rf"{res.get('start_time', '')} - {res.get('end_time', '')}",
                transform=axs[1].transAxes, fontsize=10, verticalalignment='top')
    y_pos -= line_height * 0.8

    # 收益率指标
    for label, key, fmt in [
        ("复利收益率:", '复利收益率%', '.2f'),
        ("年化收益率:", '年化收益率%', '.2f'),
    ]:
        val = res.get(key, 0)
        axs[1].text(0.05, y_pos, label, transform=axs[1].transAxes,
                    fontsize=12, verticalalignment='top')
        color = 'red' if val > 0 else 'green'
        axs[1].text(0.6, y_pos, f"{val:{fmt}}%", transform=axs[1].transAxes,
                    fontsize=12, verticalalignment='top', color=color)
        y_pos -= line_height

    # 最大回撤
    mmd_val = res.get('mmd%', 0)
    axs[1].text(0.05, y_pos, "最大回撤:", transform=axs[1].transAxes,
                fontsize=12, verticalalignment='top')
    axs[1].text(0.6, y_pos, f"{mmd_val:.3f}%", transform=axs[1].transAxes,
                fontsize=12, verticalalignment='top', color='green')
    y_pos -= line_height * 1.2

    # 分隔线
    axs[1].text(0.05, y_pos, "─" * 18, transform=axs[1].transAxes,
                fontsize=10, verticalalignment='top')
    y_pos -= line_height * 0.8

    # 风险调整收益指标
    for label, key, fmt in [
        ("夏普比率:", '夏普_d', '.3f'),
        ("索提诺:", '索提诺_d', '.3f'),
        ("卡玛比率:", '卡玛比_d', '.3f'),
    ]:
        val = res.get(key, 0)
        axs[1].text(0.05, y_pos, label, transform=axs[1].transAxes,
                    fontsize=12, verticalalignment='top')
        axs[1].text(0.6, y_pos, f"{val:{fmt}}", transform=axs[1].transAxes,
                    fontsize=12, verticalalignment='top')
        y_pos -= line_height

    # 交易统计
    if show_trade_info:
        y_pos -= line_height * 0.2
        axs[1].text(0.05, y_pos, "─" * 18, transform=axs[1].transAxes,
                    fontsize=10, verticalalignment='top')
        y_pos -= line_height * 0.8
        win_rate = res.get('胜率', 0)
        axs[1].text(0.05, y_pos, "胜率:", transform=axs[1].transAxes,
                    fontsize=12, verticalalignment='top')
        axs[1].text(0.6, y_pos, f"{win_rate:.2f}%", transform=axs[1].transAxes,
                    fontsize=12, verticalalignment='top')
    else:
        win_rate = res.get('胜率', 0)
        axs[1].text(0.05, y_pos, "胜率:", transform=axs[1].transAxes,
                    fontsize=12, verticalalignment='top')
        axs[1].text(0.6, y_pos, f"{win_rate:.2f}%", transform=axs[1].transAxes,
                    fontsize=12, verticalalignment='top')


def plot_strategy_curves(ax, market_df02, all_jz, symbol, x_tick_step=500):
    """
    在左侧子图绘制累计收益率曲线

    参数:
        ax            : matplotlib 子图
        market_df02   : 含 close/datetime 列的 DataFrame
        all_jz        : 策略净值字典 {name: cum_curve}
        symbol        : 品种代码
        x_tick_step   : x 轴刻度步长
    """
    for name, curve in all_jz.items():
        ax.plot(curve)
    ax.plot(market_df02['close'] / market_df02['close'].iloc[0], color='red', label="close")
    if 'jz_mean' in market_df02.columns:
        ax.plot(market_df02['jz_mean'], color='black', label="mean of all")
    ax.legend()
    ax.set_xlabel('时间')
    ax.set_ylabel('收益率')
    ax.set_title(f"{symbol} 累计收益率曲线")
    ax.set_xticks(market_df02.iloc[::x_tick_step].index,
                  market_df02['datetime'].iloc[::x_tick_step].astype(str).str[:10], rotation=25)
