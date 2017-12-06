from ipywidgets.widgets import Dropdown, Text, Button, HBox, VBox
from IPython.display import display, clear_output
import pandas as pd

from FileTransformer.app import TheTranformer

def get_clicked(b):
    clear_output() #resets output every time you click the button
    csv_to_dataframe = pd.read_csv(FILE_PATH.value)
    transform_app = TheTranformer(csv_to_dataframe, FUNCTION.value)
    output = transform_app.main()
    output.to_csv(FILE_PATH.value.replace('.csv', '_transformed.csv'), sep=',')
    print('Transformed! Please verify the output')

FILE_PATH = Text(placeholder='Path to file or directory')
TRANSFORM_BUTTON = Button(description="Transform!", button_style="primary")
FUNCTION = Dropdown(description="Select a File Type", options=['Hobos', 'FMD', 'DisplayCases'])
TRANSFORM_BUTTON.on_click(get_clicked)
FILE_PATH.layout.width = '75%'
display(FILE_PATH, FUNCTION)
display(TRANSFORM_BUTTON)
