"""
生成信贷模拟数据并写入 MySQL dw 库。
运行前确保 docker-compose 已启动（MySQL 可连接）。
用法：uv run python scripts/generate_credit_data.py
"""

import random
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

import pymysql

# ── 连接配置（与 app_config.yaml 保持一致）─────────────────────────
DB_CFG = dict(host="localhost", port=3306, user="test1",
              password="123321", database="dw", charset="utf8mb4")

# ── 业务参数 ───────────────────────────────────────────────────────
LOAN_COUNT   = 30000
START_DATE   = date(2025, 1, 1)
END_DATE     = date(2026, 5, 31)
OVERDUE_RATE = 0.02   # 每期逾期概率，整体约6%

PRODUCTS = [
    {"product_type_id": 1, "product_name": "消费分期12期", "term_months": 12,
     "annual_rate": Decimal("0.1800"), "max_amount": Decimal("50000")},
    {"product_type_id": 2, "product_name": "消费分期6期",  "term_months": 6,
     "annual_rate": Decimal("0.1600"), "max_amount": Decimal("30000")},
    {"product_type_id": 3, "product_name": "小额消费贷3期", "term_months": 3,
     "annual_rate": Decimal("0.2400"), "max_amount": Decimal("10000")},
]

CHANNELS = [
    {"channel_id": 1, "channel_name": "自营APP"},
    {"channel_id": 2, "channel_name": "京东金融"},
    {"channel_id": 3, "channel_name": "抖音"},
    {"channel_id": 4, "channel_name": "线下门店-北京"},
    {"channel_id": 5, "channel_name": "线下门店-上海"},
]

# 渠道权重（自营APP最多）
CHANNEL_WEIGHTS = [0.35, 0.25, 0.20, 0.10, 0.10]
# 产品权重（12期最多）
PRODUCT_WEIGHTS = [0.50, 0.35, 0.15]


def date_to_id(d: date) -> int:
    return int(d.strftime("%Y%m%d"))


def monthly_payment(principal: Decimal, annual_rate: Decimal, months: int) -> Decimal:
    """等额还款月供，利率为0时直接均摊。"""
    if annual_rate == 0:
        return (principal / months).quantize(Decimal("0.01"), ROUND_HALF_UP)
    r = annual_rate / 12
    factor = r * (1 + r) ** months / ((1 + r) ** months - 1)
    return (principal * factor).quantize(Decimal("0.01"), ROUND_HALF_UP)


def random_date(start: date, end: date) -> date:
    return start + timedelta(days=random.randint(0, (end - start).days))


