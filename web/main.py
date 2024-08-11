from flask import Flask, jsonify, request, render_template
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.cluster import Birch
import os
import uuid

app = Flask(__name__)

# Create uploads directory if it doesn't exist
if not os.path.exists('static/uploads'):
    os.makedirs('static/uploads')

# Database connection details
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'data_smartphone',
    'port': 3306
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def execute_query_to_dataframe(connection, query, params=None):
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params)
        result = cursor.fetchall()
        df = pd.DataFrame(result)
        return df
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        cursor.close()

def categorize_sales_percentage(percent_sold):
    if percent_sold < 10:
        return 'Sangat Rendah'
    elif percent_sold < 20:
        return 'Rendah'
    elif percent_sold < 50:
        return 'Cukup'
    elif percent_sold < 70:
        return 'Tinggi'
    else:
        return 'Sangat Tinggi'

def perform_clustering(df, threshold):
    # Fill NaN values with zero
    df.fillna(0, inplace=True)
    
    birch_model = Birch(n_clusters=None, threshold=threshold)
    df_features = df[['Jumlah_Stok', 'Harga_Satuan_Rp', 'Persentase_Jumlah_Terjual']]
    birch_model.fit(df_features)
    clusters = birch_model.predict(df_features)
    df['Cluster'] = clusters
    return df

