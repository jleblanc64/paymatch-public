from IPython.core.display import Javascript
from IPython.core.display_functions import clear_output, display
from ipydatagrid import DataGrid
import pandas as pd

def check_javascript():
    clear_output()
    start_marker = "a_" + "rteveighuer"
    end_marker = "e_" + "rteveighuer2"

    display(start_marker)
    grid = DataGrid(pd.DataFrame({"0": [0]}), layout={"height": "10px"})
    display(grid)
    display(end_marker)

    js_code = f"""
(() => {{
    const err = ["Loading widget...", "Error displaying widget: model not found", "Click to show javascript error"];
    
    const html = document.body.innerHTML;
    const startMarker = "{start_marker[0]}" + "{start_marker[1:]}";
    const endMarker = "{end_marker[0]}" + "{end_marker[1:]}";
    const startIdx = html.indexOf(startMarker);
        if (startIdx === -1) {{
        return;
    }}
    const endIdx = html.indexOf(endMarker, startIdx + startMarker.length);
        if (endIdx === -1) {{
        return;
    }}
    const extractedText = html.substring(startIdx + startMarker.length, endIdx);
    
    var isJsError = err.some(e => extractedText.includes(e));
    if (isJsError){{
        alert('Browser will be refreshed to fully load Jupyter widgets');
        window.location.reload();
    }}
}})();
"""
    
    display(Javascript(js_code))
    clear_output()