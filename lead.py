import pandas as pd
import altair as alt

# ontario_lead = pd.ExcelFile("./OntarioLead5_7_24.xlsx")
# dfs = {
#     sheet_name: ontario_lead.parse(sheet_name) for sheet_name in ontario_lead.sheet_names
# }
# master = dfs["Master"]
# master = master[master.columns.drop(list(master.filter(regex='Unnamed*')))]
# master.to_excel("refined_master.xlsx", sheet_name = "master")

lead_excel = pd.ExcelFile("./refined_master.xlsx")
master = lead_excel.parse("master")

def clean_name(dws_name):
    proned_name = " ".join(dws_name.split(" ")[1:-1])
    return proned_name.strip()

def clean_year(year_name):
    return int(str(year_name)[0:4])

# master.insert(loc=4, column="DWS Name cleaned", value=master["DWS Name"].apply(lambda x: clean_name(x)))
master.insert(loc=4, column="Year cleared", value=master["Year"].apply(lambda x: clean_year(x)))

years = master["Year cleared"].unique().tolist()
categories = master["DWS Category"].unique().tolist()
dws_names = master["DWS Name cleared"].unique().tolist()

# multi select
# _years = years # [201920]
# _categories = categories # ['Public School']
# _school_name = 'R243 LAMBTON KENT COMP S (5473)'

def apply_filters(_school_name, _categories, _years):
    return master[master["Year cleared"].isin(_years)][master["DWS Category"].isin(_categories)][master["DWS Name cleared"] == _school_name]


def get_pie(_school_name, _categories, _years):
    result = apply_filters(_school_name, _categories, _years)
    # Pie chart
    pie_data = pd.DataFrame(result.groupby(['Exceed2'])['Exceed2'].count())
    pie_result = {}
    for i in range(len(pie_data)):
        pie_result[pie_data.iloc[i].name] = pie_data.iloc[i]["Exceed2"]
    pie_data = pd.DataFrame(pie_result.items(), columns=['Label', 'Count'])

    pie = alt.Chart(pie_data).mark_arc(innerRadius=75).encode(
        theta=alt.Theta(field="Count", type="quantitative"),
        color=alt.Color(title="Label", field="Label", type="nominal", scale=alt.Scale(scheme='purples')),
        tooltip = ['Count']
        ).properties(
        width=600,
        height=400,
        title='Label Distribution'
        ).configure_title(
            fontSize=20,
            font='Helvetica',
            fontWeight='bold',
            color='black'
        )
    # pie.save("pie.html", format="html")
    return pie


def get_histogram(_school_name, _categories, _years):
    result = apply_filters(_school_name, _categories, _years)
    colors = ['#FF5733', '#C70039', '#900C3F', '#581845', '#36404D']
    histogram = alt.Chart(result).mark_bar(
        color=colors[0],
        opacity=0.7
    ).encode(
        alt.X('Result', bin=alt.Bin(step=1), title='Lead (UG/L)'),
        alt.Y('count()', title='Count')
    ).properties(
        width=600,
        height=400,
        title='Lead Histogram'
    ).configure_title(
        fontSize=20,
        font='Helvetica',
        fontWeight='bold',
        color=colors[1]
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=16,
        labelColor=colors[2],
        titleColor=colors[3]
    )
    # histogram.save("hist.html", format="html")
    return histogram


def get_line(_school_name, _categories, _years):
    result = apply_filters(_school_name, _categories, _years)
    colors = ['#FF5733', '#C70039', '#900C3F', '#581845', '#36404D']
    year_exceed = pd.DataFrame(result.groupby(['Year cleared','Exceed2'])['Exceed2'].count())
    years_ratio = {
        year: {
            "N": 0,
            "Y": 0
        } for year in years
    }
    for i in range(len(year_exceed)):
        years_ratio[year_exceed.iloc[i].name[0]][year_exceed.iloc[i].name[1]] += year_exceed.iloc[i][0]

    criteria = "N"
    for year, distribution in years_ratio.items():
        years_ratio[year] = 0 if distribution[criteria] == 0 else distribution[criteria]/(distribution["N"]+distribution["Y"])

    line_data = pd.DataFrame({
        'Year cleared': [str(year) for year in years_ratio.keys()],
        f'{criteria} ratio': years_ratio.values()
    })

    line_chart = alt.Chart(line_data).mark_line(
        color=colors[0]
    ).encode(
        alt.X('Year cleared', title='Year'),
        y=f'{criteria} ratio'
    ).properties(
        width=600,
        height=400,
        title=f'{criteria} ratio over the years'
    ).configure_title(
        fontSize=20,
        font='Helvetica',
        fontWeight='bold',
        color=colors[1]
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=16,
        labelColor=colors[2],
        titleColor=colors[3]
    )
    # line_chart.save("line.html", format="html")
    return line_chart
