import marimo

__generated_with = "0.23.5"
app = marimo.App(width="medium")


@app.cell
def imports():
    import marimo as mo
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt

    return mo, np, pd, plt


@app.cell(hide_code=True)
def title(mo):
    mo.md(r"""
    # marimo — A Reactive Python Notebook (Flash Intro)

    **Duration:** ~30 min
    **Audience:** Python-basic, some may know Jupyter
    **Goal:** Walk away able to install, launch, write, and share a marimo notebook.
    """)
    return


@app.cell(hide_code=True)
def what_is_marimo(mo):
    mo.md(r"""
    ## 1. What Is marimo? (2 min)

    marimo is an **open-source, reactive Python notebook** — like Jupyter, but with
    a fundamentally different execution model and built-in deployment.

    **Key contrast with Jupyter:**

    |  | Jupyter | marimo |
    |--|---------|--------|
    | Execution model | REPL — you must run cells manually in order | **Reactive DAG** — cells auto-run when their inputs change |
    | Hidden state | Runs in whatever order you click — stale/ghost variables are a classic bug | Guaranteed consistency: delete a cell = its variables are gone from memory |
    | File format | `.ipynb` (JSON with output blobs) — git-unfriendly | `.py` — pure Python, git-friendly, diffable, importable as a module |
    | Deployment | nbconvert / Voilà / Binder (separate toolchain) | `marimo run notebook.py` — runs as a **web app** with the same code |
    | Version control | Diff noise from JSON, output blobs, metadata | Clean Python diffs, standard git workflows |
    | Reusability | Impossible to import functions from a `.ipynb` | `from my_notebook import my_function` works because it's a `.py` file |

    **When marimo shines:**
    - Exploratory data analysis where you change a filter and charts/tables auto-update.
    - Reproducible research / ML experiments where consistency matters.
    - Building internal dashboards without rewriting in Streamlit/Dash.
    - Teaching — students can't get into hidden-state trouble.
    """)
    return


@app.cell(hide_code=True)
def installation(mo):
    mo.md(r"""
    ## 2. Installation & Launch (3 min)

    ### Install

    ```bash
    pip install marimo
    # or, with uv (recommended):
    uv tool install marimo   # then `marimo` available globally
    uvx marimo               # ephemeral run, no install needed
    ```

    ### Key CLI commands

    | Command | What it does |
    |---------|-------------|
    | `marimo edit notebook.py` | Open/edit a notebook (creates one if missing) |
    | `marimo run notebook.py` | Serve notebook as a **read-only web app** |
    | `marimo tutorial` | Launch interactive built-in tutorials |
    | `marimo convert notebook.ipynb -o notebook.py` | Convert Jupyter → marimo |
    | `marimo export ipynb notebook.py -o notebook.ipynb` | Export back to Jupyter format |
    | `marimo export html notebook.py -o notebook.html` | Self-contained WASM-backed interactive HTML |
    | `marimo edit .` | Launch marimo **workspace** — browse all `.py` files in a directory |
    """)
    return


@app.cell(hide_code=True)
def core_concepts_intro(mo):
    mo.md(r"""
    ## 3. Core Concepts — How marimo Thinks (8 min)

    ### 3.1 The Reactive DAG

    marimo **statically analyses** each cell: it reads the cell's AST to find
    which variables are **defined** (written) and which are **referenced** (read).
    This builds a Directed Acyclic Graph (DAG) of cells.

    **The fundamental rule:** When a cell is run, every cell that **references**
    any variable it **defines** is automatically re-run.

    Try it below — edit `x` in the first cell and watch the downstream cells
    update automatically.
    """)
    return


@app.cell
def dag_demo_x():
    x = 69
    return (x,)


@app.cell
def dag_demo_y(x):
    y = x + 1
    return (y,)


@app.cell(hide_code=True)
def dag_demo_output(mo, x, y):
    mo.md(f"""
    **Reactive chain result:** `x = {x}`, `x + 1 = {y}`

    Change `x` in the first cell and this message updates automatically —
    no "Run All" needed, no stale values.
    """)
    return


@app.cell(hide_code=True)
def dag_sibling_order(mo):
    mo.md(r"""
    **Execution order is determined by the DAG, not by cell position.**
    You can reorder cells freely; marimo computes the correct topological order.

    **Caveat — sibling ordering:** If B and C both depend on A (no dependency
    between B and C), their relative order is **not defined** by the DAG. The
    tie-breaker is cell creation order, not visual notebook order. For pure
    computations this is irrelevant; for **side effects** (mutation of shared
    objects, stdout, file I/O) it can bite you. If order matters, create an
    explicit dependency or refactor so siblings are pure.
    """)
    return


