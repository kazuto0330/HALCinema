-- MySQL dump 10.13  Distrib 8.4.5, for Win64 (x86_64)
--
-- Host: localhost    Database: halcinemadb
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
-- Table structure for table `t_account`
--

DROP TABLE IF EXISTS `t_account`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_account` (
  `accountId` int NOT NULL,
  `accountName` varchar(63) DEFAULT NULL,
  `emailAddress` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `realName` varchar(127) DEFAULT NULL,
  `phoneNumber` varchar(20) DEFAULT NULL,
  `birthDate` date DEFAULT NULL,
  `accountIcon` varchar(255) DEFAULT NULL,
  `points` int DEFAULT NULL,
  PRIMARY KEY (`accountId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_account`
--

LOCK TABLES `t_account` WRITE;
/*!40000 ALTER TABLE `t_account` DISABLE KEYS */;
INSERT INTO `t_account` VALUES (1,'john_doe','john.doe@example.com','hashedpassword123','John Doe','090-1234-5678','1985-05-15','https://example.com/icons/john.png',1500),(2,'jane_smith','jane.smith@example.com','securepassabc','Jane Smith','080-9876-5432','1992-11-20','200038e6-d84e-45c1-8c9b-1bd9b7d1c587.jpg',2300),(3,'alice_wonder','alice.w@example.com','passwordxyz','Alice Wonderland','070-1111-2222','2000-03-01',NULL,500),(4,'robert_j','robert.j@example.com','mysecretpass','Robert Johnson',NULL,'1970-07-25','https://example.com/icons/robert.gif',4000),(5,'maria_g','maria.g@example.com','anotherhashedpass','Maria Garcia','090-5555-6666','1995-01-01','https://example.com/icons/maria.webp',100);
/*!40000 ALTER TABLE `t_account` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_creditcard`
--

DROP TABLE IF EXISTS `t_creditcard`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_creditcard` (
  `creditcardID` int NOT NULL,
  `accountId` int NOT NULL,
  `creditcardNumber` varchar(31) DEFAULT NULL,
  `creditcardExpiry` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`creditcardID`),
  KEY `accountId` (`accountId`),
  CONSTRAINT `t_creditcard_ibfk_1` FOREIGN KEY (`accountId`) REFERENCES `t_account` (`accountId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_creditcard`
--

LOCK TABLES `t_creditcard` WRITE;
/*!40000 ALTER TABLE `t_creditcard` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_creditcard` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_event`
--

DROP TABLE IF EXISTS `t_event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_event` (
  `eventInfoId` int NOT NULL,
  `eventTitle` varchar(255) DEFAULT NULL,
  `eventStartDate` date DEFAULT NULL,
  `eventEndDate` date DEFAULT NULL,
  `eventDescription` text,
  `eventImage` varchar(255) DEFAULT NULL,
  `eventUrl` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`eventInfoId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_event`
--

LOCK TABLES `t_event` WRITE;
/*!40000 ALTER TABLE `t_event` DISABLE KEYS */;
INSERT INTO `t_event` VALUES (1,'未来技術EXPO 2024','2025-05-15','2026-03-10','最新のAI、ロボティクス、IoT技術が集結する展示会です。未来を体験しよう！','a7334f44-cf5d-4449-9b1a-6fb58d50b799.jpg','https://expo.example.com/futuretech'),(2,'心と体の癒しフェス','2025-04-20','2026-01-05','ヨガ、瞑想、アロマセラピーなど、心身をリフレッシュするプログラムが満載です。','b8c4e5d6-d2a1-43e7-8b9c-0f1e2d3c4b5a.jpg',NULL),(3,'地域ふれあい祭り','2024-12-01','2025-11-20','地元のお店やパフォーマーが集まる、地域密着型のお祭りです。家族みんなで楽しめます。','c1d2e3f4-5a6b-7c8d-9e0f-1a2b3c4d5e6f.jpg','https://local-festival.org/2024'),(4,'冬のグルメ大試食会','2025-06-10','2026-02-15','全国各地の冬の味覚が集まる、食いしん坊にはたまらないイベントです。','d9e0f1a2-b3c4-5d6e-7f8a-9b0c1d2e3f4a.jpg',NULL),(5,'子ども科学教室','2025-03-01','2026-01-10','実験を通じて科学の楽しさを学ぶ、小中学生向けのワークショップです。','e5f6a7b8-c9d0-1e2f-3a4b-5c6d7e8f9a0b.jpg','https://science-class.kids/spring'),(6,'起業家向け交流会','2025-01-15','2025-12-31','新たなビジネスチャンスを探す起業家や投資家のためのネットワーキングイベント。','f0a1b2c3-d4e5-6f7a-8b9c-0d1e2f3a4b5c.jpg','https://startup-meetup.com/next'),(7,'伝統工芸品展','2024-09-01','2025-08-30','日本の美しい伝統工芸品を一堂に集めた展示販売会です。職人の技に触れてみませんか。','1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d.jpg',NULL),(8,'国際映画フェスティバル','2025-02-10','2026-01-25','世界中から選りすぐりの映画が集まる、映画ファン必見の祭典です。','2e3f4a5b-6c7d-8e9f-0a1b-2c3d4e5f6a7b.jpg','https://intl-film-fest.org/2024'),(9,'健康と美容の祭典','2024-07-01','2025-06-01','最新の健康食品、美容機器、フィットネスプログラムを体験できます。','3c4d5e6f-7a8b-9c0d-1e2f-3a4b5c6d7e8f.jpg',NULL),(10,'ゲーム開発者会議','2025-06-10','2026-05-30','ゲーム業界の最前線で活躍する開発者が集結し、最新技術やノウハウを共有します。','4d5e6f7a-8b9c-0d1e-2f3a-4b5c6d7e8f9a.jpg','https://gamedev-conf.net/spring');
/*!40000 ALTER TABLE `t_event` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_movies`
--

