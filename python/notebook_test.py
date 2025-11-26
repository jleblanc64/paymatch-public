from python import popup
from python.notebook import compute
from python.utils import find_project_root

popup.s3 = None
excel_folder = f"{find_project_root()}/excels/"

pm_excel = f"{excel_folder}A.xlsx"
pm_sarl_excel = f"{excel_folder}B.xlsx"
bank_excel = f"{excel_folder}C.xlsx"
generated_excel_path = f"{excel_folder}paymatch.xlsx"
selected_month = 1

red_percent = compute(pm_excel, pm_sarl_excel, bank_excel, generated_excel_path, selected_month)
assert red_percent < 30