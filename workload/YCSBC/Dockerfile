# 使用官方的 Ubuntu 22.04 作为基础镜像
FROM ubuntu:22.04

# RUN apt-get update && apt-get install -y libtbb-dev libhiredis-dev
# RUN apt-get install -y g++ make
# 设置工作目录
WORKDIR /app

# 将编译好的可执行文件和配置文件复制到容器中

COPY ycsbc /app/ycsbc

# 设置容器启动时运行的命令
CMD ["./ycsbc", "-P", "/app/hash.spec"]