import xml.etree.ElementTree as ET
from typing import Dict, Union, Callable, Any

def parse_xml_equations(xml_file: str) -> Dict[str, Union[str, float, int]]:
    """
    Parse equations from an XML file.
    Expected format:
    <equations>
        <equation>
            <name>variable_name</name>
            <value>100</value>  <!-- For constants -->
            <!-- OR -->
            <expression>base_price * tax_rate</expression>  <!-- For expressions -->
        </equation>
    </equations>
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    equations = {}
    for equation in root.findall('equation'):
        name = equation.find('name').text
        value_elem = equation.find('value')
        expr_elem = equation.find('expression')
        
        if value_elem is not None:
            # Try to convert to number if possible
            value = value_elem.text
            try:
                # Try float first
                value = float(value)
                # If it's a whole number, convert to int
                if value.is_integer():
                    value = int(value)
            except ValueError:
                # Keep as string if not a number
                pass
            equations[name] = value
        elif expr_elem is not None:
            equations[name] = expr_elem.text
            
    return equations 