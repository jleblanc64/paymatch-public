import ipywidgets as widgets
from IPython.display import display

def upload_button(name, file_name):
    upload_widget = widgets.FileUpload(
        accept='.xlsx',
        multiple=False,
        layout=widgets.Layout(overflow_y='visible')  # Allow vertical expansion
    )

    # Use HTML widget for label with inline font size
    label_widget = widgets.HTML(f"<span style='font-size:20px;'>{name}</span>")

    filename_display = widgets.HTML(
        value="<span style='visibility:hidden;'>Uploaded: placeholder.xlsx</span>"
    )

    upload_box = widgets.VBox([
        label_widget,
        upload_widget,
        filename_display
    ], layout=widgets.Layout(overflow='visible'))  # Avoid clipping scrollbars

    def handle_upload(_):
        if upload_widget.value:
            uploaded_file = upload_widget.value[0]
            content = uploaded_file['content']
            user_filename = uploaded_file['name']

            with open(file_name, "wb") as f:
                f.write(content)

            filename_display.value = f"<span style='color:red;'>Uploaded: {user_filename}</span>"

    upload_widget.observe(handle_upload, names='value')
    display(upload_box)
