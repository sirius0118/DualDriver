import matplotlib.pyplot as plt

# 打开文件并读取数据
f = open('./keylog/addr_record.txt', 'r')
addr = {}
data = f.readlines()

num = 0
# 读取每一行数据并统计每个地址出现的次数
for line in data:
    num += 1
    if len(line) == 0:  # 跳过以 '0' 开头的行
        continue
    addr[line] = addr.get(line, 0) + 1

# 对字典按照值进行排序
sorted_dict = dict(sorted(addr.items(), key=lambda item: item[1]))
# print(sorted_dict)

plt.plot(range(len(sorted_dict), 0, -1), list(sorted_dict.values()))
plt.ylim([0, 50])
# 绘制条形图
# plt.bar(range(len(sorted_dict)), list(sorted_dict.values()), align='center')
# plt.xticks(range(len(sorted_dict)), list(sorted_dict.keys()), rotation=90)
plt.savefig('addr_record.png')  # 保存图像
plt.show()  # 显示图像


rdata = data[0:1000]
hot, cold = 0, 0
hotset, coldset = [], []
key = list(sorted_dict.keys())
for i in range(len(rdata)):
    if key.index(rdata[i]) < len(key) * 0.97:
        cold+=1
        if rdata[i] not in coldset:
            coldset.append(rdata[i])
    else:
        hot+=1
        if rdata[i] not in hotset:
            hotset.append(rdata[i])
print(hot, cold)
print(len(hotset), len(coldset))