import csv

with open('cumulative.csv', encoding="utf8") as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
    main_data = sorted(reader, key=lambda x: x['kepoi_name'], reverse=True)


def looking_for_same(data):
    # looking for same pos
    # using the worldwide
    # coords
    new_database = []
    for key in data[0].keys():
        main_obj = new_database[0][key]
        for elm in data:
            if main_obj[key] + 0.12235235345 <= elm[key] <= main_obj[key] - 0.53463467:
                new_database += [elm]

    return new_database


new_database = looking_for_same(main_data)

for elm in new_database:
    if elm["koi_score"] != 1.0:
        print(elm)
