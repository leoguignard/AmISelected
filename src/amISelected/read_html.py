#! python
import re
from time import sleep
import urllib.request
import argparse
import smtplib
import datetime
from getpass import getpass


def get_candidates(name_to_check, year, sections_to_check=[], first_run=False):
    result_page = "https://www.coudert.name/concours_cnrs_{year}.html"
    check_num = re.compile("\([0-9]+\)")
    table = {}
    try:
        with urllib.request.urlopen(result_page.format(year=year)) as fp:
            mybytes = fp.read()
            html_doc = mybytes.decode("utf8")
    except Exception as e:
        print(f"The year {year} was probably not found.")
        print(f"Page requested: {result_page.format(year=year)}")
        print(f"The raise error: {e}")
        exit
    find_name = re.compile(name_to_check, re.IGNORECASE)

    find_section = re.compile("[0-9][0-9]/[0-9][0-9]")
    if sections_to_check == []:
        sections_to_check = [
            int(find_section.search(line).group().split("/")[0])
            for line in html_doc.splitlines()
            if find_section.search(line)
        ]
        sections_to_check = set(sections_to_check)

    for section in sections_to_check:
        start = html_doc.find(f"Concours {section:02d}")
        found = True
        while "(CRCN)" not in html_doc[start:].splitlines()[0] and found:
            found = html_doc[start + 1 :].find(f"Concours {section:02d}") != -1
            start = (
                html_doc[start + 1 :].find(f"Concours {section:02d}")
                + start
                + 1
            )
        if not found:
            continue
        stop = html_doc[start:].find("<h2>") + start
        lines = html_doc[start:stop].splitlines()
        if len(lines) < 2:
            continue
        curr_status = "Admis"
        if "details" in lines[1]:
            l_num = 2
            curr_status = "Concourir"
        else:
            l_num = 3
        while l_num < len(lines) - 2:
            line = lines[l_num]
            l_num += 1
            if "Admis" in curr_status:
                if "table" in line:
                    curr_status = "Concourir"
                    l_num += 1
                else:
                    start = line.find("<td>") + 4
                    stop = line.find("</td>")
                    name = line[start:stop]
                    rank_search = check_num.search(name)
                    name = name[: rank_search.start()].strip()
                    info = table.setdefault(name, {})
                    info[section] = " ".join(
                        [curr_status, rank_search.group()]
                    )
            elif curr_status == "Concourir":
                if "details" in line:
                    curr_status = "Poursuivre"
                    l_num += 1
                else:
                    name = line[:-5]
                    if not table.get(name, {}).get(section):
                        info = table.setdefault(name, {})
                        info[section] = curr_status
            else:
                name = line[:-5]
                if not table.get(name, {}).get(section):
                    info = table.setdefault(name, {})
                    info[section] = curr_status
                elif "Admis" not in table[name][section]:
                    table[name][section] = curr_status
    matching_name = [v for v in table if find_name.search(v)]
    if len(matching_name) == 0:
        print(f"\n!!{name_to_check} not found, please check the spelling !!\n")
        quit()
    elif 1 < len(matching_name):
        print(f"\n!! Found multiple possibilities for {name_to_check}:\n")
        for n in matching_name:
            print(f"\t{n}")
        print(f"We will use {matching_name[0]} !!\n")
    elif first_run:
        print(f"We found the name {matching_name[0]}")
        print("We hope they are the one you were looking for\n")
    n = matching_name[0]
    candidate_status = table[n]
    current_status = {}
    for name, sections in table.items():
        for section, status in sections.items():
            if section in candidate_status:
                current_status.setdefault(section, set()).add(status)
    return candidate_status, current_status, n


