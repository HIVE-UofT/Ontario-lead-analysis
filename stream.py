import lead as ld
import streamlit as st

school_name = st.selectbox(
    "School Name:",
    ld.dws_names,
    # default option
    index=next(
        (index for index, name in enumerate(ld.dws_names) if name.startswith('LAMBTON KENT COMP S')),
        0,
    ))

years = st.multiselect(
    "Year:",
    ld.years,
    # default option
    ld.years[0:2]
    )

categories = st.multiselect(
    "Category:",
    ld.categories,
    # default option
    ld.categories[0:2]
    )

run_diagrams = True
if len(categories) == 0:
    run_diagrams = False
    st.write("Please choose at least one category.")

if len(years) == 0:
    run_diagrams = False
    st.write("Please choose at least one year.")

if run_diagrams:
    pie = ld.get_pie(school_name, categories, years)
    histogram = ld.get_histogram(school_name, categories, years)
    line = ld.get_line(school_name, categories, years)

    st.altair_chart(pie, use_container_width= True)
    st.altair_chart(histogram, use_container_width= True)
    st.altair_chart(line, use_container_width= True)
