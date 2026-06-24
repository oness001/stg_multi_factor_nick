import os

import redis

class RdsQueue:
    def __init__(self, name, max_length, redis):
        self.redis = redis
        self.queue_key = f"{name}"
        self.max_length = max_length

    def push(self, item):
        """尾部插入并动态修剪长度"""
        current_len = self.redis.rpush(self.queue_key, item)
        if current_len > self.max_length:
            self.redis.ltrim(self.queue_key, current_len - self.max_length, -1)

    def batch_push(self, items):
        """批量插入（Pipeline优化）"""
        with self.redis.pipeline() as pipe:
            for item in items:
                pipe.rpush(self.queue_key, item)
            pipe.ltrim(self.queue_key, -self.max_length, -1)
            pipe.execute()

    def update_tail(self, new_value):
        """安全更新末尾元素"""
        self.redis.lset(self.queue_key, -1, new_value)

    def safe_update_tail(self, new_value):
        """乐观锁保护的高频更新"""
        with self.redis.pipeline() as pipe:
            while True:
                try:
                    pipe.watch(self.queue_key)
                    if pipe.llen(self.queue_key) == 0:
                        break
                    pipe.multi()
                    pipe.lset(self.queue_key, -1, new_value)
                    pipe.execute()
                    break
                except redis.WatchError:
                    continue

    def get_all(self):
        """获取全部元素"""
        return self.redis.lrange(self.queue_key, 0, -1)

    def get_last_element_via_range(self):
        """备选：使用 LRANGE 获取最新元素"""
        elements = self.redis.lrange(self.queue_key, -1, -1)
        return elements[0] if elements else None

    def get_len(self):
        """当前队列长度"""
        return self.redis.llen(self.queue_key)

    def blocking_pop(self, timeout=0):
        """阻塞式出队"""
        return self.redis.blpop(self.queue_key, timeout=timeout)

    def pop_from_end(self):
        """从队列末尾弹出一个元素"""
        return self.redis.rpop(self.queue_key)

    def batch_pop_from_end(self, count):
        """从队列末尾批量弹出count个元素，返回列表（按弹出顺序）"""
        result = []
        for _ in range(count):
            item = self.redis.rpop(self.queue_key)
            if item is None:
                break
            result.append(item)
        return result

    def resize(self, new_max_length):
        """动态调整队列长度"""
        self.max_length = new_max_length
        self.redis.ltrim(self.queue_key, -new_max_length, -1)

    def get_element_at(self, reverse_index):
        """
        获取倒数第i个元素（从1开始计数）

        参数:
            reverse_index: 倒数索引（1表示最后一个元素，2表示倒数第二个，以此类推）

        返回:
            指定位置的元素，如果索引超出范围返回None
        """

        # 计算正向索引：列表长度 - 倒数索引
        # 例如：获取倒数第2个元素，正向索引 = 长度 - 2
        elements = self.redis.lrange(self.queue_key, -reverse_index, -reverse_index)
        return elements[0] if elements else None

    def get_range(self, start_reverse_index, end_reverse_index):
        """
        获取从倒数第i个到倒数第j个的元素范围（i > j）

        参数:
            start_reverse_index: 起始倒数索引（较大的数，更靠近队列开头）
            end_reverse_index: 结束倒数索引（较小的数，更靠近队列末尾）

        返回:
            指定范围内的元素列表
        """

        start_index = start_reverse_index
        end_index = end_reverse_index

        return self.redis.lrange(self.queue_key, start_index, end_index)


if __name__ == '__main__':
    import pandas as pd
    import orjson
    import time

    pd.set_option('mode.chained_assignment', None)  # 直接屏蔽警告（安全、不影响运行）
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 9999)
    pd.set_option('mode.chained_assignment', None)  # 禁用链式赋值警告
    for symbol_id in [    "GCmain", "SImain", "CLmain", "HGmain","ZWmain", "ZLmain", "ZCmain", "ZSmain", "ZMmain"]:
        # symbol_id = 'CLmain'
        interval = '15min'
        redis_cli = redis.Redis(    host="47.83.140.255",
                                     port=6379,
                                     password="e7LpFUoMwBzjfPBvJW",
                                     decode_responses=True)
        st = time.time()
        list_data = redis_cli.lrange(f'tiger_his_kline_list:{interval}:{symbol_id}', start=0, end=-1)
        list_data = [orjson.loads(i) for i in list_data]
        print(time.time()-st)
        # print(list_data)
        print(len(list_data))
        df = pd.DataFrame(list_data)
        print(df.shape)
        print(df.head())
        print(df.tail())
        print(df.dtypes)
        duplicates = df[df['candle_begin_time'].duplicated(keep=False)]
        print(duplicates)
        df['candle_begin_time'] = pd.to_datetime(df['candle_begin_time'], utc=True)
        df = df.drop_duplicates(subset='candle_begin_time', keep='last')
        df.sort_values(by='candle_begin_time', inplace=True)
        df['ts'] = df['candle_begin_time'] + pd.Timedelta(hours=8)
        df['ts'] = df['ts'].dt.strftime('%Y-%m-%d %H:%M:%S')
        df.reset_index(drop=True, inplace=True)

        df['candle_begin_time'] = pd.to_datetime(df['candle_begin_time'], utc=True)
        df = df.drop_duplicates(subset='candle_begin_time', keep='last')
        df.sort_values(by='candle_begin_time', inplace=True)
        df['ts'] = df['candle_begin_time'] + pd.Timedelta(hours=8)
        df['ts'] = df['ts'].dt.strftime('%Y-%m-%d %H:%M:%S')
        df.reset_index(drop=True, inplace=True)
        os.makedirs(r'D:\贵金属_data\comex_15min', exist_ok=True)
        df.to_csv(fr'D:\贵金属_data\comex_15min\comex_{symbol_id}_{interval}.csv')
        # df.to_csv(f'comex_CLmain_15min.csv')
        print(df.shape)
        print(df.head())
        print(df.tail())
        print(df.dtypes)
        time.sleep(1)