# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.19.10",
#     "pandas>=2.3.3",
#     "plotly>=6.5.1",
#     "pyarrow>=22.0.0",
#     "pyzmq>=27.1.0",
# ]
# ///

import marimo

__generated_with = "0.19.11"
app = marimo.App()


@app.cell
def _(mo):
    mo.md(
        r"""
        # Personal Portfolio Webpage

        This portfolio showcases my interest in financial analysis, data visualisation, and interactive storytelling using Python, pandas, Plotly, and marimo.
        """
    )
    return


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import micropip
    return micropip, mo, pd


@app.cell
def _(pd):
    # Data loading
    csv_url = "https://gist.githubusercontent.com/DrAYim/80393243abdbb4bfe3b45fef58e8d3c8/raw/ed5cfd9f210bf80cb59a5f420bf8f2b88a9c2dcd/sp500_ZScore_AvgCostofDebt.csv"

    df = pd.read_csv(csv_url)

    # Basic cleaning
    df = df.dropna(subset=["AvgCost_of_Debt", "Z_Score_lag", "Sector_Key", "Market_Cap", "Name"])
    df = df[df["AvgCost_of_Debt"] < 5].copy()

    # New columns
    df["Debt_Cost_Percent"] = df["AvgCost_of_Debt"] * 100
    df["Market_Cap_B"] = df["Market_Cap"] / 1e9

    return (df,)


@app.cell
def _(df, mo):
    # UI controls
    all_sectors = sorted(df["Sector_Key"].unique().tolist())

    sector_dropdown = mo.ui.multiselect(
        options=all_sectors,
        value=all_sectors[:4],
        label="Filter by Sector",
    )

    cap_slider = mo.ui.slider(
        start=0,
        stop=200,
        step=10,
        value=20,
        label="Minimum Market Cap ($bn)",
    )

    return all_sectors, cap_slider, sector_dropdown


@app.cell
def _(cap_slider, df, sector_dropdown):
    # Reactive filtering
    filtered_df = df[
        (df["Sector_Key"].isin(sector_dropdown.value)) &
        (df["Market_Cap_B"] >= cap_slider.value)
    ].copy()

    company_count = len(filtered_df)

    avg_debt_cost = round(filtered_df["Debt_Cost_Percent"].mean(), 2) if company_count > 0 else 0
    avg_z_score = round(filtered_df["Z_Score_lag"].mean(), 2) if company_count > 0 else 0
    largest_cap = round(filtered_df["Market_Cap_B"].max(), 1) if company_count > 0 else 0

    return avg_debt_cost, avg_z_score, company_count, filtered_df, largest_cap


@app.cell
async def _(micropip):
    await micropip.install("plotly")
    import plotly.express as px
    return (px,)


@app.cell
def _(avg_debt_cost, avg_z_score, company_count, filtered_df, largest_cap, mo):
    # Summary KPI cards
    kpi_1 = mo.stat(label="Companies", value=str(company_count))
    kpi_2 = mo.stat(label="Average Cost of Debt", value=f"{avg_debt_cost}%")
    kpi_3 = mo.stat(label="Average Z-Score", value=str(avg_z_score))
    kpi_4 = mo.stat(label="Largest Market Cap", value=f"${largest_cap}bn")

    kpis = mo.hstack([kpi_1, kpi_2, kpi_3, kpi_4], gap=2, widths="equal")
    return (kpis,)


@app.cell
def _(company_count, filtered_df, mo, px):
    # Main interactive chart
    fig = px.scatter(
        filtered_df,
        x="Z_Score_lag",
        y="Debt_Cost_Percent",
        color="Sector_Key",
        size="Market_Cap_B",
        hover_name="Name",
        title=f"Cost of Debt vs Altman Z-Score ({company_count} companies)",
        labels={
            "Z_Score_lag": "Altman Z-Score (lagged)",
            "Debt_Cost_Percent": "Average Cost of Debt (%)",
            "Sector_Key": "Sector",
            "Market_Cap_B": "Market Cap ($bn)"
        },
        template="presentation",
        width=950,
        height=600,
    )

    fig.add_vline(
        x=1.81,
        line_dash="dash",
        line_color="red",
        annotation_text="Distress threshold",
        annotation_position="top left",
    )

    fig.add_vline(
        x=2.99,
        line_dash="dash",
        line_color="green",
        annotation_text="Safe threshold",
        annotation_position="top right",
    )

    fig.update_layout(
        legend_title_text="Sector",
        margin=dict(l=40, r=40, t=70, b=40),
    )

    chart = mo.ui.plotly(fig)
    return (chart,)


