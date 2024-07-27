import mysql.connector
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, clear_output
from matplotlib.animation import FuncAnimation
from sklearn.metrics import silhouette_score
from sklearn.cluster import Birch  # Pastikan Anda mengimpor Birch

# Connection details
host = 'localhost'
user = 'root'
password = ''
database = 'data_smartphone'
port = 3306

# Establish a connection to the database
connection = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database,
    port=port
)

print("Koneksi ke database berhasil")

def execute_query_to_dataframe(connection, query):
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchall()
        df = pd.DataFrame(result)
        return df
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        cursor.close()

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
    data.Tipe = data_spesifikasi.Tipe;
"""

if connection.is_connected():
    df = execute_query_to_dataframe(connection, query)
    if df is not None and not df.empty:

        # Menghitung persentase jumlah terjual dibandingkan dengan jumlah stok
        df['Persentase_Jumlah_Terjual'] = (df['Jumlah_Terjual'] / df['Jumlah_Stok']) * 100

        # Definisi kategori berdasarkan persentase penjualan
        def categorize_sales_percentage(percent_sold):
            if percent_sold < 20:
                return 'Sangat Rendah'
            elif percent_sold < 40:
                return 'Rendah'
            elif percent_sold < 50:
                return 'Cukup'
            elif percent_sold < 80:
                return 'Tinggi'
            else:
                return 'Sangat Tinggi'

        df['Kategori_Penjualan'] = df['Persentase_Jumlah_Terjual'].apply(categorize_sales_percentage)

        # Generating random centroids
        np.random.seed(42)  # Ensure reproducibility
        df['Centroid_X'] = np.random.uniform(1, 7, size=len(df))
        df['Centroid_Y'] = np.random.uniform(1, 7, size=len(df))

        # Color mapping based on sales categories
        colors = {
            'Sangat Rendah': 'black',
            'Rendah': 'green',
            'Cukup': 'yellow',
            'Tinggi': 'grey',
            'Sangat Tinggi': 'red'
        }

        # Initialize plot
        fig, ax = plt.subplots(figsize=(10, 8))
        scatter = ax.scatter(df['Centroid_X'], df['Centroid_Y'], c=df['Kategori_Penjualan'].apply(lambda x: colors[x]), alpha=0.6)

        ax.set_title('Pemisahan Data Berdasarkan Kategori Penjualan (Iterasi 0)')
        ax.set_xlabel('Nilai X')
        ax.set_ylabel('Nilai Y')
        plt.tight_layout()

        def update_plot(frame):
            global df, iterasi, best_silhouette, best_df

            # Update clustering using Birch
            birch_model = Birch(n_clusters=None, threshold=0.5)
            birch_model.fit(df[['Jumlah_Stok', 'Jumlah_Terjual', 'Harga_Satuan_Rp', 'Persentase_Jumlah_Terjual']])
            clusters = birch_model.predict(df[['Jumlah_Stok', 'Jumlah_Terjual', 'Harga_Satuan_Rp', 'Persentase_Jumlah_Terjual']])
            df['Cluster'] = clusters

            silhouette_avg = silhouette_score(df[['Jumlah_Stok', 'Jumlah_Terjual', 'Harga_Satuan_Rp', 'Persentase_Jumlah_Terjual']], clusters)

            if silhouette_avg > best_silhouette:
                best_silhouette = silhouette_avg
                best_df = df.copy()

            # Update centroids dynamically based on changes in clusters or data
            for category, color in colors.items():
                subset = df[df['Kategori_Penjualan'] == category]
                if len(subset['Centroid_X'].unique()) > 1 or len(subset['Centroid_Y'].unique()) > 1:
                    df.loc[subset.index, 'Centroid_X'] = np.random.uniform(subset['Centroid_X'].min() - 1, subset['Centroid_X'].max() + 1, size=len(subset))
                    df.loc[subset.index, 'Centroid_Y'] = np.random.uniform(subset['Centroid_Y'].min() - 1, subset['Centroid_Y'].max() + 1, size=len(subset))

            # Print and save best result every 4 iterations
            if iterasi % 4 == 0:
                clear_output(wait=True)
                print(f"Iterasi {iterasi}: Silhouette Score = {best_silhouette:.6f}")

            iterasi += 1
            ax.clear()
            scatter = ax.scatter(df['Centroid_X'], df['Centroid_Y'], c=df['Kategori_Penjualan'].apply(lambda x: colors[x]), alpha=0.6)
            ax.set_title(f'Pemisahan Data Berdasarkan Kategori Penjualan (Iterasi {iterasi}, Silhouette Score: {silhouette_avg:.2f})')
            ax.set_xlabel('Nilai X')
            ax.set_ylabel('Nilai Y')

            return scatter,

        iterasi = 0
        best_silhouette = -1
        best_df = pd.DataFrame()

        ani = FuncAnimation(fig, update_plot, frames=100, interval=500, blit=True, cache_frame_data=False)  # Tentukan jumlah frame

        plt.show()
    else:
        print("No data found or query eclsxecution failed.")
else:
    print("No connection to the database.")
