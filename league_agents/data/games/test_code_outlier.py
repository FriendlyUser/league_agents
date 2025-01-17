import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score

# Load the dataset
data = pd.read_csv("/content/dashapp_pricing.csv")

# --- Exploratory Data Analysis (EDA) ---
# (EDA code remains the same as in the original article)
# ... (scatter plots, box plots, correlation matrix)


high_demand_percentile = 75
low_demand_percentile = 25

data['demand_multiplier'] = np.where(
    data['Number_of_Products'] > np.percentile(data['Number_of_Products'], high_demand_percentile),
    data['Number_of_Products'] / np.percentile(data['Number_of_Products'], high_demand_percentile),
    data['Number_of_Products'] / np.percentile(data['Number_of_Products'], low_demand_percentile)
)

# Supply multiplier now based on Number_of_Products
high_supply_percentile = 75
low_supply_percentile = 25

data['supply_multiplier'] = np.where(
    data['Number_of_Products'] > np.percentile(data['Number_of_Products'], low_supply_percentile),
    np.percentile(data['Number_of_Products'], high_supply_percentile) / data['Number_of_Products'],
    np.percentile(data['Number_of_Products'], low_supply_percentile) / data['Number_of_Products']
)

demand_threshold_high = 1.2
demand_threshold_low = 0.8
supply_threshold_high = 0.8
supply_threshold_low = 1.2

data['adjusted_product_cost'] = data['Historical_Product_Cost'] * (
    np.maximum(data['demand_multiplier'], demand_threshold_low) *
    np.maximum(data['supply_multiplier'], supply_threshold_high)
)

# --- Profit Calculation and Visualization ---
data['profit_percentage'] = ((data['adjusted_product_cost'] - data['Historical_Product_Cost']) / data['Historical_Product_Cost']) * 100
profitable_sales = data[data['profit_percentage'] > 0]
loss_sales = data[data['profit_percentage'] < 0]

profitable_count = len(profitable_sales)
loss_count = len(loss_sales)

labels = ['Profitable Sales', 'Loss Sales']
values = [profitable_count, loss_count]

fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4)])
fig.update_layout(title='Profitability of Sales (Dynamic Pricing vs Historical Pricing)')
fig.show()

# --- Machine Learning Model Training (Modified for Number_of_Products) ---

data["Product_Type"] = data["Product_Type"].map({"Premium": 1, "Standard": 0})
data["Time_of_Sale"] = data["Time_of_Sale"].map({"Afternoon": 0, "Evening": 1, "Morning": 2, "Night": 3})

x = np.array(data[["Number_of_Products", "Number_of_Products", "Product_Type", "Time_of_Sale", "Expected_Delivery_Time"]])
y = np.array(data[["adjusted_product_cost"]])

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

y_train = y_train.ravel()
y_test = y_test.ravel()

model = RandomForestRegressor()
model.fit(x_train, y_train)

# --- Prediction Function (Modified for Number_of_Products Input) ---
def get_product_type_numeric(vehicle_type):
  type_mapping = {
      "Premium": 1,
      "Standard": 0
  }
  type_numeric = type_mapping.get(vehicle_type)
  return type_numeric

def get_time_of_sale_numeric(time_of_booking):
  time_of_sale_mapping = {
      "Afternoon": 0, 
      "Evening": 1, 
      "Morning": 2, 
      "Night": 3 
  }
  time_of_sale_numeric = time_of_sale_mapping.get(time_of_booking)
  return time_of_sale_numeric

#making predictions using user input values
def predict_price(number_of_riders, number_of_drivers, vehicle_type, time_of_booking, Expected_Delivery_Time):
  type_numeric = get_product_type_numeric(vehicle_type)
  if type_numeric is None:
    raise ValueError("Invalid product type")
  
  time_of_sale_numeric = get_time_of_sale_numeric(time_of_booking)
  if time_of_sale_numeric is None:
    raise ValueError("Invalid time of sale")

  input_data = np.array([[number_of_riders, number_of_drivers, type_numeric, time_of_sale_numeric, Expected_Delivery_Time]])
  predicted_price = model.predict(input_data)
  return predicted_price