-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Jul 28, 2024 at 08:06 PM
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
-- Database: `kkn_karangligar`
--

-- --------------------------------------------------------

--
-- Table structure for table `tbl_m_data`
--

CREATE TABLE `tbl_m_data` (
  `id_tmd` int(11) NOT NULL,
  `judul_tmd` text NOT NULL,
  `nama_tmd` text NOT NULL,
  `keterangan_tmd` varchar(100) NOT NULL,
  `active_tmd` enum('0','1') NOT NULL DEFAULT '0',
  `created_tmd` int(11) NOT NULL,
  `created_time_tmd` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `delected_tmd` int(11) DEFAULT NULL,
  `delected_time_tmd` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_m_label`
--

CREATE TABLE `tbl_m_label` (
  `id_tml` int(11) NOT NULL,
  `nama_tml` varchar(100) NOT NULL,
  `created_tml` int(11) NOT NULL,
  `created_time_tml` timestamp NOT NULL DEFAULT current_timestamp(),
  `delected_tml` int(11) DEFAULT NULL,
  `delected_time_tml` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_m_laporan`
--

CREATE TABLE `tbl_m_laporan` (
  `id_tmla` int(11) NOT NULL,
  `judul_tmla` varchar(50) NOT NULL,
  `file_tmla` text NOT NULL,
  `active_tmla` enum('0','1') NOT NULL,
  `created_tmla` int(11) NOT NULL,
  `created_time_tmla` timestamp NOT NULL DEFAULT current_timestamp(),
  `delected_tmla` int(11) DEFAULT NULL,
  `delected_time_tmla` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_m_profil`
--

CREATE TABLE `tbl_m_profil` (
  `id_tmpo` int(11) NOT NULL,
  `informasi_tmpo` text NOT NULL,
  `facebook_tmpo` varchar(100) NOT NULL,
  `instagram_tmpo` varchar(100) NOT NULL,
  `visi_tmpo` text NOT NULL,
  `misi_tmpo` text NOT NULL,
  `kepala_desa_tmpo` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`kepala_desa_tmpo`)),
  `struktur_tmpo` text NOT NULL,
  `kantor_tmpo` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`kantor_tmpo`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_m_profil`
--

INSERT INTO `tbl_m_profil` (`id_tmpo`, `informasi_tmpo`, `facebook_tmpo`, `instagram_tmpo`, `visi_tmpo`, `misi_tmpo`, `kepala_desa_tmpo`, `struktur_tmpo`, `kantor_tmpo`) VALUES
(1, 'Halo semua', 'facebook.com/contoh', 'instagram.com/contoh', 'Visi desa contoh.', 'Misi desa contoh.', '{\"nama\": \"Nama Kepala Desa\", \"jabatan\": \"Jabatan Kepala Desa\", \"foto\": \"img-about.jpg\"}', 'Gambar-Pemandangan-Sawah-yang-Indah-.jpg', '{\"kode_pos\": \"12345\", \"alamat\": \"Alamat Kantor Desa\", \"notelepon\": \"08012345678\", \"email\": \"kantor@desa.com\"}');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_m_struktur`
--

CREATE TABLE `tbl_m_struktur` (
  `id_tms` int(11) NOT NULL,
  `id_tmla` int(11) NOT NULL,
  `type_tms` varchar(30) DEFAULT NULL,
  `max_tms` int(5) DEFAULT NULL,
  `font_tms` varchar(30) DEFAULT NULL,
  `font_size_tms` int(11) DEFAULT NULL,
  `x_tms` int(5) DEFAULT NULL,
  `y_tms` int(5) DEFAULT NULL,
  `detail_json_tms` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`detail_json_tms`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_m_users`
--

CREATE TABLE `tbl_m_users` (
  `id_tmu` int(11) NOT NULL,
  `nama_tmu` varchar(50) NOT NULL,
  `username_tmu` varchar(30) NOT NULL,
  `password_tmu` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_m_users`
--

INSERT INTO `tbl_m_users` (`id_tmu`, `nama_tmu`, `username_tmu`, `password_tmu`) VALUES
(1, 'Vikha', 't', '202cb962ac59075b964b07152d234b70');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_t_pdf`
--

CREATE TABLE `tbl_t_pdf` (
  `id_ttp` int(11) NOT NULL,
  `file_ttp` text NOT NULL,
  `id_tmla` int(11) NOT NULL,
  `json_ttp` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`json_ttp`)),
  `created_time_ttp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_t_post`
--

CREATE TABLE `tbl_t_post` (
  `id_ttp` int(11) NOT NULL,
  `id_tml` int(11) NOT NULL,
  `judul_ttp` varchar(100) NOT NULL,
  `gambar_ttp` text NOT NULL,
  `postingan_ttp` text NOT NULL,
  `active_ttp` enum('0','1') NOT NULL DEFAULT '0',
  `created_ttp` int(11) NOT NULL,
  `created_time_ttp` timestamp NOT NULL DEFAULT current_timestamp(),
  `delected_ttp` int(11) DEFAULT NULL,
  `delected_time_ttp` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `tbl_m_data`
--
ALTER TABLE `tbl_m_data`
  ADD PRIMARY KEY (`id_tmd`);

--
-- Indexes for table `tbl_m_label`
--
ALTER TABLE `tbl_m_label`
  ADD PRIMARY KEY (`id_tml`);

--
-- Indexes for table `tbl_m_laporan`
--
ALTER TABLE `tbl_m_laporan`
  ADD PRIMARY KEY (`id_tmla`);

--
-- Indexes for table `tbl_m_profil`
--
ALTER TABLE `tbl_m_profil`
  ADD PRIMARY KEY (`id_tmpo`);

--
-- Indexes for table `tbl_m_struktur`
--
ALTER TABLE `tbl_m_struktur`
  ADD PRIMARY KEY (`id_tms`),
  ADD KEY `id_tmla` (`id_tmla`);

--
-- Indexes for table `tbl_m_users`
--
ALTER TABLE `tbl_m_users`
  ADD PRIMARY KEY (`id_tmu`);

--
-- Indexes for table `tbl_t_pdf`
--
ALTER TABLE `tbl_t_pdf`
  ADD PRIMARY KEY (`id_ttp`),
  ADD KEY `id_tmla` (`id_tmla`);

--
-- Indexes for table `tbl_t_post`
--
ALTER TABLE `tbl_t_post`
  ADD PRIMARY KEY (`id_ttp`),
  ADD KEY `id_tml` (`id_tml`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `tbl_m_data`
--
ALTER TABLE `tbl_m_data`
  MODIFY `id_tmd` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `tbl_m_label`
--
ALTER TABLE `tbl_m_label`
  MODIFY `id_tml` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `tbl_m_laporan`
--
ALTER TABLE `tbl_m_laporan`
  MODIFY `id_tmla` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `tbl_m_profil`
--
ALTER TABLE `tbl_m_profil`
  MODIFY `id_tmpo` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `tbl_m_struktur`
--
ALTER TABLE `tbl_m_struktur`
  MODIFY `id_tms` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `tbl_m_users`
--
ALTER TABLE `tbl_m_users`
  MODIFY `id_tmu` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `tbl_t_pdf`
--
ALTER TABLE `tbl_t_pdf`
  MODIFY `id_ttp` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `tbl_t_post`
--
ALTER TABLE `tbl_t_post`
  MODIFY `id_ttp` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `tbl_m_struktur`
--
ALTER TABLE `tbl_m_struktur`
  ADD CONSTRAINT `tbl_m_struktur_ibfk_1` FOREIGN KEY (`id_tmla`) REFERENCES `tbl_m_laporan` (`id_tmla`);

--
-- Constraints for table `tbl_t_pdf`
--
ALTER TABLE `tbl_t_pdf`
  ADD CONSTRAINT `tbl_t_pdf_ibfk_1` FOREIGN KEY (`id_tmla`) REFERENCES `tbl_m_laporan` (`id_tmla`);

--
-- Constraints for table `tbl_t_post`
--
ALTER TABLE `tbl_t_post`
  ADD CONSTRAINT `tbl_t_post_ibfk_1` FOREIGN KEY (`id_tml`) REFERENCES `tbl_m_label` (`id_tml`) ON DELETE NO ACTION ON UPDATE NO ACTION;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
