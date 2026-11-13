# Laborator OSDS

Rezolvări pentru Operating Systems: Design and Security, lucrate în Ubuntu prin WSL 2, pe x86_64.

Materiale: [Costinteo/osds-lab](https://github.com/Costinteo/osds-lab), versiunea `27a6cf1`.

## Laboratoare

- [Laboratorul 1 — memorie virtuală și procese](lab1/README.md): exercițiile 1–3 și răspunsurile Q1–Q5.
- [Laboratorul 2 – Buffer Overflow și pwntools](lab2/README.md): exercițiile 1–4 și bonus.

Fișierele `ex1.c`, `ex3.c` și `dummy.c` provin din materialele laboratorului. Au fost păstrate instrucțiunile programelor și eliminate comentariile. `ex2.c` completează șablonul loaderului. Comenzile din fișierele `.gdb` reproduc experimentele.

## Pornire pe calculatorul local

Deschide Ubuntu din meniul Start sau scrie `wsl -d Ubuntu` în PowerShell. În terminalul Ubuntu:

```sh
cd '/mnt/c/Users/user/Documents/ChatGPT/OSDS - SAL (LAB)/lab1'
make ex1
gdb -q -x ex1.gdb bin/ex1
```

În GDB, `quit` închide debuggerul. Dacă întreabă dacă vrei să oprești procesul, răspunde `y`.

Pe acest calculator sunt instalate GCC, Make, Binutils, GDB și GEF. GEF se încarcă din `/root/.gdbinit`. Pașii și explicațiile fiecărui exercițiu sunt în [lab1/README.md](lab1/README.md).
