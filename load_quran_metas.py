from nasrulhifz.models import QuranMeta, SurahMeta, User, Hifz, WordIndex


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
    for i, myrange in enumerate(juz_ranges):
        if myrange.get(surah_number) is not None:
            ayat_limit = myrange.get(surah_number)
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


u = User(username='aimanuslim')
u.set_password('chanayya211')
u.is_staff = True
u.is_superuser = True

u.save()

from numpy.random import randint
for i in range(15):
    sn = randint(114) + 1
    lastayat = SurahMeta.objects.get(surah_number=sn).surah_ayat_max
    an = randint(lastayat) + 1

    found_unique = False
    while not found_unique:
        try:
            htest =Hifz.objects.get(surah_number=sn, ayat_number=an)
            sn = randint(114) + 1
            lastayat = SurahMeta.objects.get(surah_number=sn).surah_ayat_max
            an = randint(lastayat) + 1
        except:
            found_unique = True
    h = Hifz(hafiz=u, surah_number=sn, ayat_number=an)

    h.average_difficulty = 3
    h.save()

    lenayat = len(QuranMeta.objects.get(surah_number=sn, ayat_number=an).ayat_string.split(" "))
    for i in range(lenayat):
        w = WordIndex(index=i, difficulty=randint(3)+1, hifz=h)
        w.save()

    h.save_average_difficulty()
    h.save()