def run_whole():
    description = """Are you selected yet?
    (from https://www.coudert.name/concours_cnrs_{year}.html)"""
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "-s",
        "--sections",
        nargs="*",
        default=[],
        type=int,
        help="Inform the sections to check",
    )
    parser.add_argument(
        "-n",
        "--name",
        nargs="+",
        default=["guignard", "léo"],
        type=str,
        help="Name to look for",
    )
    parser.add_argument(
        "-y",
        "--year",
        default=2024,
        type=int,
        help="Inform the years to check",
    )
    parser.add_argument(
        "-t",
        "--smtp",
        default="smtp.gmail.com",
        type=str,
        help="smtp (default smtp.gmail.com)",
    )
    parser.add_argument(
        "-p",
        "--port",
        default=465,
        type=int,
        help="port for email (default 465)",
    )
    parser.add_argument(
        "-u",
        "--username",
        default="leo.guignard@gmail.com",
        type=str,
        help="username for email (default leo.guignard@gmail.com)",
    )
    parser.add_argument(
        "-r",
        "--recipient",
        default="leo.guignard@gmail.com",
        type=str,
        help="email where to send the news (default leo.guignard@gmail.com)",
    )
    parser.add_argument(
        "-w",
        "--wait",
        default=10,
        type=float,
        help="Waiting time between each check (default 10 min)",
    )

    args = parser.parse_args()
    args.name = " ".join(args.name)
    print("Running with the following parameters:")
    print(f"\tName: {args.name}, Year: {args.year}\n")

    smtp_server = args.smtp
    smtp_port = args.port
    smtp_username = args.username
    wait = args.wait

    print(
        f"Please input the {args.smtp} account password for the user {smtp_username}."
    )
    smtp_password = getpass("Password: ")
    candidate_init_status, init_status, using_name = get_candidates(
        args.name, args.year, args.sections, first_run=True
    )
    sections_applied_to = init_status.keys()
    print("I found you appearing in the following sections:")
    for section, status in candidate_init_status.items():
        print(f"\tSection {section}, status: {status}")
    sender = f"{smtp_username}@{smtp_server.removeprefix('smtp.')}"
    recipient = args.recipient
    subject = "[CNRS] Am I selected??"

    message = "Subject: [CNRS] Starting the check\n\nJust making sure everything's working properly ..."
    server = smtplib.SMTP_SSL("smtp.gmail.com", smtp_port)
    try:
        server.login(smtp_username, smtp_password)
        server.sendmail(sender, recipient, message)
    except Exception as e:
        print(f"Could not send the email: {e}")

    start_time = datetime.datetime.now()
    while True:
        body = "Have I made it to the next round?\n"
        candidate_status, current_status, _ = get_candidates(
            using_name, args.year, sections_applied_to
        )
        for section, status in current_status.items():
            if init_status[section] != status:
                print("Update has happened")
                if candidate_init_status[section] == candidate_status[section]:
                    print("You haven't made it to the next round :(")
                    body += f"\tNope (section {section})\n"
                else:
                    print(f"You are now listed as {candidate_status[section]}")
                    body += f"\tYes, You are now listed as {candidate_status[section]} in section {section}"
        candidate_init_status = candidate_status
        init_status = current_status
        if body != "Have I made it to the next round?\n":
            message = f"Subject: {subject}\n\n{body}"
            server = smtplib.SMTP_SSL("smtp.gmail.com", smtp_port)
            try:
                server.login(smtp_username, smtp_password)
                server.sendmail(sender, recipient, message)
            except Exception as e:
                print(f"Could not send the email: {e}")
        else:
            current_time = datetime.datetime.now()
            print(
                f"\nOn the {current_time.strftime('%d/%m at %H:%M:%S')} ... still no update"
            )
        if 4 < (datetime.datetime.now() - start_time).seconds / 60 / 60:
            if 7 < datetime.datetime.now().hour < 20:
                message = "Subject: [CNRS] Still no news\n\nYep, nothing ..."
                server = smtplib.SMTP_SSL("smtp.gmail.com", smtp_port)
                try:
                    server.login(smtp_username, smtp_password)
                    server.sendmail(sender, recipient, message)
                except Exception as e:
                    print(f"Could not send the email: {e}")
                start_time = datetime.datetime.now()
        sleep(wait * 60)


if __name__ == "__main__":
    run_whole()
