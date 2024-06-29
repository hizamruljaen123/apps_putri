import pandas as pd

# Buat dataframe dengan kolom yang sesuai
columns = ["No", "Merek", "Tipe", "Kamera Utama (MP)", "Kamera Depan (MP)", "RAM", "Memori Internal", "Baterai (mAh)", "Jenis Layar"]

# Data spesifikasi smartphone
first_50_smartphones = [
    (1, "Oppo", "Reno11 F", 50, 32, "8GB", "128GB", 4300, "AMOLED"),
    (2, "Oppo", "Reno11 Pro", 64, 44, "12GB", "256GB", 4500, "AMOLED"),
    (3, "Oppo", "Reno11", 64, 32, "8GB", "128GB", 4300, "AMOLED"),
    (4, "Oppo", "A79", 48, 16, "6GB", "128GB", 5000, "IPS LCD"),
    (5, "Oppo", "A18", 50, 8, "4GB", "64GB", 5000, "IPS LCD"),
    (6, "Oppo", "A60", 50, 8, "6GB", "128GB", 5000, "IPS LCD"),
    (7, "Oppo", "A38", 50, 8, "4GB", "64GB", 5000, "IPS LCD"),
    (8, "Oppo", "A58", 50, 16, "6GB", "128GB", 5000, "IPS LCD"),
    (9, "Oppo", "A77s", 50, 16, "8GB", "128GB", 5000, "IPS LCD"),
    (10, "Oppo", "A58 NFC", 50, 16, "6GB", "128GB", 5000, "IPS LCD"),
    (11, "Oppo", "Reno8", 64, 32, "8GB", "128GB", 4500, "AMOLED"),
    (12, "Oppo", "A98", 50, 16, "8GB", "128GB", 5000, "IPS LCD"),
    (13, "Oppo", "A17", 50, 8, "4GB", "64GB", 5000, "IPS LCD"),
    (14, "Oppo", "A78", 50, 16, "6GB", "128GB", 5000, "IPS LCD"),
    (15, "Oppo", "A96", 50, 16, "8GB", "128GB", 5000, "IPS LCD"),
    (16, "Oppo", "Reno10", 64, 32, "8GB", "128GB", 4500, "AMOLED"),
    (17, "Oppo", "Reno10 Pro", 64, 44, "12GB", "256GB", 4500, "AMOLED"),
    (18, "Oppo", "Reno10 Plus", 64, 44, "12GB", "256GB", 4500, "AMOLED"),
    (19, "Vivo", "Y28", 50, 8, "4GB", "64GB", 5000, "IPS LCD"),
    (20, "Vivo", "Y17s", 50, 8, "4GB", "64GB", 5000, "IPS LCD"),
    (21, "Vivo", "Y22", 50, 8, "4GB", "64GB", 5000, "IPS LCD"),
    (22, "Vivo", "V29e", 64, 32, "8GB", "128GB", 4500, "AMOLED"),
    (23, "Vivo", "Y35", 50, 16, "6GB", "128GB", 5000, "IPS LCD"),
    (24, "Vivo", "V29", 64, 32, "8GB", "128GB", 4500, "AMOLED"),
    (25, "Vivo", "Y100", 50, 16, "6GB", "128GB", 5000, "IPS LCD"),
    (26, "Vivo", "Y36", 50, 16, "6GB", "128GB", 5000, "IPS LCD"),
    (27, "Vivo", "Y18", 50, 8, "4GB", "64GB", 5000, "IPS LCD"),
    (28, "Vivo", "Y27", 50, 8, "4GB", "64GB", 5000, "IPS LCD"),
    (29, "Vivo", "Y03", 50, 8, "3GB", "32GB", 5000, "IPS LCD"),
    (30, "Vivo", "Y02t", 50, 8, "3GB", "32GB", 5000, "IPS LCD"),
    (31, "Vivo", "V30", 64, 32, "8GB", "128GB", 4500, "AMOLED"),
    (32, "Vivo", "V30e", 64, 32, "8GB", "128GB", 4500, "AMOLED"),
    (33, "Vivo", "X100 Pro", 64, 44, "12GB", "256GB", 4500, "AMOLED"),
    (34, "Vivo", "X100", 64, 32, "12GB", "256GB", 4500, "AMOLED"),
    (35, "Vivo", "Y33s", 50, 16, "6GB", "128GB", 5000, "IPS LCD"),
    (36, "Samsung", "Galaxy A05", 50, 8, "4GB", "64GB", 5000, "IPS LCD"),
    (37, "Samsung", "Galaxy A15", 50, 8, "4GB", "64GB", 5000, "IPS LCD"),
    (38, "Samsung", "Galaxy A05s", 50, 8, "4GB", "64GB", 5000, "IPS LCD"),
    (39, "Samsung", "Galaxy A55", 50, 16, "6GB", "128GB", 5000, "IPS LCD"),
    (40, "Samsung", "Galaxy A35", 50, 8, "4GB", "64GB", 5000, "IPS LCD"),
    (41, "Samsung", "Galaxy A54", 50, 16, "6GB", "128GB", 5000, "IPS LCD"),
    (42, "Samsung", "Galaxy A25", 50, 8, "4GB", "64GB", 5000, "IPS LCD"),
    (43, "Samsung", "Galaxy A23", 50, 16, "6GB", "128GB", 5000, "IPS LCD"),
    (44, "Samsung", "Galaxy A34", 50, 16, "6GB", "128GB", 5000, "IPS LCD"),
    (45, "Samsung", "Galaxy M54", 64, 32, "8GB", "128GB", 6000, "Super AMOLED"),
    (46, "Samsung", "Galaxy S23 Fe", 50, 32, "8GB", "128GB", 4500, "Dynamic AMOLED"),
    (47, "Samsung", "Galaxy S23", 50, 32, "8GB", "128GB", 4500, "Dynamic AMOLED"),
    (48, "Samsung", "Galaxy S23 Ultra", 108, 40, "12GB", "256GB", 5000, "Dynamic AMOLED"),
    (49, "Samsung", "Galaxy S24 Ultra", 200, 40, "16GB", "512GB", 5000, "Dynamic AMOLED"),
    (50, "Samsung", "Galaxy S24", 108, 32, "12GB", "256GB", 4500, "Dynamic AMOLED")
]

# Convert list to DataFrame
new_data = pd.DataFrame(first_50_smartphones, columns=columns)

# Save to Excel
output_path = 'data_spesifikasi_updated.xlsx'
new_data.to_excel(output_path, index=False)

print(f"Data saved to {output_path}")
