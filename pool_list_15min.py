
filter_slow_trend_long = ["_",  # COMEX_GC
    "price_higher_sma^21", "price_higher_sma^34", "price_higher_sma^233", 
    "tsi_higher_signal^34^34^17", 
    "rsi_fast_higher_low^13^26", "rsi_fast_higher_low^21^42", 
    "emacd_increase^21^42^21", "emacd_increase^34^68^34", 
    "emacd_histogram_increase^55^110^55", 
    "ema_fast_higher_slow^21^42", "ema_fast_higher_slow^55^110", 
    "aroon_diff_higher0^233", 
    "atr_fast_lower_slow^89^178", "atr_fast_lower_slow^144^288", 
    "emacd_higher_signal^21^42^21", 
    "roc_higher0^55", 
    "adx_plus_higher_minus^34", "adx_plus_higher_minus^55", 
    "skew_negative^233^EMA", 
    "adx_lower_threshold^21^20", 
]
filter_slow_trend_long = ["_",  # COMEX_SI
    "tsi_higher_signal^34^34^17", "tsi_higher_signal^55^55^27", 
    "emacd_histogram_increase^89^178^89", 
    "skew_negative^233^EMA", "skew_negative^377^EMA", 
    "emacd_higher_signal^21^42^21", "emacd_higher_signal^34^68^34", 
    "mass_lower1^13^13", "mass_lower1^21^21", 
    "roc_higher0^233", 
    "adx_plus_higher_minus^8", "adx_plus_higher_minus^13", 
    "kc_neutral^34^17^2.5", 
    "emacd_increase^55^110^55", 
    "aroon_diff_higher0^21", 
    "adx_lower_threshold^34^20", 
    "price_higher_sma^233", 
    "atr_fast_lower_slow^144^288", 
    "rsi_fast_higher_low^34^68", 
    "ema_fast_higher_slow^13^26", 
]
filter_slow_trend_long = ["_",  # COMEX_CL
    "mass_lower1^21^21", "mass_lower1^34^34", "mass_lower1^55^55", 
    "skew_negative^55^EMA", "skew_negative^89^EMA", "skew_negative^144^EMA", 
    "atr_fast_lower_slow^21^42", "atr_fast_lower_slow^34^68", 
    "rvi_neutral^233^67^20^-20", 
    "smi_neutral^55^16^16^20^-20", 

    "adx_lower_threshold^21^20", "adx_lower_threshold^34^20", "adx_lower_threshold^55^20", 
    "price_higher_sma^89", "price_higher_sma^144", 
    "tsi_higher_signal^55^55^27", 
    "adx_plus_higher_minus^8", "adx_plus_higher_minus^13", "adx_plus_higher_minus^21", 
    "emacd_higher_signal^34^68^34", "emacd_higher_signal^55^110^55", 
    "rsi_fast_higher_low^13^26", "rsi_fast_higher_low^55^110", "rsi_fast_higher_low^89^178", 
    "ema_fast_higher_slow^34^68", 
    "roc_higher0^89", 
]
filter_slow_trend_long = ["_",  # COMEX_HG
    "mass_lower1^13^13", "mass_lower1^21^21", 
    "skew_negative^89^EMA", "skew_negative^144^EMA", "skew_negative^233^EMA", 
    "atr_fast_lower_slow^144^288", 
    "kc_neutral^89^44^3.0", 
    "smi_neutral^89^25^25^20^-20", 

    "emacd_increase^34^68^34", "emacd_increase^55^110^55", 
    "adx_plus_higher_minus^8", "adx_plus_higher_minus^13", "adx_plus_higher_minus^21", 
    "aroon_diff_higher0^55", 
    "emacd_histogram_increase^55^110^55", "emacd_histogram_increase^89^178^89", 
    "rsi_fast_higher_low^21^42", "rsi_fast_higher_low^34^68", "rsi_fast_higher_low^55^110", 
    "emacd_higher_signal^34^68^34", "emacd_higher_signal^55^110^55", "emacd_higher_signal^233^466^233", 
    "tsi_higher_signal^55^55^27", "tsi_higher_signal^89^89^44", "tsi_higher_signal^377^377^188", 
    "adx_lower_threshold^34^20", 
]
filter_slow_trend_long = [  # 通用
    "emacd_increase^55^110^55", 
    "emacd_higher_signal^34^68^34", 
    "emacd_histogram_increase^89^178^89", 
    "tsi_higher_signal^55^55^27", 
    "adx_plus_higher_minus^21", 
    "mass_lower1^21^21", 
    "adx_lower_threshold^21^20", 
    "skew_negative^89^EMA", 
]
filter_slow_trend_long = ["_",  # _ 表示不使用任何过滤条件，满足入场条件即可入场
    "ema_fast_higher_slow^13^26", "ema_fast_higher_slow^21^42", "ema_fast_higher_slow^34^68", "ema_fast_higher_slow^55^110", "ema_fast_higher_slow^89^178", "ema_fast_higher_slow^144^288", 
    "emacd_increase^13^26^13", "emacd_increase^21^42^21", "emacd_increase^34^68^34", "emacd_increase^55^110^55", "emacd_increase^89^178^89", "emacd_increase^144^288^144", 
    "emacd_higher_signal^21^42^21", "emacd_higher_signal^34^68^34", "emacd_higher_signal^55^110^55", "emacd_higher_signal^89^178^89", "emacd_higher_signal^144^288^144", "emacd_higher_signal^233^466^233", 
    "emacd_histogram_increase^34^68^34", "emacd_histogram_increase^55^110^55", "emacd_histogram_increase^89^178^89", "emacd_histogram_increase^144^288^144", "emacd_histogram_increase^233^466^233", "emacd_histogram_increase^377^754^377", 
    "tsi_higher_signal^34^34^17", "tsi_higher_signal^55^55^27", "tsi_higher_signal^89^89^44", "tsi_higher_signal^144^144^72", "tsi_higher_signal^233^233^116", "tsi_higher_signal^377^377^188", 
    "adx_plus_higher_minus^8", "adx_plus_higher_minus^13", "adx_plus_higher_minus^21", "adx_plus_higher_minus^34", "adx_plus_higher_minus^55", "adx_plus_higher_minus^89", 
    "roc_higher0^34", "roc_higher0^55", "roc_higher0^89", "roc_higher0^144", "roc_higher0^233", "roc_higher0^377", 
    "aroon_diff_higher0^21", "aroon_diff_higher0^34", "aroon_diff_higher0^55", "aroon_diff_higher0^89", "aroon_diff_higher0^144", "aroon_diff_higher0^233", 
    "rsi_fast_higher_low^13^26", "rsi_fast_higher_low^21^42", "rsi_fast_higher_low^34^68", "rsi_fast_higher_low^55^110", "rsi_fast_higher_low^89^178", "rsi_fast_higher_low^144^288", 
    "price_higher_sma^21", "price_higher_sma^34", "price_higher_sma^55", "price_higher_sma^89", "price_higher_sma^144", "price_higher_sma^233", 
    "kc_neutral^13^6^1.5", "kc_neutral^21^10^2.0", "kc_neutral^34^17^2.5", "kc_neutral^55^27^3.0", "kc_neutral^89^44^3.0", "kc_neutral^144^72^3.5", 
    "smi_neutral^13^4^4^20^-20", "smi_neutral^21^6^6^20^-20", "smi_neutral^34^10^10^20^-20", "smi_neutral^55^16^16^20^-20", "smi_neutral^89^25^25^20^-20", "smi_neutral^144^41^41^20^-20", 
    "atr_fast_lower_slow^13^26", "atr_fast_lower_slow^21^42", "atr_fast_lower_slow^34^68", "atr_fast_lower_slow^55^110", "atr_fast_lower_slow^89^178", "atr_fast_lower_slow^144^288", 
    "mass_lower1^8^8", "mass_lower1^13^13", "mass_lower1^21^21", "mass_lower1^34^34", "mass_lower1^55^55", "mass_lower1^89^89", # 144不行
    "adx_lower_threshold^8^20", "adx_lower_threshold^13^20", "adx_lower_threshold^21^20", "adx_lower_threshold^34^20", "adx_lower_threshold^55^20", "adx_lower_threshold^89^20", 
    "skew_negative^34^EMA", "skew_negative^55^EMA", "skew_negative^89^EMA", "skew_negative^144^EMA", "skew_negative^233^EMA", "skew_negative^377^EMA", 
]