@app.cell(hide_code=True)
def one_definition(mo):
    mo.md(r"""
    ### 3.2 One Definition Per Variable

    A **global variable may be defined in only one cell.** This prevents the
    classic Jupyter bug where `df` is defined in cell 3, mutated in cell 8, and
    cell 5 that reads `df` sees either state depending on click order.

    **If you get an error:** "This variable has already been defined" — you've
    reused a name. Solutions:
    - Merge the two cells into one.
    - Use a different variable name (e.g. `df_clean = df.dropna()`).
    - Prefix temporary variables with `_` — these are **local to the cell** and
      don't count as global definitions.
    """)
    return


@app.cell(hide_code=True)
def one_definition_demo(mo, pd):
    _df = pd.DataFrame({"a": [1, 2, 3]})
    _df["b"] = _df["a"] * 2
    mo.md(
        f"""
        **Good pattern** — all operations in the defining cell, prefixed with `_`:

        ```
        _df = pd.DataFrame({{"a": [1, 2, 3]}})
        _df["b"] = _df["a"] * 2
        ```

        | a | b |
        |---|---|
        | 1 | 2 |
        | 2 | 4 |
        | 3 | 6 |
        """
    )
    return


@app.cell(hide_code=True)
def mutations_not_tracked(mo):
    mo.md(r"""
    ### 3.3 Mutations Are NOT Tracked

    marimo cannot track `df["col"] = ...` or `list.append(...)` **across cells**.
    Only variable *assignment* (`df = ...`, `x = ...`) triggers reactivity.

    **Rule:** If you need to mutate, do it in the same cell that defines the variable.
    """)
    return


@app.cell(hide_code=True)
def last_expression(mo):
    mo.md(r"""
    ### 3.4 The Last Expression Is the Output

    A cell's **last expression** is rendered above the cell as its visual output.
    This output also appears in the read-only app view (`marimo run`).

    Run the cell below — the DataFrame preview is the output:
    """)
    return


@app.cell
def describe_demo(pd):
    _df = pd.DataFrame({"a": [4, 5, 6], "b": [7, 8, 9]})
    _df.describe()
    return


@app.cell(hide_code=True)
def marimo_markdown(mo):
    mo.md(r"""
    ### 3.5 Marimo Markdown (`mo.md`)

    Rich text output via `mo.md()` — supports f-string interpolation for live values.

    A cell that *only* contains `mo.md(...)` gets a special **Markdown editor**
    in the UI (toggle between Python and Markdown modes).

    ```python
    name = mo.ui.text(placeholder="Your name")
    mo.md(f"Hello, {name.value or 'world'}!")
    ```
    """)
    return


@app.cell(hide_code=True)
def interactive_intro(mo):
    mo.md(r"""
    ## 4. Interactivity — UI Elements (5 min)

    marimo's UI elements (`mo.ui.*`) are **reactive by nature** — interact with a
    slider, and every cell that reads its value auto-updates.
    """)
    return


@app.cell
def slider_demo(mo):
    slider_val = mo.ui.slider(1, 100, step=1, value=30, label="Pick a number")
    slider_val
    return (slider_val,)


@app.cell(hide_code=True)
def slider_output(mo, slider_val):
    mo.md(f"""
    **Current slider value:** {slider_val.value}
    """)
    return


@app.cell(hide_code=True)
def key_widgets(mo):
    mo.md(r"""
    ### Key widgets

    | Widget | Purpose |
    |--------|---------|
    | `mo.ui.slider(min, max)` | Numeric slider → `.value` |
    | `mo.ui.text(placeholder)` | Text input → `.value` |
    | `mo.ui.number(start, stop)` | Numeric input → `.value` |
    | `mo.ui.dropdown(options)` | Dropdown selector → `.value` |
    | `mo.ui.checkbox()` | Boolean toggle → `.value` |
    | `mo.ui.button(label)` | Clickable button → `.value` (click count) |
    | `mo.ui.run_button()` | Gates execution — returns value only after click |
    | `mo.ui.dataframe(df)` | Interactive DataFrame viewer with filtering/sorting |
    | `mo.ui.table(df)` | Paginated table |
    | `mo.ui.plotly(fig)` | Plotly figure with selection → `.value` |
    | `mo.ui.form([...])` | Gated group: values only sent on submit |

    ### Layout helpers

    ```python
    mo.output.append(object) # workaround for only last value in cell displayed
    mo.hstack([slider, checkbox, button], justify="center")
    mo.vstack([output1, output2])
    mo.accordion({"Details": "More info..."})
    mo.ui.tabs({"Plot": plot_out, "Table": table_out})
    ```
    """)
    return


