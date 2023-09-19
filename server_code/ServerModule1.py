import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import uuid
import anvil.http

# ----------------------------------------------------------------------------------------------------------------------------------
#Get user id for session 
#https://anvil.works/forum/t/how-do-you-define-a-session/606
@anvil.server.callable
def get_uuid():
  if "id" not in anvil.server.session:
    anvil.server.session['id']=str(uuid.uuid4())
  return anvil.server.session['id']

# ----------------------------------------------------------------------------------------------------------------------------------
# Tables of constants

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

# ----------------------------------------------------------------------------------------------------------------------------------
# Functions

@anvil.server.callable
def get_inputs(inputs_val):
   
    inputs = inputs_val
    
    row = app_tables.user_data.add_row(avg_pwr=inputs["avg_pwr"],
                                days_op_per_year=inputs["days_op_per_year"],
                                cost_fuel=inputs["cost_fuel"],
                                cost_electric=inputs["cost_electric"],
                                energy_inflation=inputs["energy_inflation"],
                                avg_solar_irr=inputs["avg_solar_irr"],
                                avg_wind_speed=inputs["avg_wind_speed"],
                                run_time=inputs["run_time"],
                                user_id=inputs["user_id"],
                                date_time=inputs["date_time"],
                                country=inputs['country'],
                                user_ip=inputs['user_ip']
                                      )
    
    row = app_tables.inputs_tmp.add_row(avg_pwr=inputs["avg_pwr"],
                            days_op_per_year=inputs["days_op_per_year"],
                            cost_fuel=inputs["cost_fuel"],
                            cost_electric=inputs["cost_electric"],
                            energy_inflation=inputs["energy_inflation"],
                            avg_solar_irr=inputs["avg_solar_irr"],
                            avg_wind_speed=inputs["avg_wind_speed"],
                            run_time=inputs["run_time"]
                                    )
    print(inputs)
    
@anvil.server.callable
def build_dfs(inputs):
    cumulative_cost_df, capital_costs_df_long = run_calcs(inputs, generators, cost_factor, generator_costs, generator_efficiency)
    return cumulative_cost_df, capital_costs_df_long

@anvil.server.callable
def run_calcs(inputs, generators, cost_factor, generator_costs, generator_efficiency):
    
    avg_power_selected = float(inputs["avg_pwr"])
    run_time_selected = float(inputs["run_time"])
    days_year_selected = float(inputs["days_op_per_year"])
    solar_irrad_selected = float(inputs["avg_solar_irr"])
    wind_speed_selected = float(inputs["avg_wind_speed"])
    fuel_cost_selected = float(inputs["cost_electric"])
    elect_grid_cost_selected = float(inputs["energy_inflation"])
    energy_inflation_selected = float(inputs["cost_fuel"])
    
    # ----------------------------------------------------------------------------------------------------------------------------------
    # Tabular constants definition
    
    capital_costs = {}
    total_power_comsumption = avg_power_selected * run_time_selected * days_year_selected
    
    print(f"Total power calculated {total_power_comsumption} \n")
    
    generator_efficiency_df = pd.DataFrame.from_dict(generator_efficiency).set_index("generator_size_kw")
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
    
    capital_costs_df_long = pd.DataFrame()
    capital_costs_df_long["generator"] = generators
    capital_costs_df_long["Yearly fuel costs"] = [capital_costs[item]["Yearly fuel costs"] for item in generators]
    capital_costs_df_long["Yearly maintenance costs"] = [capital_costs[item]["Yearly maintenance costs"] for item in generators]
    capital_costs_df_long["Initial capital cost"] = [capital_costs[item]["Initial capital cost"] for item in generators]

    print(f"Capital costs \n {capital_costs_df} \n")
    print(f"Capital costs long version \n {capital_costs_df_long} \n")
    
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
    return cumulative_cost_df, capital_costs_df_long

# -------------------------------------------------------------------------------------------------------------------------------
# Plots

@anvil.server.callable
def create_plot_cc(cumulative_cost_df):
    fig = px.line(cumulative_cost_df, x= "year", y= ["piston", "grid", "MGT", "HMGT", "solar", "wind"], text="year", title='Cumulative cost')
    fig.update_traces(textposition="bottom right")
    return fig

@anvil.server.callable
def create_plot_ic(df):
    fig = px.bar(df, x="generator", y="Initial capital cost", title="Initial cost")
    # fig.update_traces(textposition="bottom right")
    return fig

@anvil.server.callable
def create_plot_ymc(df):
    fig = px.bar(df, x="generator", y="Yearly maintenance costs", title="Yearly maintenance costs")
    # fig.update_traces(textposition="bottom right")
    return fig

@anvil.server.callable
def create_plot_yfc(df):
    fig = px.bar(df, x="generator", y="Yearly fuel costs", title="Yearly fuel costs")
    # fig.update_traces(textposition="bottom right")
    return fig

@anvil.server.callable
def pressed_button():
    inputs_tmp_search = app_tables.inputs_tmp.search()
    inputs_list = [{'days_op_per_year': r['days_op_per_year'],
               'cost_fuel': r['cost_fuel'],
               'cost_electric': r['cost_electric'],
               'avg_pwr': r['avg_pwr'],
               'energy_inflation': r['energy_inflation'],
               'avg_solar_irr': r['avg_solar_irr'],
               'avg_wind_speed': r['avg_wind_speed'],
               'run_time': r['run_time'],
              }
    for r in inputs_tmp_search]

    inputs = inputs_list[0]
    
    cumulative_cost_df, capital_costs_df_long = build_dfs(inputs)
    fig1 = create_plot_cc(cumulative_cost_df)
    fig2 = create_plot_ic(capital_costs_df_long)
    fig3 = create_plot_ymc(capital_costs_df_long)
    fig4 = create_plot_yfc(capital_costs_df_long)
    
    return fig1, fig2, fig3, fig4

@anvil.server.callable
def delete_inputs_tmp():
    app_tables.inputs_tmp.delete_all_rows()

# https://anvil.works/forum/t/getting-users-ip-address-in-an-app/146/8
# @anvil.server.http_endpoint("/tools/:v")
# def tools(v, **params):
#     if v=="myip":
#         return anvil.server.request.remote_address

# https://anvil.works/docs/server/call-context
# https://anvil.works/forum/t/getting-users-ip-address-in-an-app/146/14
@anvil.server.callable
def get_ip():
    country = anvil.server.context.client.location.country 
    ip_addres = anvil.server.context.client.ip
    return country, ip_addres