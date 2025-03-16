#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <time.h>
#include <math.h>
#include <stdatomic.h>
#include <signal.h>
#include <stdint.h>
#include <math.h>
#include <sys/time.h>
#include <getopt.h>

// 配置参数
size_t MEMORY_SIZE = 1073741824;
char ACCESS_DISTRIBUTION[20] = "uniform";
int RW_RATIO = 70;
int ACCESS_SLEEP_TIME = 0;
int THREADS = 4;
int FIXED_MODE = 1;
int RECORD_INTERVAL = 1000;
int RECORD_SLEEP_INTERVAL = 1000;
int PROCESS_NUM=1;

size_t page_size;
size_t total_pages;
void *memory;
char *page_ops;
_Atomic int stop_flag = 0;

FILE *output_file = NULL;

_Atomic int stop = 0;

typedef struct {
    pthread_t thread;
    _Atomic uint64_t read_count;
    _Atomic uint64_t write_count;
    unsigned int seed;
    size_t seq_pos;
} ThreadData;

ThreadData *threads_data;

void parse_config(const char *filename);
void init_page_ops();
void* thread_func(void *arg);
size_t get_page_index(ThreadData *data);
size_t zipf_variate(unsigned int *seed);

void handle_signal(int sig) {
    stop_flag = 1;
}

void suspend(int sig){
    stop = 1;
}

void run(int sig){
    stop = 0;
}

void format_timestamp(char *buffer, size_t buffer_size) {
    struct timeval tv;
    struct tm tm_info;
    
    gettimeofday(&tv, NULL);
    localtime_r(&tv.tv_sec, &tm_info);
    
    strftime(buffer, buffer_size, "%Y-%m-%d %H:%M:%S", &tm_info);
    size_t len = strlen(buffer);
    snprintf(buffer + len, buffer_size - len, ".%03ld", tv.tv_usec / 1000);
}

void parse_arguments(int argc, char *argv[]) {
    int opt;
    while ((opt = getopt(argc, argv, "o:")) != -1) {
        switch (opt) {
            case 'o':
                output_file = fopen(optarg, "w");
                if (!output_file) {
                    perror("Failed to open output file");
                    exit(EXIT_FAILURE);
                }
                break;
            default:
                fprintf(stderr, "Usage: %s [-o output_file]\n", argv[0]);
                exit(EXIT_FAILURE);
        }
    }
}

// 修改后的输出函数
void print_statistics(const char *timestamp_buf, 
    uint64_t total_read, uint64_t total_write,
    uint64_t interval_read, uint64_t interval_write) {
    char buffer[256];
    snprintf(buffer, sizeof(buffer),
        "[%s] Interval: %lu (R:%lu W:%lu)\n",
        timestamp_buf,
        interval_read + interval_write,
        interval_read,
        interval_write
    );

    // 输出到文件或标准输出
    if (output_file) {
        fprintf(output_file, "%s", buffer);
        fflush(output_file);  // 确保内容立即写入文件
    } else {
        printf("%s", buffer);
    }
}

int main(int argc, char *argv[]) {
    signal(SIGINT, handle_signal);

    // 解析命令行参数
    parse_arguments(argc, argv);

    // 解析配置文件
    parse_config("config.cfg");

    // 创建PROCESS_NUM个进程
    for(int i=1;i<PROCESS_NUM;i++)
        fork();

    // 初始化页面大小和总页面数
    page_size = sysconf(_SC_PAGESIZE);
    total_pages = MEMORY_SIZE / page_size;
    MEMORY_SIZE = total_pages * page_size;

    // 分配对齐的内存区域
    if (posix_memalign(&memory, page_size, MEMORY_SIZE) != 0) {
        perror("posix_memalign");
        exit(EXIT_FAILURE);
    }

    // 初始化内存区域为 0
    memset(memory, 0, MEMORY_SIZE);

    // 如果启用固定模式，初始化页面操作类型
    if (FIXED_MODE) {
        init_page_ops();
    }

    // 创建线程数据数组
    threads_data = calloc(THREADS, sizeof(ThreadData));
    if (!threads_data) {
        perror("calloc");
        exit(EXIT_FAILURE);
    }

    // 创建线程
    for (int i = 0; i < THREADS; i++) {
        threads_data[i].seed = time(NULL) ^ i;
        threads_data[i].seq_pos = i * (total_pages / THREADS);
        if (pthread_create(&threads_data[i].thread, NULL, thread_func, &threads_data[i]) != 0) {
            perror("pthread_create");
            exit(EXIT_FAILURE);
        }
    }

    // 初始化统计变量
    uint64_t last_total_read = 0, last_total_write = 0;
    char timestamp_buf[64];

    // 主循环
    while (!stop_flag) {
        usleep(RECORD_INTERVAL * 1000);
        atomic_store(&stop, 1);
        usleep(RECORD_SLEEP_INTERVAL * 1000);
        atomic_store(&stop, 0);

        // 获取时间戳
        format_timestamp(timestamp_buf, sizeof(timestamp_buf));

        // 计算总量
        uint64_t current_total_read = 0, current_total_write = 0;
        for (int i = 0; i < THREADS; i++) {
            current_total_read += atomic_load(&threads_data[i].read_count);
            current_total_write += atomic_load(&threads_data[i].write_count);
        }

        // 计算增量
        uint64_t interval_read = current_total_read - last_total_read;
        uint64_t interval_write = current_total_write - last_total_write;

        // 输出统计信息
        print_statistics(timestamp_buf,
                        current_total_read, current_total_write,
                        interval_read, interval_write);

        // 保存当前值作为下次的上次值
        last_total_read = current_total_read;
        last_total_write = current_total_write;
    }

    // 等待所有线程结束
    for (int i = 0; i < THREADS; i++) {
        pthread_join(threads_data[i].thread, NULL);
    }

    // 释放资源
    free(memory);
    free(threads_data);
    if (FIXED_MODE) free(page_ops);

    // 关闭输出文件
    if (output_file) {
        fclose(output_file);
    }

    return 0;
}

