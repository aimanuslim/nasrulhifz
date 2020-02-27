from nasrulhifz.models import QuranMeta, SurahMeta, User, Hifz, WordIndex

u = User.objects.get(username='aimanuslim@gmail.com')

if u is None:

    u = User(username='aimanuslim@gmail')
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