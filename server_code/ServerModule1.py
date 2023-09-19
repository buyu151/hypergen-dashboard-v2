import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import uuid


#Get user id for session 
#https://anvil.works/forum/t/how-do-you-define-a-session/606
@anvil.server.callable
def get_uuid():
  if "id" not in anvil.server.session:
    anvil.server.session['id']=str(uuid.uuid4())

  return anvil.server.session['id']

inputs = {}

@anvil.server.callable
def get_inputs(avg_pwr, run_time, days_op_per_year, avg_solar_irr, avg_wind_speed, cost_electric, energy_inflation, cost_fuel, user_id):
    inputs["avg_pwr"] = avg_pwr
    inputs["run_time"] = run_time
    inputs["days_op_per_year"] = days_op_per_year
    inputs["avg_solar_irr"] = avg_solar_irr
    inputs["avg_wind_speed"] = avg_wind_speed
    inputs["cost_electric"] = cost_electric
    inputs["energy_inflation"] = energy_inflation
    inputs["cost_fuel"] = cost_fuel
    inputs["user_id"] = user_id
    print(inputs)

@anvil.server.callable
def reset_inputs():
    inputs.clear()

@anvil.server.callable
def run_calcs(inputs):
    
    avg_power_selected = float(inputs["avg_pwr"])
    run_time_selected = float(inputs["run_time"])
    days_year_selected = float(inputs["days_op_per_year"])
    solar_irrad_selected = float(inputs["avg_solar_irr"])
    wind_speed_selected = float(inputs["avg_wind_speed"])
    fuel_cost_selected = float(inputs["cost_electric"])
    elect_grid_cost_selected = float(inputs["energy_inflation"])
    energy_inflation_selected = float(inputs["cost_fuel"])
    
    
    # print(inputs)
    
    # ----------------------------------------------------------------------------------------------------------------------------------
    # Tabular constants definition
    
    total_power_comsumption = avg_power_selected * run_time_selected * days_year_selected
    
    print(f"Total power calculated {total_power_comsumption} \n")
    
    capital_costs = {}
    generators = ["piston", "MGT", "HMGT", "solar", "wind"]
    cost_factor = {
        "piston": [0.15],
        "MGT": [0.0045],
        "HMGT": [0.0045],
        "solar": [3000],
        "wind": [0.0082]
    }
    
    generator_costs = {
        "generator": ["piston", "MGT", "HMGT", "solar", "wind"],
        "pounds_per_kwh": [300, 500, 600, 2000, 4500]
    }
    
    generator_efficiency = {
        "generator_size_kw": ["20.0", "30.0", "40.0", "60.0", "75.0", "100.0", "125.0", "135.0", "150.0", "175.0", "200.0"],
        "45%_l/h": [7.3, 13.2, 18.2, 21.8, 27.7, 33.6, 41.4, 44.6, 49.6, 57.7, 65.5],
        "35%_l/h": [8, 14.5, 20, 24, 30.5, 37, 45.5, 49, 54.5, 63.5, 72],
        "50%_l/h": [5.46, 11.87, 16.37, 19.64, 24.96, 30.28, 37.23, 40.1, 44.6, 51.96, 58.92],
    }
    
    generator_efficiency_df = pd.DataFrame.from_dict(generator_efficiency).set_index(
        "generator_size_kw"
    )
    generator_cost_df = pd.DataFrame.from_dict(generator_costs).set_index("generator")
    cost_factor_df = pd.DataFrame.from_dict(cost_factor)
    
    # ----------------------------------------------------------------------------------------------------------------------------------
    # Calculations
    
    for item in generators:
        generator_cost_obj = generator_cost_df["pounds_per_kwh"][item]
        capital_costs[item] = {
            "Initial capital cost": generator_cost_obj * avg_power_selected
        }
    
        if item == "solar":
            capital_costs[item]["Yearly maintenance costs"] = cost_factor["solar"][0]
            capital_costs[item]["Yearly fuel costs"] = 0
        else:
            capital_costs[item]["Yearly maintenance costs"] = (
                total_power_comsumption * cost_factor[item][0]
            )
    
        if item == "wind":
            capital_costs[item]["Yearly fuel costs"] = 0
    
        if item not in ["solar", "wind"]:
            if item == "piston":
                efficiency = "45%_l/h"
            elif item == "MGT":
                efficiency = "35%_l/h"
            elif item == "HMGT":
                efficiency = "50%_l/h"
            fuel_data = generator_efficiency_df.loc[str(avg_power_selected)][efficiency]
            # print(f"fuel data: {fuel_data}, for system {item}")
            capital_costs[item]["Yearly fuel costs"] = (
                fuel_data * run_time_selected * days_year_selected * fuel_cost_selected
            )
    
    capital_costs_df = pd.DataFrame.from_dict(capital_costs)
    print(f"Capital costs \n {capital_costs_df} \n")
    
    # -------------------------------------------------------------------------------------------------------------------------------
    # Calculate cumulative costs
    
    years = [i for i in range(0, 11)]
    # print(self.years)
    
    cumulative_cost = {}
    
    for item in generators:
        cumulative_cost[item] = [
            capital_costs[item]["Initial capital cost"]
            + i
            * (
                capital_costs[item]["Yearly maintenance costs"]
                + capital_costs[item]["Yearly fuel costs"]
            )
            for i in years
        ]
        cumulative_cost["grid"] = [ (1 + year) * (total_power_comsumption * elect_grid_cost_selected *
                                      (1 + year * (energy_inflation_selected/100))) for year in years]
        cumulative_cost["year"] = years
    cumulative_cost_df = pd.DataFrame.from_dict(cumulative_cost)
    
    print(f"Cumulative costs \n {cumulative_cost_df} \n")
    # -------------------------------------------------------------------------------------------------------------------------------
    # Calculate cumulative costs   
    
    fig1 = px.line(cumulative_cost_df, x= "year", y= ["piston", "grid", "MGT", "HMGT", "solar", "wind"], text="year", title='Cumulative cost')
    fig1.update_traces(textposition="bottom right")
    
    return fig1
