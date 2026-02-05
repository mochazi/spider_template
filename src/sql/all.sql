-- MySQL dump 10.13  Distrib 8.0.12, for Win64 (x86_64)
DROP TABLE IF EXISTS `spider_task`;
SET character_set_client = utf8mb4 ;
CREATE TABLE `spider_task` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url` varchar(1000) DEFAULT NULL COMMENT '爬虫需要的抓取数据需要的参数',
  `state` int(11) DEFAULT NULL COMMENT '任务状态',
  `parser_name` varchar(255) DEFAULT NULL COMMENT '任务解析器的脚本类名',
  `quantity_id` varchar(255) DEFAULT NULL COMMENT '分布式id',
  PRIMARY KEY (`id`),
  UNIQUE KEY `nui` (`url`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

LOCK TABLES `spider_task` WRITE;
UNLOCK TABLES;