def build_dim_date(conn):
    """写入 dim_date，覆盖2025-01 ~ 2027-12（含最长12期还款周期）。"""
    cur = conn.cursor()
    cur.execute("DELETE FROM dim_date")
    rows = []
    d = date(2025, 1, 1)
    while d <= date(2027, 12, 31):
        rows.append((date_to_id(d), d.year, d.month, (d.month - 1) // 3 + 1, d.day))
        d += timedelta(days=1)
    cur.executemany(
        "INSERT INTO dim_date (date_id,year,month,quarter,day) VALUES (%s,%s,%s,%s,%s)",
        rows)
    conn.commit()
    print(f"  dim_date: {len(rows)} 行")


def generate_loans(conn):
    """生成 dwd_loan，返回 loan_id → loan 字典供后续使用。"""
    cur = conn.cursor()
    cur.execute("DELETE FROM dwd_loan")

    loans = []
    for i in range(1, LOAN_COUNT + 1):
        prod = random.choices(PRODUCTS, weights=PRODUCT_WEIGHTS)[0]
        chan = random.choices(CHANNELS, weights=CHANNEL_WEIGHTS)[0]
        min_amt = prod["max_amount"] * Decimal("0.10")
        amount = Decimal(random.randint(
            int(min_amt), int(prod["max_amount"])
        ))
        loan_date = random_date(START_DATE, END_DATE)
        mp = monthly_payment(amount, prod["annual_rate"], prod["term_months"])
        loans.append({
            "loan_id":         i,
            "borrower_id":     random.randint(100000, 999999),
            "product_type_id": prod["product_type_id"],
            "channel_id":      chan["channel_id"],
            "loan_date_id":    date_to_id(loan_date),
            "loan_date":       loan_date,
            "loan_amount":     amount,
            "term_months":     prod["term_months"],
            "monthly_payment": mp,
            "loan_status":     "还款中",   # 后面按逾期情况覆盖
            "product_name":    prod["product_name"],
            "channel_name":    chan["channel_name"],
            "annual_rate":     prod["annual_rate"],
        })

    cur.executemany(
        """INSERT INTO dwd_loan
           (loan_id,borrower_id,product_type_id,channel_id,loan_date_id,
            loan_amount,term_months,monthly_payment,loan_status)
           VALUES (%(loan_id)s,%(borrower_id)s,%(product_type_id)s,%(channel_id)s,
                   %(loan_date_id)s,%(loan_amount)s,%(term_months)s,
                   %(monthly_payment)s,%(loan_status)s)""",
        loans)
    conn.commit()
    print(f"  dwd_loan: {len(loans)} 行")
    return {l["loan_id"]: l for l in loans}


def generate_repayments(conn, loans: dict):
    """生成 dwd_repayment，标记逾期记录并返回逾期 loan_id 集合。"""
    cur = conn.cursor()
    cur.execute("DELETE FROM dwd_repayment")

    today = date(2026, 6, 1)   # 以2026-06-01为"今天"
    overdue_loan_ids = set()
    rows = []

    for loan in loans.values():
        for period in range(1, loan["term_months"] + 1):
            due_date = date(
                loan["loan_date"].year + (loan["loan_date"].month + period - 1) // 12,
                (loan["loan_date"].month + period - 1) % 12 + 1,
                min(loan["loan_date"].day, 28)
            )
            if due_date > today:
                status = "未到期"
                actual_date_id = None
                actual_amount  = None
            elif random.random() < OVERDUE_RATE:
                status = "逾期"
                actual_date_id = None
                actual_amount  = None
                overdue_loan_ids.add(loan["loan_id"])
            else:
                status = "已还"
                pay_date = due_date + timedelta(days=random.randint(0, 3))
                actual_date_id = date_to_id(pay_date)
                actual_amount  = loan["monthly_payment"]

            rows.append((
                loan["loan_id"], period, date_to_id(due_date),
                loan["monthly_payment"], actual_date_id, actual_amount, status
            ))

    cur.executemany(
        """INSERT INTO dwd_repayment
           (loan_id,period,due_date_id,due_amount,actual_date_id,actual_amount,status)
           VALUES (%s,%s,%s,%s,%s,%s,%s)""",
        rows)
    conn.commit()
    print(f"  dwd_repayment: {len(rows)} 行，逾期贷款: {len(overdue_loan_ids)} 笔")
    return overdue_loan_ids


def generate_overdue(conn, loans: dict, overdue_loan_ids: set):
    """生成 dwd_overdue，并回写 dwd_loan.loan_status。"""
    cur = conn.cursor()
    cur.execute("DELETE FROM dwd_overdue")

    rows = []
    for loan_id in overdue_loan_ids:
        loan = loans[loan_id]
        overdue_days = random.randint(1, 90)
        bucket = "M1" if overdue_days <= 30 else ("M2" if overdue_days <= 60 else "M3+")
        overdue_date = loan["loan_date"] + timedelta(days=random.randint(30, 180))
        rows.append((
            loan_id, 1, overdue_days, loan["monthly_payment"],
            date_to_id(overdue_date), bucket
        ))
        # 超过90天标为坏账，其余标逾期
        new_status = "坏账" if overdue_days > 60 else "逾期"
        cur.execute("UPDATE dwd_loan SET loan_status=%s WHERE loan_id=%s",
                    (new_status, loan_id))

    cur.executemany(
        """INSERT INTO dwd_overdue
           (loan_id,period,overdue_days,overdue_amount,overdue_date_id,bucket)
           VALUES (%s,%s,%s,%s,%s,%s)""",
        rows)
    conn.commit()
    print(f"  dwd_overdue: {len(rows)} 行")


def build_ads(conn, loans: dict):
    """聚合写入 ads_loan_monthly 和 ads_overdue_monthly。"""
    cur = conn.cursor()
    cur.execute("DELETE FROM ads_loan_monthly")
    cur.execute("DELETE FROM ads_overdue_monthly")

    # ── ads_loan_monthly ──────────────────────────────────────────
    from collections import defaultdict
    loan_agg = defaultdict(lambda: {"count": 0, "amount": Decimal("0")})
    for loan in loans.values():
        d = str(loan["loan_date"])[:7]   # "2025-01"
        key = (d, loan["channel_name"], loan["product_name"])
        loan_agg[key]["count"]  += 1
        loan_agg[key]["amount"] += loan["loan_amount"]

    loan_rows = []
    for (month, channel, product), v in loan_agg.items():
        avg = (v["amount"] / v["count"]).quantize(Decimal("0.01"), ROUND_HALF_UP)
        loan_rows.append((month, channel, product, v["count"], v["amount"], avg))

    cur.executemany(
        """INSERT INTO ads_loan_monthly
           (stat_month,channel_name,product_name,loan_count,loan_amount,avg_loan_amount)
           VALUES (%s,%s,%s,%s,%s,%s)""",
        loan_rows)

    # ── ads_overdue_monthly ───────────────────────────────────────
    # 取 dwd_repayment 中已到期的期次，按月/渠道/产品聚合
    cur.execute("""
        SELECT
            DATE_FORMAT(STR_TO_DATE(r.due_date_id, '%Y%m%d'), '%Y-%m') AS stat_month,
            dc.channel_name,
            dp.product_name,
            COUNT(*)                              AS due_count,
            SUM(r.due_amount)                     AS due_amount,
            SUM(r.status = '逾期')                AS overdue_count,
            SUM(CASE WHEN r.status='逾期' THEN r.due_amount ELSE 0 END) AS overdue_amount
        FROM dwd_repayment r
        JOIN dwd_loan l      ON r.loan_id = l.loan_id
        JOIN dim_channel dc   ON l.channel_id = dc.channel_id
        JOIN dim_product_type dp ON l.product_type_id = dp.product_type_id
        WHERE r.status IN ('已还','逾期')
        GROUP BY stat_month, dc.channel_name, dp.product_name
    """)
    repay_rows = cur.fetchall()

    # M1 count per (month, channel, product)
    cur.execute("""
        SELECT
            DATE_FORMAT(STR_TO_DATE(r.due_date_id, '%Y%m%d'), '%Y-%m') AS stat_month,
            dc.channel_name,
            dp.product_name,
            COUNT(*) AS m1_count
        FROM dwd_repayment r
        JOIN dwd_loan l      ON r.loan_id = l.loan_id
        JOIN dim_channel dc   ON l.channel_id = dc.channel_id
        JOIN dim_product_type dp ON l.product_type_id = dp.product_type_id
        JOIN dwd_overdue o   ON r.loan_id = o.loan_id AND r.period = o.period
        WHERE o.bucket = 'M1'
        GROUP BY stat_month, dc.channel_name, dp.product_name
    """)
    m1_map = {(r[0], r[1], r[2]): r[3] for r in cur.fetchall()}

    overdue_rows = []
    for row in repay_rows:
        month, channel, product, due_cnt, due_amt, ov_cnt, ov_amt = row
        m1_cnt = m1_map.get((month, channel, product), 0)
        m1_rate = Decimal(m1_cnt) / Decimal(due_cnt) if due_cnt else Decimal("0")
        ov_rate = Decimal(str(ov_amt)) / Decimal(str(due_amt)) if due_amt else Decimal("0")
        overdue_rows.append((
            month, channel, product,
            due_cnt, due_amt, ov_cnt, ov_amt,
            m1_cnt,
            m1_rate.quantize(Decimal("0.000001"), ROUND_HALF_UP),
            ov_rate.quantize(Decimal("0.000001"), ROUND_HALF_UP),
        ))

    cur.executemany(
        """INSERT INTO ads_overdue_monthly
           (stat_month,channel_name,product_name,due_count,due_amount,
            overdue_count,overdue_amount,m1_count,m1_overdue_rate,overall_overdue_rate)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        overdue_rows)

    conn.commit()
    print(f"  ads_loan_monthly: {len(loan_rows)} 行")
    print(f"  ads_overdue_monthly: {len(overdue_rows)} 行")


def main():
    print("连接数据库...")
    conn = pymysql.connect(**DB_CFG)
    try:
        print("写入 dim_date...")
        build_dim_date(conn)

        print("生成 dwd_loan...")
        loans = generate_loans(conn)

        print("生成 dwd_repayment...")
        overdue_ids = generate_repayments(conn, loans)

        print("生成 dwd_overdue...")
        generate_overdue(conn, loans, overdue_ids)

        print("聚合 ADS 层...")
        build_ads(conn, loans)

        print("\n完成！验证行数：")
        cur = conn.cursor()
        for table in ["dwd_loan", "dwd_repayment", "dwd_overdue",
                      "ads_loan_monthly", "ads_overdue_monthly"]:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            print(f"  {table}: {cur.fetchone()[0]}")
    finally:
        conn.close()


if __name__ == "__main__":
    random.seed(42)
    main()
