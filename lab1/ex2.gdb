set pagination off
set disassembly-flavor intel
break ex2.c:36
run 0x1106 0x4e
vmmap
next
p/x ptr
vmmap
tbreak ex2.c:52
continue
x/24i ptr
