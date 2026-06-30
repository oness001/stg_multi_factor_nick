"""
15分钟全品种多目标优化脚本

基于 优化回测.py 核心库，对多个品种进行批量优化
支持自定义指标过滤和权重配置

作者: NICK
日期: 2026-06-13
"""
import sys
import os
import warnings
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from orjson import orjson
import glob

matplotlib.use('Agg')
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)


# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 从优化回测.py导入核心库
from 优化回测 import  (
    run_optimization_for_single_code,
    run_optimization_batch,
    logger
)
logger.remove()
logger.add(sink=sys.stderr, level="INFO")
# ==================== 配置部分 ====================

def load_json(path):
    import orjson
    from pathlib import Path

    return orjson.loads(Path(path).read_bytes())


def get_fliter(filter_path):
    long_filter_list = {}
    short_filter_list = {}
    df = pd.read_csv(filter_path)
    con = df['direction'] == 'short'
    df0 = df[con]
    for k, v in df0.groupby(['window_label']):
        v = v.reset_index()
        short_filter_list[k[0]] = v['策略名称'].to_list()
    con = df['direction'] == 'long'
    df0 = df[con]
    for k, v in df0.groupby(['window_label']):
        v = v.reset_index()
        long_filter_list[k[0]] = v['策略名称'].to_list()

    return long_filter_list, short_filter_list, df['window_label'].unique()


def get_signal(signal_path):
    short_signal_list = {}
    long_signal_list = {}
    df = pd.read_csv(signal_path)
    con = df['direction'] == 'short'
    df0 = df[con]
    for k, v in df0.groupby(['window_label']):
        v = v.reset_index()
        short_signal_list[k[0]] = v['策略名称'].to_list()

    con = df['direction'] == 'long'
    df0 = df[con]
    for k, v in df0.groupby(['window_label']):
        v = v.reset_index()
        long_signal_list[k[0]] = v['策略名称'].to_list()
    return long_signal_list, short_signal_list, df['window_label'].unique()

if True:
    # 市场数据路径配置
    frequency = "15min"
    MK_DATA_PATHS = {
        "GCmain": rf"D:\贵金属_data\comex_GCmain_{frequency}.csv",
        "SImain": rf"D:\贵金属_data\comex_SImain_{frequency}.csv",
        "CLmain": rf"D:\贵金属_data\comex_CLmain_{frequency}.csv",
        "HGmain": rf"D:\贵金属_data\comex_HGmain_{frequency}.csv",
        "ZSmain": rf"D:\贵金属_data\comex_ZSmain_{frequency}.csv",
        "ZLmain": rf"D:\贵金属_data\comex_ZLmain_{frequency}.csv",
        "ZMmain": rf"D:\贵金属_data\comex_ZMmain_{frequency}.csv",
        "ZWmain": rf"D:\贵金属_data\comex_ZWmain_{frequency}.csv",
        "ZCmain": rf"D:\贵金属_data\comex_ZCmain_{frequency}.csv",
        "USDCNH": rf"D:\IB_CTA_SYS\ib_data_sv\USDCNH_15m_UTC.csv",
    }

    SAVE_RAW_FORCE_FILTER_CONFIG = {"total+总收益率%":10,
                                    'total+交易胜率%':45 ,
                                    'total+盈亏比':2,
                                    'total+交易次数':5,
                                    'total+最大回撤%':-10}


    SAVE_RAW_FORCE_FILTER_CONFIG0 = {"total+总收益率%":0,
                                    'total+交易胜率%':45 ,
                                    'total+盈亏比':1.5,
                                    'total+交易次数':5,
                                    'total+最大回撤%':-11}
    # 优化目标配置
    OBJECTIVES_CONFIG = [{"name": name, "direction": -1*np.sign(val)}
                         if  "最大回撤" not in  name
                         else {"name": name, "direction": abs(np.sign(val)) }
                         for name,val in SAVE_RAW_FORCE_FILTER_CONFIG.items()
                         ]


