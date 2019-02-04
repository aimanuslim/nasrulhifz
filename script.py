from nasrulhifz.models import QuranMeta, SurahMeta


with open('quran-uthmani.txt', 'r', encoding='utf8') as f:
    text = f.readlines()

import json
with open('juzs.json', 'r') as f:
    data = json.load(f)
    juz_ranges = data['data']

strings = []
for ayat in text[:6235]:
    ayat = ayat.strip()
    surah_number, ayat_number, string = ayat.split('|')
    for i, range in enumerate(juz_ranges):
        if range.get(surah_number) is not None:
            ayat_limit = range.get(surah_number)
            if int(ayat_number) <= ayat_limit[1] and int(ayat_number) >= ayat_limit[0]:
                qm = QuranMeta(ayat_string=string, surah_number=surah_number, ayat_number=ayat_number, juz_number=i)
                qm.save()
                break


import json
with open('surahs.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    surahmeta = data['data']

for sm in surahmeta:
    osm = SurahMeta(surah_number=sm.get('number'), name_string=sm.get('name'), surah_ayat_max=sm.get('numberOfAyahs'))
    osm.save()







