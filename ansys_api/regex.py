import re


# Variables=["Young's Modulus"],
# Values=[["200000000000 [Pa]"]])
PATTERN_FOR_VATIABLES = re.compile(r'Variables=\["(.*?)"\],\s*Values=\[\["(.*?)"\]\]')

# Parameter = parameter1,
# Expression = "15 [MPa]")
PATTERN_FOR_PARAMS = re.compile(r'Parameter=(\w+),\s*Expression="(.*?)"')

# Saving calculation result path regex
PATTERN_FOR_RESULT_CSV_FILE = re.compile(r'FilePath="([^"]+\.csv)"')

# Project .wbpj file path regex
PATTERN_WBPJ = re.compile(r'(Open|Save)\(FilePath="([^"]+\.wbpj)"')
