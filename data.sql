-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               10.4.24-MariaDB - mariadb.org binary distribution
-- Server OS:                    Win64
-- HeidiSQL Version:             12.0.0.6532
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- Dumping structure for table smartphone_data.data
CREATE TABLE IF NOT EXISTS `data` (
  `No` int(11) NOT NULL,
  `Merek` varchar(255) DEFAULT NULL,
  `Tipe` varchar(255) DEFAULT NULL,
  `Bulan` varchar(50) DEFAULT NULL,
  `Jumlah_Stok` int(11) DEFAULT NULL,
  `Jumlah_Terjual` int(11) DEFAULT NULL,
  `Harga_Satuan_Rp` int(11) DEFAULT NULL,
  `Total_Penjualan_Rp` int(11) DEFAULT NULL,
  PRIMARY KEY (`No`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Dumping data for table smartphone_data.data: ~50 rows (approximately)
INSERT INTO `data` (`No`, `Merek`, `Tipe`, `Bulan`, `Jumlah_Stok`, `Jumlah_Terjual`, `Harga_Satuan_Rp`, `Total_Penjualan_Rp`) VALUES
	(1, 'Samsung', 'Galaxy S21', 'Jan', 10, 8, 10000000, 80000000),
	(2, 'Samsung', 'Galaxy S21', 'Feb', 9, 7, 10000000, 70000000),
	(3, 'Samsung', 'Galaxy S21', 'Mar', 8, 6, 10000000, 60000000),
	(4, 'Samsung', 'Galaxy S21', 'Apr', 7, 5, 10000000, 50000000),
	(5, 'Samsung', 'Galaxy S21', 'May', 6, 4, 10000000, 40000000),
	(6, 'Samsung', 'Galaxy S21', 'Jun', 5, 3, 10000000, 30000000),
	(7, 'Apple', 'iPhone 13', 'Jan', 15, 12, 15000000, 180000000),
	(8, 'Apple', 'iPhone 13', 'Feb', 13, 10, 15000000, 150000000),
	(9, 'Apple', 'iPhone 13', 'Mar', 12, 9, 15000000, 135000000),
	(10, 'Apple', 'iPhone 13', 'Apr', 11, 8, 15000000, 120000000),
	(11, 'Apple', 'iPhone 13', 'May', 10, 7, 15000000, 105000000),
	(12, 'Apple', 'iPhone 13', 'Jun', 9, 6, 15000000, 90000000),
	(13, 'Xiaomi', 'Redmi Note 10', 'Jan', 20, 15, 5000000, 75000000),
	(14, 'Xiaomi', 'Redmi Note 10', 'Feb', 18, 14, 5000000, 70000000),
	(15, 'Xiaomi', 'Redmi Note 10', 'Mar', 16, 13, 5000000, 65000000),
	(16, 'Xiaomi', 'Redmi Note 10', 'Apr', 15, 12, 5000000, 60000000),
	(17, 'Xiaomi', 'Redmi Note 10', 'May', 14, 11, 5000000, 55000000),
	(18, 'Xiaomi', 'Redmi Note 10', 'Jun', 12, 10, 5000000, 50000000),
	(19, 'Oppo', 'Reno 5', 'Jan', 10, 7, 8000000, 56000000),
	(20, 'Oppo', 'Reno 5', 'Feb', 9, 6, 8000000, 48000000),
	(21, 'Oppo', 'Reno 5', 'Mar', 8, 5, 8000000, 40000000),
	(22, 'Oppo', 'Reno 5', 'Apr', 7, 4, 8000000, 32000000),
	(23, 'Oppo', 'Reno 5', 'May', 6, 3, 8000000, 24000000),
	(24, 'Oppo', 'Reno 5', 'Jun', 5, 2, 8000000, 16000000),
	(25, 'Vivo', 'V21', 'Jan', 12, 9, 6000000, 54000000),
	(26, 'Vivo', 'V21', 'Feb', 11, 8, 6000000, 48000000),
	(27, 'Vivo', 'V21', 'Mar', 10, 7, 6000000, 42000000),
	(28, 'Vivo', 'V21', 'Apr', 9, 6, 6000000, 36000000),
	(29, 'Vivo', 'V21', 'May', 8, 5, 6000000, 30000000),
	(30, 'Vivo', 'V21', 'Jun', 7, 4, 6000000, 24000000),
	(31, 'Realme', '8 Pro', 'Jan', 18, 15, 7000000, 105000000),
	(32, 'Realme', '8 Pro', 'Feb', 16, 13, 7000000, 91000000),
	(33, 'Realme', '8 Pro', 'Mar', 15, 12, 7000000, 84000000),
	(34, 'Realme', '8 Pro', 'Apr', 13, 11, 7000000, 77000000),
	(35, 'Realme', '8 Pro', 'May', 12, 10, 7000000, 70000000),
	(36, 'Realme', '8 Pro', 'Jun', 11, 9, 7000000, 63000000),
	(37, 'Asus', 'ROG Phone 5', 'Jan', 5, 4, 12000000, 48000000),
	(38, 'Asus', 'ROG Phone 5', 'Feb', 5, 4, 12000000, 48000000),
	(39, 'Asus', 'ROG Phone 5', 'Mar', 4, 3, 12000000, 36000000),
	(40, 'Asus', 'ROG Phone 5', 'Apr', 4, 3, 12000000, 36000000),
	(41, 'Asus', 'ROG Phone 5', 'May', 3, 2, 12000000, 24000000),
	(42, 'Asus', 'ROG Phone 5', 'Jun', 3, 2, 12000000, 24000000),
	(43, 'Huawei', 'P40 Pro', 'Jan', 7, 5, 11000000, 55000000),
	(44, 'Huawei', 'P40 Pro', 'Feb', 7, 5, 11000000, 55000000),
	(45, 'Huawei', 'P40 Pro', 'Mar', 6, 4, 11000000, 44000000),
	(46, 'Huawei', 'P40 Pro', 'Apr', 6, 4, 11000000, 44000000),
	(47, 'Huawei', 'P40 Pro', 'May', 5, 3, 11000000, 33000000),
	(48, 'Huawei', 'P40 Pro', 'Jun', 5, 3, 11000000, 33000000),
	(49, 'Lenovo', 'Legion Phone', 'Jan', 10, 8, 9000000, 72000000),
	(50, 'Lenovo', 'Legion Phone', 'Feb', 9, 7, 9000000, 63000000);

-- Dumping structure for table smartphone_data.data_spesifikasi
CREATE TABLE IF NOT EXISTS `data_spesifikasi` (
  `No` int(11) NOT NULL,
  `Merek` varchar(255) DEFAULT NULL,
  `Tipe` varchar(255) DEFAULT NULL,
  `Kamera_Utama_MP` int(11) DEFAULT NULL,
  `Kamera_Depan_MP` int(11) DEFAULT NULL,
  `RAM` varchar(50) DEFAULT NULL,
  `Memori_Internal` varchar(50) DEFAULT NULL,
  `Baterai_mAh` int(11) DEFAULT NULL,
  `Jenis_Layar` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`No`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Dumping data for table smartphone_data.data_spesifikasi: ~9 rows (approximately)
INSERT INTO `data_spesifikasi` (`No`, `Merek`, `Tipe`, `Kamera_Utama_MP`, `Kamera_Depan_MP`, `RAM`, `Memori_Internal`, `Baterai_mAh`, `Jenis_Layar`) VALUES
	(1, 'Samsung', 'Galaxy S21', 64, 10, '8GB', '128GB', 4000, 'Dynamic AMOLED'),
	(2, 'Apple', 'iPhone 13', 12, 12, '4GB', '128GB', 3240, 'Super Retina XDR'),
	(3, 'Xiaomi', 'Redmi Note 10', 48, 13, '6GB', '64GB', 5000, 'AMOLED'),
	(4, 'Oppo', 'Reno 5', 64, 44, '8GB', '128GB', 4310, 'AMOLED'),
	(5, 'Vivo', 'V21', 64, 44, '8GB', '128GB', 4000, 'AMOLED'),
	(6, 'Realme', '8 Pro', 108, 16, '8GB', '128GB', 4500, 'Super AMOLED'),
	(7, 'Asus', 'ROG Phone 5', 64, 24, '16GB', '256GB', 6000, 'AMOLED'),
	(8, 'Huawei', 'P40 Pro', 50, 32, '8GB', '256GB', 4200, 'OLED'),
	(9, 'Lenovo', 'Legion Phone', 64, 20, '12GB', '256GB', 5000, 'AMOLED');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
