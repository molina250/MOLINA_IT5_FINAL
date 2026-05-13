-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 13, 2026 at 01:20 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `edugate_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `enrollment_reports`
--

CREATE TABLE `enrollment_reports` (
  `id` int(11) NOT NULL,
  `student_id` varchar(20) NOT NULL,
  `first_name` varchar(100) DEFAULT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `full_name` varchar(220) DEFAULT NULL,
  `email` varchar(150) DEFAULT NULL,
  `contact_number` varchar(50) DEFAULT NULL,
  `grade_level` varchar(20) DEFAULT NULL,
  `strand` varchar(50) DEFAULT NULL,
  `section` varchar(50) DEFAULT NULL,
  `schedule` varchar(50) DEFAULT NULL,
  `form_137` varchar(20) DEFAULT NULL,
  `form_138` varchar(20) DEFAULT NULL,
  `birth_certificate` varchar(20) DEFAULT NULL,
  `status` varchar(30) DEFAULT NULL,
  `payment_status` varchar(30) DEFAULT NULL,
  `registrar_db_id` int(11) DEFAULT NULL,
  `registrar_account` varchar(50) DEFAULT NULL,
  `registrar_name` varchar(150) DEFAULT NULL,
  `enrolled_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `enrollment_reports`
--

INSERT INTO `enrollment_reports` (`id`, `student_id`, `first_name`, `last_name`, `full_name`, `email`, `contact_number`, `grade_level`, `strand`, `section`, `schedule`, `form_137`, `form_138`, `birth_certificate`, `status`, `payment_status`, `registrar_db_id`, `registrar_account`, `registrar_name`, `enrolled_at`, `updated_at`) VALUES
(10, 'ST-0001', 'John', 'Dela Cruz', 'John Dela Cruz', 'john.delacruz1@gmail.com', '09171234501', '11', 'ABM', 'ABM11 - 2', 'AFTERNOON', 'Passed', 'Passed', 'Passed', 'Enrolled', 'Paid', 24, 'justin123', 'justin molina', '2026-05-13 01:23:10', '2026-05-13 07:48:37'),
(11, 'ST-0002', 'Maria', 'Santos', 'Maria Santos', 'maria.santos2@gmail.com', '09171234502', '12', 'ABM', 'AMB12 - 1', 'MORNING', 'Passed', 'To-Follow', 'Passed', 'Enrolled', 'Paid', 24, 'justin123', 'justin molina', '2026-05-13 01:24:56', '2026-05-13 07:48:37'),
(12, 'ST-0003', 'Joseph', 'Reyes', 'Joseph Reyes', 'joseph.reyes3@gmail.com', '09171234503', '11', 'STEM', 'STEM11  - 2', 'AFTERNOON', 'Passed', 'Passed', 'Passed', 'Enrolled', 'Paid', 24, 'justin123', 'justin molina', '2026-05-13 01:24:58', '2026-05-13 07:48:37'),
(13, 'ST-0004', 'Angela', 'Garcia', 'Angela Garcia', 'mark.mendoza5@gmail.com', '09171234505', '12', 'STEM', 'STEM12 - 3', 'EVENING', 'Passed', 'To-Follow', 'Passed', 'Enrolled', 'Paid', 24, 'justin123', 'justin molina', '2026-05-13 01:25:01', '2026-05-13 07:48:37'),
(14, 'ST-0007', 'Kevin', 'Aquino', 'Kevin Aquino', 'kevin.aquino9@gmail.com', '09171234509', '12', 'GAS', 'GAS12 - 2', 'AFTERNOON', 'Passed', 'Passed', 'Passed', 'Enrolled', 'Paid', 26, 'lebron123', 'lebron james', '2026-05-13 01:27:24', '2026-05-13 07:48:37'),
(15, 'ST-0006', 'Jasmine', 'Ramos', 'Jasmine Ramos', 'jasmine.ramos8@gmail.com', '09171234508', '11', 'TVL', 'TVL11 - 1', 'MORNING', 'Passed', 'Passed', 'Passed', 'Enrolled', 'Paid', 26, 'lebron123', 'lebron james', '2026-05-13 01:27:27', '2026-05-13 07:48:37'),
(16, 'ST-0005', 'Daniel', 'Flores', 'Daniel Flores', 'daniel.flores7@gmail.com', '09171234507', '11', 'HUMSS', 'HUMSS11 - 1', 'MORNING', 'Passed', 'Passed', 'Passed', 'Enrolled', 'Paid', 26, 'lebron123', 'lebron james', '2026-05-13 01:27:29', '2026-05-13 07:48:37'),
(28, 'ST-0008', 'gonza', 'gaga', 'gonza gaga', 'gaga@gmail.com', '0963258741', '12', 'GAS', 'GAS12 - 2', 'AFTERNOON', 'Passed', 'Passed', 'Passed', 'Enrolled', 'Paid', 24, 'justin123', 'justin molina', '2026-05-13 01:52:01', '2026-05-13 07:48:37');

