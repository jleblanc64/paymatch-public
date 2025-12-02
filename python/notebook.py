from python.pm_sarl import *
from python.popup import *
from python.utils_excel import *
from python.utils_button import *
from python.fuzzy import *

from datetime import datetime
from ipydatagrid import DataGrid, TextRenderer, VegaExpr
import pandas as pd
import string
from collections import defaultdict
from IPython.display import HTML, display
import ipywidgets as widgets
import uuid

bank_customer_key = "Beguenstigter/Zahlungspflichtiger"
bank_amount_key = "Betrag"
bank_date_key = "Buchungstag"

def run():
    # make "Month:" description red + bold
    display(HTML("""<style>
            .widget-label {
                font-size: 20px !important;
                font-weight: bold !important;
                color: red !important;
            }
            </style>"""))

    # paths where excel files will be downloaded
    pm_excel = f"/tmp/{str(uuid.uuid4())}"
    pm_sarl_excel = f"/tmp/{str(uuid.uuid4())}"
    bank_excel = f"/tmp/{str(uuid.uuid4())}"
    generated_excel_path = f"/tmp/{str(uuid.uuid4())}"

    upload_button("A.xlsx", pm_excel)
    display(HTML("</br></br>"))
    upload_button("B.xlsx", pm_sarl_excel)
    display(HTML("</br></br>"))
    upload_button("C.xlsx", bank_excel)
    display(HTML("</br></br>"))

    month_dropdown = widgets.Dropdown(
        options=[(datetime(2000, m, 1).strftime('%B'), m) for m in range(1, 13)],
        value=1,
        description='Month:',
    )
    display(month_dropdown)
    display(HTML("</br></br>"))
    create_interactive_popup()
    display(HTML("</br></br>"))

    run_button = widgets.Button(
        description=" Run",
        button_style='danger',
        tooltip='Click to run function',
        icon='play'
    )

    notebook_output = widgets.Output()
    def on_run_button_click(_):
        notebook_output.clear_output()
        with notebook_output:
            try:
                compute(
                    pm_excel,
                    pm_sarl_excel,
                    bank_excel,
                    generated_excel_path,
                    month_dropdown.value
                )
            except:
                error_label = widgets.HTML(
                    "<span style='color:red; font-size:20px; font-weight:bold;'>Error. Please upload the 3 proper excels</span>"
                )
                display(error_label)

    run_button.on_click(on_run_button_click)
    display(run_button)
    display(HTML("</br></br>"))
    display(notebook_output)


def css(out):
    with out:
        display(HTML("""
            <style>
            .lm-Widget.widget-label {
                font-size: 40px !important;
                font-weight: bold !important;
                color: #222 !important;
            }
            </style>
        """))

def compute_column_widths(df, pixel_per_char=6, pixel_per_char_hdr=8, padding=2):
    column_widths = {}
    for col in df.columns:
        col_name_len = len(str(col))
        try:
            if pd.api.types.is_numeric_dtype(df[col]):
                max_cell_len = df[col].apply(lambda x: len(f"{x:.2f}")).max() + 1
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                max_cell_len = len(str(df[col].iloc[0]))
            else:
                max_cell_len = df[col].astype(str).map(len).max()
        except Exception:
            max_cell_len = col_name_len

        if col_name_len > max_cell_len:
            width = (col_name_len + padding) * pixel_per_char_hdr
        else:
            width = (max_cell_len + padding) * pixel_per_char

        column_widths[col] = width

    return column_widths

