from ._anvil_designer import Form3Template
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import time

class Form3(Form3Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

    def outlined_button_1_click(self, **event_args):
        """This method is called when the button is clicked"""
        name = self.name_box.text
        email = self.email_box.text
        company = self.company_box.text
        feedback = self.feedback_box.text
        anvil.server.call('add_feedback', name, email,company, feedback)
        Notification("Feedback submitted! Thank you for your interest. We will be in touch shortly.").show()
        self.clear_inputs()
        time.sleep(2) # Sleep for 2 seconds
        open_form('Form1')

    def clear_inputs(self):
        self.name_box.text = ""
        self.email_box.text = ""
        self.company_box.text = ""
        self.feedback_box.text = ""

    def return_button_click(self, **event_args):
        """This method is called when the button is clicked"""
        open_form('Form1')

    