-- --------------------------------------------------------

--
-- Table structure for table `payment_queue`
--

CREATE TABLE `payment_queue` (
  `id` int(11) NOT NULL,
  `student_id` varchar(20) NOT NULL,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  `contact_number` varchar(50) NOT NULL,
  `grade_level` varchar(10) NOT NULL,
  `strand` varchar(20) NOT NULL,
  `form_137` varchar(20) DEFAULT 'To-Follow',
  `form_138` varchar(20) DEFAULT 'To-Follow',
  `birth_certificate` varchar(20) DEFAULT 'To-Follow',
  `section` varchar(50) DEFAULT NULL,
  `assignments` text DEFAULT NULL,
  `payment_status` varchar(15) DEFAULT 'Unpaid',
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `strand_id` int(11) DEFAULT NULL,
  `schedule` varchar(50) DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `payment_queue`
--

INSERT INTO `payment_queue` (`id`, `student_id`, `first_name`, `last_name`, `email`, `contact_number`, `grade_level`, `strand`, `form_137`, `form_138`, `birth_certificate`, `section`, `assignments`, `payment_status`, `created_at`, `updated_at`, `strand_id`, `schedule`) VALUES
(36, 'ST-0009', 'Brian', 'Fernandez', 'brian.fernandez@gmail.com', '09171234515', '12', 'HUMSS', 'Passed', 'Passed', 'Passed', 'HUMSS12 - 1', '{\"PHILIPPINE POLITICS\": \"Paulo R. Navarro\", \"APPLIED SOCIAL SCIENCE\": \"Liza C. Bautista\", \"COMMUNITY ENGAGEMENT\": \"Liza C. Bautista\", \"TRENDS, NETWORKS AND CRITICAL THINKING\": \"Adrian T. Flores\"}', 'Unpaid', '2026-05-13 02:06:07', '2026-05-13 02:06:08', 5440, 'MORNING');

-- --------------------------------------------------------

--
-- Table structure for table `pending_enrollments`
--

CREATE TABLE `pending_enrollments` (
  `id` int(11) NOT NULL,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  `contact_number` varchar(50) NOT NULL,
  `grade_level` varchar(20) NOT NULL,
  `strand` varchar(50) NOT NULL,
  `form_137` varchar(20) DEFAULT 'To-Follow',
  `form_138` varchar(20) DEFAULT 'To-Follow',
  `birth_certificate` varchar(20) DEFAULT 'To-Follow',
  `section` varchar(50) DEFAULT '',
  `adviser` varchar(150) DEFAULT '',
  `teacher_assignments` text DEFAULT NULL,
  `payment_status` varchar(20) DEFAULT 'Unpaid',
  `submitted_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `student_id` varchar(20) DEFAULT NULL,
  `strand_id` int(11) DEFAULT NULL,
  `schedule` varchar(50) DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `pending_enrollments`
--

INSERT INTO `pending_enrollments` (`id`, `first_name`, `last_name`, `email`, `contact_number`, `grade_level`, `strand`, `form_137`, `form_138`, `birth_certificate`, `section`, `adviser`, `teacher_assignments`, `payment_status`, `submitted_at`, `student_id`, `strand_id`, `schedule`) VALUES
(34, 'Brian', 'Fernandez', 'brian.fernandez@gmail.com', '09171234515', '12', 'HUMSS', 'Passed', 'Passed', 'Passed', 'HUMSS12 - 1', '', '{\"PHILIPPINE POLITICS\": \"Paulo R. Navarro\", \"APPLIED SOCIAL SCIENCE\": \"Liza C. Bautista\", \"COMMUNITY ENGAGEMENT\": \"Liza C. Bautista\", \"TRENDS, NETWORKS AND CRITICAL THINKING\": \"Adrian T. Flores\"}', 'Unpaid', '2026-05-12 18:06:07', 'ST-0009', 5440, '');

-- --------------------------------------------------------

--
-- Table structure for table `registrars`
--

CREATE TABLE `registrars` (
  `id` int(11) NOT NULL,
  `registrar_id` varchar(10) NOT NULL,
  `full_name` varchar(150) NOT NULL,
  `email` varchar(150) NOT NULL,
  `contact_number` varchar(30) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `registrars`
--

INSERT INTO `registrars` (`id`, `registrar_id`, `full_name`, `email`, `contact_number`, `username`, `password`, `created_at`) VALUES
(23, 'gonz123', 'alex gonzaga', 'gonzaga@gmail.com', '09654152524', 'reg_gonz123', 'ENC:dHZmc3Q=', '2026-05-11 10:42:04'),
(24, 'justin123', 'justin molina', 'justinmols@gmail.com', '096325872', 'reg_justin123', 'ENC:dHZmc3Q=', '2026-05-11 11:02:55'),
(25, 'gem123', 'gema gabs', 'gema@gmail.com', '09632587155', 'reg_gem123', 'ENC:dHZmc3Q=', '2026-05-12 15:12:42'),
(26, 'lebron123', 'lebron james', 'lebron@gmail.com', '09632584133', 'reg_lebron123', 'ENC:dHZmc3Q=', '2026-05-12 16:24:11'),
(27, 'shiloh123', 'SHILOH ROQUE', 'SHI123@GMAIL.COM', '09654152', 'reg_shiloh123', 'ENC:dHZmc3Q=', '2026-05-12 17:28:54'),
(28, 'jing123', 'JING KAZAMA', 'JING@GMAIL.COM', '096288741', 'reg_jing123', 'ENC:dHZmc3Q=', '2026-05-12 17:38:32');

-- --------------------------------------------------------

--
-- Table structure for table `reports`
--

CREATE TABLE `reports` (
  `id` int(11) NOT NULL,
  `strand` varchar(20) NOT NULL,
  `daily` int(11) NOT NULL DEFAULT 0,
  `weekly` int(11) NOT NULL DEFAULT 0,
  `monthly` int(11) NOT NULL DEFAULT 0,
  `yearly` int(11) NOT NULL DEFAULT 0,
  `total` int(11) NOT NULL DEFAULT 0,
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `strand_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `reports`
--

INSERT INTO `reports` (`id`, `strand`, `daily`, `weekly`, `monthly`, `yearly`, `total`, `updated_at`, `strand_id`) VALUES
(6, 'ABM', 2, 2, 2, 2, 2, '2026-05-13 07:49:43', 5439),
(7, 'GAS', 2, 2, 2, 2, 2, '2026-05-13 07:49:43', 5441),
(8, 'HUMSS', 1, 1, 1, 1, 1, '2026-05-13 07:49:43', 5440),
(9, 'STEM', 2, 2, 2, 2, 2, '2026-05-13 07:49:43', 5438),
(10, 'TVL', 1, 1, 1, 1, 1, '2026-05-13 07:49:43', 5442);

-- --------------------------------------------------------

--
-- Table structure for table `slots`
--

CREATE TABLE `slots` (
  `id` int(11) NOT NULL,
  `strand` varchar(50) NOT NULL,
  `grade_level` varchar(10) NOT NULL,
  `section` varchar(50) NOT NULL,
  `schedule` varchar(50) DEFAULT '',
  `max_slots` int(11) DEFAULT 50,
  `taken_slots` int(11) DEFAULT 0,
  `available_slots` int(11) DEFAULT 50,
  `updated_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `slots`
--

INSERT INTO `slots` (`id`, `strand`, `grade_level`, `section`, `schedule`, `max_slots`, `taken_slots`, `available_slots`, `updated_at`) VALUES
(1, 'STEM', '11', 'STEM11 - 1', 'Morning', 50, 0, 50, '2026-05-13 07:45:05'),
(2, 'STEM', '11', 'STEM11 - 2', 'Afternoon', 50, 1, 49, '2026-05-13 07:45:05'),
(3, 'STEM', '11', 'STEM11 - 3', 'Evening', 50, 0, 50, '2026-05-13 07:45:05'),
(4, 'STEM', '12', 'STEM12 - 1', 'Morning', 50, 0, 50, '2026-05-13 07:45:05'),
(5, 'STEM', '12', 'STEM12 - 2', 'Afternoon', 50, 0, 50, '2026-05-13 07:45:05'),
(6, 'STEM', '12', 'STEM12 - 3', 'Evening', 50, 1, 49, '2026-05-13 07:45:05'),
(7, 'ABM', '11', 'ABM11 - 1', 'Morning', 50, 0, 50, '2026-05-13 07:45:05'),
(8, 'ABM', '11', 'ABM11 - 2', 'Afternoon', 50, 1, 49, '2026-05-13 07:45:05'),
(9, 'ABM', '11', 'ABM11 - 3', 'Evening', 50, 0, 50, '2026-05-13 07:45:05'),
(10, 'ABM', '12', 'ABM12 - 1', 'Morning', 50, 0, 50, '2026-05-13 07:45:05'),
(11, 'ABM', '12', 'ABM12 - 2', 'Afternoon', 50, 0, 50, '2026-05-13 07:45:05'),
(12, 'ABM', '12', 'ABM12 - 3', 'Evening', 50, 0, 50, '2026-05-13 07:45:05'),
(13, 'HUMSS', '11', 'HUMSS11 - 1', 'Morning', 50, 1, 49, '2026-05-13 07:45:05'),
(14, 'HUMSS', '11', 'HUMSS11 - 2', 'Afternoon', 50, 0, 50, '2026-05-13 07:45:05'),
(15, 'HUMSS', '11', 'HUMSS11 - 3', 'Evening', 50, 0, 50, '2026-05-13 07:45:05'),
(16, 'HUMSS', '12', 'HUMSS12 - 1', 'Morning', 50, 1, 49, '2026-05-13 07:45:05'),
(17, 'HUMSS', '12', 'HUMSS12 - 2', 'Afternoon', 50, 0, 50, '2026-05-13 07:45:05'),
(18, 'HUMSS', '12', 'HUMSS12 - 3', 'Evening', 50, 0, 50, '2026-05-13 07:45:05'),
(19, 'GAS', '11', 'GAS11 - 1', 'Morning', 50, 0, 50, '2026-05-13 07:45:05'),
(20, 'GAS', '11', 'GAS11 - 2', 'Afternoon', 50, 0, 50, '2026-05-13 07:45:05'),
(21, 'GAS', '11', 'GAS11 - 3', 'Evening', 50, 0, 50, '2026-05-13 07:45:05'),
(22, 'GAS', '12', 'GAS12 - 1', 'Morning', 50, 0, 50, '2026-05-13 07:45:05'),
(23, 'GAS', '12', 'GAS12 - 2', 'Afternoon', 50, 2, 48, '2026-05-13 07:45:05'),
(24, 'GAS', '12', 'GAS12 - 3', 'Evening', 50, 0, 50, '2026-05-13 07:45:05'),
(25, 'TVL', '11', 'TVL11 - 1', 'Morning', 50, 1, 49, '2026-05-13 07:45:05'),
(26, 'TVL', '11', 'TVL11 - 2', 'Afternoon', 50, 0, 50, '2026-05-13 07:45:05'),
(27, 'TVL', '11', 'TVL11 - 3', 'Evening', 50, 0, 50, '2026-05-13 07:45:05'),
(28, 'TVL', '12', 'TVL12 - 1', 'Morning', 50, 0, 50, '2026-05-13 07:45:05'),
(29, 'TVL', '12', 'TVL12 - 2', 'Afternoon', 50, 0, 50, '2026-05-13 07:45:05'),
(30, 'TVL', '12', 'TVL12 - 3', 'Evening', 50, 0, 50, '2026-05-13 07:45:05');

-- --------------------------------------------------------

--
-- Table structure for table `strands`
--

CREATE TABLE `strands` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `strands`
--

INSERT INTO `strands` (`id`, `name`) VALUES
(5439, 'ABM'),
(5441, 'GAS'),
(5440, 'HUMSS'),
(5438, 'STEM'),
(5442, 'TVL');

-- --------------------------------------------------------

--
-- Table structure for table `students`
--

CREATE TABLE `students` (
  `id` int(11) NOT NULL,
  `student_id` varchar(12) DEFAULT NULL,
  `first_name` varchar(100) DEFAULT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `email` varchar(150) DEFAULT NULL,
  `contact_number` varchar(30) DEFAULT NULL,
  `grade_level` enum('11','12') DEFAULT NULL,
  `strand` varchar(50) DEFAULT NULL,
  `form_137` varchar(20) DEFAULT NULL,
  `form_138` varchar(20) DEFAULT NULL,
  `birth_certificate` varchar(20) DEFAULT NULL,
  `status` enum('Pending','Enrolled','Dropped') DEFAULT 'Pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `section` varchar(50) DEFAULT NULL,
  `schedule` varchar(50) DEFAULT '',
  `adviser` varchar(100) DEFAULT NULL,
  `payment_status` varchar(20) DEFAULT NULL,
  `payment_approved` tinyint(1) DEFAULT 0,
  `paid_at` datetime DEFAULT NULL,
  `enrolled_at` datetime DEFAULT NULL,
  `teacher_assignments` text DEFAULT NULL,
  `assignments` text DEFAULT NULL,
  `registrar_id` int(11) DEFAULT NULL,
  `strand_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `students`
--

INSERT INTO `students` (`id`, `student_id`, `first_name`, `last_name`, `email`, `contact_number`, `grade_level`, `strand`, `form_137`, `form_138`, `birth_certificate`, `status`, `created_at`, `section`, `schedule`, `adviser`, `payment_status`, `payment_approved`, `paid_at`, `enrolled_at`, `teacher_assignments`, `assignments`, `registrar_id`, `strand_id`) VALUES
(8, 'ST-0001', 'John', 'Dela Cruz', 'john.delacruz1@gmail.com', '09171234501', '11', 'ABM', 'Passed', 'Passed', 'Passed', 'Enrolled', '2026-05-12 17:23:10', 'ABM11 - 2', 'AFTERNOON', NULL, 'Paid', 1, '2026-05-13 01:23:10', '2026-05-13 01:23:10', '{\"FABM 1\": \"Andrew M. Lim\", \"BUSINESS MATHEMATICS\": \"Joseph L. Mendoza\", \"APPLIED ECONOMICS\": \"Patricia L. Gomez\", \"BUSINESS ETHICS\": \"Patricia L. Gomez\"}', '{\"FABM 1\": \"Andrew M. Lim\", \"BUSINESS MATHEMATICS\": \"Joseph L. Mendoza\", \"APPLIED ECONOMICS\": \"Patricia L. Gomez\", \"BUSINESS ETHICS\": \"Patricia L. Gomez\"}', 24, 5439),
(9, 'ST-0002', 'Maria', 'Santos', 'maria.santos2@gmail.com', '09171234502', '12', 'ABM', 'Passed', 'To-Follow', 'Passed', 'Enrolled', '2026-05-12 17:24:56', 'AMB12 - 1', 'MORNING', NULL, 'Paid', 1, '2026-05-13 01:24:56', '2026-05-13 01:24:56', '{\"FABM 2\": \"Angela R. Cruz\", \"BUSINESS FINANCE\": \"Clarissa M. Villanueva\", \"ENTREPRENEURSHIP\": \"Clarissa M. Villanueva\", \"STRATEGIC MANAGEMENT\": \"Clarissa M. Villanueva\"}', '{\"FABM 2\": \"Angela R. Cruz\", \"BUSINESS FINANCE\": \"Clarissa M. Villanueva\", \"ENTREPRENEURSHIP\": \"Clarissa M. Villanueva\", \"STRATEGIC MANAGEMENT\": \"Clarissa M. Villanueva\"}', 24, 5439),
(10, 'ST-0003', 'Joseph', 'Reyes', 'joseph.reyes3@gmail.com', '09171234503', '11', 'STEM', 'Passed', 'Passed', 'Passed', 'Enrolled', '2026-05-12 17:24:58', 'STEM11  - 2', 'AFTERNOON', NULL, 'Paid', 1, '2026-05-13 01:24:58', '2026-05-13 01:24:58', '{\"PRE-CALCULUS\": \"Nicole S. Reyes\", \"BASIC CALCULUS\": \"Leonard M. Cruz\", \"GENERAL BIOLOGY 1\": \"Angela F. Dizon\", \"GENERAL CHEMISTRY 1\": \"Catherine L. Uy\", \"GENERAL PHYSICS 1\": \"Janine F. Dela Cruz\"}', '{\"PRE-CALCULUS\": \"Nicole S. Reyes\", \"BASIC CALCULUS\": \"Leonard M. Cruz\", \"GENERAL BIOLOGY 1\": \"Angela F. Dizon\", \"GENERAL CHEMISTRY 1\": \"Catherine L. Uy\", \"GENERAL PHYSICS 1\": \"Janine F. Dela Cruz\"}', 24, 5438),
(11, 'ST-0004', 'Angela', 'Garcia', 'mark.mendoza5@gmail.com', '09171234505', '12', 'STEM', 'Passed', 'To-Follow', 'Passed', 'Enrolled', '2026-05-12 17:25:01', 'STEM12 - 3', 'EVENING', NULL, 'Paid', 1, '2026-05-13 01:25:01', '2026-05-13 01:25:01', '{\"GENERAL BIOLOGY 2\": \"Paolo R. Navarro\", \"GENERAL CHEMISTRY 2\": \"Arvin S. Bautista\", \"GENERAL PHYSICS 2\": \"Clarissa M. Villanueva\", \"RESEARCH / CAPSTONE\": \"Andrea L. Perez\", \"BASIC CALCULUS\": \"Jonathan P. Reyes\"}', '{\"GENERAL BIOLOGY 2\": \"Paolo R. Navarro\", \"GENERAL CHEMISTRY 2\": \"Arvin S. Bautista\", \"GENERAL PHYSICS 2\": \"Clarissa M. Villanueva\", \"RESEARCH / CAPSTONE\": \"Andrea L. Perez\", \"BASIC CALCULUS\": \"Jonathan P. Reyes\"}', 24, 5438),
(12, 'ST-0007', 'Kevin', 'Aquino', 'kevin.aquino9@gmail.com', '09171234509', '12', 'GAS', 'Passed', 'Passed', 'Passed', 'Enrolled', '2026-05-12 17:27:24', 'GAS12 - 2', 'AFTERNOON', NULL, 'Paid', 1, '2026-05-13 01:27:24', '2026-05-13 01:27:24', '{\"HUMANITIES 2\": \"Jerome V. Castillo\", \"COMMUNITY ENGAGEMENT\": \"Kevin M. Salazar\", \"ENTREPRENEURSHIP\": \"Faith L. Torres\", \"MEDIA INFORMATION LITERACY\": \"Andrea L. Perez\"}', '{\"HUMANITIES 2\": \"Jerome V. Castillo\", \"COMMUNITY ENGAGEMENT\": \"Kevin M. Salazar\", \"ENTREPRENEURSHIP\": \"Faith L. Torres\", \"MEDIA INFORMATION LITERACY\": \"Andrea L. Perez\"}', 26, 5441),
(13, 'ST-0006', 'Jasmine', 'Ramos', 'jasmine.ramos8@gmail.com', '09171234508', '11', 'TVL', 'Passed', 'Passed', 'Passed', 'Enrolled', '2026-05-12 17:27:27', 'TVL11 - 1', 'MORNING', NULL, 'Paid', 1, '2026-05-13 01:27:27', '2026-05-13 01:27:27', '{\"SPECIALIZATION 1\": \"Brian T. Villamor\", \"ENTREPRENEURSHIP\": \"Lorna M. Santiago\", \"SAFETY AND WORKPLACE PRACTICES\": \"Dennis A. Morales\"}', '{\"SPECIALIZATION 1\": \"Brian T. Villamor\", \"ENTREPRENEURSHIP\": \"Lorna M. Santiago\", \"SAFETY AND WORKPLACE PRACTICES\": \"Dennis A. Morales\"}', 26, 5442),
(14, 'ST-0005', 'Daniel', 'Flores', 'daniel.flores7@gmail.com', '09171234507', '11', 'HUMSS', 'Passed', 'Passed', 'Passed', 'Enrolled', '2026-05-12 17:27:29', 'HUMSS11 - 1', 'MORNING', NULL, 'Paid', 1, '2026-05-13 01:27:29', '2026-05-13 01:27:29', '{\"CREATIVE WRITING\": \"Maria L. Reyes\", \"CREATIVE NONFICTION\": \"Maria L. Reyes\", \"WORLD RELIGIONS\": \"Adrian T. Flores\", \"21st CENTURY LITERATURE\": \"Maria L. Reyes\"}', '{\"CREATIVE WRITING\": \"Maria L. Reyes\", \"CREATIVE NONFICTION\": \"Maria L. Reyes\", \"WORLD RELIGIONS\": \"Adrian T. Flores\", \"21st CENTURY LITERATURE\": \"Maria L. Reyes\"}', 26, 5440),
(19, 'ST-0008', 'gonza', 'gaga', 'gaga@gmail.com', '0963258741', '12', 'GAS', 'Passed', 'Passed', 'Passed', 'Enrolled', '2026-05-12 17:52:01', 'GAS12 - 2', 'AFTERNOON', NULL, 'Paid', 1, '2026-05-13 01:52:01', '2026-05-13 01:52:01', '{\"HUMANITIES 2\": \"Jerome V. Castillo\", \"COMMUNITY ENGAGEMENT\": \"Kevin M. Salazar\", \"ENTREPRENEURSHIP\": \"Faith L. Torres\", \"MEDIA INFORMATION LITERACY\": \"Andrea L. Perez\"}', '{\"HUMANITIES 2\": \"Jerome V. Castillo\", \"COMMUNITY ENGAGEMENT\": \"Kevin M. Salazar\", \"ENTREPRENEURSHIP\": \"Faith L. Torres\", \"MEDIA INFORMATION LITERACY\": \"Andrea L. Perez\"}', 24, 5441);

-- --------------------------------------------------------

--
-- Table structure for table `student_enrollment`
--

CREATE TABLE `student_enrollment` (
  `id` int(11) NOT NULL,
  `student_id` varchar(12) NOT NULL,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `email` varchar(150) DEFAULT NULL,
  `contact_number` varchar(30) NOT NULL,
  `grade_level` enum('11','12') NOT NULL,
  `strand` varchar(50) NOT NULL,
  `form_137` varchar(20) NOT NULL DEFAULT 'To-Follow',
  `form_138` varchar(20) NOT NULL DEFAULT 'To-Follow',
  `birth_certificate` varchar(20) NOT NULL DEFAULT 'To-Follow',
  `status` enum('Pending','Enrolled','Dropped') NOT NULL DEFAULT 'Pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `registrar_id` int(11) DEFAULT NULL,
  `strand_id` int(11) DEFAULT NULL,
  `section` varchar(50) DEFAULT NULL,
  `adviser` varchar(100) DEFAULT NULL,
  `payment_status` varchar(20) NOT NULL DEFAULT 'Unpaid',
  `payment_approved` tinyint(1) NOT NULL DEFAULT 0,
  `paid_at` datetime DEFAULT NULL,
  `enrolled_at` datetime DEFAULT NULL,
  `teacher_assignments` text DEFAULT NULL,
  `assignments` text DEFAULT NULL,
  `schedule` varchar(50) DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `enrollment_reports`
--
ALTER TABLE `enrollment_reports`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `student_id` (`student_id`),
  ADD KEY `idx_enrollment_reports_strand` (`strand`),
  ADD KEY `idx_enrollment_reports_registrar` (`registrar_db_id`);

--
-- Indexes for table `payment_queue`
--
ALTER TABLE `payment_queue`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `student_id` (`student_id`),
  ADD KEY `fk_payment_strand` (`strand_id`);

--
-- Indexes for table `pending_enrollments`
--
ALTER TABLE `pending_enrollments`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `student_id` (`student_id`),
  ADD KEY `fk_pending_strand` (`strand_id`);

--
-- Indexes for table `registrars`
--
ALTER TABLE `registrars`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `registrar_id` (`registrar_id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `reports`
--
ALTER TABLE `reports`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `strand` (`strand`),
  ADD KEY `idx_reports_strand_id` (`strand_id`);

--
-- Indexes for table `slots`
--
ALTER TABLE `slots`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_section` (`strand`,`grade_level`,`section`);

--
-- Indexes for table `strands`
--
ALTER TABLE `strands`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `students`
--
ALTER TABLE `students`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `student_id` (`student_id`);

--
-- Indexes for table `student_enrollment`
--
ALTER TABLE `student_enrollment`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `student_id` (`student_id`),
  ADD KEY `idx_student_enrollment_registrar_id` (`registrar_id`),
  ADD KEY `idx_student_enrollment_strand_id` (`strand_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `enrollment_reports`
--
ALTER TABLE `enrollment_reports`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=40;

--
-- AUTO_INCREMENT for table `payment_queue`
--
ALTER TABLE `payment_queue`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=37;

--
-- AUTO_INCREMENT for table `pending_enrollments`
--
ALTER TABLE `pending_enrollments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=35;

--
-- AUTO_INCREMENT for table `registrars`
--
ALTER TABLE `registrars`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT for table `reports`
--
ALTER TABLE `reports`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `slots`
--
ALTER TABLE `slots`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;

--
-- AUTO_INCREMENT for table `strands`
--
ALTER TABLE `strands`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9078;

--
-- AUTO_INCREMENT for table `students`
--
ALTER TABLE `students`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT for table `student_enrollment`
--
ALTER TABLE `student_enrollment`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `payment_queue`
--
ALTER TABLE `payment_queue`
  ADD CONSTRAINT `fk_payment_strand` FOREIGN KEY (`strand_id`) REFERENCES `strands` (`id`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Constraints for table `pending_enrollments`
--
ALTER TABLE `pending_enrollments`
  ADD CONSTRAINT `fk_pending_strand` FOREIGN KEY (`strand_id`) REFERENCES `strands` (`id`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Constraints for table `reports`
--
ALTER TABLE `reports`
  ADD CONSTRAINT `fk_reports_strands` FOREIGN KEY (`strand_id`) REFERENCES `strands` (`id`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Constraints for table `student_enrollment`
--
ALTER TABLE `student_enrollment`
  ADD CONSTRAINT `fk_student_enrollment_registrars` FOREIGN KEY (`registrar_id`) REFERENCES `registrars` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_student_enrollment_strands` FOREIGN KEY (`strand_id`) REFERENCES `strands` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_student_registrar` FOREIGN KEY (`registrar_id`) REFERENCES `registrars` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_student_strand` FOREIGN KEY (`strand_id`) REFERENCES `strands` (`id`) ON DELETE SET NULL ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
