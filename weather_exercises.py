import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def imports():
    import marimo as mo
    from pathlib import Path
    import polars as pl
    import matplotlib.pyplot as plt
    import numpy as np

    return Path, mo, np, pl, plt


@app.cell(hide_code=True)
def title(mo):
    mo.md(r"""
    # Weather Data Exercises

    Four exercises using daily temperature records for Warsaw (2001–present).

    | # | Exercise | Key technique |
    |---|----------|---------------|
    | 1 | Temperature Anomaly | `GROUP BY`, `JOIN` |
    | 2 | Frost-Free Growing Season | `CASE WHEN` inside `MAX` / `MIN` |
    | 3 | Temperature Variability | `STDDEV()` aggregate |
    | 4 | Monthly Warming Rates | Python loop + `polyfit` per group |

    **Data:** Stored as Parquet in `data/`. The cell below loads it into a
    table called `df`.
    """)
    return


@app.cell
def load_data(Path, mo, pl):
    parquet_files = sorted(Path("data").glob("warsaw_weather_*.parquet"))
    if not parquet_files:
        raise FileNotFoundError(
            "No parquet file found in data/. Run acquire_data.py first."
        )
    parquet_path = parquet_files[-1]
    df = pl.read_parquet(parquet_path)

    mo.md(
        f"**Loaded:** `{parquet_path.name}` — {len(df):,} rows "
        f"({df['date'].min()} to {df['date'].max()})"
    )
    return (df,)


# ── SQL JOIN: quick introduction ──────────────────────────────────────────────


@app.cell(hide_code=True)
def join_intro(mo):
    mo.md(r"""
    ## SQL JOINs — Quick Introduction

    A `JOIN` combines two tables by matching rows on a common column.
    The most common type is **INNER JOIN** — it keeps only rows where
    the key exists in both tables.

    ```sql
    SELECT *
    FROM table_a
    JOIN table_b ON table_a.key = table_b.key
    ```

    If the join key has the same name in both tables, you can use the
    shorter `USING` syntax:

    ```sql
    SELECT *
    FROM table_a
    JOIN table_b USING (key)
    ```

    **Example.** Two small tables that share a `category_id` column:
    """)
    return


@app.cell
def join_demo_data(mo, pl):
    products = pl.DataFrame({
        "product": ["Widget", "Gadget", "Doohickey"],
        "category_id": [1, 2, 1],
    })
    categories = pl.DataFrame({
        "category_id": [1, 2],
        "category_name": ["Tools", "Electronics"],
    })
    mo.hstack([products, categories])
    return categories, products


@app.cell
def join_demo_query(categories, mo, products):
    result = mo.sql(
        f"""
        SELECT
            product,
            category_name
        FROM products
        JOIN categories ON products.category_id = categories.category_id
        """
    )
    return


# ── EXERCISE 1 — Temperature Anomaly ──────────────────────────────────────────


@app.cell(hide_code=True)
def e1_title(mo):
    mo.md(r"""
    ## Exercise 1: Monthly Temperature Anomaly

    A **temperature anomaly** is the deviation of a measured temperature from
    a long-term average (the "baseline" or "climatological normal"). Climate
    scientists use anomalies because they remove the seasonal cycle, making
    long-term warming visible in a single time series.

    **Steps:**

    1. *(Pre-filled)* Compute the average `t_mean` for each month of each year.
    2. Compute the long-term (2001–2020) average per calendar month — the baseline.
    3. `JOIN` the two tables and compute `anomaly = avg_temp − baseline_temp`.
    """)
    return


@app.cell(hide_code=True)
def e1_step1_intro(mo):
    mo.md(r"""
    ### Step 1 — Monthly Averages per Year

    Pre-filled. Run it, verify the output, then move on.
    """)
    return


@app.cell
def e1_step1_sql(df, mo):
    monthly = mo.sql(
        f"""
        SELECT
            year(date)      AS year,
            month(date)     AS month_num,
            ROUND(AVG(t_mean), 2) AS avg_temp
        FROM df
        GROUP BY year, month_num
        ORDER BY year, month_num
        """
    )
    return (monthly,)


