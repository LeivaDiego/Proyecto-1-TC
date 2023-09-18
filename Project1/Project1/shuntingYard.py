# Define la clase Shunting Yard para la conversion de una expresion regular infix a postfix
class ShuntingYard:
    
    # Inicializa la lista de operadores validos
    def __init__(self):
        self.allOperators = ['|', '?', '+', '*', '^']


    # Retorna la precedencia del operador dado, 0 si no se encuentra
    def getPrecedence(self, c):
        
        precedence = {
            '(': 1,
            '|': 2,
            '^': 3,
            '?': 4,
            '*': 4,
            '+': 4,
        }
        return precedence.get(c, 0)


    # Convierte el operador '+' a su forma explicita, es decir, 'a+' pasa a ser 'aa*'
    def plus_operator_convertion(self, regex):

        i = 0
        transformed_exp = ""

        # Bucle que recorre la expresion regular
        while i < len(regex):

            # Si encuentra un '+' verifica el caracter anterior
            if regex[i] == '+':
                # si es un parentesis, busca el parentesis correspondiente y reemplaza por '*'
                if regex[i-1] == ')':
                    for j in range(i-1, -1, -1):
                        if regex[j] == '(':
                            transformed_exp += regex[j:i] + "*"
                          
                else:
                    transformed_exp += regex[i-1] + '*'
            else:
                transformed_exp += regex[i]
            i += 1
        return transformed_exp


    # Convierte la extension de expresion '?' a su forma explicita, es decir, 'a?' a 'a|ε'
    def interrogation_operator_convertion(self, regex):
        
        stack = []
        openParentesis = []
        i = 0

        # Bucle que recorre la expresion regular
        while i < len(regex):
            # Si encuentra '?', verifica el caracter anterior
            if regex[i] == '?':
                # si es un parentesis, busca el parentesis correspondiente 
                if regex[i-1] == ')':
                    for j in range(i-1, -1, -1):
                        if regex[j] == ')':
                            stack.append(regex[j])
                        elif regex[j] == '(':
                            stack.pop()
                            if not stack:
                                openParentesis.append(j + 1)
                                break
                else:
                    openParentesis.append(i - 1)
            i += 1

        transformed_exp = ""
        i = 0

        while i < len(regex):
            if i in openParentesis:
                count = openParentesis.count(i)
                transformed_exp += '(' * count + regex[i]

            elif regex[i] == '?':
                transformed_exp += '|ε)' #  reemplaza por '|ε'

            else:
                transformed_exp += regex[i]

            i += 1

        return transformed_exp


    # Maneja la concatenacion implicita, transformandola en explicita usando ^
    def concatenation_convertion(self, expression):
       
        new_expression = []

        # Bucle que recorre la expresion
        for i in range(len(expression) - 1):
            new_expression.append(expression[i])

            # si encuentra caracteres consecutivos que no sean operadores, agrega '^' entre caracteres
            if (expression[i] not in ['|', '(', '^'] and 
                expression[i+1] not in ['|', ')', '*', '+', '?']
                ):
                new_expression.append('^')

        new_expression.append(expression[-1])

        return ''.join(new_expression)


    # Hace uso de las conversiones para transformar la expresion a su forma explicita antes de hacer shunting yard
    def formatRegEx(self, regex):
        
        regex = self.plus_operator_convertion(regex)
        regex = self.interrogation_operator_convertion(regex)
        regex = self.concatenation_convertion(regex)

        return regex


    # Convierte la expresion infix a formato postfix utilizando el algoritmo de Shunting Yard
    def infixToPostfix(self, regex):
        
        postfix = []
        stack = []
        formattedRegEx = self.formatRegEx(regex)

        for c in formattedRegEx:
            if c == '(':
                stack.append(c)

            elif c == ')':
                while stack and stack[-1] != '(':
                    postfix.append(stack.pop())

                if stack:
                    stack.pop()  

            elif c in self.allOperators:
                while (stack and 
                       self.getPrecedence(stack[-1]) >= self.getPrecedence(c)
                       ):
                    postfix.append(stack.pop())

                stack.append(c)

            else:
                postfix.append(c)

        while stack:
            postfix.append(stack.pop())

        return ''.join(postfix)