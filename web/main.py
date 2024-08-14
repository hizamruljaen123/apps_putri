from flask import Flask, jsonify, request, render_template
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.cluster import Birch
import os
import uuid
from sklearn.manifold import TSNE
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly
import json
import logging


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


def visualize_sales_distribution_combined(df):
    color_mapping = {
        'Sangat Rendah': 'blue',
        'Rendah': 'green',
        'Cukup': 'gold',
        'Tinggi': 'salmon',
        'Sangat Tinggi': 'maroon'
    }
    
    kategori_per_merek = df.groupby(['Merek', 'Kategori_Penjualan']).size().unstack(fill_value=0)
    total_per_merek = kategori_per_merek.sum(axis=1)

    bar_data = []
    for kategori in kategori_per_merek.columns:
        bar_data.append(
            go.Bar(
                name=kategori,
                x=kategori_per_merek.index,
                y=kategori_per_merek[kategori],
                marker_color=color_mapping[kategori],
                text=[f"{count} ({(count / total_per_merek[merek] * 100):.1f}%)" 
                      for merek, count in zip(kategori_per_merek.index, kategori_per_merek[kategori])],
                textposition='auto'
            )
        )

    fig = go.Figure(data=bar_data)
    fig.update_layout(
        barmode='stack',
        title=f'Distribusi Kategori Penjualan per Merek Untuk {df["Toko"].iloc[0]}',
        xaxis_title='Merek',
        yaxis_title='Jumlah Produk',
        height=900
    )

    return fig

# Visualisasi t-SNE berdasarkan kategori penjualan
def visualize_clusters_tsne(df):
    features = ['Jumlah_Stok', 'Jumlah_Terjual', 'Persentase_Jumlah_Terjual']
    df_numeric = df[features].copy()
    df_numeric = df_numeric.fillna(df_numeric.median())
    X_normalized = (df_numeric.values - df_numeric.values.mean(axis=0)) / df_numeric.values.std(axis=0)

    tsne = TSNE(n_components=2, random_state=42)
    X_tsne = tsne.fit_transform(X_normalized)
    
    df_plot = df[['Merek', 'Tipe', 'Kategori_Penjualan']].copy()
    df_plot['x'] = X_tsne[:, 0]
    df_plot['y'] = X_tsne[:, 1]
    
    color_map = {
        'Sangat Rendah': '#FF4136',
        'Rendah': '#2ECC40',
        'Cukup': '#0074D9',
        'Tinggi': '#FF851B',
        'Sangat Tinggi': '#B10DC9',
    }
    
    fig = go.Figure()
    for category in df_plot['Kategori_Penjualan'].unique():
        category_data = df_plot[df_plot['Kategori_Penjualan'] == category]
        fig.add_trace(go.Scatter(
            x=category_data['x'],
            y=category_data['y'],
            mode='markers',
            marker=dict(size=8, color=color_map.get(category, 'grey'), opacity=0.7),
            text=category_data['Merek'] + ' - ' + category_data['Tipe'] + '<br>Kategori: ' + category,
            hoverinfo='text',
            name=category
        ))

    fig.update_layout(
        title=f'Visualisasi t-SNE Berdasarkan Kategori Penjualan {df["Toko"].iloc[0]}',
        xaxis_title='t-SNE Dimension 1',
        yaxis_title='t-SNE Dimension 2',
        legend_title='Kategori Penjualan',
        height=800
        # width=1000
    )

    return fig