def stg_filter_main(symbol_id, output_dir, BACKTEST_CONFIG,
                    start_time = datetime(2025, 10, 1),
                    end_time = datetime(2026, 6, 30)):
    # ==================== 配置参数 ====================
    # 筛选参数
    PCT_N = 0.1  # 各维度筛选前/后10%
    Force_N = 200
    LIMIT_N = 80  # 最终数量限制500个
    LOW_CORR_N = 20  # 低相关性策略选50个
    LIMIT_CORR_VAL = 0.1  # 相关系数阈值0.5

    # 指标配置：列名 -> (方向, 权重)
    # 方向: 'positive'=越大越好, 'negative'=越小越好
    # 'total+bar胜率%': ('positive', 1),
    # 'total+交易次数': ('positive', 0.5),
    METRICS_CONFIG = {
        'total+总收益率%': ('positive', 3),
        'total+交易胜率%': ('positive', 2),
        'total+盈亏比': ('positive', 2),
        'total+sharpe比率': ('positive', 1.5),
        'total+calmar比率': ('positive', 2.5),

        'total+最大回撤%': ('negative', 4),
    }
    # positive / negative 区分 过滤种类。
    # 数值小于0 就是过滤百分位，大于零是正常数值过滤
    Force_CONFIG = {
        'total+calmar比率': ('positive', -0.3),  # calmar至少0.5
        'total+sharpe比率': ('positive', -0.3),  # sharpe至少1.0
        # 'total+年化收益率%': ('positive', -0.4),  # calmar至少0.5
        'total+总收益率%': ('positive', 15),  # 总收益率至少20%
        'total+交易次数': ('positive', 10),  # calmar至少0.5
        'total+交易胜率%': ('positive', 50),  # 交易胜率至少45%
        'total+最大回撤%': ('negative', 7),  # 最大回撤不超过30%
        'total+盈亏比': ('positive', 2),  # 盈亏比至少1.5
    }
    Force_CONFIG = {
        'total+总收益率%': ('positive', 10.5),  # 总收益率至少20%
        'total+交易次数': ('positive', 3),  # calmar至少0.5
        'total+calmar比率': ('positive', -0.5),  # calmar至少0.5
        'total+交易胜率%': ('positive', 50),  # 交易胜率至少45%
        'total+盈亏比': ('positive', 1.85),  # 盈亏比至少1.5
        'total+sharpe比率': ('positive', 2.5),  # sharpe至少1.0
        'total+最大回撤%': ('negative', 10),  # 最大回撤不超过30%
    }
    start = BACKTEST_CONFIG.get('start_date')
    end = BACKTEST_CONFIG.get('end_date')

    main(symbol_id, output_dir, METRICS_CONFIG, Force_CONFIG, PCT_N, Force_N, LIMIT_N, LOW_CORR_N, LIMIT_CORR_VAL, BACKTEST_CONFIG,start, end)