def compute(pm_excel, pm_sarl_excel, bank_excel, generated_excel_path, selected_month):
    bank_df = pd.read_excel(bank_excel)
    pm_df = pd.read_excel(pm_excel, header=None)
    pm_sarl_df = pd.read_excel(pm_sarl_excel)

    bank_rows = [
        row for row in bank_df.to_dict(orient='records')
        if (parse_date(row[bank_date_key]).month == selected_month
            and to_float(row[bank_amount_key]) > 0
            and pd.notna(row[bank_customer_key]))
    ]
    bank_names_unique = unique_sorted([row[bank_customer_key] for row in bank_rows])

    pm_df.columns = list(string.ascii_uppercase[:pm_df.shape[1]])
    valid_rows = pm_df['A'].notna() & pm_df['E'].notna()
    filtered_df = pm_df[valid_rows]
    pm_name_to_parking = dict(zip(filtered_df['A'], filtered_df['E']))
    pm_names = pm_df["A"].dropna().tolist()
    result = match_strings(pm_names, bank_names_unique)

    # display pm_names_not_matched
    pm_names_not_matched = unique_sorted([a for a, (b, _) in result.items() if not b])

    # do PM Sarl
    pm_sarl_to_sum = locataire_to_sum(pm_sarl_df)
    pm_sarl_names = list(pm_sarl_to_sum.keys())
    result_sarl = match_strings(pm_sarl_names, pm_names)
    pm_name_to_pm_sarl_names = defaultdict(list)
    for a, (b, _) in result_sarl.items():
        if b:
            pm_name_to_pm_sarl_names[b].append(a)

    pm_sarl_names_not_matched = unique_sorted([a for a, (b, _) in result_sarl.items() if not b])
    pm_names = pm_names + pm_sarl_names_not_matched

    # match PM Sarl -> Bank
    result_sarl_new = match_strings(pm_sarl_names_not_matched, bank_names_unique)

    # init pm_sarl_names_not_matched
    pm_sarl_names_not_matched = unique_sorted([a for a, (b, _) in result_sarl_new.items() if not b])
    pm_names_not_matched.extend(pm_sarl_names_not_matched)
    save_list_to_s3("values1.json", pm_names_not_matched)

    # match Bank -> PM
    result = match_strings(bank_names_unique, pm_names)

    # init bank_names_not_matched
    bank_names_not_matched = unique_sorted([a for a, (b, _) in result.items() if not b])
    save_list_to_s3("values2.json", bank_names_not_matched)

    # add manual mappings to result + remove them from not matched
    for pm, bank in load_mappings_s3():
        if bank in bank_names_unique and pm in pm_names:
            pm_names_not_matched.remove(pm)
            bank_names_not_matched.remove(bank)
            result[bank] = (pm, 100.0)

    # display pm_sarl_names_not_matched
    display(HTML('<p style="color:red;">Excel A, names not matched:</p>'))
    print(pm_names_not_matched)
    print()

    # display bank_names_not_matched
    display(HTML('<p style="color:red;">Excel C, names not matched:</p>'))
    print(bank_names_not_matched)
    print()

    # group Bank by PM
    bank_to_pm = {a: b for a, (b, score) in result.items() if b}
    grouped_by_pm_name = defaultdict(list)
    for row in bank_rows:
        bank_name = row[bank_customer_key]
        pm_name = bank_to_pm.get(bank_name)
        if pm_name:
            grouped_by_pm_name[pm_name].append(row)
    row_red_flags = export_pm_amounts_to_excel(pm_names, grouped_by_pm_name, bank_customer_key, bank_amount_key,
                                               generated_excel_path, pm_name_to_parking, pm_name_to_pm_sarl_names, pm_sarl_to_sum)
    display(HTML('<p style="color:red;">Computed amounts sums:</p>'))
    display(create_download_button(generated_excel_path))
    display(HTML('''
    <style>
    .lm-ScrollBar-thumb {
        background-color: red !important;
    }
    .lm-ScrollBar-track {
        background-color: #f0f0f0 !important;
    }
    </style>
    '''))
    df = pd.read_excel(generated_excel_path)
    df = df.fillna("")

    js_array = str(row_red_flags).lower()
    renderer = TextRenderer(
        background_color=VegaExpr(f"{js_array}[cell.row] ? 'pink' : 'white'")
    )

    column_widths = compute_column_widths(df)

    grid = DataGrid(
        df,
        selection_mode="cell",
        default_renderer=renderer,
        column_widths=column_widths
    )
    grid.layout.height = '400px'
    grid.layout.width = '100%'
    display(grid)

    # test stats
    red_percent = (sum(row_red_flags) / len(pm_names) * 100.0)
    return red_percent