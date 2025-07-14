import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Page configuration
st.set_page_config(page_title="Restaurant Dashboard", layout="wide")

# Load and clean data
@st.cache_data

def load_data():
    df = pd.read_csv("simulated_indian_muslim_eateries_survey_data.csv")
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(r"\s+", "_", regex=True)
        .str.replace(r"[^0-9a-zA-Z_]", "", regex=True)
    )
    return df

# Load data
df = load_data()

# Sidebar layout with chart selection
with st.sidebar:

    st.title("📊 Restaurant Dashboard")
    st.header("View Options")

    view_option = st.selectbox(
        "Select a View",
        [
            "Dataset Overview",
            "Operational Scale",
            "Customer Behavior",
            "Food Preparation",
            "Food Waste Management",
            "Factors Comparison",
            "Variables Relation"
        ]
    )

# Helper: Five-number summary
def five_number_summary(series):
    summary = {
        "Min": round(series.min(), 2),
        "Q1": round(series.quantile(0.25), 2),
        "Median": round(series.median(), 2),
        "Q3": round(series.quantile(0.75), 2),
        "Max": round(series.max(), 2)
    }
    return summary

# Helper: Histogram & Boxplot

def plot_histogram_and_boxplot(series, title, color="#00CED1"):
    fig, axs = plt.subplots(2, 1, figsize=(6, 6), gridspec_kw={'height_ratios': [3, 1]})
    fig.patch.set_alpha(0)
    axs[0].set_facecolor('none')
    axs[1].set_facecolor('none')

    axs[0].hist(series.dropna(), bins=10, color=color, edgecolor='white')
    axs[0].set_title(f"{title.replace('_', ' ')} Distribution", color='white', pad=10)
    axs[0].set_ylabel("Frequency", color='white')
    axs[0].tick_params(axis='x', colors='white')
    axs[0].tick_params(axis='y', colors='white')

    axs[1].boxplot(series.dropna(), patch_artist=True,
                   boxprops=dict(facecolor=color, color='white'),
                   capprops=dict(color='white'),
                   whiskerprops=dict(color='white'),
                   flierprops=dict(markerfacecolor=color, marker='o', color='white'),
                   medianprops=dict(color='white'))
    axs[1].set_xlabel(title.replace('_', ' '), color='white')
    axs[1].tick_params(axis='x', colors='white')
    axs[1].tick_params(axis='y', colors='white')
    fig.subplots_adjust(hspace=0.4)
    return fig

# Helper: Bar chart

def plot_bar(data, x_col, y_col, title, xlabel, color="#FFA500"):
    fig, ax = plt.subplots(figsize=(6, 5))
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')
    bars = ax.bar(data[x_col], data[y_col], color=color)
    ax.set_title(title, color='white', pad=15)
    ax.set_xlabel(xlabel, color='white')
    ax.set_ylabel("Count", color='white')
    ax.tick_params(axis='x', colors='white', rotation=45)
    ax.tick_params(axis='y', colors='white')
    ax.bar_label(bars, labels=data[y_col], padding=3, color='white', fontsize=8)
    fig.tight_layout()
    return fig

if view_option == "Dataset Overview":
    st.title("📁 Full Dataset Overview")

    numeric_vars = [
        "Staff_per_Shift",
        "Servings_per_Item",
        "Daily_Customers",
        "PreConsumer_Waste_"
    ]

    # Display metrics in 4 columns
    st.subheader("📌 Key Averages")
    cols = st.columns(4)
    for i, var in enumerate(numeric_vars):
        avg = df[var].mean()
        with cols[i]:
            st.metric(label=var.replace("_", " "), value=f"{avg:.2f}")

    st.markdown("---")

    # Summary histograms
    st.subheader("📊 Distribution Overview")
    colors = ['#FFA07A', '#9370DB', '#20B2AA', '#FFD700']

    for i in range(0, len(numeric_vars), 2):
        row = st.columns(2)
        for j in range(2):
            if i + j < len(numeric_vars):
                var = numeric_vars[i + j]
                with row[j]:
                    with st.container(border=True):
                        st.subheader(var.replace("_", " "))
                        fig, ax = plt.subplots(figsize=(5, 3))
                        fig.patch.set_alpha(0)
                        ax.set_facecolor('none')
                        ax.hist(df[var].dropna(), bins=10, color=colors[(i + j) % len(colors)], edgecolor='white')
                        ax.set_title(f"{var.replace('_', ' ')} Distribution", color='white', pad=10)
                        ax.set_xlabel(var.replace("_", " "), color='white')
                        ax.set_ylabel("Frequency", color='white')
                        ax.tick_params(colors='white')
                        fig.tight_layout()
                        st.pyplot(fig)

    st.markdown("---")
    st.subheader("📄 Full Dataset")
    st.dataframe(df)
    
