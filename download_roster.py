#!/usr/bin/env python3

import argparse
import csv
import getpass
import re
import requests
import sys

# probably bad to hardcode this, but hopefully the format shouldn't change
all_columns = [
    'Net ID',
    'UIN',
    'Gender',
    'Last Name',
    'First Name',
    'Email Address',
    'Credit',
    'Level',
    'Year',
    'Subject',
    'Number',
    'Section',
    'CRN',
    'Degree Name',
    'Major 1 Name',
    'College',
    'Program Code',
    'Program Name',
    'FERPA',
]

epilog = '''Examples:

./download_roster.py your-NetID 233 AYA AYA.csv
    Download the roster for 233 section AYA to file AYA.csv. The columns
    included by default are suitable for the section.html script

./download_roster.py your-NetID 233 AYC,AYD roster.csv -c "Net ID"
    Download the roster for 233 sections AYC and AYD to file roster.csv
    and only include the Net ID column

./download_roster.py your-NetID 233 AYB AYB.csv -s "Last Name,First Name"
    Download the roster for 233 section AYB to AYB.csv, sorting by the
    Last Name and then the First Name columns'''

parser = argparse.ArgumentParser(description='CS roster download script',
        epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('netid', help='Your NetID')
parser.add_argument('course', help='The course number (e.g. 233)')
parser.add_argument('sections', help='A comma-separated list of sections to fetch\n(e.g. AYD,AYH)')
parser.add_argument('output', help='Output file name')
parser.add_argument('-c', '--columns',
        help='A comma-separated list of columns to include.\n' \
             'Defaults to "Net ID,Last Name,First Name".\n' \
             'Valid columns are:\n    ' + '\n    '.join(all_columns),
        default='Net ID,Last Name,First Name')
parser.add_argument('-d', '--header', action='store_true', help='Include CSV header row')
parser.add_argument('-s', '--sort',
        help='A comma-separated list of columns to sort on.\n' \
             'Defaults to the first specified column')
args = parser.parse_args()

columns = args.columns.split(',')
invalid_columns = set(columns) - set(all_columns)
if invalid_columns:
    error = 'Invalid columns {} specified\n'.format(','.join(invalid_columns))
    sys.stderr.write(error)
    sys.exit(2)

sort_columns = (args.sort and args.sort.split(',')) or [columns[0]]
invalid_sort_columns = set(sort_columns) - set(columns)
if invalid_sort_columns:
    error = 'Sort columns {} not in specified columns\n'.format(','.join(invalid_sort_columns))
    sys.stderr.write(error)
    sys.exit(2)

password = getpass.getpass('Enter your AD password: ')
session = requests.session()

login_url = 'https://my.cs.illinois.edu/login.asp'
login_data = {
        'netid': args.netid,
        'password': password,
        'action': 'Sign in',
}
login_response = session.post(login_url, data=login_data, allow_redirects=False)
if not login_response.is_redirect:
    sys.stderr.write('Login failed\n')
    sys.exit(1)

roster_url = 'https://my.cs.illinois.edu/classtools/viewroster.asp'
roster_params = { 'subj': 'cs', 'num': args.course, 'sec': '' }
roster_page = session.get(roster_url, params=roster_params, allow_redirects=False)

sections = args.sections.split(',')
crns = []
for section in sections:
    section_re = r'<input type="checkbox" name="CRN_TERM" value="(\d+\|\d+\|{0})"'.format(section)
    course_checkbox = re.search(section_re, roster_page.text)
    if course_checkbox is None:
        sys.stderr.write('Could not find section {}\n'.format(section))
        sys.exit(1)
    crns.append(course_checkbox.group(1))

roster_data = { 'CRN_TERM': crns, 'cross_list': '1', 'step': 'view', 'style': 'Export to Excel' }
roster = session.post(roster_url, data=roster_data, allow_redirects=False).text

# FIXME: hackery instead of proper parsing
students = []
in_tbody = False
column = 0
student = {}
for line in roster.split('\r\n'):
    if line.startswith('<tbody>'):
        in_tbody = True
        continue

    if line.startswith('</tbody>'):
        in_tbody = False
        continue

    if not in_tbody:
        continue

    if line.startswith('<tr>'):
        column = 0
        continue

    if column < len(all_columns):
        # to exclude the <td > and </td> surrounding the column
        student[all_columns[column]] = line[5:-5]

    if column == len(all_columns): # when you hit the </tr>
        students.append(student)
        student = {}

    column += 1

students.sort(key=lambda student: [student[column] for column in sort_columns])
roster_path = args.output
with open(roster_path, 'w') as roster_file:
    writer = csv.writer(roster_file)
    if args.header:
        writer.writerow(columns)

    rows = [[student[column] for column in columns] for student in students]
    writer.writerows(rows)
