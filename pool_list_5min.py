
entry_filter_long_slow = ["_",  # _ 表示不使用任何过滤条件，满足入场条件即可入场
    # "sma_increase^55", "sma_increase^89", "sma_increase^144", 
    "sma_increase_2^55", "sma_increase_2^89", "sma_increase_2^144", 
    # "sma_fast_higher_slow^55^110", "sma_fast_higher_slow^89^178", "sma_fast_higher_slow^144^288", 
    "sma_fast_higher_slow_and_increase^55^110", "sma_fast_higher_slow_and_increase^89^178", "sma_fast_higher_slow_and_increase^144^288", 
    # "sma_fast_higher_slow_or_increase^55^110", "sma_fast_higher_slow_or_increase^89^178", "sma_fast_higher_slow_or_increase^144^288", 
    # "sma_first_higher_second^55^55", "sma_first_higher_second^89^89", "sma_first_higher_second^144^144", 
    # "sma_first_higher_second_and_increase^55^55", "sma_first_higher_second_and_increase^89^89", "sma_first_higher_second_and_increase^144^144", 
    # "sma_first_higher_second_or_increase^55^55", "sma_first_higher_second_or_increase^89^89", "sma_first_higher_second_or_increase^144^144", 
    # "ema_increase^55", "ema_increase^89", "ema_increase^144", 
    # "ema_fast_higher_slow^55^110", "ema_fast_higher_slow^89^178", "ema_fast_higher_slow^144^288", 
    # "ema_first_higher_second^55^55", "ema_first_higher_second^89^89", "ema_first_higher_second^144^144", 
]
entry_filter_long_slow = ["_",  # _ 表示不使用任何过滤条件，满足入场条件即可入场
    "smacd_signal_higher0^55^110^55", "smacd_signal_higher0^89^178^89", "smacd_signal_higher0^144^288^144", 
    # "smacd_higher_signal^55^110^55", "smacd_higher_signal^89^178^89", "smacd_higher_signal^144^288^144", 
    # "smacd_higher_signal_and_increase^55^110^55", "smacd_higher_signal_and_increase^89^178^89", "smacd_higher_signal_and_increase^144^288^144", 
    # "smacd_higher_signal_or_increase^55^110^55", "smacd_higher_signal_or_increase^89^178^89", "smacd_higher_signal_or_increase^144^288^144", 
    # "smacd2_signal_higher0^55^55^55", "smacd2_signal_higher0^89^89^89", "smacd2_signal_higher0^144^144^144", 
    # "smacd2_higher_signal^55^55^55", "smacd2_higher_signal^89^89^89", "smacd2_higher_signal^144^144^144", 
    # "smacd2_higher_signal_and_increase^55^55^55", "smacd2_higher_signal_and_increase^89^89^89", "smacd2_higher_signal_and_increase^144^144^144", 
    # "smacd2_higher_signal_or_increase^55^55^55", "smacd2_higher_signal_or_increase^89^89^89", "smacd2_higher_signal_or_increase^144^144^144", 
    # "emacd_signal_higher0^55^110^55", "emacd_signal_higher0^89^178^89", "emacd_signal_higher0^144^288^144", 
    # "emacd_higher_signal^55^110^55", "emacd_higher_signal^89^178^89", "emacd_higher_signal^144^288^144", 
    "emacd_higher_signal_and_increase^55^110^55", "emacd_higher_signal_and_increase^89^178^89", "emacd_higher_signal_and_increase^144^288^144", 
    # "emacd_higher_signal_or_increase^55^110^55", "emacd_higher_signal_or_increase^89^178^89", "emacd_higher_signal_or_increase^144^288^144", 
    # "emacd2_signal_higher0^55^55^55", "emacd2_signal_higher0^89^89^89", "emacd2_signal_higher0^144^144^144", 
    # "emacd2_higher_signal^55^55^55", "emacd2_higher_signal^89^89^89", "emacd2_higher_signal^144^144^144", 
    # "emacd2_higher_signal_and_increase^55^55^55", "emacd2_higher_signal_and_increase^89^89^89", "emacd2_higher_signal_and_increase^144^144^144", 
    # "emacd2_higher_signal_or_increase^55^55^55", "emacd2_higher_signal_or_increase^89^89^89", "emacd2_higher_signal_or_increase^144^144^144", 
]
entry_filter_long_slow = ["_",  # _ 表示不使用任何过滤条件，满足入场条件即可入场
    "adx_plus_higher_minus^34", "adx_plus_higher_minus^55", "adx_plus_higher_minus^89", 
    "tsi_higher_signal^55^27^27", "tsi_higher_signal^89^44^44", "tsi_higher_signal^144^72^72", 
    # "rsi_fast_higher_low^34^55", "rsi_fast_higher_low^55^89", "rsi_fast_higher_low^89^144", 
    # "rsi_fast_higher_low^34^68", "rsi_fast_higher_low^55^110", "rsi_fast_higher_low^89^178", 
    "rsi_fast_higher_low^34^89", "rsi_fast_higher_low^55^144", "rsi_fast_higher_low^89^233", 
    # "supertrend_long_period^55^4.0", "supertrend_long_period^89^4.5", "supertrend_long_period^144^5.0", 
    # "supertrend_long_period^55^4.5", "supertrend_long_period^89^5.0", "supertrend_long_period^144^5.5", 
    "ma_atr_long_period^55^27^1.3", "ma_atr_long_period^89^44^1.3", "ma_atr_long_period^144^72^1.3", 
    # "ma_atr_long_period^55^27^1.7", "ma_atr_long_period^89^44^1.7", "ma_atr_long_period^144^72^1.7", 
    # "ma_atr_long_period^55^27^2.1", "ma_atr_long_period^89^44^2.1", "ma_atr_long_period^144^72^2.1", 
]
entry_filter_long_slow = ["_",  # _ 表示不使用任何过滤条件，满足入场条件即可入场
    "sma_increase_2^55", "sma_increase_2^89", "sma_increase_2^144", 
    "sma_fast_higher_slow_and_increase^55^110", "sma_fast_higher_slow_and_increase^89^178", "sma_fast_higher_slow_and_increase^144^288", 
    "smacd_signal_higher0^55^110^55", "smacd_signal_higher0^89^178^89", "smacd_signal_higher0^144^288^144", 
    "emacd_higher_signal_and_increase^55^110^55", "emacd_higher_signal_and_increase^89^178^89", "emacd_higher_signal_and_increase^144^288^144", 
    "adx_plus_higher_minus^34", "adx_plus_higher_minus^55", "adx_plus_higher_minus^89", 
    "tsi_higher_signal^55^27^27", "tsi_higher_signal^89^44^44", "tsi_higher_signal^144^72^72", 
    "rsi_fast_higher_low^34^89", "rsi_fast_higher_low^55^144", "rsi_fast_higher_low^89^233", 
    "ma_atr_long_period^55^27^1.3", "ma_atr_long_period^89^44^1.3", "ma_atr_long_period^144^72^1.3", 
]
entry_filter_long_slow = [
    "smacd_signal_higher0^89^178^89", 
    "sma_fast_higher_slow_and_increase^55^110", "sma_fast_higher_slow_and_increase^89^178", "sma_fast_higher_slow_and_increase^144^288", 
    "adx_plus_higher_minus^34", "adx_plus_higher_minus^55", "adx_plus_higher_minus^89", 
    "rsi_fast_higher_low^89^233", 
    "sma_increase_2^55", "sma_increase_2^89", 
    "emacd_higher_signal_and_increase^55^110^55", "emacd_higher_signal_and_increase^144^288^144", 
]


