import pandas as pd


import sqlite3

# Connect to your SQLite database
conn = sqlite3.connect('supplychain.sqlite')  

# Define the SQL query
query = """
SELECT *
FROM shipping_data
WHERE
    Days_for_shipment > 14
    OR LOWER(Late_delivery_risk) = 'yes'
    OR Order_Item_Discount_Rate > 0.5
    OR Order_Item_Discount > 1000
    OR Order_Item_Profit_Ratio < 0.05
    OR "Benefit per order" <= 0
    OR Product_Status IS NULL
    OR LOWER(Product_Status) = 'discontinued'
    OR (Product_Price > 5000 AND "Sales per customer" < 100)
    OR Shipping_Mode IS NULL
    OR Days_for_shipping > 10
    OR shipping_date IS NULL
"""

# Read the result into a DataFrame
flagged_df = pd.read_sql_query(query, conn)

# Close the connection
conn.close()

# Show flagged records
print("Potentially non-compliant supplier records:")
print(flagged_df)

# Optionally export to CSV
flagged_df.to_csv('flagged_suppliers.csv', index=False)
