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
INSERT INTO `t_account` VALUES (1,'test_user_1','user1@example.com','pass123','山田 太郎','090-1111-2222','1985-04-15','genta',NULL),(2,'test_userだなも','user2@example.com','pass456','田中 花子','080-3333-4444','1990-07-20','1db7b703-801f-4a10-83eb-b1ff57b683c7.jpg',NULL),(3,'test_user_3','user3@example.com','pass789','佐藤 健太','070-5555-6666','1992-11-01','genta',NULL),(4,'test_user_4','user4@example.com','passabc','鈴木 美咲','090-7777-8888','1988-02-29','genta',NULL),(5,'test_user_5','user5@example.com','passxyz','高橋 雄大','080-9999-0000','1995-09-10','genta',NULL);
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
INSERT INTO `t_event` VALUES (1,'春開催、秋終了のイベント A','2025-04-01','2025-09-30','ID:1の説明。長期にわたるイベントです。','eventimage1.jpg','https://wwws.warnerbros.co.jp/minecraft-movie/news/?id=11'),(2,'境界値を含む長期イベント B','2025-05-26','2025-08-26','ID:2の説明。開始日と終了日が境界値。','eventimage2.jpg',NULL),(3,'3月から10月開催のイベント C','2025-03-15','2025-10-15','ID:3の説明。春から秋の開催です。','eventimage3.jpg','https://wwws.warnerbros.co.jp/minecraft-movie/news/?id=11'),(4,'初夏から晩秋のイベント D','2025-05-01','2025-11-30','ID:4の説明。長期間楽しめるイベント。','eventimage4.jpg',NULL),(5,'4月から9月開催のイベント E','2025-04-15','2025-09-15','ID:5の説明。季節をまたぐイベントです。','eventimage5.jpg','https://wwws.warnerbros.co.jp/minecraft-movie/news/?id=11'),(6,'長期開催イベント F','2025-03-05','2025-10-20','ID:6の説明。ランダムな画像とURLが設定されます。','eventimage1.jpg',NULL),(7,'長期開催イベント G','2025-04-25','2025-09-01','ID:7の説明。幅広い期間をカバーします。','eventimage2.jpg','https://wwws.warnerbros.co.jp/minecraft-movie/news/?id=11'),(8,'長期開催イベント H','2025-05-10','2025-10-05','ID:8の説明。テストデータのための架空イベント。','eventimage3.jpg',NULL),(9,'長期開催イベント I','2025-03-20','2025-11-15','ID:9の説明。データの多様性を確保します。','eventimage4.jpg','https://wwws.warnerbros.co.jp/minecraft-movie/news/?id=11'),(10,'長期開催イベント J','2025-04-05','2025-08-27','ID:10の説明。最終レコードです。','eventimage5.jpg',NULL),(11,'年末年始をまたぐイベント K','2025-08-26','2025-12-26','ID:11の説明。未来の長期イベントです。','eventimage1.jpg','https://wwws.warnerbros.co.jp/minecraft-movie/news/?id=11'),(12,'来年まで開催のイベント L','2025-09-10','2026-01-15','ID:12の説明。新年まで開催されます。','eventimage2.jpg',NULL),(13,'冬から春のイベント M','2025-10-01','2026-02-20','ID:13の説明。未来のイベント。','eventimage3.jpg','https://wwws.warnerbros.co.jp/minecraft-movie/news/?id=11'),(14,'未来の長期イベント N','2025-08-30','2026-01-30','ID:14の説明。テストデータの一部。','eventimage4.jpg',NULL),(15,'未来の長期イベント O','2025-09-20','2026-02-10','ID:15の説明。画像とURLはランダムに設定。','eventimage5.jpg','https://wwws.warnerbros.co.jp/minecraft-movie/news/?id=11'),(16,'未来の長期イベント P','2025-10-10','2026-03-05','ID:16の説明。来年度に終了。','eventimage1.jpg',NULL),(17,'未来の長期イベント Q','2025-11-01','2026-01-01','ID:17の説明。年をまたぎます。','eventimage2.jpg','https://wwws.warnerbros.co.jp/minecraft-movie/news/?id=11'),(18,'未来の長期イベント R','2025-09-05','2026-02-25','ID:18の説明。日付の範囲を確認してください。','eventimage3.jpg',NULL),(19,'未来の長期イベント S','2025-10-25','2026-03-10','ID:19の説明。多角的なテストを可能にします。','eventimage4.jpg','https://wwws.warnerbros.co.jp/minecraft-movie/news/?id=11'),(20,'未来の長期イベント T','2025-08-27','2026-01-20','ID:20の説明。データ生成ルールに従います。','eventimage5.jpg',NULL),(21,'冬季開催、春終了のイベント U','2025-01-01','2025-03-31','ID:21の説明。過去の短期イベントです。','eventimage1.jpg','https://wwws.warnerbros.co.jp/minecraft-movie/news/?id=11'),(22,'境界値を含む短期イベント V','2025-02-26','2025-05-26','ID:22の説明。開始日と終了日が境界値。','eventimage2.jpg',NULL),(23,'1月から4月開催のイベント W','2025-01-15','2025-04-15','ID:23の説明。短い期間の開催。','eventimage3.jpg','https://wwws.warnerbros.co.jp/minecraft-movie/news/?id=11'),(24,'冬から春のイベント X','2025-02-01','2025-05-01','ID:24の説明。季節の変わり目のイベント。','eventimage4.jpg',NULL),(25,'1月から4月開催のイベント Y','2025-01-20','2025-04-20','ID:25の説明。画像とURLはランダムに設定。','eventimage5.jpg','https://wwws.warnerbros.co.jp/minecraft-movie/news/?id=11'),(26,'過去の短期イベント Z','2025-02-10','2025-03-10','ID:26の説明。テスト用のダミーデータ。','eventimage1.jpg',NULL),(27,'過去の短期イベント AA','2025-01-05','2025-04-05','ID:27の説明。様々なパターンを含みます。','eventimage2.jpg','https://wwws.warnerbros.co.jp/minecraft-movie/news/?id=11'),(28,'過去の短期イベント BB','2025-02-15','2025-05-15','ID:28の説明。テーブルに挿入して使用できます。','eventimage3.jpg',NULL),(29,'過去の短期イベント CC','2025-01-25','2025-04-25','ID:29の説明。これで全レコードです。','eventimage4.jpg','https://wwws.warnerbros.co.jp/minecraft-movie/news/?id=11'),(30,'過去の短期イベント DD','2025-02-05','2025-05-05','ID:30の説明。テストデータ生成完了。','eventimage5.jpg',NULL);
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
INSERT INTO `t_movies` VALUES (1,'未来への扉 1','2025-01-10','2025-09-01',171,704383,'感動と興奮が詰まった物語の始まり。','movieimage4.jpg'),(2,'星の囁き 2','2025-02-15','2025-10-15',120,368007,'遠い宇宙からのメッセージが届く。','movieimage2.jpg'),(3,'時を越えて 3','2025-03-20','2025-08-26',116,422267,'過去と未来が交差するSFアドベンチャー。','movieimage4.jpg'),(4,'虹の向こう 4','2025-04-05','2025-11-05',81,845181,'希望を求めて旅立つ少年少女の物語。','movieimage4.jpg'),(5,'忘れられた歌 5','2025-05-01','2025-12-01',161,213272,'失われたメロディが世界を救うファンタジー。','movieimage3.jpg'),(6,'夜明けの誓い 6','2025-01-01','2026-01-01',175,241922,'新たな始まりを告げる勇者の物語。','movieimage2.jpg'),(7,'影の秘密 7','2025-02-01','2025-09-20',169,595469,'謎多き事件の真相に迫るミステリー。','movieimage2.jpg'),(8,'夢幻の園 8','2025-03-01','2025-10-05',103,105663,'不思議な世界での出会いと別れ。','movieimage3.jpg'),(9,'孤島の灯台 9','2025-04-10','2025-11-20',173,375375,'閉ざされた場所での人間模様を描く。','movieimage1.jpg'),(10,'嵐のあと 10','2025-05-26','2025-08-26',66,177114,'困難を乗り越えた先にある希望の物語。','movieimage4.jpg'),(11,'黄金の絆 11','2025-09-01','2026-01-15',64,34032,'友情と裏切りが織りなす壮大なドラマ。','movieimage1.jpg'),(12,'凍てつく炎 12','2025-10-10','2026-02-20',87,940511,'相反する力がぶつかり合うアクション。','movieimage1.jpg'),(13,'最後の選択 13','2025-08-26','2025-12-26',93,322056,'運命を決める決断の瞬間。','movieimage4.jpg'),(14,'未知なる旅 14','2025-11-01','2026-03-01',173,370677,'想像を超える冒険が始まる。','movieimage1.jpg'),(15,'記憶の破片 15','2025-12-05','2026-04-10',60,958664,'失われた記憶を辿るサスペンス。','movieimage4.jpg'),(16,'光の使者 16','2026-01-01','2026-05-01',60,684851,'世界を照らすヒーローの誕生。','movieimage3.jpg'),(17,'沈黙の街 17','2025-09-15','2026-01-05',63,904214,'誰もいない都市で何が起こったのか。','movieimage3.jpg'),(18,'運命の糸 18','2025-10-20','2026-02-15',111,846179,'出会うべくして出会う人々の物語。','movieimage5.jpg'),(19,'希望の砦 19','2025-11-25','2026-03-20',87,280537,'絶望の中で見つける希望の光。','movieimage4.jpg'),(20,'無限の空 20','2025-12-10','2026-04-05',150,596175,'自由を求めて旅立つ大冒険。','movieimage4.jpg'),(21,'青春の足跡 21','2025-01-01','2025-03-10',163,119505,'甘酸っぱい学生時代の思い出。','movieimage1.jpg'),(22,'古城の謎 22','2025-02-01','2025-04-15',143,463692,'廃墟となった城に隠された秘密。','movieimage2.jpg'),(23,'春風のエール 23','2025-03-01','2025-05-01',144,868780,'新生活を応援する心温まる物語。','movieimage2.jpg'),(24,'雪解けの音 24','2024-12-10','2025-02-20',123,982756,'冬が終わり、新しい季節が訪れる。','movieimage2.jpg'),(25,'始まりの場所 25','2025-03-26','2025-05-26',134,163474,'全ての物語が始まった場所。','movieimage5.jpg'),(26,'小さな奇跡 26','2025-01-15','2025-03-25',93,543514,'日常に隠されたささやかな感動。','movieimage5.jpg'),(27,'木漏れ日の庭 27','2025-02-10','2025-04-05',148,67355,'癒やしの空間で綴られる人間ドラマ。','movieimage1.jpg'),(28,'さよならの前に 28','2025-03-05','2025-05-10',110,713564,'別れと向き合う人々の切ない物語。','movieimage2.jpg'),(29,'懐かしの道 29','2024-11-20','2025-01-30',113,266575,'思い出が詰まった道を振り返る。','movieimage1.jpg'),(30,'新しい一日 30','2025-02-28','2025-04-20',85,59776,'毎日を大切に生きることの尊さ。','movieimage4.jpg');
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
INSERT INTO `t_scheduledshowing` VALUES (1,10,1,'2025-08-25'),(2,25,1,'2025-08-20');
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
INSERT INTO `t_seatreservation` VALUES (1,1,2,'A-5'),(2,2,2,'B-10');
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

-- Dump completed on 2025-06-09 11:49:23