@app.cell(hide_code=True)
def sine_wave_title(mo):
    mo.md(r"""
    ### Interactive sine wave demo

    Drag the sliders — the plot redraws automatically, no "Run All" required.
    """)
    return


@app.cell
def sine_widgets(mo):
    freq = mo.ui.slider(0.5, 10.0, step=0.5, value=2.0, label="Frequency (Hz)")
    amp = mo.ui.slider(0.1, 3.0, step=0.1, value=1.0, label="Amplitude")
    n_points = mo.ui.slider(10, 300, step=10, value=80, label="Points")
    mo.hstack([freq, amp, n_points], justify="center")
    return amp, freq, n_points


@app.cell
def sine_plot(amp, freq, n_points, np, plt):
    plt.close("all")
    _x = np.linspace(0, 4 * np.pi, n_points.value)
    fig, ax = plt.subplots()
    ax.plot(_x, amp.value * np.sin(freq.value * _x))
    ax.set_title(f"{amp.value} · sin({freq.value} · x)  —  {n_points.value} points")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_ylim(-3.5, 3.5)
    ax.grid(alpha=0.3)
    fig
    return


@app.cell(hide_code=True)
def sql_intro(mo):
    mo.md(r"""
    ## 5. SQL Cells (3 min)

    marimo has **built-in SQL** — query DataFrames, SQLite, DuckDB, PostgreSQL,
    and more via a dedicated SQL cell type (click the SQL button at the bottom
    of the notebook or right-click `+`).

    No `%%sql` magic — SQL cells are a cell-type switch in the UI, represented
    in code as `mo.sql(...)`.

    **Python variables are directly accessible in SQL** by name:
    """)
    return


@app.cell
def sql_data(pd):
    cities = pd.DataFrame({
        "city": ["Warsaw", "Kraków", "Gdańsk", "Wrocław", "Poznań"],
        "population_m": [1.8, 0.8, 0.5, 0.6, 0.5],
        "voivodeship": ["mazowieckie", "małopolskie", "pomorskie", "dolnośląskie", "wielkopolskie"],
    })
    return


@app.cell
def sql_query(mo):
    result = mo.sql(
        f"""
        SELECT city, population_m
        FROM cities
        WHERE population_m > 0.55
        ORDER BY population_m DESC
        """
    )
    return


@app.cell(hide_code=True)
def sql_db_connect(mo):
    mo.md(r"""
    Connect to real databases via the UI ("Add Database Connection") or by
    defining a connection engine in a Python cell:

    ```python
    import sqlalchemy
    engine = sqlalchemy.create_engine("postgresql://user:***@host/db")
    ```

    Supported: DuckDB (default in-memory), PostgreSQL, MySQL, SQLite,
    Snowflake, BigQuery, and more.
    """)
    return


@app.cell(hide_code=True)
def mo_reference(mo):
    mo.md(r"""
    ## 6. The mo Library — Quick Reference (3 min)

    ```python
    import marimo as mo
    ```

    | Call | Purpose |
    |------|---------|
    | `mo.md("...")` | Markdown output with f-string interpolation |
    | `mo.ui.slider(min, max)` | Slider widget → `.value` |
    | `mo.ui.text(placeholder)` | Text input → `.value` |
    | `mo.ui.button(label)` | Clickable button → `.value` (click count) |
    | `mo.ui.run_button()` | Gates execution: returns value only after click |
    | `mo.ui.dataframe(df)` | Interactive DataFrame viewer |
    | `mo.ui.table(df)` | Paginated table |
    | `mo.ui.plotly(fig)` | Plotly chart with selection → `.value` |
    | `mo.ui.form([...])` | Gated group: values only sent on submit |
    | `mo.hstack` / `mo.vstack` | Horizontal / vertical layout |
    | `mo.accordion({...})` | Collapsible sections |
    | `mo.ui.tabs({"A": a, "B": b})` | Tabbed layout |
    | `mo.status.progress_bar(range(...))` | Iterable progress bar |
    | `mo.stop(condition)` | Halt cell if condition is True |
    | `mo.refs()` / `mo.defs()` | Inspect variable references/definitions |
    | `mo.notebook_dir()` | Path to notebook's directory |
    | `marimo.__version__` | Version check |
    """)
    return


