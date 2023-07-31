from sympy import Matrix, lcm
import re

def balance_equation(reactants, products):
    
    #completely AI generated and smh works, don`t touch anything here unless you really know what you are doing, cuz i don`t give a fuck what anything does
    element_list = []
    element_matrix = []

    def add_to_matrix(element, index, count, side):
        if index == len(element_matrix):
            element_matrix.append([0]*len(element_list))
        if element not in element_list:
            element_list.append(element)
            for row in element_matrix:
                row.append(0)
        column = element_list.index(element)
        element_matrix[index][column] += count*side

    def find_elements(segment, index, multiplier, side):
        elements_and_numbers = re.split('([A-Z][a-z]?)', segment)
        i = 0
        while i < len(elements_and_numbers) - 1:  # last element always blank
            i += 1
            if len(elements_and_numbers[i]) > 0:
                if elements_and_numbers[i+1].isdigit():
                    count = int(elements_and_numbers[i+1])*multiplier
                    add_to_matrix(elements_and_numbers[i], index, count, side)
                    i += 1
                else:
                    add_to_matrix(elements_and_numbers[i], index, multiplier, side)

    def compound_decipher(compound, index, side):
        segments = re.split('(\([A-Za-z0-9]*\)[0-9]*)', compound)
        for segment in segments:
            if segment.startswith("("):
                segment = re.split('\)([0-9]*)', segment)
                multiplier = int(segment[1])
                segment = segment[0][1:]
            else:
                multiplier = 1
            find_elements(segment, index, multiplier, side)

    for i, reactant in enumerate(reactants):
        compound_decipher(reactant, i, 1)
    for i, product in enumerate(products):
        compound_decipher(product, i+len(reactants), -1)

    # Solve the system
    element_matrix = Matrix(element_matrix).transpose()
    solution = element_matrix.nullspace()[0]

    # Find the least common multiple of the denominators of all the fractions in solution
    multiple = lcm([val.q for val in solution])
    solution = multiple*solution

    # Convert solution to a list of coefficients
    coefficients = solution.tolist()

    # Format the output
    output = " + ".join([f"{coefficients[i][0]}{reactants[i]}" for i in range(len(reactants))])
    output += " => "
    output += " + ".join([f"{coefficients[i+len(reactants)][0]}{products[i]}" for i in range(len(products))])

    return output