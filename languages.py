# languages.py
# ISO 639-1 language codes
# Please note that for Chinese, the code 'ZH' is used, which is a macro language 
# encompassing Mandarin, Cantonese, and other dialects. For Norwegian, the code 'NO' is used, 
# which does not distinguish between Bokmål and Nynorsk.

import platform
import subprocess

EN_LANGUAGE_DICT = {
    'English': 'EN-US',
    'German': 'DE',
    'French': 'FR',
    'Spanish': 'ES',
    'Bulgarian': 'BG',
    'Chinese': 'ZH',
    'Czech': 'CS',
    'Danish': 'DA',
    'Dutch': 'NL',
    'Estonian': 'ET',
    'Finnish': 'FI',
    'Greek': 'EL',
    'Hungarian': 'HU',
    'Indonesian': 'ID',
    'Italian': 'IT',
    'Japanese': 'JA',
    'Korean': 'KO',
    'Latvian': 'LV',
    'Lithuanian': 'LT',
    'Norwegian': 'NO',
    'Polish': 'PL',
    'Portuguese': 'PT',
    'Romanian': 'RO',
    'Russian': 'RU',
    'Slovak': 'SK',
    'Slovenian': 'SL',
    'Swedish': 'SV',
    'Turkish': 'TR',
    'Ukrainian': 'UK'
}    

DE_LANGUAGE_DICT = {
    'Englisch': 'EN-US',
    'Deutsch': 'DE',
    'Französisch': 'FR',
    'Spanisch': 'ES',
    'Bulgarisch': 'BG',
    'Chinesisch': 'ZH',
    'Tschechisch': 'CS',
    'Dänisch': 'DA',
    'Niederländisch': 'NL',
    'Estnisch': 'ET',
    'Finnisch': 'FI',
    'Griechisch': 'EL',
    'Ungarisch': 'HU',
    'Indonesisch': 'ID',
    'Italienisch': 'IT',
    'Japanisch': 'JA',
    'Koreanisch': 'KO',
    'Lettisch': 'LV',
    'Litauisch': 'LT',
    'Norwegisch': 'NO',
    'Polnisch': 'PL',
    'Portugiesisch': 'PT',
    'Rumänisch': 'RO',
    'Russisch': 'RU',
    'Slowakisch': 'SK',
    'Slowenisch': 'SL',
    'Schwedisch': 'SV',
    'Türkisch': 'TR',
    'Ukrainisch': 'UK'
}

FR_LANGUAGE_DICT = {
    'Anglais': 'EN-US',
    'Allemand': 'DE',
    'Français': 'FR',
    'Espagnol': 'ES',
    'Bulgare': 'BG',
    'Chinois': 'ZH',
    'Tchèque': 'CS',
    'Danois': 'DA',
    'Néerlandais': 'NL',
    'Estonien': 'ET',
    'Finnois': 'FI',
    'Grec': 'EL',
    'Hongrois': 'HU',
    'Indonésien': 'ID',
    'Italien': 'IT',
    'Japonais': 'JA',
    'Coréen': 'KO',
    'Letton': 'LV',
    'Lituanien': 'LT',
    'Norvégien': 'NO',
    'Polonais': 'PL',
    'Portugais': 'PT',
    'Roumain': 'RO',
    'Russe': 'RU',
    'Slovaque': 'SK',
    'Slovène': 'SL',
    'Suédois': 'SV',
    'Turc': 'TR',
    'Ukrainien': 'UK'
}

IT_LANGUAGE_DICT = {
    'Inglese': 'EN-US',
    'Tedesco': 'DE',
    'Francese': 'FR',
    'Spagnolo': 'ES',
    'Bulgaro': 'BG',
    'Cinese': 'ZH',
    'Ceco': 'CS',
    'Danese': 'DA',
    'Olandese': 'NL',
    'Estone': 'ET',
    'Finlandese': 'FI',
    'Greco': 'EL',
    'Ungherese': 'HU',
    'Indonesiano': 'ID',
    'Italiano': 'IT',
    'Giapponese': 'JA',
    'Coreano': 'KO',
    'Lettone': 'LV',
    'Lituano': 'LT',
    'Norvegese': 'NO',
    'Polacco': 'PL',
    'Portoghese': 'PT',
    'Rumeno': 'RO',
    'Russo': 'RU',
    'Slovacco': 'SK',
    'Sloveno': 'SL',
    'Svedese': 'SV',
    'Turco': 'TR',
    'Ucraino': 'UK'
}

