# Premium bo'limdagi emojilarni tuzatish
content = open('main.py', 'r', encoding='utf-8').read()

# Buzilgan emojilarni tuzatish
replacements = [
    ('?? Tarif:', '📦 Tarif:'),
    ('?? So\'rov:', '🆔 So\'rov:'),
    ('?? Premium', '👆 Premium'),
    ('??', '📌'),
]

for old, new in replacements:
    content = content.replace(old, new)

open('main.py', 'w', encoding='utf-8').write(content)
print('Emojilar tuzatildi!')
