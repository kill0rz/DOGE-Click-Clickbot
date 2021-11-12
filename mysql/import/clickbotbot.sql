SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';

SET NAMES utf8mb4;
CREATE DATABASE IF NOT EXISTS `clickbotbot` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;
USE `clickbotbot`;

DROP TABLE IF EXISTS `cbb_channels`;
CREATE TABLE `cbb_channels` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `channelname` varchar(33) NOT NULL,
  `joinedat` datetime NOT NULL DEFAULT '0000-00-00 00:00:00' ON UPDATE current_timestamp(),
  `hourstolast` int(11) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `channelname` (`channelname`),
  UNIQUE KEY `ID` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DELIMITER ;;

CREATE TRIGGER `cbb_channels_setjoinedat` BEFORE INSERT ON `cbb_channels` FOR EACH ROW
BEGIN
    SET NEW.joinedat = NOW();
END;;

DELIMITER ;

DROP VIEW IF EXISTS `cbb_v_getChannelsToLeave`;
CREATE TABLE `cbb_v_getChannelsToLeave` (`channelname` varchar(33));


DROP TABLE IF EXISTS `cbb_v_getChannelsToLeave`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `cbb_v_getChannelsToLeave` AS select `cbb_channels`.`channelname` AS `channelname` from `cbb_channels` where `cbb_channels`.`joinedat` + interval `cbb_channels`.`hourstolast` hour < current_timestamp();