void parse_config(const char *filename) {
    FILE *fp = fopen(filename, "r");
    char line[128];
    while (fgets(line, sizeof(line), fp)) {
        if (line[0] == '#' || line[0] == '\n') continue;
        
        char key[50], value[50];
        if (sscanf(line, "%[^=]=%s", key, value) == 2) {
            if (strcmp(key, "MEMORY_SIZE") == 0) {
                MEMORY_SIZE = strtoull(value, NULL, 10);
            } else if (strcmp(key, "ACCESS_DISTRIBUTION") == 0) {
                strncpy(ACCESS_DISTRIBUTION, value, sizeof(ACCESS_DISTRIBUTION));
            } else if (strcmp(key, "RW_RATIO") == 0) {
                RW_RATIO = atoi(value);
            } else if (strcmp(key, "ACCESS_SLEEP_TIME") == 0) {
                ACCESS_SLEEP_TIME = atoi(value);
            } else if (strcmp(key, "THREADS") == 0) {
                THREADS = atoi(value);
            } else if (strcmp(key, "FIXED_MODE") == 0) {
                FIXED_MODE = atoi(value);
            } else if (strcmp(key, "RECORE_TIMEINTERVAL") == 0) {
                RECORD_INTERVAL = atoi(value);
            } else if (strcmp(key, "RECORE_SLEEP_TIMEINTERVAL") == 0){
                RECORD_SLEEP_INTERVAL = atoi(value);
            } else if (strcmp(key, "PROCESS_NUM") == 0) {
                PROCESS_NUM = atoi(value);
            }
        }
    }
    fclose(fp);
}

void init_page_ops() {
    page_ops = malloc(total_pages);
    size_t read_pages = (total_pages * RW_RATIO) / 100;
    
    for (size_t i = 0; i < total_pages; i++) {
        page_ops[i] = (i < read_pages) ? 'R' : 'W';
    }

    for (size_t i = total_pages - 1; i > 0; i--) {
        size_t j = rand() % (i + 1);
        char tmp = page_ops[i];
        page_ops[i] = page_ops[j];
        page_ops[j] = tmp;
    }
}

void* thread_func(void *arg) {
    ThreadData *data = (ThreadData *)arg;
    while (!stop_flag) {
        size_t page_idx = get_page_index(data);
        volatile char *addr = (volatile char *)memory + page_idx * page_size;

        if (FIXED_MODE) {
            if (page_ops[page_idx] == 'R') {
                (void)*addr;
                atomic_fetch_add(&data->read_count, 1);
            } else {
                *addr = (char)rand_r(&data->seed);
                atomic_fetch_add(&data->write_count, 1);
            }
        } else {
            if (rand_r(&data->seed) % 100 < RW_RATIO) {
                (void)*addr;
                atomic_fetch_add(&data->read_count, 1);
            } else {
                *addr = (char)rand_r(&data->seed);
                atomic_fetch_add(&data->write_count, 1);
            }
        }

        if (ACCESS_SLEEP_TIME > 0) {
            usleep(ACCESS_SLEEP_TIME);
        }
        if (atomic_load(&stop))
            while (atomic_load(&stop)) usleep(1000);
    }
    return NULL;
}

size_t get_page_index(ThreadData *data) {
    if (strcmp(ACCESS_DISTRIBUTION, "uniform") == 0) {
        return rand_r(&data->seed) % total_pages;
    } else if (strcmp(ACCESS_DISTRIBUTION, "sequential") == 0) {
        size_t idx = data->seq_pos;
        data->seq_pos = (data->seq_pos + 1) % total_pages;
        return idx;
    } else if (strcmp(ACCESS_DISTRIBUTION, "zipf") == 0) {
        return zipf_variate(&data->seed);
    }
    return 0;
}

// 这个计算的开销也有点太大了，导致每10ms最多才能访问744次内存
size_t zipf_variate_fast(unsigned int *seed, size_t total_pages, double alpha) {
    // 生成均匀分布的随机数 u ∈ (0,1)
    double u = (double)rand_r(seed) / (double)RAND_MAX;

    // 处理 alpha=1 的特殊情况（需单独优化）
    if (alpha == 1.0) alpha = 1.000001;

    // 近似公式：通过逆变换法直接计算 Key
    double numerator = pow(total_pages, 1.0 - alpha) - 1.0;
    double k = pow(u * numerator + 1.0, 1.0 / (1.0 - alpha)) - 1.0;

    // 四舍五入并限制范围
    size_t result = (size_t)(k + 0.5);
    if (result >= total_pages) result = total_pages - 1;

    return result;
}

size_t zipf_variate(unsigned int *seed) {
    return zipf_variate_fast(seed, total_pages, 0.99);
}