elif view_option == "Customer Behavior":
    st.title("🧍 Customer Behavior")

    behavior_bar_vars = ['Popular_Menu_Items', 'Prep_Quantity_Basis', 'Sales_Tracking']
    behavior_hist_vars = ['Daily_Customers']
    all_behavior_vars = behavior_bar_vars + behavior_hist_vars

    selected_behavior_vars = st.multiselect(
        "Select Customer Behavior Variables to Plot",
        options=all_behavior_vars
    )
    if not selected_behavior_vars:
        selected_behavior_vars = all_behavior_vars

    bar_colors = ['#FF7F50', '#6495ED', '#FFD700']
    hist_colors = {'Daily_Customers': '#DC143C'}

    for i in range(0, len(selected_behavior_vars), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(selected_behavior_vars):
                var = selected_behavior_vars[i + j]
                with cols[j]:
                    st.subheader(var.replace('_', ' '))
                    if var in behavior_bar_vars:
                        color = bar_colors[(i + j) % len(bar_colors)]
                        if var == 'Popular_Menu_Items':
                            exploded = df[var].astype(str).str.split(',').apply(lambda items: [i.strip() for i in items])
                            exploded_df = df.copy()
                            exploded_df[var] = exploded
                            exploded_df = exploded_df.explode(var)
                            counts = exploded_df[var].value_counts().reset_index()
                        else:
                            counts = df[var].dropna().value_counts().reset_index()
                        counts.columns = [var, 'Count']
                        fig = plot_bar(counts, var, 'Count', f"{var.replace('_', ' ')} Distribution", var.replace('_', ' '), color)
                        st.pyplot(fig)
                    elif var in behavior_hist_vars:
                        color = hist_colors.get(var, '#888888')
                        fig = plot_histogram_and_boxplot(df[var], var, color=color)
                        st.pyplot(fig)
                        summary = five_number_summary(df[var])
                        st.markdown("##### Five-Number Summary")
                        st.markdown(
                            f"**Min:** {summary['Min']} &nbsp;&nbsp;&nbsp; "
                            f"**Q1:** {summary['Q1']} &nbsp;&nbsp;&nbsp; "
                            f"**Median:** {summary['Median']} &nbsp;&nbsp;&nbsp; "
                            f"**Q3:** {summary['Q3']} &nbsp;&nbsp;&nbsp; "
                            f"**Max:** {summary['Max']}"
                        )

elif view_option == "Operational Scale":
    st.title("🏢 Operational Scale")

    op_pie_vars = ['Opening_Hours']
    op_hist_vars = ['Staff_per_Shift']
    op_bar_vars = ['Peak_Hours', 'Day_Influence', 'Occasion_Impact']
    all_op_vars = op_pie_vars + op_hist_vars + op_bar_vars

    selected_op_vars = st.multiselect(
        "Select Operational Scale Variables to Plot",
        options=all_op_vars
    )
    if not selected_op_vars:
        selected_op_vars = all_op_vars

    pie_colors = plt.cm.tab10.colors
    hist_colors = {'Staff_per_Shift': '#00CED1'}
    bar_colors = ['#FFA500', '#20B2AA', '#8A2BE2']

    for i in range(0, len(selected_op_vars), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(selected_op_vars):
                var = selected_op_vars[i + j]
                with cols[j]:
                    st.subheader(var.replace('_', ' '))
                    if var in op_pie_vars:
                        opening_counts = df[var].dropna().value_counts().reset_index()
                        opening_counts.columns = [var, 'Count']
                        fig, ax = plt.subplots(figsize=(4, 4))
                        fig.patch.set_alpha(0)
                        ax.set_facecolor('none')
                        wedges, texts, autotexts = ax.pie(
                            opening_counts['Count'], labels=opening_counts[var], autopct='%1.1f%%', startangle=140,
                            textprops={'color': 'white'}, colors=pie_colors
                        )
                        ax.axis('equal')
                        ax.set_title(var.replace('_', ' '), color='white', pad=15)
                        st.pyplot(fig)

                    elif var in op_hist_vars:
                        color = hist_colors.get(var, '#888888')
                        fig = plot_histogram_and_boxplot(df[var], var, color=color)
                        st.pyplot(fig)
                        summary = five_number_summary(df[var])
                        st.markdown("##### Five-Number Summary")
                        st.markdown(
                            f"**Min:** {summary['Min']} &nbsp;&nbsp;&nbsp; "
                            f"**Q1:** {summary['Q1']} &nbsp;&nbsp;&nbsp; "
                            f"**Median:** {summary['Median']} &nbsp;&nbsp;&nbsp; "
                            f"**Q3:** {summary['Q3']} &nbsp;&nbsp;&nbsp; "
                            f"**Max:** {summary['Max']}"
                        )

                    elif var in op_bar_vars:
                        color = bar_colors[(i + j) % len(bar_colors)]
                        if var == 'Day_Influence':
                            counts = df[var].dropna().astype(str).str.split('=').str[0].str.strip().value_counts().reset_index()
                        else:
                            exploded = df[var].astype(str).str.split(',').apply(lambda items: [i.strip() for i in items])
                            exploded_df = df.copy()
                            exploded_df[var] = exploded
                            exploded_df = exploded_df.explode(var)
                            counts = exploded_df[var].value_counts().reset_index()
                        counts.columns = [var, 'Count']
                        fig = plot_bar(counts, var, 'Count', f"{var.replace('_', ' ')} Distribution", var.replace('_', ' '), color)
                        st.pyplot(fig)

elif view_option == "Food Preparation":
    st.title("🍽️ Food Preparation")

    prep_hist_vars = ['Servings_per_Item', 'PreConsumer_Waste_']
    prep_bar_vars = ['Storage_Methods']
    all_prep_vars = prep_hist_vars + prep_bar_vars

    selected_prep_vars = st.multiselect(
        "Select Food Preparation Variables to Plot",
        options=all_prep_vars
    )
    if not selected_prep_vars:
        selected_prep_vars = all_prep_vars

    hist_colors = {
        'Servings_per_Item': '#00BFFF',
        'PreConsumer_Waste_': '#DC143C'
    }
    bar_colors = ['#9ACD32']

    for i in range(0, len(selected_prep_vars), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(selected_prep_vars):
                var = selected_prep_vars[i + j]
                with cols[j]:
                    st.subheader(var.replace('_', ' '))
                    if var in prep_hist_vars:
                        color = hist_colors.get(var, '#888888')
                        fig = plot_histogram_and_boxplot(df[var], var, color=color)
                        st.pyplot(fig)
                        summary = five_number_summary(df[var])
                        st.markdown("##### Five-Number Summary")
                        st.markdown(
                            f"**Min:** {summary['Min']} &nbsp;&nbsp;&nbsp; "
                            f"**Q1:** {summary['Q1']} &nbsp;&nbsp;&nbsp; "
                            f"**Median:** {summary['Median']} &nbsp;&nbsp;&nbsp; "
                            f"**Q3:** {summary['Q3']} &nbsp;&nbsp;&nbsp; "
                            f"**Max:** {summary['Max']}"
                        )
                    elif var in prep_bar_vars:
                        counts = df[var].dropna().value_counts().reset_index()
                        counts.columns = [var, 'Count']
                        color = bar_colors[(i + j) % len(bar_colors)]
                        fig = plot_bar(counts, var, 'Count', f"{var.replace('_', ' ')} Distribution", var.replace('_', ' '), color)
                        st.pyplot(fig)

elif view_option == "Food Waste Management":
    st.title("🥚 Food Waste Management")

    waste_bar_vars = ['Leftover_Handling', 'PostConsumer_Waste_Measure']

    selected_waste_vars = st.multiselect(
        "Select Food Waste Management Variables to Plot",
        options=waste_bar_vars
    )
    if not selected_waste_vars:
        selected_waste_vars = waste_bar_vars

    bar_colors = ['#FF69B4', '#BA55D3']

    for i in range(0, len(selected_waste_vars), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(selected_waste_vars):
                var = selected_waste_vars[i + j]
                with cols[j]:
                    st.subheader(var.replace('_', ' '))
                    counts = df[var].dropna().value_counts().reset_index()
                    counts.columns = [var, 'Count']
                    color = bar_colors[(i + j) % len(bar_colors)]
                    fig = plot_bar(counts, var, 'Count', f"{var.replace('_', ' ')} Distribution", var.replace('_', ' '), color)
                    st.pyplot(fig)



elif view_option == "Factors Comparison":
    st.title("📈 Factors Comparison")

    all_hist_vars = [
        "Staff_per_Shift",
        "Servings_per_Item",
        "Daily_Customers",
        "PreConsumer_Waste_"
    ]

    selected_hist_vars = st.multiselect(
        "Select Variables to Plot (leave blank to show all)",
        options=all_hist_vars
    )

    if not selected_hist_vars:
        selected_hist_vars = all_hist_vars

    def plot_histogram_and_boxplot(series, title, color="#00CED1"):
        fig, axs = plt.subplots(2, 1, figsize=(6, 7), gridspec_kw={'height_ratios': [3, 1]})
        fig.patch.set_alpha(0)
        axs[0].set_facecolor('none')
        axs[1].set_facecolor('none')

        # Histogram
        axs[0].hist(series.dropna(), bins=10, color=color, edgecolor='white')
        axs[0].set_title(f"{title.replace('_', ' ')} Distribution", color='white', pad=10)
        axs[0].set_ylabel("Frequency", color='white')
        axs[0].tick_params(axis='x', colors='white')
        axs[0].tick_params(axis='y', colors='white')

        # Boxplot
        axs[1].boxplot(series.dropna(), patch_artist=True,
                       boxprops=dict(facecolor=color, color='white'),
                       capprops=dict(color='white'),
                       whiskerprops=dict(color='white'),
                       flierprops=dict(markerfacecolor=color, marker='o', color='white'),
                       medianprops=dict(color='white'))
        axs[1].set_xlabel(title.replace('_', ' '), color='white', labelpad=10)
        axs[1].tick_params(axis='x', colors='white')
        axs[1].tick_params(axis='y', colors='white')
        fig.subplots_adjust(hspace=0.4)
        return fig

    def five_number_summary(series):
            summary = {
                "Min": round(series.min(), 2),
                "Q1": round(series.quantile(0.25), 2),
                "Median": round(series.median(), 2),
                "Q3": round(series.quantile(0.75), 2),
                "Max": round(series.max(), 2)
            }
            return summary

    dark_colors = ['#00CED1', '#8A2BE2', '#DC143C', '#32CD32']

    for i in range(0, len(selected_hist_vars), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(selected_hist_vars):
                var = selected_hist_vars[i + j]
                color = dark_colors[(i + j) % len(dark_colors)]
                with cols[j]:
                    with st.container(border=True):
                        st.subheader(var.replace("_", " "))
                        fig = plot_histogram_and_boxplot(df[var], var, color=color)
                        st.pyplot(fig)

                        summary = five_number_summary(df[var].dropna())
                        st.markdown("##### Five-Number Summary")
                        st.markdown(
                            f"**Min:** {summary['Min']} &nbsp;&nbsp;&nbsp; "
                            f"**Q1:** {summary['Q1']} &nbsp;&nbsp;&nbsp; "
                            f"**Median:** {summary['Median']} &nbsp;&nbsp;&nbsp; "
                            f"**Q3:** {summary['Q3']} &nbsp;&nbsp;&nbsp; "
                            f"**Max:** {summary['Max']}"
                        )

elif view_option == "Variables Relation":
    st.title("🧮 Variables Relation")

    # --- HEATMAP ---
    st.subheader("Correlation Heatmap (Numerical Variables Only)")

    numeric_df = df.select_dtypes(include=['int64', 'float64'])

    if not numeric_df.empty:
        corr = numeric_df.corr()

        fig, ax = plt.subplots(figsize=(8, 6))
        fig.patch.set_alpha(0)
        ax.set_facecolor('none')

        heatmap = ax.imshow(corr, cmap="coolwarm", interpolation="nearest")
        ax.set_xticks(range(len(corr.columns)))
        ax.set_yticks(range(len(corr.columns)))
        ax.set_xticklabels(corr.columns, rotation=45, ha="right", color="white")
        ax.set_yticklabels(corr.columns, color="white")
        ax.set_title("Correlation Matrix", color="white", pad=15)

        for i in range(len(corr.columns)):
            for j in range(len(corr.columns)):
                ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha='center', va='center', color='white', fontsize=8)

        cbar = fig.colorbar(heatmap)
        cbar.ax.yaxis.set_tick_params(color='white')
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')

        st.pyplot(fig)
    else:
        st.warning("No numerical columns available for correlation heatmap.")

    st.markdown("---")

    # --- SCATTER PLOT ---
    st.subheader("🔎 Scatter Plot Comparison")

    scatter_vars = [
        "Staff_per_Shift",
        "Servings_per_Item",
        "Daily_Customers",
        "PreConsumer_Waste_"
    ]

    col1, col2 = st.columns(2)
    with col1:
        x_var = st.selectbox("Select X-axis variable", scatter_vars)
    with col2:
        y_var = st.selectbox("Select Y-axis variable", scatter_vars, index=1)

    if x_var and y_var and x_var != y_var:
        fig, ax = plt.subplots(figsize=(7, 4))
        fig.patch.set_alpha(0)
        ax.set_facecolor('none')

        ax.scatter(df[x_var], df[y_var], color="#00FA9A", edgecolor='white')
        ax.set_xlabel(x_var.replace("_", " "), color='white')
        ax.set_ylabel(y_var.replace("_", " "), color='white')
        ax.set_title(f"{x_var.replace('_', ' ')} vs {y_var.replace('_', ' ')}", color='white', pad=10)
        ax.tick_params(colors='white')

        st.pyplot(fig)
    else:
        st.info("Select two different numerical variables to view scatter plot.")