from ipywidgets.widgets import Dropdown, Text, Button, HBox, VBox
from IPython.display import display, clear_output
import pandas as pd

from FileValidator.app import TheValidator

def get_clicked(b):
    clear_output() #resets output every time you click the button
    csv_to_dataframe = pd.read_csv(FILE_PATH.value)
    validate_app = TheValidator(csv_to_dataframe, FUNCTION.value)
    output = validate_app.main()
    output.to_csv(FILE_PATH.value.replace('.csv', '_validated.csv'), sep=',')
    print('Validated! Please verify the output')

FILE_PATH = Text(placeholder='Path to file')
VALIDATE_BUTTON = Button(description="Validate!", button_style="primary")
FUNCTION = Dropdown(description="Select a File Type", options=['FileType1'])
VALIDATE_BUTTON.on_click(get_clicked)
FILE_PATH.layout.width = '75%'
display(FILE_PATH, FUNCTION)
display(VALIDATE_BUTTON)
