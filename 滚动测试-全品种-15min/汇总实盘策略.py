
import pandas as pd
import glob
import os
pd.set_option('display.max_rows', 10000)
pd.set_option('display.max_columns', 10000)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 1500)
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('expand_frame_repr', False)
pd.set_option('display.float_format', lambda x: '%.4f' % x)

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('tkAgg')
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

for Ns in [(3, 3, 2), (4, 2, 2), (2, 4, 2), (2, 2, 3), (3, 3, 3)]:
    n1, n2, n3 = Ns
    # output_dir_long = rf'D:\nick01\stg_multi_factor_nick\滚动测试-全品种-15min\滚动信号结果\roll-{n1}_s-{n2}_e-{n3}_jzmode-d-20260331_20260630-long\allresult'
    output_dir_long = rf'D:\nick01\stg_multi_factor_nick\滚动测试-全品种-15min\滚动信号结果\roll-{n1}_s-{n2}_e-{n3}_jzmode-d-20260331_20260630-short\allresult'

    if True == 1:
        # 查找所有实盘参数文件
        csv_files = glob.glob(os.path.join(output_dir_long, "*_实盘参数.csv"))
        # 读取并合并所有文件
        all_dfs = []
        for file in csv_files:
            df = pd.read_csv(file)
            all_dfs.append(df)
        # 合并所有 DataFrame
        result_df = pd.concat(all_dfs, ignore_index=True)
        result_df['cl_index'] = [rf"cl_{i + 1}" for i in result_df.index]
        # 保存结果
        output_file = rf"{output_dir_long}\one_stgcfg_choose_策略.csv"
        result_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n已保存到: {output_file}")
    if True == 1:
        csv_files = glob.glob(os.path.join(output_dir_long, "*_筛选策略metrics.csv"))
        all_dfs = []
        for file in csv_files:
            symbol_name = os.path.basename(file).strip('_筛选策略metrics.csv')
            print(os.path.basename(file).strip('_筛选策略metrics.csv'))
            df = pd.read_csv(file)
            df_res = df.describe().round(4)
            df_res['symbol'] = symbol_name
            res = df_res.loc['mean']
            res = {'symbol': symbol_name,'count':df_res.loc['count','total+总收益率%'],**res}

            all_dfs.append(res)
        else:
            resdf = pd.DataFrame(all_dfs)
            resdf.rename(columns={k:k.split("+")[-1] for k in resdf.columns}, inplace=True)
            output_file = rf"{output_dir_long}\策略_均值.csv"
            resdf.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(resdf)
    if True == 1:
        # 读取并合并所有文件
        csv_files = glob.glob(os.path.join(output_dir_long, "*_all_equity_curve.csv"))
        all_dfs = pd.DataFrame()
        symbol_list = []
        for file in csv_files:

            symbol_name = os.path.basename(file).strip('_all_equity_curve.csv')
            symbol_list.append(symbol_name)
            print(os.path.basename(file).strip('_all_equity_curve.csv'))
            df = pd.read_csv(file)
            df_col = [i for i in df.columns if "&" in i ]

            df[symbol_name] = df[df_col].mean(axis=1)
            if all_dfs.empty:
                all_dfs = df[['datetime',symbol_name]]
            else:
                all_dfs = pd.merge(all_dfs, df[['datetime',symbol_name]],on='datetime',how = 'outer')

        else:
            all_dfs = all_dfs.ffill()
            all_dfs =all_dfs.reset_index(drop=True)
            all_dfs['datetime'] = all_dfs['datetime'].str[:10]

            fig,axs = plt.subplots(nrows=2, ncols=1, figsize=(18,14),height_ratios=[2,1])
            axs[0].plot(all_dfs[symbol_list], label=symbol_list)
            # plt.xlabel()
            axs[0].set_xticks(all_dfs.index[::300],all_dfs['datetime'].iloc[::300],rotation=90)
            axs[0].set_title(f"{Ns}")
            axs[0].legend()
            axs[0].grid()
            axs[1].text(0.01,0.1,resdf.to_string(),fontsize=11)

            plt.show()


