; Hola mundo version 64 bits
;nasm -f elf64 hola64-v2.asm -o hola64-v2.o
;ld -o hola64-v2 hola64-v2.o
;./hola64

%include 'stdio64.asm'

SECTION .data
    msg db "Hola perrines locos!", 10, 0

SECTION .text
    global _start
_start:
    mov rax, msg ; Length of the string
    call printStr
    call salir
