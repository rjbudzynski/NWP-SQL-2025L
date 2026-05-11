import marimo

__generated_with = "0.23.5"
app = marimo.App(width="medium")


@app.cell
def imports():
    import marimo as mo
    from pathlib import Path
    import polars as pl
    import matplotlib.pyplot as plt
    import numpy as np

    return Path, mo, np, pl, plt


@app.cell
def load_data(Path, mo, pl):
    # Discover the most recent parquet file in data/
    parquet_files = sorted(Path("data").glob("warsaw_weather_*.parquet"))
    if not parquet_files:
        raise FileNotFoundError(
            "No parquet file found in data/. Run acquire_data.py first."
        )
    parquet_path = parquet_files[-1]
    df = pl.read_parquet(parquet_path)

    mo.md(
        f"""
        **Data source:** `{parquet_path}`  
        **Size:** {parquet_path.stat().st_size / 1024:.1f} KB  
        **Rows:** {len(df):,}  
        **In memory:** loaded into global `df` — all SQL cells query it directly
        """
    )
    return (df,)


@app.cell(hide_code=True)
def title(mo):
    mo.md(r"""
    # Warsaw Temperature Analysis — The Past Quarter Century

    Analysis of daily temperatures in Warsaw (2001–present) using marimo SQL cells
    backed by DuckDB. Each section explains the goal before the SQL query — when
    using this as a student exercise, replace the SQL cell body with a placeholder.

    **Data:** Daily mean, maximum, and minimum temperatures from the Open-Meteo
    archive API, stored as Parquet in `data/`.
    """)
    return


@app.cell(hide_code=True)
def step1_intro(mo):
    mo.md(r"""
    ## Step 1: Select temperatures in a time subrange

    **Goal:** Use a year range slider to filter the dataset. The SQL query should
    return all daily records whose year falls within the selected interval.

    **Expected output:** A table with columns `date`, `t_mean`, `t_max`, `t_min`,
    ordered by date. Rows are reactive — moving the slider re-runs the query
    automatically.

    **SQL concepts:** `year(date)` function, `BETWEEN … AND …` range filter,
    `ORDER BY`.
    """)
    return


@app.cell
def step1_slider(df, mo):
    year_bounds = mo.sql(
        """
        SELECT
            min(year(date)) AS min_year,
            max(year(date)) AS max_year
        FROM df
        """,
        output=False,
    )

    min_year = year_bounds["min_year"].item() if year_bounds is not None else 2001
    max_year = year_bounds["max_year"].item() if year_bounds is not None else 2026

    year_range = mo.ui.range_slider(
        start=min_year,
        stop=max_year,
        step=1,
        value=(min_year, max_year),
        label="Year range",
        show_value=True,
    )
    year_range
    return (year_range,)


@app.cell
def step1_sql(df, mo, year_range):
    temps = mo.sql(
        f"""
        SELECT
            date,
            t_mean,
            t_max,
            t_min
        FROM df
        WHERE
            year(date) BETWEEN {year_range.value[0]}
            AND {year_range.value[1]}
        ORDER BY date
        """
    )
    return (temps,)


@app.cell
def step1_plot(plt, temps):
    plt.close("all")
    _fig, (ax1, ax2, ax3) = plt.subplots(
        3, 1, figsize=(12, 8), sharex=True,
    )
    ax1.plot(temps["date"], temps["t_mean"], color="#2a9d8f", linewidth=0.3)
    ax1.set_ylabel("T mean (°C)")
    ax1.set_title("Daily Temperatures — Warsaw")
    ax1.grid(alpha=0.3)

    ax2.plot(temps["date"], temps["t_max"], color="#e76f51", linewidth=0.3)
    ax2.set_ylabel("T max (°C)")
    ax2.grid(alpha=0.3)

    ax3.plot(temps["date"], temps["t_min"], color="#457b9d", linewidth=0.3)
    ax3.set_ylabel("T min (°C)")
    ax3.set_xlabel("Date")
    ax3.grid(alpha=0.3)

    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def step2_intro(mo):
    mo.md(r"""
    ## Step 2: Yearly average, maximum, and minimum temperatures

    **Goal:** For each year in the dataset, compute:
    - The **average** daily mean temperature
    - The **highest** daily maximum temperature
    - The **lowest** daily minimum temperature

    **Expected output:** A table with columns `year`, `avg_temp`, `max_temp`,
    `min_temp`, one row per year, sorted by year.

    **SQL concepts:** `year(date)` for grouping, `AVG()`, `MAX()`, `MIN()` as
    aggregate functions, `GROUP BY`, `ROUND()` for readability.
    """)
    return


