import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# Set page config
st.set_page_config(page_title="HAVC-PRO Advanced Sheet Metal Dashboard", layout="wide")

# Product categories and their specific attributes
PRODUCTS = {
    "Rectangular Duct": {
        "unit": "sq ft", 
        "material": "Galvanized Steel", 
        "thickness": ["24 ga", "22 ga", "20 ga"],
        "dimensions": ["12\"x8\"", "16\"x10\"", "20\"x12\""]
    },
    "Round Pipes": {
        "unit": "linear ft", 
        "material": "Galvanized Steel", 
        "diameter": ["6\"", "8\"", "10\"", "12\""]
    },
    "Elbows": {
        "unit": "piece", 
        "material": "Galvanized Steel", 
        "angle": ["45°", "90°"], 
        "diameter": ["6\"", "8\"", "10\"", "12\""]
    },
    "Reducers": {
        "unit": "piece", 
        "material": "Galvanized Steel", 
        "size": ["8\"x6\"", "10\"x8\"", "12\"x10\""]
    },
    "Dampers": {
        "unit": "piece", 
        "material": "Galvanized Steel", 
        "type": ["Manual", "Motorized"], 
        "size": ["6\"", "8\"", "10\"", "12\""]
    },
    "Boots": {
        "unit": "piece", 
        "material": "Galvanized Steel", 
        "type": ["Side", "End"], 
        "size": ["6\"x10\"", "8\"x12\"", "10\"x12\""]
    },
    "Take Offs": {
        "unit": "piece", 
        "material": "Galvanized Steel", 
        "size": ["6\"", "8\"", "10\"", "12\""]
    },
    "Spiral Pipes": {
        "unit": "linear ft", 
        "material": "Galvanized Steel", 
        "diameter": ["6\"", "8\"", "10\"", "12\""]
    },
    "Flex Pipes": {
        "unit": "linear ft", 
        "material": "Aluminum", 
        "diameter": ["6\"", "8\"", "10\"", "12\""]
    },
    "Caps": {
        "unit": "piece", 
        "material": "Galvanized Steel", 
        "diameter": ["6\"", "8\"", "10\"", "12\""]
    },
    "Tees": {
        "unit": "piece", 
        "material": "Galvanized Steel", 
        "size": ["6\"", "8\"", "10\"", "12\""]
    },
    "Collars": {
        "unit": "piece", 
        "material": "Galvanized Steel", 
        "diameter": ["6\"", "8\"", "10\"", "12\""]
    },
    "Insulation Sleeves": {
        "unit": "linear ft", 
        "material": "Fiberglass", 
        "thickness": ["1\"", "1.5\"", "2\""], 
        "diameter": ["6\"", "8\"", "10\"", "12\""]
    }
}

# Generate fake data
def generate_fake_data(days=365):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days-1)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    data = {
        'Date': date_range,
        'Steel_Cost': np.random.uniform(0.5, 1.0, days) + np.sin(np.arange(days) * 2 * np.pi / 365) * 0.1,
        'Aluminum_Cost': np.random.uniform(1.0, 1.5, days) + np.sin(np.arange(days) * 2 * np.pi / 365) * 0.15,
        'Fiberglass_Cost': np.random.uniform(0.3, 0.6, days) + np.sin(np.arange(days) * 2 * np.pi / 365) * 0.05,
        'Labor_Rate': np.random.uniform(20, 30, days) + np.cumsum(np.random.normal(0, 0.01, days)),
        'Electricity_Cost': np.random.uniform(0.1, 0.2, days) + np.sin(np.arange(days) * 2 * np.pi / 365) * 0.02,
        'Order_Volume': np.random.randint(50, 500, days) + np.sin(np.arange(days) * 2 * np.pi / 365) * 100
    }
    return pd.DataFrame(data)

# Calculate price
def calculate_price(base_cost, margin, volume_discount=0):
    return base_cost / (1 - margin) * (1 - volume_discount)

