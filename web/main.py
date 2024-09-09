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
import plotly.express as px
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
        'Sangat Tinggi': 'maroon',
        'Tinggi': 'salmon',
        'Cukup': 'gold',
        'Rendah': 'green',
        'Sangat Rendah': 'blue'
    }

    # Urutkan kategori sesuai dengan urutan yang diinginkan
    kategori_terurut = ['Sangat Tinggi', 'Tinggi', 'Cukup', 'Rendah', 'Sangat Rendah']

    kategori_per_merek = df.groupby(['Merek', 'Kategori_Penjualan']).size().unstack(fill_value=0)
    total_per_merek = kategori_per_merek.sum(axis=1)

    bar_data = []
    for kategori in kategori_terurut:
        if kategori in kategori_per_merek.columns:
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
        title=f'Distribusi Frekuensi Kemunculan Kategori Penjualan per Merek Untuk {df["Toko"].iloc[0]}  2020 - 2024',
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
    
    df_plot = df[['Merek', 'Tipe', 'Kategori_Penjualan', 'Bulan', 'Tahun']].copy()
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
            text=category_data['Merek'] + ' - ' + category_data['Tipe'] + '<br>Kategori: ' + category +
                 '<br>Bulan: ' + category_data['Bulan'].astype(str) + '<br>Tahun: ' + category_data['Tahun'].astype(str),
            hoverinfo='text',
            name=category
        ))

    fig.update_layout(
        title=f'Visualisasi t-SNE Berdasarkan Kategori Penjualan {df["Toko"].iloc[0]} 2020 - 2024',
        xaxis_title='t-SNE Dimension 1',
        yaxis_title='t-SNE Dimension 2',
        legend_title='Kategori Penjualan',
        height=800
    )

    return fig


