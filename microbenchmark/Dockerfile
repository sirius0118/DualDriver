# 使用官方的 Ubuntu 22.04 作为基础镜像
FROM ubuntu:22.04

# 设置工作目录
WORKDIR /app

# 将编译好的可执行文件和配置文件复制到容器中
COPY test /app/test
COPY config.cfg /app/config.cfg

# 设置容器启动时运行的命令
CMD ["./test", "-o", "/app/result.log"]