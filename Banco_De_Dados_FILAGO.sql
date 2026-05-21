/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.7.2-MariaDB, for Win64 (AMD64)
--
-- Host: 163.176.235.85    Database: filago
-- ------------------------------------------------------
-- Server version	10.6.23-MariaDB-0ubuntu0.22.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `upa_atendimento_eventos`
--

DROP TABLE IF EXISTS `upa_atendimento_eventos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `upa_atendimento_eventos` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `atendimento_id` bigint(20) unsigned NOT NULL,
  `unidade_id` bigint(20) unsigned NOT NULL,
  `setor_id` bigint(20) unsigned DEFAULT NULL,
  `usuario_id` bigint(20) unsigned DEFAULT NULL,
  `tipo_evento` enum('CHEGADA_QR','CHEGADA_TOTEM','CHEGADA_RECEPCAO','RECEPCAO_CHAMADO','RECEPCAO_INICIADA','RECEPCAO_FINALIZADA','TRIAGEM_CHAMADO','TRIAGEM_INICIADA','TRIAGEM_FINALIZADA','CLASSIFICACAO_DEFINIDA','CONSULTA_CHAMADO','CONSULTA_INICIADA','CONSULTA_FINALIZADA','MEDICACAO_ENCAMINHADO','OBSERVACAO_INICIADA','OBSERVACAO_FINALIZADA','ALTA','EVASAO','TRANSFERENCIA','CANCELAMENTO','REABERTURA') NOT NULL,
  `status_anterior` varchar(60) DEFAULT NULL,
  `status_novo` varchar(60) DEFAULT NULL,
  `observacao` text DEFAULT NULL,
  `criado_em` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_upa_eventos_atendimento` (`atendimento_id`),
  KEY `idx_upa_eventos_unidade_tipo` (`unidade_id`,`tipo_evento`),
  KEY `idx_upa_eventos_criado_em` (`criado_em`),
  KEY `fk_upa_eventos_setor` (`setor_id`),
  KEY `fk_upa_eventos_usuario` (`usuario_id`),
  CONSTRAINT `fk_upa_eventos_atendimento` FOREIGN KEY (`atendimento_id`) REFERENCES `upa_atendimentos` (`id`),
  CONSTRAINT `fk_upa_eventos_setor` FOREIGN KEY (`setor_id`) REFERENCES `upa_setores` (`id`),
  CONSTRAINT `fk_upa_eventos_unidade` FOREIGN KEY (`unidade_id`) REFERENCES `upa_unidades` (`id`),
  CONSTRAINT `fk_upa_eventos_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `upa_usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `upa_atendimento_eventos`
--

