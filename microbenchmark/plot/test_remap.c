#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <time.h>
#include <string.h>

#define SIZE (1 * 1024 * 1024 * 1024) // 1GB

int main() {
    // 初始映射1GB内存
    void *old_addr = mmap(NULL, SIZE, PROT_READ | PROT_WRITE, 
                        MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);
    if (old_addr == MAP_FAILED) {
        perror("Initial mmap failed");
        return EXIT_FAILURE;
    }
    memset(old_addr, 0, SIZE);  // 初始化内存

    // 记录开始时间
    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    // 执行内存重映射（保持相同大小）
    void *new_addr = mremap(old_addr, SIZE, SIZE, MREMAP_MAYMOVE);
    if (new_addr == MAP_FAILED) {
        perror("mremap failed");
        munmap(old_addr, SIZE);  // 失败时释放原始内存[1](@ref)
        return EXIT_FAILURE;
    }

    // 记录结束时间
    clock_gettime(CLOCK_MONOTONIC, &end);

    // 计算并输出时间
    double elapsed = (end.tv_sec - start.tv_sec) + 
                    (end.tv_nsec - start.tv_nsec) / 1e9;
    printf("mremap 1GB time: %.6f seconds\n", elapsed);

    // 释放重映射后的内存
    if (munmap(new_addr, SIZE) == -1) {
        perror("munmap failed");
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}