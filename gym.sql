-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 17-07-2024 a las 09:11:27
-- Versión del servidor: 8.0.37
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `gym2`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `daily_progress`
--

CREATE TABLE `daily_progress` (
  `id` int NOT NULL,
  `member_id` int NOT NULL,
  `progress_date` date NOT NULL,
  `progress_percentage` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `member`
--

CREATE TABLE `member` (
  `member_id` int NOT NULL,
  `username` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `password` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `first_name` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `last_name` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `date_of_birth` date NOT NULL,
  `gender` enum('Male','Female','Other') COLLATE utf8mb4_general_ci NOT NULL,
  `email` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `phone_number` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `address` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `blood_group` enum('A+','A-','B+','B-','AB+','AB-','O+','O-') COLLATE utf8mb4_general_ci DEFAULT NULL,
  `has_heart_problem` tinyint(1) DEFAULT NULL,
  `has_hypertension` tinyint(1) DEFAULT NULL,
  `has_diabetes` tinyint(1) DEFAULT NULL,
  `has_breathing_problem` tinyint(1) DEFAULT NULL,
  `has_hernia` tinyint(1) DEFAULT NULL,
  `has_fracture_dislocation` tinyint(1) DEFAULT NULL,
  `has_back_pain` tinyint(1) DEFAULT NULL,
  `has_knee_problem` tinyint(1) DEFAULT NULL,
  `has_recent_surgery` tinyint(1) DEFAULT NULL,
  `recent_surgery_details` text COLLATE utf8mb4_general_ci,
  `weight` decimal(5,2) DEFAULT NULL,
  `height` decimal(5,2) DEFAULT NULL,
  `photo` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `status` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `member_activities`
--

CREATE TABLE `member_activities` (
  `member_id` int NOT NULL,
  `daily_warm_ups` tinyint(1) DEFAULT NULL,
  `marching_spot_jogging` tinyint(1) DEFAULT NULL,
  `wall_push_ups` tinyint(1) DEFAULT NULL,
  `squats` tinyint(1) DEFAULT NULL,
  `mic_chest_press_seated_row` tinyint(1) DEFAULT NULL,
  `mic_leg_press` tinyint(1) DEFAULT NULL,
  `cycle` tinyint(1) DEFAULT NULL,
  `stretch_walk` tinyint(1) DEFAULT NULL,
  `bench_up_down_step` tinyint(1) DEFAULT NULL,
  `db_shoulder_press_triceps_biceps` tinyint(1) DEFAULT NULL,
  `walker` tinyint(1) DEFAULT NULL,
  `kicks` tinyint(1) DEFAULT NULL,
  `crunches_hip_raises` tinyint(1) DEFAULT NULL,
  `cycling_reverse_cycling` tinyint(1) DEFAULT NULL,
  `reverse_curl` tinyint(1) DEFAULT NULL,
  `single_leg_up_down` tinyint(1) DEFAULT NULL,
  `suryanamaskar` tinyint(1) DEFAULT NULL,
  `stretches_shavasana` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `member_plans`
--

CREATE TABLE `member_plans` (
  `id` int NOT NULL,
  `member_id` int NOT NULL,
  `plan_title` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `fees` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `member_progress`
--

CREATE TABLE `member_progress` (
  `id` int NOT NULL,
  `member_id` int NOT NULL,
  `progress_date` date NOT NULL,
  `progress` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `member_trainer`
--

CREATE TABLE `member_trainer` (
  `member_trainer_id` int NOT NULL,
  `member_id` int NOT NULL,
  `trainer_id` int NOT NULL,
  `assignment_date` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `payment`
--

CREATE TABLE `payment` (
  `payment_id` int NOT NULL,
  `member_id` int NOT NULL,
  `transaction_id` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `payment_date` date NOT NULL,
  `fees` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `posts`
--

CREATE TABLE `posts` (
  `post_id` int NOT NULL,
  `member_id` int NOT NULL,
  `post_description` text COLLATE utf8mb4_general_ci NOT NULL,
  `post_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `title` varchar(255) COLLATE utf8mb4_general_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `trainer`
--

CREATE TABLE `trainer` (
  `trainer_id` int NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `specialization` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `contact_number` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `email` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `username` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `password` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `status` enum('active','inactive') COLLATE utf8mb4_general_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `daily_progress`
--
ALTER TABLE `daily_progress`
  ADD PRIMARY KEY (`id`),
  ADD KEY `member_id` (`member_id`);

--
-- Indices de la tabla `member`
--
ALTER TABLE `member`
  ADD PRIMARY KEY (`member_id`);

--
-- Indices de la tabla `member_activities`
--
ALTER TABLE `member_activities`
  ADD PRIMARY KEY (`member_id`);

--
-- Indices de la tabla `member_plans`
--
ALTER TABLE `member_plans`
  ADD PRIMARY KEY (`id`),
  ADD KEY `member_id` (`member_id`);

--
-- Indices de la tabla `member_progress`
--
ALTER TABLE `member_progress`
  ADD PRIMARY KEY (`id`),
  ADD KEY `member_id` (`member_id`);

--
-- Indices de la tabla `member_trainer`
--
ALTER TABLE `member_trainer`
  ADD PRIMARY KEY (`member_trainer_id`),
  ADD KEY `member_id` (`member_id`),
  ADD KEY `trainer_id` (`trainer_id`);

--
-- Indices de la tabla `payment`
--
ALTER TABLE `payment`
  ADD PRIMARY KEY (`payment_id`),
  ADD KEY `member_id` (`member_id`);

--
-- Indices de la tabla `posts`
--
ALTER TABLE `posts`
  ADD PRIMARY KEY (`post_id`),
  ADD KEY `member_id` (`member_id`);

--
-- Indices de la tabla `trainer`
--
ALTER TABLE `trainer`
  ADD PRIMARY KEY (`trainer_id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `daily_progress`
--
ALTER TABLE `daily_progress`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `member`
--
ALTER TABLE `member`
  MODIFY `member_id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `member_plans`
--
ALTER TABLE `member_plans`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `member_progress`
--
ALTER TABLE `member_progress`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `member_trainer`
--
ALTER TABLE `member_trainer`
  MODIFY `member_trainer_id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `payment`
--
ALTER TABLE `payment`
  MODIFY `payment_id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `posts`
--
ALTER TABLE `posts`
  MODIFY `post_id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `trainer`
--
ALTER TABLE `trainer`
  MODIFY `trainer_id` int NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `daily_progress`
--
ALTER TABLE `daily_progress`
  ADD CONSTRAINT `daily_progress_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `member` (`member_id`);

--
-- Filtros para la tabla `member_activities`
--
ALTER TABLE `member_activities`
  ADD CONSTRAINT `member_activities_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `member` (`member_id`);

--
-- Filtros para la tabla `member_plans`
--
ALTER TABLE `member_plans`
  ADD CONSTRAINT `member_plans_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `member` (`member_id`);

--
-- Filtros para la tabla `member_progress`
--
ALTER TABLE `member_progress`
  ADD CONSTRAINT `member_progress_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `member` (`member_id`);

--
-- Filtros para la tabla `member_trainer`
--
ALTER TABLE `member_trainer`
  ADD CONSTRAINT `member_trainer_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `member` (`member_id`),
  ADD CONSTRAINT `member_trainer_ibfk_2` FOREIGN KEY (`trainer_id`) REFERENCES `trainer` (`trainer_id`);

--
-- Filtros para la tabla `payment`
--
ALTER TABLE `payment`
  ADD CONSTRAINT `payment_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `member` (`member_id`);

--
-- Filtros para la tabla `posts`
--
ALTER TABLE `posts`
  ADD CONSTRAINT `posts_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `member` (`member_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
