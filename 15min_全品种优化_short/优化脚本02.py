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

matplotlib.use('tkAgg')
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
if True:
    #  回测参数配置

    # 市场数据路径配置
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

    #  指标过滤配置（用于筛选优质策略）强制过滤
    metrics_map_1 = {
        "GCmain": [('total+calmar比率', 1), ('total+交易胜率%', 40), ('total+交易次数', 15), ('total+盈亏比', 1)],
        "SImain": [('total+calmar比率', 1), ('total+交易胜率%', 40), ('total+交易次数', 15), ('total+盈亏比', 1)],
        "CLmain": [('total+calmar比率', 1), ('total+交易胜率%', 40), ('total+交易次数', 15), ('total+盈亏比', 1)],
        "HGmain": [('total+calmar比率', 1), ('total+交易胜率%', 40), ('total+交易次数', 15), ('total+盈亏比', 1)],
        "ZSmain": [('total+calmar比率', 1), ('total+交易胜率%', 40), ('total+交易次数', 15), ('total+盈亏比', 1)],
        "ZLmain": [('total+calmar比率', 1), ('total+交易胜率%', 40), ('total+交易次数', 15), ('total+盈亏比', 1)],
        "ZMmain": [('total+calmar比率', 1), ('total+交易胜率%', 40), ('total+交易次数', 15), ('total+盈亏比', 1)],
        "ZWmain": [('total+calmar比率', 1), ('total+交易胜率%', 40), ('total+交易次数', 15), ('total+盈亏比', 1)],
        "ZRmain": [('total+calmar比率', 1), ('total+交易胜率%', 40), ('total+交易次数', 15), ('total+盈亏比', 1)],
        "ZCmain": [('total+calmar比率', 1), ('total+交易胜率%', 40), ('total+交易次数', 15), ('total+盈亏比', 1)],
    }

    # 时间周期配置
    period_list = [
        ("total", 0.5),           # 全周期，权重50%
        ("2026-03-01", 0.3),      # 3月，权重30%
        ("2026-04-01", 0.3),      # 4月，权重30%
        ("2026-05-01", 0.4),      # 5月，权重40%
    ]

    #  信号池配置
    study_signal_list = [
        ("filter_0_0",),     # 过滤器组
        ("entry_0_0",),      # 入场信号组
        ("exit_0",),         # 出场信号组1
        ("exit_1_0",),       # 出场信号组2
    ]

    # 每组需要选择的信号数量
    select_signal_dict = {
        "filter_0_0": 15,    # 从过滤器池中选择15个
        "entry_0_0": 15,     # 从入场信号池中选择15个
        "exit_0": 2,         # 从出场信号池1中选择2个
        "exit_1_0": 4,       # 从出场信号池2中选择4个
    }


    SAVE_RAW_FORCE_FILTER_CONFIG = {"total+总收益率%":15,
                                    'total+交易胜率%':48 ,
                                    'total+盈亏比':1.5,
                                    'total+交易次数':5,
                                    'total+最大回撤%':-12}
    # 优化目标配置
    OBJECTIVES_CONFIG = [{"name": name, "direction": -1*np.sign(val)}
                         if  "最大回撤" not in  name
                         else {"name": name, "direction": abs(np.sign(val)) }
                         for name,val in SAVE_RAW_FORCE_FILTER_CONFIG.items()
                         ]
