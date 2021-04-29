from datetime import date, datetime, timedelta
today = date.today()
wochentage = ["Montag", "Dienstag", "Mittwoch",
              "Donnerstag", "Freitag", "Samstag", "Sonntag"]
d = date(2020, 12, 28)
print("KW", d.isocalendar()[1])
for i in range(0, 7):
	print(d.strftime("%Y%m%d"), wochentage[d.weekday()])
	d += timedelta(days=1)
