import re
from requests import get as gt
from os import listdir
import json
from functools import lru_cache

@lru_cache(maxsize=32)
def get_elements(lower_bound:int = 0,upper_bound: int = 100,raw: bool = False):

    #check if bounds are correct and if not correct them
    if upper_bound<lower_bound:
        temp = upper_bound
        upper_bound = lower_bound
        lower_bound = temp
    if upper_bound>118:
        upper_bound=118
    if lower_bound<0:
        lower_bound=0
        
    
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
@lru_cache(maxsize=32)
def molar_mass(formula: str) -> float:
    parsed_formula = parse_chemical_formula(formula)
    molar = 0.0
    data = get_elements(raw=True)
    element_to_mass = {element['symbol']: element['atomic_mass'] for element in data['elements']}
    for element, count in parsed_formula.items():
        molar += float(element_to_mass[element]) * count
    return molar
@lru_cache(maxsize=32)
def parse_chemical_formula(formula:str,error_finding: bool = True) -> dict:
    #delete all spaces cuz they don`t have meaning in them and can make function do wrong outputs
    formula = formula.replace(" ","")
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


@lru_cache(maxsize=32)
def check_equasion(eq:str) -> bool:
    #taking in mind that eq should have this pattern "a + b => c + d" or "a=>b+c+d+e"
    first,second = eq.split("=>")
    def count_half(hf:str) -> dict:
        res = {}
        hf = hf.split("+")
        for l in hf:
            for k,v in parse_chemical_formula(l).items():
                if k in res:
                    res[k] += v
                else:
                    res[k] = v
        return res
    if count_half(first)==count_half(second):
        return True
    return False