entry_filter_v_hl = ["_",  # _ 表示不使用任何过滤条件，满足入场条件即可入场
    # "atr_fast_higher_slow^21^42", "atr_fast_higher_slow^34^68", "atr_fast_higher_slow^55^110",  # *2
    # "atr_fast_lower_slow^21^42", "atr_fast_lower_slow^34^68", "atr_fast_lower_slow^55^110", 
    # "atr_fast_higher_slow^21^84", "atr_fast_higher_slow^34^136", "atr_fast_higher_slow^55^220",  # *4
    # "atr_fast_lower_slow^21^84", "atr_fast_lower_slow^34^136", "atr_fast_lower_slow^55^220", 
    "atr_fast_higher_slow^21^126", "atr_fast_higher_slow^34^204", "atr_fast_higher_slow^55^330",  # *6
    # "atr_fast_lower_slow^21^126", "atr_fast_lower_slow^34^204", "atr_fast_lower_slow^55^330", 
]
entry_filter_v_hl = ["_",  # _ 表示不使用任何过滤条件，满足入场条件即可入场
    "mass_higher1^34^17", "mass_higher1^55^27", "mass_higher1^89^44", 
    # "mass_lower1^34^17", "mass_lower1^55^27", "mass_lower1^89^44", 
    # "mass_higher1^34^34", "mass_higher1^55^55", "mass_higher1^89^89", 
    # "mass_lower1^34^34", "mass_lower1^55^55", "mass_lower1^89^89", 
    # "adx_higher_threshold^21^25", "adx_higher_threshold^34^25", "adx_higher_threshold^55^25", 
    "adx_lower_threshold^21^25", "adx_lower_threshold^34^25", "adx_lower_threshold^55^25", 
    # "skew_positive^34^EMA", "skew_positive^55^EMA", "skew_positive^89^EMA", 
    # "skew_negative^34^EMA", "skew_negative^55^EMA", "skew_negative^89^EMA", 
    "convexity_higher1^34^SMA", "convexity_higher1^55^SMA", "convexity_higher1^89^SMA", 
    # "convexity_lower1^34^SMA", "convexity_lower1^55^SMA", "convexity_lower1^89^SMA", 
    # "skew_positive^34^SMA", "skew_positive^55^SMA", "skew_positive^89^SMA", 
    "skew_negative^34^SMA", "skew_negative^55^SMA", "skew_negative^89^SMA", 
]
entry_filter_v_hl = ["_",  # _ 表示不使用任何过滤条件，满足入场条件即可入场
    "atr_fast_higher_slow^21^126", "atr_fast_higher_slow^34^204", "atr_fast_higher_slow^55^330",
    "mass_higher1^34^17", "mass_higher1^55^27", "mass_higher1^89^44", 
    "adx_lower_threshold^21^25", "adx_lower_threshold^34^25", "adx_lower_threshold^55^25", 
    "convexity_higher1^34^SMA", "convexity_higher1^55^SMA", "convexity_higher1^89^SMA", 
    "skew_negative^34^SMA", "skew_negative^55^SMA", "skew_negative^89^SMA", 
    "adx_lower_threshold_and_smacd_signal_higher0^21^42^21^25^1.0", "adx_lower_threshold_and_smacd_signal_higher0^34^68^34^25^1.0", "adx_lower_threshold_and_smacd_signal_higher0^55^110^55^25^1.0", 
    "atr_fast_higher_slow_and_sma_fast_higher_slow_and_increase^21^42^4.236", "atr_fast_higher_slow_and_sma_fast_higher_slow_and_increase^34^68^4.236", "atr_fast_higher_slow_and_sma_fast_higher_slow_and_increase^55^110^4.236", 
]
entry_filter_v_hl = [
    "atr_fast_higher_slow_and_sma_fast_higher_slow_and_increase^21^42^4.236", "atr_fast_higher_slow_and_sma_fast_higher_slow_and_increase^34^68^4.236", "atr_fast_higher_slow_and_sma_fast_higher_slow_and_increase^55^110^4.236", 
    "mass_higher1^55^27", "mass_higher1^89^44", 
    "adx_lower_threshold_and_smacd_signal_higher0^21^42^21^25^1.0", 
    "skew_negative^55^SMA", "skew_negative^89^SMA", 
    "atr_fast_higher_slow^21^126", "atr_fast_higher_slow^34^204", "atr_fast_higher_slow^55^330",
]


