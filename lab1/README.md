# Laboratorul 1 — Memorie virtuală și procese

Cerințe: [Laboratory 0x01](https://github.com/Costinteo/osds-lab/tree/main/lab1).

## Pregătire

Comenzile de mai jos se rulează din directorul `lab1`, în Ubuntu prin WSL.

```sh
make ex1
make dummy
make ex2
make ex3
```

Makefile folosește opțiunile din laborator: `-fno-stack-protector -no-pie -g`. Prima dezactivează protecția cu stack canary, a doua produce un executabil fără PIE, iar ultima adaugă informații pentru debugger.

Verificarea a fost făcută pe Ubuntu 26.04, x86_64, cu GCC 15.2 și GDB 17.1 + GEF. Adresele și dimensiunile de mai jos sunt cele obținute aici. Ele pot diferi cu alt compilator.

## Exercițiul 1

`ex1.c` stă într-o buclă infinită, astfel încât procesul să poată fi inspectat. Pentru pornire direct din debugger:

```sh
gdb -q bin/ex1
```

În GDB:

```gdb
break main
run
vmmap
info address useful
x/s useful
search-pattern "Where is this located?"
info address bar
disassemble bar
```

Aceste comenzi se află și în `ex1.gdb`:

```sh
gdb -q -x ex1.gdb bin/ex1
```

Varianta cu două terminale din cerință funcționează astfel. În primul rulezi `./bin/ex1`. În al doilea, din același director, rulezi `sudo gdb -p $(pgrep -n -x ex1) -x ~/.gdbinit`. La final, `detach` eliberează procesul, iar în primul terminal îl oprești cu Ctrl+C.

### Q1 — Unde sunt mapate secțiunile?

Memoria virtuală reprezintă adresele văzute de proces. Sistemul de operare le asociază unor pagini de memorie fizică. Două procese pot folosi aceeași adresă virtuală fără să folosească aceeași pagină fizică.

În terminal putem compara secțiunile ELF cu segmentele încărcate:

```sh
readelf -SW bin/ex1
readelf -lW bin/ex1
objdump -h bin/ex1
```

`readelf -lW` arată și corespondența dintre secțiuni și segmente. În GDB, `info files` arată intervalele secțiunilor, iar `vmmap` arată mapările și permisiunile lor. Acestea sunt două niveluri diferite: secțiunile descriu organizarea fișierului, segmentele sunt folosite pentru încărcare.

| Secțiune | Conținut | Adresă de început observată | Permisiuni ale mapării |
| --- | --- | --- | --- |
| `.text` | Instrucțiunile funcțiilor | `0x401050` | `r-x` |
| `.rodata` | Date constante | `0x402000` | `r--` |
| `.data` | Globale inițializate cu valori nenule | `0x404010` | `rw-` |
| `.bss` | Globale neinițializate sau inițializate cu zero | `0x404037` | `rw-` |

`r` înseamnă citire, `w` scriere, iar `x` execuție.

`useful` se află la `0x404020`, în `.data`. Deși conține un șir, declarația este `char useful[]`, deci octeții lui pot fi modificați. În acest executabil, textul este păstrat în tabloul global, nu într-un obiect separat din `.rodata`.

`.bss` ocupă memorie la rulare, dar nu stochează în fișier toți octeții zero. În program nu există o globală proprie neinițializată; mica secțiune `.bss` provine din codul de inițializare legat de compilator.

Pentru experimentul cu alte tipuri sugerat în cerință, se pot adăuga temporar înainte de `bar` declarațiile `int a;`, `int b = 0;`, `int c = 7;` și `const char text[] = "constant";`. După recompilare, `a` și `b` sunt în `.bss`, `c` în `.data`, iar `text` în `.rodata`. Versiunea păstrată în repository este cea din enunț.

Mapările pot fi văzute și din celălalt terminal, cât timp `ex1` rulează:

```sh
cat /proc/$(pgrep -n -x ex1)/maps
```

### Q2 — Adresa și dezasamblarea lui bar

`info address bar` indică `0x401136`. Comanda `disassemble bar` arată instrucțiunile funcției. Se observă pregătirea cadrului de stivă, apelul `puts` din buclă și instrucțiunea `ret` de la final.

## Exercițiul 2

`ex2.c` deschide `bin/dummy`, citește octeții funcției `foo()` și îi copiază într-o zonă obținută cu `mmap`. Apoi convertește adresa într-un pointer la funcție și o apelează.

Mai întâi aflăm poziția și dimensiunea funcției:

```sh
objdump -d -F bin/dummy
nm -S bin/dummy
```

În executabilul verificat, `foo` începe la adresa virtuală `0x401106`, iar `objdump -F` indică offsetul în fișier `0x1106`. Ultima instrucțiune este `ret` la `0x401153`, de un octet. Dimensiunea este `0x401154 - 0x401106 = 0x4e`, adică 78 de octeți. `nm -S` confirmă dimensiunea.

```sh
./bin/ex2 0x1106 0x4e
```

Rezultatul este `haxxlol`. Funcția scrie și un octet nul la final, fără newline. Pentru a vedea exact cei opt octeți:

```sh
./bin/ex2 0x1106 0x4e | od -An -tx1
```

Rezultat:

```text
68 61 78 78 6c 6f 6c 00
```

Primul argument al loaderului este offsetul în fișier, al doilea este numărul de octeți copiați. Dacă `dummy.c` sau compilatorul se schimbă, aceste valori trebuie recalculate. Actualizează și linia `run` din `ex2.gdb`.

### Q3 — Ce se schimbă în vmmap după mmap?

```sh
gdb -q -x ex2.gdb bin/ex2
```

Scriptul se oprește înainte de `mmap`, afișează mapările, execută apelul cu `next` și le afișează din nou. După citirea octeților, se oprește înainte de apelul prin pointer și afișează instrucțiunile copiate.

În verificare, `ptr` a fost `0x7ffff7fb5000`, într-o mapare anonimă de la `0x7ffff7fb5000` până la `0x7ffff7fb6000`, cu permisiuni `rwx`. Adresa poate fi diferită la altă rulare. Zona este anonimă deoarece nu este asociată direct unui fișier: programul copiază în ea octeții prin `fread`.

Deși sunt ceruți numai 78 de octeți, maparea ocupă o pagină de 4096 de octeți pe sistemul verificat. `PROT_READ | PROT_WRITE | PROT_EXEC` permite citirea, copierea și apoi executarea codului, conform exercițiului.

De la oprirea dinaintea apelului, folosește `display/i $pc` și `si` repetat. Prima instrucțiune executată este încă în `main`; continuă până când `$rip` ajunge în zona indicată de `ptr`. `si` intră în apel, în timp ce `ni` execută apelul fără să urmărească fiecare instrucțiune din interior. `continue` lasă programul să termine.

Copierea este suficientă pentru această funcție, care construiește șirul pe stivă și folosește direct syscall-ul `write`. Nu este un loader ELF complet și nu rezolvă relocările necesare altor funcții.

## Exercițiul 3

```sh
objdump -d -M intel bin/ex3
gdb -q -x ex3.gdb bin/ex3
```

### Q4 — Cum identificăm argumentele?

Pe Linux x86_64, primele șase argumente întregi sau pointeri sunt transmise prin `RDI`, `RSI`, `RDX`, `RCX`, `R8` și `R9`. Pentru un `int` se pot folosi cei 32 de biți inferiori ai registrului, de exemplu `EDI`.

Chiar înainte de `call advertisment`, apar:

```asm
lea rax, [rbp-0x100]
mov rsi, rax
mov edi, edx
call advertisment
```

`RSI` primește adresa tabloului `name`, iar `EDI` primește numărul calculat prin `rand() % 10`. Ordinea corespunde semnăturii `advertisment(int num, char *target)`.

### Apelarea funcției care nu este apelată în program

`print_msg` există în sursă, dar nu este apelată de `main`. În GDB, după `break main` și `run`, modificările se fac numai prin `set`:

```gdb
set $return_address = $rip
set {char[21]} message = "Robert - laborator 1"
set $rdi = (unsigned long)&message
set $rsp = $rsp - 8
set {unsigned long}$rsp = $return_address
set $rip = (unsigned long)print_msg
```

`message` are loc pentru textul ales, inclusiv terminatorul nul. `RDI` primește adresa lui. Pe stivă este rezervat spațiul de opt octeți în care un `call` ar fi pus adresa de întoarcere. În acel loc se scrie instrucțiunea din `main` la care vrem să revenim. Modificarea lui `RIP` mută execuția la `print_msg`.

Fișierul `ex3.gdb` adaugă un breakpoint la adresa de revenire și continuă execuția. Rezultatul este:

```text
-==[ Robert - laborator 1 ]==-
```

După revenirea în `main`, tastează `continue` și introdu numele când programul îl cere. Programul poate continua normal. Pentru reluare de la început, închide GDB și rulează din nou comanda.

### Q5 — De ce poate apărea SIGSEGV în printf?

Convenția de apel cere ca `RSP` să fie multiplu de 16 înainte de `call`. Instrucțiunea `call` pune pe stivă o adresă de opt octeți, deci la intrarea în funcție `RSP % 16` trebuie să fie 8.

Simpla schimbare a lui `RIP` nu execută un `call`: nu pregătește nici alinierea, nici adresa de întoarcere. O funcție din libc poate folosi instrucțiuni precum `movaps`, care cer aliniere la 16 octeți, iar o adresă nealiniată poate produce `SIGSEGV`.

În experimentul local cu salt direct, fără pregătirea stivei, nu a apărut o eroare în `printf`; execuția a ajuns la adresa invalidă `0x1` la întoarcere. Aceasta era valoarea luată greșit de `ret` de pe stivă. Comportamentul exact depinde de versiunea libc și de calea executată. În varianta corectă din `ex3.gdb`, am pregătit atât alinierea, cât și adresa de revenire, iar programul a terminat normal.

## Imaginile din material

Cele trei imagini folosite de laboratorul 1 sunt [memoria virtuală](https://github.com/Costinteo/osds-lab/blob/main/img/procvm.png), [procesul compilării](https://github.com/Costinteo/osds-lab/blob/main/img/compilation_process.png) și [convenția de apel](https://github.com/Costinteo/osds-lab/blob/main/img/calling_convention.png). Ele explică, în această ordine, maparea secțiunilor, transformarea sursei în instrucțiuni și organizarea unui apel de funcție.

Rezolvarea acoperă exercițiile 1–3 și întrebările Q1–Q5. Secțiunea „Extra Challenges” din material conține extensii opționale.

## Verificare

Toate cele patru programe au fost compilate în WSL. Cele trei fișiere `.gdb` au rulat fără erori. Loaderul a returnat codul 0 și exact octeții de mai sus; au fost verificate și argumentele lipsă, offsetul invalid sau negativ, dimensiunea invalidă și citirea din afara fișierului. Experimentul cu `print_msg` a afișat mesajul ales, apoi `ex3` a continuat și s-a încheiat cu codul 0 după introducerea numelui.