def main_all_in_one(Ns ,code_ids,BACKTEST_CONFIG,OPTIMIZATION_CONFIG,trailing_stg,run_l_s = [True,True],run_opt = True,run_opt_filter = True):
    n1 ,n2,n3 = Ns

    SAVE_DIR_PATH = os.path.join(os.path.dirname(__file__),rf'滚动信号结果')
    os.makedirs(SAVE_DIR_PATH, exist_ok=True)
    roll_signal_path = os.path.join(os.path.dirname(__file__),r'滚动测试信号')


    # exit()
    STRATEGY_PARAMS_CONFIG_long = {}
    STRATEGY_PARAMS_CONFIG_short = {}
    win_label = {}
    for symbol_id in code_ids:

        filter_path = rf"{roll_signal_path}\{symbol_id}_filters_20260101_20260701_rolling_3_1_全量滚动窗口筛选结果.csv"
        signal_path = rf"{roll_signal_path}\{symbol_id}_signals_20260101_20260701_rolling_3_1_全量滚动窗口筛选结果.csv"
        long_filter_list, short_filter_list, filter_window_labels = get_fliter(filter_path)
        long_signal_list, short_signal_list, signal_window_labels = get_signal(signal_path)
        win_label = set(filter_window_labels) & set(signal_window_labels)
        win_label = sorted(win_label, reverse=True)

        for winlabel0 in win_label:
                stg_cfg0 = [
                    {'name': 'EntryFilters', 'select_count': n1, 'combination': 'and', 'items': long_filter_list.get(winlabel0)},
                    {'name': 'EntrySignals', 'select_count': n2, 'combination': 'or', 'items': long_signal_list.get(winlabel0)},
                    {'name': 'ExitSignals', 'select_count': n3, 'combination': 'or', 'items': short_signal_list.get(winlabel0)+trailing_stg}
                ]
                STRATEGY_PARAMS_CONFIG_long = {symbol_id: stg_cfg0,**STRATEGY_PARAMS_CONFIG_long}
                stg_cfg0 = [
                    {'name': 'EntryFilters', 'select_count': n1, 'combination': 'and', 'items':short_filter_list.get(winlabel0)},
                    {'name': 'EntrySignals', 'select_count': n2, 'combination': 'or', 'items': short_signal_list.get(winlabel0) },
                    {'name': 'ExitSignals', 'select_count': n3, 'combination': 'or', 'items': long_signal_list.get(winlabel0) + trailing_stg}
                ]
                STRATEGY_PARAMS_CONFIG_short = {symbol_id: stg_cfg0, **STRATEGY_PARAMS_CONFIG_short}

    else:
        for winlabel0 in win_label[:]:

            output_dir_long = f"{SAVE_DIR_PATH}\\roll-{n1}_s-{n2}_e-{n3}_jzmode-{BACKTEST_CONFIG.get('jz_mode')}-{winlabel0}-long"
            os.makedirs(output_dir_long, exist_ok=True)
            output_dir_short = fr"{SAVE_DIR_PATH}\roll-{n1}_s-{n2}_e-{n3}_jzmode-{BACKTEST_CONFIG.get('jz_mode')}-{winlabel0}-short"
            os.makedirs(output_dir_short, exist_ok=True)

            st,et = winlabel0.split('_')
            st = pd.to_datetime(st)
            et = pd.to_datetime(et)

            BACKTEST_CONFIG['direction_long'] = True
            if run_opt and run_l_s[0]:
                run_optimization_batch( code_ids=code_ids,
                                    start=start,
                                    end=end,
                                    output_dir=output_dir_long,
                                    market_data_paths=MK_DATA_PATHS,
                                    strategy_config=STRATEGY_PARAMS_CONFIG_long,
                                    objectives_config=OBJECTIVES_CONFIG,
                                    backtest_config=BACKTEST_CONFIG,
                                    save_raw_force_filter_config = SAVE_RAW_FORCE_FILTER_CONFIG,
                                    population_size=OPTIMIZATION_CONFIG["population_size"],
                                    n_generations=OPTIMIZATION_CONFIG["n_generations"]  ,
                                    num_processes=10,
                                )
            if run_opt_filter and run_l_s[0]:
                for code_id in code_ids:
                    try:
                        stg_filter_main(code_id, output_dir_long,BACKTEST_CONFIG,st,et)
                    except Exception as e:
                        print(e)



            BACKTEST_CONFIG['direction_long'] = False
            if run_opt and run_l_s[1]:
                run_optimization_batch(code_ids=code_ids,
                                       start=start,
                                       end=end,
                                       output_dir=output_dir_short,
                                       market_data_paths=MK_DATA_PATHS,
                                       strategy_config=STRATEGY_PARAMS_CONFIG_short,
                                       objectives_config=OBJECTIVES_CONFIG,
                                       backtest_config=BACKTEST_CONFIG,
                                       save_raw_force_filter_config=SAVE_RAW_FORCE_FILTER_CONFIG,
                                       population_size=OPTIMIZATION_CONFIG["population_size"],
                                       n_generations=OPTIMIZATION_CONFIG["n_generations"],
                                       num_processes=10,
                                       )
            if run_opt_filter and run_l_s[1]:
                for code_id in code_ids:
                    try:

                        stg_filter_main(code_id, output_dir_short,BACKTEST_CONFIG,st,et)
                    except Exception as e:
                        print(e)

        return output_dir_long, output_dir_short

if __name__ == "__main__":
    from 策略筛选 import main
    # global PCT_N, Force_N, LIMIT_N, LOW_CORR_N, LIMIT_CORR_VAL, BACKTEST_CONFIG, METRICS_CONFIG, Force_CONFIG

    OPTIMIZATION_CONFIG = {"population_size": 4000,"n_generations": 500}
    start = datetime(2026, 2, 1)
    end = datetime(2026, 6, 30)
    BACKTEST_CONFIG = {
                        "direction_long": True,
                        "ignore_new_entry": True,
                        "transaction_cost": 0.0005,
                        "rf": 0.00,
                        "jz_mode": "d",
                        "resample_rule" : "",
                        "verbose" :1,
                        'mk_data_paths': MK_DATA_PATHS,
                        'start_date': start,
                        'end_date': end,
    }

    trailing_stg = ['trailing_stop^34^1.5', 'trailing_stop^34^2.5',
                    'trailing_stop^34^2.0', 'trailing_stop^34^3.0',
                    'trailing_stop^34^3.5', 'trailing_stop^34^4.0',
                    'trailing_stop^84^3.5', 'trailing_stop^84^4.0'
                    ]
    Ns = (3,3,2)

    for Ns in [(3,3,2),(4,2,2),(2,4,2),(2,2,3),(3,3,3)]:
        code_ids = ['GCmain', 'SImain',  'HGmain','CLmain', 'ZSmain', 'ZLmain', 'ZMmain', 'ZWmain', 'ZCmain'][:]
        run_l_s = [True, True]
        run_opt = False
        run_opt_filter = True
        output_dir_long, output_dir_short = main_all_in_one(Ns ,code_ids,BACKTEST_CONFIG,OPTIMIZATION_CONFIG,trailing_stg,run_l_s,run_opt,run_opt_filter)

