-- MySQL dump 10.13  Distrib 8.0.40, for macos14 (arm64)
--
-- Host: localhost    Database: material_management
-- ------------------------------------------------------
-- Server version	8.0.40

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
-- Table structure for table `acessorios`
--

DROP TABLE IF EXISTS `acessorios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `acessorios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `equipamento_id` int DEFAULT NULL,
  `tipo_acessorio` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `equipamento_id` (`equipamento_id`),
  CONSTRAINT `acessorios_ibfk_1` FOREIGN KEY (`equipamento_id`) REFERENCES `equipamentos` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `acessorios`
--

LOCK TABLES `acessorios` WRITE;
/*!40000 ALTER TABLE `acessorios` DISABLE KEYS */;
INSERT INTO `acessorios` VALUES (7,41,'Carregador'),(8,41,'Mala'),(9,42,'Carregador'),(10,42,'Mala');
/*!40000 ALTER TABLE `acessorios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `documentos`
--

DROP TABLE IF EXISTS `documentos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `documentos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `equipamento_id` int DEFAULT NULL,
  `escola_id` int DEFAULT NULL,
  `nome_arquivo` varchar(255) NOT NULL,
  `caminho_arquivo` varchar(255) NOT NULL,
  `data_upload` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `equipamento_id` (`equipamento_id`),
  KEY `escola_id` (`escola_id`),
  CONSTRAINT `documentos_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `documentos_ibfk_2` FOREIGN KEY (`equipamento_id`) REFERENCES `equipamentos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `documentos_ibfk_3` FOREIGN KEY (`escola_id`) REFERENCES `escolas` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `documentos`
--

LOCK TABLES `documentos` WRITE;
/*!40000 ALTER TABLE `documentos` DISABLE KEYS */;
INSERT INTO `documentos` VALUES (18,3,35,31,'Captura de ecrã 2024-11-18, às 10.56.27.png','static/uploads/Captura de ecrã 2024-11-18, às 10.56.27.png','2024-12-03 15:12:49');
/*!40000 ALTER TABLE `documentos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `equipamentos`
--

DROP TABLE IF EXISTS `equipamentos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `equipamentos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tipo` varchar(255) NOT NULL,
  `status` enum('Disponivel','Em uso','Em manutenção','Extraviado') NOT NULL DEFAULT 'Disponivel',
  `user_id` int DEFAULT NULL,
  `escola_id` int DEFAULT NULL,
  `data_aquisicao` date DEFAULT NULL,
  `data_ultimo_movimento` date DEFAULT NULL,
  `cedido_a_escola` int DEFAULT NULL,
  `serial_number` text,
  `aluno_CC` text,
  `observacoes` varchar(2000) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_serial_number` (`serial_number`(255)),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_escola_id` (`escola_id`),
  KEY `idx_cedido_a_escola` (`cedido_a_escola`)
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `equipamentos`
--

LOCK TABLES `equipamentos` WRITE;
/*!40000 ALTER TABLE `equipamentos` DISABLE KEYS */;
INSERT INTO `equipamentos` VALUES (34,'Tablet','Disponivel',NULL,2,'2024-11-19','2024-11-19',NULL,'SN6578',NULL,NULL),(35,'Tablet','Em uso',NULL,31,'2024-11-19','2024-12-03',33,'SN6577','12392',NULL),(36,'Tablet','Em uso',NULL,31,'2024-11-19','2024-11-20',32,'SN6578','0123213',NULL),(37,'Tablet','Em uso',NULL,31,'2024-11-19','2024-12-03',32,'SN6579','87',NULL),(38,'Tablet','Em uso',NULL,31,'2024-11-19','2024-12-03',32,'SN6580','CC12554',NULL),(39,'Tablet','Em uso',NULL,31,'2024-11-19','2024-12-03',33,'SN6581','98',NULL),(40,'Tablet','Em uso',NULL,7,'2024-11-19','2024-11-19',2,'SN6578','123',NULL),(41,'Tablet','Em uso',NULL,31,'2024-11-20','2024-12-03',32,'SN6','123456',NULL),(42,'Tablet','Em uso',NULL,31,'2024-12-03','2024-12-03',33,'SN66689','adsas',NULL);
/*!40000 ALTER TABLE `equipamentos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `escolas`
--

DROP TABLE IF EXISTS `escolas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `escolas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `escolas`
--

LOCK TABLES `escolas` WRITE;
/*!40000 ALTER TABLE `escolas` DISABLE KEYS */;
INSERT INTO `escolas` VALUES (1,'EBS NORDESTE'),(2,'EBI DA RIBEIRA GRANDE'),(3,'EBI DA MAIA'),(4,'EBI DE VILA DE CAPELAS'),(5,'ES LARANJEIRAS'),(6,'EBI DE ARRIFES'),(7,'Conservatório Regional de Ponta Delgada'),(8,'EBI ÁGUA DE PAU'),(9,'ES DA LAGOA'),(10,'ES ANTERO QUENTAL'),(11,'EBI ROBERTO IVENS'),(12,'ES DA RIBEIRA GRANDE'),(13,'EBI RABO DE PEIXE'),(14,'EBI PONTA GARÇA'),(15,'EBI DA LAGOA'),(16,'ES DOMINGOS REBELO'),(17,'EBI CANTO DA MAIA'),(18,'EBI DE GINETES'),(19,'EBS POVOAÇÃO'),(20,'EBS ARMANDO CÔRTES-RODRIGUES'),(21,'ES JERÓNIMO EMILIANO ANDRADE'),(22,'EBI DOS BISCOITOS'),(23,'ES VITORINO NEMÉSIO'),(24,'EBI DA PRAIA DA VITÓRIA'),(25,'EBS TOMÁS DE BORBA'),(26,'EBI DE ANGRA DO HEROÍSMO'),(27,'EBI FRANCISCO FERREIRA DRUMMOND'),(28,'EBS de Santa Maria'),(29,'EBI HORTA'),(30,'ES Manuel Arriaga'),(31,'EBS Lajes do Pico'),(32,'EBS S.Roque do Pico'),(33,'EBS da Madalena'),(34,'EBS das Velas'),(35,'EBS da Calheta'),(36,'EBI Topo'),(37,'EBS da Graciosa'),(38,'EBS das Flores'),(39,'EBS Mouzinho Silveira');
/*!40000 ALTER TABLE `escolas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ilha`
--

DROP TABLE IF EXISTS `ilha`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ilha` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome_ilha` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ilha`
--

LOCK TABLES `ilha` WRITE;
/*!40000 ALTER TABLE `ilha` DISABLE KEYS */;
INSERT INTO `ilha` VALUES (1,'São Miguel'),(2,'Terceira'),(3,'Pico'),(4,'Faial'),(5,'São Jorge'),(6,'Santa Maria'),(7,'Flores'),(8,'Corvo'),(9,'Graciosa');
/*!40000 ALTER TABLE `ilha` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ilha_escola`
--

DROP TABLE IF EXISTS `ilha_escola`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ilha_escola` (
  `escola_id` int NOT NULL,
  `ilha_id` int NOT NULL,
  PRIMARY KEY (`escola_id`,`ilha_id`),
  KEY `ilha_id` (`ilha_id`),
  CONSTRAINT `ilha_escola_ibfk_1` FOREIGN KEY (`escola_id`) REFERENCES `escolas` (`id`),
  CONSTRAINT `ilha_escola_ibfk_2` FOREIGN KEY (`ilha_id`) REFERENCES `ilha` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ilha_escola`
--

LOCK TABLES `ilha_escola` WRITE;
/*!40000 ALTER TABLE `ilha_escola` DISABLE KEYS */;
INSERT INTO `ilha_escola` VALUES (1,1),(2,1),(3,1),(4,1),(5,1),(6,1),(7,1),(8,1),(9,1),(10,1),(11,1),(12,1),(13,1),(14,1),(15,1),(16,1),(17,1),(18,1),(19,1),(20,1),(21,2),(22,2),(23,2),(24,2),(25,2),(26,2),(27,2),(31,3),(32,3),(33,3),(29,4),(30,4),(34,5),(35,5),(36,5),(28,6),(38,7),(39,8),(37,9);
/*!40000 ALTER TABLE `ilha_escola` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `email` varchar(150) NOT NULL,
  `cc` int DEFAULT NULL,
  `role` enum('admin','user') NOT NULL DEFAULT 'user',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `escola_id` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (2,'Rafael Pereira','$2b$12$JhzbzuTellkrfAtwXYInPORyiHOcm.PujCYjNltHnXTLLxRvNvrWi','rafael.b.pereira@azores.gov.pt',NULL,'admin','2024-11-05 16:14:58',NULL),(3,'Fábio Silva','$2b$12$Wa5WXCt91vAherN0JsclB.Gh8yZ8Jnjw8bA3C4KviZ6e6XA0eZiOa','Fabio.HV.Silva@edu.azores.gov.pt',NULL,'user','2024-11-05 16:34:28',31);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-12-03 14:15:24