# Main app
def main():
    st.title("HAVC-PRO Advanced Sheet Metal Pricing & Analysis Dashboard")

    # Generate fake data
    df = generate_fake_data()

    # Sidebar for global inputs
    st.sidebar.header("Global Pricing Factors")
    target_margin = st.sidebar.slider("Target Profit Margin", 0.1, 0.5, 0.3, 0.01)
    volume_discount = st.sidebar.slider("Volume Discount", 0.0, 0.2, 0.05, 0.01)
    
    # Create tabs
    tabs = st.tabs(["Market Overview", "Product Pricing", "Cost Analysis", "Demand Forecasting", "Competitor Analysis"])
    
    with tabs[0]:  # Market Overview
        st.header("Market Overview")
        col1, col2, col3 = st.columns(3)
        col1.metric("Avg. Steel Cost", f"${df['Steel_Cost'].mean():.2f}/lb", f"{(df['Steel_Cost'].pct_change().mean() * 100):.2f}%")
        col2.metric("Avg. Labor Rate", f"${df['Labor_Rate'].mean():.2f}/hr", f"{(df['Labor_Rate'].pct_change().mean() * 100):.2f}%")
        col3.metric("Avg. Electricity Cost", f"${df['Electricity_Cost'].mean():.2f}/kWh", f"{(df['Electricity_Cost'].pct_change().mean() * 100):.2f}%")

        st.subheader("Material Cost Trends")
        fig = px.line(df, x='Date', y=['Steel_Cost', 'Aluminum_Cost', 'Fiberglass_Cost'], 
                      title="Material Costs Over Time")
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Order Volume Trends")
        fig = px.bar(df, x='Date', y='Order_Volume', title="Daily Order Volume")
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Order_Volume'].rolling(window=30).mean(), 
                                 mode='lines', name='30-day Moving Average'))
        st.plotly_chart(fig, use_container_width=True)

    with tabs[1]:  # Product Pricing
        st.header("Product Pricing Calculator")
        
        product = st.selectbox("Select Product", list(PRODUCTS.keys()))
        attributes = PRODUCTS[product]
        
        options = {}
        for attr, values in attributes.items():
            if isinstance(values, list):
                options[attr] = st.selectbox(f"Select {attr}", values)
        
        material_cost = st.number_input(f"{attributes['material']} Cost", 0.5, 5.0, 1.0, 0.1)
        labor_hours = st.number_input("Labor Hours", 0.5, 10.0, 1.0, 0.1)
        overhead_cost = st.number_input("Overhead Cost", 5.0, 50.0, 10.0, 0.5)
        
        base_cost = material_cost + (labor_hours * df['Labor_Rate'].mean()) + overhead_cost
        price = calculate_price(base_cost, target_margin)
        
        st.metric("Calculated Price", f"${price:.2f}/{attributes['unit']}")
        
        st.subheader("Price Breakdown")
        fig = px.pie(values=[material_cost, labor_hours * df['Labor_Rate'].mean(), overhead_cost], 
                     names=['Material', 'Labor', 'Overhead'],
                     title="Cost Components")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Price Sensitivity")
        margin_range = np.linspace(0.1, 0.5, 100)
        prices = [calculate_price(base_cost, m) for m in margin_range]
        fig = px.line(x=margin_range, y=prices, labels={'x': 'Profit Margin', 'y': 'Price'})
        fig.add_vline(x=target_margin, line_dash="dash", annotation_text="Current Margin")
        st.plotly_chart(fig, use_container_width=True)

    with tabs[2]:  # Cost Analysis
        st.header("Cost Analysis")
        
        st.subheader("Cost Correlation Heatmap")
        corr = df[['Steel_Cost', 'Aluminum_Cost', 'Fiberglass_Cost', 'Labor_Rate', 'Electricity_Cost']].corr()
        fig = px.imshow(corr, text_auto=True, aspect="auto")
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Cost Sensitivity Analysis")
        material_range = np.linspace(df['Steel_Cost'].min(), df['Steel_Cost'].max(), 100)
        labor_range = np.linspace(df['Labor_Rate'].min(), df['Labor_Rate'].max(), 100)
        
        X, Y = np.meshgrid(material_range, labor_range)
        Z = calculate_price(X + Y + overhead_cost, target_margin)
        
        fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y)])
        fig.update_layout(scene = dict(xaxis_title='Material Cost',
                                       yaxis_title='Labor Rate',
                                       zaxis_title='Price'))
        st.plotly_chart(fig, use_container_width=True)

    with tabs[3]:  # Demand Forecasting
        st.header("Demand Forecasting")
        
        st.subheader("Seasonal Decomposition")
        from statsmodels.tsa.seasonal import seasonal_decompose
        result = seasonal_decompose(df['Order_Volume'], model='additive', period=30)
        fig = make_subplots(rows=4, cols=1, subplot_titles=("Observed", "Trend", "Seasonal", "Residual"))
        fig.add_trace(go.Scatter(x=df['Date'], y=result.observed, mode='lines', name='Observed'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['Date'], y=result.trend, mode='lines', name='Trend'), row=2, col=1)
        fig.add_trace(go.Scatter(x=df['Date'], y=result.seasonal, mode='lines', name='Seasonal'), row=3, col=1)
        fig.add_trace(go.Scatter(x=df['Date'], y=result.resid, mode='lines', name='Residual'), row=4, col=1)
        fig.update_layout(height=800)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Future Demand Prediction")
        future_dates = pd.date_range(start=df['Date'].max() + timedelta(days=1), periods=30, freq='D')
        future_demand = np.random.randint(df['Order_Volume'].min(), df['Order_Volume'].max(), 30)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Order_Volume'], mode='lines', name='Historical Demand'))
        fig.add_trace(go.Scatter(x=future_dates, y=future_demand, mode='lines', name='Predicted Demand'))
        
        # Add a custom vertical line for "Today"
        max_date = df['Date'].max()
        y_range = [df['Order_Volume'].min(), df['Order_Volume'].max()]
        fig.add_trace(go.Scatter(x=[max_date, max_date], y=y_range, 
                                 mode='lines', name='Today',
                                 line=dict(color='red', width=2, dash='dash')))
        
        fig.update_layout(
            annotations=[
                dict(
                    x=max_date,
                    y=y_range[1],
                    xref="x",
                    yref="y",
                    text="Today",
                    showarrow=True,
                    arrowhead=7,
                    ax=0,
                    ay=-40
                )
            ]
        )
        
        st.plotly_chart(fig, use_container_width=True)


    with tabs[4]:  # Competitor Analysis
        st.header("Competitor Analysis")
        
        st.subheader("Market Position")
        competitor1 = st.number_input("Competitor 1 Price", 0.0, 1000.0, price * 0.9, 5.0)
        competitor2 = st.number_input("Competitor 2 Price", 0.0, 1000.0, price * 1.1, 5.0)
        
        fig = go.Figure(data=[
            go.Bar(name='HAVC-PRO', x=['Price'], y=[price]),
            go.Bar(name='Competitor 1', x=['Price'], y=[competitor1]),
            go.Bar(name='Competitor 2', x=['Price'], y=[competitor2])
        ])
        fig.update_layout(barmode='group')
        st.plotly_chart(fig, use_container_width=True)
        
        if price < min(competitor1, competitor2):
            st.success("Your price is competitive in the market!")
        elif price > max(competitor1, competitor2):
            st.warning("Your price is higher than competitors. Consider adjusting your margins or reducing costs.")
        else:
            st.info("Your price is within the competitive range.")

        st.subheader("Price-Quality Matrix")
        quality_score = st.slider("HAVC-PRO Quality Score", 1, 10, 8)
        comp1_quality = st.slider("Competitor 1 Quality Score", 1, 10, 7)
        comp2_quality = st.slider("Competitor 2 Quality Score", 1, 10, 6)
        
        fig = px.scatter(x=[quality_score, comp1_quality, comp2_quality], 
                         y=[price, competitor1, competitor2],
                         text=['HAVC-PRO', 'Competitor 1', 'Competitor 2'],
                         labels={'x': 'Quality Score', 'y': 'Price'})
        fig.update_traces(textposition='top center')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()