@app.cell(hide_code=True)
def e1_step2_intro(mo):
    mo.md(r"""
    ### Step 2 — Baseline (2001–2020)

    Compute the long-term average temperature for each calendar month using
    **only years 2001 through 2020** (inclusive).

    **Expected output:** columns `month_num` (1–12) and `baseline_temp`.

    **Hint:** Same structure as Step 1, but group only by `month_num` and
    add a `WHERE` clause filtering `year(date)` between 2001 and 2020.

    Write the query below.
    """)
    return


@app.cell
def e1_step2_sql(mo):
    baseline = mo.sql(
        f"""
        -- write SQL query here
        """
    )
    return (baseline,)


@app.cell(hide_code=True)
def e1_step3_intro(mo):
    mo.md(r"""
    ### Step 3 — Join and Compute Anomaly

    You now have two tables: `monthly` (one row per month per year) and
    `baseline` (one row per calendar month). They share the column
    `month_num` — the key for the JOIN.

    Write a query that:

    - **Joins** `monthly` with `baseline` on `month_num`.
    - **Selects** `year`, `month_num`, `avg_temp`, `baseline_temp`, and
      `avg_temp - baseline_temp AS anomaly`.
    - **Orders** the result by year then month.

    **Expected output:** columns `year`, `month_num`, `avg_temp`,
    `baseline_temp`, `anomaly`, sorted.

    **Hint:**
    ```sql
    FROM monthly JOIN baseline ON monthly.month_num = baseline.month_num
    ```
    """)
    return


@app.cell
def e1_step3_sql(mo):
    anomaly = mo.sql(
        f"""
        -- write SQL query here
        """
    )
    return (anomaly,)