entry_filter_v_over = ["_",  # _ 表示不使用任何过滤条件，满足入场条件即可入场
    # "bb_not_overbought^21^2.0", "bb_not_overbought^34^2.5", "bb_not_overbought^55^3.0", 
    "bb_neutral^21^2.0", "bb_neutral^34^2.5", "bb_neutral^55^3.0", 
    # "bb_not_oversold^21^2.0", "bb_not_oversold^34^2.5", "bb_not_oversold^55^3.0", 
    # "bb_overbought^21^2.0", "bb_overbought^34^2.5", "bb_overbought^55^3.0", 
    # "bb_oversold^21^2.0", "bb_oversold^34^2.5", "bb_oversold^55^3.0", 
]
entry_filter_v_over = ["_",  # _ 表示不使用任何过滤条件，满足入场条件即可入场
    # "kc_not_overbought^21^10^2.0", "kc_not_overbought^34^17^2.5", "kc_not_overbought^55^27^3.0", 
    "kc_neutral^21^10^2.0", "kc_neutral^34^17^2.5", "kc_neutral^55^27^3.0", 
    # "kc_not_oversold^21^10^2.0", "kc_not_oversold^34^17^2.5", "kc_not_oversold^55^27^3.0", 
    # "kc_not_overbought^21^10^2.0", "kc_not_overbought^34^17^2.5", "kc_not_overbought^55^27^3.0", 
    # "kc_not_oversold^21^10^2.0", "kc_not_oversold^34^17^2.5", "kc_not_oversold^55^27^3.0", 
]
entry_filter_v_over = ["_",  # _ 表示不使用任何过滤条件，满足入场条件即可入场
    # "tsi_not_overbought^21^10^25", "tsi_not_overbought^34^17^25", "tsi_not_overbought^55^27^25", 
    "tsi_neutral^21^10^25^-25", "tsi_neutral^34^17^25^-25", "tsi_neutral^55^27^25^-25", 
    # "tsi_not_oversold^21^10^-25", "tsi_not_oversold^34^17^-25", "tsi_not_oversold^55^27^-25", 
    # "tsi_overbought^21^10^25", "tsi_overbought^34^17^25", "tsi_overbought^55^27^25", 
    # "tsi_oversold^21^10^-25", "tsi_oversold^34^17^-25", "tsi_oversold^55^27^-25", 
]
entry_filter_v_over = ["_",  # _ 表示不使用任何过滤条件，满足入场条件即可入场
    # "rsi_not_overbought^13^70", "rsi_not_overbought^21^70", "rsi_not_overbought^34^70", 
    "rsi_neutral^13^70^30", "rsi_neutral^21^70^30", "rsi_neutral^34^70^30", 
    # "rsi_not_oversold^13^30", "rsi_not_oversold^21^30", "rsi_not_oversold^34^30", 
    # "rsi_overbought^13^70", "rsi_overbought^21^70", "rsi_overbought^34^70", 
    # "rsi_oversold^13^30", "rsi_oversold^21^30", "rsi_oversold^34^30", 
]
entry_filter_v_over = ["_",  # _ 表示不使用任何过滤条件，满足入场条件即可入场
    # "stoch_not_overbought^21^5^5^80", "stoch_not_overbought^34^9^9^80", "stoch_not_overbought^55^14^14^80", 
    "stoch_neutral^21^5^5^80^20", "stoch_neutral^34^9^9^80^20", "stoch_neutral^55^14^14^80^20", 
    # "stoch_not_oversold^21^5^5^20", "stoch_not_oversold^34^9^9^20", "stoch_not_oversold^55^14^14^20", 
    # "stoch_overbought^21^5^5^80", "stoch_overbought^34^9^9^80", "stoch_overbought^55^14^14^80", 
    # "stoch_oversold^21^5^5^20", "stoch_oversold^34^9^9^20", "stoch_oversold^55^14^14^20", 
]
entry_filter_v_over = ["_",  # _ 表示不使用任何过滤条件，满足入场条件即可入场
    # "kdj_not_overbought^21^5^5^80", "kdj_not_overbought^34^9^9^80", "kdj_not_overbought^55^14^14^80", 
    "kdj_neutral^21^5^5^80^20", "kdj_neutral^34^9^9^80^20", "kdj_neutral^55^14^14^80^20", 
    # "kdj_not_oversold^21^5^5^20", "kdj_not_oversold^34^9^9^20", "kdj_not_oversold^55^14^14^20", 
    # "kdj_overbought^21^5^5^80", "kdj_overbought^34^9^9^80", "kdj_overbought^55^14^14^80", 
    # "kdj_oversold^21^5^5^20", "kdj_oversold^34^9^9^20", "kdj_oversold^55^14^14^20", 
]
entry_filter_v_over = ["_",  # _ 表示不使用任何过滤条件，满足入场条件即可入场
    # "smi_not_overbought^21^5^5^20", "smi_not_overbought^34^9^9^20", "smi_not_overbought^55^14^14^20", 
    "smi_neutral^21^5^5^20^-20", "smi_neutral^34^9^9^20^-20", "smi_neutral^55^14^14^20^-20", 
    # "smi_not_oversold^21^5^5^-20", "smi_not_oversold^34^9^9^-20", "smi_not_oversold^55^14^14^-20", 
    # "smi_overbought^21^5^5^20", "smi_overbought^34^9^9^20", "smi_overbought^55^14^14^20", 
    # "smi_oversold^21^5^5^-20", "smi_oversold^34^9^9^-20", "smi_oversold^55^14^14^-20", 
]
entry_filter_v_over = ["_",  # _ 表示不使用任何过滤条件，满足入场条件即可入场
    # "rvi_not_overbought^21^5^20", "rvi_not_overbought^34^9^20", "rvi_not_overbought^55^14^20", 
    "rvi_neutral^21^5^20^-20", "rvi_neutral^34^9^20^-20", "rvi_neutral^55^14^20^-20", 
    # "rvi_not_oversold^21^5^-20", "rvi_not_oversold^34^9^-20", "rvi_not_oversold^55^14^-20", 
    # "rvi_overbought^21^5^20", "rvi_overbought^34^9^20", "rvi_overbought^55^14^20", 
    # "rvi_oversold^21^5^-20", "rvi_oversold^34^9^-20", "rvi_oversold^55^14^-20", 
]
entry_filter_v_over = ["_",  # _ 表示不使用任何过滤条件，满足入场条件即可入场
    # "bb_neutral^21^2.0", "bb_neutral^34^2.5", "bb_neutral^55^3.0", 
    "kc_neutral^21^10^2.0", "kc_neutral^34^17^2.5", "kc_neutral^55^27^3.0", 
    "tsi_neutral^21^10^25^-25", "tsi_neutral^34^17^25^-25", "tsi_neutral^55^27^25^-25", 
    # "rsi_neutral^13^70^30", "rsi_neutral^21^70^30", "rsi_neutral^34^70^30", 
    # "stoch_neutral^21^5^5^80^20", "stoch_neutral^34^9^9^80^20", "stoch_neutral^55^14^14^80^20", 
    # "kdj_neutral^21^5^5^80^20", "kdj_neutral^34^9^9^80^20", "kdj_neutral^55^14^14^80^20", 
    "smi_neutral^21^5^5^20^-20", "smi_neutral^34^9^9^20^-20", "smi_neutral^55^14^14^20^-20", 
    # "rvi_neutral^21^5^20^-20", "rvi_neutral^34^9^20^-20", "rvi_neutral^55^14^20^-20", 
]
entry_filter_v_over = [
    "kc_neutral^34^17^2.5", "kc_neutral^55^27^3.0", 
    "smi_neutral^21^5^5^20^-20", "smi_neutral^55^14^14^20^-20", 
]