filter_vol_state = []
filter_vol_over = []
filter_divergence = []
filter_fast_trend_long = []

entry_fast_trend_long = [  # COMEX_GC
    "kc_price_crossover_high_2^89^44^3.0", 
    "adx_plus_crossover_minus^34", "adx_plus_crossover_minus^55", 
    "emacd_histogram_start_increase^34^68^34", "emacd_histogram_start_increase^55^110^55", 
    "ema_fast_crossover_slow^13^26", 
    "aroon_diff_crossover0^89", 
    "emacd_start_increase^34^68^34", "emacd_start_increase^55^110^55", 
    "roc_crossover0^21", "roc_crossover0^34", 
    "price_crossover_sma_2^34", 
    "smi_k_crossover_d^34^10^10", 
    "rvi_crossover_signal^377^108", 
    "emacd_crossover_signal^34^68^34", 
]
entry_fast_trend_long = [  # COMEX_SI
    "kc_price_crossover_high_2^13^6^1.5", "kc_price_crossover_high_2^21^10^2.0", "kc_price_crossover_high_2^144^72^3.0", 
    "roc_crossover0^55", "roc_crossover0^89", 
    "bb_price_crossover_high_2^13^1.5", "bb_price_crossover_high_2^21^2.0", "bb_price_crossover_high_2^34^2.5", 
    "adx_plus_crossover_minus^21", "adx_plus_crossover_minus^55", "adx_plus_crossover_minus^89", 
    "emacd_histogram_start_increase^34^68^34", "emacd_histogram_start_increase^144^288^144", 
    "price_crossover_sma_2^89", 
    "aroon_diff_crossover0^55", "aroon_diff_crossover0^89", 
    "emacd_crossover_signal^8^16^8", "emacd_crossover_signal^13^26^13", "emacd_crossover_signal^21^42^21", 
    "smi_k_crossover_d^89^25^25", "smi_k_crossover_d^144^41^41", 
    "ema_fast_crossover_slow^5^10", "ema_fast_crossover_slow^8^16", 
    "rvi_crossover_signal^377^108", 
]
entry_fast_trend_long = [  # COMEX_CL
    "emacd_start_increase^5^10^5", "emacd_start_increase^21^42^21", "emacd_start_increase^34^68^34", 
    "roc_crossover0^89", 
    "emacd_crossover_signal^3^6^3", "emacd_crossover_signal^13^26^13", 
    "smi_k_crossover_d^13^4^4", "smi_k_crossover_d^21^6^6", "smi_k_crossover_d^34^10^10", 
    "adx_plus_crossover_minus^8", "adx_plus_crossover_minus^13", "adx_plus_crossover_minus^21", 
    "aroon_diff_crossover0^21", "aroon_diff_crossover0^89", 
    "emacd_histogram_start_increase^13^26^13", "emacd_histogram_start_increase^21^42^21", "emacd_histogram_start_increase^55^110^55", 
    "rvi_crossover_signal^55^16", "rvi_crossover_signal^89^25", "rvi_crossover_signal^233^67", 
    "kc_price_crossover_high_2^13^6^1.5", "kc_price_crossover_high_2^144^72^3.0", 
    "price_crossover_sma_2^34", "price_crossover_sma_2^21", 
]
entry_fast_trend_long = [  # COMEX_HG
    "rvi_crossover_signal^233^67", "rvi_crossover_signal^377^108", 
    "emacd_histogram_start_increase^55^110^55", 
    "adx_plus_crossover_minus^8", "adx_plus_crossover_minus^13", "adx_plus_crossover_minus^21", 
    "emacd_crossover_signal^13^26^13", "emacd_crossover_signal^21^42^21", "emacd_crossover_signal^34^68^34", 
    "ema_fast_crossover_slow^5^10", "ema_fast_crossover_slow^8^16", "ema_fast_crossover_slow^13^26", 
    "smi_k_crossover_d^21^6^6", "smi_k_crossover_d^34^10^10", "smi_k_crossover_d^144^41^41", 
    "roc_crossover0^34", 
    "emacd_start_increase^34^68^34", 
    "price_crossover_sma_2^21", 
    "bb_price_crossover_high_2^34^2.5", 
    "kc_price_crossover_high_2^89^44^3.0", 
]
entry_fast_trend_long = [  # 通用
    "adx_plus_crossover_minus^13", 
    "kc_price_crossover_high_2^55^27^3.0", 
    "smi_k_crossover_d^34^10^10", 
    "emacd_histogram_start_increase^55^110^55", 
    "roc_crossover0^34", 
    "aroon_diff_crossover0^89", 
    "rvi_crossover_signal^89^25", 
    "bb_price_crossover_high_2^34^2.5", 
    "emacd_crossover_signal^21^42^21", 
    "emacd_start_increase^34^68^34", 
    "price_crossover_sma_2^21", 
]
entry_fast_trend_long = [
    "adx_plus_crossover_minus^8", "adx_plus_crossover_minus^13", "adx_plus_crossover_minus^21", "adx_plus_crossover_minus^34", "adx_plus_crossover_minus^55", "adx_plus_crossover_minus^89",
    "kc_price_crossover_high_2^13^6^1.5", "kc_price_crossover_high_2^21^10^2.0", "kc_price_crossover_high_2^34^17^2.5", "kc_price_crossover_high_2^55^27^3.0", "kc_price_crossover_high_2^89^44^3.0", "kc_price_crossover_high_2^144^72^3.0", 
    "smi_k_crossover_d^13^4^4", "smi_k_crossover_d^21^6^6", "smi_k_crossover_d^34^10^10", "smi_k_crossover_d^55^16^16", "smi_k_crossover_d^89^25^25", "smi_k_crossover_d^144^41^41", 
    "emacd_histogram_start_increase^13^26^13", "emacd_histogram_start_increase^21^42^21", "emacd_histogram_start_increase^34^68^34", "emacd_histogram_start_increase^55^110^55", "emacd_histogram_start_increase^89^178^89", "emacd_histogram_start_increase^144^288^144", 
    "roc_crossover0^13", "roc_crossover0^21", "roc_crossover0^34", "roc_crossover0^55", "roc_crossover0^89", "roc_crossover0^144", 
    "aroon_diff_crossover0^21", "aroon_diff_crossover0^34", "aroon_diff_crossover0^55", "aroon_diff_crossover0^89", "aroon_diff_crossover0^144", "aroon_diff_crossover0^233", 
    "rvi_crossover_signal^34^10", "rvi_crossover_signal^55^16", "rvi_crossover_signal^89^25", "rvi_crossover_signal^144^41", "rvi_crossover_signal^233^67", "rvi_crossover_signal^377^108", 
    "bb_price_crossover_high_2^8^1.5", "bb_price_crossover_high_2^13^1.5", "bb_price_crossover_high_2^21^2.0", "bb_price_crossover_high_2^34^2.5", "bb_price_crossover_high_2^55^3.0", "bb_price_crossover_high_2^89^3.0", 
    "emacd_crossover_signal^3^6^3", "emacd_crossover_signal^5^10^5", "emacd_crossover_signal^8^16^8", "emacd_crossover_signal^13^26^13", "emacd_crossover_signal^21^42^21", "emacd_crossover_signal^34^68^34", 
    "ema_fast_crossover_slow^5^10", "ema_fast_crossover_slow^8^16", "ema_fast_crossover_slow^13^26", "ema_fast_crossover_slow^21^42", "ema_fast_crossover_slow^34^68", "ema_fast_crossover_slow^55^110", 
    "emacd_start_increase^5^10^5", "emacd_start_increase^8^16^8", "emacd_start_increase^13^26^13", "emacd_start_increase^21^42^21", "emacd_start_increase^34^68^34", "emacd_start_increase^55^110^55", 
    "price_crossover_sma_2^8", "price_crossover_sma_2^13", "price_crossover_sma_2^21", "price_crossover_sma_2^34", "price_crossover_sma_2^55", "price_crossover_sma_2^89", 
]
entry_fast_trend_long_nick = [

    # "tp_high_1^5^0",
    # "tp_high_1^5^1",
    # "tp_high_1^8^0",
    # "tp_high_1^8^1",
    # "tp_high_1^16^0",
    # "tp_high_1^16^1",
    # "tp_high_1^24^0",
    # "tp_high_1^24^1",
    # "tp_high_1^34^0",
    # "tp_high_1^34^1",

    "tp_high_2^5^1",
    "tp_high_2^8^1",
    "tp_high_2^16^1",
    "tp_high_2^24^1",

    "tp_high_2^5^0",
    "tp_high_2^8^0",
    "tp_high_2^16^0",
    "tp_high_2^24^0",
    "tp_high_2^34^0",

    "s_tp_high_1^8^0^0","s_tp_high_1^8^0^1","s_tp_high_1^8^0^2",
    # "s_tp_high_1^18^0^0","s_tp_high_1^18^0^1","s_tp_high_1^18^0^2",
    "s_tp_high_1^34^0^0","s_tp_high_1^34^0^1","s_tp_high_1^34^0^2",

    "tp_low_1^15^0","tp_low_2^15^0", "s_tp_low_1^15^0^0","s_tp_low_1^15^0^1","s_tp_low_1^15^0^2",
    # "tp_low_1^23^0","tp_low_2^23^0", "s_tp_low_1^23^0^0","s_tp_low_1^23^0^1","s_tp_low_1^23^0^2",
    "tp_low_1^31^0","tp_low_2^31^0", "s_tp_low_1^31^0^0","s_tp_low_1^31^0^1","s_tp_low_1^31^0^2",

    # "tp_low_1^7^1" , "tp_low_2^7^1", "s_tp_low_1^7^1^0" ,"s_tp_low_1^7^1^1" ,"s_tp_low_1^7^1^2",
    # "tp_low_1^15^1","tp_low_2^15^1", "s_tp_low_1^15^1^0","s_tp_low_1^15^1^1","s_tp_low_1^15^1^2",
    # "tp_low_1^23^1","tp_low_2^23^1", "s_tp_low_1^23^1^0","s_tp_low_1^23^1^1","s_tp_low_1^23^1^2",
    # "tp_low_1^31^1","tp_low_2^31^1", "s_tp_low_1^31^1^0","s_tp_low_1^31^1^1","s_tp_low_1^31^1^2",



]
exit_signal_general = [
    "trailing_stop^34^2.5",
    "trailing_stop^34^3.0",
    "trailing_stop^34^3.5",
]