@app.cell
def _(filtered_df, mo):
    # Top companies table
    table_cols = ["Name", "Sector_Key", "Debt_Cost_Percent", "Z_Score_lag", "Market_Cap_B"]

    if len(filtered_df) > 0:
        table_df = (
            filtered_df[table_cols]
            .sort_values(by="Debt_Cost_Percent", ascending=False)
            .head(10)
            .rename(columns={
                "Name": "Company",
                "Sector_Key": "Sector",
                "Debt_Cost_Percent": "Cost of Debt (%)",
                "Z_Score_lag": "Z-Score",
                "Market_Cap_B": "Market Cap ($bn)"
            })
        )
    else:
        table_df = filtered_df.head(0)

    table = mo.ui.table(table_df)
    return table, table_df


@app.cell
def _(mo, pd, px):
    # Personal interests demo chart
    interest_data = pd.DataFrame({
        "City": ["London", "Mumbai", "Marrakesh", "Dubai", "Paris"],
        "Lat": [51.5074, 19.0760, 31.6295, 25.2048, 48.8566],
        "Lon": [-0.1278, 72.8777, -7.9811, 55.2708, 2.3522],
        "Category": ["Study", "Family", "Travel", "Travel", "Culture"]
    })

    fig_map = px.scatter_geo(
        interest_data,
        lat="Lat",
        lon="Lon",
        hover_name="City",
        color="Category",
        projection="natural earth",
        title="Places Connected to My Interests",
        template="plotly"
    )

    fig_map.update_traces(marker=dict(size=12))
    interest_chart = mo.ui.plotly(fig_map)

    return fig_map, interest_chart


@app.cell
def _(chart, cap_slider, kpis, mo, sector_dropdown, table):
    # Passion project tab
    tab_project = mo.vstack([
        mo.md("## Interactive Credit Risk Dashboard"),
        mo.callout(
            mo.md(
                """
                This project explores the relationship between **credit risk** and **borrowing costs** across large US companies.

                I used Python, pandas, Plotly, and marimo to clean the data, create interactive filters, and visualise how sector and firm size may affect the cost of debt.
                """
            ),
            kind="info",
        ),
        kpis,
        mo.hstack([sector_dropdown, cap_slider], justify="center", gap=2),
        chart,
        mo.md("### Highest Cost of Debt Companies in Current View"),
        table,
    ])

    return (tab_project,)


@app.cell
def _(interest_chart, mo):
    # Personal interests tab
    tab_personal = mo.vstack([
        mo.md("## Personal Interests"),
        mo.md(
            """
            Outside academics, I am interested in travel, markets, fitness, and personal development.

            I enjoy exploring how data can turn broad interests into something measurable, visual, and easier to understand.
            """
        ),
        interest_chart,
    ])
    return (tab_personal,)


@app.cell
def _(mo):
    # About me tab
    tab_about = mo.md(
        """
        ## About Me

        **Name:** YOUR NAME HERE  
        **Course:** BSc Accounting & Finance  
        **University:** Bayes Business School  

        I am a first-year Accounting & Finance student with a growing interest in financial markets, company analysis, and data-driven decision-making.

        This webpage reflects my early development in Python-based data analysis and interactive visualisation. My goal is to build technical skills that complement financial understanding and support stronger analytical judgement.

        ### Skills
        - Python
        - pandas
        - Data cleaning and preparation
        - Interactive data visualisation
        - Plotly
        - marimo
        - GitHub
        """
    )
    return (tab_about,)


@app.cell
def _(mo, tab_about, tab_personal, tab_project):
    tabs = mo.ui.tabs({
        "About Me": tab_about,
        "Passion Project": tab_project,
        "Personal Interests": tab_personal,
    })

    mo.md(
        f"""
        # **YOUR NAME HERE**
        ### Aspiring Finance Professional | Data-Driven Thinker

        ---
        {tabs}
        """
    )
    return


if __name__ == "__main__":
    app.run()
