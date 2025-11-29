import boto3
import ipyvuetify as v
import ipywidgets as widgets
from IPython.display import display
import logging
import json

# s3 = boto3.client('s3')
s3 = None
bucket = "paymatch"
key = "mappings.json"

def create_interactive_popup():
    # start with empty dropdowns; values will be set on open
    dropdown1 = v.Select(label='A names', items=[], v_model=None, style_='flex:1; margin-right:5px;')
    dropdown2 = v.Select(label='C names', items=[], v_model=None, style_='flex:1; margin-left:5px;')

    # Container for the new rows
    rows_container = v.Container(fluid=True, children=[])

    # Add Row button
    add_row_btn = v.Btn(children=['Add mapping'], color='primary')

    # Dropdowns layout side by side
    dropdowns_layout = v.Layout(
        children=[dropdown1, dropdown2],
        row=True,
        align_items='center',
        justify_content='space-between',
        style_='margin-bottom:10px;'
    )

    # Main popup dialog
    popup = v.Dialog(
        width='500',
        children=[
            v.Card(children=[
                v.CardTitle(children=['Excel A -> Excel C']),
                v.CardText(children=[
                    dropdowns_layout,
                    add_row_btn,
                    rows_container
                ]),
                v.CardActions(children=[v.Btn(children=['Close'], color='red')])
            ])
        ]
    )

    # Reference to the close button
    close_button = popup.children[0].children[2].children[0]

    def on_click_close(widget, event, data):
        popup.v_model = False

    close_button.on_event('click', on_click_close)

    def save_rows_to_s3():
        try:
            data = [row._value for row in rows_container.children]
            body = json.dumps(data).encode("utf-8")
            s3.put_object(Bucket=bucket, Key=key, Body=body)
            logging.info(f"Saved {len(data)} rows to s3://{bucket}/{key}")
        except Exception as e:
            logging.error("Error saving to S3", exc_info=e)

    def load_rows_from_s3(values1, values2):
        rows_container.children = []
        for val1, val2 in load_mappings_s3():
            # skip invalid mappings
            if val1 not in values1 or val2 not in values2:
                continue

            # Recreate row with delete button
            delete_btn = v.Btn(icon=True, children=[v.Icon(children=['mdi-close-circle'])], x_small=True, dense=True)
            new_row = v.Layout(
                children=[v.Chip(children=[f'{val1} -> {val2}']), delete_btn],
                row=True,
                align_items='center',
                justify_content='space-between',
                style_='margin:2px 0;'
            )
            new_row._value = (val1, val2)

            def delete_row_handler(widget, event, data, row=new_row):
                val1, val2 = row._value
                dropdown1.items = sorted(list(dropdown1.items) + [val1])
                dropdown2.items = sorted(list(dropdown2.items) + [val2])
                rows_container.children = [c for c in rows_container.children if c != row]
                save_rows_to_s3()

            delete_btn.on_event('click', delete_row_handler)
            rows_container.children = list(rows_container.children) + [new_row]

            # Remove from dropdowns so they can’t be picked again
            dropdown1.items = [i for i in dropdown1.items if i != val1]
            dropdown2.items = [i for i in dropdown2.items if i != val2]

    # Handler for Add Row button
    def on_add_row_click(widget, event, data):
        if dropdown1.v_model and dropdown2.v_model:
            val1 = dropdown1.v_model
            val2 = dropdown2.v_model

            # Create delete button
            delete_btn = v.Btn(icon=True, children=[v.Icon(children=['mdi-close-circle'])], x_small=True, dense=True)

            # Row layout using v.Layout (prevents scrollbars)
            new_row = v.Layout(
                children=[v.Chip(children=[f'{val1} / {val2}']), delete_btn],
                row=True,
                align_items='center',
                justify_content='space-between',
                style_='margin:2px 0;'
            )

            # Store values on the row for deletion
            new_row._value = (val1, val2)

            # Delete handler closes over new_row
            def delete_row_handler(widget, event, data, row=new_row):
                val1, val2 = row._value
                dropdown1.items = sorted(list(dropdown1.items) + [val1])
                dropdown2.items = sorted(list(dropdown2.items) + [val2])
                rows_container.children = [c for c in rows_container.children if c != row]
                save_rows_to_s3()

            delete_btn.on_event('click', delete_row_handler)

            # Add row
            rows_container.children = list(rows_container.children) + [new_row]

            # Remove selected values
            dropdown1.items = [i for i in dropdown1.items if i != val1]
            dropdown2.items = [i for i in dropdown2.items if i != val2]

            # Reset selections
            dropdown1.v_model = None
            dropdown2.v_model = None

            # Save to S3
            save_rows_to_s3()

    add_row_btn.on_event('click', on_add_row_click)

    # Open popup button
    button = widgets.Button(description="Manual mappings")
    def on_click_open(b):
        values1 = load_values_from_s3("values1.json")
        values2 = load_values_from_s3("values2.json")
        dropdown1.items = values1
        dropdown2.items = values2
        popup.v_model = True
        load_rows_from_s3(values1, values2)

    button.on_click(on_click_open)

    display(button, popup)

def load_mappings_s3():
    try:
        obj = s3.get_object(Bucket=bucket, Key=key)
        return json.loads(obj["Body"].read().decode("utf-8"))
    except:
        return []

mem_cache = {}
def load_values_from_s3(filename):
    try:
        obj = s3.get_object(Bucket=bucket, Key=filename)
        return json.loads(obj["Body"].read().decode("utf-8"))
    except Exception:
        return mem_cache.get(filename, [])

def save_list_to_s3(key: str, values: list[str]):
    try:
        body = json.dumps(values).encode("utf-8")
        s3.put_object(Bucket=bucket, Key=key, Body=body)
        logging.info(f"Saved {len(values)} items to s3://{bucket}/{key}")
    except Exception as e:
        mem_cache[key] = values
        # logging.error(f"Error saving list to S3 at {key}", exc_info=e)
