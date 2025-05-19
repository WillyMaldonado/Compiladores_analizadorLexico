%include "stdio.asm";
section .data 
    msg db "Como estan perros", 0Ah,0 ; The string to print, followed by a newline character

section .text
    global _start ; Entry point for the program
_start:
    ;------------------printing the string print(msg)------------------
    mov eax, msg;
    call printstr
    call quit
;------------------end of the program------------------