ES_LANGUAGE_DICT = {
    'Inglés': 'EN-US',
    'Alemán': 'DE',
    'Francés': 'FR',
    'Español': 'ES',
    'Búlgaro': 'BG',
    'Chino': 'ZH',
    'Checo': 'CS',
    'Danés': 'DA',
    'Holandés': 'NL',
    'Estonio': 'ET',
    'Finlandés': 'FI',
    'Griego': 'EL',
    'Húngaro': 'HU',
    'Indonesio': 'ID',
    'Italiano': 'IT',
    'Japonés': 'JA',
    'Coreano': 'KO',
    'Letón': 'LV',
    'Lituano': 'LT',
    'Noruego': 'NO',
    'Polaco': 'PL',
    'Portugués': 'PT',
    'Rumano': 'RO',
    'Ruso': 'RU',
    'Eslovaco': 'SK',
    'Esloveno': 'SL',
    'Sueco': 'SV',
    'Turco': 'TR',
    'Ucraniano': 'UK'
}

UK_LANGUAGE_DICT = {
    'Англійська': 'EN-US',
    'Німецька': 'DE',
    'Французька': 'FR',
    'Іспанська': 'ES',
    'Болгарська': 'BG',
    'Китайська': 'ZH',
    'Чеська': 'CS',
    'Данська': 'DA',
    'Голландська': 'NL',
    'Естонська': 'ET',
    'Фінська': 'FI',
    'Грецька': 'EL',
    'Угорська': 'HU',
    'Індонезійська': 'ID',
    'Італійська': 'IT',
    'Японська': 'JA',
    'Корейська': 'KO',
    'Латвійська': 'LV',
    'Литовська': 'LT',
    'Норвезька': 'NO',
    'Польська': 'PL',
    'Португальська': 'PT',
    'Румунська': 'RO',
    'Російська': 'RU',
    'Словацька': 'SK',
    'Словенська': 'SL',
    'Шведська': 'SV',
    'Турецька': 'TR',
    'Українська': 'UK'
}

RU_LANGUAGE_DICT = {
    'Английский': 'EN-US',
    'Немецкий': 'DE',
    'Французский': 'FR',
    'Испанский': 'ES',
    'Болгарский': 'BG',
    'Китайский': 'ZH',
    'Чешский': 'CS',
    'Датский': 'DA',
    'Голландский': 'NL',
    'Эстонский': 'ET',
    'Финский': 'FI',
    'Греческий': 'EL',
    'Венгерский': 'HU',
    'Индонезийский': 'ID',
    'Итальянский': 'IT',
    'Японский': 'JA',
    'Корейский': 'KO',
    'Латвийский': 'LV',
    'Литовский': 'LT',
    'Норвежский': 'NO',
    'Польский': 'PL',
    'Португальский': 'PT',
    'Румынский': 'RO',
    'Русский': 'RU',
    'Словацкий': 'SK',
    'Словенский': 'SL',
    'Шведский': 'SV',
    'Турецкий': 'TR',
    'Украинский': 'UK'
}


# Get the system language macOS
def get_macos_system_language():
    try:
        # Execute the command and decode the output
        output = subprocess.check_output(
            "defaults read -g AppleLanguages", shell=True
        ).decode('utf-8')

        # Parsing the output to get the first language
        # The output is typically in the format: ('en', 'de', ...)
        # We strip the unwanted characters and split by comma
        languages = output.strip('()\n ').split(', ')
        first_language = languages[0].strip('"')

        return first_language
    except subprocess.SubprocessError as e:
        #print(f"Error: {e}")
        return None

# Get the system language Linux
def get_linux_system_language():
    try:
        lang = subprocess.check_output(
            "echo $LANG", shell=True
        ).strip().decode('utf-8')
        return lang.split('.')[0]  # Removes encoding part
    except subprocess.SubprocessError:
        return None

def get_system_language():
    os_name = platform.system()

    if os_name == 'Darwin':
        return get_macos_system_language() or 'en'
    elif os_name == 'Linux':
        return get_linux_system_language() or 'en'
    else:
        return 'en'  # Default for other OSes

def get_language_dict(language_code):
    
    language_dict_map = {
        'EN': EN_LANGUAGE_DICT,
        'DE': DE_LANGUAGE_DICT,
        'FR': FR_LANGUAGE_DICT,
        'IT': IT_LANGUAGE_DICT,
        'ES': ES_LANGUAGE_DICT,
        'UK': UK_LANGUAGE_DICT,
        'RU': RU_LANGUAGE_DICT,
        # Add more mappings as needed
    }
    return language_dict_map.get(language_code.upper(), EN_LANGUAGE_DICT)  # Default to English

def map_system_language_to_application_language(system_language):
    # Default to 'en' if system_language is None or empty
    if not system_language:
        return 'en', 'English'

    # Split the language code by '-' or '_' based on which one is present
    if '-' in system_language:
        language_code = system_language.split('-')[0]
       # print("language_code :", language_code)
    elif '_' in system_language:
        language_code = system_language.split('_')[0]
    else:
        language_code = system_language

    language_code = language_code.lower()
    
    # Mapping from language code to language name
    language_map = {
        'en': 'English',
        'de': 'German',
        'fr': 'French',
        # ... more mappings
    }

    # Get the full language name, default to 'English' if not found
    full_language_name = language_map.get(language_code, 'English')
    return language_code, full_language_name


