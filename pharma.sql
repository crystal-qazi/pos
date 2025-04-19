-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               8.0.30 - MySQL Community Server - GPL
-- Server OS:                    Win64
-- HeidiSQL Version:             12.1.0.6537
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- Dumping data for table pharma.issued_items: ~0 rows (approximately)
DELETE FROM `issued_items`;

-- Dumping data for table pharma.items: ~10 rows (approximately)
DELETE FROM `items`;
INSERT INTO `items` (`item_id`, `item_code`, `item_name`, `category`, `unit`, `stock_quantity`, `reorder_level`, `batch_no`, `expiry_date`, `purchase_price`, `selling_price`, `created_at`) VALUES
	(1, 'TAB-001', 'Paracetamol 500mg', 'Tablet', 'Piece', 5, 10, 'B202401', '2026-05-15', 2.50, 5.00, '2025-02-08 13:18:28'),
	(2, 'TAB-002', 'Ibuprofen 200mg', 'Tablet', 'Piece', 80, 10, 'B202402', '2025-12-10', 3.00, 6.00, '2025-02-08 13:18:28'),
	(3, 'INJ-001', 'Ceftriaxone 1g', 'Injection', 'Vial', 50, 5, 'B202403', '2025-09-30', 15.00, 30.00, '2025-02-08 13:18:28'),
	(4, 'SYR-001', 'Cough Syrup 100ml', 'Syrup', 'Bottle', 60, 10, 'B202404', '2025-11-20', 10.00, 18.00, '2025-02-08 13:18:28'),
	(5, 'CAP-001', 'Amoxicillin 500mg', 'Capsule', 'Piece', 66, 10, 'B202405', '2026-07-12', 4.50, 9.00, '2025-02-08 13:18:28'),
	(6, 'OINT-001', 'Mupirocin 2% Ointment', 'Ointment', 'Tube', 30, 5, 'B202406', '2025-08-25', 7.00, 14.00, '2025-02-08 13:18:28'),
	(7, 'MISC-001', 'Vitamin C Chewable', 'Misc', 'Pack', 39, 5, 'B202407', '2026-01-15', 5.00, 10.00, '2025-02-08 13:18:28'),
	(8, 'TAB-003', 'Aspirin 75mg', 'Tablet', 'Piece', 41, 10, 'B202408', '2025-10-05', 2.00, 4.50, '2025-02-08 13:18:28'),
	(9, 'INJ-002', 'Insulin 10ml', 'Injection', 'Vial', 30, 5, 'B202409', '2025-12-31', 25.00, 50.00, '2025-02-08 13:18:28'),
	(10, 'SYR-002', 'Multivitamin Syrup 150ml', 'Syrup', 'Bottle', 50, 10, 'B202410', '2026-03-22', 8.50, 16.00, '2025-02-08 13:18:28');

-- Dumping data for table pharma.ledger: ~0 rows (approximately)
DELETE FROM `ledger`;

-- Dumping data for table pharma.orders: ~13 rows (approximately)
DELETE FROM `orders`;
INSERT INTO `orders` (`order_id`, `order_uuid`, `visit_id`, `order_number`, `order_status`, `created_date`) VALUES
	(131, 'e70daf8b-1d2e-11f0-b6be-f079595cf759', 74, 'o20250001', 'Complete', NULL);

-- Dumping data for table pharma.order_detail: ~15 rows (approximately)
DELETE FROM `order_detail`;
INSERT INTO `order_detail` (`oitem_id`, `order_id`, `item_code`, `oitem_name`, `qty`, `selling_price`, `Column 7`, `Column 4`) VALUES
	(82, 131, 'TAB-001', 'Paracetamol 500mg', 1, 5, NULL, NULL),
	(83, 131, 'TAB-003', 'Aspirin 75mg', 1, 4.5, NULL, NULL);

-- Dumping data for table pharma.patients: ~4 rows (approximately)
DELETE FROM `patients`;
INSERT INTO `patients` (`patient_id`, `p_uuid`, `MRN`, `first_name`, `last_name`, `age`, `created_at`, `cnic`, `Mobile`, `address`) VALUES
	(19, 'uuid()', 'A2025-1804-0001', 'Azeem', 'Khalil', 34, '2025-04-18 12:59:24', 12345, 3453151738, NULL),
	(20, 'uuid()', 'A2025-1904-0001', 'Adnan', 'Ahmed', 55, '2025-04-19 05:05:17', 123, 3450000000, NULL),
	(21, 'uuid()', 'A2025-1904-0002', 'Danish', 'Khan', 34, '2025-04-19 05:22:23', 3450000000, 923453151738, NULL),
	(22, 'uuid()', 'A2025-1904-0003', 'Zia', 'uddin', 35, '2025-04-19 05:38:23', 12345, 12345, NULL);

