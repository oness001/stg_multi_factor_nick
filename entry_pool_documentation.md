# Entry Pool 函数文档

## 概述

`entry_pool.py` 是一个量化交易策略的**入场信号函数库**，包含各类技术分析相关的入场点位检测函数。这些函数主要用于：
- 趋势反转信号检测（金叉/死叉）
- 突破信号检测（价格突破关键点）
- 动量信号检测（指标开始上升/下降）
- 超买超卖反转信号

---

## 目录

1. [基础工具函数](#1-基础工具函数)
2. [多头入场信号函数](#2-多头入场信号函数)
3. [空头入场信号函数](#3-空头入场信号函数)
4. [突破/转折信号函数](#4-突破转折信号函数)
5. [函数命名规范](#5-函数命名规范)
6. [使用示例](#6-使用示例)

---

## 1. 基础工具函数

### 1.1 `crossover(array1, array2)` ✅
**用途**: 检测上穿交叉信号

**原理**:
```
当前 array1 > array2 且 前一根 array1 ≤ array2
```

**返回**: 布尔数组，True 表示金叉（上穿）

**示例**: `crossover(fast_ma, slow_ma)` 检测快线上穿慢线

---

### 1.2 `crossunder(array1, array2)` ✅
**用途**: 检测下穿交叉信号

**原理**:
```
当前 array1 ≤ array2 且 前一根 array1 > array2
```

**返回**: 布尔数组，True 表示死叉（下穿）

---

### 1.3 `increase(array, timeperiod)` ✅
**用途**: 检测数组上升状态

**原理**:
- 当前值 > 前1天值
- 当前值 > 前 `timeperiod/20` 天值

**返回**: 布尔数组

---

### 1.4 `decrease(array, timeperiod)` ✅
**用途**: 检测数组下降状态

**原理**:
- 当前值 ≤ 前1天值
- 当前值 ≤ 前 `timeperiod/20` 天值

---

### 1.5 `start_increase(array, timeperiod)` ✅
**用途**: 检测开始上升的转折点

**原理**: 从非上升状态变为上升状态

---

### 1.6 `start_decrease(array, timeperiod)` ✅
**用途**: 检测开始下降的转折点

**原理**: 从非下降状态变为下降状态

---

## 2. 多头入场信号函数

### 2.1 分类概览

| 类别 | 函数前缀 | 说明 |
|------|---------|------|
| ROC 动量 | `roc_crossover0` | ROC 上穿 0 |
| AROON 趋势 | `aroon_diff_crossover0` | AROON 差值上穿 0 |
| 价格突破 | `price_crossover_*` | 价格上穿均线 |
| 均线金叉 | `sma_*_crossover_*`, `ema_*_crossover_*` | 双均线金叉 |
| MACD | `smacd_*`, `emacd_*` | MACD 相关信号 |
| TRIX | `trix_crossover0`, `trix_start_increase` | TRIX 信号 |
| 布林带 | `bb_price_crossover_*` | 价格突破布林带 |
| 肯特纳通道 | `kc_price_crossover_*` | 价格突破肯特纳通道 |
| 震荡指标 | `stoch_*`, `kdj_*`, `smi_*` | 金叉信号 |
| RVI | `rvi_crossover_signal` | RVI 交叉信号 |
| ADX | `adx_plus_crossover_minus` | +DI 上穿 -DI |
| RSI | `rsi_fast_crossover_low` | 快线上穿慢线 |
| 趋势跟踪 | `supertrend_long_signal` | SuperTrend 多头 |
| 自定义 | `second_wave_trend_*` | 第二波段趋势 |

---

### 2.2 ROC 动量类

#### `roc_crossover0(market_df, timeperiod)`
**条件**: ROC 从负值上穿 0
**用途**: 动量由负转正，可能开始上涨

---

### 2.3 均线交叉类

#### `price_crossover_sma(market_df, timeperiod)`
**条件**: 收盘价上穿 SMA
**用途**: 价格突破均线支撑

#### `sma_fast_crossover_slow(market_df, fastperiod, slowperiod)`
**条件**: 快 SMA 上穿 慢 SMA **且** 快 SMA 上升
**用途**: 金叉且趋势向上

#### `ema_fast_crossover_slow(market_df, fastperiod, slowperiod)`
**条件**: 快 EMA 上穿 慢 EMA
**用途**: EMA 金叉信号

---

### 2.4 MACD 类

#### `smacd_crossover_signal(market_df, fastperiod=12, slowperiod=26, signalperiod=9)`
**条件**: Histogram 上穿 0
**用途**: MACD 动量转正

#### `smacd_crossover_signal_2(market_df, ...)`
**条件**: Histogram 上穿 0 **且** 快 SMA 上升
**用途**: MACD 转正 + 趋势确认

#### `emacd_start_increase(market_df, ...)`
**条件**: MACD 线开始上升
**用途**: MACD 动量开始增强

---

### 2.5 Stochastic/KDJ/SMI 类

#### `stoch_k_crossover_d(market_df, fastk_period=5, slowk_period=3, slowd_period=3)`
**条件**: SlowK 上穿 SlowD
**用途**: 经典随机指标金叉

#### `stoch_k_crossover_d_2(market_df, ..., oversold_threshold=20.0)`
**条件**: 超卖区金叉（"上膛"机制）
**用途**: 在超卖区等待金叉，避免过早入场

**上膛机制说明**:
1. 当 SlowK ≤ 阈值时"上膛"
2. 金叉时触发信号并"清膛"
3. 避免在超卖区上方频繁金叉

#### `kdj_k_crossover_d(market_df, ...)`
**条件**: K 上穿 D（使用 EMA 平滑）
**用途**: KDJ 金叉信号

#### `smi_k_crossover_d(market_df, ...)`
**条件**: SMI 上穿信号线
**用途**: 随机动量指数金叉

---

### 2.6 布林带/肯特纳通道

#### `bb_price_crossover_low(market_df, timeperiod, nbdev)`
**条件**: 收盘价上穿布林下轨
**用途**: 价格从超卖区域反弹

#### `bb_price_crossover_high(market_df, timeperiod, nbdev)`
**条件**: 收盘价上穿布林上轨
**用途**: 价格突破压力位（追涨）

#### `kc_price_crossover_low(market_df, timeperiod, atr_timeperiod, multiplier)`
**条件**: 收盘价上穿肯特纳下轨
**用途**: 基于 ATR 的支撑突破

---

### 2.7 自定义指标

#### `second_wave_trend_1(market_df, timeperiod=8)`
**条件**: 第二波段入场（严格版）
**用途**: 在趋势回调后第二波上涨时入场

**入场条件**:
1. 慢 EMA 持续上涨
2. 慢 EMA 斜率变缓（回调）
3. 快 EMA 下跌
4. 快 EMA 斜率变缓
5. 价格上涨

#### `second_wave_trend_2(market_df, timeperiod=8)`
**条件**: 第二波段入场（宽松版）
**用途**: 交易次数约为版本1的2倍

---

## 3. 空头入场信号函数

### 3.1 与多头信号对称

空头函数是多头函数的**镜像版本**，只需将 `crossover` 改为 `crossunder`，`increase` 改为 `decrease`。

| 多头函数 | 空头函数 |
|---------|---------|
| `roc_crossover0` | `roc_crossunder0` |
| `price_crossover_sma` | `price_crossunder_sma` |
| `sma_fast_crossover_slow` | `sma_fast_crossunder_slow` |
| `emacd_start_increase` | `emacd_start_decrease` |
| `stoch_k_crossover_d` | `stoch_k_crossunder_d` |

---

### 3.2 空头特有函数

#### `stoch_k_crossunder_d_2(market_df, ..., overbought_threshold=80.0)`
**条件**: 超买区死叉（"上膛"机制）
**用途**: 在超买区等待死叉，避免过早做空

**上膛机制**:
1. 当 SlowK ≥ 阈值时"上膛"
2. 死叉时触发信号并"清膛"

---

## 4. 突破/转折信号函数

### 4.1 高点突破类

#### `tp_high_0(df, N1, N2=0)`
**条件**: 收盘价上穿 N1 周期最高价
**参数**:
- `N1`: 突破周期
- `N2`: 价格类型（0=close, 1=high）

**用途**: 创新高信号

---

#### `tp_high_1(df, N1, N2=0)`
**条件**: 收盘价上穿（N1周期最高价 + 影线修正）
**原理**: 考虑上影线，向上调整突破位

---

#### `tp_high_2(df, N1, N3=0)`
**条件**: 收盘价上穿平滑后的突破位
**原理**: 对突破位进行 SMA 平滑，减少假突破

---

#### `s_tp_high_1(df, N1, N2=0, N3=0)`
**条件**: 突破确认信号
**原理**: 
1. 检测突破信号
2. N1 周期内有突破信号后才触发
3. 结合 K 线形态确认

---

### 4.2 低点突破类

#### `tp_low_0(df, N1, N2=0)`
**条件**: 收盘价下穿 N1 周期最低价（或根据斜率选择）
**参数**:
- `N1`: 突破周期
- `N2`: 选项（0=close, 1=low）

**用途**: 创新低信号

---

#### `tp_low_1(df, N1, N2=0)`
**条件**: 收盘价下穿（N1周期最低价 + 影线修正）
**原理**: 考虑下影线，向下调整突破位

---

#### `s_tp_low_1(df, N1, N2=0, N3=0)`
**条件**: 低点突破确认信号
**原理**: 
1. 检测下破信号
2. N1 周期内有下破信号后才触发
3. 结合 K 线形态（阴线/大阴线）确认

---

## 5. 函数命名规范

### 5.1 交叉信号命名

```
[指标]_[交叉类型]_[目标]
```

**示例**:
- `roc_crossover0` - ROC 上穿 0
- `price_crossover_sma` - 价格上穿 SMA
- `sma_fast_crossover_slow` - 快 SMA 上穿 慢 SMA
- `stoch_k_crossover_d` - K 上穿 D

---

### 5.2 动量信号命名

```
[指标]_[动量类型]
```

**示例**:
- `smacd_start_increase` - SMACD 开始上升
- `trix_start_decrease` - TRIX 开始下降
- `emacd_histogram_start_increase` - EMACD 柱状图开始上升

---

### 5.3 组合信号命名

```
[基础信号]_[修饰]_[序号]
```

**示例**:
- `sma_fast_crossover_slow_2` - 版本2（慢均线也上升）
- `sma_fast_crossover_slow_3` - 版本3（或条件：开始上升且快线>慢线）

---

### 5.4 突破信号命名

```
tp_[方向]_[版本]  或  s_tp_[方向]_[版本]
```

**示例**:
- `tp_high_0` - 高点突破版本0
- `tp_high_1` - 高点突破版本1（影线修正）
- `s_tp_high_1` - 高点突破确认信号

---

## 6. 使用示例

### 6.1 基础用法

```python
import pandas as pd
from cal_func.new.entry_pool import *

# 准备数据
df = pd.DataFrame({
    'open': [100, 101, 102, 103, 104],
    'high': [102, 103, 104, 105, 106],
    'low': [99, 100, 101, 102, 103],
    'close': [101, 102, 103, 102, 105]
})

# 检测金叉信号
signal = sma_fast_crossover_slow(df, fastperiod=5, slowperiod=20)
print(signal)  # [False, False, True, False, False]
```

---

### 6.2 策略组合示例

```python
# 组合多个入场信号
def multi_signal_entry(df):
    signal1 = sma_fast_crossover_slow(df, 5, 20)
    signal2 = emacd_crossover_signal(df, 12, 26, 9)
    signal3 = rsi_not_overbought(df, 14, 70)
    
    # 所有条件满足才入场
    entry = signal1 & signal2 & signal3
    return entry
```

---

### 6.3 上膛机制示例

```python
# 超卖区金叉（更可靠的买入信号）
signal = stoch_k_crossover_d_2(df, fastk_period=5, slowk_period=3, slowd_period=3, oversold_threshold=20.0)

# 逻辑说明：
# 1. SlowK <= 20 时"上膛"
# 2. SlowK 上穿 SlowD 时"开枪"
# 3. 触发后"清膛"，等待下次上膛
```

---

## 7. 函数清单

### 7.1 工具函数 (6个)
- `crossover`
- `crossunder`
- `increase`
- `decrease`
- `start_increase`
- `start_decrease`

### 7.2 多头信号 (~60个)
- ROC 动量: `roc_crossover0`
- AROON: `aroon_diff_crossover0`
- 价格突破: `price_crossover_sma`, `price_crossover_sma_2`, `price_crossover_ema`
- 均线金叉: `sma_fast_crossover_slow`, `sma_fast_crossover_slow_2`, `ema_fast_crossover_slow`
- MACD: `smacd_start_increase`, `smacd_crossover_signal` 等 15+ 个
- TRIX: `trix_crossover0`, `trix_start_increase`
- 布林带: `bb_price_crossover_low`, `bb_price_crossover_low_2`
- 肯特纳: `kc_price_crossover_low`, `kc_price_crossover_low_2`
- Stochastic: `stoch_k_crossover_d`, `stoch_k_crossover_d_2` 等
- KDJ: `kdj_k_crossover_d`, `kdj_k_crossover_d_2` 等
- SMI: `smi_k_crossover_d`, `smi_k_crossover_d_2` 等
- RVI: `rvi_crossover_signal`
- ADX: `adx_plus_crossover_minus`
- TSI: `tsi_crossover_signal`
- RSI: `rsi_fast_crossover_low`
- 趋势: `supertrend_long_signal`
- 自定义: `second_wave_trend_1`, `second_wave_trend_2`

### 7.3 空头信号 (~60个)
- 与多头对称的下穿/死叉/下降信号

### 7.4 突破信号 (~8个)
- `tp_high_0`, `tp_high_1`, `tp_high_2`
- `s_tp_high_1`
- `tp_low_0`, `tp_low_1`, `tp_low_2`
- `s_tp_low_1`

---

## 8. 注意事项

### 8.1 无未来函数
所有信号函数均使用历史数据，适合实盘使用。

### 8.2 信号类型
- **点位信号**: 返回 True 的那天即为信号日
- **状态信号**: 返回 True 表示处于某种状态中

### 8.3 参数选择
- 建议使用非重叠的参数组合避免过拟合
- 周期参数：5, 10, 14, 20, 30, 50, 100, 200
- 阈值参数：超卖 20，超买 80（可调整）

### 8.4 上膛机制
适用于 `_2` 和 `_4` 版本的 Stochastic/KDJ/SMI 函数：
- 避免在非极值区域频繁金叉/死叉
- 提高信号质量，减少交易次数

---

**文档生成时间**: 2026-06-15
**适用版本**: entry_pool.py v1.0
