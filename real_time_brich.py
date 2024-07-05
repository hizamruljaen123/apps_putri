import mysql.connector
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, clear_output
from matplotlib.animation import FuncAnimation
from sklearn.cluster import Birch, KMeans
from sklearn.metrics import silhouette_score

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

        def classify_sales(row):
            if row['Jumlah_Terjual'] <= 2:
                return 'Sangat Rendah'
            elif row['Jumlah_Terjual'] <= 5:
                return 'Rendah'
            elif row['Jumlah_Terjual'] <= 10:
                return 'Cukup'
            elif row['Jumlah_Terjual'] <= 20:
                return 'Berpotensi Tinggi'
            elif row['Jumlah_Terjual'] <= 50:
                return 'Tinggi'
            else:
                return 'Sangat Tinggi'

        df['Kategori_Penjualan'] = df.apply(classify_sales, axis=1)

        # Generating random centroids
        np.random.seed(42)  # Ensure reproducibility
        df['Centroid_X'] = np.random.uniform(1, 7, size=len(df))
        df['Centroid_Y'] = np.random.uniform(1, 7, size=len(df))

        # Color mapping based on sales categories
        colors = {
            'Sangat Rendah': 'blue',
            'Rendah': 'green',
            'Cukup': 'yellow',
            'Berpotensi Tinggi': 'orange',
            'Tinggi': 'red',
            'Sangat Tinggi': 'purple'
        }

        # Initialize plot
        fig, ax = plt.subplots(figsize=(10, 8))
        scatter = ax.scatter(df['Centroid_X'], df['Centroid_Y'], c=df['Kategori_Penjualan'].apply(lambda x: colors[x]), alpha=0.6)

        ax.set_title('Pemisahan Data Berdasarkan Kategori Penjualan (Iterasi 0)')
        ax.set_xlabel('Nilai X')
        ax.set_ylabel('Nilai Y')
        plt.tight_layout()

        # Initialize K-Means for initial centroids
        kmeans = KMeans(n_clusters=6, n_init='auto')
        initial_centroids = kmeans.fit(df[['Centroid_X', 'Centroid_Y']])
        df['Cluster'] = initial_centroids.labels_

        def update_plot(frame):
            global df, iterasi, terpisah, best_silhouette, best_df

            terpisah = True
            for category, color in colors.items():
                subset = df[df['Kategori_Penjualan'] == category]
                if len(subset['Centroid_X'].unique()) > 1 or len(subset['Centroid_Y'].unique()) > 1:
                    terpisah = False
                    df.loc[subset.index, 'Centroid_X'] = np.random.uniform(subset['Centroid_X'].min() - 1, subset['Centroid_X'].max() + 1, size=len(subset))
                    df.loc[subset.index, 'Centroid_Y'] = np.random.uniform(subset['Centroid_Y'].min() - 1, subset['Centroid_Y'].max() + 1, size=len(subset))

            # Update clustering using Birch
            birch_model = Birch(n_clusters=None, threshold=0.5)
            birch_model.fit(df[['Centroid_X', 'Centroid_Y']])
            clusters = birch_model.predict(df[['Centroid_X', 'Centroid_Y']])
            df['Cluster'] = clusters

            silhouette_avg = silhouette_score(df[['Centroid_X', 'Centroid_Y']], clusters)

            if silhouette_avg > best_silhouette:
                best_silhouette = silhouette_avg
                best_df = df.copy()

            if iterasi % 5 == 0:
                clear_output(wait=True)
                print(f"Iterasi {iterasi}: Silhouette Score = {best_silhouette:.6f}")

            iterasi += 1
            ax.clear()
            scatter = ax.scatter(df['Centroid_X'], df['Centroid_Y'], c=df['Kategori_Penjualan'].apply(lambda x: colors[x]), alpha=0.6)
            ax.set_title(f'Pemisahan Data Berdasarkan Kategori Penjualan (Iterasi {iterasi}, Silhouette Score: {silhouette_avg:.2f})')
            ax.set_xlabel('Nilai X')
            ax.set_ylabel('Nilai Y')

            return scatter,

        terpisah = False
        iterasi = 0
        best_silhouette = -1
        best_df = pd.DataFrame()

        ani = FuncAnimation(fig, update_plot, interval=500, blit=True)

        plt.show()
    else:
        print("No data found or query execution failed.")
else:
    print("No connection to the database.")