@app.cell(hide_code=True)
def deployment(mo):
    mo.md(r"""
    ## 7. Deployment & Sharing (3 min)

    ### Edit your notebook

    ```bash
    marimo edit notebook.py
    # Opens the editor in your browser — changes save automatically
    ```

    ### As a web app (no code changes)

    ```bash
    marimo run notebook.py
    # Serves at http://localhost:2718 — read-only, interactive widgets work
    ```

    This is the **killer feature** compared to Jupyter: the same `.py` file is
    both your editor and your deployed app. No rewriting for Streamlit/Dash.

    ### Gallery mode

    ```bash
    marimo run folder/           # Card gallery of all notebooks in folder
    marimo run a.py b.py dir/    # Mixed list
    ```

    ### Export options

    ```bash
    marimo export html notebook.py > notebook.html    # WASM-backed, interactive
    marimo export pdf notebook.py                      # PDF
    marimo export ipynb notebook.py -o notebook.ipynb   # Jupyter format
    marimo export script notebook.py > script.py        # Linear script
    ```

    ### Run as a script

    ```bash
    python notebook.py        # Executes all cells headlessly
    ```

    ### molab (free hosting)

    [molab.marimo.io](https://molab.marimo.io/) — free cloud hosting with GitHub
    integration and "Open in molab" badges. Great for sharing with students or
    colleagues without setting up servers.
    """)
    return


@app.cell(hide_code=True)
def migration(mo):
    mo.md(r"""
    ## 8. marimo vs Jupyter — Migration Tips (2 min)

    | Jupyter habit | marimo equivalent |
    |---------------|-------------------|
    | `!ls -l` | `import subprocess; subprocess.run(["ls", "-l"])` |
    | `%timeit` | `import timeit; timeit.timeit(...)` |
    | `%matplotlib inline` | Auto-displayed (no magic needed) |
    | `%%html` | `mo.Html(...)` or `mo.md(...)` |
    | `%%latex` | `mo.md(r"$$ ... $$")` |
    | `%who_ls` | `mo.refs()`, `mo.defs()` |
    | `%cd` | `os.chdir()` or `mo.notebook_dir()` |
    | `%pip install` | Sidebar → Package Manager panel |

    **Conversion workflow:**

    ```bash
    marimo convert old_notebook.ipynb -o new_notebook.py
    marimo edit new_notebook.py
    ```

    After conversion, you may need to split monolithic cells and fix variable
    redefinitions. The built-in marimo linter flags issues.
    """)
    return


@app.cell(hide_code=True)
def exercises(mo):
    mo.md(r"""
    ## 9. Hands-On Exercises (4 min)

    ### Exercise 1: Interactive data filter

    Build a mini dashboard on an inline dataset. Create three cells in a new notebook:

    **Cell 1** — define some sample data:
    ```python
    import pandas as pd
    inventory = pd.DataFrame({
        "product": ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"],
        "category": ["A", "B", "A", "B", "A"],
        "price": [10, 25, 15, 30, 20],
        "stock": [100, 50, 75, 30, 90],
    })
    ```

    **Cell 2** — two widgets to filter by:
    ```python
    import marimo as mo
    cat = mo.ui.dropdown(options=["A", "B"], value="A", label="Category")
    min_p = mo.ui.slider(start=0, stop=30, step=1, value=10, label="Min price")
    mo.hstack([cat, min_p])
    ```

    **Cell 3** — reactive filter + table + bar chart:
    ```python
    import matplotlib.pyplot as plt
    mask = (inventory.category == cat.value) & (inventory.price >= min_p.value)
    filtered = inventory[mask]
    fig, ax = plt.subplots()
    ax.bar(filtered["product"], filtered["stock"])
    ax.set_title(f"Stock in category {cat.value} (price >= {min_p.value})")
    mo.hstack([mo.ui.table(filtered), fig])
    ```

    Change the dropdown or slider — the table and chart update automatically.
    """)
    return


@app.cell(hide_code=True)
def when_not(mo):
    mo.md(r"""
    ## 10. When NOT to Use marimo (1 min)

    - You need to run cells interactively in a **non-linear / arbitrary order**
      repeatedly (marimo's DAG constraints don't allow it).
    - You heavily depend on **IPython magics** or shell `!` commands
      (marimo doesn't support these — use standard Python instead).
    - You have many **redefinitions of the same variable** across cells
      (requires refactoring).
    - Your notebook is **>10,000 cells** with very expensive computation
      (the reactive DAG overhead becomes noticeable).
    """)
    return


@app.cell(hide_code=True)
def resources(mo):
    mo.md(r"""
    ## Further Resources

    | Link | What |
    |------|------|
    | [marimo.io](https://marimo.io/) | Homepage |
    | [docs.marimo.io](https://docs.marimo.io/) | Full documentation |
    | [GitHub](https://github.com/marimo-team/marimo) | Source, issues, examples |
    | [molab.marimo.io](https://molab.marimo.io/) | Free cloud hosting |
    | [Roadmap](https://marimo.io/roadmap) | Upcoming features |
    | `marimo tutorial` | Interactive tutorials in your terminal |
    """)
    return


if __name__ == "__main__":
    app.run()
