import re
import json

texto = """
if (x) {
    while (y) {
        z;
    }
} else {
    w;
}
"""

# Definir patrones de tokens
token_patron = {
    "KEYWORD": r'\b(int|void|return|if|else|while)\b',
    "IDENTIFIER": r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',
    "NUMBER": r'\b\d+(\.\d+)?\b',
    "OPERATOR": r'[+\-*/=<>]',
    "DELIMITER": r'[(),;{}]',
    "WHITESPACE": r'\s+'
}

def tokenize(text):
    patron_general = "|".join(f"(?P<{token}>{patron})" for token, patron in token_patron.items())
    patron_regex = re.compile(patron_general)
    tokens_encontrados = [(m.lastgroup, m.group()) for m in patron_regex.finditer(text) if m.lastgroup != "WHITESPACE"]
    return tokens_encontrados

tokens = tokenize(texto)

# Clases necesarias para interpretar el código (incluyendo while y if)
class TablaSimbolos:
    def __init__(self):
        self.tabla = {}
        self.offset_actual = 0  # Desplazamiento desde rbp
    
    def agregar_variable(self, nombre, tipo):
        self.offset_actual += 8
        self.tabla[nombre] = {"tipo": tipo, "offset": self.offset_actual}
        return self.offset_actual
    
    def obtener_offset(self, nombre):
        if nombre in self.tabla:
            return self.tabla[nombre]["offset"]
        raise Exception(f"Variable {nombre} no encontrada")

    def tiene_variable(self, nombre):
        return nombre in self.tabla

class GestorRegistros:
    def __init__(self):
        self.registros = ["rax", "rbx", "rcx", "rdx", "rsi", "rdi", "r8", "r9", "r10", "r11"]
        self.en_uso = set()
    
    def obtener_registro(self):
        for reg in self.registros:
            if reg not in self.en_uso:
                self.en_uso.add(reg)
                return reg
        raise Exception("No hay registros disponibles")
    
    def liberar_registro(self, reg):
        if reg in self.en_uso:
            self.en_uso.remove(reg)

# Implementación del parser para estructuras if y while
class NodoCondicional:
    def __init__(self, condicion, cuerpo, alternativo=None):
        self.condicion = condicion
        self.cuerpo = cuerpo
        self.alternativo = alternativo
    
    def generar_codigo(self, tabla_simbolos):
        codigo = self.condicion.generar_codigo(tabla_simbolos)
        etiqueta_verdadera = f"true_{id(self)}"
        etiqueta_falsa = f"false_{id(self)}"
        etiqueta_final = f"end_{id(self)}"

        # Generar código para condición (si es verdadera, ejecuta el cuerpo)
        codigo += f"    cmp rax, 0\n"
        codigo += f"    je {etiqueta_falsa}\n"  # Si la condición es falsa, salta

        # Código para el cuerpo
        for instruccion in self.cuerpo:
            codigo += instruccion.generar_codigo(tabla_simbolos)
        
        # Si hay un bloque alternativo (else)
        if self.alternativo:
            codigo += f"    jmp {etiqueta_final}\n"
            codigo += f"{etiqueta_falsa}:\n"
            for instruccion in self.alternativo:
                codigo += instruccion.generar_codigo(tabla_simbolos)
        
        codigo += f"{etiqueta_final}:\n"
        return codigo

class NodoWhile:
    def __init__(self, condicion, cuerpo):
        self.condicion = condicion
        self.cuerpo = cuerpo
    
    def generar_codigo(self, tabla_simbolos):
        etiqueta_inicio = f"start_{id(self)}"
        etiqueta_final = f"end_{id(self)}"
        
        codigo = f"{etiqueta_inicio}:\n"
        # Generamos código para la condición del while
        condicion_codigo = self.condicion.generar_codigo(tabla_simbolos)
        codigo += condicion_codigo
        codigo += f"    cmp rax, 0\n"
        codigo += f"    je {etiqueta_final}\n"
        
        # Código para el cuerpo del while
        for instruccion in self.cuerpo:
            codigo += instruccion.generar_codigo(tabla_simbolos)
        
        # Salto al inicio del bucle
        codigo += f"    jmp {etiqueta_inicio}\n"
        codigo += f"{etiqueta_final}:\n"
        return codigo

# Implementación de las demás clases para generar código (asignación, operaciones, etc.)
# La estructura general sigue siendo la misma que te compartí antes.

# Parser modificado para manejar estructuras condicionales y de bucle
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def obtener_token_actual(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def coincidir(self, tipo_esperado):
        token_actual = self.obtener_token_actual()
        if token_actual and token_actual[0] == tipo_esperado:
            self.pos += 1
            return token_actual[1]
        else:
            raise SyntaxError(f'Error: se esperaba {tipo_esperado}, encontrado: {token_actual}')

    def parsear(self):
        instrucciones = []
        while self.obtener_token_actual():
            token_actual = self.obtener_token_actual()
            if token_actual[0] == "KEYWORD" and token_actual[1] == "if":
                instrucciones.append(self.parsear_if())
            elif token_actual[0] == "KEYWORD" and token_actual[1] == "while":
                instrucciones.append(self.parsear_while())
            else:
                instrucciones.append(self.parsear_asignacion())
        return instrucciones

    def parsear_if(self):
        self.coincidir("KEYWORD")  # if
        self.coincidir("DELIMITER")  # (
        condicion = self.expresion()
        self.coincidir("DELIMITER")  # )
        self.coincidir("DELIMITER")  # {
        cuerpo = self.cuerpo()
        alternativo = None
        if self.obtener_token_actual() and self.obtener_token_actual()[0] == "KEYWORD" and self.obtener_token_actual()[1] == "else":
            self.coincidir("KEYWORD")  # else
            self.coincidir("DELIMITER")  # {
            alternativo = self.cuerpo()
        self.coincidir("DELIMITER")  # }
        return NodoCondicional(condicion, cuerpo, alternativo)

    def parsear_while(self):
        self.coincidir("KEYWORD")  # while
        self.coincidir("DELIMITER")  # (
        condicion = self.expresion()
        self.coincidir("DELIMITER")  # )
        self.coincidir("DELIMITER")  # {
        cuerpo = self.cuerpo()
        self.coincidir("DELIMITER")  # }
        return NodoWhile(condicion, cuerpo)

    def expresion(self):
        # Aquí va la lógica de expresiones como se definió antes
        pass

    def cuerpo(self):
        # Aquí va la lógica del cuerpo de la función
        pass

class GeneradorEnsamblador:
    def __init__(self, instrucciones):
        self.instrucciones = instrucciones

    def generar(self):
        codigo = ""
        for instruccion in self.instrucciones:
            codigo += instruccion.generar_codigo(None)  # Aquí deberías pasar la tabla de símbolos adecuada
        return codigo

# Ejemplo de uso del parser modificado
def main():
    tokens = tokenize(texto)
    parser = Parser(tokens)
    instrucciones = parser.parsear()
    
    # Generar código de ensamblador con las instrucciones parseadas
    generador = GeneradorEnsamblador(instrucciones)
    codigo_ensamblador = generador.generar()
    
    # Imprimir el código generado
    print(codigo_ensamblador)

if __name__ == "__main__":
    main()
