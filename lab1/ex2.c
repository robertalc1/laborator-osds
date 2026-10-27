#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Utilizare: %s offset dimensiune\n", argv[0]);
        return 1;
    }

    char *end;
    long offset = strtol(argv[1], &end, 0);
    if (*end != '\0' || end == argv[1] || offset < 0) {
        fprintf(stderr, "Offset invalid.\n");
        return 1;
    }

    long size = strtol(argv[2], &end, 0);
    if (*end != '\0' || end == argv[2] || size <= 0 || size > 4096) {
        fprintf(stderr, "Dimensiune invalida.\n");
        return 1;
    }

    FILE *file = fopen("bin/dummy", "rb");
    if (file == NULL) {
        perror("fopen");
        return 1;
    }

    if (fseek(file, offset, SEEK_SET) != 0) {
        perror("fseek");
        fclose(file);
        return 1;
    }

    void *ptr = mmap(NULL, size, PROT_READ | PROT_WRITE | PROT_EXEC,
                     MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (ptr == MAP_FAILED) {
        perror("mmap");
        fclose(file);
        return 1;
    }

    if (fread(ptr, 1, size, file) != (size_t)size) {
        fprintf(stderr, "Nu s-au putut citi toti octetii.\n");
        fclose(file);
        munmap(ptr, size);
        return 1;
    }

    fclose(file);
    ((void (*)(void))ptr)();
    munmap(ptr, size);
    return 0;
}
