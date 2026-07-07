TRANSLATIONS = {
    'uz': {
        'title': "AVTOTRANSPORT VOSITASI QIYMATINI BAHOLASH TO'G'RISIDA HISOBOT",
        'analog_table': "Solishtirma tahlil jadvali",
        'indicators': "Ko'rsatkichlar",
        'model': "Transport vositasi rusumi",
        'type': "Turi",
        'body_type': "Kuzov turi",
        'year': "Ishlab chiqarilgan yili",
        'age': "Foydalanilgan muddat (yil)",
        'mileage': "Bosib o'tgan masofasi (km)",
        'color': "Rangi",
        'transmission': "Uzatma quti turi",
        'minor_defects': "Jiddiy bo'lmagan nuqsonlar",
        'location': "Joylashgan manzili",
        'value_type': "Qiymat turi",
        'price': "Qiymati",
        'source': "Foydalanilgan manbaa",
        'physical_wear': "Jismoniy eskirish",
        'adjustment': "Kiritilgan tuzatish",
        'final_value': "Baholash ob'yekti qiymati",
        # ... va barcha boshqa qatorlar uchun tarjimalar
    },
    'kz': {
        'title': "АВТОКӨЛІК ҚҰРАЛЫНЫҢ ҚҰНЫН БАҒАЛАУ ТУРАЛЫ ЕСЕП",
        'analog_table': "Салыстырмалы талдау кестесі",
        'indicators': "Көрсеткіштер",
        'model': "Көлік құралының маркасы",
        'type': "Түрі",
        'body_type': "Шанақ түрі",
        'year': "Шығарылған жылы",
        # ... qozoqcha tarjimalar
    },
    # RU, EN, TJ, KG, TR tillari uchun ham xuddi shunday
}

def get_text(key, lang='uz'):
    return TRANSLATIONS.get(lang.lower(), TRANSLATIONS['uz']).get(key, key)
