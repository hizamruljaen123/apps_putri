import pandas as pd
import numpy as np

# Load the provided Excel file
file_path = 'data.xlsx'
data = pd.read_excel(file_path)

# Calculate percentage of sales and price ratio
data['Percentage_Sold'] = data['Jumlah Terjual'] / data['Jumlah Stok']
data['Price_Ratio'] = data['Total Penjualan (Rp)'] / data['Harga Satuan (Rp)']

# Define the Clustering Feature class
class ClusteringFeature:
    def __init__(self, N, LS, SS):
        self.N = N  # Number of points
        self.LS = LS  # Linear Sum
        self.SS = SS  # Squared Sum
    
    def add_point(self, point):
        self.N += 1
        self.LS += point
        self.SS += point ** 2
    
    def merge(self, other_cf):
        self.N += other_cf.N
        self.LS += other_cf.LS
        self.SS += other_cf.SS

# Define the CF Tree Node class
class CFNode:
    def __init__(self, threshold):
        self.threshold = threshold
        self.entries = []

    def add_entry(self, entry):
        self.entries.append(entry)
        if len(self.entries) > self.threshold:
            self.split()

    def split(self):
        pass  # Simplified for this example

# Define the BIRCH Clustering class
class BIRCH:
    def __init__(self, threshold=3):
        self.threshold = threshold
        self.root = CFNode(threshold)

    def fit(self, data):
        for index, row in data.iterrows():
            point = np.array([row['Percentage_Sold'], row['Price_Ratio']])
            cf = ClusteringFeature(1, point, point ** 2)
            self.insert_cf(self.root, cf)

    def insert_cf(self, node, cf):
        if len(node.entries) == 0:
            node.add_entry(cf)
        else:
            closest_cf = min(node.entries, key=lambda entry: np.linalg.norm(entry.LS / entry.N - cf.LS / cf.N))
            if np.linalg.norm(closest_cf.LS / closest_cf.N - cf.LS / cf.N) < self.threshold:
                closest_cf.merge(cf)
            else:
                node.add_entry(cf)
    
    def print_tree(self, node=None, depth=0):
        if node is None:
            node = self.root
        for entry in node.entries:
            print('  ' * depth, f'N: {entry.N}, LS: {entry.LS}, SS: {entry.SS}')
            if isinstance(entry, CFNode):
                self.print_tree(entry, depth + 1)

# Function to categorize the sales levels
def categorize_sales_level(percentage_sold):
    if percentage_sold <= 0.2:
        return 'Sangat Rendah'
    elif percentage_sold <= 0.4:
        return 'Rendah'
    elif percentage_sold <= 0.6:
        return 'Cukup'
    elif percentage_sold <= 0.8:
        return 'Tinggi'
    else:
        return 'Sangat Tinggi'

# Apply categorization
data['Sales_Level'] = data['Percentage_Sold'].apply(categorize_sales_level)

# Create and fit the BIRCH model
birch = BIRCH(threshold=0.5)
birch.fit(data[['Percentage_Sold', 'Price_Ratio']])
birch.print_tree()

# Display categorized data
print(data[['Merek', 'Tipe', 'Percentage_Sold', 'Sales_Level']])