def generate_visualizations(df):
    df.fillna(0, inplace=True)
    image_files = {}

    def save_plot(filename_prefix):
        file_id = str(uuid.uuid4())
        file_path = f'static/uploads/{filename_prefix}.png'
        plt.savefig(file_path)
        plt.close()
        return file_path

    # Scatter Plot Klasterisasi
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='Jumlah_Terjual', y='Harga_Satuan_Rp', hue='Cluster', data=df, palette='viridis', s=100)
    plt.title('Scatter Plot Klasterisasi')
    plt.xlabel('Jumlah Terjual')
    plt.ylabel('Harga Satuan Rp')
    plt.legend(title='Klaster')
    plt.grid(True)
    image_files['scatter_klasterisasi'] = save_plot('scatter_klasterisasi')

    # Scatter Plot berdasarkan Kategori Penjualan
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='Jumlah_Stok', y='Harga_Satuan_Rp', hue='Kategori_Penjualan', data=df, palette='viridis', s=100)
    plt.title('Scatter Plot berdasarkan Kategori Penjualan')
    plt.xlabel('Jumlah Stok')
    plt.ylabel('Harga Satuan Rp')
    plt.legend(title='Kategori Penjualan')
    plt.grid(True)
    image_files['scatter_kategori_penjualan'] = save_plot('scatter_kategori_penjualan')

    # Hasil Pemisahan Berdasarkan Kategori Penjualan
    plt.figure(figsize=(10, 6))
    colors = {
        'Sangat Rendah': 'blue',
        'Rendah': 'green',
        'Cukup': 'red',
        'Tinggi': 'purple',
        'Sangat Tinggi': 'orange'
    }
    for category, color in colors.items():
        plt.scatter(df.loc[df['Kategori_Penjualan'] == category, 'Jumlah_Terjual'],
                    df.loc[df['Kategori_Penjualan'] == category, 'Harga_Satuan_Rp'],
                    color=color, label=category, alpha=0.7, edgecolors='k', linewidths=0.5)
    plt.title('Hasil Pemisahan Berdasarkan Kategori Penjualan')
    plt.xlabel('Jumlah Terjual')
    plt.ylabel('Harga Satuan (Rp)')
    plt.legend()
    plt.grid(True)
    image_files['hasil_pemisahan_kategori_penjualan'] = save_plot('hasil_pemisahan_kategori_penjualan')

    # Jumlah Tipe Merek dalam Setiap Kategori Penjualan
    plt.figure(figsize=(12, 8))
    penjualan_merek = df.groupby(['Merek', 'Kategori_Penjualan']).size().reset_index(name='Frekuensi')
    sns.barplot(x='Merek', y='Frekuensi', hue='Kategori_Penjualan', data=penjualan_merek, palette='viridis')
    plt.title('Jumlah Tipe Merek dalam Setiap Kategori Penjualan')
    plt.xlabel('Merek')
    plt.ylabel('Frekuensi')
    plt.xticks(rotation=45)
    plt.legend(title='Kategori Penjualan', loc='upper right')
    plt.tight_layout()
    image_files['jumlah_tipe_merek_kategori_penjualan'] = save_plot('jumlah_tipe_merek_kategori_penjualan')

    # Total Penjualan Berdasarkan Merek Smartphone
    plt.figure(figsize=(12, 6))
    penjualan_merek = df.groupby('Merek')['Jumlah_Terjual'].sum().sort_values(ascending=False)
    colors = plt.cm.tab10(np.arange(len(penjualan_merek)))
    penjualan_merek.plot(kind='bar', color=colors)
    plt.title('Total Penjualan Berdasarkan Merek Smartphone')
    plt.xlabel('Merek')
    plt.ylabel('Total Penjualan')
    plt.xticks(rotation=45)
    plt.grid(axis='y')
    patches = [plt.Rectangle((0,0),1,1, color=colors[i], label=merek) for i, merek in enumerate(penjualan_merek.index)]
    plt.legend(handles=patches, loc='upper right')
    image_files['total_penjualan_merek'] = save_plot('total_penjualan_merek')

    # Distribusi Penjualan Berdasarkan Kategori Klastering Menggunakan BIRCH
    plt.figure(figsize=(14, 8))
    class_boundaries = {
        'Sangat Rendah': (0, 2),
        'Rendah': (3, 5),
        'Cukup': (6, 10),
        'Berpotensi Tinggi': (11, 20),
        'Tinggi': (21, 50),
        'Sangat Tinggi': (51, np.inf)
    }
    class_colors = {
        'Sangat Rendah': 'blue',
        'Rendah': 'green',
        'Cukup': 'yellow',
        'Berpotensi Tinggi': 'orange',
        'Tinggi': 'red',
        'Sangat Tinggi': 'purple'
    }
    for class_name, (lower, upper) in class_boundaries.items():
        plt.fill_betweenx(y=[lower, upper], x1=0, x2=len(df), color=class_colors[class_name], alpha=0.2, label=f'{class_name}')
    for idx, row in df.iterrows():
        plt.scatter(idx, row['Jumlah_Terjual'], color=class_colors[row['Kategori_Penjualan']], label=row['Kategori_Penjualan'])
    plt.title('Distribusi Penjualan Berdasarkan Kategori Klastering Menggunakan BIRCH')
    plt.xlabel('Indeks Data')
    plt.ylabel('Jumlah Terjual')
    plt.grid(True)
    handles = [plt.Rectangle((0,0),1,1, color=class_colors[label]) for label in class_boundaries.keys()]
    labels = class_boundaries.keys()
    plt.legend(handles, labels, loc='upper left')
    image_files['distribusi_penjualan_klastering_birch'] = save_plot('distribusi_penjualan_klastering_birch')

    # Heatmap Distribusi Penjualan Berdasarkan Merek dan Bulan
    plt.figure(figsize=(12, 8))
    penjualan_bulanan = df.pivot_table(index='Merek', columns='Bulan', values='Jumlah_Terjual', aggfunc='sum', fill_value=0)
    fig, ax = plt.subplots(figsize=(12, 8))
    cax = ax.imshow(penjualan_bulanan, cmap='viridis', aspect='auto')
    for i in range(len(penjualan_bulanan.index)):
        for j in range(len(penjualan_bulanan.columns)):
            val = penjualan_bulanan.iloc[i, j]
            ax.text(j, i, f'{val}', ha='center', va='center', color='white', fontsize=10, fontweight='bold')
    ax.set_xticks(range(len(penjualan_bulanan.columns)))
    ax.set_yticks(range(len(penjualan_bulanan.index)))
    ax.set_xticklabels(penjualan_bulanan.columns, color='white')
    ax.set_yticklabels(penjualan_bulanan.index, color='white')
    fig.colorbar(cax, ax=ax, label='Jumlah Terjual')
    plt.title('Heatmap Distribusi Penjualan Berdasarkan Merek Smartphone', color='white')
    plt.xlabel('Bulan', color='white')
    plt.ylabel('Merek', color='white')
    image_files['heatmap_penjualan_merek'] = save_plot('heatmap_penjualan_merek')

    return image_files

@app.route('/visualize', methods=['POST'])
def visualize_data():
    request_data = request.get_json()
    store_name = request_data.get('store')
    if not store_name:
        return jsonify({"error": "Store name is required"}), 400
    
    store_name = map_store_name(store_name)

    query = """
    SELECT 
        data.Merek,
        data.Tipe,
        data.Bulan,
        data.Jumlah_Stok,
        data.Jumlah_Terjual,
        data.Harga_Satuan_Rp,
        data.Total_Penjualan_Rp,
        data_spesifikasi.Kamera_Utama_MP,
        data_spesifikasi.Kamera_Depan_MP,
        data_spesifikasi.RAM,
        data_spesifikasi.Memori_Internal,
        data_spesifikasi.Baterai_mAh,
        data_spesifikasi.Jenis_Layar
    FROM 
        data
    LEFT JOIN 
        data_spesifikasi 
    ON 
        data.Tipe = data_spesifikasi.Tipe
    WHERE 
        data.toko = %s;
    """
    
    connection = get_db_connection()
    if connection and connection.is_connected():
        df = execute_query_to_dataframe(connection, query, (store_name,))
        if df is not None and not df.empty:
            df['Persentase_Jumlah_Terjual'] = (df['Jumlah_Terjual'] / df['Jumlah_Stok']) * 100
            df['Kategori_Penjualan'] = df['Persentase_Jumlah_Terjual'].apply(categorize_sales_percentage)
            
            # Perform clustering
            threshold_start = request_data.get('threshold_start', 0.1)
            threshold_end = request_data.get('threshold_end', 0.5)
            num_iterations = request_data.get('num_iterations', 5)
            threshold_increment = (threshold_end - threshold_start) / (num_iterations - 1)
            current_threshold = threshold_start
            
            for _ in range(num_iterations):
                df = perform_clustering(df, current_threshold)
                current_threshold += threshold_increment
            
            image_files = generate_visualizations(df)
            return jsonify({"message": "Visualizations created", "images": image_files})
        else:
            return jsonify({"error": "Data not found"}), 404
    else:
        return jsonify({"error": "Failed to connect to the database"}), 500