entry_filter_long_fast = ["_",  # _ 表示不使用任何过滤条件，满足入场条件即可入场
    "sma_increase^13", "sma_increase^21", "sma_increase^34", 
    "sma_increase_2^13", "sma_increase_2^21", "sma_increase_2^34", 
    "sma_fast_higher_slow^13^26", "sma_fast_higher_slow^21^42", "sma_fast_higher_slow^34^68", 
    "sma_fast_higher_slow_and_increase^13^26", "sma_fast_higher_slow_and_increase^21^42", "sma_fast_higher_slow_and_increase^34^68", 
    "sma_fast_higher_slow_or_increase^13^26", "sma_fast_higher_slow_or_increase^21^42", "sma_fast_higher_slow_or_increase^34^68", 
    "sma_first_higher_second^13^13", "sma_first_higher_second^21^21", "sma_first_higher_second^34^34", 
    "sma_first_higher_second_and_increase^13^13", "sma_first_higher_second_and_increase^21^21", "sma_first_higher_second_and_increase^34^34", 
    "sma_first_higher_second_or_increase^13^13", "sma_first_higher_second_or_increase^21^21",  "sma_first_higher_second_or_increase^34^34", 
    "ema_increase^13", "ema_increase^21", "ema_increase^34", 
    "ema_fast_higher_slow^13^26", "ema_fast_higher_slow^21^42", "ema_fast_higher_slow^34^68", 
    "ema_first_higher_second^13^13", "ema_first_higher_second^21^21", "ema_first_higher_second^34^34", 
    "smacd_signal_higher0^13^26^13", "smacd_signal_higher0^21^42^21", "smacd_signal_higher0^34^68^34", 
    "smacd_higher_signal^13^26^13", "smacd_higher_signal^21^42^21", "smacd_higher_signal^34^68^34", 
    "smacd_higher_signal_and_increase^13^26^13", "smacd_higher_signal_and_increase^21^42^21", "smacd_higher_signal_and_increase^34^68^34", 
    "smacd_higher_signal_or_increase^13^26^13", "smacd_higher_signal_or_increase^21^42^21", "smacd_higher_signal_or_increase^34^68^34", 
    "smacd2_signal_higher0^13^13^13", "smacd2_signal_higher0^21^21^21", "smacd2_signal_higher0^34^34^34", 
    "smacd2_higher_signal^13^13^13", "smacd2_higher_signal^21^21^21", "smacd2_higher_signal^34^34^34", 
    "smacd2_higher_signal_and_increase^13^13^13", "smacd2_higher_signal_and_increase^21^21^21", "smacd2_higher_signal_and_increase^34^34^34", 
    "smacd2_higher_signal_or_increase^13^13^13", "smacd2_higher_signal_or_increase^21^21^21", "smacd2_higher_signal_or_increase^34^34^34", 
    "emacd_signal_higher0^13^26^13", "emacd_signal_higher0^21^42^21", "emacd_signal_higher0^34^68^34", 
    "emacd_higher_signal^13^26^13", "emacd_higher_signal^21^42^21", "emacd_higher_signal^34^68^34", 
    "emacd_higher_signal_and_increase^13^26^13", "emacd_higher_signal_and_increase^21^42^21", "emacd_higher_signal_and_increase^34^68^34", 
    "emacd_higher_signal_or_increase^13^26^13", "emacd_higher_signal_or_increase^21^42^21", "emacd_higher_signal_or_increase^34^68^34", 
    "emacd2_signal_higher0^13^13^13", "emacd2_signal_higher0^21^21^21", "emacd2_signal_higher0^34^34^34", 
    "emacd2_higher_signal^13^13^13", "emacd2_higher_signal^21^21^21", "emacd2_higher_signal^34^34^34", 
    "emacd2_higher_signal_and_increase^13^13^13", "emacd2_higher_signal_and_increase^21^21^21", "emacd2_higher_signal_and_increase^34^34^34", 
    "emacd2_higher_signal_or_increase^13^13^13", "emacd2_higher_signal_or_increase^21^21^21", "emacd2_higher_signal_or_increase^34^34^34", 
    "adx_plus_higher_minus^8", "adx_plus_higher_minus^13", "adx_plus_higher_minus^21", 
    "tsi_higher_signal^13^6^6", "tsi_higher_signal^21^10^10", "tsi_higher_signal^34^17^17", 
    "rsi_fast_higher_low^8^13", "rsi_fast_higher_low^13^21", "rsi_fast_higher_low^21^34", 
    "rsi_fast_higher_low^8^21", "rsi_fast_higher_low^13^34", "rsi_fast_higher_low^21^55", 
    "supertrend_long_period^13^2.5", "supertrend_long_period^21^3.0", "supertrend_long_period^34^3.5", 
    "ma_atr_long_period^13^6^1.3", "ma_atr_long_period^21^10^1.3", "ma_atr_long_period^34^17^1.3", 
    "ma_atr_long_period^13^6^1.7", "ma_atr_long_period^21^10^1.7", "ma_atr_long_period^34^17^1.7", 
    "ma_atr_long_period^13^6^2.1", "ma_atr_long_period^21^10^2.1", "ma_atr_long_period^34^17^2.1", 
]
entry_filter_long_fast = ["_",  # _ 表示不使用任何过滤条件，满足入场条件即可入场
    "sma_decrease^13", "sma_decrease^21", "sma_decrease^34", 
    "sma_decrease_2^13", "sma_decrease_2^21", "sma_decrease_2^34", 
    "sma_fast_lower_slow^13^26", "sma_fast_lower_slow^21^42", "sma_fast_lower_slow^34^68", 
    "sma_fast_lower_slow_and_decrease^13^26", "sma_fast_lower_slow_and_decrease^21^42", "sma_fast_lower_slow_and_decrease^34^68", 
    "sma_fast_lower_slow_or_decrease^13^26", "sma_fast_lower_slow_or_decrease^21^42", "sma_fast_lower_slow_or_decrease^34^68", 
    "sma_first_lower_second^13^13", "sma_first_lower_second^21^21", "sma_first_lower_second^34^34", 
    "sma_first_lower_second_and_decrease^13^13", "sma_first_lower_second_and_decrease^21^21", "sma_first_lower_second_and_decrease^34^34", 
    "sma_first_lower_second_or_decrease^13^13", "sma_first_lower_second_or_decrease^21^21",  "sma_first_lower_second_or_decrease^34^34", 
    "ema_decrease^13", "ema_decrease^21", "ema_decrease^34", 
    "ema_fast_lower_slow^13^26", "ema_fast_lower_slow^21^42", "ema_fast_lower_slow^34^68", 
    "ema_first_lower_second^13^13", "ema_first_lower_second^21^21", "ema_first_lower_second^34^34", 
    "smacd_signal_lower0^13^26^13", "smacd_signal_lower0^21^42^21", "smacd_signal_lower0^34^68^34", 
    "smacd_lower_signal^13^26^13", "smacd_lower_signal^21^42^21", "smacd_lower_signal^34^68^34", 
    "smacd_lower_signal_and_decrease^13^26^13", "smacd_lower_signal_and_decrease^21^42^21", "smacd_lower_signal_and_decrease^34^68^34", 
    "smacd_lower_signal_or_decrease^13^26^13", "smacd_lower_signal_or_decrease^21^42^21", "smacd_lower_signal_or_decrease^34^68^34", 
    "smacd2_signal_lower0^13^13^13", "smacd2_signal_lower0^21^21^21", "smacd2_signal_lower0^34^34^34", 
    "smacd2_lower_signal^13^13^13", "smacd2_lower_signal^21^21^21", "smacd2_lower_signal^34^34^34", 
    "smacd2_lower_signal_and_decrease^13^13^13", "smacd2_lower_signal_and_decrease^21^21^21", "smacd2_lower_signal_and_decrease^34^34^34", 
    "smacd2_lower_signal_or_decrease^13^13^13", "smacd2_lower_signal_or_decrease^21^21^21", "smacd2_lower_signal_or_decrease^34^34^34", 
    "emacd_signal_lower0^13^26^13", "emacd_signal_lower0^21^42^21", "emacd_signal_lower0^34^68^34", 
    "emacd_lower_signal^13^26^13", "emacd_lower_signal^21^42^21", "emacd_lower_signal^34^68^34", 
    "emacd_lower_signal_and_decrease^13^26^13", "emacd_lower_signal_and_decrease^21^42^21", "emacd_lower_signal_and_decrease^34^68^34", 
    "emacd_lower_signal_or_decrease^13^26^13", "emacd_lower_signal_or_decrease^21^42^21", "emacd_lower_signal_or_decrease^34^68^34", 
    "emacd2_signal_lower0^13^13^13", "emacd2_signal_lower0^21^21^21", "emacd2_signal_lower0^34^34^34", 
    "emacd2_lower_signal^13^13^13", "emacd2_lower_signal^21^21^21", "emacd2_lower_signal^34^34^34", 
    "emacd2_lower_signal_and_decrease^13^13^13", "emacd2_lower_signal_and_decrease^21^21^21", "emacd2_lower_signal_and_decrease^34^34^34", 
    "emacd2_lower_signal_or_decrease^13^13^13", "emacd2_lower_signal_or_decrease^21^21^21", "emacd2_lower_signal_or_decrease^34^34^34", 
    "adx_plus_lower_minus^8", "adx_plus_lower_minus^13", "adx_plus_lower_minus^21", 
    "tsi_lower_signal^13^6^6", "tsi_lower_signal^21^10^10", "tsi_lower_signal^34^17^17", 
    "rsi_fast_lower_low^8^13", "rsi_fast_lower_low^13^21", "rsi_fast_lower_low^21^34", 
    "rsi_fast_lower_low^8^21", "rsi_fast_lower_low^13^34", "rsi_fast_lower_low^21^55", 
    "supertrend_short_period^13^2.5", "supertrend_short_period^21^3.0", "supertrend_short_period^34^3.5", 
    "ma_atr_short_period^13^6^1.3", "ma_atr_short_period^21^10^1.3", "ma_atr_short_period^34^17^1.3", 
    "ma_atr_short_period^13^6^1.7", "ma_atr_short_period^21^10^1.7", "ma_atr_short_period^34^17^1.7", 
    "ma_atr_short_period^13^6^2.1", "ma_atr_short_period^21^10^2.1", "ma_atr_short_period^34^17^2.1", 
]


