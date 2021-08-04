from datetime import date, timedelta
today = date.today()
wochentage = [
    "Montag", "Dienstag", "Mittwoch",
    "Donnerstag", "Freitag", "Samstag", "Sonntag"
]
d = date(2021, 7, 26)
print("KW", d.isocalendar()[1])
for i in range(0, 7):
    print(d.strftime("%Y%m%d"), wochentage[d.weekday()])
    d += timedelta(days=1)
