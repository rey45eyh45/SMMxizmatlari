# -*- coding: utf-8 -*-
import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Eng yaxshi xizmatlar handlerini topib o'chirish
pattern = r'@router\.message\(F\.text == ".*?Eng yaxshi xizmatlar"\)\nasync def best_services_menu\(message: Message\):.*?reply_markup=best_services_inline\(\)\)'
content = re.sub(pattern, '', content, flags=re.DOTALL)

# Bo'sh qatorlarni tozalash
content = re.sub(r'\n{4,}', '\n\n\n', content)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('OK - best_services_menu olib tashlandi')
