set pagination off
set disassembly-flavor intel
break main
run
disassemble main
set $return_address = $rip
set {char[21]} message = "Robert - laborator 1"
set $rdi = (unsigned long)&message
set $rsp = $rsp - 8
set {unsigned long}$rsp = $return_address
set $rip = (unsigned long)print_msg
tbreak *$return_address
continue
