import codecs
with codecs.open('c:\\Users\\Asus\\Desktop\\antigravity\\backend\\available_models.txt', 'r', 'utf-16le') as f:
    content = f.read()
with open('c:\\Users\\Asus\\Desktop\\antigravity\\backend\\available_models_utf8.txt', 'w', encoding='utf-8') as f:
    f.write(content)
print("Converted to UTF-8")
