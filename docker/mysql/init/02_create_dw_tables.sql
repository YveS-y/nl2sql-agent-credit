SET NAMES utf8mb4;
USE dw;

-- ─────────────────────────────────────────
-- DIM 层（维度表）
-- ─────────────────────────────────────────

CREATE TABLE IF NOT EXISTS dim_product_type (
    product_type_id INT PRIMARY KEY AUTO_INCREMENT,
    product_name    VARCHAR(100)   NOT NULL COMMENT '产品名称',
    term_months     INT            NOT NULL COMMENT '还款期数',
    annual_rate     DECIMAL(5,4)   NOT NULL COMMENT '年化利率',
    max_loan_amount DECIMAL(10,2)  NOT NULL COMMENT '最高放款金额'
) COMMENT='产品类型维度表';

CREATE TABLE IF NOT EXISTS dim_channel (
    channel_id   INT PRIMARY KEY AUTO_INCREMENT,
    channel_name VARCHAR(100) NOT NULL COMMENT '渠道名称',
    channel_type VARCHAR(50)  NOT NULL COMMENT '渠道类型：线上/线下'
) COMMENT='渠道维度表';

CREATE TABLE IF NOT EXISTS dim_date (
    date_id INT PRIMARY KEY COMMENT '日期ID，格式yyyyMMdd',
    year    INT NOT NULL COMMENT '年份',
    month   INT NOT NULL COMMENT '月份',
    quarter INT NOT NULL COMMENT '季度',
    day     INT NOT NULL COMMENT '日'
) COMMENT='时间维度表';

-- ─────────────────────────────────────────
-- DWD 层（明细层）
-- ─────────────────────────────────────────

CREATE TABLE IF NOT EXISTS dwd_loan (
    loan_id         BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '放款唯一ID',
    borrower_id     BIGINT         NOT NULL COMMENT '借款人ID',
    product_type_id INT            NOT NULL COMMENT '产品类型，关联dim_product_type',
    channel_id      INT            NOT NULL COMMENT '放款渠道，关联dim_channel',
    loan_date_id    INT            NOT NULL COMMENT '放款日期，关联dim_date',
    loan_amount     DECIMAL(10,2)  NOT NULL COMMENT '放款金额',
    term_months     INT            NOT NULL COMMENT '还款期数',
    monthly_payment DECIMAL(10,2)  NOT NULL COMMENT '每月应还金额',
    loan_status     VARCHAR(20)    NOT NULL COMMENT '贷款状态：还款中/已结清/逾期/坏账'
) COMMENT='放款事实表，DWD层明细数据';

CREATE TABLE IF NOT EXISTS dwd_repayment (
    repayment_id   BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '还款记录ID',
    loan_id        BIGINT         NOT NULL COMMENT '关联放款ID',
    period         INT            NOT NULL COMMENT '第几期（1-12）',
    due_date_id    INT            NOT NULL COMMENT '应还款日期，关联dim_date',
    due_amount     DECIMAL(10,2)  NOT NULL COMMENT '应还金额',
    actual_date_id INT            NULL COMMENT '实际还款日期，NULL表示未还',
    actual_amount  DECIMAL(10,2)  NULL COMMENT '实际还款金额，NULL表示未还',
    status         VARCHAR(20)    NOT NULL COMMENT '状态：已还/逾期/未到期'
) COMMENT='还款记录表，DWD层明细数据';

CREATE TABLE IF NOT EXISTS dwd_overdue (
    overdue_id     BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '逾期记录ID',
    loan_id        BIGINT         NOT NULL COMMENT '关联放款ID',
    period         INT            NOT NULL COMMENT '逾期期数',
    overdue_days   INT            NOT NULL COMMENT '逾期天数',
    overdue_amount DECIMAL(10,2)  NOT NULL COMMENT '逾期金额',
    overdue_date_id INT           NOT NULL COMMENT '逾期日期，关联dim_date',
    bucket         VARCHAR(10)    NOT NULL COMMENT '逾期桶：M1/M2/M3+'
) COMMENT='逾期记录表，DWD层明细数据';

-- ─────────────────────────────────────────
-- ADS 层（已聚合结果，直接查）
-- ─────────────────────────────────────────

CREATE TABLE IF NOT EXISTS ads_loan_monthly (
    stat_month      VARCHAR(7)     NOT NULL COMMENT '统计月份，格式2025-01',
    channel_name    VARCHAR(100)   NOT NULL COMMENT '渠道名称',
    product_name    VARCHAR(100)   NOT NULL COMMENT '产品名称',
    loan_count      INT            NOT NULL COMMENT '放款笔数',
    loan_amount     DECIMAL(12,2)  NOT NULL COMMENT '放款总额',
    avg_loan_amount DECIMAL(10,2)  NOT NULL COMMENT '平均放款金额',
    PRIMARY KEY (stat_month, channel_name, product_name)
) COMMENT='月度放款汇总，ADS层已聚合';

CREATE TABLE IF NOT EXISTS ads_overdue_monthly (
    stat_month           VARCHAR(7)    NOT NULL COMMENT '统计月份，格式2025-01',
    channel_name         VARCHAR(100)  NOT NULL COMMENT '渠道名称',
    product_name         VARCHAR(100)  NOT NULL COMMENT '产品名称',
    due_count            INT           NOT NULL COMMENT '到期应还笔数',
    due_amount           DECIMAL(12,2) NOT NULL COMMENT '到期应还金额',
    overdue_count        INT           NOT NULL COMMENT '逾期笔数',
    overdue_amount       DECIMAL(12,2) NOT NULL COMMENT '逾期金额',
    m1_count             INT           NOT NULL COMMENT 'M1逾期笔数',
    m1_overdue_rate      DECIMAL(8,6)  NOT NULL COMMENT '首逾率：M1逾期笔数/到期笔数',
    overall_overdue_rate DECIMAL(8,6)  NOT NULL COMMENT '整体逾期率：逾期金额/应还金额',
    PRIMARY KEY (stat_month, channel_name, product_name)
) COMMENT='月度逾期汇总，ADS层已聚合';

-- ─────────────────────────────────────────
-- DIM 层静态数据
-- ─────────────────────────────────────────

INSERT INTO dim_product_type (product_name, term_months, annual_rate, max_loan_amount) VALUES
('消费分期12期', 12, 0.1800, 50000.00),
('消费分期6期',   6, 0.1600, 30000.00),
('小额消费贷3期', 3, 0.2400, 10000.00);

INSERT INTO dim_channel (channel_name, channel_type) VALUES
('自营APP',       '线上'),
('京东金融',      '线上'),
('抖音',          '线上'),
('线下门店-北京', '线下'),
('线下门店-上海', '线下');