entry_signal_long = [
    "price_crossover_sma^13", "price_crossover_sma^21", "price_crossover_sma^34", 
    "price_crossover_sma_2^13", "price_crossover_sma_2^21", "price_crossover_sma_2^34", 
    # "sma_fast_crossover_slow^13^26", "sma_fast_crossover_slow^21^42", "sma_fast_crossover_slow^34^68", 
    # "sma_fast_crossover_slow_2^13^26", "sma_fast_crossover_slow_2^21^42", "sma_fast_crossover_slow_2^34^68", 
    # "sma_fast_crossover_slow_3^13^26", "sma_fast_crossover_slow_3^21^42", "sma_fast_crossover_slow_3^34^68", 
    # "sma_first_crossover_second^13^13", "sma_first_crossover_second^21^21", "sma_first_crossover_second^34^34", 
    # "sma_first_crossover_second_2^13^13", "sma_first_crossover_second_2^21^21", "sma_first_crossover_second_2^34^34", 
    # "sma_first_crossover_second_3^13^13", "sma_first_crossover_second_3^21^21", "sma_first_crossover_second_3^34^34", 
    # "price_crossover_ema^13", "price_crossover_ema^21", "price_crossover_ema^34", 
    # "ema_fast_crossover_slow^13^26", "ema_fast_crossover_slow^21^42", "ema_fast_crossover_slow^34^68", 
    "ema_first_crossover_second^13^13", "ema_first_crossover_second^21^21", "ema_first_crossover_second^34^34", 
]
entry_signal_long = [
    # "emacd2_signal_crossover0^13^13^13", "emacd2_signal_crossover0^21^21^21", "emacd2_signal_crossover0^34^34^34", 
    # "emacd2_signal_crossover0_2^13^13^13", "emacd2_signal_crossover0_2^21^21^21", "emacd2_signal_crossover0_2^34^34^34", 
    # "emacd2_crossover_signal^13^13^13", "emacd2_crossover_signal^21^21^21", "emacd2_crossover_signal^34^34^34", 
    "emacd2_crossover_signal_2^13^13^13", "emacd2_crossover_signal_2^21^21^21", "emacd2_crossover_signal_2^34^34^34", 
    # "emacd2_crossover_signal_3^13^13^13", "emacd2_crossover_signal_3^21^21^21", "emacd2_crossover_signal_3^34^34^34", 
    "emacd2_crossover_signal_4^13^13^13", "emacd2_crossover_signal_4^21^21^21", "emacd2_crossover_signal_4^34^34^34", 
    # "emacd2_crossover_signal_5^13^13^13", "emacd2_crossover_signal_5^21^21^21", "emacd2_crossover_signal_5^34^34^34", 
    # "emacd2_crossover_signal_6^13^13^13", "emacd2_crossover_signal_6^21^21^21", "emacd2_crossover_signal_6^34^34^34", 
]
entry_signal_long = [
    # "smacd_signal_crossover0^13^26^13", "smacd_signal_crossover0^21^42^21", "smacd_signal_crossover0^34^68^34", 
    # "smacd_crossover_signal^13^26^13", "smacd_crossover_signal^21^42^21", "smacd_crossover_signal^34^68^34", 
    # "smacd_crossover_signal_2^13^26^13", "smacd_crossover_signal_2^21^42^21", "smacd_crossover_signal_2^34^68^34", 
    # "smacd_crossover_signal_3^13^26^13", "smacd_crossover_signal_3^21^42^21", "smacd_crossover_signal_3^34^68^34", 
    # "smacd_crossover_signal_4^13^26^13", "smacd_crossover_signal_4^21^42^21", "smacd_crossover_signal_4^34^68^34", 
    # "smacd2_signal_crossover0^13^13^13", "smacd2_signal_crossover0^21^21^21", "smacd2_signal_crossover0^34^34^34", 
    # "smacd2_crossover_signal^13^13^13", "smacd2_crossover_signal^21^21^21", "smacd2_crossover_signal^34^34^34", 
    # "smacd2_crossover_signal_2^13^13^13", "smacd2_crossover_signal_2^21^21^21", "smacd2_crossover_signal_2^34^34^34", 
    # "smacd2_crossover_signal_3^13^13^13", "smacd2_crossover_signal_3^21^21^21", "smacd2_crossover_signal_3^34^34^34", 
    # "smacd2_crossover_signal_4^13^13^13", "smacd2_crossover_signal_4^21^21^21", "smacd2_crossover_signal_4^34^34^34", 
    # "emacd_signal_crossover0^13^26^13", "emacd_signal_crossover0^21^42^21", "emacd_signal_crossover0^34^68^34", 
    # "emacd_crossover_signal^13^26^13", "emacd_crossover_signal^21^42^21", "emacd_crossover_signal^34^68^34", 
    # "emacd_crossover_signal_2^13^26^13", "emacd_crossover_signal_2^21^42^21", "emacd_crossover_signal_2^34^68^34", 
    # "emacd_crossover_signal_3^13^26^13", "emacd_crossover_signal_3^21^42^21", "emacd_crossover_signal_3^34^68^34", 
    # "emacd_crossover_signal_4^13^26^13", "emacd_crossover_signal_4^21^42^21", "emacd_crossover_signal_4^34^68^34", 
    # "emacd2_signal_crossover0^13^13^13", "emacd2_signal_crossover0^21^21^21", "emacd2_signal_crossover0^34^34^34", 
    # "emacd2_crossover_signal^13^13^13", "emacd2_crossover_signal^21^21^21", "emacd2_crossover_signal^34^34^34", 
    "emacd2_crossover_signal_2^13^13^13", "emacd2_crossover_signal_2^21^21^21", "emacd2_crossover_signal_2^34^34^34", 
    # "emacd2_crossover_signal_3^13^13^13", "emacd2_crossover_signal_3^21^21^21", "emacd2_crossover_signal_3^34^34^34", 
    "emacd2_crossover_signal_4^13^13^13", "emacd2_crossover_signal_4^21^21^21", "emacd2_crossover_signal_4^34^34^34", 
]
entry_signal_long = [
    # "bb_price_crossover_low^13^1.5", "bb_price_crossover_low^21^2.0", "bb_price_crossover_low^34^2.5", 
    # "bb_price_crossover_low_2^13^1.5", "bb_price_crossover_low_2^21^2.0", "bb_price_crossover_low_2^34^2.5", 
    "bb_price_crossover_high^13^1.5", "bb_price_crossover_high^21^2.0", "bb_price_crossover_high^34^2.5", 
    # "bb_price_crossover_high_2^13^1.5", "bb_price_crossover_high_2^21^2.0", "bb_price_crossover_high_2^34^2.5", 
    # "kc_price_crossover_low^13^6^1.5", "kc_price_crossover_low^21^10^2.0", "kc_price_crossover_low^34^17^2.5", 
    # "kc_price_crossover_low_2^13^6^1.5", "kc_price_crossover_low_2^21^10^2.0", "kc_price_crossover_low_2^34^17^2.5", 
    "kc_price_crossover_high^13^6^1.5", "kc_price_crossover_high^21^10^2.0", "kc_price_crossover_high^34^17^2.5", 
    # "kc_price_crossover_high_2^13^6^1.5", "kc_price_crossover_high_2^21^10^2.0", "kc_price_crossover_high_2^34^17^2.5", 
]
entry_signal_long = [
    # "mass_crossover1^13^6", "mass_crossover1^21^10", "mass_crossover1^34^17", 
    # "mass_crossunder1^13^6", "mass_crossunder1^21^10", "mass_crossunder1^34^17", 
    # "stoch_k_crossover_d^13^3^3", "stoch_k_crossover_d^21^5^5", "stoch_k_crossover_d^34^9^9", 
    # "kdj_k_crossover_d^13^3^3", "kdj_k_crossover_d^21^5^5", "kdj_k_crossover_d^34^9^9", 
    "smi_k_crossover_d^13^3^3", "smi_k_crossover_d^21^5^5", "smi_k_crossover_d^34^9^9", 
    # "rvi_crossover_signal^13^3", "rvi_crossover_signal^21^5", "rvi_crossover_signal^34^9", 
    "adx_plus_crossover_minus^8", "adx_plus_crossover_minus^13", "adx_plus_crossover_minus^21", 
    "tsi_crossover_signal^13^6^6", "tsi_crossover_signal^21^10^10", "tsi_crossover_signal^34^17^17", 
    "rsi_fast_crossover_low^8^16", "rsi_fast_crossover_low^13^26", "rsi_fast_crossover_low^21^42", 
    # "supertrend_long_signal^13^3.0", "supertrend_long_signal^21^3.5", "supertrend_long_signal^34^4.0", 
    # "second_wave_trend_1^13", "second_wave_trend_1^21", "second_wave_trend_1^34", 
    # "second_wave_trend_2^13", "second_wave_trend_2^21", "second_wave_trend_2^34", 
]
entry_signal_long = [  # 组合信号
    "adx_plus_crossover_minus^8", "adx_plus_crossover_minus^13", "adx_plus_crossover_minus^21", 
    # "adx_plus_crossover_minus_and_ema_decrease^8^1.0", "adx_plus_crossover_minus_and_ema_decrease^13^1.0", "adx_plus_crossover_minus_and_ema_decrease^21^1.0", 
    # "adx_plus_crossover_minus_and_ema_decrease^8^4.236", "adx_plus_crossover_minus_and_ema_decrease^13^4.236", "adx_plus_crossover_minus_and_ema_decrease^21^4.236", 
    # "emacd2_crossover_signal_2^13^13^13", "emacd2_crossover_signal_2^21^21^21", "emacd2_crossover_signal_2^34^34^34", 
    # "emacd2_crossover_signal_4^13^13^13", "emacd2_crossover_signal_4^21^21^21", "emacd2_crossover_signal_4^34^34^34", 
    # "emacd2_crossover_signal_2_and_emacd2_signal_higher0^13^13^13^1.0", "emacd2_crossover_signal_2_and_emacd2_signal_higher0^21^21^21^1.0", "emacd2_crossover_signal_2_and_emacd2_signal_higher0^34^34^34^1.0", 
    # "emacd2_crossover_signal_4_and_emacd2_signal_higher0^13^13^13^1.0", "emacd2_crossover_signal_4_and_emacd2_signal_higher0^21^21^21^1.0", "emacd2_crossover_signal_4_and_emacd2_signal_higher0^34^34^34^1.0", 
    # "emacd2_crossover_signal_4_and_emacd2_higher_signal_and_increase^13^13^13^1.0", "emacd2_crossover_signal_4_and_emacd2_higher_signal_and_increase^21^21^21^1.0", "emacd2_crossover_signal_4_and_emacd2_higher_signal_and_increase^34^34^34^1.0", 
    # "emacd2_crossover_signal_4_and_sma_fast_lower_slow_or_decrease^13^13^13^1.0", "emacd2_crossover_signal_4_and_sma_fast_lower_slow_or_decrease^21^21^21^1.0", "emacd2_crossover_signal_4_and_sma_fast_lower_slow_or_decrease^34^34^34^1.0", 
    "emacd2_crossover_signal_2_and_emacd2_signal_higher0^13^13^13^4.236", "emacd2_crossover_signal_2_and_emacd2_signal_higher0^21^21^21^4.236", "emacd2_crossover_signal_2_and_emacd2_signal_higher0^34^34^34^4.236", 
    "emacd2_crossover_signal_4_and_emacd2_signal_higher0^13^13^13^4.236", "emacd2_crossover_signal_4_and_emacd2_signal_higher0^21^21^21^4.236", "emacd2_crossover_signal_4_and_emacd2_signal_higher0^34^34^34^4.236", 
    # "emacd2_crossover_signal_4_and_emacd2_higher_signal_and_increase^13^13^13^4.236", "emacd2_crossover_signal_4_and_emacd2_higher_signal_and_increase^21^21^21^4.236", "emacd2_crossover_signal_4_and_emacd2_higher_signal_and_increase^34^34^34^4.236", 
    # "emacd2_crossover_signal_4_and_sma_fast_lower_slow_or_decrease^13^13^13^4.236", "emacd2_crossover_signal_4_and_sma_fast_lower_slow_or_decrease^21^21^21^4.236", "emacd2_crossover_signal_4_and_sma_fast_lower_slow_or_decrease^34^34^34^4.236", 
    "emacd2_crossover_signal_2_and_emacd2_signal_higher0_and_sma_fast_higher_slow_and_increase^13^13^13^4.236", "emacd2_crossover_signal_2_and_emacd2_signal_higher0_and_sma_fast_higher_slow_and_increase^21^21^21^4.236", "emacd2_crossover_signal_2_and_emacd2_signal_higher0_and_sma_fast_higher_slow_and_increase^34^34^34^4.236", 
    "emacd2_crossover_signal_2_and_emacd2_signal_higher0_and_atr_fast_higher_slow^13^13^13^4.236", "emacd2_crossover_signal_2_and_emacd2_signal_higher0_and_atr_fast_higher_slow^21^21^21^4.236", "emacd2_crossover_signal_2_and_emacd2_signal_higher0_and_atr_fast_higher_slow^34^34^34^4.236", 
]
entry_signal_long = [
    "price_crossover_sma^13", "price_crossover_sma^21", "price_crossover_sma^34", 
    "price_crossover_sma_2^13", "price_crossover_sma_2^21", "price_crossover_sma_2^34", 
    "ema_first_crossover_second^13^13", "ema_first_crossover_second^21^21", "ema_first_crossover_second^34^34", 
    "emacd2_crossover_signal_2^13^13^13", "emacd2_crossover_signal_2^21^21^21", "emacd2_crossover_signal_2^34^34^34", 
    "emacd2_crossover_signal_4^13^13^13", "emacd2_crossover_signal_4^21^21^21", "emacd2_crossover_signal_4^34^34^34", 
    # "bb_price_crossover_high^13^1.5", "bb_price_crossover_high^21^2.0", "bb_price_crossover_high^34^2.5", 
    # "kc_price_crossover_high^13^6^1.5", "kc_price_crossover_high^21^10^2.0", "kc_price_crossover_high^34^17^2.5", 
    "smi_k_crossover_d^13^3^3", "smi_k_crossover_d^21^5^5", "smi_k_crossover_d^34^9^9", 
    "adx_plus_crossover_minus^8", "adx_plus_crossover_minus^13", "adx_plus_crossover_minus^21", 
    "tsi_crossover_signal^13^6^6", "tsi_crossover_signal^21^10^10", "tsi_crossover_signal^34^17^17", 
    "rsi_fast_crossover_low^8^16", "rsi_fast_crossover_low^13^26", "rsi_fast_crossover_low^21^42", 
    "emacd2_crossover_signal_2_and_emacd2_signal_higher0^13^13^13^4.236", "emacd2_crossover_signal_2_and_emacd2_signal_higher0^21^21^21^4.236", "emacd2_crossover_signal_2_and_emacd2_signal_higher0^34^34^34^4.236", 
    "emacd2_crossover_signal_4_and_emacd2_signal_higher0^13^13^13^4.236", "emacd2_crossover_signal_4_and_emacd2_signal_higher0^21^21^21^4.236", "emacd2_crossover_signal_4_and_emacd2_signal_higher0^34^34^34^4.236", 
    "emacd2_crossover_signal_2_and_emacd2_signal_higher0_and_sma_fast_higher_slow_and_increase^13^13^13^4.236", "emacd2_crossover_signal_2_and_emacd2_signal_higher0_and_sma_fast_higher_slow_and_increase^21^21^21^4.236", "emacd2_crossover_signal_2_and_emacd2_signal_higher0_and_sma_fast_higher_slow_and_increase^34^34^34^4.236", 
    "emacd2_crossover_signal_2_and_emacd2_signal_higher0_and_atr_fast_higher_slow^13^13^13^4.236", "emacd2_crossover_signal_2_and_emacd2_signal_higher0_and_atr_fast_higher_slow^21^21^21^4.236", "emacd2_crossover_signal_2_and_emacd2_signal_higher0_and_atr_fast_higher_slow^34^34^34^4.236", 
]
entry_signal_long = [
    "emacd2_crossover_signal_2_and_emacd2_signal_higher0_and_atr_fast_higher_slow^21^21^21^4.236", "emacd2_crossover_signal_2_and_emacd2_signal_higher0_and_atr_fast_higher_slow^34^34^34^4.236", 
    "emacd2_crossover_signal_2_and_emacd2_signal_higher0_and_sma_fast_higher_slow_and_increase^21^21^21^4.236", "emacd2_crossover_signal_2_and_emacd2_signal_higher0_and_sma_fast_higher_slow_and_increase^34^34^34^4.236", 
    "emacd2_crossover_signal_4_and_emacd2_signal_higher0^21^21^21^4.236", "emacd2_crossover_signal_4_and_emacd2_signal_higher0^34^34^34^4.236", 
    "emacd2_crossover_signal_4^21^21^21", 
    "adx_plus_crossover_minus^8", "adx_plus_crossover_minus^13", "adx_plus_crossover_minus^21", 
    "price_crossover_sma_2^21", "price_crossover_sma_2^34", 
    "smi_k_crossover_d^13^3^3", 
    "emacd2_crossover_signal_2^13^13^13", 
    "price_crossover_sma^34", 
    "tsi_crossover_signal^13^6^6", 
]


