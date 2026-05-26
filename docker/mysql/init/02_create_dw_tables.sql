SET NAMES utf8mb4;
USE dw;

CREATE TABLE IF NOT EXISTS dim_region (
    region_id INT PRIMARY KEY AUTO_INCREMENT,
    province VARCHAR(100) COMMENT '省份',
    region_name VARCHAR(100) COMMENT '大区名称',
    country VARCHAR(100) COMMENT '国家'
) COMMENT='地区维度表';

CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_name VARCHAR(100) COMMENT '客户名称',
    gender VARCHAR(10) COMMENT '性别',
    member_level VARCHAR(50) COMMENT '会员等级'
) COMMENT='客户维度表';

CREATE TABLE IF NOT EXISTS dim_product (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    product_name VARCHAR(200) COMMENT '商品名称',
    category VARCHAR(100) COMMENT '品类',
    brand VARCHAR(100) COMMENT '品牌'
) COMMENT='商品维度表';

CREATE TABLE IF NOT EXISTS dim_date (
    date_id INT PRIMARY KEY COMMENT '日期ID，格式yyyyMMdd',
    year INT COMMENT '年份',
    quarter INT COMMENT '季度',
    month INT COMMENT '月份',
    day INT COMMENT '日'
) COMMENT='时间维度表';

CREATE TABLE IF NOT EXISTS fact_order (
    order_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT COMMENT '客户ID',
    product_id INT COMMENT '商品ID',
    date_id INT COMMENT '日期ID',
    region_id INT COMMENT '地区ID',
    order_quantity INT COMMENT '购买数量',
    order_amount DECIMAL(12,2) COMMENT '订单金额'
) COMMENT='订单事实表';

-- 插入示例数据
INSERT INTO dim_region (province, region_name, country) VALUES
('广东省', '华南', '中国'),
('浙江省', '华东', '中国'),
('北京市', '华北', '中国'),
('四川省', '西南', '中国');

INSERT INTO dim_customer (customer_name, gender, member_level) VALUES
('张三', '男', '黄金'),
('李四', '女', '钻石'),
('王五', '男', '普通'),
('赵六', '女', '白金');

INSERT INTO dim_product (product_name, category, brand) VALUES
('iPhone 15', '手机', '苹果'),
('MacBook Pro', '电脑', '苹果'),
('小米14', '手机', '小米'),
('耐克运动鞋', '鞋类', '耐克');

INSERT INTO dim_date (date_id, year, quarter, month, day) VALUES
(20240101, 2024, 1, 1, 1),
(20240201, 2024, 1, 2, 1),
(20240301, 2024, 1, 3, 1),
(20240401, 2024, 2, 4, 1);

INSERT INTO fact_order (customer_id, product_id, date_id, region_id, order_quantity, order_amount) VALUES
(1, 1, 20240101, 1, 2, 15998.00),
(2, 2, 20240201, 2, 1, 14999.00),
(3, 3, 20240301, 3, 1, 3999.00),
(4, 4, 20240401, 4, 3, 1197.00),
(1, 3, 20240101, 1, 1, 3999.00),
(2, 1, 20240201, 2, 1, 7999.00);
