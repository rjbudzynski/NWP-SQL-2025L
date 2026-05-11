import marimo

__generated_with = "0.23.5"
app = marimo.App(width="medium")


@app.cell
def imports():
    import marimo as mo
    import json
    import urllib.request
    import urllib.error
    from datetime import date, timedelta
    from pathlib import Path
    import polars as pl

    DATA_DIR = Path("data")
    return DATA_DIR, date, json, mo, pl, timedelta, urllib


@app.cell(hide_code=True)
def title(mo):
    mo.md(r"""
    # Acquire Historical Weather Data — Warsaw

    This notebook fetches daily temperature records for Warsaw, Poland from the
    [Open-Meteo Archive API](https://open-meteo.com/en/docs/historical-weather-api)
    (free, no API key required), saves them to CSV, and converts to Parquet
    format using DuckDB via marimo's built-in SQL cells.

    **Pipeline:**

    1. Fetch daily mean, max, and min temperatures (2001-01-01 → today)
    2. Save as CSV with the first/last dates in the filename
    3. Read CSV with DuckDB and write as Parquet (dates typed as `DATE`)
    """)
    return


@app.cell(hide_code=True)
def step1_intro(mo):
    mo.md(r"""
    ## Step 1: Fetch from the Archive API

    We call the Open-Meteo archive endpoint with:
    - **Latitude / Longitude:** 52.23, 21.01 (Warsaw city centre)
    - **Daily variables:** `temperature_2m_mean`, `temperature_2m_max`, `temperature_2m_min`
    - **Time range:** 2001-01-01 to today
    - **Timezone:** `Europe/Warsaw`

    The API returns a JSON object with a `daily` key containing parallel arrays
    (one element per day). We load these into a Polars DataFrame with a
    properly typed `Date` column.
    """)
    return


@app.cell
def fetch_data(date, json, mo, pl, timedelta, urllib):
    # ── Parameters ──────────────────────────────────────────────────────────
    LAT, LON = 52.23, 21.01
    START = date(2001, 1, 1)
    END = date.today() - timedelta(days=1)

    # ── API call ────────────────────────────────────────────────────────────
    url = (
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={LAT}&longitude={LON}"
        f"&start_date={START}&end_date={END}"
        f"&daily=temperature_2m_mean,temperature_2m_max,temperature_2m_min"
        f"&timezone=Europe/Warsaw"
    )

    mo.md(f"**Requesting:** {url}")

    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            raw = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"API returned {e.code}: {e.reason}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error: {e.reason}") from e

    # ── Extract daily data into a typed Polars DataFrame ────────────────────
    daily = raw["daily"]
    df = pl.DataFrame({
        "date":   daily["time"],
        "t_mean": daily["temperature_2m_mean"],
        "t_max":  daily["temperature_2m_max"],
        "t_min":  daily["temperature_2m_min"],
    }).with_columns(
        pl.col("date").str.strptime(pl.Date, "%Y-%m-%d")
    )

    mo.md(
        f"""
        **Rows received:** {len(df)}  
        **Date range in data:** {df['date'].min()} → {df['date'].max()}
        """
    )
    return (df,)


@app.cell
def data_preview(df):
    df
    return


@app.cell(hide_code=True)
def step2_intro(mo):
    mo.md(r"""
    ## Step 2: Save as CSV

    We encode the actual first and last dates in the filename so it's
    self-documenting:

    ```
    data/warsaw_weather_YYYY-MM-DD_YYYY-MM-DD.csv
    ```

    The `data/` directory is created automatically if it doesn't exist.
    """)
    return


@app.cell
def save_csv(DATA_DIR, df, mo):
    first = df["date"].min().strftime("%Y-%m-%d")
    last = df["date"].max().strftime("%Y-%m-%d")
    stem = f"warsaw_weather_{first}_{last}"
    csv_path = DATA_DIR / f"{stem}.csv"

    DATA_DIR.mkdir(exist_ok=True)
    df.write_csv(csv_path)

    mo.md(
        f"""
        **Written:** `{csv_path}`  
        **Rows:** {len(df)}  
        **Size:** {csv_path.stat().st_size / 1024:.1f} KB
        """
    )
    return csv_path, stem


@app.cell(hide_code=True)
def step3_intro(mo):
    mo.md(r"""
    ## Step 3: Convert CSV → Parquet with DuckDB

    DuckDB can read CSV files directly via `read_csv_auto()` and write to
    **Parquet**, a columnar binary format that is:

    - **Faster** to read back (column pruning, predicate pushdown)
    - **Smaller** on disk (dictionary encoding, compression)
    - **Better** for analytical queries in DuckDB, Polars, Spark, etc.

    We use marimo's **SQL cell** — a cell type dedicated to SQL queries. Under
    the hood it runs on DuckDB; Python variables are directly accessible by name.

    DuckDB's `read_csv_auto()` automatically detects column types including
    `DATE` from ISO-formatted date strings — no explicit CAST needed.
    """)
    return


@app.cell
def prepare_parquet_path(DATA_DIR, stem):
    parquet_path = DATA_DIR / f"{stem}.parquet"
    return (parquet_path,)


@app.cell
def csv_to_parquet(csv_path, mo, parquet_path):
    _df = mo.sql(
        f"""
        COPY (
            SELECT
                *
            FROM
                read_csv_auto('{csv_path}')
        ) TO '{parquet_path}' (FORMAT PARQUET)
        """,
        output=False
    )
    return


@app.cell
def verify_parquet(mo, parquet_path):
    stats = mo.sql(
        f"""
        SELECT
            count(*)            AS n_rows,
            min(date)           AS first_date,
            max(date)           AS last_date,
            CAST(AVG(t_mean) AS DECIMAL(4,1)) AS avg_t_mean,
            CAST(AVG(t_max)  AS DECIMAL(4,1)) AS avg_t_max,
            CAST(AVG(t_min)  AS DECIMAL(4,1)) AS avg_t_min
        FROM '{parquet_path}'
        """
    )
    return


@app.cell
def summary(csv_path, mo, parquet_path):
    csv_size = csv_path.stat().st_size / 1024
    parquet_size = parquet_path.stat().st_size / 1024

    mo.md(
        f"""
        ## Summary

        | File | Size | Format |
        |------|------|--------|
        | `{csv_path.name}` | {csv_size:.1f} KB | CSV (human-readable) |
        | `{parquet_path.name}` | {parquet_size:.1f} KB | Parquet (columnar, compressed) |

        The Parquet file is ready for analytical queries in the next notebook.
        The `date` column is typed as `DATE` for convenience.

        To read it back:

        ```python
        import duckdb
        duckdb.sql("SELECT * FROM 'data/{parquet_path.name}' LIMIT 5")
        ```
        """
    )
    return


if __name__ == "__main__":
    app.run()
