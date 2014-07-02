-- phpMyAdmin SQL Dump
-- version 3.5.8.2
-- http://www.phpmyadmin.net
--
-- Client: localhost
-- Généré le: Jeu 27 Mars 2014 à 16:13
-- Version du serveur: 5.5.36-MariaDB
-- Version de PHP: 5.5.10

SET FOREIGN_KEY_CHECKS=0;
SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

--
-- Base de données: `2leadin`
--

--
-- Contenu de la table `applications`
--

INSERT INTO `applications` (`id`, `display`, `name`, `app_key`, `website`, `created`, `removed`, `status`) VALUES
(1, 'Demo app', 'demo', 'development', NULL, '2014-03-05 17:46:57', NULL, 'DEV');

--
-- Contenu de la table `application_plans`
--

INSERT INTO `application_plans` (`id`, `display`, `description`, `application_id`, `sms`, `members`, `storage`, `projects`, `monthly_price`, `yearly_price`, `currency`, `share`, `start`, `created`, `removed`) VALUES
(1, 'Free membership', '', 1, 0, 1, 0, 1, 0, 0, 'EUR', 50, '2014-03-24 22:14:45', '2014-03-24 22:14:45', NULL);

--
-- Contenu de la table `organizations`
--

INSERT INTO `organizations` (`id`, `name`, `display`, `description`, `website`, `created`, `removed`, `currency`, `application_id`, `application_plan_id`) VALUES
(1, 'reflectiv', '', '', '', '2014-03-24 22:15:09', NULL, 'EUR', 1, 1);


--
-- Contenu de la table `members`
--

INSERT INTO `profiles` (`id`, `email`, `password`, `application_id`) VALUES
(1, 'cx42net@gmail.com', '$2a$10$SvBx.HpqseikPbRbu/kU6.nS9eJc0nTHUEjiXqllgeJbHdl.yHqa.', 1),
(2, 'member@invoi.cz', '$2a$10$Jb9QV.tHsJLf6cj5J0J7u.wIFFJtdqJ8krA1aTg/NTctBp/ld.1yi', 1),
(3, 'client@invoi.cz', '$2a$10$cFx5zTaf8FGWDOdf7PRocOR5arT8zq7gS0eQobXraov0x9nyReCNm', 1);


--
-- Contenu de la table `members`
--

INSERT INTO `members` (`id`, `display`, `address`, `zipcode`, `city`, `state`, `country`, `office`, `mobile`, `fax`, `website`, `description`, `sector`, `seen`, `last_seen`, `created`, `modified`, `lang`, `is_disabled`, `removed`, `owner_id`, `profile_id`, `organization_id`, `status`, `is_admin`) VALUES
(1, 'Cyril N.', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2014-03-05 17:46:57', '2014-03-05 17:46:57', '', 0, NULL, 1, 1, 1, 'MEMBER', 1),
(2, 'test', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2014-03-05 19:19:34', '2014-03-05 19:19:34', 'en', 0, NULL, 1, 2, 1, 'CLIENT', 0),
(3, 'test', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2014-03-05 19:20:09', '2014-03-05 19:20:09', 'en', 0, NULL, 1, 3, 1, 'CLIENT', 0);

--
-- Contenu de la table `member_comments`
--

INSERT INTO `member_comments` (`id`, `created`, `message`, `author_id`, `client_id`) VALUES
(1, '2014-03-27 14:53:53', 'Hello dear boy :)', 1, 1),
(2, '2014-03-27 14:54:48', 'How are you today ?', 1, 1),
(4, '2014-03-27 15:09:11', 'I hope you don''t mind, I talked to you to the boss ;) Right?', 1, 1);

--
-- Contenu de la table `sessions`
--

SET FOREIGN_KEY_CHECKS=1;
