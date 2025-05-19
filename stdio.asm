
    ; calculate string length
    strlen:
    push  ebx
    mov ebx, eax ; point to string
    nextChar:
    cmp byte [eax], 0 ; check for null terminator
    jz endlen
    inc eax ; move to next character
    jmp nextChar ; repeat until null terminator
    endlen:
    sub eax, ebx ; calculate length
    pop ebx ; restore registers
    ret ; return to caller
    ;------------------printing the string print(msg)------------------
    printstr:
    ; save registers to stack
    push edx
    push ecx
    push ebx
    push eax ;point to string
    ; calculate string length
    call strlen
    mov edx, eax ; Length of the string
    pop eax ; Restore the pointer to the string
    mov ecx,eax; Pointer to the string
    mov ebx, 1 ; File descriptor 1 (stdout)
    mov eax, 4 ; syscall number for sys_write 
    int 0x80 ; Call kernel

    pop ebx ; Restore registers
    pop ecx
    pop edx
    ret ; return to caller
    ; Exit the program
    quit:
    mov ebx, 0 ; Exit code 0
    mov eax, 1 ; syscall number for sys_exit
    int 0x80 ; Call kernel