# Visualisasi t-SNE berdasarkan merek
def visualize_tsne_by_brand(df, clusters):
    features = ['Jumlah_Stok', 'Jumlah_Terjual', 'Persentase_Jumlah_Terjual']
    df_numeric = df[features].copy()
    df_numeric = df_numeric.fillna(df_numeric.median())
    X_normalized = (df_numeric.values - df_numeric.values.mean(axis=0)) / df_numeric.values.std(axis=0)

    tsne = TSNE(n_components=2, random_state=42)
    X_tsne = tsne.fit_transform(X_normalized)

    df['x'] = X_tsne[:, 0]
    df['y'] = X_tsne[:, 1]
    df['Cluster'] = clusters

    merek_list = df['Merek'].unique()

    rows, cols = 2, 4
    fig = make_subplots(
        rows=rows, cols=cols, 
        subplot_titles=merek_list[:rows*cols],
        vertical_spacing=0.05,
        horizontal_spacing=0.05
    )

    color_map = {
        0: '#FF4136',
        1: '#2ECC40',
        2: '#0074D9',
        3: '#FF851B',
        4: '#B10DC9',
    }

    for i, merek in enumerate(merek_list[:rows*cols]):
        df_merek = df[df['Merek'] == merek]
        fig.add_trace(
            go.Scatter(
                x=df_merek['x'], 
                y=df_merek['y'], 
                mode='markers', 
                marker=dict(size=6, color=[color_map[cluster] for cluster in df_merek['Cluster']], opacity=0.7),
                text=df_merek['Tipe'] + '<br>Kategori: ' + df_merek['Kategori_Penjualan'],
                hoverinfo='text',
                showlegend=False
            ),
            row=(i//cols)+1, col=(i%cols)+1
        )

    fig.update_layout(
        title_text=f"Visualisasi t-SNE Berdasarkan Merek {df['Toko'].iloc[0]}",
        height=600 * rows,
        showlegend=False
    )

    return fig

# Visualisasi 3D berdasarkan cluster
def visualize_clusters_3d(df, clusters):
    features = ['Jumlah_Stok', 'Jumlah_Terjual', 'Persentase_Jumlah_Terjual']
    df_numeric = df[features].copy()
    
    for col in df_numeric.columns:
        df_numeric[col] = pd.to_numeric(df_numeric[col], errors='coerce')
    
    df_numeric = df_numeric.fillna(df_numeric.median())
    X_normalized = (df_numeric.values - df_numeric.values.mean(axis=0)) / df_numeric.values.std(axis=0)
    
    tsne = TSNE(n_components=3, random_state=42)
    X_tsne = tsne.fit_transform(X_normalized)
    
    df_plot = df[['Merek', 'Tipe', 'Kategori_Penjualan']].copy()
    df_plot['x'] = X_tsne[:, 0]
    df_plot['y'] = X_tsne[:, 1]
    df_plot['z'] = X_tsne[:, 2]
    df_plot['Cluster'] = clusters
    
    color_map = {
        0: '#FF4136',  
        1: '#2ECC40',  
        2: '#0074D9',  
        3: '#FF851B',  
        4: '#B10DC9',  
    }
    
    fig = go.Figure()

    for cluster in range(5):  
        cluster_data = df_plot[df_plot['Cluster'] == cluster]
        fig.add_trace(go.Scatter3d(
            x=cluster_data['x'],
            y=cluster_data['y'],
            z=cluster_data['z'],
            mode='markers',
            marker=dict(size=4, color=color_map[cluster], opacity=0.7),
            text=cluster_data['Merek'] + ' - ' + cluster_data['Tipe'] + '<br>Kategori: ' + cluster_data['Kategori_Penjualan'],
            hoverinfo='text',
            name=f'Cluster {cluster}'
        ))

    fig.update_layout(
        title='Visualisasi 3D 5 Cluster Utama BIRCH menggunakan t-SNE',
        scene=dict(
            xaxis_title='t-SNE Dimension 1',
            yaxis_title='t-SNE Dimension 2',
            zaxis_title='t-SNE Dimension 3',
        ),
        legend_title='Clusters',
        height=800,
        # width=1000,
        margin=dict(r=20, b=10, l=10, t=40)
    )

    return fig

def handle_missing_values(df):
    df.fillna({'': 0, np.number: 0}, inplace=True)

@app.route('/visualisasi')
def visualisasi():
    store = request.args.get('store', 'Jaya Com')
    connection = get_db_connection()
    query = f"""
    SELECT
        data.toko as Toko,
        data.Merek,
        data.Tipe,
        data.Bulan,
        data.tahun,
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
        data.toko = '{store}'
    """
    df = execute_query_to_dataframe(connection, query)

    if df is not None and not df.empty:
        # Cek apakah kolom 'Toko' ada di DataFrame
        if 'Toko' not in df.columns:
            return "Error: Kolom 'Toko' tidak ditemukan dalam data."

        columns_needed = ['Merek', 'Tipe', 'Jumlah_Stok', 'Jumlah_Terjual',
                          'Harga_Satuan_Rp', 'Total_Penjualan_Rp',
                          'Kamera_Utama_MP', 'Kamera_Depan_MP', 'RAM',
                          'Memori_Internal', 'Baterai_mAh', 'Jenis_Layar', 'Bulan', 'tahun']

        df_klastering = df[columns_needed].copy()
        df_klastering['Persentase_Jumlah_Terjual'] = (df_klastering['Jumlah_Terjual'] / df_klastering['Jumlah_Stok']) * 100

        handle_missing_values(df_klastering)
        df_klastering['Kategori_Penjualan'] = df_klastering['Persentase_Jumlah_Terjual'].apply(categorize_sales_percentage)

        birch_model = Birch(n_clusters=5, threshold=0.5)
        df_features = df_klastering[['Jumlah_Stok', 'Jumlah_Terjual', 'Persentase_Jumlah_Terjual']]
        birch_model.fit(df_features)

        clusters = birch_model.predict(df_features)
        df_klastering['Cluster'] = clusters

        # Tambahkan kolom 'Toko' ke df_klastering
        df_klastering['Toko'] = store

        fig_sales_distribution = visualize_sales_distribution_combined(df_klastering)
        fig_clusters_tsne = visualize_clusters_tsne(df_klastering)
        fig_tsne_by_brand = visualize_tsne_by_brand(df_klastering, clusters)
        fig_clusters_3d = visualize_clusters_3d(df_klastering, clusters)

        graphJSON_sales_distribution = json.dumps(fig_sales_distribution, cls=plotly.utils.PlotlyJSONEncoder)
        graphJSON_clusters_tsne = json.dumps(fig_clusters_tsne, cls=plotly.utils.PlotlyJSONEncoder)
        graphJSON_tsne_by_brand = json.dumps(fig_tsne_by_brand, cls=plotly.utils.PlotlyJSONEncoder)
        graphJSON_clusters_3d = json.dumps(fig_clusters_3d, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template('visualization.html',
                               graphJSON_sales_distribution=graphJSON_sales_distribution,
                               graphJSON_clusters_tsne=graphJSON_clusters_tsne,
                               graphJSON_tsne_by_brand=graphJSON_tsne_by_brand,
                               graphJSON_clusters_3d=graphJSON_clusters_3d,
                               store=store)

    return "No data available"
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
@app.route('/fetch-data/<nama_toko>', methods=['GET'])
def fetch_data(nama_toko):
    # Mapping nama_toko dari URL ke nama toko yang sesuai di database
    toko_mapping = {
        "jaya_com": "Jaya Com",
        "tm_store": "TM Store"
    }

    # Konversi nama_toko yang diterima menjadi format yang sesuai
    nama_toko_db = toko_mapping.get(nama_toko.lower())

    if not nama_toko_db:
        return jsonify({"error": "Invalid store name"}), 400

    logging.info(f"Fetching data for store: {nama_toko_db}")

    # Membuat query SQL untuk mengambil data dari database dengan filter berdasarkan nama toko
    query = """
    SELECT 
       data.toko as Toko,
        data.Merek,
        data.Tipe,
        data.Bulan,
        data.tahun,
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

    # Koneksi ke database
    connection = get_db_connection()

    try:
        # Eksekusi query dengan parameter nama_toko_db
        df = execute_query_to_dataframe(connection, query, (nama_toko_db,))
        logging.info(f"Query executed, number of rows retrieved: {len(df)}")
    except Exception as e:
        logging.error(f"Error executing query: {e}")
        return jsonify({"error": "Error fetching data"}), 500
    finally:
        # Tutup koneksi
        connection.close()

    if df is not None and not df.empty:
        # Ganti NaN dengan string kosong atau "-"
        df = df.fillna(value={
            'Jumlah_Stok': '-',
            'Jumlah_Terjual': '-',
            'Harga_Satuan_Rp': '-',
            'Total_Penjualan_Rp': '-',
            'Kamera_Utama_MP': '-',
            'Kamera_Depan_MP': '-',
            'RAM': '-',
            'Memori_Internal': '-',
            'Baterai_mAh': '-',
            'Jenis_Layar': '-'
        })

        # Bangun objek JSON dengan key unik
        data = {}
        for _, row in df.iterrows():
            key = f"{row['Merek']}_{row['Tipe']}_{row['Bulan']}"
            data[key] = {
                "Merek": row["Merek"],
                "Tipe": row["Tipe"],
                "Bulan": row["Bulan"],
                "tahun": row["tahun"],
                "Jumlah_Stok": row["Jumlah_Stok"],
                "Jumlah_Terjual": row["Jumlah_Terjual"],
                "Harga_Satuan_Rp": row["Harga_Satuan_Rp"],
                "Total_Penjualan_Rp": row["Total_Penjualan_Rp"],
                "Kamera_Utama_MP": row["Kamera_Utama_MP"],
                "Kamera_Depan_MP": row["Kamera_Depan_MP"],
                "RAM": row["RAM"],
                "Memori_Internal": row["Memori_Internal"],
                "Baterai_mAh": row["Baterai_mAh"],
                "Jenis_Layar": row["Jenis_Layar"]
            }

        # Mengembalikan data sebagai JSON terstruktur
        return jsonify({"data": data, "message": "Data fetched successfully"})
    else:
        logging.warning(f"No data found for store: {nama_toko_db}")
        return jsonify({"error": "No data found"}), 404




def map_store_name(store_name):
    store_name_map = {
        'tm_store': 'TM Store',
        'jaya_com': 'Jaya Com'
    }
    return store_name_map.get(store_name, store_name)

if __name__ == '__main__':
    app.run(debug=True)
