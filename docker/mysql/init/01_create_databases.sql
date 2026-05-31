SET NAMES utf8mb4;

-- 创建 meta 数据库
CREATE DATABASE IF NOT EXISTS meta CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建 dw 数据库
CREATE DATABASE IF NOT EXISTS dw CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 授权 test1 访问 dw
GRANT ALL PRIVILEGES ON dw.* TO 'test1'@'%';
FLUSH PRIVILEGES;

USE meta;

-- 表信息表（对应 TableInfoMySQL）
CREATE TABLE IF NOT EXISTS table_info (
    id VARCHAR(64) PRIMARY KEY COMMENT '表编号',
    name VARCHAR(128) COMMENT '表名称',
    role VARCHAR(32) COMMENT '表类型(fact/dim)',
    description TEXT COMMENT '表描述'
) CHARACTER SET utf8mb4 COMMENT='表元数据';

-- 字段信息表（对应 ColumnInfoMySQL）
CREATE TABLE IF NOT EXISTS column_info (
    id VARCHAR(64) PRIMARY KEY COMMENT '列编号',
    name VARCHAR(128) COMMENT '列名称',
    type VARCHAR(64) COMMENT '数据类型',
    role VARCHAR(32) COMMENT '列类型(primary_key/foreign_key/measure/dimension)',
    examples JSON COMMENT '数据示例',
    description TEXT COMMENT '列描述',
    alias JSON COMMENT '列别名',
    table_id VARCHAR(64) COMMENT '所属表编号'
) CHARACTER SET utf8mb4 COMMENT='字段元数据';

-- 指标信息表（对应 MetricInfoMySQL）
CREATE TABLE IF NOT EXISTS metric_info (
    id VARCHAR(64) PRIMARY KEY COMMENT '指标编码',
    name VARCHAR(128) COMMENT '指标名称',
    description TEXT COMMENT '指标描述',
    relevant_columns JSON COMMENT '关联字段',
    alias JSON COMMENT '指标别名'
) CHARACTER SET utf8mb4 COMMENT='指标元数据';

-- 字段-指标关联表（对应 ColumnMetricMySQL）
CREATE TABLE IF NOT EXISTS column_metric (
    column_id VARCHAR(64) NOT NULL COMMENT '列编号',
    metric_id VARCHAR(64) NOT NULL COMMENT '指标编号',
    PRIMARY KEY (column_id, metric_id)
) CHARACTER SET utf8mb4 COMMENT='字段指标关联';