-- Dumping data for table pharma.patient_bills: ~0 rows (approximately)
DELETE FROM `patient_bills`;

-- Dumping data for table pharma.patient_visit: ~14 rows (approximately)
DELETE FROM `patient_visit`;
INSERT INTO `patient_visit` (`visit_id`, `visit_uuid`, `visit_number`, `patient_id`, `status`) VALUES
	(74, 'f43892b7-1c54-11f0-9bb8-f079595cf759', 'v20250001', 19, 'confirmed'),
	(81, 'bb8acf94-1c58-11f0-9bb8-f079595cf759', 'v20250002', 19, 'comfirmed'),
	(91, '04586a57-1c5a-11f0-9bb8-f079595cf759', 'v20250003', 19, 'comfirmed'),
	(92, '4172fbcc-1c5c-11f0-9bb8-f079595cf759', 'v20250004', 19, 'comfirmed'),
	(93, 'a3062048-1c6c-11f0-9bb8-f079595cf759', 'v20250004', 19, 'comfirmed'),
	(94, 'b217b541-1c6c-11f0-9bb8-f079595cf759', 'v20250005', 19, 'comfirmed'),
	(95, '6393d977-1cd8-11f0-b6be-f079595cf759', 'v20250006', 19, 'comfirmed'),
	(96, 'e8fc70ec-1cdb-11f0-b6be-f079595cf759', 'v20250007', 20, 'comfirmed'),
	(97, '4f593305-1cde-11f0-b6be-f079595cf759', 'v20250008', 21, 'comfirmed'),
	(98, 'b6e5e6ad-1ce0-11f0-b6be-f079595cf759', 'v20250009', 22, 'comfirmed'),
	(99, '33b78bed-1d07-11f0-b6be-f079595cf759', 'v20250010', 19, 'comfirmed'),
	(100, 'd4d01344-1d07-11f0-b6be-f079595cf759', 'v20250011', 19, 'comfirmed'),
	(101, '569bf514-1d08-11f0-b6be-f079595cf759', 'v20250012', 19, 'comfirmed'),
	(102, '8f6e8915-1d08-11f0-b6be-f079595cf759', 'v20250013', 19, 'comfirmed'),
	(103, '79da3ac7-1d19-11f0-b6be-f079595cf759', 'v20250014', 19, 'comfirmed'),
	(104, '0f175500-1d1d-11f0-b6be-f079595cf759', 'v20250015', 19, 'comfirmed'),
	(105, 'd4133ad4-1d20-11f0-b6be-f079595cf759', 'v20250016', 19, 'comfirmed'),
	(106, '84291fff-1d22-11f0-b6be-f079595cf759', 'v20250017', 19, 'comfirmed'),
	(107, 'b15ef665-1d25-11f0-b6be-f079595cf759', 'v20250001', 19, 'comfirmed'),
	(108, '74759837-1d26-11f0-b6be-f079595cf759', 'v20250002', 19, 'comfirmed'),
	(109, '34422f14-1d2a-11f0-b6be-f079595cf759', 'v20250003', 19, 'comfirmed'),
	(110, 'fba3a2c5-1d2c-11f0-b6be-f079595cf759', 'v20250004', 19, 'comfirmed'),
	(111, 'e7019e0d-1d2e-11f0-b6be-f079595cf759', 'v20250001', 19, 'comfirmed');

-- Dumping data for table pharma.purchase_orders: ~0 rows (approximately)
DELETE FROM `purchase_orders`;

-- Dumping data for table pharma.purchase_order_items: ~0 rows (approximately)
DELETE FROM `purchase_order_items`;

-- Dumping data for table pharma.sales_ledger: ~1 rows (approximately)
DELETE FROM `sales_ledger`;
INSERT INTO `sales_ledger` (`id`, `invoice_number`, `transection_type`, `s_order_id`, `transaction_date`, `total_amount`, `amount_paid`, `payment_method`, `status`, `remarks`) VALUES
	(7, '125', 'Sale', 131, '2025-04-19 15:00:04', 10, 10, 'cash', 'complete', NULL);

-- Dumping data for table pharma.stock_transactions: ~0 rows (approximately)
DELETE FROM `stock_transactions`;
INSERT INTO `stock_transactions` (`transaction_id`, `item_id`, `transaction_type`, `quantity`, `transaction_date`, `reference`) VALUES
	(82, 1, 'Stock Out', 1, '2025-04-19 15:00:04', NULL),
	(83, 8, 'Stock Out', 1, '2025-04-19 15:00:04', NULL);

-- Dumping data for table pharma.users: ~0 rows (approximately)
DELETE FROM `users`;
INSERT INTO `users` (`id`, `username`, `password`, `role`) VALUES
	(2, 'azeem', '12345', 'admin');

-- Dumping data for table pharma.vendors: ~0 rows (approximately)
DELETE FROM `vendors`;

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
