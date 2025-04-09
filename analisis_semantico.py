from analizador import *
#------------------------- Análisis semántico -------------------------


class AnalizadorSemantico:
    def __init__(self):
        self.tabla_simbolos = TablaSimbolos()
    
    def analizar(self, nodo):
        if isinstance(nodo, NodoAsignacion):
            # Obtener el nombre real de la variable (no la tupla completa)
            nombre_var = nodo.nombre[1] if isinstance(nodo.nombre, tuple) else nodo.nombre
            
            # Registrar la variable si es una declaración y no existe
            if nombre_var not in self.tabla_simbolos.variables:
                self.tabla_simbolos.declarar_variable(nombre_var, 'int')  # Suponiendo tipo 'int' por defecto
            
            # Analizar la expresión de la asignación
            self.analizar(nodo.expresion)
            
        elif isinstance(nodo, NodoIdentificador):
            # Extraer el nombre real del identificador
            nombre_var = nodo.nombre[1] if isinstance(nodo.nombre, tuple) else nodo.nombre
            return self.tabla_simbolos.obtener_tipo_variable(nombre_var)
            
        elif isinstance(nodo, NodoNumero):
            return 'int'
            
        elif isinstance(nodo, NodoOperacion):
            tipo_izquierda = self.analizar(nodo.izquierda)
            tipo_derecha = self.analizar(nodo.derecha)
            if tipo_izquierda != tipo_derecha:
                raise Exception(f'Error semántico: tipos incompatibles {tipo_izquierda} y {tipo_derecha}')
            return tipo_izquierda # Retorna el tipo de la operación
            
        elif isinstance(nodo, NodoFuncion):
            # Registrar la función en la tabla de símbolos
            nombre_funcion = nodo.nombre[1] if isinstance(nodo.nombre, tuple) else nodo.nombre
            tipo_retorno = nodo.tipo_retorno[1] if isinstance(nodo.tipo_retorno, tuple) else nodo.tipo_retorno
            
            # Lista para almacenar los tipos de parámetros
            parametros_info = []
            
            # Registrar los parámetros de la función en la tabla de símbolos
            for parametro in nodo.parametros:
                nombre_param = parametro.nombre[1] if isinstance(parametro.nombre, tuple) else parametro.nombre
                tipo_param = parametro.tipo[1] if isinstance(parametro.tipo, tuple) else parametro.tipo
                
                self.tabla_simbolos.declarar_variable(nombre_param, tipo_param)
                parametros_info.append((nombre_param, tipo_param))
            
            # Registrar la función con su tipo de retorno y parámetros
            self.tabla_simbolos.declarar_funcion(nombre_funcion, tipo_retorno, parametros_info)
            
            # Analizar el cuerpo de la función
            for instruccion in nodo.cuerpo:
                self.analizar(instruccion)
                
        elif isinstance(nodo, NodoLlamadaFuncion):
            nombre_funcion = nodo.nombre[1] if isinstance(nodo.nombre, tuple) else nodo.nombre
            tipo_retorno, parametros = self.tabla_simbolos.obtener_funcion(nombre_funcion)
            
            if len(nodo.argumentos) != len(parametros):
                raise Exception(f'Error: La funcion {nombre_funcion} espera {len(parametros)} argumentos, pero se le pasaron {len(nodo.argumentos)}')
            
            # Verificar tipos de argumentos
            for i, arg in enumerate(nodo.argumentos):
                tipo_arg = self.analizar(arg)
                nombre_param, tipo_param = parametros[i]
                if tipo_arg != tipo_param:
                    raise Exception(f'Error: El argumento {i+1} de la función {nombre_funcion} debe ser de tipo {tipo_param}, pero se pasó {tipo_arg}')
            
            return tipo_retorno
            
        elif isinstance(nodo, NodoPrograma):
            for funcion in nodo.funciones:
                self.analizar(funcion)
            # No es necesario retornar algo para el nodo programa


class TablaSimbolos:
    def __init__(self):
        self.variables = {}  # Diccionario para almacenar variables {nombre: tipo}
        self.funciones = {}  # Diccionario para almacenar funciones {nombre: (tipo_retorno,[parametros])}

    def declarar_variable(self, nombre, tipo):
        if nombre in self.variables:
            raise Exception(f'Error: la variable {nombre} ya está declarada')
        self.variables[nombre] = tipo

    def obtener_tipo_variable(self, nombre):
        if nombre not in self.variables:
            raise Exception(f'Error: la variable {nombre} no está declarada')
        return self.variables[nombre]
    
    def declarar_funcion(self, nombre, tipo_retorno, parametros):
        if nombre in self.funciones:
            raise Exception(f'Error: la función {nombre} ya está declarada')
        self.funciones[nombre] = (tipo_retorno, parametros)

    def obtener_funcion(self, nombre):
        if nombre not in self.funciones:
            raise Exception(f'Error: la función {nombre} no está declarada')
        return self.funciones[nombre]