from ._anvil_designer import Form1Template
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import plotly.graph_objects as go
import time
from datetime import datetime
# from random import randint

class Form1(Form1Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

     #-----------------------------------------------------------------------------------------------------------
        #Variables drop down menus:

        t_begin = time.time()
        
        self.avg_power = ['20', '30', '40', '60', '75', '100', '125', '135', '150', '175', '200']
        self.dd_avg_power.items = self.avg_power #dd for drop down menue
        self.dd_avg_power.selected_value = '30' #Default value in drop down menue
        # print(f'Average power\n{self.avg_power}\n')
        
        self.run_time = [ str(item) for item in range(1, 24+1) ]
        self.dd_run_time.items = self.run_time
        self.dd_run_time.selected_value = '8' #Default value
        # print(f'Run time\n{self.run_time}\n')
        
        self.days_year = [ str(item) for item in range(1, 365+1)]
        self.dd_days_year.items = self.days_year
        self.dd_days_year.selected_value = '250' #Default value
        # print(f'Days of the year operating\n{self.days_year}\n')
        
        
        self.solar_irrad = ['1.5', '2.6', '3', '4', '5.45', '6']
        self.dd_solar_irrad.items = self.solar_irrad
        self.dd_solar_irrad.selected_value = '5.45' #Default value
        # Solar radiation can be categorized into four classes: levels less than 2.6 kWh/m2 
        # are classified as low solar radiation while solar irradiance between 2.6-3 kWh/m2 
        # is moderate solar radiation; irradiance of between 3-4 kWh/m2 is high solar radiation
        # and irradiance higher than 4 kWh/m2 is very high radiation.
        # print(f'Average solar irradiation\n{self.solar_irrad}\n')
        
        self.wind_speed = [str(item) for item in range(2, 15+1)]
        self.dd_wind_speed.items = self.wind_speed
        self.dd_wind_speed.selected_value = '5' #Default value
        # print(f'Average wind speed\n{self.wind_speed}\n')
        
        self.fuel_cost = [str(1 + (item/10)) for item in range(0, 11) ]
        self.dd_fuel_cost.items = self.fuel_cost
        self.dd_fuel_cost.selected_value = '1.0' #Default value
        # print(f'Average fuel cost\n{self.fuel_cost}\n')
        
        self.elect_grid_cost = [str(round((3 + (item/10))/10, 2)) for item in range(4, 70)]
        self.dd_elect_grid_cost.items = self.elect_grid_cost
        self.dd_elect_grid_cost.selected_value = '0.34' #Default value
        # print(f'Electric grid cost\n{self.elect_grid_cost}\n')

        self.energy_inflation = [ str(item) for item in range(10, 101, 10)]
        self.dd_energy_inflation.items = self.energy_inflation
        self.dd_energy_inflation.selected_value = '30' #Default value
        # print(f'Energy inflation\n{self.energy_inflation}\n')

        t_end = time.time()
        print(f'Build drop down list values in {t_end-t_begin} seconds')
        
       
        #-----------------------------------------------------------------------------------------------------------
        #Delete previous run
        # anvil.server.call('delete_cumulative_costs')
        


    def button_run_click(self, **event_args):
        
        """This method is called when the button is clicked"""

        #-----------------------------------------------------------------------------------------------------------
        #Get user id
        self.user_id = anvil.server.call('get_uuid')
        print(f'User id is {self.user_id}')
        
        #-----------------------------------------------------------------------------------------------------------
        #Upload inputs to server:

        self.session_time = datetime.now()

        t_begin_total = time.time()

        t_begin = time.time()

        anvil.server.call('get_inputs',
                          self.dd_avg_power.selected_value,
                          self.dd_run_time.selected_value,
                          self.dd_days_year.selected_value,
                          self.dd_solar_irrad.selected_value,
                          self.dd_wind_speed.selected_value,
                          self.dd_elect_grid_cost.selected_value,
                          self.dd_energy_inflation.selected_value,
                          self.dd_fuel_cost.selected_value,
                          self.user_id
                         )


        t_end = time.time()
        print(f'Done uploading inputs to server in {t_end-t_begin} seconds')
        #-----------------------------------------------------------------------------------------------------------
        #Runcalculations server:
        t_begin = time.time()
        
        inputs ={}

        inputs["avg_pwr"] = self.dd_avg_power.selected_value
        inputs["run_time"] = self.dd_run_time.selected_value
        inputs["days_op_per_year"] = self.dd_days_year.selected_value
        inputs["avg_solar_irr"] = self.dd_solar_irrad.selected_value
        inputs["avg_wind_speed"] = self.dd_wind_speed.selected_value
        inputs["cost_electric"] = self.dd_elect_grid_cost.selected_value
        inputs["energy_inflation"] = self.dd_energy_inflation.selected_value
        inputs["cost_fuel"] = self.dd_fuel_cost.selected_value

        self.fig1 = anvil.server.call('run_calcs', inputs)

        open_form('Form2')

        t_end = time.time()
        print(f'Done doing calculations in server in {t_end-t_begin} seconds')

        t_end_total = time.time()

        print(f"Total run time {t_end_total-t_begin_total} seconds")






























































    

    def dd_avg_power_change(self, **event_args):
        """This method is called when an item is selected"""
        pass

    def dd_days_year_change(self, **event_args):
        """This method is called when an item is selected"""
        pass

    def dd_run_time_change(self, **event_args):
        """This method is called when an item is selected"""
        pass

    def dd_solar_irrad_change(self, **event_args):
        """This method is called when an item is selected"""
        pass

    def dd_wind_speed_change(self, **event_args):
        """This method is called when an item is selected"""
        pass

    def dd_elect_grid_cost_change(self, **event_args):
        """This method is called when an item is selected"""
        pass

    def dd_fuel_cost_change(self, **event_args):
        """This method is called when an item is selected"""
        pass

    def dd_energy_inflation_change(self, **event_args):
        """This method is called when an item is selected"""
        pass








































    


