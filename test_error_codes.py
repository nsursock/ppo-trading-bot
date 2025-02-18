from interactions import error_codes_1, error_codes_2
import re

tuple_error_codes = ('0x34f38ee9', '0x34f38ee9') 

error_code = tuple_error_codes[0][2:] if '0x' in tuple_error_codes[0] else tuple_error_codes[0]

print(error_code)

error_message = "Unknown error"
for code_dict in [error_codes_1, error_codes_2]:
    for code, message in code_dict.items():
        if re.fullmatch(code, error_code):
            error_message = message
            break
    if error_message != "Unknown error":
        break

print(error_message)