exit_signal_short = [  # COMEX_GC
    "emacd_crossunder_signal^8^16^8", "emacd_crossunder_signal^13^26^13", "emacd_crossunder_signal^21^42^21", 
    "emacd_histogram_start_decrease^55^110^55", "emacd_histogram_start_decrease^89^178^89", "emacd_histogram_start_decrease^377^754^377", 
    "kc_price_crossunder_high^21^10^2.0", "kc_price_crossunder_high^34^17^2.5", "kc_price_crossunder_high^55^27^3.0", 
    "roc_crossunder0^13", "roc_crossunder0^34", "roc_crossunder0^89", 
    "smi_k_crossunder_d^21^6^6", "smi_k_crossunder_d^34^10^10", 
    "aroon_diff_crossunder0^21", 
    "adx_plus_crossunder_minus^34", 
    "emacd_start_decrease^144^288^144", 
    "price_crossunder_sma_2^144", 
    "bb_price_crossunder_high^34^2.5", 
    "rvi_crossunder_signal^34^10", 
]
exit_signal_short = [  # COMEX_SI
    "emacd_crossunder_signal^8^16^8", "emacd_crossunder_signal^13^26^13", "emacd_crossunder_signal^21^42^21", 
    "smi_k_crossunder_d^13^4^4", "smi_k_crossunder_d^21^6^6", "smi_k_crossunder_d^34^10^10", 
    "bb_price_crossunder_high^21^2.0", 
    "roc_crossunder0^21", "roc_crossunder0^34", 
    "emacd_histogram_start_decrease^34^68^34", "emacd_histogram_start_decrease^55^110^55", "emacd_histogram_start_decrease^89^178^89", 
    "adx_plus_crossunder_minus^13", "adx_plus_crossunder_minus^55", 
    "aroon_diff_crossunder0^21", 
    "kc_price_crossunder_high^89^44^3.0", "kc_price_crossunder_high^144^72^3.0", 
    "emacd_start_decrease^34^68^34", "emacd_start_decrease^55^110^55", 
    "rvi_crossunder_signal^144^41", 
]
exit_signal_short = [  # COMEX_CL
    "smi_k_crossunder_d^34^10^10", "smi_k_crossunder_d^55^16^16", "smi_k_crossunder_d^89^25^25", 
    "roc_crossunder0^55", "roc_crossunder0^89", "roc_crossunder0^144", 
    "bb_price_crossunder_high^144^3.0", "bb_price_crossunder_high^233^3.5", 
    "aroon_diff_crossunder0^34", "aroon_diff_crossunder0^55", "aroon_diff_crossunder0^144", 
    "emacd_crossunder_signal^21^42^21", "emacd_crossunder_signal^55^110^55", 
    "emacd_start_decrease^89^178^89", "emacd_start_decrease^144^288^144", 
    "price_crossunder_sma_2^144", 
    "kc_price_crossunder_high^55^27^3.0", "kc_price_crossunder_high^144^72^3.0", 
    "emacd_histogram_start_decrease^233^466^233", 
    "adx_plus_crossunder_minus^89", 
]
exit_signal_short = [  # COMEX_HG
    "kc_price_crossunder_high^21^10^2.0", "kc_price_crossunder_high^34^17^2.5", "kc_price_crossunder_high^233^116^3.5", 
    "adx_plus_crossunder_minus^34", "adx_plus_crossunder_minus^55", "adx_plus_crossunder_minus^89", 
    "smi_k_crossunder_d^13^4^4", "smi_k_crossunder_d^21^6^6", "smi_k_crossunder_d^55^16^16", 
    "roc_crossunder0^13", "roc_crossunder0^144", 
    "emacd_crossunder_signal^8^16^8", 
    "aroon_diff_crossunder0^21", "aroon_diff_crossunder0^34", "aroon_diff_crossunder0^55", 
    "bb_price_crossunder_high^89^3.0", "bb_price_crossunder_high^233^3.5", 
    "emacd_start_decrease^233^466^233", 
    "emacd_histogram_start_decrease^89^178^89", 
    "price_crossunder_sma_2^144", 
]
exit_signal_short = [  # 通用
    "adx_plus_crossunder_minus^55", 
    "kc_price_crossunder_high^55^27^3.0", 
    "smi_k_crossunder_d^34^10^10", 
    "emacd_histogram_start_decrease^89^178^89", 
    "roc_crossunder0^34", 
    "aroon_diff_crossunder0^21", 
    "emacd_crossunder_signal^21^42^21", 
    "price_crossunder_sma_2^144", 
]
exit_signal_short = ["_",  # _ 表示不使用任何出场条件
    "adx_plus_crossunder_minus^13", "adx_plus_crossunder_minus^21", "adx_plus_crossunder_minus^34", "adx_plus_crossunder_minus^55", "adx_plus_crossunder_minus^89", "adx_plus_crossunder_minus^144", 
    "kc_price_crossunder_high^21^10^2.0", "kc_price_crossunder_high^34^17^2.5", "kc_price_crossunder_high^55^27^3.0", "kc_price_crossunder_high^89^44^3.0", "kc_price_crossunder_high^144^72^3.0", "kc_price_crossunder_high^233^116^3.5", 
    "smi_k_crossunder_d^13^4^4", "smi_k_crossunder_d^21^6^6", "smi_k_crossunder_d^34^10^10", "smi_k_crossunder_d^55^16^16", "smi_k_crossunder_d^89^25^25", "smi_k_crossunder_d^144^41^41", 
    "emacd_histogram_start_decrease^34^68^34", "emacd_histogram_start_decrease^55^110^55", "emacd_histogram_start_decrease^89^178^89", "emacd_histogram_start_decrease^144^288^144", "emacd_histogram_start_decrease^233^466^233", "emacd_histogram_start_decrease^377^754^377", 
    "roc_crossunder0^13", "roc_crossunder0^21", "roc_crossunder0^34", "roc_crossunder0^55", "roc_crossunder0^89", "roc_crossunder0^144", 
    "aroon_diff_crossunder0^21", "aroon_diff_crossunder0^34", "aroon_diff_crossunder0^55", "aroon_diff_crossunder0^89", "aroon_diff_crossunder0^144", "aroon_diff_crossunder0^233", # 13不行
    "rvi_crossunder_signal^34^10", "rvi_crossunder_signal^55^16", "rvi_crossunder_signal^89^25", "rvi_crossunder_signal^144^41", "rvi_crossunder_signal^233^67", "rvi_crossunder_signal^377^108", 
    "bb_price_crossunder_high^21^2.0", "bb_price_crossunder_high^34^2.5", "bb_price_crossunder_high^55^3.0", "bb_price_crossunder_high^89^3.0", "bb_price_crossunder_high^144^3.0", "bb_price_crossunder_high^233^3.5",  # 13不行
    "emacd_crossunder_signal^8^16^8", "emacd_crossunder_signal^13^26^13", "emacd_crossunder_signal^21^42^21", "emacd_crossunder_signal^34^68^34", "emacd_crossunder_signal^55^110^55", "emacd_crossunder_signal^89^178^89",  # 5不行
    "emacd_start_decrease^21^42^21", "emacd_start_decrease^34^68^34", "emacd_start_decrease^55^110^55", "emacd_start_decrease^89^178^89", "emacd_start_decrease^144^288^144", "emacd_start_decrease^233^466^233", 
    "price_crossunder_sma_2^13", "price_crossunder_sma_2^21", "price_crossunder_sma_2^34", "price_crossunder_sma_2^55", "price_crossunder_sma_2^89", "price_crossunder_sma_2^144",  # 8不行
    "ema_fast_crossunder_slow^5^10", "ema_fast_crossunder_slow^8^16", "ema_fast_crossunder_slow^13^26", "ema_fast_crossunder_slow^21^42", "ema_fast_crossunder_slow^34^68", "ema_fast_crossunder_slow^55^110", 
]

