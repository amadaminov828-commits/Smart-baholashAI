import os

search_str = "New SDK"
found = False

for root, dirs, files in os.walk('c:/Users/Asus/Desktop/antigravity/backend'):
    for file in files:
        if file.endswith('.py') or file.endswith('.pyc'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if search_str in content:
                        print(f"FOUND IN: {filepath}")
                        found = True
            except:
                pass

if not found:
    print("NOT FOUND ANYWHERE!")
