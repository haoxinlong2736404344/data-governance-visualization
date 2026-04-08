"""
公开零售数据集加载模块
用于将公开数据集标准化为项目内部字段
"""

from __future__ import annotations

import os
from typing import Optional

import pandas as pd


class PublicRetailDatasetLoader:
    """公开零售数据加载器（优先使用带渠道字段的数据集）"""

    DEFAULT_CANDIDATES = (
        "data/Online Retail.xlsx",
        "data/online_retail.xlsx",
        "data/online_retail.csv",
    )
    SUPERMARKET_CANDIDATES = (
        "data/supermarket_sales.csv",
        "data/Supermarket Sales.csv",
    )
    SUPERMARKET_FALLBACK_URL = (
        "https://raw.githubusercontent.com/sushantag9/"
        "Supermarket-Sales-Data-Analysis/master/supermarket_sales%20-%20Sheet1.csv"
    )
    SUPERSTORE_CANDIDATES = (
        "data/superstore_sales.csv",
        "data/Superstore sales dataset.csv",
    )
    SUPERSTORE_FALLBACK_URL = (
        "https://raw.githubusercontent.com/yajasarora/"
        "Superstore-Sales-Analysis-with-Tableau/master/Superstore%20sales%20dataset.csv"
    )

    def load_best_available(self) -> tuple[pd.DataFrame, str]:
        """优先加载区域和渠道维度更丰富的数据集，不可用时回退UCI数据集"""
        try:
            return self.load_superstore_sales(), "Superstore Sales（区域+渠道维度丰富）"
        except Exception:
            try:
                return self.load_supermarket_sales(), "Supermarket Sales（含渠道字段）"
            except Exception:
                return self.load_uci_online_retail(), "UCI Online Retail"

    def load_superstore_sales(self, filepath: Optional[str] = None) -> pd.DataFrame:
        """加载并标准化 Superstore 数据集（含 Ship Mode 和 Region）"""
        source_path = filepath or self._find_first_existing_superstore_path()
        if source_path:
            raw_df = pd.read_csv(source_path, encoding="utf-8-sig")
        else:
            raw_df = pd.read_csv(self.SUPERSTORE_FALLBACK_URL, encoding="latin1")

        return self._normalize_superstore_schema(raw_df)

    def load_supermarket_sales(self, filepath: Optional[str] = None) -> pd.DataFrame:
        """
        加载并标准化 Supermarket Sales 数据集
        该数据集原生包含 Payment 字段，可作为销售渠道
        """
        source_path = filepath or self._find_first_existing_supermarket_path()
        if source_path:
            raw_df = pd.read_csv(source_path)
        else:
            raw_df = pd.read_csv(self.SUPERMARKET_FALLBACK_URL)

        return self._normalize_supermarket_schema(raw_df)

    def load_uci_online_retail(self, filepath: Optional[str] = None) -> pd.DataFrame:
        """
        加载并标准化 UCI Online Retail 数据集

        输出字段与现有流程保持一致：
        order_id, order_date, customer_id, product_id, quantity, unit_price,
        region, channel, sales_amount, discount_rate
        """
        source_path = filepath or self._find_first_existing_path()
        if not source_path:
            raise FileNotFoundError(
                "未找到真实数据文件。请将 UCI 的 `Online Retail.xlsx` 放到 `data/` 目录。"
            )

        if source_path.lower().endswith(".csv"):
            raw_df = pd.read_csv(source_path)
        else:
            raw_df = pd.read_excel(source_path)

        return self._normalize_uci_schema(raw_df)

    def _find_first_existing_path(self) -> Optional[str]:
        for p in self.DEFAULT_CANDIDATES:
            if os.path.exists(p):
                return p
        return None

    def _find_first_existing_supermarket_path(self) -> Optional[str]:
        for p in self.SUPERMARKET_CANDIDATES:
            if os.path.exists(p):
                return p
        return None

    def _find_first_existing_superstore_path(self) -> Optional[str]:
        for p in self.SUPERSTORE_CANDIDATES:
            if os.path.exists(p):
                return p
        return None

    def _normalize_uci_schema(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        df = raw_df.copy()

        required = [
            "InvoiceNo",
            "StockCode",
            "Quantity",
            "InvoiceDate",
            "UnitPrice",
            "CustomerID",
            "Country",
        ]
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"数据字段不完整，缺少: {missing}")

        df = df[required].rename(
            columns={
                "InvoiceNo": "order_id",
                "StockCode": "product_id",
                "Quantity": "quantity",
                "InvoiceDate": "order_date",
                "UnitPrice": "unit_price",
                "CustomerID": "customer_id",
                "Country": "region",
            }
        )

        # 清理取消订单与明显异常值，确保业务口径更合理
        df = df[~df["order_id"].astype(str).str.upper().str.startswith("C")]
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
        df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
        df = df[(df["quantity"] > 0) & (df["unit_price"] > 0)]

        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
        df["customer_id"] = df["customer_id"].fillna("UNKNOWN").astype(str)
        df["order_id"] = df["order_id"].astype(str)
        df["product_id"] = df["product_id"].astype(str)
        df["region"] = df["region"].fillna("UNKNOWN").astype(str)

        # 兼容现有图表逻辑：补齐字段
        df["sales_amount"] = (df["quantity"] * df["unit_price"]).astype(float)
        df["discount_rate"] = 0.0
        df["channel"] = "online"

        final_columns = [
            "order_id",
            "order_date",
            "customer_id",
            "product_id",
            "quantity",
            "unit_price",
            "region",
            "channel",
            "sales_amount",
            "discount_rate",
        ]
        return df[final_columns].reset_index(drop=True)

    def _normalize_supermarket_schema(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        df = raw_df.copy()
        required = [
            "Invoice ID",
            "Date",
            "Customer type",
            "Product line",
            "Quantity",
            "Unit price",
            "City",
            "Payment",
            "Total",
        ]
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"Supermarket数据字段不完整，缺少: {missing}")

        df = df[required].rename(
            columns={
                "Invoice ID": "order_id",
                "Date": "order_date",
                "Customer type": "customer_id",
                "Product line": "product_id",
                "Quantity": "quantity",
                "Unit price": "unit_price",
                "City": "region",
                "Payment": "channel",
                "Total": "sales_amount",
            }
        )

        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
        df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
        df["sales_amount"] = pd.to_numeric(df["sales_amount"], errors="coerce")
        df = df[(df["quantity"] > 0) & (df["unit_price"] > 0) & (df["sales_amount"] > 0)]

        df["order_id"] = df["order_id"].astype(str)
        df["customer_id"] = df["customer_id"].fillna("UNKNOWN").astype(str)
        df["product_id"] = df["product_id"].fillna("UNKNOWN").astype(str)
        df["region"] = df["region"].fillna("UNKNOWN").astype(str)
        df["channel"] = df["channel"].fillna("UNKNOWN").astype(str)
        channel_map = {
            "Ewallet": "电子钱包",
            "Cash": "现金",
            "Credit card": "信用卡",
        }
        df["channel"] = df["channel"].map(lambda x: channel_map.get(x, x))
        df["discount_rate"] = 0.0

        final_columns = [
            "order_id",
            "order_date",
            "customer_id",
            "product_id",
            "quantity",
            "unit_price",
            "region",
            "channel",
            "sales_amount",
            "discount_rate",
        ]
        return df[final_columns].reset_index(drop=True)

    def _normalize_superstore_schema(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        df = raw_df.copy()
        if "ï»¿Row ID" in df.columns:
            df = df.rename(columns={"ï»¿Row ID": "Row ID"})

        required = [
            "Order ID",
            "Order Date",
            "Customer ID",
            "Product ID",
            "Quantity",
            "Sales",
            "State",
            "Region",
            "Ship Mode",
            "Discount",
            "City",
        ]
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"Superstore数据字段不完整，缺少: {missing}")

        df = df[required].rename(
            columns={
                "Order ID": "order_id",
                "Order Date": "order_date",
                "Customer ID": "customer_id",
                "Product ID": "product_id",
                "Quantity": "quantity",
                "Sales": "sales_amount",
                "State": "region",
                "Region": "region_type",
                "Ship Mode": "channel",
                "Discount": "discount_rate",
                "City": "city",
            }
        )

        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
        df["sales_amount"] = pd.to_numeric(df["sales_amount"], errors="coerce")
        df["discount_rate"] = pd.to_numeric(df["discount_rate"], errors="coerce").fillna(0.0)
        df = df[(df["quantity"] > 0) & (df["sales_amount"] > 0)]

        df["unit_price"] = (df["sales_amount"] / df["quantity"]).astype(float)
        df["order_id"] = df["order_id"].astype(str)
        df["customer_id"] = df["customer_id"].fillna("UNKNOWN").astype(str)
        df["product_id"] = df["product_id"].fillna("UNKNOWN").astype(str)
        df["region"] = df["region"].fillna("UNKNOWN").astype(str)
        df["region_type"] = df["region_type"].fillna("UNKNOWN").astype(str)
        df["city"] = df["city"].fillna("UNKNOWN").astype(str)
        df["channel"] = df["channel"].fillna("UNKNOWN").astype(str)

        channel_map = {
            "Standard Class": "标准配送",
            "Second Class": "次日达",
            "First Class": "优先配送",
            "Same Day": "当日达",
        }
        df["channel"] = df["channel"].map(lambda x: channel_map.get(x, x))

        final_columns = [
            "order_id",
            "order_date",
            "customer_id",
            "product_id",
            "quantity",
            "unit_price",
            "region",
            "region_type",
            "city",
            "channel",
            "sales_amount",
            "discount_rate",
        ]
        return df[final_columns].reset_index(drop=True)
