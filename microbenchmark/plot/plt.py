import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

interval = 20

# 读取日志文件
def read_log_file(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()

log_file = read_log_file('./post_result.log')

time = []
data = []
data1, data2 = [], []

i = 0
value1, value2 = 0, 0
now = 0
for line in log_file:
    
    i = i % 2
    if i == 0:
        sub_str = line[len('[2025-03-16 02:40:59.624] Interval: '): len('[2025-03-16 02:40:59.594] Interval: 616')]
        if sub_str[-1] == '(':
            sub_str = sub_str[:-1]
        value1 = 0
        value1 += int(sub_str)
    else:
        sub_str = line[len('[2025-03-16 02:40:59.624] Interval: '): len('[2025-03-16 02:40:59.594] Interval: 616')]
        if sub_str[-1] == '(':
            sub_str = sub_str[:-1]
        value2 += int(sub_str)
        time_str = line[len('[2025-03-16 '):len('[2025-03-16 02:40:59.586')]
        h = int(time_str[:2])
        m = int(time_str[3:5])
        s = int(time_str[6:8])
        ms = int(time_str[9:12])
        now = h * 60 * 60 * 1000 + m * 60 * 1000 + s * 1000 + ms;
        if len(time) == 0 or now - time[len(time) - 1] < interval * 2:
            time.append(now)
            data.append((value1 + value2) / 2)
            data1.append(value1)
            data2.append(value2)
        else:
            for i in range(int((now - time[len(time) - 1]) / interval)):
                time.append(time[len(time) - 1] + interval )
                data.append(0)
                data1.append(0)
                data2.append(0)
        value1, value2 = 0, 0
    i += 1

time_100 = []
data_100 = []

for i in range(int(len(time) / 100) + 1):
    time_100.append(time[i * 100])
    data_100.append(np.array(data[i * 100 : min(len(data), (i + 1) * 100)]).mean())

# time = time_100
# data = data_100

plt.figure(figsize=(16, 5))
time = np.array(time)
time = time/1000 - time[0] / 1000
plt.plot(time, data, color='black')
# plt.plot(time, data1)
# plt.plot(time, data2)
plt.xticks(range(18,25))
plt.xlim([18, 24])
plt.ylabel("Memory access (times)", fontsize=15)
plt.xlabel("Time (seconds)", fontsize=15)
# plt.xticks(time, time/1000 - time[0])
plt.savefig("result.png")
plt.show()