@app.cell
def step2_sql(df, mo):
    yearly = mo.sql(
        f"""
        SELECT
            year(date)                    AS year,
            ROUND(AVG(t_mean), 2)         AS avg_temp,
            MAX(t_max)                    AS max_temp,
            MIN(t_min)                    AS min_temp
        FROM df
        GROUP BY year(date)
        ORDER BY year
        """
    )
    return (yearly,)


@app.cell
def step2_plot(np, plt, yearly):
    plt.close("all")
    _fig, _ax = plt.subplots(figsize=(12, 5))

    # Exclude current (incomplete) year from trend computation
    last_year = yearly["year"].max()
    complete = yearly.filter(yearly["year"] < last_year)

    years_all = yearly["year"]
    years_c = complete["year"]

    # Average temperature — circle markers + regression line
    avg_all = yearly["avg_temp"]
    avg_c = complete["avg_temp"]
    m_avg, b = np.polyfit(years_c, avg_c, 1)
    _ax.scatter(years_all, avg_all, color="#2a9d8f", s=18, zorder=3,
                label=f"Average ({m_avg * 10:+.2f} °C/decade)")
    _ax.plot(years_c, np.polyval([m_avg, b], years_c),
             color="#2a9d8f", linewidth=2, zorder=2)

    # Maximum temperature — square markers + regression line
    mx_all = yearly["max_temp"]
    mx_c = complete["max_temp"]
    m_max, b = np.polyfit(years_c, mx_c, 1)
    _ax.scatter(years_all, mx_all, color="#e76f51", s=18, marker="s",
                zorder=3, label=f"Maximum ({m_max * 10:+.2f} °C/decade)")
    _ax.plot(years_c, np.polyval([m_max, b], years_c),
             color="#e76f51", linewidth=2, zorder=2)

    # Minimum temperature — triangle markers + regression line
    mn_all = yearly["min_temp"]
    mn_c = complete["min_temp"]
    m_min, b = np.polyfit(years_c, mn_c, 1)
    _ax.scatter(years_all, mn_all, color="#457b9d", s=18, marker="v",
                zorder=3, label=f"Minimum ({m_min * 10:+.2f} °C/decade)")
    _ax.plot(years_c, np.polyval([m_min, b], years_c),
             color="#457b9d", linewidth=2, zorder=2)

    _ax.set_xlabel("Year")
    _ax.set_ylabel("Temperature (°C)")
    _ax.set_title(
        "Yearly Temperature Statistics — Warsaw "
        f"(trends from complete years only, {last_year} excluded)"
    )
    _ax.legend()
    _ax.grid(alpha=0.3)
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def step3_intro(mo):
    mo.md(r"""
    ## Step 3: Extreme temperature days per year

    **Goal:** For each year, count how many days had:
    - Maximum temperature **above 30°C** (hot days)
    - Minimum temperature **below −10°C** (cold days)

    **Expected output:** A table with columns `year`, `days_above_30`,
    `days_below_minus_10`, one row per year, sorted by year.

    **SQL concepts:** Conditional counting with `COUNT(*) FILTER (WHERE …)`,
    `year()` for grouping, `ORDER BY`.
    """)
    return


@app.cell
def step3_sql(df, mo):
    extremes = mo.sql(
        f"""
        SELECT
            year(date)                                        AS year,
            COUNT(*) FILTER (WHERE t_max > 30)                AS days_above_30,
            COUNT(*) FILTER (WHERE t_min < -10)               AS days_below_minus_10
        FROM df
        GROUP BY year(date)
        ORDER BY year
        """
    )
    return (extremes,)


@app.cell
def step3_plot(extremes, plt):
    plt.close("all")
    _fig, _ax = plt.subplots(figsize=(12, 5))

    x = extremes["year"].to_list()
    width = 0.4

    _ax.bar([xi - width / 2 for xi in x], extremes["days_above_30"],
           width, color="#e76f51", label="Days above 30°C")
    _ax.bar([xi + width / 2 for xi in x], extremes["days_below_minus_10"],
           width, color="#457b9d", label="Days below −10°C")

    _ax.set_xlabel("Year")
    _ax.set_ylabel("Number of days")
    _ax.set_title("Extreme Temperature Days per Year — Warsaw")
    _ax.legend()
    _ax.grid(alpha=0.3, axis="y")
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def step4_intro(mo):
    mo.md(r"""
    ## Step 4: Temperature extremes by day of year

    **Goal:** Each calendar date can be assigned an ordinal number from 1
    (January 1) to 365 (December 31), or 366 in leap years. For each day number,
    collect the records from **all years** and compute:

    - The **maximum** daily maximum temperature ever recorded on that day
    - The **minimum** daily minimum temperature ever recorded on that day
    - The **average** daily mean temperature across all years

    This reveals the seasonal temperature envelope — the hottest and coldest
    each calendar day has ever been, plus the typical value.

    **Expected output:** A table with columns `day_num`, `max_temp`, `min_temp`,
    `avg_temp` (366 rows), ordered by `day_num`.

    **SQL concepts:** `dayofyear(date)` for extracting the ordinal day number,
    `MAX()`, `MIN()`, `AVG()` as aggregate functions, `GROUP BY`, `ROUND()`.
    """)
    return


