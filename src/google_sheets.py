from typing import List, Dict

import gspread

gc = gspread.service_account()
spead_sheet = gc.open_by_url(
    'https://docs.google.com/spreadsheets/d/1bfWDcVUSaILHxxYGQiWrGPgwO0htEmPOlyt7yInW2Is/edit#gid=0'
)


def get_traffic_status(city):
    traffic_status = spead_sheet.worksheet("trafficStatus")
    r = traffic_status.get_all_values()
    for inner_city, value in r:
        if inner_city == city:
            return value
    return 0


def get_posters(city, day) -> List[Dict[str, str | int]]:
    out = []
    posters = spead_sheet.worksheet("posters")
    r = posters.get_all_values()
    k = -1
    for i in range(len(r[0]) - 1):
        if r[0][i] == city and r[0][i + 1] == day:
            k = i
            break
    for i in range(1, len(r)):
        out.append({
            'event': r[i][k + 0],
            'price': r[i][k + 1],
            'link': r[i][k + 2],
        })
    return out


if __name__ == '__main__':
    print(get_posters('санкт-петербург', 'завтра'))
