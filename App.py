import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="📊 Student Performance Analysis", layout="wide")
st.title("📚 Student Performance Analysis System")
st.markdown("Analyze marks, totals, averages, attendance, grades, and anomalies from the dataset.")

# File uploader
uploaded_file = st.file_uploader("Upload Excel file (with Marks & Attendance sheets)", type=["xlsx"])

if uploaded_file:
    try:
        # Load both sheets
        marks_df = pd.read_excel(uploaded_file, sheet_name="Marks")
        attend_df = pd.read_excel(uploaded_file, sheet_name="Attendance")
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
        st.stop()

    # Clean column names
    marks_df.columns = marks_df.columns.str.strip()
    attend_df.columns = attend_df.columns.str.strip()

    # First column is Name
    name_col = marks_df.columns[0]
    score_cols = marks_df.columns[1:]

    # Convert to numeric
    for col in score_cols:
        marks_df[col] = pd.to_numeric(marks_df[col], errors="coerce")

    # Total and average
    marks_df["Total"] = marks_df[score_cols].sum(axis=1)
    marks_df["Average"] = marks_df[score_cols].mean(axis=1)

    # Merge with Attendance on Name
    df = pd.merge(marks_df, attend_df, on=name_col, how="left")

    # Grading system
    def grade(avg):
        if avg >= 15:
            return "A"
        elif avg >= 12:
            return "B"
        elif avg >= 9:
            return "C"
        else:
            return "Fail"
    df["Grade"] = df["Average"].apply(grade)

    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    student_search = st.sidebar.text_input("Search student by name")
    min_avg, max_avg = st.sidebar.slider("Filter by Average Score", float(df["Average"].min()), float(df["Average"].max()), (float(df["Average"].min()), float(df["Average"].max())))
    grade_filter = st.sidebar.multiselect("Select Grade", df["Grade"].unique(), default=list(df["Grade"].unique()))

    filtered_df = df[
        (df["Average"].between(min_avg, max_avg)) &
        (df["Grade"].isin(grade_filter))
    ]
    if student_search:
        filtered_df = filtered_df[filtered_df[name_col].str.contains(student_search, case=False)]

    # Show filtered data
    st.subheader("📌 Filtered Dataset")
    st.dataframe(filtered_df)

    # Summary statistics
    st.subheader("📈 Summary Statistics")
    st.write(filtered_df[score_cols].describe())



    # Charts
st.subheader("📊 Visualizations")
chart_choice = st.radio(
    "Choose a visualization:",
    ["Bar Plot (Total)",  "Correlation Heatmap"]
)

if chart_choice == "Bar Plot (Total)":
    fig, ax = plt.subplots(figsize=(9, 4))
    sns.barplot(
        x=name_col, y="Total",
        data=filtered_df.sort_values("Total", ascending=False),
        palette="viridis", ax=ax
    )
    plt.xticks(rotation=90)
    st.pyplot(fig)


elif chart_choice == "Correlation Heatmap":
    # Keep only numeric columns for correlation
    numeric_df = filtered_df.select_dtypes(include=["number"])
    if numeric_df.shape[1] > 1:
        fig, ax = plt.subplots(figsize=(7, 5))
        sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)
    else:
        st.warning("⚠️ Not enough numeric data for correlation heatmap.")


    # Top performers
    st.subheader("🏆 Top 5 Students by Total")
    st.table(filtered_df.sort_values("Total", ascending=False).head(5)[[name_col, "Total", "Average", "Grade"]])

    # Download filtered data
    st.subheader("⬇️ Download Results")
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "student_performance.csv", "text/csv")

else:
    st.info("📂 Upload an Excel file with **Marks** and **Attendance** sheets to begin.")

# --- Student Profile View ---
st.subheader("👤 Student Profile View")

student_choice = st.selectbox("Select a student to view details", df[name_col].unique())

if student_choice:
    student_data = df[df[name_col] == student_choice].iloc[0]

    st.markdown(f"### 📌 Profile: **{student_data[name_col]}**")
    st.markdown(f"- 🏷️ Grade: **{student_data['Grade']}**")
    st.markdown(f"- 🏆 Total Score: **{student_data['Total']}**")
    st.markdown(f"- 📊 Average Score: **{student_data['Average']:.2f}**")
    if "Attendance" in df.columns:
        st.markdown(f"- 🎯 Attendance: **{student_data['Attendance']}%**")

    # Marks breakdown bar chart
    st.markdown("#### 📊 Marks Breakdown")
    marks_breakdown = student_data[score_cols]
    fig, ax = plt.subplots()
    marks_breakdown.plot(kind="bar", ax=ax, color="skyblue")
    plt.xticks(rotation=90)
    plt.ylabel("Score")
    st.pyplot(fig)

    # Pie chart of marks distribution
    st.markdown("#### 🥧 Marks Distribution")
    fig, ax = plt.subplots()
    marks_breakdown.plot(kind="pie", autopct="%1.1f%%", ax=ax, startangle=90, colormap="tab20")
    ax.set_ylabel("")
    st.pyplot(fig)

    # Trend line across tests
    st.markdown("#### 📈 Performance Trend")
    fig, ax = plt.subplots()
    marks_breakdown.plot(kind="line", marker="o", ax=ax, color="green")
    plt.ylabel("Score")
    plt.xticks(rotation=90)
    st.pyplot(fig)

 