# Visualisasi t-SNE berdasarkan merek
def visualize_clusters_tsne(df):
    features = ['Jumlah_Stok', 'Jumlah_Terjual', 'Persentase_Jumlah_Terjual']
    df_numeric = df[features].copy()
    df_numeric = df_numeric.fillna(df_numeric.median())
    X_normalized = (df_numeric.values - df_numeric.values.mean(axis=0)) / df_numeric.values.std(axis=0)

    tsne = TSNE(n_components=2, random_state=42)
    X_tsne = tsne.fit_transform(X_normalized)
    
    df_plot = df[['Merek', 'Tipe', 'Kategori_Penjualan', 'Bulan', 'Tahun']].copy()
    df_plot['x'] = X_tsne[:, 0]
    df_plot['y'] = X_tsne[:, 1]
    
    color_map = {
        'Sangat Rendah': '#FF4136',
        'Rendah': '#2ECC40',
        'Cukup': '#0074D9',
        'Tinggi': '#FF851B',
        'Sangat Tinggi': '#B10DC9',
    }

    # Urutkan kategori dari sangat rendah hingga sangat tinggi
    kategori_terurut = ['Sangat Rendah', 'Rendah', 'Cukup', 'Tinggi', 'Sangat Tinggi']
    
    fig = go.Figure()

    # Tambahkan trace berdasarkan urutan kategori yang telah diurutkan
    for category in kategori_terurut:
        if category in df_plot['Kategori_Penjualan'].unique():
            category_data = df_plot[df_plot['Kategori_Penjualan'] == category]
            fig.add_trace(go.Scatter(
                x=category_data['x'],
                y=category_data['y'],
                mode='markers',
                marker=dict(size=8, color=color_map.get(category, 'grey'), opacity=0.7),
                text=category_data['Merek'] + ' - ' + category_data['Tipe'] + '<br>Kategori: ' + category +
                     '<br>Bulan: ' + category_data['Bulan'].astype(str) + '<br>Tahun: ' + category_data['Tahun'].astype(str),
                hoverinfo='text',
                name=category
            ))

    fig.update_layout(
        title=f'Visualisasi t-SNE Berdasarkan Kategori Penjualan {df["Toko"].iloc[0]} 2020 - 2024',
        xaxis_title='t-SNE Dimension 1',
        yaxis_title='t-SNE Dimension 2',
        legend_title='Kategori Penjualan',
        height=800,
        legend_traceorder="normal"  # Urutan legend mengikuti data
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
    
    df_plot = df[['Merek', 'Tipe', 'Kategori_Penjualan', 'Bulan', 'Tahun']].copy()
    df_plot['x'] = X_tsne[:, 0]
    df_plot['y'] = X_tsne[:, 1]
    df_plot['z'] = X_tsne[:, 2]
    df_plot['Cluster'] = clusters
    
    # Color map sesuai dengan kategori penjualan
    color_map = {
        'Sangat Rendah': '#FF4136',  # Warna merah
        'Rendah': '#2ECC40',         # Warna hijau
        'Cukup': '#0074D9',          # Warna biru
        'Tinggi': '#FF851B',         # Warna oranye
        'Sangat Tinggi': '#B10DC9',  # Warna ungu
    }
    
    fig = go.Figure()

    # Urutkan kategori dari "Sangat Rendah" hingga "Sangat Tinggi"
    kategori_terurut = ['Sangat Rendah', 'Rendah', 'Cukup', 'Tinggi', 'Sangat Tinggi']

    # Buat visualisasi untuk setiap kategori sesuai urutan
    for category in kategori_terurut:
        if category in df_plot['Kategori_Penjualan'].unique():
            category_data = df_plot[df_plot['Kategori_Penjualan'] == category]
            fig.add_trace(go.Scatter3d(
                x=category_data['x'],
                y=category_data['y'],
                z=category_data['z'],
                mode='markers',
                marker=dict(size=4, color=color_map[category], opacity=0.7),
                text=category_data['Merek'] + ' - ' + category_data['Tipe'] + '<br>Kategori: ' + category +
                     '<br>Bulan: ' + category_data['Bulan'].astype(str) + '<br>Tahun: ' + category_data['Tahun'].astype(str),
                hoverinfo='text',
                name=category
            ))

    fig.update_layout(
        title='Visualisasi 3D Berdasarkan Kategori Penjualan menggunakan t-SNE 2020 - 2024',
        scene=dict(
            xaxis_title='t-SNE Dimension 1',
            yaxis_title='t-SNE Dimension 2',
            zaxis_title='t-SNE Dimension 3',
        ),
        legend_title='Kategori Penjualan',
        height=800,
        margin=dict(r=20, b=10, l=10, t=40)
    )

    return fig


def visualize_tsne_per_tahun(df):
    features = ['Jumlah_Stok', 'Jumlah_Terjual', 'Persentase_Jumlah_Terjual']
    df_numeric = df[features].copy()
    df_numeric = df_numeric.fillna(df_numeric.median())
    X_normalized = (df_numeric.values - df_numeric.values.mean(axis=0)) / df_numeric.values.std(axis=0)

    tsne = TSNE(n_components=2, random_state=42)
    X_tsne = tsne.fit_transform(X_normalized)

    df['x'] = X_tsne[:, 0]
    df['y'] = X_tsne[:, 1]

    years = df['Tahun'].unique()
    rows = (len(years) + 1) // 2  # Atur baris berdasarkan jumlah tahun
    fig = make_subplots(
        rows=rows, cols=2,
        subplot_titles=[f"Tahun {year}" for year in years],
        vertical_spacing=0.1,
        horizontal_spacing=0.1
    )

    # Urutkan kategori dari "Sangat Rendah" hingga "Sangat Tinggi"
    kategori_terurut = ['Sangat Rendah', 'Rendah', 'Cukup', 'Tinggi', 'Sangat Tinggi']
    
    color_map = {
        'Sangat Rendah': '#FF4136',
        'Rendah': '#2ECC40',
        'Cukup': '#0074D9',
        'Tinggi': '#FF851B',
        'Sangat Tinggi': '#B10DC9',
    }

    # Track legend visibility untuk setiap kategori
    legend_visibility = {kategori: True for kategori in kategori_terurut}

    for i, year in enumerate(years):
        df_year = df[df['Tahun'] == year]
        row = (i // 2) + 1
        col = (i % 2) + 1

        for category in kategori_terurut:
            if category in df_year['Kategori_Penjualan'].unique():
                category_data = df_year[df_year['Kategori_Penjualan'] == category]
                fig.add_trace(go.Scatter(
                    x=category_data['x'],
                    y=category_data['y'],
                    mode='markers',
                    marker=dict(size=8, color=color_map.get(category, 'grey'), opacity=0.7),
                    text=category_data['Merek'] + ' - ' + category_data['Tipe'] + '<br>Kategori: ' + category +
                         '<br>Bulan: ' + category_data['Bulan'].astype(str) + '<br>Tahun: ' + category_data['Tahun'].astype(str),
                    hoverinfo='text',
                    name=category,
                    showlegend=legend_visibility[category]  # Tampilkan legend sekali untuk setiap kategori
                ), row=row, col=col)
                
                # Matikan legend setelah pertama kali muncul
                legend_visibility[category] = False

    fig.update_layout(
        title='Visualisasi t-SNE Berdasarkan Tahun',
        height=600 * rows,
        showlegend=True,  # Aktifkan legend
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)  # Letakkan legend di bawah grid
    )

    return fig




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

    # Warna berdasarkan kategori penjualan
    color_map = {
        'Sangat Rendah': '#FF4136',  # Merah
        'Rendah': '#2ECC40',         # Hijau
        'Cukup': '#0074D9',          # Biru
        'Tinggi': '#FF851B',         # Oranye
        'Sangat Tinggi': '#B10DC9',  # Ungu
    }

    # Urutkan kategori dari "Sangat Rendah" hingga "Sangat Tinggi"
    kategori_terurut = ['Sangat Rendah', 'Rendah', 'Cukup', 'Tinggi', 'Sangat Tinggi']

    # Track legend visibility untuk setiap kategori
    legend_visibility = {kategori: True for kategori in kategori_terurut}

    for i, merek in enumerate(merek_list[:rows*cols]):
        df_merek = df[df['Merek'] == merek]

        # Plot berdasarkan kategori penjualan dengan urutan yang benar
        for category in kategori_terurut:
            if category in df_merek['Kategori_Penjualan'].unique():
                category_data = df_merek[df_merek['Kategori_Penjualan'] == category]
                fig.add_trace(
                    go.Scatter(
                        x=category_data['x'], 
                        y=category_data['y'], 
                        mode='markers', 
                        marker=dict(size=6, color=color_map.get(category, 'grey'), opacity=0.7),
                        text=category_data['Tipe'] + '<br>Kategori: ' + category_data['Kategori_Penjualan'] +
                             '<br>Bulan: ' + category_data['Bulan'].astype(str) + '<br>Tahun: ' + category_data['Tahun'].astype(str),
                        hoverinfo='text',
                        name=category,
                        showlegend=legend_visibility[category]  # Tampilkan legend sekali untuk setiap kategori
                    ),
                    row=(i//cols)+1, col=(i%cols)+1
                )
                
                # Matikan legend setelah pertama kali muncul
                legend_visibility[category] = False

    fig.update_layout(
        title_text=f"Visualisasi t-SNE Berdasarkan Merek {df['Toko'].iloc[0]} 2020 - 2024",
        height=600 * rows,
        showlegend=True,  # Aktifkan legend
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)  # Letakkan legend di bawah grid
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
        IFNULL(data.Merek, '-') AS Merek,
        IFNULL(data.Tipe, '-') AS Tipe,
        IFNULL(data.Bulan, '-') AS Bulan,
        IFNULL(data.tahun, '-') AS Tahun,
        IFNULL(CAST(data.Jumlah_Stok AS DECIMAL(10,2)), 0) AS Jumlah_Stok,
        IFNULL(CAST(data.Jumlah_Terjual AS DECIMAL(10,2)), 0) AS Jumlah_Terjual,
        IFNULL(CAST(data.Harga_Satuan_Rp AS DECIMAL(15,2)), 0) AS Harga_Satuan_Rp,
        IFNULL(CAST((data.Jumlah_Terjual * data.Harga_Satuan_Rp) AS DECIMAL(20,2)), 0) AS total_penjualan,
        IFNULL(data.toko, '-') AS toko
    FROM data
    WHERE data.toko = %s
    """
    df = execute_query_to_dataframe(connection, query, (store,))

    if df is not None and not df.empty:
        # Konversi kolom numerik untuk memastikan penanganan sebagai float
        df['Jumlah_Stok'] = df['Jumlah_Stok'].astype(float)
        df['Jumlah_Terjual'] = df['Jumlah_Terjual'].astype(float)
        df['Harga_Satuan_Rp'] = df['Harga_Satuan_Rp'].astype(float)
        df['total_penjualan'] = df['total_penjualan'].astype(float)

        # Hanya kolom-kolom yang diperlukan
        columns_needed = ['Merek', 'Tipe', 'Jumlah_Stok', 'Jumlah_Terjual', 'Harga_Satuan_Rp', 'total_penjualan', 'Bulan', 'Tahun']
        df_klastering = df[columns_needed].copy()

        df_klastering['Persentase_Jumlah_Terjual'] = (df_klastering['Jumlah_Terjual'] / df_klastering['Jumlah_Stok']) * 100

        # Visualisasi dan clustering
        handle_missing_values(df_klastering)
        df_klastering['Kategori_Penjualan'] = df_klastering['Persentase_Jumlah_Terjual'].apply(categorize_sales_percentage)

        birch_model = Birch(n_clusters=5, threshold=0.5)
        df_features = df_klastering[['Jumlah_Stok', 'Jumlah_Terjual', 'Persentase_Jumlah_Terjual']]
        birch_model.fit(df_features)
        clusters = birch_model.predict(df_features)
        df_klastering['Cluster'] = clusters

        df_klastering['Toko'] = store

        # Visualisasi yang berbeda
        fig_sales_distribution = visualize_sales_distribution_combined(df_klastering)
        fig_clusters_tsne = visualize_clusters_tsne(df_klastering)
        fig_tsne_by_brand = visualize_tsne_by_brand(df_klastering, clusters)
        fig_clusters_3d = visualize_clusters_3d(df_klastering, clusters)
        fig_tsne_per_tahun = visualize_tsne_per_tahun(df_klastering)

        # Convert to JSON for rendering in HTML
        graphJSON_sales_distribution = json.dumps(fig_sales_distribution, cls=plotly.utils.PlotlyJSONEncoder)
        graphJSON_clusters_tsne = json.dumps(fig_clusters_tsne, cls=plotly.utils.PlotlyJSONEncoder)
        graphJSON_tsne_by_brand = json.dumps(fig_tsne_by_brand, cls=plotly.utils.PlotlyJSONEncoder)
        graphJSON_clusters_3d = json.dumps(fig_clusters_3d, cls=plotly.utils.PlotlyJSONEncoder)
        graphJSON_tsne_per_tahun = json.dumps(fig_tsne_per_tahun, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template('visualization.html',
                               graphJSON_sales_distribution=graphJSON_sales_distribution,
                               graphJSON_clusters_tsne=graphJSON_clusters_tsne,
                               graphJSON_tsne_by_brand=graphJSON_tsne_by_brand,
                               graphJSON_clusters_3d=graphJSON_clusters_3d,
                               graphJSON_tsne_per_tahun=graphJSON_tsne_per_tahun,
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

    query = f"""
    SELECT 
        IFNULL(data.Merek, '-') AS Merek,
        IFNULL(data.Tipe, '-') AS Tipe,
        IFNULL(data.Bulan, '-') AS Bulan,
        IFNULL(data.tahun, '-') AS Tahun,
        IFNULL(CAST(data.Jumlah_Stok AS DECIMAL(10,2)), 0) AS Jumlah_Stok,
        IFNULL(CAST(data.Jumlah_Terjual AS DECIMAL(10,2)), 0) AS Jumlah_Terjual,
        IFNULL(CAST(data.Harga_Satuan_Rp AS DECIMAL(15,2)), 0) AS Harga_Satuan_Rp,
        IFNULL(CAST((data.Jumlah_Terjual * data.Harga_Satuan_Rp) AS DECIMAL(20,2)), 0) AS total_penjualan,
        IFNULL(data.toko, '-') AS toko
    FROM data
    WHERE data.toko = %s
    """
    
    connection = get_db_connection()
    if connection and connection.is_connected():
        df = execute_query_to_dataframe(connection, query, (store_name,))
        print(len(df))
        if df is not None and not df.empty:
            # Konversi kolom numerik untuk memastikan penanganan sebagai float
            df['Jumlah_Stok'] = df['Jumlah_Stok'].astype(float)
            df['Jumlah_Terjual'] = df['Jumlah_Terjual'].astype(float)
            df['Harga_Satuan_Rp'] = df['Harga_Satuan_Rp'].astype(float)
            df['total_penjualan'] = df['total_penjualan'].astype(float)
            df['Persentase_Jumlah_Terjual'] = (df['Jumlah_Terjual'] / df['Jumlah_Stok']) * 100
            df['Kategori_Penjualan'] = df['Persentase_Jumlah_Terjual'].apply(categorize_sales_percentage)
            
            df = perform_clustering(df, threshold)
            
            response_data = df[['Merek', 'Tipe', 'Bulan', 'Persentase_Jumlah_Terjual', 'Kategori_Penjualan', 'Cluster', 'Tahun']].to_dict(orient='records')
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

    # Extract data from request
    data_spec = data.get('dataSpesifikasi')
    data_penjualan = data.get('dataPenjualan')

    # Validate incoming data
    if not data_spec or not data_penjualan:
        return jsonify({'status': 'error', 'message': 'Specification and sales data are required'}), 400

    connection = get_db_connection()

    if connection and connection.is_connected():
        cursor = connection.cursor()

        try:
            # Handle Kamera_Utama_MP
            if isinstance(data_spec['Kamera_Utama'], str):
                kamera_utama = int(data_spec['Kamera_Utama'].replace(' MP', '').strip())
            else:
                kamera_utama = int(data_spec['Kamera_Utama'])

            # Handle Kamera_Depan_MP
            if isinstance(data_spec['Kamera_Depan'], str):
                kamera_depan = int(data_spec['Kamera_Depan'].replace(' MP', '').strip())
            else:
                kamera_depan = int(data_spec['Kamera_Depan'])

            # Handle Baterai_mAh
            if isinstance(data_spec['Baterai'], str):
                baterai = int(data_spec['Baterai'].replace(' mAh', '').strip())
            else:
                baterai = int(data_spec['Baterai'])

            # Insert into data_spesifikasi table
            cursor.execute("""
                INSERT INTO data_spesifikasi (Merek, Tipe, Kamera_Utama_MP, Kamera_Depan_MP, RAM, Memori_Internal, Baterai_mAh, Jenis_Layar)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data_spec['Merek'],
                data_spec['Tipe'],
                kamera_utama,  # Cleaned value
                kamera_depan,  # Cleaned value
                data_spec['RAM'],
                data_spec['Memori_Internal'],
                baterai,  # Cleaned value
                data_spec['Jenis_Layar']
            ))

            # Insert into data table
            cursor.execute("""
                INSERT INTO data (toko, Merek, Tipe, Bulan, tahun, Jumlah_Stok, Jumlah_Terjual, Harga_Satuan_Rp, Total_Penjualan_Rp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data_penjualan['toko'],  # Toko dimasukkan dari data_penjualan
                data_spec['Merek'],
                data_spec['Tipe'],
                data_penjualan['Bulan'],
                int(data_penjualan['Tahun']),
                int(data_penjualan['Stok']),
                int(data_penjualan['Unit_Terjual']),
                int(data_penjualan['Harga_Satuan']),
                int(data_penjualan['Total_Penjualan'])
            ))

            # Commit the transaction
            connection.commit()

            return jsonify({'status': 'success'}), 200

        except Exception as e:
            # Rollback the transaction if there's an error
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
        IFNULL(data.toko, '-') AS Toko,
        IFNULL(data.Merek, '-') AS Merek,
        IFNULL(data.Tipe, '-') AS Tipe,
        IFNULL(data.Bulan, '-') AS Bulan,
        IFNULL(data.tahun, '-') AS Tahun,
        IFNULL(CAST(data.Jumlah_Stok AS DECIMAL(10,2)), 0) AS Jumlah_Stok,
        IFNULL(CAST(data.Jumlah_Terjual AS DECIMAL(10,2)), 0) AS Jumlah_Terjual,
        IFNULL(CAST(data.Harga_Satuan_Rp AS DECIMAL(15,2)), 0) AS Harga_Satuan_Rp,
        IFNULL(CAST((data.Jumlah_Terjual * data.Harga_Satuan_Rp) AS DECIMAL(20,2)), 0) AS Total_Penjualan_Rp,
        IFNULL(CAST(data_spesifikasi.Kamera_Utama_MP AS DECIMAL(5,2)), 0) AS Kamera_Utama_MP,
        IFNULL(CAST(data_spesifikasi.Kamera_Depan_MP AS DECIMAL(5,2)), 0) AS Kamera_Depan_MP,
        IFNULL(data_spesifikasi.RAM, '-') AS RAM,
        IFNULL(data_spesifikasi.Memori_Internal, '-') AS Memori_Internal,
        IFNULL(CAST(data_spesifikasi.Baterai_mAh AS DECIMAL(10,2)), 0) AS Baterai_mAh,
        IFNULL(data_spesifikasi.Jenis_Layar, '-') AS Jenis_Layar
    FROM 
        data
    LEFT JOIN 
        data_spesifikasi 
    ON 
        data.Tipe = data_spesifikasi.Tipe and data.Merek = data_spesifikasi.Merek
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
        jumlah_data = len(df)
        
        # Ganti NaN dengan angka 0 atau string "-" sesuai dengan jenis datanya
        df = df.fillna(value={
            'Jumlah_Stok': 0,
            'Jumlah_Terjual': 0,
            'Harga_Satuan_Rp': 0,
            'Total_Penjualan_Rp': 0,
            'Kamera_Utama_MP': 0,
            'Kamera_Depan_MP': 0,
            'RAM': '-',
            'Memori_Internal': '-',
            'Baterai_mAh': 0,
            'Jenis_Layar': '-'
        })

        # Bangun objek JSON dengan key unik
        data = {}
        for _, row in df.iterrows():
            key = f"{row['Merek']}_{row['Tipe']}_{row['Bulan']}_{row['Tahun']}_{row['Toko']}"
            data[key] = {
                "Merek": row["Merek"],
                "Tipe": row["Tipe"],
                "Bulan": row["Bulan"],
                "Tahun": int(row["Tahun"]),
                "Jumlah_Stok": float(row["Jumlah_Stok"]),
                "Jumlah_Terjual": float(row["Jumlah_Terjual"]),
                "Harga_Satuan_Rp": float(row["Harga_Satuan_Rp"]),
                "Total_Penjualan_Rp": float(row["Total_Penjualan_Rp"]),
                "Toko": row["Toko"],
                "Kamera_Utama_MP": float(row["Kamera_Utama_MP"]),
                "Kamera_Depan_MP": float(row["Kamera_Depan_MP"]),
                "RAM": row["RAM"],
                "Memori_Internal": row["Memori_Internal"],
                "Baterai_mAh": float(row["Baterai_mAh"]),
                "Jenis_Layar": row["Jenis_Layar"]
            }
        # print(len(data))
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
