#! python
from enum import Enum
import re
from time import sleep
import urllib.request
import argparse
import smtplib
import datetime
from getpass import getpass

class Stages(Enum):
    START = "ADMCONC"
    CONTINUE = "ADMAPOUR"
    ADMIN = "ADMISSIBILITE"
    FINAL = "ADMISSION"

    def __str__(self):
        if self == self.START:
            return "Admis(e) à Concourir"
        elif self == self.CONTINUE:
            return "Admis(e) à Poursuivre"
        elif self == self.ADMIN:
            return "Admis(e)"
        elif self == self.FINAL:
            return "Admission finale"

SECTIONS = list(range(1, 42)) + list(range(50, 56))

def get_candidates_official(name_to_check, current_status=None):
    url = (
        "http://intersection.dsi.cnrs.fr/intersection/resultats-cc-fr.do?campagne=101"
        "&section={section:02d}&grade=223&phase={adm:s}&conc={section:02d}/{conc:02d}"
    )
    if current_status is None:
        print("Checking all sections:")
        current_status = {}
        for section in SECTIONS:
            print(section, end=", ", flush=True)
            for conc in range(1, 6):
                with urllib.request.urlopen(url.format(section=section, adm=Stages.START.value, conc=conc)) as fp:
                    mybytes = fp.read()
                if name_to_check.lower() in str(mybytes).lower():
                    current_status[(section, conc)] = []
    
    # current_status = {}
    new_status = {}
    for section, conc in current_status:
        # went_through = []
        new_status[(section, conc)] = []
        for stage in Stages:
            with urllib.request.urlopen(url.format(section=section, adm=stage.value, conc=conc)) as fp:
                mybytes = fp.read()
            if not "pas encore" in str(mybytes):
                    new_status[(section, conc)].append((stage, name_to_check.lower() in str(mybytes).lower()))
    
    return new_status
    
def print_results(current_status):
    str_out = "Your current status is:\n"
    for section, status in current_status.items():
        str_out += f"\tSection {section[0]:02d}/{section[1]:02d}, status: " + ("" if status[-1][1] else "PAS ") + str(status[-1][0]) + "\n"
    return str_out

if __name__ == '__main__':
    description="""Are you selected yet?
    (from http://intersection.dsi.cnrs.fr)"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-s', '--sections', nargs='*', default=[],
                        type=int, help='Inform the sections to check')
    parser.add_argument('-n', '--name', nargs='+', default=['guignard', 'léo'],
                        type=str, help='Name to look for')
    parser.add_argument('-y', '--year', default=2023,
                        type=int, help='Inform the years to check')
    parser.add_argument('-t', '--smtp', default='smtp.lis-lab.fr',
                        type=str, help='smtp (default LIS)')
    parser.add_argument('-p', '--port', default=587,
                        type=int, help='port for email (default 587)')
    parser.add_argument('-u', '--username', default='leo.guignard',
                        type=str, help='password for email (default leo.guignard)')
    parser.add_argument('-r', '--recipient', default='leo.guignard@gmail.com',
                        type=str, help='email where to send the news (default leo.guignard@gmail.com)')

    args = parser.parse_args()
    args.name = ' '.join(args.name)
    print("Running with the following parameters:")
    print(f"\tName: {args.name}, Year: {args.year}\n")
    
    smtp_server = args.smtp
    smtp_port = args.port
    smtp_username = args.username

    print(f"Please input the {args.smtp} account password for the user {smtp_username}.")
    smtp_password = getpass("Password: ")
    using_name = args.name
    current_status = get_candidates_official(args.name)
    print(print_results(current_status))
    sender = f"{smtp_username}@{smtp_server.removeprefix('smtp.')}"
    recipient = args.recipient
    subject = '[CNRS] Am I selected??'
    start_time = datetime.datetime.now()
    while True:
        body = "Have I made it to the next round?\n"
        new_status = get_candidates_official(using_name, current_status)
        if new_status != current_status:
            new_status_str = print_results(new_status)
            body += new_status_str
            message = f'Subject: {subject}\n\n{body}'
            smtp_connection = smtplib.SMTP(smtp_server, smtp_port)
            smtp_connection.starttls()  # enable TLS encryption
            try:
                smtp_connection.login(smtp_username, smtp_password)
                smtp_connection.sendmail(sender, recipient, message)
                smtp_connection.quit()
            except Exception as e:
                print(f'Could not send the email: {e}')
        else:
            current_time = datetime.datetime.now()
            print(f"\nOn the {current_time.strftime('%d/%m at %H:%M:%S')} ... still no update")
        if 4<(datetime.datetime.now() - start_time).seconds/60/60:
            if 7<datetime.datetime.now().hour<20:
                message = f'Subject: [CNRS] Still no news\n\nYep, nothing ...'
                smtp_connection = smtplib.SMTP(smtp_server, smtp_port)
                smtp_connection.starttls()  # enable TLS encryption
                try:
                    smtp_connection.login(smtp_username, smtp_password)
                    smtp_connection.sendmail(sender, recipient, message)
                    smtp_connection.quit()
                except Exception as e:
                    print(f'Could not send the email: {e}')
                start_time = datetime.datetime.now()
        sleep(10*60)