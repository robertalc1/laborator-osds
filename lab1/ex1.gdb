set pagination off
set disassembly-flavor intel
break main
run
vmmap
info address useful
x/s useful
search-pattern "Where is this located?"
info address bar
disassemble bar
