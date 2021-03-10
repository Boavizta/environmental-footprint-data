import csv
from datetime import datetime
import locale

output = open('boavizta-data-fr.csv', 'w')
writer = csv.writer(output, delimiter=';')
with open('boavizta-data-us.csv') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        # Convert number format
        row[5] = row[5].replace('.', ',')
        row[6] = row[6].replace('.', ',')
        row[7] = row[7].replace('.', ',')
        row[11] = row[11].replace('.', ',')
        row[12] = row[12].replace('.', ',')
        row[13] = row[13].replace('.', ',')

        # Convert date
        if row[9].count(' ') == 1:
            locale.setlocale(locale.LC_TIME, "en_US.utf8")
            d = datetime.strptime(row[9], '%B %Y')
            locale.setlocale(locale.LC_TIME, "fr_FR.utf8")
            row[9] = d.strftime('%B %Y').capitalize()
        elif row[9].count(' ') == 2:
            locale.setlocale(locale.LC_TIME, "en_US.utf8")
            d = datetime.strptime(row[9], '%B %d, %Y')
            locale.setlocale(locale.LC_TIME, "fr_FR.utf8")
            row[9] = d.strftime('%-d %B %Y')

        # Save
        writer.writerow(row)

output.close()
