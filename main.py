import re

texto = """
def cuadrado(x) { return x * x; }
print(cuadrado(4) + sqrt(16));
"""

# Definir patrones de tokens
token_patron = {
    "KEYWORD": r'\b(if|else|while|for|return|def|print|sqrt|pow)\b',
    "IDENTIFIER": r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',
    "NUMBER": r'\b\d+(\.\d+)?\b',  # Soporta enteros y decimales
    "OPERATOR": r'[+\-*/=<>]',  # Operadores básicos
    "DELIMITER": r'[(),;{}]',  # Paréntesis, llaves, punto y coma
    "WHITESPACE": r'\s+'  # Espacios en blanco
}

def tokenize(text):
    patron_general = "|".join(f"(?P<{token}>{patron})" for token, patron in token_patron.items())
    patron_regex = re.compile(patron_general)
    tokens_encontrados = [ (m.lastgroup, m.group()) for m in patron_regex.finditer(text) if m.lastgroup != "WHITESPACE"]
    return tokens_encontrados

tokens = tokenize(texto)

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
            return token_actual
        else:
            raise SyntaxError(f'Error: se esperaba {tipo_esperado}, encontrado: {token_actual}')

    def parsear(self):
        while self.obtener_token_actual():
            self.instruccion()

    def instruccion(self):
        token_actual = self.obtener_token_actual()
        if not token_actual:
            return
        
        if token_actual[0] == 'KEYWORD':
            if token_actual[1] == 'print':
                self.imprimir()
            elif token_actual[1] == 'if':
                self.condicional()
            elif token_actual[1] == 'while':
                self.bucle()
            elif token_actual[1] == 'for':
                self.bucle_for()
            elif token_actual[1] == 'def':
                self.definir_funcion()
            else:
                raise SyntaxError(f'Palabra clave desconocida: {token_actual}')
        elif token_actual[0] == 'IDENTIFIER':
            self.asignacion_o_llamada()
        else:
            raise SyntaxError(f'Instrucción inválida: {token_actual}')

    def imprimir(self):
        self.coincidir('KEYWORD')
        self.coincidir('DELIMITER')  # (
        self.expresion()
        self.coincidir('DELIMITER')  # )
        self.coincidir('DELIMITER')  # ;

    def asignacion_o_llamada(self):
        self.coincidir('IDENTIFIER')
        if self.obtener_token_actual() and self.obtener_token_actual()[1] == '(':
            self.llamada_funcion()
        else:
            self.coincidir('OPERATOR')
            self.expresion()
            self.coincidir('DELIMITER')
    
    def definir_funcion(self):
        self.coincidir('KEYWORD')  # def
        self.coincidir('IDENTIFIER')
        self.coincidir('DELIMITER')  # (
        self.parametros()
        self.coincidir('DELIMITER')  # )
        self.coincidir('DELIMITER')  # {
        self.cuerpo()
        self.coincidir('DELIMITER')  # }
    
    def parametros(self):
        if self.obtener_token_actual() and self.obtener_token_actual()[0] == 'IDENTIFIER':
            self.coincidir('IDENTIFIER')
            while self.obtener_token_actual() and self.obtener_token_actual()[1] == ',':
                self.coincidir('DELIMITER')
                self.coincidir('IDENTIFIER')
    
    def llamada_funcion(self):
        self.coincidir('DELIMITER')  # (
        if self.obtener_token_actual() and self.obtener_token_actual()[0] in ['IDENTIFIER', 'NUMBER']:
            self.expresion()
            while self.obtener_token_actual() and self.obtener_token_actual()[1] == ',':
                self.coincidir('DELIMITER')
                self.expresion()
        self.coincidir('DELIMITER')  # )
    
    def cuerpo(self):
        while self.obtener_token_actual() and self.obtener_token_actual()[1] != '}':
            self.instruccion()

    def condicional(self):
        self.coincidir('KEYWORD')  # if
        self.coincidir('DELIMITER')  # (
        self.expresion()
        self.coincidir('DELIMITER')  # )
        self.instruccion_o_bloque()
        if self.obtener_token_actual() and self.obtener_token_actual()[1] == 'else':
            self.coincidir('KEYWORD')
            self.instruccion_o_bloque()
    
    def bucle(self):
        self.coincidir('KEYWORD')  # while
        self.coincidir('DELIMITER')  # (
        self.expresion()
        self.coincidir('DELIMITER')  # )
        self.instruccion_o_bloque()
    
    def bucle_for(self):
        self.coincidir('KEYWORD')  # for
        self.coincidir('DELIMITER')  # (
        self.asignacion()
        self.expresion()
        self.coincidir('DELIMITER')
        self.asignacion()
        self.coincidir('DELIMITER')  # )
        self.instruccion_o_bloque()
    
    def instruccion_o_bloque(self):
        if self.obtener_token_actual() and self.obtener_token_actual()[1] == '{':
            self.coincidir('DELIMITER')
            self.cuerpo()
            self.coincidir('DELIMITER')
        else:
            self.instruccion()

    def expresion(self):
        self.termino()
        while self.obtener_token_actual() and self.obtener_token_actual()[1] in ['+', '-']:
            self.coincidir('OPERATOR')
            self.termino()

    def termino(self):
        self.factor()
        while self.obtener_token_actual() and self.obtener_token_actual()[1] in ['*', '/']:
            self.coincidir('OPERATOR')
            self.factor()
    
    def factor(self):
        token_actual = self.obtener_token_actual()
        if token_actual[0] in ['NUMBER', 'IDENTIFIER']:
            self.coincidir(token_actual[0])
            if self.obtener_token_actual() and self.obtener_token_actual()[1] == '(':
                self.llamada_funcion()
        elif token_actual[1] == '(':
            self.coincidir('DELIMITER')
            self.expresion()
            self.coincidir('DELIMITER')
        else:
            raise SyntaxError(f'Factor no válido: {token_actual}')

# Prueba
try:
    print('Iniciando análisis sintáctico...')
    parser = Parser(tokens)
    parser.parsear()
    print('Análisis exitoso!')
except SyntaxError as e:
    print(e)