@app.cell
def step4_sql(mo):
    daily = mo.sql(
        f"""
        -- write SQL query here
        """
    )
    return (daily,)


@app.cell
def step4_plot(daily, mo, plt):
    _out = mo.md("*(Write the SQL query in the cell above to see the plot here.)*")
    if daily is not None:
        plt.close("all")
        _fig, _ax = plt.subplots(figsize=(12, 5))

        _ax.fill_between(
            daily["day_num"],
            daily["min_temp"],
            daily["max_temp"],
            alpha=0.15, color="#2a9d8f",
        )
        _ax.plot(daily["day_num"], daily["max_temp"],
                color="#e76f51", linewidth=0.6, label="Record high")
        _ax.plot(daily["day_num"], daily["min_temp"],
                color="#457b9d", linewidth=0.6, label="Record low")
        _ax.plot(daily["day_num"], daily["avg_temp"],
                color="#2a9d8f", linewidth=1.8, label="Average")

        _ax.set_xlabel("Day of year")
        _ax.set_ylabel("Temperature (°C)")
        _ax.set_title("Temperature Envelope by Day of Year — Warsaw (2001–present)")
        _ax.legend()
        _ax.grid(alpha=0.3)
        _fig.tight_layout()
        _out = _fig
    _out
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 5: Per‑month trends

    **Goal:**
    A dropdown widget picks a month, then a query returns one row **per year**
    for that month (columns `year`, `avg_temp`, `max_temp`, `min_temp` — note
    the `GROUP BY`). A scatter plot shows the three series vs year with
    **linear regression lines** and per‑decade warming/cooling rates in the
    legend.

    **SQL concepts:** `month(date)` or `strftime(date, '%m')` for filtering,
    `GROUP BY year(date)` inside a per‑month filter, `AVG() / MAX() / MIN()`.
    """)
    return


@app.cell
def _(month_sel):
    month_num = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
        "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
        "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
    }[month_sel.value]
    return


@app.cell
def _(mo):
    month_data = mo.sql(
        f"""
        -- write SQL query here
        """
    )
    return (month_data,)


@app.cell(hide_code=True)
def _(mo):
    months = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]
    month_sel = mo.ui.dropdown(
        options=months,
        value="Jan",
        label="Month",
    )
    month_sel
    return (month_sel,)


@app.cell(hide_code=True)
def _(mo, month_data, month_sel, np, plt):
    _out = mo.md("*(Write the SQL query in the cell above to see the plot here.)*")

    if month_data is not None:
        plt.close("all")
        _fig, _ax = plt.subplots(figsize=(12, 5))
    
        years = month_data["year"]
    
        # Average — circle markers + regression line
        _m_avg, _b = np.polyfit(years, month_data["avg_temp"], 1)
        _ax.scatter(years, month_data["avg_temp"], color="#2a9d8f", s=30, zorder=3,
                    label=f"Mean ({_m_avg * 10:+.2f} °C/decade)")
        _ax.plot(years, np.polyval([_m_avg, _b], years),
                 color="#2a9d8f", linewidth=2, zorder=2)
    
        # Maximum — square markers + regression line
        _m_max, _b = np.polyfit(years, month_data["max_temp"], 1)
        _ax.scatter(years, month_data["max_temp"], color="#e76f51", s=30, marker="s",
                    zorder=3, label=f"Maximum ({_m_max * 10:+.2f} °C/decade)")
        _ax.plot(years, np.polyval([_m_max, _b], years),
                 color="#e76f51", linewidth=2, zorder=2)
    
        # Minimum — triangle markers + regression line
        _m_min, _b = np.polyfit(years, month_data["min_temp"], 1)
        _ax.scatter(years, month_data["min_temp"], color="#457b9d", s=30, marker="v",
                    zorder=3, label=f"Minimum ({_m_min * 10:+.2f} °C/decade)")
        _ax.plot(years, np.polyval([_m_min, _b], years),
                 color="#457b9d", linewidth=2, zorder=2)
    
        _ax.set_xlabel("Year")
        _ax.set_ylabel("Temperature (°C)")
        _ax.set_title(f"Monthly Temperatures in {month_sel.value} — Warsaw (2001–present)")
        _ax.legend()
        _ax.grid(alpha=0.3)
        _fig.tight_layout()
        _out = _fig
    _out
    return


if __name__ == "__main__":
    app.run()
