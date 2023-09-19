from ._anvil_designer import Form2Template
from anvil import *
import plotly.graph_objects as go
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..Form1 import Form1

class Form2(Form2Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.plot_1.figure = Form1.fig1
        self.plot_2.figure = Form1.fig2
        self.plot_3.figure = Form1.fig3
        self.plot_4.figure = Form1.fig4
       

    def button_1_click(self, **event_args):
        """This method is called when the button is clicked"""
        # anvil.server.call('delete_inputs_tmp')
        open_form('Form1')

    