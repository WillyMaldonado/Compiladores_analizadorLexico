;------------------------ int strlen(cadena)-----------------------------
strLen:
    push rsi ; resguardar en pila rsi
    mov rsi, rax 
sigChar:
    cmp byte[rax], 0
    jz  finStrLen
    inc rax
    jmp sigChar
finStrLen:
    sub rax,rsi
    pop rsi ;restauro el contenido previo de rsi
    ret




;-------------printStr(cadena)----------------------
printStr:
    ; guardar registros en pila
    push rdx 
    push rsi 
    push rdi
    push rax
    ; --------------------- llamada a longitud de cadena (cadena en rax)
    call strLen
    ;---------------------- la longitud se devuelve en rax
    mov rdx, rax;longitud cadena
    pop rax
    mov rsi, rax; Pointer to the string
    mov rdi, 1 ; File descriptor 1 (stdout)
    mov rax, 1 ; syscall number for sys_write
    syscall ; Call kernel
    ; ------------------------- devolver el contenido de los registros
    pop rdi
    pop rsi 
    pop rdx
    ret 

    ; ----------------------- salir()---------------------------------
salir:
    mov rax , 60 ; syscall number for sys_exit
    xor rdi, rdi ; Exit code 0
    syscall ; Call kernel
    ret
    ; Exit the program