@app.route('/perform-clustering', methods=['POST'])
def perform_clustering_route():
    request_data = request.get_json()
    store_name = request_data.get('store')
    threshold = request_data.get('threshold', 0.3)

    if not store_name:
        return jsonify({"error": "Store name is required"}), 400
    
    store_name = map_store_name(store_name)

    query = """
    SELECT 
        data.Merek,
        data.Tipe,
        data.Bulan,
        data.Jumlah_Stok,
        data.Jumlah_Terjual,
        data.Harga_Satuan_Rp,
        data.Total_Penjualan_Rp,
        data_spesifikasi.Kamera_Utama_MP,
        data_spesifikasi.Kamera_Depan_MP,
        data_spesifikasi.RAM,
        data_spesifikasi.Memori_Internal,
        data_spesifikasi.Baterai_mAh,
        data_spesifikasi.Jenis_Layar
    FROM 
        data
    LEFT JOIN 
        data_spesifikasi 
    ON 
        data.Tipe = data_spesifikasi.Tipe
    WHERE 
        data.toko = %s;
    """
    
    connection = get_db_connection()
    if connection and connection.is_connected():
        df = execute_query_to_dataframe(connection, query, (store_name,))
        if df is not None and not df.empty:
            df['Persentase_Jumlah_Terjual'] = (df['Jumlah_Terjual'] / df['Jumlah_Stok']) * 100
            df['Kategori_Penjualan'] = df['Persentase_Jumlah_Terjual'].apply(categorize_sales_percentage)
            df = perform_clustering(df, threshold)
            
            response_data = df[['Merek', 'Tipe', 'Bulan', 'Persentase_Jumlah_Terjual', 'Kategori_Penjualan', 'Cluster']].to_dict(orient='records')
            return jsonify({"message": "Clustering performed", "data": response_data})
        else:
            return jsonify({"error": "Data not found"}), 404
    else:
        return jsonify({"error": "Failed to connect to the database"}), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit-data', methods=['POST'])
def submit_data():
    data = request.json

    store_name = data.get('store')
    data_spec = data.get('dataSpec')
    data_penjualan = data.get('dataPenjualan')

    if not store_name or not data_spec or not data_penjualan:
        return jsonify({'status': 'error', 'message': 'Store name, data specification, and sales data are required'}), 400

    connection = get_db_connection()
    if connection and connection.is_connected():
        cursor = connection.cursor()
        try:
            # Insert into data_spesifikasi
            cursor.execute("""
                INSERT INTO data_spesifikasi (Merek, Tipe, Kamera_Utama_MP, Kamera_Depan_MP, RAM, Memori_Internal, Baterai_mAh, Jenis_Layar)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data_spec['Merek'],
                data_spec['Tipe'],
                data_spec['Kamera_Utama_MP'],
                data_spec['Kamera_Depan_MP'],
                data_spec['RAM'],
                data_spec['Memori_Internal'],
                data_spec['Baterai_mAh'],
                data_spec['Jenis_Layar']
            ))

            # Insert into data
            cursor.execute("""
                INSERT INTO data (store, Jumlah_Terjual, Total_Penjualan_Rp, Merek, Tipe, Bulan, Jumlah_Stok)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                store_name,
                data_penjualan['Jumlah_Penjualan'],
                data_penjualan['Total_Penjualan'],
                data_spec['Merek'],
                data_spec['Tipe'],
                data_penjualan['Bulan'],
                data_penjualan['Jumlah_Stok']
            ))

            connection.commit()
            return jsonify({'status': 'success'}), 200
        except Exception as e:
            connection.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    else:
        return jsonify({'status': 'error', 'message': 'Failed to connect to the database'}), 500

def map_store_name(store_name):
    store_name_map = {
        'tm_store': 'TM Store',
        'jaya_com': 'Jaya Com'
    }
    return store_name_map.get(store_name, store_name)

if __name__ == '__main__':
    app.run(debug=True)