if True == 0:
# 回测参数配置

    tp_sig = [
        "tp_high_2^16^1",
        "tp_high_2^24^1",
        "tp_high_2^34^1",

        "tp_high_2^16^0",
        "tp_high_2^24^0",
        "tp_high_2^34^0",

        "s_tp_high_1^15^0^0","s_tp_high_1^15^0^1","s_tp_high_1^15^0^2",
        "s_tp_high_1^34^0^0","s_tp_high_1^34^0^1","s_tp_high_1^34^0^2",

        "tp_low_1^15^0","tp_low_2^15^0", "s_tp_low_1^15^0^0","s_tp_low_1^15^0^1","s_tp_low_1^15^0^2",
        "tp_low_1^31^0","tp_low_2^31^0", "s_tp_low_1^31^0^0","s_tp_low_1^31^0^1","s_tp_low_1^31^0^2",]
    n1,n2,n3 = 2,2,2
    STRATEGY_PARAMS_CONFIG = dict(  GCmain=[
                                    {
                                    "name": "EntryFilters", "select_count": n1, 'combination': 'and',
                                    "items": ["_",
                                          "emacd_histogram_increase^144^288^144",
                                          "aroon_diff_higher0^21",
                                          "tsi_higher_signal^55^55^27",
                                          "price_higher_sma^233",
                                          "aroon_diff_higher0^144",
                                          "price_higher_sma^144",
                                          "atr_fast_lower_slow^144^288",
                                          "adx_plus_higher_minus^34",
                                          "rsi_fast_higher_slow^13^26",
                                          "emacd_higher_signal^89^178^89",
                                          "atr_fast_lower_slow^89^178",
                                          "aroon_diff_higher0^89",
                                          "tsi_higher_signal^89^89^44",
                                          "adx_plus_higher_minus^55",
                                          "roc_higher0^377"
                                          ],
                                    },
                                    {
                                    "name": "EntrySignals", "select_count": n2, 'combination': 'or',
                                    "items": [

                                             "aroon_diff_crossover0^34",
                                             "roc_crossover0^34",
                                             "bb_price_crossover_high_2^21^2.0",
                                             "roc_crossover0^21",
                                             "emacd_crossover_signal^34^68^34",
                                             "adx_plus_crossover_minus^21",
                                             "emacd_start_increase^55^110^55",
                                             "emacd_histogram_start_increase^55^110^55",
                                             "ema_fast_crossover_slow^13^26",
                                             "smi_k_crossover_d^34^10^10",
                                             "aroon_diff_crossover0^89",
                                             "adx_plus_crossover_minus^34",
                                             "adx_plus_crossover_minus^55",
                                             "adx_plus_crossover_minus^89",
                                             "kc_price_crossover_high_2^89^44^3.0"] + tp_sig,
                                    },
                                    {
                                    "name": "ExitSignals", "select_count": n3, 'combination': 'or',
                                    "items": [
                                    "trailing_stop^34^2.5",
                                    "trailing_stop^34^3.5",
                                    "smi_k_crossunder_d^21^6^6",
                                    "emacd_start_decrease^34^68^34",
                                    "emacd_crossunder_signal^8^16^8",
                                    "emacd_histogram_start_decrease^55^110^55"
                                    ],
                                    }
                                    ],
                                    SImain=[
                                    {'name': 'EntryFilters',
                                    'select_count': n1,
                                    'combination': 'and',
                                    'items': ['mass_lower1^21^21',
                                       'adx_lower_threshold^13^20',
                                       'adx_plus_higher_minus^13',
                                       'mass_lower1^55^55',
                                       'atr_fast_lower_slow^55^110',
                                       'aroon_diff_higher0^21',
                                       'tsi_higher_signal^55^55^27',
                                       'adx_plus_higher_minus^89',
                                       'price_higher_sma^233',
                                       'adx_lower_threshold^21^20',
                                       'mass_lower1^13^13',
                                       'emacd_higher_signal^233^466^233',
                                       'roc_higher0^233',
                                       'adx_plus_higher_minus^21',
                                       'emacd_histogram_increase^89^178^89']},
                                    {'name': 'EntrySignals',
                                    'select_count': n2,
                                    'combination': 'or',
                                    'items': ['emacd_crossover_signal^13^26^13',
                                       'kc_price_crossover_high_2^55^27^3.0',
                                       'aroon_diff_crossover0^233',
                                       'emacd_crossover_signal^21^42^21',
                                       'price_crossover_sma_2^89',
                                       'kc_price_crossover_high_2^34^17^2.5',
                                       'adx_plus_crossover_minus^21',
                                       'adx_plus_crossover_minus^55',
                                       'bb_price_crossover_high_2^21^2.0',
                                       'emacd_histogram_start_increase^144^288^144',
                                       'kc_price_crossover_high_2^144^72^3.0',
                                       'roc_crossover0^89',
                                       'bb_price_crossover_high_2^34^2.5',
                                       'roc_crossover0^55',
                                       'kc_price_crossover_high_2^13^6^1.5'] + tp_sig
                                    },
                                    {'name': 'ExitSignals',
                                    'select_count': n3,
                                    'combination': 'or',
                                    'items': ["trailing_stop^34^2.5",
                                       "trailing_stop^34^3.0",
                                       "roc_crossunder0^34",
                                       "emacd_histogram_start_decrease^89^178^89",
                                       "emacd_start_decrease^34^68^34",
                                       "rvi_crossunder_signal^144^41"]
                                    }],
                                    HGmain=[{'name': 'EntryFilters',
                                    'select_count': n1,
                                    'combination': 'and',
                                    'items': ['price_higher_sma^34',
                                           'emacd_histogram_increase^34^68^34',
                                           'skew_negative^377^EMA',
                                           'rsi_fast_higher_slow^13^26',
                                           'emacd_higher_signal^21^42^21',
                                           'price_higher_sma^21',
                                           'mass_lower1^13^13',
                                           'rsi_fast_higher_slow^55^110',
                                           'emacd_histogram_increase^55^110^55',
                                           'aroon_diff_higher0^21',
                                           'emacd_increase^34^68^34',
                                           'emacd_increase^55^110^55',
                                           'adx_plus_higher_minus^8',
                                           'mass_lower1^21^21',
                                           'emacd_higher_signal^233^466^233']},
                                    {'name': 'EntrySignals',
                                    'select_count': n2,
                                    'combination': 'or',
                                    'items': ['adx_plus_crossover_minus^13',
                                           'smi_k_crossover_d^55^16^16',
                                           'price_crossover_sma_2^34',
                                           'emacd_histogram_start_increase^55^110^55',
                                           'adx_plus_crossover_minus^8',
                                           'rvi_crossover_signal^377^108',
                                           'smi_k_crossover_d^34^10^10',
                                           'smi_k_crossover_d^21^6^6',
                                           'roc_crossover0^34',
                                           'emacd_crossover_signal^21^42^21',
                                           'ema_fast_crossover_slow^13^26',
                                           'adx_plus_crossover_minus^21',
                                           'smi_k_crossover_d^144^41^41',
                                           'emacd_crossover_signal^13^26^13',
                                           'emacd_crossover_signal^34^68^34'] + tp_sig},
                                    {'name': 'ExitSignals',
                                    'select_count': n3,
                                    'combination': 'or',
                                    'items': ["trailing_stop^34^3.5",
                                           "trailing_stop^34^3.0",
                                           "price_crossunder_sma_2^144",
                                           "adx_plus_crossunder_minus^55",
                                           "adx_plus_crossunder_minus^89",
                                           "roc_crossunder0^144"
                                           ]}],
                                    CLmain=[{'name': 'EntryFilters',
                                    'select_count': n1,
                                    'combination': 'and',
                                    'items': ['atr_fast_lower_slow^21^42',
                                           'price_higher_sma^89',
                                           'adx_lower_threshold^55^20',
                                           'ema_fast_higher_slow^34^68',
                                           'tsi_higher_signal^55^55^27',
                                           'atr_fast_lower_slow^55^110',
                                           'adx_plus_higher_minus^21',
                                           'mass_lower1^55^55',
                                           'adx_lower_threshold^21^20',
                                           'adx_lower_threshold^34^20',
                                           'mass_lower1^34^34',
                                           'atr_fast_lower_slow^34^68',
                                           'skew_negative^55^EMA',
                                           'skew_negative^89^EMA',
                                           'skew_negative^144^EMA']},
                                    {'name': 'EntrySignals',
                                    'select_count': n2,
                                    'combination': 'or',
                                    'items': ['adx_plus_crossover_minus^34',
                                           'adx_plus_crossover_minus^13',
                                           'smi_k_crossover_d^34^10^10',
                                           'aroon_diff_crossover0^21',
                                           'aroon_diff_crossover0^89',
                                           'adx_plus_crossover_minus^21',
                                           'emacd_histogram_start_increase^55^110^55',
                                           'kc_price_crossover_high_2^13^6^1.5',
                                           'roc_crossover0^89',
                                           'emacd_histogram_start_increase^21^42^21',
                                           'emacd_start_increase^21^42^21',
                                           'smi_k_crossover_d^13^4^4',
                                           'adx_plus_crossover_minus^8',
                                           'emacd_start_increase^5^10^5',
                                           'emacd_start_increase^34^68^34'] + tp_sig},
                                    {'name': 'ExitSignals',
                                    'select_count': n3,
                                    'combination': 'or',
                                    'items': ['aroon_diff_crossunder0^144',
                                           'emacd_start_decrease^144^288^144',
                                           'aroon_diff_crossunder0^55',
                                           'smi_k_crossunder_d^55^16^16',
                                           'trailing_stop^34^2.5',
                                           'trailing_stop^34^3.0']}],
                                    ZCmain=[{'name': 'EntryFilters',
                                    'select_count': n1,
                                    'combination': 'and',
                                    'items': ['rsi_fast_higher_slow^55^110',
                                           'emacd_histogram_increase^34^68^34',
                                           'emacd_increase^13^26^13',
                                           'rsi_fast_higher_slow^13^26',
                                           'kc_neutral^89^44^3.0',
                                           'adx_lower_threshold^13^20',
                                           'kc_neutral^144^72^3.5',
                                           'adx_plus_higher_minus^21',
                                           'rsi_fast_higher_slow^34^68',
                                           'emacd_higher_signal^34^68^34',
                                           'emacd_histogram_increase^89^178^89',
                                           'skew_negative^55^EMA',
                                           'emacd_histogram_increase^144^288^144',
                                           'tsi_higher_signal^89^89^44',
                                           'skew_negative^233^EMA']},
                                    {'name': 'EntrySignals',
                                    'select_count': n2,
                                    'combination': 'or',
                                    'items': ['emacd_histogram_start_increase^21^42^21',
                                           'rvi_crossover_signal^144^41',
                                           'emacd_start_increase^8^16^8',
                                           'ema_fast_crossover_slow^5^10',
                                           'emacd_crossover_signal^5^10^5',
                                           'rvi_crossover_signal^55^16',
                                           'roc_crossover0^13',
                                           'roc_crossover0^89',
                                           'emacd_start_increase^55^110^55',
                                           'emacd_crossover_signal^13^26^13',
                                           'rvi_crossover_signal^89^25',
                                           'emacd_start_increase^34^68^34',
                                           'ema_fast_crossover_slow^21^42',
                                           'emacd_histogram_start_increase^55^110^55',
                                           'roc_crossover0^144'] + tp_sig},
                                    {'name': 'ExitSignals',
                                    'select_count': n3,
                                    'combination': 'or',
                                    'items': ['kc_price_crossunder_high^89^44^3.0',
                                           'kc_price_crossunder_high^34^17^2.5',
                                           'kc_price_crossunder_high^21^10^2.0',
                                           'kc_price_crossunder_high^55^27^3.0',
                                           'trailing_stop^34^3.0',
                                           'trailing_stop^34^3.5']}],
                                    ZWmain=[{'name': 'EntryFilters',
                                    'select_count': n1,
                                    'combination': 'and',
                                    'items': ['adx_lower_threshold^8^20',
                                           'emacd_increase^55^110^55',
                                           'ema_fast_higher_slow^34^68',
                                           'ema_fast_higher_slow^21^42',
                                           'emacd_histogram_increase^377^754^377',
                                           'adx_plus_higher_minus^55',
                                           'aroon_diff_higher0^89',
                                           'emacd_histogram_increase^144^288^144',
                                           'rsi_fast_higher_slow^55^110',
                                           'adx_plus_higher_minus^34',
                                           'emacd_histogram_increase^233^466^233',
                                           'aroon_diff_higher0^55',
                                           'emacd_higher_signal^55^110^55',
                                           'emacd_higher_signal^89^178^89',
                                           'emacd_increase^144^288^144']},
                                    {'name': 'EntrySignals',
                                    'select_count': n2,
                                    'combination': 'or',
                                    'items': ['rvi_crossover_signal^55^16',
                                           'roc_crossover0^89',
                                           'price_crossover_sma_2^89',
                                           'ema_fast_crossover_slow^8^16',
                                           'aroon_diff_crossover0^21',
                                           'emacd_crossover_signal^13^26^13',
                                           'emacd_start_increase^55^110^55',
                                           'emacd_histogram_start_increase^21^42^21',
                                           'ema_fast_crossover_slow^5^10',
                                           'emacd_start_increase^34^68^34',
                                           'roc_crossover0^21',
                                           'roc_crossover0^13',
                                           'rvi_crossover_signal^89^25',
                                           'emacd_histogram_start_increase^89^178^89',
                                           'rvi_crossover_signal^144^41'] + tp_sig},
                                    {'name': 'ExitSignals',
                                    'select_count': n3,
                                    'combination': 'or',
                                    'items': ['bb_price_crossunder_high^144^3.0',
                                           'emacd_histogram_start_decrease^233^466^233',
                                           'bb_price_crossunder_high^34^2.5',
                                           'adx_plus_crossunder_minus^89',
                                           'trailing_stop^34^3.0',
                                           'trailing_stop^34^2.5']}],
                                    ZSmain=[{'name': 'EntryFilters',
                                    'select_count': n1,
                                    'combination': 'and',
                                    'items': ['rsi_fast_higher_slow^34^68',
                                           'emacd_histogram_increase^144^288^144',
                                           'rsi_fast_higher_slow^21^42',
                                           'adx_lower_threshold^55^20',
                                           'emacd_increase^55^110^55',
                                           'kc_neutral^144^72^3.5',
                                           'skew_negative^233^EMA',
                                           'rsi_fast_higher_slow^55^110',
                                           'aroon_diff_higher0^55',
                                           'smi_neutral^34^10^10^20^-20',
                                           'adx_plus_higher_minus^21',
                                           'adx_lower_threshold^34^20',
                                           'roc_higher0^89',
                                           'aroon_diff_higher0^89',
                                           'adx_lower_threshold^21^20']},
                                    {'name': 'EntrySignals',
                                    'select_count': n2,
                                    'combination': 'or',
                                    'items': ['kc_price_crossover_high_2^55^27^3.0',
                                           'emacd_start_increase^55^110^55',
                                           'ema_fast_crossover_slow^13^26',
                                           'bb_price_crossover_high_2^13^1.5',
                                           'ema_fast_crossover_slow^21^42',
                                           'adx_plus_crossover_minus^89',
                                           'emacd_crossover_signal^13^26^13',
                                           'bb_price_crossover_high_2^21^2.0',
                                           'adx_plus_crossover_minus^55',
                                           'kc_price_crossover_high_2^34^17^2.5',
                                           'aroon_diff_crossover0^89',
                                           'kc_price_crossover_high_2^21^10^2.0',
                                           'ema_fast_crossover_slow^34^68',
                                           'price_crossover_sma_2^89',
                                           'roc_crossover0^89'] + tp_sig},
                                    {'name': 'ExitSignals',
                                    'select_count': n3,
                                    'combination': 'or',
                                    'items': ['roc_crossunder0^55',
                                           'emacd_crossunder_signal^34^68^34',
                                           'emacd_start_decrease^55^110^55',
                                           'ema_fast_crossunder_slow^13^26',
                                           'trailing_stop^34^3.5',
                                           'trailing_stop^34^3.0']}],
                                    ZMmain=[{'name': 'EntryFilters',
                                    'select_count': n1,
                                    'combination': 'and',
                                    'items': ['atr_fast_lower_slow^89^178',
                                           'roc_higher0^55',
                                           'rsi_fast_higher_slow^55^110',
                                           'mass_lower1^89^89',
                                           'atr_fast_lower_slow^55^110',
                                           'ema_fast_higher_slow^55^110',
                                           'adx_plus_higher_minus^21',
                                           'adx_plus_higher_minus^13',
                                           'emacd_histogram_increase^377^754^377',
                                           'rsi_fast_higher_slow^89^178',
                                           'roc_higher0^89',
                                           'tsi_higher_signal^233^233^116',
                                           'atr_fast_lower_slow^144^288',
                                           'emacd_higher_signal^89^178^89',
                                           'emacd_increase^144^288^144']},
                                    {'name': 'EntrySignals',
                                    'select_count': n2,
                                    'combination': 'or',
                                    'items': ['smi_k_crossover_d^55^16^16',
                                           'kc_price_crossover_high_2^55^27^3.0',
                                           'emacd_crossover_signal^5^10^5',
                                           'emacd_histogram_start_increase^89^178^89',
                                           'emacd_start_increase^8^16^8',
                                           'aroon_diff_crossover0^21',
                                           'ema_fast_crossover_slow^5^10',
                                           'emacd_crossover_signal^21^42^21',
                                           'price_crossover_sma_2^13',
                                           'roc_crossover0^144',
                                           'emacd_histogram_start_increase^55^110^55',
                                           'rvi_crossover_signal^89^25',
                                           'emacd_crossover_signal^13^26^13',
                                           'emacd_start_increase^34^68^34',
                                           'kc_price_crossover_high_2^89^44^3.0'] + tp_sig},
                                    {'name': 'ExitSignals',
                                    'select_count': n3,
                                    'combination': 'or',
                                    'items': ['aroon_diff_crossunder0^34',
                                           'adx_plus_crossunder_minus^21',
                                           'roc_crossunder0^55',
                                           'adx_plus_crossunder_minus^89',
                                           'trailing_stop^34^3.5',
                                           'trailing_stop^34^3.0']}],
                                    ZLmain=[{'name': 'EntryFilters',
                                    'select_count': n1,
                                    'combination': 'and',
                                    'items': ['kc_neutral^21^10^2.0',
                                           'emacd_histogram_increase^377^754^377',
                                           'adx_plus_higher_minus^8',
                                           'kc_neutral^13^6^1.5',
                                           'adx_plus_higher_minus^55',
                                           'adx_plus_higher_minus^34',
                                           'emacd_histogram_increase^233^466^233',
                                           'adx_lower_threshold^21^20',
                                           'skew_negative^55^EMA',
                                           'skew_negative^89^EMA',
                                           'adx_lower_threshold^55^20',
                                           'skew_negative^377^EMA',
                                           'emacd_histogram_increase^144^288^144',
                                           'emacd_higher_signal^55^110^55',
                                           'aroon_diff_higher0^89']},
                                    {'name': 'EntrySignals',
                                    'select_count': n2,
                                    'combination': 'or',
                                    'items': ['emacd_crossover_signal^34^68^34',
                                           'emacd_crossover_signal^5^10^5',
                                           'rvi_crossover_signal^144^41',
                                           'adx_plus_crossover_minus^34',
                                           'ema_fast_crossover_slow^5^10',
                                           'adx_plus_crossover_minus^55',
                                           'emacd_start_increase^21^42^21',
                                           'emacd_histogram_start_increase^89^178^89',
                                           'kc_price_crossover_high_2^89^44^3.0',
                                           'emacd_histogram_start_increase^144^288^144',
                                           'emacd_histogram_start_increase^55^110^55',
                                           'emacd_crossover_signal^3^6^3',
                                           'emacd_crossover_signal^13^26^13',
                                           'emacd_crossover_signal^21^42^21',
                                           'adx_plus_crossover_minus^21'] + tp_sig},
                                    {'name': 'ExitSignals',
                                    'select_count': n3,
                                    'combination': 'or',
                                    'items': ['aroon_diff_crossunder0^89',
                                           'emacd_histogram_start_decrease^233^466^233',
                                           'roc_crossunder0^89',
                                           'bb_price_crossunder_high^34^2.5',
                                           'trailing_stop^34^3.0',
                                           'trailing_stop^34^3.5']}],
                                    SOLUSDT=[{'name': 'EntryFilters',
                                    'select_count': n1,
                                    'combination': 'and',
                                    'items': ["adx_lower_threshold^34^20",
                                            "aroon_diff_higher0^89",
                                            "roc_higher0^34",
                                            "emacd_increase^34^68^34",
                                            "smi_neutral^13^4^4^20^-20",
                                            "emacd_histogram_increase^377^754^377",
                                            "rsi_fast_higher_slow^144^288",
                                            "rsi_fast_higher_slow^89^178",
                                            "emacd_histogram_increase^34^68^34",
                                            "smi_neutral^55^16^16^20^-20",
                                            "adx_plus_higher_minus^55",
                                            "roc_higher0^233",
                                            "smi_neutral^144^41^41^20^-20",
                                            "adx_plus_higher_minus^89",
                                            "emacd_higher_signal^233^466^233"]},
                                    {'name': 'EntrySignals',
                                    'select_count': n2,
                                    'combination': 'or',
                                    'items':
                                      ["ema_fast_crossover_slow^8^16",
                                       "aroon_diff_crossover0^55",
                                       "adx_plus_crossover_minus^21",
                                       "rvi_crossover_signal^233^67",
                                       "roc_crossover0^34",
                                       "price_crossover_sma_2^89",
                                       "emacd_crossover_signal^34^68^34",
                                       "rvi_crossover_signal^377^108",
                                       "ema_fast_crossover_slow^34^68",
                                       "ema_fast_crossover_slow^21^42",
                                       "adx_plus_crossover_minus^13",
                                       "roc_crossover0^55",
                                       "adx_plus_crossover_minus^89",
                                       "roc_crossover0^144",
                                       "adx_plus_crossover_minus^55"]},
                                    {'name': 'ExitSignals',
                                    'select_count': n3,
                                    'combination': 'or',
                                    'items': ["trailing_stop^34^2.5",
                                            "trailing_stop^34^3.0",
                                            "kc_price_crossunder_high^21^10^2.0",
                                            "smi_k_crossunder_d^21^6^6",
                                            "kc_price_crossunder_high^144^72^3.0",
                                            "kc_price_crossunder_high^55^27^3.0"]}
                                    ],
                                    BTCUSDT=[
                                    {'name': 'EntryFilters',
                                    'select_count': n1,
                                    'combination': 'and',
                                    'items': ["roc_higher0^34",
                                       "roc_higher0^89",
                                       "aroon_diff_higher0^21",
                                       "aroon_diff_higher0^89",
                                       "emacd_histogram_increase^377^754^377",
                                       "price_higher_sma^34",
                                       "aroon_diff_higher0^233",
                                       "emacd_increase^144^288^144",
                                       "emacd_increase^13^26^13",
                                       "smi_neutral^34^10^10^20^-20",
                                       "rsi_fast_higher_slow^13^26",
                                       "adx_plus_higher_minus^13",
                                       "smi_neutral^21^6^6^20^-20",
                                       "smi_neutral^13^4^4^20^-20",
                                       "adx_plus_higher_minus^89"]},
                                    {'name': 'EntrySignals',
                                    'select_count': n2,
                                    'combination': 'or',
                                    'items':
                                    ["smi_k_crossover_d^144^41^41",
                                    "ema_fast_crossover_slow^34^68",
                                    "bb_price_crossover_high_2^55^3.0",
                                    "aroon_diff_crossover0^144",
                                    "emacd_start_increase^55^110^55",
                                    "smi_k_crossover_d^34^10^10",
                                    "ema_fast_crossover_slow^34^68",
                                    "ema_fast_crossover_slow^21^42",
                                    "aroon_diff_crossover0^144",
                                    "aroon_diff_crossover0^89",
                                    "adx_plus_crossover_minus^34",
                                    "adx_plus_crossover_minus^21",
                                    "ema_fast_crossover_slow^13^26",
                                    "rvi_crossover_signal^377^108",
                                    "emacd_histogram_start_increase^89^178^89",
                                    "roc_crossover0^144",
                                    "adx_plus_crossover_minus^55",
                                    "emacd_histogram_start_increase^144^288^144",
                                    "emacd_crossover_signal^34^68^34"
                                    ]},
                                    {'name': 'ExitSignals',
                                    'select_count': n3,
                                    'combination': 'or',
                                    'items': ["trailing_stop^34^3.0",
                                       "trailing_stop^34^3.5",
                                       "smi_k_crossunder_d^13^4^4",
                                       "emacd_histogram_start_decrease^34^68^34",
                                       "bb_price_crossunder_high^21^2.0",
                                       "smi_k_crossunder_d^21^6^6"]
                                    }
                                    ],
                                    ETHUSDT=[
                                    {'name': 'EntryFilters',
                                    'select_count': n1,
                                    'combination': 'and',
                                    'items': ["rsi_fast_higher_slow^13^26",
                                       "adx_plus_higher_minus^89",
                                       "aroon_diff_higher0^144",
                                       "aroon_diff_higher0^233",
                                       "rsi_fast_higher_slow^144^288",
                                       "adx_lower_threshold^34^20",
                                       "adx_lower_threshold^21^20",
                                       "emacd_higher_signal^34^68^34",
                                       "ema_fast_higher_slow^55^110",
                                       "ema_fast_higher_slow^89^178",
                                       "rsi_fast_higher_slow^89^178",
                                       "emacd_histogram_increase^377^754^377",
                                       "smi_neutral^13^4^4^20^-20",
                                       "smi_neutral^144^41^41^20^-20",
                                       "tsi_higher_signal^233^233^116"
                                       ]},
                                    {'name': 'EntrySignals',
                                    'select_count': n2,
                                    'combination': 'or',
                                    'items':
                                    ["emacd_start_increase^55^110^55",
                                    "smi_k_crossover_d^34^10^10",
                                    "ema_fast_crossover_slow^34^68",
                                    "ema_fast_crossover_slow^21^42",
                                    "aroon_diff_crossover0^144",
                                    "aroon_diff_crossover0^89",
                                    "adx_plus_crossover_minus^34",
                                    "adx_plus_crossover_minus^21",
                                    "ema_fast_crossover_slow^13^26",
                                    "rvi_crossover_signal^377^108",
                                    "emacd_histogram_start_increase^89^178^89",
                                    "roc_crossover0^144",
                                    "adx_plus_crossover_minus^55",
                                    "emacd_histogram_start_increase^144^288^144",
                                    "emacd_crossover_signal^34^68^34"
                                    ]},
                                    {'name': 'ExitSignals',
                                    'select_count': n3,
                                    'combination': 'or',
                                    'items':
                                    ["trailing_stop^34^2.5",
                                    "trailing_stop^34^3.0",
                                    "ema_fast_crossunder_slow^55^110",
                                    "kc_price_crossunder_high^55^27^3.0",
                                    "kc_price_crossunder_high^233^116^3.5",
                                    "kc_price_crossunder_high^144^72^3.0"]
                                    }
                                    ],
                                    DOGEUSDT=[
                                    {'name': 'EntryFilters',
                                    'select_count': n1,
                                    'combination': 'and',
                                    'items': ["skew_negative^144^EMA",
                                       "atr_fast_lower_slow^13^26",
                                       "emacd_histogram_increase^377^754^377",
                                       "smi_neutral^34^10^10^20^-20",
                                       "kc_neutral^13^6^1.5",
                                       "roc_higher0^377",
                                       "emacd_higher_signal^21^42^21",
                                       "ema_fast_higher_slow^13^26",
                                       "skew_negative^89^EMA",
                                       "ema_fast_higher_slow^21^42",
                                       "ema_fast_higher_slow^34^68",
                                       "smi_neutral^21^6^6^20^-20",
                                       "tsi_higher_signal^233^233^116",
                                       "smi_neutral^13^4^4^20^-20",
                                       "aroon_diff_higher0^233"

                                       ]},
                                    {'name': 'EntrySignals',
                                    'select_count': n2,
                                    'combination': 'or',
                                    'items':
                                    [
                                     "roc_crossover0^89",
                                     "kc_price_crossover_high_2^55^27^3.0",
                                     "smi_k_crossover_d^89^25^25",
                                     "kc_price_crossover_high_2^13^6^1.5",
                                     "smi_k_crossover_d^34^10^10",
                                     "aroon_diff_crossover0^55",
                                     "aroon_diff_crossover0^89",
                                     "emacd_crossover_signal^34^68^34",
                                     "adx_plus_crossover_minus^89",
                                     "bb_price_crossover_high_2^55^3.0",
                                     "rvi_crossover_signal^233^67",
                                     "bb_price_crossover_high_2^34^2.5",
                                     "aroon_diff_crossover0^233",
                                     "ema_fast_crossover_slow^21^42",
                                     "rvi_crossover_signal^377^108"
                                    ]},
                                    {'name': 'ExitSignals',
                                    'select_count': n3,
                                    'combination': 'or',
                                    'items':
                                    ["trailing_stop^34^3.0",
                                    "trailing_stop^34^3.5",

                                    "bb_price_crossunder_high^144^3.0",
                                    "aroon_diff_crossunder0^34",
                                    "emacd_crossunder_signal^34^68^34",
                                    "kc_price_crossunder_high^233^116^3.5"]
                                    }
                                    ],
                                )
    n1,n2,n3 = 2,2,2
    STRATEGY_PARAMS_CONFIG = dict(  GCmain=[
                                    {
                                    "name": "EntryFilters", "select_count": n1, 'combination': 'and',
                                    "items": pd.read_csv(fr"GCmain_all_filters_summary.csv",usecols=['策略名称'])['策略名称'].tolist(),
                                    },
                                    {
                                    "name": "EntrySignals", "select_count": n2, 'combination': 'or',
                                    "items": [

                                             "aroon_diff_crossover0^34",
                                             "roc_crossover0^34",
                                             "bb_price_crossover_high_2^21^2.0",
                                             "roc_crossover0^21",
                                             "emacd_crossover_signal^34^68^34",
                                             "adx_plus_crossover_minus^21",
                                             "emacd_start_increase^55^110^55",
                                             "emacd_histogram_start_increase^55^110^55",
                                             "ema_fast_crossover_slow^13^26",
                                             "smi_k_crossover_d^34^10^10",
                                             "aroon_diff_crossover0^89",
                                             "adx_plus_crossover_minus^34",
                                             "adx_plus_crossover_minus^55",
                                             "adx_plus_crossover_minus^89",
                                             "kc_price_crossover_high_2^89^44^3.0"] + tp_sig,
                                    },
                                    {
                                    "name": "ExitSignals", "select_count": n3, 'combination': 'or',
                                    "items": [
                                    "trailing_stop^34^2.5",
                                    "trailing_stop^34^3.5",
                                    "smi_k_crossunder_d^21^6^6",
                                    "emacd_start_decrease^34^68^34",
                                    "emacd_crossunder_signal^8^16^8",
                                    "emacd_histogram_start_decrease^55^110^55"
                                    ],
                                    }
                                    ],
                                    SImain=[
                                    {'name': 'EntryFilters',
                                    'select_count': n1,
                                    'combination': 'and',
                                    'items': pd.read_csv(fr"SImain_all_filters_summary.csv",usecols=['策略名称'])['策略名称'].tolist()},
                                    {'name': 'EntrySignals',
                                    'select_count': n2,
                                    'combination': 'or',
                                    'items': ['emacd_crossover_signal^13^26^13',
                                       'kc_price_crossover_high_2^55^27^3.0',
                                       'aroon_diff_crossover0^233',
                                       'emacd_crossover_signal^21^42^21',
                                       'price_crossover_sma_2^89',
                                       'kc_price_crossover_high_2^34^17^2.5',
                                       'adx_plus_crossover_minus^21',
                                       'adx_plus_crossover_minus^55',
                                       'bb_price_crossover_high_2^21^2.0',
                                       'emacd_histogram_start_increase^144^288^144',
                                       'kc_price_crossover_high_2^144^72^3.0',
                                       'roc_crossover0^89',
                                       'bb_price_crossover_high_2^34^2.5',
                                       'roc_crossover0^55',
                                       'kc_price_crossover_high_2^13^6^1.5'] + tp_sig
                                    },
                                    {'name': 'ExitSignals',
                                    'select_count': n3,
                                    'combination': 'or',
                                    'items': ["trailing_stop^34^2.5",
                                       "trailing_stop^34^3.0",
                                       "roc_crossunder0^34",
                                       "emacd_histogram_start_decrease^89^178^89",
                                       "emacd_start_decrease^34^68^34",
                                       "rvi_crossunder_signal^144^41"]
                                    }],
                                    HGmain=[{'name': 'EntryFilters',
                                    'select_count': n1,
                                    'combination': 'and',
                                    'items': pd.read_csv(fr"HGmain_all_filters_summary.csv",usecols=['策略名称'])['策略名称'].tolist()},
                                    {'name': 'EntrySignals',
                                    'select_count': n2,
                                    'combination': 'or',
                                    'items': ['adx_plus_crossover_minus^13',
                                           'smi_k_crossover_d^55^16^16',
                                           'price_crossover_sma_2^34',
                                           'emacd_histogram_start_increase^55^110^55',
                                           'adx_plus_crossover_minus^8',
                                           'rvi_crossover_signal^377^108',
                                           'smi_k_crossover_d^34^10^10',
                                           'smi_k_crossover_d^21^6^6',
                                           'roc_crossover0^34',
                                           'emacd_crossover_signal^21^42^21',
                                           'ema_fast_crossover_slow^13^26',
                                           'adx_plus_crossover_minus^21',
                                           'smi_k_crossover_d^144^41^41',
                                           'emacd_crossover_signal^13^26^13',
                                           'emacd_crossover_signal^34^68^34'] + tp_sig},
                                    {'name': 'ExitSignals',
                                    'select_count': n3,
                                    'combination': 'or',
                                    'items': ["trailing_stop^34^3.5",
                                           "trailing_stop^34^3.0",
                                           "price_crossunder_sma_2^144",
                                           "adx_plus_crossunder_minus^55",
                                           "adx_plus_crossunder_minus^89",
                                           "roc_crossunder0^144"
                                           ]}],
                                    CLmain=[{'name': 'EntryFilters',
                                    'select_count': n1,
                                    'combination': 'and',
                                    'items': pd.read_csv(fr"CLmain_all_filters_summary.csv",usecols=['策略名称'])['策略名称'].tolist()},
                                    {'name': 'EntrySignals',
                                    'select_count': n2,
                                    'combination': 'or',
                                    'items': ['adx_plus_crossover_minus^34',
                                           'adx_plus_crossover_minus^13',
                                           'smi_k_crossover_d^34^10^10',
                                           'aroon_diff_crossover0^21',
                                           'aroon_diff_crossover0^89',
                                           'adx_plus_crossover_minus^21',
                                           'emacd_histogram_start_increase^55^110^55',
                                           'kc_price_crossover_high_2^13^6^1.5',
                                           'roc_crossover0^89',
                                           'emacd_histogram_start_increase^21^42^21',
                                           'emacd_start_increase^21^42^21',
                                           'smi_k_crossover_d^13^4^4',
                                           'adx_plus_crossover_minus^8',
                                           'emacd_start_increase^5^10^5',
                                           'emacd_start_increase^34^68^34'] + tp_sig},
                                    {'name': 'ExitSignals',
                                    'select_count': n3,
                                    'combination': 'or',
                                    'items': ['aroon_diff_crossunder0^144',
                                           'emacd_start_decrease^144^288^144',
                                           'aroon_diff_crossunder0^55',
                                           'smi_k_crossunder_d^55^16^16',
                                           'trailing_stop^34^2.5',
                                           'trailing_stop^34^3.0']}],
                                ZSmain=[{'name': 'EntryFilters',
                                         'select_count': n1,
                                         'combination': 'and',
                                         'items':pd.read_csv(fr"ZSmain_all_filters_summary.csv",usecols=['策略名称'])['策略名称'].tolist()},
                                        {'name': 'EntrySignals',
                                         'select_count': n2,
                                         'combination': 'or',
                                         'items': ['kc_price_crossover_high_2^55^27^3.0',
                                                   'emacd_start_increase^55^110^55',
                                                   'ema_fast_crossover_slow^13^26',
                                                   'bb_price_crossover_high_2^13^1.5',
                                                   'ema_fast_crossover_slow^21^42',
                                                   'adx_plus_crossover_minus^89',
                                                   'emacd_crossover_signal^13^26^13',
                                                   'bb_price_crossover_high_2^21^2.0',
                                                   'adx_plus_crossover_minus^55',
                                                   'kc_price_crossover_high_2^34^17^2.5',
                                                   'aroon_diff_crossover0^89',
                                                   'kc_price_crossover_high_2^21^10^2.0',
                                                   'ema_fast_crossover_slow^34^68',
                                                   'price_crossover_sma_2^89',
                                                   'roc_crossover0^89'] + tp_sig},
                                        {'name': 'ExitSignals',
                                         'select_count': n3,
                                         'combination': 'or',
                                         'items': ['roc_crossunder0^55',
                                                   'emacd_crossunder_signal^34^68^34',
                                                   'emacd_start_decrease^55^110^55',
                                                   'ema_fast_crossunder_slow^13^26',
                                                   'trailing_stop^34^3.5',
                                                   'trailing_stop^34^2.5',
                                                   'trailing_stop^34^3.0']}],
        ZLmain=[{'name': 'EntryFilters',
                 'select_count': n1,
                 'combination': 'and',
                 'items': pd.read_csv(fr"ZLmain_all_filters_summary.csv",usecols=['策略名称'])['策略名称'].tolist()},
                {'name': 'EntrySignals',
                 'select_count': n2,
                 'combination': 'or',
                 'items': ['emacd_crossover_signal^34^68^34',
                           'emacd_crossover_signal^5^10^5',
                           'rvi_crossover_signal^144^41',
                           'adx_plus_crossover_minus^34',
                           'ema_fast_crossover_slow^5^10',
                           'adx_plus_crossover_minus^55',
                           'emacd_start_increase^21^42^21',
                           'emacd_histogram_start_increase^89^178^89',
                           'kc_price_crossover_high_2^89^44^3.0',
                           'emacd_histogram_start_increase^144^288^144',
                           'emacd_histogram_start_increase^55^110^55',
                           'emacd_crossover_signal^3^6^3',
                           'emacd_crossover_signal^13^26^13',
                           'emacd_crossover_signal^21^42^21',
                           'adx_plus_crossover_minus^21'] + tp_sig},
                {'name': 'ExitSignals',
                 'select_count': n3,
                 'combination': 'or',
                 'items': ['aroon_diff_crossunder0^89',
                           'emacd_histogram_start_decrease^233^466^233',
                           'roc_crossunder0^89',
                           'bb_price_crossunder_high^34^2.5',
                           'trailing_stop^34^2.5',
                           'trailing_stop^34^3.0',
                           'trailing_stop^34^3.5',
                           ]}],

    )
    en_list = pd.read_csv(rf"C:\Users\zrm50\Downloads\GCmain_entry_all_validated.csv",usecols=['signal_id'])['signal_id'].tolist()

    flt_list = pd.read_csv(fr"GCmain_all_filters_summary.csv",usecols=['策略名称'])['策略名称'].tolist()
    # flt_list = flt_list

    STRATEGY_PARAMS_CONFIG = STRATEGY_PARAMS_CONFIG

