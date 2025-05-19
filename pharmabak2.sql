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


-- Dumping database structure for pharma
CREATE DATABASE IF NOT EXISTS `pharma` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `pharma`;

-- Dumping structure for table pharma.issued_items
CREATE TABLE IF NOT EXISTS `issued_items` (
  `issue_id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int DEFAULT NULL,
  `item_id` int DEFAULT NULL,
  `quantity` int NOT NULL,
  `issued_by` varchar(100) DEFAULT NULL,
  `issue_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`issue_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table pharma.issued_items: ~0 rows (approximately)
DELETE FROM `issued_items`;

-- Dumping structure for table pharma.items
CREATE TABLE IF NOT EXISTS `items` (
  `b_item_id` int NOT NULL AUTO_INCREMENT,
  `b_Item_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `b_item_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `b_cat` enum('Tablet','Injection','Syrup','Capsule','Ointment','Misc','Drops','Inhaler','Suppository','Gel','Cream','Lotion','Spray','Powder') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `uom` enum('pcs','ml','mg','g','l','kg') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `pieces_per_pack` int DEFAULT '1' COMMENT 'Number of pieces per pack (0 if sold loose)',
  `packs_per_unit` int DEFAULT '0' COMMENT 'Number of packs per unit/box (0 if N/A)',
  `current_stock` int DEFAULT '0' COMMENT 'Total quantity in pieces',
  `min_stock` int DEFAULT '0' COMMENT 'Reorder threshold in pieces',
  `max_stock` int DEFAULT NULL COMMENT 'Max capacity in pieces',
  `supplier_id` varchar(20) DEFAULT NULL,
  `preferred_supplier` varchar(100) DEFAULT NULL,
  `last_restock_date` date DEFAULT NULL,
  `next_restock_date` date DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `requires_prescription` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `generic_name` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`b_item_id`),
  UNIQUE KEY `b_item_name` (`b_item_name`),
  UNIQUE KEY `b_Item_code` (`b_Item_code`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table pharma.items: ~4 rows (approximately)
DELETE FROM `items`;
INSERT INTO `items` (`b_item_id`, `b_Item_code`, `b_item_name`, `b_cat`, `uom`, `pieces_per_pack`, `packs_per_unit`, `current_stock`, `min_stock`, `max_stock`, `supplier_id`, `preferred_supplier`, `last_restock_date`, `next_restock_date`, `is_active`, `requires_prescription`, `created_at`, `updated_at`, `generic_name`) VALUES
	(16, 'TAB-0011', 'Panadol 20mg1', 'Injection', 'pcs', 200, 20, 0, 0, NULL, NULL, NULL, NULL, NULL, 0, 0, '2025-05-07 11:38:50', '2025-05-14 10:52:22', NULL),
	(17, 'CAP-001', 'Risek 40mg', 'Capsule', 'mg', 40, 2, 0, 0, NULL, NULL, NULL, NULL, NULL, 1, 0, '2025-05-11 19:00:00', '2025-05-12 12:01:41', NULL),
	(18, 'TAB-002', 'Amoxcil', 'Capsule', 'mg', 200, 20, 0, 0, NULL, NULL, NULL, NULL, NULL, 1, 0, '2025-05-08 14:47:03', '2025-05-08 14:47:03', NULL),
	(19, 'TAB-003', 'Neubrol Fort', 'Tablet', 'mg', 15, 3, 0, 0, NULL, NULL, NULL, NULL, NULL, 1, 0, '2025-05-09 12:23:16', '2025-05-09 12:23:16', NULL),
	(20, 'Inj-001', 'KINZ 10MG INJ', 'Injection', 'mg', 1, 1, 0, 0, NULL, NULL, NULL, NULL, NULL, 1, 0, '2025-05-14 11:27:48', '2025-05-14 11:27:48', NULL);

-- Dumping structure for table pharma.ledger
CREATE TABLE IF NOT EXISTS `ledger` (
  `ledger_id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int DEFAULT NULL,
  `transaction_type` enum('Debit','Credit') NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `transaction_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `reference` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`ledger_id`),
  KEY `patient_id` (`patient_id`),
  CONSTRAINT `ledger_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table pharma.ledger: ~0 rows (approximately)
DELETE FROM `ledger`;

-- Dumping structure for table pharma.orders
CREATE TABLE IF NOT EXISTS `orders` (
  `order_id` int NOT NULL AUTO_INCREMENT,
  `order_uuid` char(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT (uuid()),
  `visit_id` int DEFAULT NULL,
  `order_number` varchar(50) DEFAULT NULL,
  `order_status` enum('Pending','Complete','Return','Cancel') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'Pending',
  `created_date` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`order_id`),
  KEY `FK_orders_patient_visit` (`visit_id`),
  CONSTRAINT `FK_orders_patient_visit` FOREIGN KEY (`visit_id`) REFERENCES `patient_visit` (`visit_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=237 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table pharma.orders: ~0 rows (approximately)
DELETE FROM `orders`;
INSERT INTO `orders` (`order_id`, `order_uuid`, `visit_id`, `order_number`, `order_status`, `created_date`) VALUES
	(235, '16439a04-30b2-11f0-a55c-f079595cf759', 223, 'o20250001', 'Complete', '2025-05-14 10:56:28'),
	(236, 'eefb2bb8-30b3-11f0-a55c-f079595cf759', 224, 'o20250002', 'Complete', '2025-05-14 11:09:41');

-- Dumping structure for table pharma.order_detail
CREATE TABLE IF NOT EXISTS `order_detail` (
  `oitem_id` int NOT NULL AUTO_INCREMENT,
  `order_id` int DEFAULT NULL,
  `o_item_id` int DEFAULT NULL,
  `item_code` varchar(50) DEFAULT NULL,
  `oitem_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `qty` int DEFAULT NULL,
  `selling_price` float DEFAULT NULL,
  `oi_status` enum('Sale','Return','Cancel','Pending') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'Pending',
  `Column 4` int DEFAULT NULL,
  PRIMARY KEY (`oitem_id`) USING BTREE,
  KEY `FK_order_items_orders` (`order_id`),
  CONSTRAINT `FK_order_items_orders` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=213 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table pharma.order_detail: ~0 rows (approximately)
DELETE FROM `order_detail`;
INSERT INTO `order_detail` (`oitem_id`, `order_id`, `o_item_id`, `item_code`, `oitem_name`, `qty`, `selling_price`, `oi_status`, `Column 4`) VALUES
	(208, 235, 76, 'CAP-001', 'Risek 40mg', 40, 4.01, 'Pending', NULL),
	(209, 235, 77, 'TAB-002', 'Amoxcil', 5, 0.3, 'Pending', NULL),
	(210, 235, 78, 'TAB-003', 'Neubrol Fort', 5, 30.02, 'Pending', NULL),
	(211, 236, 78, 'TAB-003', 'Neubrol Fort', 5, 30.02, 'Pending', NULL),
	(212, 236, 76, 'CAP-001', 'Risek 40mg', 40, 4.01, 'Pending', NULL);

-- Dumping structure for table pharma.patients
CREATE TABLE IF NOT EXISTS `patients` (
  `patient_id` int NOT NULL AUTO_INCREMENT,
  `p_uuid` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'uuid()',
  `MRN` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `first_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `last_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `age` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `cnic` bigint DEFAULT NULL,
  `Mobile` bigint DEFAULT NULL,
  `address` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  PRIMARY KEY (`patient_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table pharma.patients: ~3 rows (approximately)
DELETE FROM `patients`;
INSERT INTO `patients` (`patient_id`, `p_uuid`, `MRN`, `first_name`, `last_name`, `age`, `created_at`, `cnic`, `Mobile`, `address`) VALUES
	(28, 'uuid()', 'A25-0705-0001', 'Azeem', 'khalil', 36, '2025-05-07 14:46:28', 4220150905441, 3453151738, NULL),
	(29, 'uuid()', 'A25-0705-0002', 'danish', 'yaseen', 31, '2025-05-07 15:29:58', 1321321321321, 32132132132, NULL),
	(30, 'uuid()', 'A25-0805-0001', 'Riaz', 'Ali', 30, '2025-05-08 14:48:56', 1234456789151, 3450000000, NULL);

-- Dumping structure for table pharma.patient_bills
CREATE TABLE IF NOT EXISTS `patient_bills` (
  `bill_id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int DEFAULT NULL,
  `total_amount` decimal(10,2) DEFAULT '0.00',
  `amount_paid` decimal(10,2) DEFAULT '0.00',
  `status` enum('Pending','Paid') DEFAULT 'Pending',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`bill_id`),
  KEY `patient_bills_ibfk_1` (`patient_id`),
  CONSTRAINT `patient_bills_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table pharma.patient_bills: ~0 rows (approximately)
DELETE FROM `patient_bills`;

-- Dumping structure for table pharma.patient_visit
CREATE TABLE IF NOT EXISTS `patient_visit` (
  `visit_id` int NOT NULL AUTO_INCREMENT,
  `visit_uuid` char(50) DEFAULT (uuid()),
  `visit_number` varchar(50) DEFAULT NULL,
  `patient_id` int DEFAULT NULL,
  `p_visit_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`visit_id`),
  KEY `FK_patient_visit_patients` (`patient_id`),
  CONSTRAINT `FK_patient_visit_patients` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=225 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table pharma.patient_visit: ~0 rows (approximately)
DELETE FROM `patient_visit`;
INSERT INTO `patient_visit` (`visit_id`, `visit_uuid`, `visit_number`, `patient_id`, `p_visit_date`, `status`) VALUES
	(223, '163907b4-30b2-11f0-a55c-f079595cf759', 'pv20250001', 28, '2025-05-14 15:56:28', 'Confirmed'),
	(224, 'eef0f962-30b3-11f0-a55c-f079595cf759', 'pv20250002', 29, '2025-05-14 16:09:41', 'Confirmed');

-- Dumping structure for table pharma.permissions
CREATE TABLE IF NOT EXISTS `permissions` (
  `permission_id` int NOT NULL AUTO_INCREMENT,
  `permission_name` varchar(100) NOT NULL,
  `description` text,
  PRIMARY KEY (`permission_id`),
  UNIQUE KEY `permission_name` (`permission_name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table pharma.permissions: ~4 rows (approximately)
DELETE FROM `permissions`;
INSERT INTO `permissions` (`permission_id`, `permission_name`, `description`) VALUES
	(1, 'create', 'Create content'),
	(2, 'read', 'Read content'),
	(3, 'update', 'Update content'),
	(4, 'delete', 'Delete content');

-- Dumping structure for table pharma.purchase_orders
CREATE TABLE IF NOT EXISTS `purchase_orders` (
  `po_id` int NOT NULL AUTO_INCREMENT,
  `vendor_id` int DEFAULT NULL,
  `order_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `status` enum('Pending','Received','Cancelled') DEFAULT 'Pending',
  `total_amount` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`po_id`),
  KEY `vendor_id` (`vendor_id`),
  CONSTRAINT `purchase_orders_ibfk_1` FOREIGN KEY (`vendor_id`) REFERENCES `vendors` (`vendor_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table pharma.purchase_orders: ~0 rows (approximately)
DELETE FROM `purchase_orders`;

-- Dumping structure for table pharma.purchase_order_items
CREATE TABLE IF NOT EXISTS `purchase_order_items` (
  `po_item_id` int NOT NULL AUTO_INCREMENT,
  `po_id` int DEFAULT NULL,
  `item_id` int DEFAULT NULL,
  `quantity` int NOT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  `received_date` date DEFAULT NULL,
  PRIMARY KEY (`po_item_id`),
  KEY `purchase_order_items_ibfk_1` (`po_id`),
  KEY `purchase_order_items_ibfk_2` (`item_id`),
  CONSTRAINT `purchase_order_items_ibfk_1` FOREIGN KEY (`po_id`) REFERENCES `purchase_orders` (`po_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `purchase_order_items_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `stock` (`item_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table pharma.purchase_order_items: ~0 rows (approximately)
DELETE FROM `purchase_order_items`;

-- Dumping structure for table pharma.returns
CREATE TABLE IF NOT EXISTS `returns` (
  `return_id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `return_number` varchar(50) NOT NULL,
  `original_sale_id` int NOT NULL,
  `return_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `reason_code` enum('DAMAGED','EXPIRED','WRONG ITEM','PATIENT RETURN','OTHER') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `restocking_fee` decimal(10,2) NOT NULL DEFAULT '0.00',
  `total_refund` decimal(12,2) DEFAULT NULL,
  `payment_method` enum('CASH','CREDIT','ADJUSTMENT') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `status` enum('COMPLETED','PENDING','REJECTED') NOT NULL DEFAULT 'COMPLETED',
  `processed_by` int DEFAULT NULL,
  `approved_by` int DEFAULT NULL,
  `notes` text,
  PRIMARY KEY (`return_id`),
  UNIQUE KEY `return_number` (`return_number`),
  KEY `FK_returns_orders` (`original_sale_id`),
  CONSTRAINT `FK_returns_orders` FOREIGN KEY (`original_sale_id`) REFERENCES `orders` (`order_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=199 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table pharma.returns: ~0 rows (approximately)
DELETE FROM `returns`;

-- Dumping structure for table pharma.return_items
CREATE TABLE IF NOT EXISTS `return_items` (
  `return_item_id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `return_id` varchar(50) NOT NULL DEFAULT '',
  `original_sale_item_id` varchar(50) NOT NULL DEFAULT '0',
  `item_id` int NOT NULL,
  `batch_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `quantity` int DEFAULT NULL,
  `original_price` decimal(10,2) DEFAULT NULL,
  `refund_amount` decimal(10,2) DEFAULT NULL,
  `reason` varchar(255) DEFAULT NULL,
  `restock_quantity` decimal(10,3) DEFAULT NULL COMMENT 'May differ if item is damaged',
  PRIMARY KEY (`return_item_id`),
  KEY `FK_return_items_returns` (`return_id`),
  KEY `FK_return_items_order_detail` (`original_sale_item_id`)
) ENGINE=InnoDB AUTO_INCREMENT=171 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table pharma.return_items: ~0 rows (approximately)
DELETE FROM `return_items`;

-- Dumping structure for table pharma.roles
CREATE TABLE IF NOT EXISTS `roles` (
  `role_id` int NOT NULL AUTO_INCREMENT,
  `role_name` varchar(50) NOT NULL,
  `description` text,
  PRIMARY KEY (`role_id`),
  UNIQUE KEY `role_name` (`role_name`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table pharma.roles: ~6 rows (approximately)
DELETE FROM `roles`;
INSERT INTO `roles` (`role_id`, `role_name`, `description`) VALUES
	(1, 'admin', 'Administrator with full access'),
	(2, 'Manager', 'Can edit content'),
	(3, 'Supervisor', 'Can view content only'),
	(5, 'Pharmacist', 'Can feed medicine and recive cash'),
	(6, 'Tech', NULL),
	(7, 'veiw_only', NULL);

-- Dumping structure for table pharma.role_permissions
CREATE TABLE IF NOT EXISTS `role_permissions` (
  `role_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`role_id`,`permission_id`),
  KEY `permission_id` (`permission_id`),
  CONSTRAINT `role_permissions_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`role_id`) ON DELETE CASCADE,
  CONSTRAINT `role_permissions_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`permission_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table pharma.role_permissions: ~8 rows (approximately)
DELETE FROM `role_permissions`;
INSERT INTO `role_permissions` (`role_id`, `permission_id`) VALUES
	(1, 1),
	(2, 1),
	(1, 2),
	(2, 2),
	(3, 2),
	(1, 3),
	(2, 3),
	(1, 4);

-- Dumping structure for table pharma.sales
CREATE TABLE IF NOT EXISTS `sales` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `invoice_number` varchar(50) NOT NULL,
  `transection_type` varchar(50) NOT NULL,
  `s_order_id` int DEFAULT NULL,
  `transaction_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `total_amount` float NOT NULL DEFAULT '0',
  `amount_paid` float DEFAULT NULL,
  `payment_method` varchar(50) DEFAULT NULL,
  `balance_due` float GENERATED ALWAYS AS ((`total_amount` - `amount_paid`)) STORED,
  `status` varchar(20) DEFAULT 'unpaid',
  `remarks` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=176 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table pharma.sales: ~0 rows (approximately)
DELETE FROM `sales`;
INSERT INTO `sales` (`id`, `invoice_number`, `transection_type`, `s_order_id`, `transaction_date`, `total_amount`, `amount_paid`, `payment_method`, `status`, `remarks`) VALUES
	(174, 'c20250001', 'Sale', 235, '2025-05-14 10:56:39', 312, 312, 'Cash', 'Complete', NULL),
	(175, 'c20250002', 'Sale', 236, '2025-05-14 11:09:58', 310, 310, 'Cash', 'Complete', NULL);

-- Dumping structure for table pharma.stock
CREATE TABLE IF NOT EXISTS `stock` (
  `item_id` int NOT NULL AUTO_INCREMENT,
  `b_item_id` int DEFAULT NULL,
  `item_code` varchar(20) NOT NULL,
  `item_name` varchar(100) NOT NULL,
  `category` enum('Tablet','Injection','Syrup','Capsule','Ointment','Misc','Drops','Inhaler','Suppository','Gel','Cream','Lotion','Spray','Powder') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `unit` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `stock_quantity` int DEFAULT '0',
  `reorder_level` int DEFAULT NULL,
  `batch_no` varchar(50) DEFAULT NULL,
  `expiry_date` date DEFAULT NULL,
  `purchase_price` decimal(10,2) DEFAULT NULL,
  `selling_price` decimal(10,2) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`item_id`),
  KEY `FK_stock_items` (`item_code`),
  KEY `FK_stock_items_2` (`item_name`),
  KEY `FK_stock_items_3` (`b_item_id`),
  CONSTRAINT `FK_stock_items` FOREIGN KEY (`item_code`) REFERENCES `items` (`b_Item_code`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_stock_items_2` FOREIGN KEY (`item_name`) REFERENCES `items` (`b_item_name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_stock_items_3` FOREIGN KEY (`b_item_id`) REFERENCES `items` (`b_item_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=79 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table pharma.stock: ~3 rows (approximately)
DELETE FROM `stock`;
INSERT INTO `stock` (`item_id`, `b_item_id`, `item_code`, `item_name`, `category`, `unit`, `stock_quantity`, `reorder_level`, `batch_no`, `expiry_date`, `purchase_price`, `selling_price`, `created_at`) VALUES
	(76, 17, 'CAP-001', 'Risek 40mg', 'Capsule', NULL, 760, 0, NULL, NULL, 150.30, 160.30, '2025-05-14 10:57:53'),
	(77, 18, 'TAB-002', 'Amoxcil', 'Capsule', NULL, 9995, 0, NULL, NULL, 50.00, 60.00, '2025-05-14 10:54:46'),
	(78, 19, 'TAB-003', 'Neubrol Fort', 'Tablet', NULL, 140, 0, NULL, NULL, 350.30, 450.30, '2025-05-14 10:55:17');

-- Dumping structure for table pharma.stock_transactions
CREATE TABLE IF NOT EXISTS `stock_transactions` (
  `transaction_id` int NOT NULL AUTO_INCREMENT,
  `item_id` int DEFAULT NULL,
  `transaction_type` enum('Stock In','Stock Out','Adjustment','Reserve','Return') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `quantity` int NOT NULL,
  `transaction_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `reference` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`transaction_id`),
  KEY `FK_stock_transactions_stock` (`item_id`),
  CONSTRAINT `FK_stock_transactions_stock` FOREIGN KEY (`item_id`) REFERENCES `stock` (`item_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=450 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table pharma.stock_transactions: ~7 rows (approximately)
DELETE FROM `stock_transactions`;
INSERT INTO `stock_transactions` (`transaction_id`, `item_id`, `transaction_type`, `quantity`, `transaction_date`, `reference`) VALUES
	(441, 76, 'Stock In', 800, '2025-05-14 10:54:16', NULL),
	(442, 77, 'Stock In', 10000, '2025-05-14 10:54:46', NULL),
	(443, 78, 'Stock In', 150, '2025-05-14 10:55:18', NULL),
	(444, 76, 'Stock Out', 40, '2025-05-13 19:00:00', NULL),
	(445, 77, 'Stock Out', 5, '2025-05-13 19:00:00', NULL),
	(446, 78, 'Stock Out', 5, '2025-05-13 19:00:00', NULL),
	(447, 76, 'Stock In', 40, '2025-05-13 12:57:53', NULL),
	(448, 78, 'Stock Out', 5, '2025-05-13 19:00:00', NULL),
	(449, 76, 'Stock Out', 40, '2025-05-13 19:00:00', NULL);

-- Dumping structure for table pharma.users
CREATE TABLE IF NOT EXISTS `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `active` int DEFAULT '1',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table pharma.users: ~9 rows (approximately)
DELETE FROM `users`;
INSERT INTO `users` (`user_id`, `username`, `password`, `email`, `active`) VALUES
	(1, 'johndoe', '$argon2id$v=19$m=65536,t=3,p=4$CF4p16xmx7tTTXP8BDijwg$Fjk8vCds/yxrsTRzcCToB7inVH9dmIVRzJWn5r9BBo4', 'john@example.com', 1),
	(2, 'azeem.khalil', '$argon2id$v=19$m=65536,t=3,p=4$9zAlSPe4WOY+1j0rwyyMIQ$oACP56yny6XX0zBlMbyTw7pmPRTaHiXXkifMEuf1tOs', 'khalil@gmail.com', 1),
	(3, 'test', 'test', 'test', 1),
	(4, 'danis.yaseen', '$argon2id$v=19$m=65536,t=3,p=4$SbXbk/ANM8C9gSDeilIAaA$jJDWOlBf9V6L8Uxk0ooSamoWRlRy0oHTHyEsVxulb0A', '0', 1),
	(5, 'azeem', '$argon2id$v=19$m=65536,t=3,p=4$SukP/MgsP5NO6Jx1fKyecQ$rWyAc0tV0zJVl1LjTBaLeRcg4Vpwdd+PxOmOmgyYG/s', '0', 1),
	(6, 'azeem3', '$argon2id$v=19$m=65536,t=3,p=4$bpVmbXWxNdJN26aAMSCakw$xkZK65JjKd4rJWBvZGFd3MtxQuNTAgTckXfZxyH5y7c', '0', 1),
	(7, 'aeem4', '$argon2id$v=19$m=65536,t=3,p=4$tGl8jYYl6k/tbBQixUYY8g$/366RujOBt6weSUTc4Y+XQ34vmzVyHaTmMG7N2j+NP4', '0', 1),
	(8, 'asdfsadf', '$argon2id$v=19$m=65536,t=3,p=4$yvp+YNGOGGs8Af4HmBgDoQ$a0bqJNKkUGXpS3Meazb6IQeJ9EC8/EXLvYeufFm3txs', '0', 1),
	(9, 'asim', '$argon2id$v=19$m=65536,t=3,p=4$0UzLUKk4lvC68F+VnverPQ$E/U7viBJRXG5NXIqIB0esQBlPpoxkMdzKngolefBDHQ', '0', 1);

-- Dumping structure for table pharma.user_roles
CREATE TABLE IF NOT EXISTS `user_roles` (
  `user_id` int NOT NULL,
  `role_id` int NOT NULL,
  PRIMARY KEY (`user_id`,`role_id`),
  KEY `role_id` (`role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table pharma.user_roles: ~5 rows (approximately)
DELETE FROM `user_roles`;
INSERT INTO `user_roles` (`user_id`, `role_id`) VALUES
	(1, 1),
	(2, 1),
	(9, 1),
	(1, 2),
	(2, 2);

-- Dumping structure for table pharma.vendors
CREATE TABLE IF NOT EXISTS `vendors` (
  `vendor_id` int NOT NULL AUTO_INCREMENT,
  `vendor_name` varchar(100) NOT NULL,
  `contact_person` varchar(100) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `address` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`vendor_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table pharma.vendors: ~0 rows (approximately)
DELETE FROM `vendors`;

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
