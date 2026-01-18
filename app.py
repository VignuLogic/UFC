from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import json
from datetime import datetime

app = Flask(__name__)

# File paths
CSV_FILE = 'sales_data.csv'
MENU_FILE = 'static/menu_data.json'

# Initialize CSV
def init_csv():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=['DateTime', 'ProductName', 'Category', 'Quantity', 'Price', 'Total'])
        df.to_csv(CSV_FILE, index=False)

init_csv()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/get-menu-data')
def get_menu_data():
    try:
        with open(MENU_FILE, 'r') as f:
            menu_data = json.load(f)
        return jsonify(menu_data)
    except FileNotFoundError:
        return jsonify({'error': 'Menu file not found'}), 404

@app.route('/order-entry')
def order_entry():
    return render_template('order_entry.html')

@app.route('/submit-order', methods=['POST'])
def submit_order():
    try:
        data = request.json
        total = float(data['quantity']) * float(data['price'])
        
        new_row = {
            'DateTime': data['datetime'],
            'ProductName': data['product_name'],
            'Category': data['category'],
            'Quantity': int(data['quantity']),
            'Price': float(data['price']),
            'Total': total
        }
        
        df = pd.read_csv(CSV_FILE)
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)
        
        return jsonify({'success': True, 'message': 'Order recorded successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/get-analytics-data')
def get_analytics_data():
    try:
        if not os.path.exists(CSV_FILE):
            return jsonify({'error': 'No data available'})
        
        df = pd.read_csv(CSV_FILE)
        
        if df.empty:
            return jsonify({'error': 'No sales data yet. Start adding orders!'})
        
        df['DateTime'] = pd.to_datetime(df['DateTime'])
        df['Date'] = df['DateTime'].dt.date
        df['Hour'] = df['DateTime'].dt.hour
        
        daily_revenue = df.groupby('Date')['Total'].sum().reset_index()
        daily_revenue['Date'] = daily_revenue['Date'].astype(str)
        
        top_products = df.groupby('ProductName')['Quantity'].sum().sort_values(ascending=False).head(10)
        
        peak_hours = df.groupby('Hour')['Total'].sum().reset_index()
        
        category_sales = df.groupby('Category')['Total'].sum().reset_index()
        
        return jsonify({
            'daily_revenue': daily_revenue.to_dict('records'),
            'top_products': {
                'labels': top_products.index.tolist(),
                'values': top_products.values.tolist()
            },
            'peak_hours': peak_hours.to_dict('records'),
            'category_sales': category_sales.to_dict('records')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/insights')
def insights():
    return render_template('insights.html')

@app.route('/get-insights')
def get_insights():
    try:
        if not os.path.exists(CSV_FILE):
            return jsonify({'insights': ['No data available']})
        
        df = pd.read_csv(CSV_FILE)
        
        if df.empty:
            return jsonify({'insights': ['No sales data yet. Start adding orders!']})
        
        df['DateTime'] = pd.to_datetime(df['DateTime'])
        df['Hour'] = df['DateTime'].dt.hour
        df['DayOfWeek'] = df['DateTime'].dt.day_name()
        df['Date'] = df['DateTime'].dt.date
        
        insights = []
        
        # Best selling item
        product_sales = df.groupby('ProductName')['Quantity'].sum()
        if not product_sales.empty:
            best_item = product_sales.idxmax()
            best_qty = product_sales.max()
            insights.append(f"🏆 Best Selling Item: {best_item} with {best_qty} units sold")
        
        # Low selling items
        if len(product_sales) >= 3:
            low_items = product_sales.sort_values().head(3)
            low_list = ', '.join([f"{name} ({qty} units)" for name, qty in low_items.items()])
            insights.append(f"📉 Low Selling Items: {low_list}")
        
        # Peak hour
        hourly_sales = df.groupby('Hour')['Total'].sum()
        if not hourly_sales.empty:
            peak_hour = hourly_sales.idxmax()
            insights.append(f"⏰ Peak Sales Hour: {peak_hour}:00 - {peak_hour+1}:00")
        
        # Most popular category
        category_sales = df.groupby('Category')['Total'].sum()
        if not category_sales.empty:
            top_category = category_sales.idxmax()
            top_revenue = category_sales.max()
            insights.append(f"📊 Most Popular Category: {top_category} (${top_revenue:.2f})")
        
        # Best day
        day_sales = df.groupby('DayOfWeek')['Total'].sum()
        if not day_sales.empty:
            best_day = day_sales.idxmax()
            insights.append(f"📅 Best Day of Week: {best_day}")
        
        # Total revenue
        total_revenue = df['Total'].sum()
        insights.append(f"💰 Total Revenue: ${total_revenue:.2f}")
        
        # Average order
        avg_order = df['Total'].mean()
        insights.append(f"💵 Average Order Value: ${avg_order:.2f}")
        
        # Total orders
        total_orders = len(df)
        insights.append(f"📦 Total Orders: {total_orders}")
        
        return jsonify({'insights': insights})
    except Exception as e:
        return jsonify({'insights': [f'Error: {str(e)}']}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🥛 UNITED FARMERS CREAMERY - Analytics System")
    print("=" * 60)
    print("Server running at: http://127.0.0.1:5000/")
    print("Press CTRL+C to stop the server")
    print("=" * 60)
    app.run(debug=True)