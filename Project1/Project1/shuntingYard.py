class ShuntingYard:
    
    def __init__(self):
        # Define los operadores
        self.allOperators = ['|', '?', '+', '*', '^']
        self.binaryOperators = ['^', '|']


    def getPrecedence(self, c):
        # Retorna la precedencia del operador dado, 0 si no se encuentra
        precedence = {
            '(': 1,
            '|': 2,
            '^': 3,
            '?': 4,
            '*': 4,
            '+': 4,
        }
        return precedence.get(c, 0)


    def plus_operator_convertion(self, regex):
        # Convierte el operador '+' a su forma explicita, es decir, 'a+' a 'aa*'
        i = 0
        transformed_exp = ""

        while i < len(regex):

            if regex[i] == '+':
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



    def interrogation_operator_convertion(self, regex):
        # Convierte la extension de expresion ? a su forma explicita, es decir, 'a?' a 'a|ε'
        stack = []
        openParentesis = []
        i = 0

        while i < len(regex):
            if regex[i] == '?':
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
                transformed_exp += '|ε)'

            else:
                transformed_exp += regex[i]

            i += 1

        return transformed_exp



    def concatenation_convertion(self, expression):
        # Maneja la concatenacion implicita, transformandola en explicita usando ^
        new_expression = []

        for i in range(len(expression) - 1):
            new_expression.append(expression[i])

            if (expression[i] not in ['|', '(', '^'] and 
                expression[i+1] not in ['|', ')', '*', '+', '?']
                ):
                new_expression.append('^')

        new_expression.append(expression[-1])

        return ''.join(new_expression)



    def formatRegEx(self, regex):
        # Hace uso de las conversiones para transformar la expresion a su forma explicita antes de hacer shunting yard
        regex = self.plus_operator_convertion(regex)
        regex = self.interrogation_operator_convertion(regex)
        regex = self.concatenation_convertion(regex)

        return regex



    def infixToPostfix(self, regex):
        # Convierte la expresion infix a formato postfix
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