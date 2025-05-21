-- MySQL dump 10.13  Distrib 8.4.5, for Win64 (x86_64)
--
-- Host: localhost    Database: halchinemadb
-- ------------------------------------------------------
-- Server version	8.4.5

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `movies`
--

DROP TABLE IF EXISTS `movies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movies` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(64) NOT NULL,
  `release_date` date DEFAULT NULL,
  `running_time` int DEFAULT NULL,
  `synopsis` text,
  `image_url` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movies`
--

LOCK TABLES `movies` WRITE;
/*!40000 ALTER TABLE `movies` DISABLE KEYS */;
INSERT INTO `movies` VALUES (1,'映画A','2025-06-01',120,'これは映画Aのあらすじです。','320.jpg','2025-05-21 06:45:18','2025-05-21 06:45:18'),(2,'映画B','2025-06-08',105,'これは映画Bのあらすじです。','320.jpg','2025-05-21 06:45:18','2025-05-21 06:45:18'),(3,'映画C','2025-06-15',98,'これは映画Cのあらすじです。','320.jpg','2025-05-21 06:45:18','2025-05-21 06:45:18'),(4,'映画D','2025-06-22',135,'これは映画Dのあらすじです。','320.jpg','2025-05-21 06:45:18','2025-05-21 06:45:18'),(5,'映画E','2025-06-29',110,'これは映画Eのあらすじです。','320.jpg','2025-05-21 06:45:18','2025-05-21 06:45:18'),(6,'映画F','2025-07-06',100,'これは映画Fのあらすじです。','320.jpg','2025-05-21 06:45:18','2025-05-21 06:45:18'),(7,'映画G','2025-07-13',115,'これは映画Gのあらすじです。','320.jpg','2025-05-21 06:45:18','2025-05-21 06:45:18'),(8,'映画H','2025-07-20',90,'これは映画Hのあらすじです。','320.jpg','2025-05-21 06:45:18','2025-05-21 06:45:18'),(9,'映画I','2025-07-27',125,'これは映画Iのあらすじです。','320.jpg','2025-05-21 06:45:18','2025-05-21 06:45:18'),(10,'映画J','2025-08-03',108,'これは映画Jのあらすじです。','320.jpg','2025-05-21 06:45:18','2025-05-21 06:45:18'),(11,'映画K','2025-08-10',130,'これは映画Kのあらすじです。','320.jpg','2025-05-21 06:45:18','2025-05-21 06:45:18'),(12,'映画L','2025-08-17',95,'これは映画Lのあらすじです。','320.jpg','2025-05-21 06:45:18','2025-05-21 06:45:18'),(13,'映画M','2025-08-24',122,'これは映画Mのあらすじです。','320.jpg','2025-05-21 06:45:18','2025-05-21 06:45:18'),(14,'映画N','2025-08-31',102,'これは映画Nのあらすじです。','320.jpg','2025-05-21 06:45:18','2025-05-21 06:45:18'),(15,'映画O','2025-09-07',118,'これは映画Oのあらすじです。','320.jpg','2025-05-21 06:45:18','2025-05-21 06:45:18'),(16,'映画P','2025-09-14',107,'これは映画Pのあらすじです。','320.jpg','2025-05-21 06:45:18','2025-05-21 06:45:18'),(17,'映画Q','2025-09-21',138,'これは映画Qのあらすじです。','320.jpg','2025-05-21 06:45:18','2025-05-21 06:45:18'),(18,'映画R','2025-09-28',93,'これは映画Rのあらすじです。','320.jpg','2025-05-21 06:45:18','2025-05-21 06:45:18'),(19,'映画S','2025-10-05',112,'これは映画Sのあらすじです。','320.jpg','2025-05-21 06:45:18','2025-05-21 06:45:18'),(20,'映画T','2025-10-12',103,'これは映画Tのあらすじです。','320.jpg','2025-05-21 06:45:18','2025-05-21 06:45:18');
/*!40000 ALTER TABLE `movies` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-21 16:00:55
