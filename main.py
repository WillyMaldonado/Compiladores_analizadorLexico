import re
import json

texto = """
int suma(int a, int b) {
    int c = a + b;
    return c;
}
void main() {
    suma(2, 3);
}
"""

# Definir patrones de tokens
token_patron = {
    "KEYWORD": r'\b(int|void|return)\b',
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

class NodoFuncion:
    def __init__(self, tipo, nombre, parametros, cuerpo):
        self.tipo = tipo
        self.nombre = nombre
        self.parametros = parametros
        self.cuerpo = cuerpo

class NodoParametro:
    def __init__(self, tipo, nombre):
        self.tipo = tipo
        self.nombre = nombre

class NodoAsignacion:
    def __init__(self, nombre, expresion):
        self.nombre = nombre
        self.expresion = expresion

class NodoOperacion:
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.operador = operador
        self.derecha = derecha

class NodoIdentificador:
    def __init__(self, nombre):
        self.nombre = nombre

class NodoNumero:
    def __init__(self, valor):
        self.valor = valor

class NodoReturn:
    def __init__(self, expresion):
        self.expresion = expresion

class NodoLlamadaFuncion:
    def __init__(self, nombre, argumentos):
        self.nombre = nombre
        self.argumentos = argumentos

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
        funciones = []
        while self.obtener_token_actual():
            funciones.append(self.definir_funcion())
        if not any(f.nombre == "main" for f in funciones):
            raise SyntaxError("Error: No se encontró la función main().")
        return funciones

    def definir_funcion(self):
        tipo = self.coincidir("KEYWORD")
        nombre = self.coincidir("IDENTIFIER")
        self.coincidir("DELIMITER")  # (
        parametros = self.parametros()
        self.coincidir("DELIMITER")  # )
        self.coincidir("DELIMITER")  # {
        cuerpo = self.cuerpo()
        self.coincidir("DELIMITER")  # }
        return NodoFuncion(tipo, nombre, parametros, cuerpo)

    def parametros(self):
        parametros = []
        if self.obtener_token_actual() and self.obtener_token_actual()[0] == "KEYWORD":
            tipo = self.coincidir("KEYWORD")
            nombre = self.coincidir("IDENTIFIER")
            parametros.append(NodoParametro(tipo, nombre))
            while self.obtener_token_actual() and self.obtener_token_actual()[1] == ',':
                self.coincidir("DELIMITER")
                tipo = self.coincidir("KEYWORD")
                nombre = self.coincidir("IDENTIFIER")
                parametros.append(NodoParametro(tipo, nombre))
        return parametros

    def cuerpo(self):
        instrucciones = []
        while self.obtener_token_actual() and self.obtener_token_actual()[1] != '}':
            token_actual = self.obtener_token_actual()
            if token_actual[0] == "KEYWORD" and token_actual[1] == "return":
                instrucciones.append(self.instruccion_return())
            elif token_actual[0] == "IDENTIFIER":
                instrucciones.append(self.llamada_funcion())
            else:
                instrucciones.append(self.asignacion())
        return instrucciones

    def asignacion(self):
        tipo = self.coincidir("KEYWORD")
        nombre = self.coincidir("IDENTIFIER")
        self.coincidir("OPERATOR")
        expresion = self.expresion()
        self.coincidir("DELIMITER")  # ;
        return NodoAsignacion(nombre, expresion)

    def instruccion_return(self):
        self.coincidir("KEYWORD")  # return
        expresion = self.expresion()
        self.coincidir("DELIMITER")  # ;
        return NodoReturn(expresion)

    def llamada_funcion(self):
        nombre = self.coincidir("IDENTIFIER")
        self.coincidir("DELIMITER")  # (
        argumentos = []
        if self.obtener_token_actual() and self.obtener_token_actual()[0] in {"IDENTIFIER", "NUMBER"}:
            argumentos.append(self.expresion())
            while self.obtener_token_actual() and self.obtener_token_actual()[1] == ',':
                self.coincidir("DELIMITER")
                argumentos.append(self.expresion())
        self.coincidir("DELIMITER")  # )
        self.coincidir("DELIMITER")  # ;
        return NodoLlamadaFuncion(nombre, argumentos)

    def expresion(self):
        izquierda = self.termino()
        while self.obtener_token_actual() and self.obtener_token_actual()[0] == "OPERATOR":
            operador = self.coincidir("OPERATOR")
            derecha = self.termino()
            izquierda = NodoOperacion(izquierda, operador, derecha)
        return izquierda

    def termino(self):
        token = self.obtener_token_actual()
        if token[0] == "IDENTIFIER":
            return NodoIdentificador(self.coincidir("IDENTIFIER"))
        elif token[0] == "NUMBER":
            return NodoNumero(int(self.coincidir("NUMBER")))
        else:
            raise SyntaxError(f"Error de sintaxis: se esperaba un identificador o un número, pero se encontró {token}")

def imprimir_ast(nodo):
    return json.dumps(nodo, default=lambda o: o.__dict__, indent=4)

try:
    parser = Parser(tokens)
    ast = parser.parsear()
    ast_json = imprimir_ast(ast)
    with open("ast.json", "w") as archivo:
        archivo.write(ast_json)
    print("AST generado y guardado en ast.json")
except SyntaxError as e:
    print(e)
