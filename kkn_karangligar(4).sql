-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Aug 03, 2024 at 09:43 AM
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
(1, 'Desa Karangligar, sebuah desa yang terletak di Kabupaten Karawang, Jawa Barat, Indonesia, memiliki karakteristik unik yang membuatnya berbeda dari desa-desa lain di sekitarnya. Desa ini terletak di dataran rendah, dengan sebagian besar wilayahnya berupa lahan pertanian yang subur. Keberadaan sungai-sungai kecil yang mengalir di sekitar desa menambah kesuburan tanah, sehingga banyak warga yang menggantungkan hidup mereka pada sektor pertanian.\r\n\r\n### Sejarah Desa Karangligar\r\n\r\nSejarah Desa Karangligar tak lepas dari perjalanan panjang yang dimulai sejak zaman kolonial. Menurut cerita turun-temurun, desa ini didirikan oleh para pendatang dari berbagai daerah yang mencari lahan subur untuk bercocok tanam. Mereka membuka lahan, membangun rumah, dan mulai bercocok tanam padi serta palawija. Nama \"Karangligar\" sendiri dipercaya berasal dari kata \"karang\" yang berarti tempat atau wilayah, dan \"ligar\" yang berarti luas atau lapang, mencerminkan luasnya wilayah pertanian yang ada di desa ini.\r\n\r\nPada masa penjajahan Belanda, Desa Karangligar mengalami banyak tantangan, termasuk pemaksaan kerja rodi dan pengambilan hasil bumi oleh penjajah. Meskipun demikian, semangat gotong royong dan kebersamaan warga desa selalu menjadi kekuatan utama untuk bertahan dan melawan penjajah. Setelah kemerdekaan Indonesia, Desa Karangligar perlahan-lahan mulai membangun kembali kehidupannya dengan fokus pada pertanian sebagai sumber utama penghidupan.\r\n\r\n### Kehidupan Sosial dan Ekonomi\r\n\r\nMayoritas penduduk Desa Karangligar bekerja sebagai petani. Lahan pertanian yang subur memungkinkan mereka menanam berbagai jenis tanaman, terutama padi, jagung, dan sayuran. Selain itu, beberapa warga juga beternak sapi, kambing, dan unggas sebagai tambahan penghasilan. Hasil pertanian dan peternakan tidak hanya dikonsumsi sendiri, tetapi juga dijual ke pasar-pasar di kota Karawang dan sekitarnya.\r\n\r\nKehidupan sosial di Desa Karangligar sangat kental dengan nilai-nilai kekeluargaan dan gotong royong. Setiap ada kegiatan desa, seperti panen raya, pembangunan fasilitas umum, atau acara adat, seluruh warga desa akan bahu-membahu bekerja sama. Tradisi gotong royong ini sudah menjadi bagian tak terpisahkan dari kehidupan sehari-hari dan diwariskan dari generasi ke generasi.\r\n\r\n### Pendidikan dan Kesehatan\r\n\r\nPendidikan di Desa Karangligar terus berkembang seiring waktu. Terdapat beberapa sekolah dasar dan satu sekolah menengah pertama yang melayani kebutuhan pendidikan anak-anak di desa ini. Para guru yang berdedikasi tinggi berperan penting dalam memberikan pendidikan yang berkualitas, meskipun dengan fasilitas yang masih terbatas. Beberapa anak desa juga melanjutkan pendidikan mereka ke tingkat yang lebih tinggi di kota-kota terdekat.\r\n\r\nKesehatan masyarakat Desa Karangligar dijaga melalui Puskesmas yang menyediakan layanan kesehatan dasar. Para petugas medis bekerja keras untuk memastikan warga desa mendapatkan perawatan yang diperlukan. Selain itu, terdapat juga program posyandu yang aktif melakukan pemantauan kesehatan ibu dan anak, serta program imunisasi rutin untuk mencegah berbagai penyakit.\r\n\r\n### Budaya dan Tradisi\r\n\r\nDesa Karangligar kaya akan budaya dan tradisi yang masih terjaga hingga kini. Salah satu tradisi yang masih dilestarikan adalah upacara adat \"Seren Taun\", yaitu acara syukuran atas hasil panen yang melibatkan seluruh warga desa. Acara ini biasanya diisi dengan berbagai kegiatan, seperti doa bersama, tarian tradisional, dan pesta rakyat. Seren Taun menjadi momen penting untuk mempererat tali silaturahmi antarwarga dan memperkuat rasa syukur kepada Tuhan atas rezeki yang diberikan.\r\n\r\nSelain Seren Taun, ada juga tradisi \"Ruwatan\" yang dilakukan untuk menolak bala dan menjaga keselamatan desa dari segala macam bahaya. Upacara ini biasanya dipimpin oleh sesepuh desa dan melibatkan berbagai ritual, seperti penyembelihan hewan, pembacaan doa, dan taburan bunga di tempat-tempat tertentu. Ruwatan menjadi simbol kepercayaan dan kebersamaan warga dalam menjaga keharmonisan desa.\r\n\r\n### Potensi dan Tantangan\r\n\r\nDesa Karangligar memiliki potensi besar untuk terus berkembang, terutama di sektor pertanian. Inovasi dalam teknik bercocok tanam dan pemanfaatan teknologi pertanian dapat meningkatkan produktivitas dan kualitas hasil pertanian. Selain itu, desa ini juga memiliki potensi untuk mengembangkan agrowisata, dengan menawarkan pengalaman bercocok tanam, wisata alam, dan kuliner khas desa kepada wisatawan.\r\n\r\nNamun, Desa Karangligar juga menghadapi berbagai tantangan. Salah satu tantangan terbesar adalah perubahan iklim yang berdampak pada pola cuaca dan ketersediaan air. Kekeringan atau banjir dapat merusak lahan pertanian dan mengancam mata pencaharian warga. Oleh karena itu, diperlukan upaya adaptasi dan mitigasi yang efektif untuk menghadapi perubahan iklim.\r\n\r\nTantangan lain adalah keterbatasan akses terhadap pendidikan dan kesehatan yang lebih baik. Fasilitas pendidikan yang masih terbatas mempengaruhi kualitas pendidikan yang dapat diberikan kepada anak-anak desa. Begitu pula dengan fasilitas kesehatan yang perlu ditingkatkan untuk memastikan seluruh warga mendapatkan layanan kesehatan yang memadai.\r\n\r\n### Harapan dan Masa Depan\r\n\r\nMeskipun menghadapi berbagai tantangan, harapan untuk masa depan Desa Karangligar tetap tinggi. Semangat gotong royong dan kebersamaan warga desa menjadi modal utama untuk menghadapi segala rintangan. Dengan dukungan dari pemerintah dan berbagai pihak, Desa Karangligar dapat terus berkembang dan meningkatkan kualitas hidup warganya.\r\n\r\nInvestasi dalam pendidikan dan kesehatan menjadi kunci penting untuk masa depan desa. Peningkatan fasilitas pendidikan dan kesehatan akan membuka peluang bagi generasi muda untuk meraih masa depan yang lebih baik. Selain itu, pengembangan sektor pertanian dan agrowisata dapat menciptakan lapangan kerja baru dan meningkatkan kesejahteraan ekonomi warga desa.\r\n\r\nDesa Karangligar adalah contoh nyata dari desa yang berjuang untuk maju dan berkembang, sambil tetap menjaga nilai-nilai budaya dan tradisi yang ada. Dengan semangat yang kuat dan kerja sama yang solid, Desa Karangligar akan terus menjadi tempat yang nyaman dan sejahtera bagi seluruh warganya.', 'facebook.com/contoh', 'instagram.com/contoh', '“MELAYANI MASYARAKAT DESA KARANGLIGAR SECARA  MENYELURUH DEMI TERWUJUD NYA DESA KARANGLIGAR YANG DISIPLIN, CERDAS, SANTUN, ADIL, RELIGI”\r\n\r\na. DISIPLIN	: Upaya peningkatan watak supaya mentaati tata tertib,displin ke bagi semua perangkat desa karangligar kepatuhan kepada aturan.\r\nb. CERDAS	: Sempurna perkembangan akan budinya untuk memotivasi Masyarakat akan penting nya pendidikan, tajam pikirannya, dalam menyelesaikan setiap permasalahan, pandai dan tanggap, terhadap keadaan aspirasi masyarakat.\r\nc. SANTUN	: Halus dan baik budi bahasa tingkah laku dalam hal untuk mencerminkan pribadi yang luhur,sopan,sabar,tenang,dan memperhatikan kepentingan 		  umum.\r\nd. ADIL		: Berperilaku baik,tidak pandang bulu,tidak \r\nberat sebelah,tidak membeda bedakan masyarakat yang satu dengan yang lainnya.dalam setiap kepentingan desa karangligar dengan tidak menimbulkan kesenjangan social di seluruh masyarakat desa karangligar baik dalam pemerataan pembangunan fisik maupun non fisik.\r\ne. RELIGI	: Kepercayaan ketaqwaan kepada tuhan yang maha esa, menguatkan kita jauh dari sifat serakah, dan saling menghormati antara sesama agama yang ada di desa karangligar.', 'a.	Berusaha mengutamakan kepentingan masyaraka dalam hal pembangunan baik dengan dana desa, pemerintah, kabupaten, provinsi maupun pusat maupun pihak yang lain nya sesuai dengan mutu nya.\r\nb.	Pemertaan pembangunan yang ada di desa karangligar teralisasi dengan baik.\r\nc.	Percepatan pembangunan yang berkualitas', '{\"nama\": \"ERSIM\", \"jabatan\": \"KEPALA DESA\", \"foto\": \"img-about.jpg\"}', 'Gambar-Pemandangan-Sawah-yang-Indah-.jpg', '{\"kode_pos\": \"41361\", \"alamat\": \"Jl. Kp. Jati Mulya No.37, RT.7/RW.2, Karangligar, Kec. Telukjambe Bar., Karawang, Jawa Barat 41361\", \"notelepon\": \"08012345678\", \"email\": \"kantor@desa.com\"}');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_m_struktur`
--

CREATE TABLE `tbl_m_struktur` (
  `id_tms` int(11) NOT NULL,
  `id_tmla` int(11) NOT NULL,
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
