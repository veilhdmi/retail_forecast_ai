import json
import os

from google.cloud import bigquery
from google.oauth2 import service_account


def _client() -> bigquery.Client:
    project = os.environ["GCP_PROJECT"]
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    if creds_json:
        info = json.loads(creds_json)
        credentials = service_account.Credentials.from_service_account_info(info)
        return bigquery.Client(project=project, credentials=credentials)
    return bigquery.Client(project=project)


def fetch_recent_sales_summary(days: int = 14) -> list[dict]:
    project = os.environ["GCP_PROJECT"]
    client = _client()

    query = f"""
        select
            product_category,
            sum(units_sold) as units_sold
        from `{project}.marts.fct_daily_category_sales`
        where sale_date >= date_sub(current_date(), interval {int(days)} day)
        group by product_category
        order by units_sold desc
    """
    return [dict(row) for row in client.query(query).result()]


def fetch_forecast_vs_stock() -> list[dict]:
    project = os.environ["GCP_PROJECT"]
    client = _client()

    query = f"""
        with demand as (
            select product_category, sum(forecast_units) as forecast_14d_units
            from `{project}.marts.fct_demand_forecast`
            group by product_category
        )
        select
            stock.product_category,
            stock.units_in_stock,
            round(demand.forecast_14d_units, 1) as forecast_14d_units
        from `{project}.marts.dim_current_stock` as stock
        left join demand using (product_category)
        order by demand.forecast_14d_units desc nulls last
    """
    return [dict(row) for row in client.query(query).result()]
