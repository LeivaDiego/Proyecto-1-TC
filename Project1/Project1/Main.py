import io
from shuntingYard import ShuntingYard
from syntaxTree import SyntaxTree
from AFNsimulator import thompson_from_tree, State, simulate_afn
from AFDsimulator import convert_to_afd, simulate_afd

converter = ShuntingYard()
tree_maker = SyntaxTree()



with io.open('regex.txt', 'r', encoding='utf-8') as file:
    lines = [line.strip().replace(" ", "") for line in file]

for index, infix in enumerate(lines):
    # Conversion de infix a postfix
    print(f"Original: {infix}")
    postfix = converter.infixToPostfix(infix)
    print(f"Postfix: {postfix}\n")

    # Construccion y visualizacion del arbol sintactico
    root = tree_maker.build_tree(postfix)
    tree_dot = tree_maker.visualize_tree(root)
    tree_dot.render(f'arbol_sintactico_{index+1}', view = True, cleanup=True)

    # Construccion y visualizacion del AFN
    State.state_counter = 0
    afn = thompson_from_tree(root)
    afn.assign_state_numbers()
    afn_dot = afn.visualize_afn()
    afn_dot.render(f'afn_{index+1}', view = True, cleanup=True)
    

    afd = convert_to_afd(afn)
    afd_dot = afd.visualize_afd()
    afd_dot.render(f'afd_{index+1}', view = True, cleanup = True)


    # Evaluacion de la cadena 
    w = input(f"Ingrese una cadena para probrar el AFN:")

    is_accepted_afn = simulate_afn(afn, w)
    is_accepted_afd = simulate_afd(afd, w)

    if is_accepted_afn:
        print(f"La cadena '{w}' es aceptada por el AFN\n")
    else:
        print(f"La cadena '{w}' no es aceptada por el AFN\n")

    if is_accepted_afd:
        print(f"La cadena '{w}' es aceptada por el AFD\n")
    else:
        print(f"La cadena '{w}' no es aceptada por el AFD\n")

    pause = input("Presione enter para continuar")