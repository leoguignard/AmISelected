#! python
import re
from time import sleep
import urllib.request
import argparse
from pathlib import Path

def get_candidates(name_to_check, year, sections_to_check = []):
    result_page = "https://www.coudert.name/concours_cnrs_{year}.html"
    check_num = re.compile('\([0-9]+\)')
    table = {}
    try:
        with urllib.request.urlopen(result_page.format(year=year)) as fp:
            mybytes = fp.read()
            html_doc = mybytes.decode("utf8")
    except Exception as e:
        print(f'The year {year} was probably not found.')
        print(f'Page requested: {result_page.format(year=year)}')
        print(f'The raise error: {e}')
        exit
    find_name = re.compile(name_to_check, re.IGNORECASE)

    find_section = re.compile('[0-9][0-9]/[0-9][0-9]')
    if sections_to_check == []:
        sections_to_check = [int(find_section.search(line).group().split('/')[0]) for line in html_doc.splitlines() if find_section.search(line)]
        sections_to_check = set(sections_to_check)

    for section in sections_to_check:
        start = html_doc.find(f'Concours {section:02d}')
        found = True
        while (not '(CRCN)' in html_doc[start:].splitlines()[0] and
                found):
            found = html_doc[start+1:].find(f'Concours {section:02d}')!=-1
            start = html_doc[start+1:].find(f'Concours {section:02d}')+start+1
        if not found:
            continue
        stop = html_doc[start:].find('<h2>') + start
        lines = html_doc[start:stop].splitlines()
        curr_status = 'Admis'
        if 'details' in lines[1]:
            l_num = 2
            curr_status = 'Concourir'
        else:
            l_num = 3
        while l_num<len(lines)-2:
            l = lines[l_num]
            l_num += 1
            if curr_status == 'Admis':
                if 'table' in l:
                    curr_status = 'Concourir'
                    l_num += 1
                else:
                    start = l.find('<td>')+4
                    stop = l.find('</td>')
                    name = l[start:stop]
                    name = name[:check_num.search(name).start()].strip()
                    info = table.setdefault(name, {})
                    info[section] = curr_status
            elif curr_status == 'Concourir':
                if 'details' in l:
                    curr_status = 'Poursuivre'
                    l_num += 1
                else:
                    name = l[:-5]
                    if not table.get(name, {}).get(section):
                        info = table.setdefault(name, {})
                        info[section] = curr_status
            else:
                name = l[:-5]
                if not table.get(name, {}).get(section):
                    info = table.setdefault(name, {})
                    info[section] = curr_status
                elif table[name][section] != 'Admis':
                    table[name][section] = curr_status
    candidate_status = [table[v] for v in table if find_name.search(v)][0]
    current_status = {}
    for name, sections in table.items():
        for section, status in sections.items():
            if section in candidate_status:
                current_status.setdefault(section, set()).add(status)
    return candidate_status, current_status

if __name__ == '__main__':
    description="""Are you selected yet?
    (from https://www.coudert.name/concours_cnrs_{year}.html)"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-s', '--sections', nargs='*', default=[],
                        type=int, help='Inform the sections to check')
    parser.add_argument('-n', '--name', nargs=1, default='guignard léo',
                        type=str, help='Name to look for')
    parser.add_argument('-y', '--year', nargs=1, default=2023,
                        type=int, help='Inform the years to check')
    parser.add_argument('-m', '--email', default='',
                        type=str, help='email to inform')

    args = parser.parse_args()

    candidate_init_status, init_status = get_candidates(args.name, args.year, args.sections)
    sections_applied_to = init_status.keys()
    print("Running with the following parameters:")
    print(f"\tName: {args.name}, Year: {args.year}")
    print("I found you as follow:")
    for section, status in candidate_init_status.items():
        print(f"\tSection {section}, status: {status}")

    while True:
        candidate_status, current_status = get_candidates(args.name, args.year, sections_applied_to)
        for section, status in current_status.items():
            if init_status[section] != status:
                print("Update has happened")
                if candidate_init_status[section] == candidate_status[section]:
                    print("You haven't made it to the next round :(")
                else:
                    print(f"You are now listed as {candidate_status[section]}")
            else:
                print("still no update")
        sleep(10*60)






















