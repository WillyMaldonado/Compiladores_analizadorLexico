; Hola mundo version 64 bits
;nasm -f elf64 hola64.asm -o hola64.o
;ld -o hola64 hola64.o
;./hola64
SECTION .data
    msg db "Hola mundo!", 10

SECTION .text
    global _start
_start:
    mov rdx, 12 ; Length of the string
    mov rsi, msg ; Pointer to the string
    mov rdi, 1 ; File descriptor 1 (stdout)
    mov rax, 1 ; syscall number for sys_write
    syscall ; Call kernel
    mov rax , 60 ; syscall number for sys_exit
    xor rdi, rdi ; Exit code 0
    syscall ; Call kernel
    ; Exit the program
