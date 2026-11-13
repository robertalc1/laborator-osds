# Laboratorul 2 — Depășirea bufferului și pwntools

Cerințe: [Laboratory 0x02](https://github.com/Costinteo/osds-lab/tree/main/lab2). Fișierele profesorului sunt păstrate în `original/`; sursele C din rădăcina acestui director sunt copii de lucru. Exercițiile suplimentare sunt opționale.

## Pregătire

Din `lab2`, în Ubuntu WSL:

```sh
make ex1 ex2 ex3 ex4
/home/robert/osds-python/.venv/bin/python -c 'import pwn'
```

Compilarea locală a reușit pentru toate cele patru programe. `ex4` emite avertismentul așteptat pentru `gets`, funcție nesigură. Makefile folosește `-fno-stack-protector -no-pie -g`; pentru `ex4` adaugă `-zexecstack`. Protecțiile sunt reduse doar pentru exercițiul local.

## Exercițiul 1 — Q1–Q3

`password` este un tablou local de 8 octeți. `scanf("%s", password)` nu limitează intrarea, astfel încât un cuvânt prea lung poate scrie peste alte date din cadrul lui `main`. `is_admin` începe la zero și devine 1 când parola coincide cu secretul. **Q1:** dacă depășirea modifică `is_admin` într-o valoare nenulă, verificarea finală poate acorda acces fără parola corectă. **Q2:** aceasta este calea de ocolire; distanța exactă depinde de binarul compilat. Terminatorul nul scris de `scanf` trebuie inclus în analiză.

**Q3:** în GDB, după `break main` și `run`, folosim `p/x &password`, `p/x &is_admin`, `p/x $rbp`, `x/48bx &password` și `disassemble main`. Diferența adreselor arată ordinea și spațiile de aliniere; examinarea după `scanf` arată octeții modificați. Nu presupunem că ordinea declarațiilor este și ordinea pe stivă.

## Exercițiul 2 — Q4

Condiția cere valoarea numerică `0xDEADBEEF`, de tip `long`. Pe x86_64, octeții corespunzători valorii sunt în ordine little endian: `ef be ad de 00 00 00 00`. După determinarea distanței dintre `password` și `is_admin`, **Q4:** `echo -ne` poate transmite umplutura urmată de acești octeți, apoi un spațiu sau newline pentru încheierea conversiei `%s`. `echo` și shellul pot interpreta diferit octeții nuli; Python/pwntools este mai reproductibil. În `original/solve_ex2.py` există șablonul profesorului. Se poate folosi `p64(0xDEADBEEF)` și `send`, după stabilirea offsetului în debugger.

## Exercițiul 3 — Q5

`win()` afișează `ESCAPING THE MATRIX...`, dar `main()` nu o apelează. `buffer[32]` primește intrare nelimitată prin `%s`. Pe Linux x86_64, `call` pune adresa de întoarcere pe stivă; prologul uzual salvează `RBP`, iar `ret` citește adresa de întoarcere. **Q5:** numărul de octeți este `($rbp + 8) - (char *)&buffer` la oprirea în `main`, înainte de revenire. Se poate verifica și cu `disassemble main` sau un model ciclic pwntools. O intrare prea lungă poate înlocui adresa de întoarcere cu adresa lui `win`, obținută prin `p/x win` sau `nm bin/ex3`. Alinierea stivei trebuie verificată dacă se apelează funcții libc după redirecționare.

## Exercițiul 4 — Q6–Q7

`gets(buffer)` nu cunoaște dimensiunea tabloului de 256 de octeți. Programul tipărește adresa acestui buffer, apoi citește intrarea. Stiva a fost marcată executabilă pentru experiment. **Q6:** primul argument al `execve` are tipul `const char *`: un pointer către un șir C terminat cu octet nul, care numește executabilul. **Q7:** dacă șirul `/bin/sh\0` este inclus în buffer, adresa lui se obține adăugând offsetul său în payload la adresa bufferului afișată de program. În convenția syscall Linux x86_64, numărul apelului se pune în `RAX`, iar primele trei argumente în `RDI`, `RSI`, `RDX`. ASLR poate schimba adresa la fiecare rulare, deci trebuie citită pentru procesul curent. Șablonul de experiment se află în `original/solve_ex4.py`.

## Verificare și limite

Comanda de compilare de mai sus a reușit. Importul pwntools nu a fost verificat în aceeași comandă deoarece rularea GDB s-a oprit mai devreme: mediul curent a returnat `ptrace: Operation not permitted` și `Could not trace the inferior process`. Prin urmare nu sunt raportate offseturi, adrese sau rezultate de exploatare ca observații locale. Pentru acestea, rulați comenzile GDB în Ubuntu WSL cu acces `ptrace`, apoi completați valorile specifice binarului vostru. Sursele C nu au fost modificate.