exit_signal_general = [
    # "trailing_stop^8^2.0", "trailing_stop^13^2.0", "trailing_stop^89^3.5", "trailing_stop^144^4.0", 
    "trailing_stop^21^2.5", "trailing_stop^34^3.0", "trailing_stop^55^3.0", 
]


exit_signal_long_slow = ["_",  # _ 表示不使用任何出场条件
    "price_crossunder_sma^55", "price_crossunder_sma^89", "price_crossunder_sma^144", 
    # "price_crossunder_sma_2^55", "price_crossunder_sma_2^89", "price_crossunder_sma_2^144", 
    # "sma_fast_crossunder_slow^55^110", "sma_fast_crossunder_slow^89^178", "sma_fast_crossunder_slow^144^288", 
    # "sma_fast_crossunder_slow_2^55^110", "sma_fast_crossunder_slow_2^89^178", "sma_fast_crossunder_slow_2^144^288", 
    # "sma_fast_crossunder_slow_3^55^110", "sma_fast_crossunder_slow_3^89^178", "sma_fast_crossunder_slow_3^144^288", 
    "sma_first_crossunder_second^55^55", "sma_first_crossunder_second^89^89", "sma_first_crossunder_second^144^144", 
    # "sma_first_crossunder_second_2^55^55", "sma_first_crossunder_second_2^89^89", "sma_first_crossunder_second_2^144^144", 
    # "sma_first_crossunder_second_3^55^55", "sma_first_crossunder_second_3^89^89", "sma_first_crossunder_second_3^144^144", 
    # "price_crossunder_ema^55", "price_crossunder_ema^89", "price_crossunder_ema^144", 
    # "ema_fast_crossunder_slow^55^110", "ema_fast_crossunder_slow^89^178", "ema_fast_crossunder_slow^144^288", 
    # "ema_first_crossunder_second^55^55", "ema_first_crossunder_second^89^89", "ema_first_crossunder_second^144^144", 
]
exit_signal_long_slow = ["_",  # _ 表示不使用任何出场条件
    "emacd2_signal_crossunder0^55^55^55", "emacd2_signal_crossunder0^89^89^89", "emacd2_signal_crossunder0^144^144^144", 
    # "emacd2_signal_crossunder0_2^55^55^55", "emacd2_signal_crossunder0_2^89^89^89", "emacd2_signal_crossunder0_2^144^144^144", 
    "emacd2_crossunder_signal^55^55^55", "emacd2_crossunder_signal^89^89^89", "emacd2_crossunder_signal^144^144^144", 
    # "emacd2_crossunder_signal_2^55^55^55", "emacd2_crossunder_signal_2^89^89^89", "emacd2_crossunder_signal_2^144^144^144", 
    # "emacd2_crossunder_signal_3^55^55^55", "emacd2_crossunder_signal_3^89^89^89", "emacd2_crossunder_signal_3^144^144^144", 
    # "emacd2_crossunder_signal_4^55^55^55", "emacd2_crossunder_signal_4^89^89^89", "emacd2_crossunder_signal_4^144^144^144", 
    # "emacd2_crossunder_signal_5^55^55^55", "emacd2_crossunder_signal_5^89^89^89", "emacd2_crossunder_signal_5^144^144^144", 
    # "emacd2_crossunder_signal_6^55^55^55", "emacd2_crossunder_signal_6^89^89^89", "emacd2_crossunder_signal_6^144^144^144", 
]
exit_signal_long_slow = ["_",  # _ 表示不使用任何出场条件
    # "smacd_signal_crossunder0^55^110^55", "smacd_signal_crossunder0^89^178^89", "smacd_signal_crossunder0^144^288^144", 
    # "smacd_crossunder_signal^55^110^55", "smacd_crossunder_signal^89^178^89", "smacd_crossunder_signal^144^288^144", 
    "smacd2_signal_crossunder0^55^55^55", "smacd2_signal_crossunder0^89^89^89", "smacd2_signal_crossunder0^144^144^144", 
    "smacd2_crossunder_signal^55^55^55", "smacd2_crossunder_signal^89^89^89", "smacd2_crossunder_signal^144^144^144", 
    # "emacd_signal_crossunder0^55^110^55", "emacd_signal_crossunder0^89^178^89", "emacd_signal_crossunder0^144^288^144", 
    # "emacd_crossunder_signal^55^110^55", "emacd_crossunder_signal^89^178^89", "emacd_crossunder_signal^144^288^144", 
    # "emacd2_signal_crossunder0^55^55^55", "emacd2_signal_crossunder0^89^89^89", "emacd2_signal_crossunder0^144^144^144", 
    # "emacd2_crossunder_signal^55^55^55", "emacd2_crossunder_signal^89^89^89", "emacd2_crossunder_signal^144^144^144", 
]
exit_signal_long_slow = ["_",  # _ 表示不使用任何出场条件
    "price_crossunder_sma^55", "price_crossunder_sma^89", "price_crossunder_sma^144", 
    # "sma_first_crossunder_second^55^55", "sma_first_crossunder_second^89^89", "sma_first_crossunder_second^144^144", 
    "smacd2_signal_crossunder0^55^55^55", "smacd2_signal_crossunder0^89^89^89", "smacd2_signal_crossunder0^144^144^144", 
    "smacd2_crossunder_signal^55^55^55", "smacd2_crossunder_signal^89^89^89", "smacd2_crossunder_signal^144^144^144", 
    # "adx_plus_crossunder_minus^34", "adx_plus_crossunder_minus^55", "adx_plus_crossunder_minus^89", 
    "tsi_crossunder_signal^55^27^27", "tsi_crossunder_signal^89^44^44", "tsi_crossunder_signal^144^72^72", 
    "rsi_fast_crossunder_low^34^89", "rsi_fast_crossunder_low^55^144", "rsi_fast_crossunder_low^89^233", 
    # "ma_atr_short_signal^55^27^1.3", "ma_atr_short_signal^89^44^1.3", "ma_atr_short_signal^144^72^1.3", 
]
exit_signal_long_slow = [
    "tsi_crossunder_signal^55^27^27", 
    "rsi_fast_crossunder_low^34^89", "rsi_fast_crossunder_low^55^144", 
    "price_crossunder_sma^55", 
    "smacd2_crossunder_signal^55^55^55", "smacd2_crossunder_signal^89^89^89", 
    "smacd2_signal_crossunder0^89^89^89", "smacd2_signal_crossunder0^144^144^144", 
]


