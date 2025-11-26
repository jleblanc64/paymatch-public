import os

import boto3

from python import popup
from python.notebook import compute

popup.s3 = boto3.Session(profile_name='charles-perso').client('s3')
project = os.getcwd()
generated_excel_path = f"{project}/excels/paymatch.xlsx"

#
pm_excel = f"{project}/excels/A.xlsx"
pm_sarl_excel = f"{project}/excels/B.xlsx"
bank_excel = f"{project}/excels/C.xlsx"
selected_month = 1

red_percent = compute(pm_excel, pm_sarl_excel, bank_excel, generated_excel_path, selected_month)
assert red_percent < 30