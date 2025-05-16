#define _GNU_SOURCE
#define _POSIX_C_SOURCE 200809L

#include <sys/types.h>
#include <sys/mman.h>

#include <unistd.h>

#include <err.h>
#include <errno.h>

size_t min(size_t x, size_t y)
{
    return x > y ? y : x;
}

/**
 * @param len != 0
 */
void fdput(int fd, const char *str, size_t len)
{
    size_t cnt = 0;
    do {
        ssize_t result = write(fd, str + cnt, min(len - cnt, 0x7ffff000));
        if (result == -1) {
            if (errno == EINTR)
                continue;
            err(1, "%s failed", "write");
        }
        cnt += result;
    } while (cnt != len);
}
#define fdputc(fd, constant_str) fdput((fd), (constant_str), sizeof(constant_str) - 1)

int main(int argc, char* argv[])
{
    int fd = memfd_create("script", 0);
    if (fd == -1)
        err(1, "%s failed", "memfd_create");

    fdputc(fd, "#!/bin/bash\necho 'Hello\n' >> test.txt");

    {
        const char * const argv[] = {"script", NULL};
        const char * const envp[] = {NULL};
        fexecve(fd, (char * const *) argv, (char * const *) envp);
    }

    err(1, "%s failed", "fexecve");
}
