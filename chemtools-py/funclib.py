import re
from requests import get as gt
from os import listdir
import json
from functools import lru_cache

@lru_cache(maxsize=32)
def get_elements(lower_bound:int = 0,upper_bound: int = 100,raw: bool = False):
    #download json containig all info and if it`s already downloaded use it
    if not "chem_elements.json" in listdir():
        response = gt("https://raw.githubusercontent.com/Bowserinator/Periodic-Table-JSON/master/PeriodicTableJSON.json")
        #error while accessing
        if response.status_code != 200:
            raise("Error accessing remote json")
        data = response.json()
        #save for later offline uses
        with open("chem_elements.json", 'w') as file:
            json.dump(response.json(), file)
    #so the json exists and just need to be opened
    else:
        data = open("chem_elements.json")
        data = json.load(data)
    #return first [lower_bound-upper_bound] ammount of elemnts, default is 100, can be lowered to inscrease speed
    if raw == False:
        return [element['symbol'] for element in data['elements'] if lower_bound <= element['number'] <= upper_bound]
    else:
        return data



def molar_mass(formula: str) -> float:
    parsed_formula = parse_chemical_formula(formula)
    molar = 0.0
    data = get_elements(raw=True)
    element_to_mass = {element['symbol']: element['atomic_mass'] for element in data['elements']}
    for element, count in parsed_formula.items():
        molar += float(element_to_mass[element]) * count
    return molar

def parse_chemical_formula(formula:str,error_finding: bool = True):
    
    # Step 1: Extract and remove the whole molecule coefficient
    coefficient = 1
    for i, char in enumerate(formula):
        if not char.isdigit():
            coefficient = int(formula[:i] or 1)
            formula = formula[i:]
            break

    # Step 2: Parse the chemical elements.
    element_pattern = re.compile(r"([A-Z][a-z]*)(\d*)|(\()([^)]+)(\))(\d*)")
    # Define dictionary to hold results
    result = {}

    formula_parts = element_pattern.findall(formula)

    for part in formula_parts:
        element, primary_number, _, sub_formula, _, multiplier = part
        if element:
            primary_number = int(primary_number) if primary_number else 1
            primary_number *= coefficient # multiply count by the molecule's coefficient
            result[element] = result.get(element, 0) + primary_number
        else:
            # when the parentheses has a multiplier (like H2O2),
            # the coefficient is multiplied by the multiplier
            sub_coefficient = coefficient * (int(multiplier) if multiplier else 1)
            # Process the sub-formula recursively
            sub_result = parse_chemical_formula(sub_formula)
            for sub_element, sub_value in sub_result.items():
                sub_value *= sub_coefficient
                result[sub_element] = result.get(sub_element, 0) + sub_value

    if error_finding:
        k = get_elements()
        for i, l in result.items():
            if not i in k:
                raise ValueError(f"Error while parsing formula '{formula}': element '{i}' not found in element list")
            
    return result