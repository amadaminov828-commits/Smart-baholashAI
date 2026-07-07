def number_to_uzbek_words(n):
    if n == 0:
        return "Nol"
    if not isinstance(n, int):
        n = int(n)
        
    ones = ["", "bir", "ikki", "uch", "to'rt", "besh", "olti", "yetti", "sakkiz", "to'qqiz"]
    tens = ["", "o'n", "yigirma", "o'ttiz", "qirq", "ellik", "oltmish", "yetmish", "sakson", "to'qson"]
    
    def convert_group(num):
        res = []
        h = num // 100
        if h > 0:
            res.append(ones[h] + " yuz")
        t = (num % 100) // 10
        if t > 0:
            res.append(tens[t])
        o = num % 10
        if o > 0:
            res.append(ones[o])
        return " ".join(res).strip()
    
    parts = []
    billions = n // 1000000000
    if billions > 0:
        parts.append(convert_group(billions) + " milliard")
    n %= 1000000000
    
    millions = n // 1000000
    if millions > 0:
        parts.append(convert_group(millions) + " million")
    n %= 1000000
    
    thousands = n // 1000
    if thousands > 0:
        parts.append(convert_group(thousands) + " ming")
    n %= 1000
    
    if n > 0:
        parts.append(convert_group(n))
        
    return " ".join(parts).strip().capitalize()