@app.cell
def e1_plot(anomaly, mo, plt):
    _out = mo.md("*(Complete Steps 2 and 3 to see the plot.)*")

    if anomaly is not None:
        plt.close("all")
        _fig, _ax = plt.subplots(figsize=(12, 5))

        _labels = [
            f"{r['year']}-{r['month_num']:02d}"
            for r in anomaly.to_dicts()
        ]

        _ax.plot(
            range(len(_labels)),
            anomaly["anomaly"],
            color="#2a9d8f",
            linewidth=0.6,
        )
        _ax.axhline(y=0, color="gray", linewidth=0.8, linestyle="--",
                    label="Baseline (zero anomaly)")

        _step = max(1, len(_labels) // 12)
        _ax.set_xticks(
            range(0, len(_labels), _step),
            [_labels[i] for i in range(0, len(_labels), _step)],
            rotation=45, fontsize=8,
        )

        _ax.set_xlabel("Year-month")
        _ax.set_ylabel("Temperature anomaly (°C)")
        _ax.set_title(
            "Monthly Temperature Anomaly — Warsaw\n"
            "(relative to 2001–2020 baseline)"
        )
        _ax.legend()
        _ax.grid(alpha=0.3)
        _fig.tight_layout()
        _out = _fig

    _out
    return


# ── EXERCISE 2 — Frost-Free Growing Season ────────────────────────────────────


@app.cell(hide_code=True)
def e2_title(mo):
    mo.md(r"""
    ## Exercise 2: First and Last Frost — Growing Season

    Agriculture and ecology are sensitive to the timing of the first autumn
    frost and the last spring frost. The number of frost-free days between
    them defines the **growing season**.

    We define a "frost day" as any day where `t_min` drops below 0°C.

    **Steps:**

    1. In a single SQL query, find both the last spring frost and the first
       autumn frost for each year.
    2. In a second SQL query, compute the growing-season length.
    """)
    return


@app.cell(hide_code=True)
def e2_step1_intro(mo):
    mo.md(r"""
    ### Step 1 — Spring and Autumn Frost in One Query

    We need two values per year in a single row:

    - **Last spring frost** — the latest `dayofyear(date)` where the
      month is March–May AND `t_min < 0`.
    - **First autumn frost** — the earliest `dayofyear(date)` where the
      month is September–November AND `t_min < 0`.

    **Expected output:** columns `year`, `last_spring_frost`,
    `first_autumn_frost`, one row per year, sorted by year.

    **How to write this:**
    - `SELECT year(date) AS year, ... FROM df`
    - `GROUP BY year(date)`
    - Spring column: `MAX(CASE WHEN month(date) BETWEEN 3 AND 5 AND t_min < 0 THEN dayofyear(date) END)`
    - Autumn column: `MIN(CASE WHEN month(date) BETWEEN 9 AND 11 AND t_min < 0 THEN dayofyear(date) END)`
    - Exclude the current (incomplete) year: `WHERE year(date) < year(current_date)`

    `CASE WHEN` evaluates to `dayofyear` when the condition is met, or
    `NULL` otherwise. `MAX` and `MIN` ignore NULLs — so you get exactly
    the extreme frost day for each year.

    Write the query below.
    """)
    return


@app.cell
def e2_step1_sql(mo):
    frost = mo.sql(
        f"""
        -- write SQL query here
        """
    )
    return (frost,)


@app.cell(hide_code=True)
def e2_step2_intro(mo):
    mo.md(r"""
    ### Step 2 — Growing-Season Length

    The `frost` table has columns `year`, `last_spring_frost`, and
    `first_autumn_frost`. Write a query that adds the season length:

    ```
    growing_season = first_autumn_frost - last_spring_frost
    ```

    **Expected output:** columns `year`, `last_spring_frost`,
    `first_autumn_frost`, `growing_season`, sorted by year.

    **Hint:** DuckDB can query Polars DataFrames the same way it queries
    Parquet files — just write `FROM frost` and subtract the columns in
    the SELECT clause.
    """)
    return


@app.cell
def e2_step2_sql(mo):
    season = mo.sql(
        f"""
        -- write SQL query here
        """
    )
    return (season,)


@app.cell
def e2_plot(mo, np, plt, season):
    _out = mo.md("*(Complete Steps 1 and 2 to see the plot.)*")

    if season is not None:
        plt.close("all")
        _fig, _ax = plt.subplots(figsize=(12, 5))

        years = season["year"]
        gs = season["growing_season"]

        _ax.scatter(years, gs, color="#2a9d8f", s=30, zorder=3)

        _last = years.max()
        _complete_mask = years < _last
        if _complete_mask.sum() >= 2:
            _yc = years.filter(_complete_mask)
            _gc = gs.filter(_complete_mask)
            _m, _b = np.polyfit(_yc, _gc, 1)
            _ax.plot(
                _yc, np.polyval([_m, _b], _yc),
                color="#e76f51", linewidth=2, zorder=2,
                label=f"Trend ({_m * 10:+.1f} days/decade)",
            )

        _ax.set_xlabel("Year")
        _ax.set_ylabel("Growing season length (days)")
        _ax.set_title(
            "Frost-Free Growing Season Length — Warsaw\n"
            "(days between last spring frost and first autumn frost)"
        )
        _ax.legend()
        _ax.grid(alpha=0.3)
        _fig.tight_layout()
        _out = _fig

    _out
    return


# ── EXERCISE 3 — Temperature Variability ──────────────────────────────────────


@app.cell(hide_code=True)
def e3_title(mo):
    mo.md(r"""
    ## Exercise 3: Temperature Variability Over Time

    The average temperature tells us about the *central tendency* of climate.
    The **standard deviation** ($\sigma$) tells us about *variability* — how
    much temperatures swing within a given period. High variability means
    less predictable weather; low variability means conditions are more
    stable.

    **Goal:** Compute the standard deviation of daily mean temperature for
    each year, then plot it over time with a linear trend line.

    **SQL:** DuckDB supports `STDDEV(col)` as an aggregate function — same
    pattern as `AVG(col)`, `MAX(col)`, etc. The rest of the query uses
    patterns you already know (`year()`, `GROUP BY`).

    Write a query that returns columns `year` and `temp_variability`
    (standard deviation of `t_mean`, rounded to 2 decimal places),
    ordered by year. Exclude the current incomplete year.
    """)
    return


@app.cell
def e3_sql(mo):
    variability = mo.sql(
        f"""
        -- write SQL query here
        """
    )
    return (variability,)


@app.cell
def e3_plot(mo, np, plt, variability):
    _out = mo.md("*(Write the query above to see the plot.)*")

    if variability is not None:
        plt.close("all")
        _fig, _ax = plt.subplots(figsize=(12, 5))

        _years = variability["year"]
        _values = variability["temp_variability"]
        _last = _years.max()
        _complete_mask = _years < _last

        _ax.scatter(_years, _values, color="#2a9d8f", s=30, zorder=3)

        if _complete_mask.sum() >= 2:
            _yc = _years.filter(_complete_mask)
            _vc = _values.filter(_complete_mask)
            _m, _b = np.polyfit(_yc, _vc, 1)
            _ax.plot(
                _yc, np.polyval([_m, _b], _yc),
                color="#e76f51", linewidth=2, zorder=2,
                label=f"Trend ({_m * 10:+.3f} °C/decade)",
            )

        _ax.set_xlabel("Year")
        _ax.set_ylabel("Standard deviation of daily t_mean (°C)")
        _ax.set_title("Yearly Temperature Variability — Warsaw")
        _ax.legend()
        _ax.grid(alpha=0.3)
        _fig.tight_layout()
        _out = _fig

    _out
    return


# ── EXERCISE 4 — Monthly Warming Rates ────────────────────────────────────────


@app.cell(hide_code=True)
def e4_title(mo):
    mo.md(r"""
    ## Exercise 4: Which Months Are Warming Fastest?

    The analysis notebook's Step 5 lets you explore one month at a time via a
    dropdown. Here you'll compute the warming rate for **all twelve months**
    at once and display them as a bar chart.

    **Approach:**
    1. Use the `monthly` table from Exercise 1, Step 1 (monthly averages per
       year — already computed).
    2. In the Python cell below, loop over months 1–12, fit a linear
       regression for each, and collect the per-decade warming rates.
    3. The pre-filled plot shows a bar chart of warming rates per month.

    **Python concepts used:** `for` loop, `np.polyfit`, `list.append`,
    building a Polars DataFrame with `pl.DataFrame({...})`.
    """)
    return


@app.cell(hide_code=True)
def e4_step1_intro(mo):
    mo.md(r"""
    ### Step 1 — Compute Warming Rates

    The `monthly` table (from Exercise 1) has columns `year`, `month_num`,
    and `avg_temp`. For each month, fit a linear regression of `avg_temp`
    versus `year` and multiply the slope by 10 to get the warming rate in
    **°C per decade**.

    **Template:**
    ```python
    rates = []
    for m in range(1, 13):
        subset = monthly.filter(pl.col("month_num") == m)
        # exclude current year
        subset = subset.filter(subset["year"] < subset["year"].max())
        if len(subset) >= 2:
            slope, _ = np.polyfit(subset["year"], (???), 1)
            rates.append(slope * 10)
        else:
            rates.append(None)
    ```

    Replace `(???)` with the temperature column. Then build a result
    DataFrame:

    ```python
    warming = pl.DataFrame({
        "month_num": list(range(1, 13)),
        "rate": rates,
    })
    ```

    `pl` (Polars) and `np` (NumPy) are already imported — just use them.
    """)
    return


@app.cell
def e4_compute(monthly, np, pl):
    # -- loop over months and compute warming rates --
    rates = []
    for m in range(1, 13):
        subset = monthly.filter(pl.col("month_num") == m)
        # exclude current year
        subset = subset.filter(subset["year"] < subset["year"].max())
        if len(subset) >= 2:
            slope, _ = np.polyfit(subset["year"], subset["avg_temp"], 1)
            rates.append(slope * 10)  # °C per decade
        else:
            rates.append(None)

    warming = pl.DataFrame({
        "month_num": list(range(1, 13)),
        "rate": rates,
    })
    return (warming,)


@app.cell
def e4_plot(mo, plt, warming):
    _out = mo.md("*(Complete the step above to see the plot.)*")

    if warming is not None:
        plt.close("all")
        _fig, _ax = plt.subplots(figsize=(12, 5))

        _months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        _colors = ["#457b9d"] * 3 + ["#2a9d8f"] * 3 + ["#e9c46a"] * 3 + ["#e76f51"] * 3

        _ax.bar(warming["month_num"], warming["rate"],
                color=_colors, width=0.7, zorder=3)

        _ax.axhline(y=0, color="gray", linewidth=0.8, linestyle="--")
        _ax.set_xticks(range(1, 13), _months)
        _ax.set_xlabel("Month")
        _ax.set_ylabel("Warming rate (°C per decade)")
        _ax.set_title("Monthly Warming Rates — Warsaw (2001–present)")
        _ax.grid(alpha=0.3, axis="y")
        _fig.tight_layout()
        _out = _fig

    _out
    return


if __name__ == "__main__":
    app.run()