if __name__ == "__main__":
    if 0:
        from 优化回测 import run_strategy_single,compute_backtest_metrics_with_jz
        df = pd.read_csv(rf"D:\nick01\stg_multi_factor_nick\15min_全品种优化_short\backtest_result_data-f-2_s-2_e-2_jzmode-d\optimization_GCmain\raw_evaluation_cache.csv").tail(30)
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
            "direction_long": False,  # 做多方向
            "ignore_new_entry": True,  # 持仓时不更新出场条件
            "resample_rule": "",  # 重采样规则（空字符串表示不重采样）
            "rf": 0.00,
            "jz_mode": "d"  # 无风险利率
        }
        (combo_name, market_df0,market_jz), metrics = run_strategy_single(
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
            market_df = market_df0[['datetime', 'open', 'high', 'low', 'close', 'volume', clname]],
            position_series=market_df0[clname],
                combo_name=combo_name,
                transaction_cost=0.0005,
                rf=0.00,
                jz_mode="d",
                resample_rule="",
                direction_long=0,
                )
            all_ms.append(all_metrics)
            plt.plot(cum_curve)
        plt.plot(market_df0['close']/market_df0['close'].iloc[0],'r')
        print(pd.DataFrame(all_ms))
        plt.show()
        exit()
    # 示例2：单品种优化
    if 0:

        code_id = "GCmain"
        output_dir = rf"D:\nick01\stg_multi_factor_nick\15min_全品种优化\backtest_result_data-f-2_s-2_e-2_jzmode-d\optimization_GCmain\test_opt_res"
        os.makedirs(output_dir, exist_ok=True)
        start = datetime(2026, 2, 1)
        end = datetime(2026, 6, 5)
        # 优化参数配置
        OPTIMIZATION_CONFIG = {
            "population_size": 2000,  # 种群大小
            "n_generations": 100,  # 迭代代数
        }
        # 回测默认配置
        BACKTEST_CONFIG = {
            "transaction_cost": 0.0005,  # 单边交易成本（万三）
            "direction_long": True,  # 做多方向
            "ignore_new_entry": True,  # 持仓时不更新出场条件
            "resample_rule": "",  # 重采样规则（空字符串表示不重采样）
            "rf": 0.00,
            "jz_mode": "d"  # 无风险利率
        }
        result = run_optimization_for_single_code(
            code_id=code_id,
            start=start,
                                end=end,
                                output_dir=output_dir,
                                market_data_paths=MK_DATA_PATHS,
                                strategy_config=STRATEGY_PARAMS_CONFIG,
                                objectives_config=OBJECTIVES_CONFIG,
                                backtest_config=BACKTEST_CONFIG,
                                save_raw_force_filter_config =SAVE_RAW_FORCE_FILTER_CONFIG,
                                population_size=OPTIMIZATION_CONFIG["population_size"],
                                n_generations=OPTIMIZATION_CONFIG["n_generations"],
                            )

    if 0:
        BACKTEST_CONFIG = {
            "transaction_cost": 0.0005,  # 单边交易成本（万三）
            "direction_long": True,  # 做多方向
            "ignore_new_entry": True,  # 持仓时不更新出场条件
            "resample_rule": "",  # 重采样规则（空字符串表示不重采样）
            "rf": 0.00,
            "jz_mode": "d"  # 无风险利率
        }

        code_ids = ['GCmain', 'SImain',  'HGmain','CLmain', 'ZSmain', 'ZLmain', 'ZMmain', 'ZWmain', 'ZCmain'][:]
        start = datetime(2026, 2, 1)
        end = datetime(2026, 6, 18)
        n1 = 1
        n2 = 1
        n3 = 1
        output_dir=rf"D:\nick01\stg_multi_factor_nick\15min_全品种优化\backtest_result_data-f-{n1}_s-{n2}_e-{n3}_jzmode-{BACKTEST_CONFIG.get('jz_mode')}_new"
        os.makedirs(output_dir, exist_ok=True)
        OPTIMIZATION_CONFIG = {
                                "population_size": 1000,  # 种群大小
                                "n_generations": 100,  # 迭代代数
                                }
        dir_data_path = rf'C:\Users\zrm50\Downloads'
        symbol_id = 'GCmain'
        STRATEGY_PARAMS_CONFIG = {symbol_id:
                [{'name': 'EntryFilters','select_count': n1,'combination': 'and','items': pd.read_csv(fr"{dir_data_path}\{symbol_id}_all_filters_summary.csv", usecols=['策略名称'])['策略名称'].tolist()[::]},
                 {'name': 'EntrySignals','select_count': n2,'combination': 'or','items': pd.read_csv(rf"{dir_data_path}\{symbol_id}_entry_all_validated.csv", usecols=['signal_id'])['signal_id'].tolist()[::]},
                 {'name': 'ExitSignals','select_count': n3,'combination': 'or','items':
                    ['aroon_diff_crossunder0^59', 'aroon_diff_crossunder0^89', 'aroon_diff_crossunder0^109','emacd_histogram_start_decrease^233^466^233',
                     'roc_crossunder0^89','roc_crossunder0^59',
                     'bb_price_crossunder_high^34^2.5','bb_price_crossunder_high^34^2',
                     'trailing_stop^34^2.5','trailing_stop^34^3.0','trailing_stop^34^3.5',]}
                ]  for symbol_id in code_ids}

        run_optimization_batch(
            code_ids=code_ids,
            start=start,
            end=end,
            output_dir=output_dir,
            market_data_paths=MK_DATA_PATHS,
            strategy_config=STRATEGY_PARAMS_CONFIG,
            objectives_config=OBJECTIVES_CONFIG,
            backtest_config=BACKTEST_CONFIG,
            save_raw_force_filter_config = SAVE_RAW_FORCE_FILTER_CONFIG,
            population_size=OPTIMIZATION_CONFIG["population_size"],
            n_generations=OPTIMIZATION_CONFIG["n_generations"]  ,
            num_processes=10,
        )



        # 保存回测配置信息到Markdown文件
        import json

        class NumpyEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, (np.integer,)):
                    return int(obj)
                elif isinstance(obj, (np.floating,)):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                return super().default(obj)

        config_md_path = os.path.join(output_dir, "回测配置信息.md")

        with open(config_md_path, 'w', encoding='utf-8') as f:
            f.write("# 回测配置信息\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## 基础配置\n\n")
            f.write(f"- **品种列表 (code_ids)**: `{code_ids}`\n")
            f.write(f"- **开始时间 (start)**: `{start}`\n")
            f.write(f"- **结束时间 (end)**: `{end}`\n\n")

            f.write("## 策略配置 (strategy_config)\n\n")
            f.write("```json\n")
            f.write(json.dumps(STRATEGY_PARAMS_CONFIG, indent=2, ensure_ascii=False, cls=NumpyEncoder))
            f.write("\n```\n\n")

            f.write("## 优化目标配置 (objectives_config)\n\n")
            f.write("```json\n")
            f.write(json.dumps(OBJECTIVES_CONFIG, indent=2, ensure_ascii=False, cls=NumpyEncoder))
            f.write("\n```\n\n")

            f.write("## 回测配置 (backtest_config)\n\n")
            f.write("```json\n")
            f.write(json.dumps(BACKTEST_CONFIG, indent=2, ensure_ascii=False, cls=NumpyEncoder))
            f.write("\n```\n\n")

            f.write("## 过滤配置 (save_raw_force_filter_config)\n\n")
            f.write("```json\n")
            f.write(json.dumps(SAVE_RAW_FORCE_FILTER_CONFIG, indent=2, ensure_ascii=False, cls=NumpyEncoder))
            f.write("\n```\n\n")

            f.write("## 优化参数\n\n")
            f.write(f"- **种群大小 (population_size)**: `{OPTIMIZATION_CONFIG['population_size']}`\n")
            f.write(f"- **迭代代数 (n_generations)**: `{OPTIMIZATION_CONFIG['n_generations']}`\n")

            f.write("---\n\n")
            f.write("*此配置文件由优化脚本自动生成*\n")

        logger.info(f"回测配置信息已保存至: {config_md_path}")

    OPTIMIZATION_CONFIG = {
                            "population_size": 5000,  # 种群大小
                            "n_generations": 400,  # 迭代代数
                            }
    n1 = 2
    n2 = 2
    n3 = 2
    if 1:
        BACKTEST_CONFIG = {
            "transaction_cost": 0.0005,  # 单边交易成本（万三）
            "direction_long": False,  # 做多方向
            "ignore_new_entry": True,  # 持仓时不更新出场条件
            "resample_rule": "",  # 重采样规则（空字符串表示不重采样）
            "rf": 0.00,
            "jz_mode": "d"  # 无风险利率
        }

        code_ids = ['GCmain', 'SImain',  'HGmain','CLmain', 'ZSmain', 'ZLmain', 'ZMmain', 'ZWmain', 'ZCmain'][:]
        start = datetime(2026, 2, 1)
        end = datetime(2026, 6, 18)

        output_dir=rf"backtest_result_data-f-{n1}_s-{n2}_e-{n3}_jzmode-{BACKTEST_CONFIG.get('jz_mode')}-new"
        os.makedirs(output_dir, exist_ok=True)
        dir_data_path = rf'D:\nick01\stg_multi_factor_nick\15min_全品种优化_short\信号和过滤'

        # symbol_id = 'GCmain'
        orjson.dumps = lambda obj: orjson.dumps(obj, option=orjson.OPT_SERIALIZE_NUMPY)
        STRATEGY_PARAMS_CONFIG = {symbol_id:
                [{'name': 'EntryFilters','select_count': n1,'combination': 'and','items': pd.read_csv(fr"{dir_data_path}\{symbol_id}_all_filters_summary_short.csv", usecols=['策略名称'])['策略名称'].tolist()[::]},
                 {'name': 'EntrySignals','select_count': n2,'combination': 'or','items': pd.read_csv(rf"{dir_data_path}\{symbol_id}_entry_all_validated_short.csv", usecols=['signal_id'])['signal_id'].tolist()[::]},
                 {'name': 'ExitSignals','select_count': n3,'combination': 'or','items': list(set(['trailing_stop^34^1.5','trailing_stop^34^2.5','trailing_stop^34^2.0','trailing_stop^34^3.0','trailing_stop^34^3.5',]+
                    load_json(rf'{dir_data_path}\select_signal_{symbol_id}_short_15min_1&1&1.json').get('exit_0_0')))
                  }
                ]  for symbol_id in code_ids}

        run_optimization_batch(
            code_ids=code_ids,
            start=start,
            end=end,
            output_dir=output_dir,
            market_data_paths=MK_DATA_PATHS,
            strategy_config=STRATEGY_PARAMS_CONFIG,
            objectives_config=OBJECTIVES_CONFIG,
            backtest_config=BACKTEST_CONFIG,
            save_raw_force_filter_config = SAVE_RAW_FORCE_FILTER_CONFIG,
            population_size=OPTIMIZATION_CONFIG["population_size"],
            n_generations=OPTIMIZATION_CONFIG["n_generations"]  ,
            num_processes=10,
        )

        # 保存回测配置信息到Markdown文件
        import json

        class NumpyEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, (np.integer,)):
                    return int(obj)
                elif isinstance(obj, (np.floating,)):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                return super().default(obj)

        config_md_path = os.path.join(output_dir, "回测配置信息.md")

        with open(config_md_path, 'w', encoding='utf-8') as f:
            f.write("# 回测配置信息\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## 基础配置\n\n")
            f.write(f"- **品种列表 (code_ids)**: `{code_ids}`\n")
            f.write(f"- **开始时间 (start)**: `{start}`\n")
            f.write(f"- **结束时间 (end)**: `{end}`\n\n")

            f.write("## 策略配置 (strategy_config)\n\n")
            f.write("```json\n")
            f.write(json.dumps(STRATEGY_PARAMS_CONFIG, indent=2, ensure_ascii=False, cls=NumpyEncoder))
            f.write("\n```\n\n")

            f.write("## 优化目标配置 (objectives_config)\n\n")
            f.write("```json\n")
            f.write(json.dumps(OBJECTIVES_CONFIG, indent=2, ensure_ascii=False, cls=NumpyEncoder))
            f.write("\n```\n\n")

            f.write("## 回测配置 (backtest_config)\n\n")
            f.write("```json\n")
            f.write(json.dumps(BACKTEST_CONFIG, indent=2, ensure_ascii=False, cls=NumpyEncoder))
            f.write("\n```\n\n")

            f.write("## 过滤配置 (save_raw_force_filter_config)\n\n")
            f.write("```json\n")
            f.write(json.dumps(SAVE_RAW_FORCE_FILTER_CONFIG, indent=2, ensure_ascii=False, cls=NumpyEncoder))
            f.write("\n```\n\n")

            f.write("## 优化参数\n\n")
            f.write(f"- **种群大小 (population_size)**: `{OPTIMIZATION_CONFIG['population_size']}`\n")
            f.write(f"- **迭代代数 (n_generations)**: `{OPTIMIZATION_CONFIG['n_generations']}`\n")

            f.write("---\n\n")
            f.write("*此配置文件由优化脚本自动生成*\n")

        logger.info(f"回测配置信息已保存至: {config_md_path}")

    n1 = 2
    n2 = 3
    n3 = 2
    if 1:
        BACKTEST_CONFIG = {
            "transaction_cost": 0.0005,  # 单边交易成本（万三）
            "direction_long": False,  # 做多方向
            "ignore_new_entry": True,  # 持仓时不更新出场条件
            "resample_rule": "",  # 重采样规则（空字符串表示不重采样）
            "rf": 0.00,
            "jz_mode": "d"  # 无风险利率
        }

        code_ids = ['GCmain', 'SImain',  'HGmain','CLmain', 'ZSmain', 'ZLmain', 'ZMmain', 'ZWmain', 'ZCmain'][:]
        start = datetime(2026, 2, 1)
        end = datetime(2026, 6, 18)

        output_dir=rf"backtest_result_data-f-{n1}_s-{n2}_e-{n3}_jzmode-{BACKTEST_CONFIG.get('jz_mode')}-new"
        os.makedirs(output_dir, exist_ok=True)

        dir_data_path = rf'D:\nick01\stg_multi_factor_nick\15min_全品种优化_short\信号和过滤'

        # symbol_id = 'GCmain'
        orjson.dumps = lambda obj: orjson.dumps(obj, option=orjson.OPT_SERIALIZE_NUMPY)
        STRATEGY_PARAMS_CONFIG = {symbol_id:
                [{'name': 'EntryFilters','select_count': n1,'combination': 'and','items': pd.read_csv(fr"{dir_data_path}\{symbol_id}_all_filters_summary_short.csv", usecols=['策略名称'])['策略名称'].tolist()[::]},
                 {'name': 'EntrySignals','select_count': n2,'combination': 'or','items': pd.read_csv(rf"{dir_data_path}\{symbol_id}_entry_all_validated_short.csv", usecols=['signal_id'])['signal_id'].tolist()[::]},
                 {'name': 'ExitSignals','select_count': n3,'combination': 'or','items': list(set(['trailing_stop^34^1.5','trailing_stop^34^2.5','trailing_stop^34^2.0','trailing_stop^34^3.0','trailing_stop^34^3.5',]+
                    load_json(rf'{dir_data_path}\select_signal_{symbol_id}_short_15min_1&1&1.json').get('exit_0_0')))
                  }
                ]  for symbol_id in code_ids}

        run_optimization_batch(
            code_ids=code_ids,
            start=start,
            end=end,
            output_dir=output_dir,
            market_data_paths=MK_DATA_PATHS,
            strategy_config=STRATEGY_PARAMS_CONFIG,
            objectives_config=OBJECTIVES_CONFIG,
            backtest_config=BACKTEST_CONFIG,
            save_raw_force_filter_config = SAVE_RAW_FORCE_FILTER_CONFIG,
            population_size=OPTIMIZATION_CONFIG["population_size"],
            n_generations=OPTIMIZATION_CONFIG["n_generations"]  ,
            num_processes=10,
        )

        # 保存回测配置信息到Markdown文件
        import json

        class NumpyEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, (np.integer,)):
                    return int(obj)
                elif isinstance(obj, (np.floating,)):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                return super().default(obj)

        config_md_path = os.path.join(output_dir, "回测配置信息.md")

        with open(config_md_path, 'w', encoding='utf-8') as f:
            f.write("# 回测配置信息\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## 基础配置\n\n")
            f.write(f"- **品种列表 (code_ids)**: `{code_ids}`\n")
            f.write(f"- **开始时间 (start)**: `{start}`\n")
            f.write(f"- **结束时间 (end)**: `{end}`\n\n")

            f.write("## 策略配置 (strategy_config)\n\n")
            f.write("```json\n")
            f.write(json.dumps(STRATEGY_PARAMS_CONFIG, indent=2, ensure_ascii=False, cls=NumpyEncoder))
            f.write("\n```\n\n")

            f.write("## 优化目标配置 (objectives_config)\n\n")
            f.write("```json\n")
            f.write(json.dumps(OBJECTIVES_CONFIG, indent=2, ensure_ascii=False, cls=NumpyEncoder))
            f.write("\n```\n\n")

            f.write("## 回测配置 (backtest_config)\n\n")
            f.write("```json\n")
            f.write(json.dumps(BACKTEST_CONFIG, indent=2, ensure_ascii=False, cls=NumpyEncoder))
            f.write("\n```\n\n")

            f.write("## 过滤配置 (save_raw_force_filter_config)\n\n")
            f.write("```json\n")
            f.write(json.dumps(SAVE_RAW_FORCE_FILTER_CONFIG, indent=2, ensure_ascii=False, cls=NumpyEncoder))
            f.write("\n```\n\n")

            f.write("## 优化参数\n\n")
            f.write(f"- **种群大小 (population_size)**: `{OPTIMIZATION_CONFIG['population_size']}`\n")
            f.write(f"- **迭代代数 (n_generations)**: `{OPTIMIZATION_CONFIG['n_generations']}`\n")

            f.write("---\n\n")
            f.write("*此配置文件由优化脚本自动生成*\n")

        logger.info(f"回测配置信息已保存至: {config_md_path}")

    n1 = 3
    n2 = 3
    n3 = 2
    if 1:
        BACKTEST_CONFIG = {
            "transaction_cost": 0.0005,  # 单边交易成本（万三）
            "direction_long": False,  # 做多方向
            "ignore_new_entry": True,  # 持仓时不更新出场条件
            "resample_rule": "",  # 重采样规则（空字符串表示不重采样）
            "rf": 0.00,
            "jz_mode": "d"  # 无风险利率
        }

        code_ids = ['GCmain', 'SImain',  'HGmain','CLmain', 'ZSmain', 'ZLmain', 'ZMmain', 'ZWmain', 'ZCmain'][:]
        start = datetime(2026, 2, 1)
        end = datetime(2026, 6, 18)

        output_dir=rf"backtest_result_data-f-{n1}_s-{n2}_e-{n3}_jzmode-{BACKTEST_CONFIG.get('jz_mode')}-new"
        os.makedirs(output_dir, exist_ok=True)

        dir_data_path = rf'D:\nick01\stg_multi_factor_nick\15min_全品种优化_short\信号和过滤'

        # symbol_id = 'GCmain'
        orjson.dumps = lambda obj: orjson.dumps(obj, option=orjson.OPT_SERIALIZE_NUMPY)
        STRATEGY_PARAMS_CONFIG = {symbol_id:
                [{'name': 'EntryFilters','select_count': n1,'combination': 'and','items': pd.read_csv(fr"{dir_data_path}\{symbol_id}_all_filters_summary_short.csv", usecols=['策略名称'])['策略名称'].tolist()[::]},
                 {'name': 'EntrySignals','select_count': n2,'combination': 'or','items': pd.read_csv(rf"{dir_data_path}\{symbol_id}_entry_all_validated_short.csv", usecols=['signal_id'])['signal_id'].tolist()[::]},
                 {'name': 'ExitSignals','select_count': n3,'combination': 'or','items': list(set(['trailing_stop^34^1.5','trailing_stop^34^2.5','trailing_stop^34^2.0','trailing_stop^34^3.0','trailing_stop^34^3.5',]+
                    load_json(rf'{dir_data_path}\select_signal_{symbol_id}_short_15min_1&1&1.json').get('exit_0_0')))
                  }
                ]  for symbol_id in code_ids}

        run_optimization_batch(
            code_ids=code_ids,
            start=start,
            end=end,
            output_dir=output_dir,
            market_data_paths=MK_DATA_PATHS,
            strategy_config=STRATEGY_PARAMS_CONFIG,
            objectives_config=OBJECTIVES_CONFIG,
            backtest_config=BACKTEST_CONFIG,
            save_raw_force_filter_config = SAVE_RAW_FORCE_FILTER_CONFIG,
            population_size=OPTIMIZATION_CONFIG["population_size"],
            n_generations=OPTIMIZATION_CONFIG["n_generations"]  ,
            num_processes=10,
        )

        # 保存回测配置信息到Markdown文件
        import json

        class NumpyEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, (np.integer,)):
                    return int(obj)
                elif isinstance(obj, (np.floating,)):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                return super().default(obj)

        config_md_path = os.path.join(output_dir, "回测配置信息.md")

        with open(config_md_path, 'w', encoding='utf-8') as f:
            f.write("# 回测配置信息\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## 基础配置\n\n")
            f.write(f"- **品种列表 (code_ids)**: `{code_ids}`\n")
            f.write(f"- **开始时间 (start)**: `{start}`\n")
            f.write(f"- **结束时间 (end)**: `{end}`\n\n")

            f.write("## 策略配置 (strategy_config)\n\n")
            f.write("```json\n")
            f.write(json.dumps(STRATEGY_PARAMS_CONFIG, indent=2, ensure_ascii=False, cls=NumpyEncoder))
            f.write("\n```\n\n")

            f.write("## 优化目标配置 (objectives_config)\n\n")
            f.write("```json\n")
            f.write(json.dumps(OBJECTIVES_CONFIG, indent=2, ensure_ascii=False, cls=NumpyEncoder))
            f.write("\n```\n\n")

            f.write("## 回测配置 (backtest_config)\n\n")
            f.write("```json\n")
            f.write(json.dumps(BACKTEST_CONFIG, indent=2, ensure_ascii=False, cls=NumpyEncoder))
            f.write("\n```\n\n")

            f.write("## 过滤配置 (save_raw_force_filter_config)\n\n")
            f.write("```json\n")
            f.write(json.dumps(SAVE_RAW_FORCE_FILTER_CONFIG, indent=2, ensure_ascii=False, cls=NumpyEncoder))
            f.write("\n```\n\n")

            f.write("## 优化参数\n\n")
            f.write(f"- **种群大小 (population_size)**: `{OPTIMIZATION_CONFIG['population_size']}`\n")
            f.write(f"- **迭代代数 (n_generations)**: `{OPTIMIZATION_CONFIG['n_generations']}`\n")

            f.write("---\n\n")
            f.write("*此配置文件由优化脚本自动生成*\n")

        logger.info(f"回测配置信息已保存至: {config_md_path}")

    n1 = 2
    n2 = 4
    n3 = 2
    if 1:
        BACKTEST_CONFIG = {
            "transaction_cost": 0.0005,  # 单边交易成本（万三）
            "direction_long": False,  # 做多方向
            "ignore_new_entry": True,  # 持仓时不更新出场条件
            "resample_rule": "",  # 重采样规则（空字符串表示不重采样）
            "rf": 0.00,
            "jz_mode": "d"  # 无风险利率
        }

        code_ids = ['GCmain', 'SImain',  'HGmain','CLmain', 'ZSmain', 'ZLmain', 'ZMmain', 'ZWmain', 'ZCmain'][:]
        start = datetime(2026, 2, 1)
        end = datetime(2026, 6, 18)

        output_dir=rf"backtest_result_data-f-{n1}_s-{n2}_e-{n3}_jzmode-{BACKTEST_CONFIG.get('jz_mode')}-new"
        os.makedirs(output_dir, exist_ok=True)

        dir_data_path = rf'D:\nick01\stg_multi_factor_nick\15min_全品种优化_short\信号和过滤'

        # symbol_id = 'GCmain'
        orjson.dumps = lambda obj: orjson.dumps(obj, option=orjson.OPT_SERIALIZE_NUMPY)
        STRATEGY_PARAMS_CONFIG = {symbol_id:
                [{'name': 'EntryFilters','select_count': n1,'combination': 'and','items': pd.read_csv(fr"{dir_data_path}\{symbol_id}_all_filters_summary_short.csv", usecols=['策略名称'])['策略名称'].tolist()[::]},
                 {'name': 'EntrySignals','select_count': n2,'combination': 'or','items': pd.read_csv(rf"{dir_data_path}\{symbol_id}_entry_all_validated_short.csv", usecols=['signal_id'])['signal_id'].tolist()[::]},
                 {'name': 'ExitSignals','select_count': n3,'combination': 'or','items': list(set(['trailing_stop^34^1.5','trailing_stop^34^2.5','trailing_stop^34^2.0','trailing_stop^34^3.0','trailing_stop^34^3.5',]+
                    load_json(rf'{dir_data_path}\select_signal_{symbol_id}_short_15min_1&1&1.json').get('exit_0_0')))
                  }
                ]  for symbol_id in code_ids}

        run_optimization_batch(
            code_ids=code_ids,
            start=start,
            end=end,
            output_dir=output_dir,
            market_data_paths=MK_DATA_PATHS,
            strategy_config=STRATEGY_PARAMS_CONFIG,
            objectives_config=OBJECTIVES_CONFIG,
            backtest_config=BACKTEST_CONFIG,
            save_raw_force_filter_config = SAVE_RAW_FORCE_FILTER_CONFIG,
            population_size=OPTIMIZATION_CONFIG["population_size"],
            n_generations=OPTIMIZATION_CONFIG["n_generations"]  ,
            num_processes=10,
        )

        # 保存回测配置信息到Markdown文件
        import json

        class NumpyEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, (np.integer,)):
                    return int(obj)
                elif isinstance(obj, (np.floating,)):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                return super().default(obj)

        config_md_path = os.path.join(output_dir, "回测配置信息.md")

        with open(config_md_path, 'w', encoding='utf-8') as f:
            f.write("# 回测配置信息\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## 基础配置\n\n")
            f.write(f"- **品种列表 (code_ids)**: `{code_ids}`\n")
            f.write(f"- **开始时间 (start)**: `{start}`\n")
            f.write(f"- **结束时间 (end)**: `{end}`\n\n")

            f.write("## 策略配置 (strategy_config)\n\n")
            f.write("```json\n")
            f.write(json.dumps(STRATEGY_PARAMS_CONFIG, indent=2, ensure_ascii=False, cls=NumpyEncoder))
            f.write("\n```\n\n")

            f.write("## 优化目标配置 (objectives_config)\n\n")
            f.write("```json\n")
            f.write(json.dumps(OBJECTIVES_CONFIG, indent=2, ensure_ascii=False, cls=NumpyEncoder))
            f.write("\n```\n\n")

            f.write("## 回测配置 (backtest_config)\n\n")
            f.write("```json\n")
            f.write(json.dumps(BACKTEST_CONFIG, indent=2, ensure_ascii=False, cls=NumpyEncoder))
            f.write("\n```\n\n")

            f.write("## 过滤配置 (save_raw_force_filter_config)\n\n")
            f.write("```json\n")
            f.write(json.dumps(SAVE_RAW_FORCE_FILTER_CONFIG, indent=2, ensure_ascii=False, cls=NumpyEncoder))
            f.write("\n```\n\n")

            f.write("## 优化参数\n\n")
            f.write(f"- **种群大小 (population_size)**: `{OPTIMIZATION_CONFIG['population_size']}`\n")
            f.write(f"- **迭代代数 (n_generations)**: `{OPTIMIZATION_CONFIG['n_generations']}`\n")

            f.write("---\n\n")
            f.write("*此配置文件由优化脚本自动生成*\n")

        logger.info(f"回测配置信息已保存至: {config_md_path}")