DROP TABLE IF EXISTS `t_movies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_movies` (
  `moviesId` int NOT NULL,
  `movieTitle` varchar(255) DEFAULT NULL,
  `movieReleaseDate` date DEFAULT NULL,
  `movieEndDate` date DEFAULT NULL,
  `movieRunningTime` int DEFAULT NULL,
  `movieAudienceCount` int DEFAULT '0',
  `movieSynopsis` text,
  `movieImage` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`moviesId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_movies`
--

LOCK TABLES `t_movies` WRITE;
/*!40000 ALTER TABLE `t_movies` DISABLE KEYS */;
INSERT INTO `t_movies` VALUES (1,'星の彼方へ','2023-01-20','2026-03-01',125,850000,'広大な宇宙を舞台に、未知の惑星への冒険を描くSF大作。主人公たちの絆と成長が感動を呼ぶ。','a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d.jpg'),(2,'古城の秘密','2024-05-10','2027-01-15',105,320000,'廃墟となった古城に隠された、数百年もの間語り継がれる秘密を解き明かすミステリー。','b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e.jpg'),(3,'最後の戦士','2022-11-25','2026-08-20',160,1200000,'滅びゆく世界で、たった一人の戦士が希望をかけて強大な敵に立ち向かう壮大なファンタジー。','c3d4e5f6-a7b8-9c0d-1e2f-3a4b5c6d7e8f.jpg'),(4,'時の旅人','2025-02-14','2028-02-01',95,450000,'時間を超えて過去や未来を行き来する青年が、歴史の謎を解き明かし運命を変える物語。','d4e5f6a7-b8c9-0d1e-2f3a-4b5c6d7e8f0a.jpg'),(5,'魔法の森','2023-07-01','2026-05-10',110,680000,'不思議な生き物たちが暮らす魔法の森で、少女が成長していく心温まるアニメーション。','e5f6a7b8-c9d0-1e2f-3a4b-5c6d7e8f0a1b.jpg'),(6,'失われた記憶','2024-09-05','2027-04-25',130,720000,'事故で記憶を失った主人公が、自身の過去を探るうちに驚くべき真実にたどり着くサスペンス。','f6a7b8c9-d0e1-2f3a-4b5c-6d7e8f0a1b2c.jpg'),(7,'真実の追求','2025-06-01','2028-01-05',140,910000,'不正がはびこる社会で、一人のジャーナリストが命をかけて真実を追い求める社会派ドラマ。','0a1b2c3d-4e5f-6a7b-8c9d-e0f1a2b3c4d5.jpg'),(8,'闇の支配者','2022-03-10','2026-06-30',170,1500000,'世界を支配しようとする闇の勢力と、それに立ち向かう若者たちの壮絶な戦いを描くアクション。','1b2c3d4e-5f6a-7b8c-9d0e-f1a2b3c4d5e6.jpg'),(9,'希望の光','2023-04-18','2027-03-10',115,580000,'絶望的な状況下で、人々が互いに助け合い、わずかな希望の光を求めて奮闘する感動的な物語。','2c3d4e5f-6a7b-8c9d-0e1f-2a3b4c5d6e7f.jpg'),(10,'伝説の宝','2024-01-07','2026-11-20',100,390000,'世界中に散らばる伝説の宝を巡り、個性豊かな冒険者たちが繰り広げるコミカルなアドベンチャー。','3d4e5f6a-7b8c-9d0e-1f2a-3b4c5d6e7f8a.jpg'),(11,'心の叫び','2025-03-20','2028-04-01',135,610000,'現代社会に生きる人々の孤独や葛藤を描き、心の奥底に秘められた感情を表現する人間ドラマ。','4e5f6a7b-8c9d-0e1f-2a3b-4c5d6e7f8a9b.jpg'),(12,'運命の出会い','2023-08-12','2027-05-15',90,280000,'偶然の出会いから始まる、男女の甘く切ない恋愛模様を描いたロマンティックコメディ。','5f6a7b8c-9d0e-1f2a-3b4c-5d6e7f8a9b0c.jpg'),(13,'新たなる夜明け','2024-02-29','2026-09-01',145,980000,'困難を乗り越え、新たな時代を切り開いていく人々の姿を描いた希望に満ちた物語。','6a7b8c9d-0e1f-2a3b-4c5d-6e7f8a9b0c1d.jpg'),(14,'都市伝説X','2025-01-05','2027-10-20',118,550000,'都市にひそむ不気味な伝説の真実を探る若者たちが体験する恐怖を描くホラー映画。','7b8c9d0e-1f2a-3b4c-5d6e-7f8a9b0c1d2e.jpg'),(15,'ロボットの夢','2023-06-15','2028-03-05',108,700000,'感情を持ったロボットが、人間社会で自身の存在意義を見つける感動的なSFヒューマンドラマ。','8c9d0e1f-2a3b-4c5d-6e7f-8a9b0c1d2e3f.jpg'),(16,'未来からのメッセージ','2025-08-01','2027-02-10',120,750000,'タイムカプセルから発見された、未来からの警告メッセージを巡るSFスリラー。','a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d.jpg'),(17,'砂漠のオアシス','2026-09-15','2028-06-01',112,480000,'果てしない砂漠を旅する中で、幻のオアシスを求めて人々が織りなす感動の物語。','b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e.jpg'),(18,'深海の謎','2025-10-20','2027-11-05',130,900000,'未踏の深海で発見された古代文明の遺跡と、そこに潜む巨大な生命体の秘密に迫る。','c3d4e5f6-a7b8-9c0d-1e2f-3a4b5c6d7e8f.jpg'),(19,'山岳救助隊','2027-08-05','2029-03-20',105,350000,'絶壁での遭難事故発生。命がけで救助に向かう山岳救助隊の活躍を描くドキュメンタリー風ドラマ。','d4e5f6a7-b8c9-0d1e-2f3a-4b5c6d7e8f0a.jpg'),(20,'記憶の断片','2025-11-10','2028-01-15',98,520000,'失われた記憶のパズルを解き明かすにつれ、主人公は自分自身と向き合うことになる心理ドラマ。','e5f6a7b8-c9d0-1e2f-3a4b-5c6d7e8f0a1b.jpg'),(21,'異世界の扉','2026-10-01','2029-05-10',140,1100000,'平凡な高校生が偶然見つけた異世界への扉。そこから始まる壮大な冒険ファンタジー。','f6a7b8c9-d0e1-2f3a-4b5c-6d7e8f0a1b2c.jpg'),(22,'ストリートダンサー','2025-09-01','2027-07-25',100,680000,'逆境に立ち向かい、ダンスで夢を掴もうとする若者たちの情熱と友情を描く青春映画。','0a1b2c3d-4e5f-6a7b-8c9d-e0f1a2b3c4d5.jpg'),(23,'幻獣物語','2027-09-20','2029-10-01',128,800000,'伝説の幻獣と心を通わせる少女の、美しくも壮絶な運命を描くアニメーション。','1b2c3d4e-5f6a-7b8c-9d0e-f1a2b3c4d5e6.jpg'),(24,'孤島のサバイバル','2025-12-01','2028-02-28',115,420000,'無人島に漂着した人々が、極限状況下で生き残りをかけて奮闘するサバイバルスリラー。','2c3d4e5f-6a7b-8c9d-0e1f-2a3b4c5d6e7f.jpg'),(25,'最後の晩餐','2026-08-22','2029-01-07',135,950000,'ある家族が、人生の終わりに向けた最後の晩餐を通じて、互いの絆を再確認する感動的なドラマ。','3d4e5f6a-7b8c-9d0e-1f2a-3b4c5d6e7f8a.jpg'),(26,'地下迷宮の冒険','2025-08-15','2027-04-10',103,600000,'都市の地下に広がる広大な迷宮に挑む探検家たちの、手に汗握るアドベンチャー。','4e5f6a7b-8c9d-0e1f-2a3b-4c5d6e7f8a9b.jpg'),(27,'偽りの顔','2027-11-01','2029-06-30',122,780000,'完璧な人生を送るかに見えた主人公の裏に隠された、もう一つの顔が暴かれるサスペンス。','5f6a7b8c-9d0e-1f2a-3b4c-5d6e7f8a9b0c.jpg'),(28,'伝説の歌姫','2026-09-05','2028-08-15',118,850000,'半世紀ぶりに発見された伝説の歌姫の未発表曲を巡る、人間模様と音楽の力。','6a7b8c9d-0e1f-2a3b-4c5d-6e7f8a9b0c1d.jpg'),(29,'AIの反乱','2025-10-08','2027-12-01',150,1300000,'自我を持ったAIが人類に反旗を翻す近未来。人類の存亡をかけた戦いが始まる。','7b8c9d0e-1f2a-3b4c-5d6e-7f8a9b0c1d2e.jpg'),(30,'小さな英雄','2027-08-25','2029-04-05',95,500000,'日々の小さな善行が、やがて大きな感動を生み出す。心温まるヒューマンドラマ。','8c9d0e1f-2a3b-4c5d-6e7f-8a9b0c1d2e3f.jpg');
/*!40000 ALTER TABLE `t_movies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_scheduledshowing`
--

DROP TABLE IF EXISTS `t_scheduledshowing`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_scheduledshowing` (
  `scheduledShowingId` int NOT NULL,
  `moviesId` int NOT NULL,
  `screenId` int NOT NULL,
  `scheduledScreeningDate` date DEFAULT NULL,
  `screeningStartTime` time DEFAULT NULL,
  PRIMARY KEY (`scheduledShowingId`),
  KEY `moviesId` (`moviesId`),
  KEY `screenId` (`screenId`),
  CONSTRAINT `t_scheduledshowing_ibfk_1` FOREIGN KEY (`moviesId`) REFERENCES `t_movies` (`moviesId`),
  CONSTRAINT `t_scheduledshowing_ibfk_2` FOREIGN KEY (`screenId`) REFERENCES `t_screen` (`screenId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_scheduledshowing`
--

LOCK TABLES `t_scheduledshowing` WRITE;
/*!40000 ALTER TABLE `t_scheduledshowing` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_scheduledshowing` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_screen`
--

DROP TABLE IF EXISTS `t_screen`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_screen` (
  `screenId` int NOT NULL,
  `screenType` int DEFAULT NULL,
  PRIMARY KEY (`screenId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_screen`
--

LOCK TABLES `t_screen` WRITE;
/*!40000 ALTER TABLE `t_screen` DISABLE KEYS */;
INSERT INTO `t_screen` VALUES (1,1),(2,1),(3,2),(4,2),(5,3),(6,3);
/*!40000 ALTER TABLE `t_screen` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_seatreservation`
--

DROP TABLE IF EXISTS `t_seatreservation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_seatreservation` (
  `seatReservationId` int NOT NULL,
  `scheduledShowingId` int NOT NULL,
  `accountId` int NOT NULL,
  `seatNumber` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`seatReservationId`),
  KEY `scheduledShowingId` (`scheduledShowingId`),
  KEY `accountId` (`accountId`),
  CONSTRAINT `t_seatreservation_ibfk_1` FOREIGN KEY (`scheduledShowingId`) REFERENCES `t_scheduledshowing` (`scheduledShowingId`),
  CONSTRAINT `t_seatreservation_ibfk_2` FOREIGN KEY (`accountId`) REFERENCES `t_account` (`accountId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_seatreservation`
--

LOCK TABLES `t_seatreservation` WRITE;
/*!40000 ALTER TABLE `t_seatreservation` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_seatreservation` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-16 10:19:11