LOCK TABLES `upa_atendimento_eventos` WRITE;
/*!40000 ALTER TABLE `upa_atendimento_eventos` DISABLE KEYS */;
INSERT INTO `upa_atendimento_eventos` VALUES
(1,1,1,NULL,NULL,'CHEGADA_QR',NULL,'AGUARDANDO_RECEPCAO','Entrada registrada pelo fluxo público de QR Code.','2026-04-30 11:54:42'),
(2,1,1,1,1,'RECEPCAO_CHAMADO','AGUARDANDO_RECEPCAO','EM_RECEPCAO','Paciente chamado para recepcao.','2026-04-30 11:55:20'),
(3,2,1,NULL,NULL,'CHEGADA_QR',NULL,'AGUARDANDO_RECEPCAO','Entrada registrada pelo fluxo público de QR Code.','2026-04-30 12:01:33'),
(4,1,1,1,1,'RECEPCAO_FINALIZADA','EM_RECEPCAO','AGUARDANDO_TRIAGEM','Cadastro finalizado pela recepcao.','2026-04-30 12:01:57'),
(5,1,1,2,1,'TRIAGEM_CHAMADO','AGUARDANDO_TRIAGEM','EM_TRIAGEM','Paciente chamado para triagem.','2026-04-30 12:02:09'),
(6,1,1,2,1,'CLASSIFICACAO_DEFINIDA','EM_TRIAGEM','EM_TRIAGEM','Classificacao definida: Urgente (AMARELO).','2026-04-30 12:05:20'),
(7,1,1,2,1,'TRIAGEM_FINALIZADA','EM_TRIAGEM','AGUARDANDO_ATENDIMENTO','STETEST','2026-04-30 12:05:20'),
(8,1,1,3,1,'CONSULTA_CHAMADO','AGUARDANDO_ATENDIMENTO','EM_ATENDIMENTO','Paciente chamado para consulta medica.','2026-04-30 12:10:06'),
(9,1,1,3,1,'CONSULTA_FINALIZADA','EM_ATENDIMENTO','EM_OBSERVACAO','tsetete','2026-04-30 12:10:27'),
(10,1,1,3,1,'OBSERVACAO_INICIADA','EM_ATENDIMENTO','EM_OBSERVACAO','Desfecho medico: EM_OBSERVACAO.','2026-04-30 12:10:27');
/*!40000 ALTER TABLE `upa_atendimento_eventos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `upa_atendimentos`
--

DROP TABLE IF EXISTS `upa_atendimentos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `upa_atendimentos` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `unidade_id` bigint(20) unsigned NOT NULL,
  `protocolo` varchar(40) NOT NULL,
  `senha` varchar(20) NOT NULL,
  `numero_senha` int(11) NOT NULL,
  `paciente_nome` varchar(180) DEFAULT NULL,
  `paciente_cpf` varchar(14) DEFAULT NULL,
  `paciente_cns` varchar(20) DEFAULT NULL,
  `paciente_data_nascimento` date DEFAULT NULL,
  `paciente_nome_mae` varchar(180) DEFAULT NULL,
  `paciente_telefone` varchar(30) DEFAULT NULL,
  `tipo_entrada` enum('QR','TOTEM','RECEPCAO') NOT NULL DEFAULT 'QR',
  `status_atual` enum('AGUARDANDO_RECEPCAO','EM_RECEPCAO','AGUARDANDO_TRIAGEM','EM_TRIAGEM','AGUARDANDO_ATENDIMENTO','EM_ATENDIMENTO','AGUARDANDO_MEDICACAO','EM_OBSERVACAO','FINALIZADO','CANCELADO','EVASAO','TRANSFERIDO') NOT NULL DEFAULT 'AGUARDANDO_RECEPCAO',
  `classificacao_risco_id` bigint(20) unsigned DEFAULT NULL,
  `especialidade` varchar(100) DEFAULT 'Clínico Geral',
  `prioridade_legal` tinyint(1) NOT NULL DEFAULT 0,
  `prioridade_descricao` varchar(120) DEFAULT NULL,
  `chegada_em` datetime NOT NULL DEFAULT current_timestamp(),
  `recepcao_inicio_em` datetime DEFAULT NULL,
  `recepcao_fim_em` datetime DEFAULT NULL,
  `triagem_inicio_em` datetime DEFAULT NULL,
  `triagem_fim_em` datetime DEFAULT NULL,
  `atendimento_inicio_em` datetime DEFAULT NULL,
  `atendimento_fim_em` datetime DEFAULT NULL,
  `finalizado_em` datetime DEFAULT NULL,
  `cancelado_em` datetime DEFAULT NULL,
  `criado_por` bigint(20) unsigned DEFAULT NULL,
  `atualizado_por` bigint(20) unsigned DEFAULT NULL,
  `criado_em` datetime NOT NULL DEFAULT current_timestamp(),
  `atualizado_em` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_upa_atendimentos_protocolo` (`protocolo`),
  KEY `idx_upa_atendimentos_unidade_status` (`unidade_id`,`status_atual`),
  KEY `idx_upa_atendimentos_chegada` (`chegada_em`),
  KEY `idx_upa_atendimentos_senha` (`senha`),
  KEY `idx_upa_atendimentos_classificacao` (`classificacao_risco_id`),
  KEY `fk_upa_atendimentos_criado_por` (`criado_por`),
  KEY `fk_upa_atendimentos_atualizado_por` (`atualizado_por`),
  CONSTRAINT `fk_upa_atendimentos_atualizado_por` FOREIGN KEY (`atualizado_por`) REFERENCES `upa_usuarios` (`id`),
  CONSTRAINT `fk_upa_atendimentos_classificacao` FOREIGN KEY (`classificacao_risco_id`) REFERENCES `upa_classificacoes_risco` (`id`),
  CONSTRAINT `fk_upa_atendimentos_criado_por` FOREIGN KEY (`criado_por`) REFERENCES `upa_usuarios` (`id`),
  CONSTRAINT `fk_upa_atendimentos_unidade` FOREIGN KEY (`unidade_id`) REFERENCES `upa_unidades` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `upa_atendimentos`
--

LOCK TABLES `upa_atendimentos` WRITE;
/*!40000 ALTER TABLE `upa_atendimentos` DISABLE KEYS */;
INSERT INTO `upa_atendimentos` VALUES
(1,1,'UPA1-20260430115442-393436','P-001',1,'DANIEL LEITE FERREIRA','29558613835','65465456456','1981-08-05','VILMA LEITE','5646545645','QR','EM_OBSERVACAO',3,'Clínico Geral',1,NULL,'2026-04-30 11:54:42','2026-04-30 11:55:20','2026-04-30 12:01:57','2026-04-30 12:02:09','2026-04-30 12:05:20','2026-04-30 12:10:06','2026-04-30 12:10:27',NULL,NULL,NULL,1,'2026-04-30 11:54:42','2026-04-30 12:10:27'),
(2,1,'UPA1-20260430120133-846E41','P-002',2,'JOSÉ VALDIR','2464654465',NULL,'1981-05-05',NULL,NULL,'QR','AGUARDANDO_RECEPCAO',NULL,'Clínico Geral',1,NULL,'2026-04-30 12:01:33',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2026-04-30 12:01:33','2026-04-30 12:01:33'),
(3,1,'UPA1-20260514212629','P-EADA',1,'FELIPE',NULL,NULL,'1111-11-11',NULL,NULL,'QR','EM_TRIAGEM',1,'Clínico Geral',0,NULL,'2026-05-15 00:26:31',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2026-05-15 00:26:31','2026-05-15 00:26:31'),
(4,1,'UPA1-20260514213321','P-B1B',1,'John ',NULL,NULL,'1991-11-14',NULL,NULL,'QR','EM_TRIAGEM',1,'Clínico Geral',0,NULL,'2026-05-15 00:33:23',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2026-05-15 00:33:23','2026-05-15 00:33:23'),
(5,1,'UPA1-20260514213755','P-C55',1,'cARL',NULL,NULL,'1950-12-12',NULL,NULL,'QR','EM_TRIAGEM',1,'Clínico Geral',0,NULL,'2026-05-15 00:37:57',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2026-05-15 00:37:57','2026-05-15 00:37:57'),
(6,1,'UPA1-20260519094658','P-639',1,'Carlos',NULL,NULL,'1965-12-13',NULL,NULL,'QR','EM_TRIAGEM',1,'Clínico Geral',0,NULL,'2026-05-19 12:46:59',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2026-05-19 12:46:59','2026-05-19 12:46:59'),
(7,1,'UPA1-20260519102108','P-51F',1,'Carlos',NULL,NULL,'1965-12-13',NULL,NULL,'QR','EM_TRIAGEM',1,'Clínico Geral',0,NULL,'2026-05-19 13:21:09',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2026-05-19 13:21:09','2026-05-19 13:21:09'),
(8,1,'UPA1-20260519102119','P-3E8',1,'Carlos Lacerda',NULL,NULL,'1965-12-13',NULL,NULL,'QR','EM_TRIAGEM',1,'Clínico Geral',0,NULL,'2026-05-19 13:21:20',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2026-05-19 13:21:20','2026-05-19 13:21:20'),
(10,1,'UPA1-20260519140456','P-7F1',1,'Daniele',NULL,NULL,'1992-11-14',NULL,NULL,'QR','EM_TRIAGEM',1,'Clínico Geral',0,NULL,'2026-05-19 17:04:57',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2026-05-19 17:04:57','2026-05-19 17:04:57'),
(11,1,'UPA1-20260519141103','P-639',1,'Daniele Nogueira',NULL,NULL,'1992-11-14',NULL,NULL,'QR','EM_TRIAGEM',1,'Clínico Geral',0,NULL,'2026-05-19 17:11:04',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2026-05-19 17:11:04','2026-05-19 17:11:04'),
(12,1,'UPA1-20260519143055','P-6AE',1,'Daniele Nogueira',NULL,NULL,'1992-11-14',NULL,NULL,'QR','EM_TRIAGEM',1,'Clínico Geral',0,NULL,'2026-05-19 17:30:56',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2026-05-19 17:30:56','2026-05-19 17:30:56'),
(13,1,'UPA1-20260519143420','P-C73',1,'Daniele Nogueira',NULL,NULL,'1992-11-14',NULL,NULL,'QR','EM_TRIAGEM',1,'Clínico Geral',0,NULL,'2026-05-19 17:34:21',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2026-05-19 17:34:21','2026-05-19 17:34:21'),
(14,1,'UPA1-20260519165119','P-9F1',1,'Zoar Diana',NULL,NULL,'1992-12-13',NULL,NULL,'QR','EM_TRIAGEM',1,'Clínico Geral',0,NULL,'2026-05-19 19:51:20',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2026-05-19 19:51:20','2026-05-19 19:51:20'),
(15,1,'UPA1-20260519203026','P-771',1,'Zoar Diana',NULL,NULL,'1992-12-13',NULL,NULL,'QR','EM_TRIAGEM',1,'Clínico Geral',0,NULL,'2026-05-19 23:30:27',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2026-05-19 23:30:27','2026-05-19 23:30:27'),
(16,1,'UPA1-20260520183940','P-EBB',1,'Marcelo Costa',NULL,NULL,'1977-11-14',NULL,NULL,'QR','EM_TRIAGEM',2,'Clínico Geral',0,NULL,'2026-05-20 21:39:42',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2026-05-20 21:39:42','2026-05-20 21:39:42'),
(17,1,'UPA1-20260520202124','P-AC1',1,'Renan Santos',NULL,NULL,'2000-12-14',NULL,NULL,'QR','EM_TRIAGEM',1,'Clínico Geral',0,NULL,'2026-05-20 23:21:25',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2026-05-20 23:21:25','2026-05-20 23:21:25');
/*!40000 ALTER TABLE `upa_atendimentos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `upa_chamadas`
--

DROP TABLE IF EXISTS `upa_chamadas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `upa_chamadas` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `atendimento_id` bigint(20) unsigned NOT NULL,
  `unidade_id` bigint(20) unsigned NOT NULL,
  `setor_id` bigint(20) unsigned DEFAULT NULL,
  `usuario_id` bigint(20) unsigned DEFAULT NULL,
  `senha` varchar(20) NOT NULL,
  `local_chamada` varchar(120) NOT NULL,
  `tipo_chamada` enum('RECEPCAO','TRIAGEM','CONSULTORIO','MEDICACAO','OBSERVACAO') NOT NULL,
  `chamada_ativa` tinyint(1) NOT NULL DEFAULT 1,
  `chamado_em` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_upa_chamadas_unidade_ativa` (`unidade_id`,`chamada_ativa`),
  KEY `idx_upa_chamadas_chamado_em` (`chamado_em`),
  KEY `fk_upa_chamadas_atendimento` (`atendimento_id`),
  KEY `fk_upa_chamadas_setor` (`setor_id`),
  KEY `fk_upa_chamadas_usuario` (`usuario_id`),
  CONSTRAINT `fk_upa_chamadas_atendimento` FOREIGN KEY (`atendimento_id`) REFERENCES `upa_atendimentos` (`id`),
  CONSTRAINT `fk_upa_chamadas_setor` FOREIGN KEY (`setor_id`) REFERENCES `upa_setores` (`id`),
  CONSTRAINT `fk_upa_chamadas_unidade` FOREIGN KEY (`unidade_id`) REFERENCES `upa_unidades` (`id`),
  CONSTRAINT `fk_upa_chamadas_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `upa_usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `upa_chamadas`
--

LOCK TABLES `upa_chamadas` WRITE;
/*!40000 ALTER TABLE `upa_chamadas` DISABLE KEYS */;
INSERT INTO `upa_chamadas` VALUES
(1,1,1,1,1,'P-001','Recepção 1','RECEPCAO',1,'2026-04-30 11:55:20'),
(2,1,1,2,1,'P-001','Triagem 1','TRIAGEM',1,'2026-04-30 12:02:09'),
(3,1,1,3,1,'P-001','Consultório 1','CONSULTORIO',1,'2026-04-30 12:10:06');
/*!40000 ALTER TABLE `upa_chamadas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `upa_classificacoes_risco`
--

DROP TABLE IF EXISTS `upa_classificacoes_risco`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `upa_classificacoes_risco` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `nome` varchar(80) NOT NULL,
  `codigo` varchar(30) NOT NULL,
  `cor` varchar(30) NOT NULL,
  `ordem_prioridade` int(11) NOT NULL,
  `tempo_alvo_minutos` int(11) NOT NULL,
  `ativo` tinyint(1) NOT NULL DEFAULT 1,
  `criado_em` datetime NOT NULL DEFAULT current_timestamp(),
  `atualizado_em` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_upa_classificacoes_codigo` (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `upa_classificacoes_risco`
--

LOCK TABLES `upa_classificacoes_risco` WRITE;
/*!40000 ALTER TABLE `upa_classificacoes_risco` DISABLE KEYS */;
INSERT INTO `upa_classificacoes_risco` VALUES
(1,'Emergência','VERMELHO','#dc3545',1,0,1,'2026-04-30 10:14:13','2026-04-30 10:14:13'),
(2,'Muito Urgente','LARANJA','#fd7e14',2,10,1,'2026-04-30 10:14:13','2026-04-30 10:14:13'),
(3,'Urgente','AMARELO','#ffc107',3,60,1,'2026-04-30 10:14:13','2026-04-30 10:14:13'),
(4,'Pouco Urgente','VERDE','#28a745',4,120,1,'2026-04-30 10:14:13','2026-04-30 10:14:13'),
(5,'Não Urgente','AZUL','#0d6efd',5,240,1,'2026-04-30 10:14:13','2026-04-30 10:14:13');
/*!40000 ALTER TABLE `upa_classificacoes_risco` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `upa_senhas_controle`
--

DROP TABLE IF EXISTS `upa_senhas_controle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `upa_senhas_controle` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `unidade_id` bigint(20) unsigned NOT NULL,
  `data_referencia` date NOT NULL,
  `tipo_senha` enum('NORMAL','PRIORITARIA') NOT NULL DEFAULT 'NORMAL',
  `ultimo_numero` int(11) NOT NULL DEFAULT 0,
  `atualizado_em` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_upa_senhas_unidade_data_tipo` (`unidade_id`,`data_referencia`,`tipo_senha`),
  CONSTRAINT `fk_upa_senhas_unidade` FOREIGN KEY (`unidade_id`) REFERENCES `upa_unidades` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `upa_senhas_controle`
--

LOCK TABLES `upa_senhas_controle` WRITE;
/*!40000 ALTER TABLE `upa_senhas_controle` DISABLE KEYS */;
INSERT INTO `upa_senhas_controle` VALUES
(1,1,'2026-04-30','PRIORITARIA',2,'2026-04-30 12:01:33');
/*!40000 ALTER TABLE `upa_senhas_controle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `upa_setores`
--

DROP TABLE IF EXISTS `upa_setores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `upa_setores` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `unidade_id` bigint(20) unsigned NOT NULL,
  `nome` varchar(120) NOT NULL,
  `codigo` varchar(60) NOT NULL,
  `tipo` enum('RECEPCAO','TRIAGEM','CONSULTORIO','MEDICACAO','OBSERVACAO','ADMINISTRATIVO') NOT NULL,
  `ativo` tinyint(1) NOT NULL DEFAULT 1,
  `criado_em` datetime NOT NULL DEFAULT current_timestamp(),
  `atualizado_em` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_upa_setores_unidade_codigo` (`unidade_id`,`codigo`),
  KEY `idx_upa_setores_unidade` (`unidade_id`),
  CONSTRAINT `fk_upa_setores_unidade` FOREIGN KEY (`unidade_id`) REFERENCES `upa_unidades` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `upa_setores`
--

LOCK TABLES `upa_setores` WRITE;
/*!40000 ALTER TABLE `upa_setores` DISABLE KEYS */;
INSERT INTO `upa_setores` VALUES
(1,1,'Recepção 1','RECEPCAO-01','RECEPCAO',1,'2026-04-30 10:14:13','2026-04-30 10:14:13'),
(2,1,'Triagem 1','TRIAGEM-01','TRIAGEM',1,'2026-04-30 10:14:13','2026-04-30 10:14:13'),
(3,1,'Consultório 1','CONSULTORIO-01','CONSULTORIO',1,'2026-04-30 10:14:13','2026-04-30 10:14:13'),
(4,1,'Consultório 2','CONSULTORIO-02','CONSULTORIO',1,'2026-04-30 10:14:13','2026-04-30 10:14:13'),
(5,1,'Medicação','MEDICACAO-01','MEDICACAO',1,'2026-04-30 10:14:13','2026-04-30 10:14:13'),
(6,1,'Observação','OBSERVACAO-01','OBSERVACAO',1,'2026-04-30 10:14:13','2026-04-30 10:14:13');
/*!40000 ALTER TABLE `upa_setores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `upa_triagem`
--

DROP TABLE IF EXISTS `upa_triagem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `upa_triagem` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `atendimento_id` bigint(20) unsigned NOT NULL,
  `gestante` tinyint(1) DEFAULT 0,
  `nivel_dor` int(11) DEFAULT NULL,
  `saturacao` decimal(5,2) DEFAULT NULL,
  `temperatura` decimal(5,2) DEFAULT NULL,
  `pressao_arterial` varchar(20) DEFAULT NULL,
  `peso` decimal(5,2) DEFAULT NULL,
  `frequencia_cardiaca` decimal(5,2) DEFAULT NULL,
  `alergias` text DEFAULT NULL,
  `queixa_observacao` text DEFAULT NULL,
  `hipertenso` tinyint(1) DEFAULT 0,
  `diabetes` tinyint(1) DEFAULT 0,
  `cancer` tinyint(1) DEFAULT 0,
  `pneumopatia` tinyint(1) DEFAULT 0,
  `tosse` tinyint(1) DEFAULT 0,
  `outros_sintomas` tinyint(1) DEFAULT 0,
  `prioridade_clinica` tinyint(1) DEFAULT 0,
  `criado_em` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_triagem_atendimento` (`atendimento_id`),
  CONSTRAINT `fk_triagem_atendimento` FOREIGN KEY (`atendimento_id`) REFERENCES `upa_atendimentos` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `upa_triagem`
--

LOCK TABLES `upa_triagem` WRITE;
/*!40000 ALTER TABLE `upa_triagem` DISABLE KEYS */;
INSERT INTO `upa_triagem` VALUES
(1,3,1,1,84.00,40.00,'',60.00,100.00,'','',1,0,0,0,0,0,0,'2026-05-15 00:26:31'),
(2,4,0,7,89.00,36.00,'8',76.00,100.00,'','',1,0,0,0,0,0,0,'2026-05-15 00:33:23'),
(3,5,1,8,5.00,37.00,'10',60.00,100.00,'','',1,0,0,0,0,0,0,'2026-05-15 00:37:57'),
(4,6,0,8,94.00,37.00,'12',100.00,100.00,'Não','Dor no peito',1,0,0,0,0,0,0,'2026-05-19 12:46:59'),
(5,7,0,8,94.00,37.00,'',100.00,100.00,'Não','Dor no peito',1,0,0,0,0,0,0,'2026-05-19 13:21:09'),
(6,8,0,8,94.00,37.00,'',100.00,100.00,'Não','Dor no peito',1,0,0,0,0,0,0,'2026-05-19 13:21:20'),
(8,10,0,1,98.00,76.00,'7',NULL,NULL,'o','o',0,0,0,1,0,0,0,'2026-05-19 17:04:57'),
(9,11,0,1,98.00,76.00,'7',NULL,NULL,'o','o',0,0,1,0,0,0,0,'2026-05-19 17:11:04'),
(10,12,0,1,98.00,76.00,'7',NULL,NULL,'o','o',0,0,0,0,1,0,0,'2026-05-19 17:30:56'),
(11,13,0,1,98.00,76.00,'7',NULL,NULL,'o','o',0,0,0,0,1,0,0,'2026-05-19 17:34:21'),
(12,14,0,10,97.00,35.00,'',NULL,80.00,'','Dor de dente',0,0,0,0,0,1,0,'2026-05-19 19:51:20'),
(13,15,0,10,97.00,35.00,'',NULL,80.00,'','Dor de dente',0,0,0,0,0,1,0,'2026-05-19 23:30:27'),
(14,16,0,10,50.00,37.00,'',100.00,100.00,'-','Nada',0,0,0,0,0,1,0,'2026-05-20 21:39:42'),
(15,17,0,1,NULL,NULL,'',NULL,NULL,'','',0,0,0,0,0,0,0,'2026-05-20 23:21:25');
/*!40000 ALTER TABLE `upa_triagem` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `upa_unidades`
--

DROP TABLE IF EXISTS `upa_unidades`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `upa_unidades` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `nome` varchar(180) NOT NULL,
  `codigo` varchar(50) NOT NULL,
  `endereco` varchar(255) DEFAULT NULL,
  `telefone` varchar(30) DEFAULT NULL,
  `ativo` tinyint(1) NOT NULL DEFAULT 1,
  `criado_em` datetime NOT NULL DEFAULT current_timestamp(),
  `atualizado_em` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_upa_unidades_codigo` (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `upa_unidades`
--

LOCK TABLES `upa_unidades` WRITE;
/*!40000 ALTER TABLE `upa_unidades` DISABLE KEYS */;
INSERT INTO `upa_unidades` VALUES
(1,'UPA Central','UPA-CENTRAL',NULL,NULL,1,'2026-04-30 10:14:13','2026-04-30 10:14:13');
/*!40000 ALTER TABLE `upa_unidades` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `upa_usuarios`
--

DROP TABLE IF EXISTS `upa_usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `upa_usuarios` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `nome` varchar(180) NOT NULL,
  `login` varchar(80) NOT NULL,
  `email` varchar(180) DEFAULT NULL,
  `senha_hash` varchar(255) NOT NULL,
  `perfil` enum('ADMIN','RECEPCAO','TRIAGEM','MEDICO','GESTOR','PAINEL') NOT NULL,
  `unidade_id` bigint(20) unsigned DEFAULT NULL,
  `ativo` tinyint(1) NOT NULL DEFAULT 1,
  `ultimo_acesso_em` datetime DEFAULT NULL,
  `criado_em` datetime NOT NULL DEFAULT current_timestamp(),
  `atualizado_em` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_upa_usuarios_login` (`login`),
  KEY `idx_upa_usuarios_unidade` (`unidade_id`),
  CONSTRAINT `fk_upa_usuarios_unidade` FOREIGN KEY (`unidade_id`) REFERENCES `upa_unidades` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `upa_usuarios`
--

LOCK TABLES `upa_usuarios` WRITE;
/*!40000 ALTER TABLE `upa_usuarios` DISABLE KEYS */;
INSERT INTO `upa_usuarios` VALUES
(1,'Administrador do Sistema','admin','admin@upa.gov.br','$2y$10$fouOwao5c5fz7ciNslQ/I.dtDMf.N1EIl6XaQWfazYschajWj56SG','ADMIN',1,1,NULL,'2026-04-30 10:56:21','2026-04-30 10:56:21');
/*!40000 ALTER TABLE `upa_usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary table structure for view `vw_upa_fila_atual`
--

DROP TABLE IF EXISTS `vw_upa_fila_atual`;
/*!50001 DROP VIEW IF EXISTS `vw_upa_fila_atual`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `vw_upa_fila_atual` AS SELECT
 1 AS `id`,
  1 AS `unidade_id`,
  1 AS `unidade_nome`,
  1 AS `protocolo`,
  1 AS `senha`,
  1 AS `paciente_nome_mascarado`,
  1 AS `paciente_nome_completo`,
  1 AS `especialidade`,
  1 AS `status_atual`,
  1 AS `prioridade_legal`,
  1 AS `classificacao_nome`,
  1 AS `classificacao_codigo`,
  1 AS `classificacao_cor`,
  1 AS `ordem_prioridade`,
  1 AS `tempo_alvo_minutos`,
  1 AS `chegada_em`,
  1 AS `minutos_desde_chegada`,
  1 AS `minutos_espera_atendimento` */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `vw_upa_tempos_medios_classificacao`
--

DROP TABLE IF EXISTS `vw_upa_tempos_medios_classificacao`;
/*!50001 DROP VIEW IF EXISTS `vw_upa_tempos_medios_classificacao`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `vw_upa_tempos_medios_classificacao` AS SELECT
 1 AS `unidade_id`,
  1 AS `classificacao_nome`,
  1 AS `classificacao_cor`,
  1 AS `ordem_prioridade`,
  1 AS `data_referencia`,
  1 AS `total_pacientes_dia`,
  1 AS `tempo_medio_espera_minutos` */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `vw_upa_tempos_medios_dia`
--

DROP TABLE IF EXISTS `vw_upa_tempos_medios_dia`;
/*!50001 DROP VIEW IF EXISTS `vw_upa_tempos_medios_dia`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `vw_upa_tempos_medios_dia` AS SELECT
 1 AS `unidade_id`,
  1 AS `data_referencia`,
  1 AS `total_atendimentos`,
  1 AS `media_chegada_ate_recepcao`,
  1 AS `media_ate_triagem`,
  1 AS `media_triagem_ate_medico`,
  1 AS `media_total_unidade` */;
SET character_set_client = @saved_cs_client;

--
-- Dumping routines for database 'filago'
--

--
-- Final view structure for view `vw_upa_fila_atual`
--

/*!50001 DROP VIEW IF EXISTS `vw_upa_fila_atual`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`feliperibeiro`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_upa_fila_atual` AS select `a`.`id` AS `id`,`a`.`unidade_id` AS `unidade_id`,`u`.`nome` AS `unidade_nome`,`a`.`protocolo` AS `protocolo`,`a`.`senha` AS `senha`,concat(substring_index(`a`.`paciente_nome`,' ',1),' ',left(substring_index(`a`.`paciente_nome`,' ',-1),1),'.') AS `paciente_nome_mascarado`,`a`.`paciente_nome` AS `paciente_nome_completo`,`a`.`especialidade` AS `especialidade`,`a`.`status_atual` AS `status_atual`,`a`.`prioridade_legal` AS `prioridade_legal`,`cr`.`nome` AS `classificacao_nome`,`cr`.`codigo` AS `classificacao_codigo`,`cr`.`cor` AS `classificacao_cor`,`cr`.`ordem_prioridade` AS `ordem_prioridade`,`cr`.`tempo_alvo_minutos` AS `tempo_alvo_minutos`,`a`.`chegada_em` AS `chegada_em`,timestampdiff(MINUTE,`a`.`chegada_em`,current_timestamp()) AS `minutos_desde_chegada`,timestampdiff(MINUTE,coalesce(`a`.`triagem_fim_em`,`a`.`chegada_em`),current_timestamp()) AS `minutos_espera_atendimento` from ((`upa_atendimentos` `a` join `upa_unidades` `u` on(`u`.`id` = `a`.`unidade_id`)) left join `upa_classificacoes_risco` `cr` on(`cr`.`id` = `a`.`classificacao_risco_id`)) where `a`.`status_atual` not in ('FINALIZADO','CANCELADO','EVASAO','TRANSFERIDO') */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_upa_tempos_medios_classificacao`
--

/*!50001 DROP VIEW IF EXISTS `vw_upa_tempos_medios_classificacao`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`feliperibeiro`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_upa_tempos_medios_classificacao` AS select `a`.`unidade_id` AS `unidade_id`,`cr`.`nome` AS `classificacao_nome`,`cr`.`cor` AS `classificacao_cor`,`cr`.`ordem_prioridade` AS `ordem_prioridade`,cast(`a`.`chegada_em` as date) AS `data_referencia`,count(`a`.`id`) AS `total_pacientes_dia`,round(avg(case when `a`.`atendimento_inicio_em` is not null then timestampdiff(MINUTE,`a`.`chegada_em`,`a`.`atendimento_inicio_em`) else timestampdiff(MINUTE,`a`.`chegada_em`,current_timestamp()) end),0) AS `tempo_medio_espera_minutos` from (`upa_atendimentos` `a` join `upa_classificacoes_risco` `cr` on(`cr`.`id` = `a`.`classificacao_risco_id`)) where `a`.`status_atual` not in ('CANCELADO','EVASAO') group by `a`.`unidade_id`,`cr`.`nome`,`cr`.`cor`,`cr`.`ordem_prioridade`,cast(`a`.`chegada_em` as date) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_upa_tempos_medios_dia`
--

/*!50001 DROP VIEW IF EXISTS `vw_upa_tempos_medios_dia`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`feliperibeiro`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_upa_tempos_medios_dia` AS select `a`.`unidade_id` AS `unidade_id`,cast(`a`.`chegada_em` as date) AS `data_referencia`,count(0) AS `total_atendimentos`,round(avg(case when `a`.`recepcao_inicio_em` is not null then timestampdiff(MINUTE,`a`.`chegada_em`,`a`.`recepcao_inicio_em`) end),1) AS `media_chegada_ate_recepcao`,round(avg(case when `a`.`triagem_inicio_em` is not null then timestampdiff(MINUTE,coalesce(`a`.`recepcao_fim_em`,`a`.`chegada_em`),`a`.`triagem_inicio_em`) end),1) AS `media_ate_triagem`,round(avg(case when `a`.`atendimento_inicio_em` is not null then timestampdiff(MINUTE,coalesce(`a`.`triagem_fim_em`,`a`.`chegada_em`),`a`.`atendimento_inicio_em`) end),1) AS `media_triagem_ate_medico`,round(avg(case when `a`.`finalizado_em` is not null then timestampdiff(MINUTE,`a`.`chegada_em`,`a`.`finalizado_em`) end),1) AS `media_total_unidade` from `upa_atendimentos` `a` group by `a`.`unidade_id`,cast(`a`.`chegada_em` as date) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2026-05-20 21:02:58
