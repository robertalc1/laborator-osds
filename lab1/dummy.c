void foo() {
    asm volatile (
        "subq $16, %%rsp;"
        "movb $'h', (%%rsp);"
        "movb $'a', 1(%%rsp);"
        "movb $'x', 2(%%rsp);"
        "movb $'x', 3(%%rsp);"
        "movb $'l', 4(%%rsp);"
        "movb $'o', 5(%%rsp);"
        "movb $'l', 6(%%rsp);"
        "movb $0, 7(%%rsp);"
        "movl $1, %%eax;"
        "movl $1, %%edi;"
        "movq %%rsp, %%rsi;"
        "movl $8, %%edx;"
        "syscall;"
        "addq $16, %%rsp;"
        :
        :
        : "%edi", "%rsi", "%edx"
    );
}

int main() {
    return 0;
}
