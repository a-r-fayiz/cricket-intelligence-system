import streamlit as st
import pandas as pd
import numpy as np
import json
import plotly.express as px


# Load the cricket data JSON file with caching
@st.cache_data
def load_data(json_file):
    with open(json_file, 'r') as f:
        return json.load(f)

# Convert JSON data to a DataFrame with caching
@st.cache_data
def json_to_dataframe(data):
    records = []
    for format_type, styles in data.items():
        for style, years in styles.items():
            for year, stats in years.items():
                for record in stats:
                    record['Format'] = format_type
                    record['Style'] = style
                    records.append(record)
    return pd.DataFrame(records)

# Filter player data with caching
@st.cache_data
def filter_player_data(df, selected_player, start_year, end_year):
    return df[(df["Player Name"] == selected_player) & (df["Year"].between(int(start_year), int(end_year)))]

# Main Streamlit app
def main():
    # Apply custom CSS
    st.markdown(
        """
        <style>
            .main { background-color: #f4f4f9; }
            .sidebar .sidebar-content { background-color: #00264d; color: white; }
            .stSelectbox, .stTable { background-color: white; color: black; }
            h1, h2, h3 { color: #00264d; }
            .block-container { padding: 2rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Title and sidebar header
    st.title("🏏 Cricket Data Analysis")
    st.sidebar.header("Filters")

    # Load data
    data_file = "cricket_data.json"
    cricket_data = load_data(data_file)
    df = json_to_dataframe(cricket_data)

    # Preprocessing
    numeric_columns = ["Matches", "Innings", "Runs", "Wickets", "Average", "Strike Rate", "Overs", "4s", "6s", "Economy Rate"]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Filtering options
    filter_type = st.sidebar.selectbox(
    "🔍 Select Filter Type", 
    ["Player Wise", "Format Wise", "Year Wise", "Player Comparison", "Optimal Team Selector"]
)

   
    
    if filter_type == "Player Wise":
            player_names = sorted(df["Player Name"].unique())
            selected_player = st.sidebar.selectbox("Select Player", player_names)
            st.header(f"📊 Player Wise Analysis of {selected_player}")

            # Year range selection with dynamic constraints
            st.subheader("Filter by Year Range")
            col1, col2 = st.columns(2)

            years = [str(y) for y in range(2011, 2026)]
            if "start_year" not in st.session_state:
                st.session_state["start_year"] = "2011"
            if "end_year" not in st.session_state:
                st.session_state["end_year"] = "2025"

            with col1:
                valid_start_years = [y for y in years if int(y) <= int(st.session_state.get("end_year", "2025"))]
                start_year_index = valid_start_years.index(st.session_state["start_year"]) if st.session_state["start_year"] in valid_start_years else 0
                start_year = st.selectbox("Start Year", valid_start_years, index=start_year_index, key="start_year")

            with col2:
                valid_end_years = [y for y in years if int(y) >= int(st.session_state.get("start_year", "2011"))]
                end_year_index = valid_end_years.index(st.session_state["end_year"]) if st.session_state["end_year"] in valid_end_years else len(valid_end_years) - 1
                end_year = st.selectbox("End Year", valid_end_years, index=end_year_index, key="end_year")

            # Convert 'Year' column to numeric and handle errors gracefully
            df["Year"] = pd.to_numeric(df["Year"], errors="coerce")

            # Filter data for the selected player and year range
            player_data = filter_player_data(df, selected_player, st.session_state["start_year"], st.session_state["end_year"])
            # Combined Table (Summary)
            st.markdown("### Player Summary (Combined)")
            summary_table = pd.DataFrame({
                "Format": ["Test", "ODI", "T20"],
                "Batting Innings": [
                    player_data[(player_data["Format"] == "test") & (player_data["Style"] == "batting")]["Innings"].sum(),
                    player_data[(player_data["Format"] == "odi") & (player_data["Style"] == "batting")]["Innings"].sum(),
                    player_data[(player_data["Format"] == "t20") & (player_data["Style"] == "batting")]["Innings"].sum(),
                ],
                "Total Runs": [
                    player_data[(player_data["Format"] == "test") & (player_data["Style"] == "batting")]["Runs"].sum(),
                    player_data[(player_data["Format"] == "odi") & (player_data["Style"] == "batting")]["Runs"].sum(),
                    player_data[(player_data["Format"] == "t20") & (player_data["Style"] == "batting")]["Runs"].sum(),
                ],
                "Bowling Innings": [
                    player_data[(player_data["Format"] == "test") & (player_data["Style"] == "bowling")]["Innings"].sum(),
                    player_data[(player_data["Format"] == "odi") & (player_data["Style"] == "bowling")]["Innings"].sum(),
                    player_data[(player_data["Format"] == "t20") & (player_data["Style"] == "bowling")]["Innings"].sum(),
                ],
                "Total Wickets": [
                    player_data[(player_data["Format"] == "test") & (player_data["Style"] == "bowling")]["Wickets"].sum(),
                    player_data[(player_data["Format"] == "odi") & (player_data["Style"] == "bowling")]["Wickets"].sum(),
                    player_data[(player_data["Format"] == "t20") & (player_data["Style"] == "bowling")]["Wickets"].sum(),
                ],
            })

            # Add a row for totals
            total_row = pd.DataFrame({
                "Format": ["Total"],
                "Batting Innings": [summary_table["Batting Innings"].sum()],
                "Total Runs": [summary_table["Total Runs"].sum()],
                "Bowling Innings": [summary_table["Bowling Innings"].sum()],
                "Total Wickets": [summary_table["Total Wickets"].sum()],
            })

            # Concatenate the total row to the summary table
            summary_table = pd.concat([summary_table, total_row], ignore_index=True)

            # Convert columns to integer type
            summary_table["Batting Innings"] = summary_table["Batting Innings"].astype(int)
            summary_table["Total Runs"] = summary_table["Total Runs"].astype(int)
            summary_table["Bowling Innings"] = summary_table["Bowling Innings"].astype(int)
            summary_table["Total Wickets"] = summary_table["Total Wickets"].astype(int)

            # Display the table
            st.table(summary_table.set_index("Format").style.set_properties(**{
                "text-align": "center",
                "background-color": "#f4f4f9",
                "border": "1px solid black",
                "font-weight": "bold",
            }))

            # Batting Section
            st.markdown("## 🏏 Batting Performance")
            st.markdown("### Batting Summary (Detailed)")

            # Convert numeric columns safely
            player_data["Runs"] = pd.to_numeric(player_data["Runs"], errors="coerce")
            player_data["Balls Faced"] = pd.to_numeric(player_data["Balls Faced"], errors="coerce")
            player_data["Innings"] = pd.to_numeric(player_data["Innings"], errors="coerce")
            player_data["4s"] = pd.to_numeric(player_data["4s"], errors="coerce")
            player_data["6s"] = pd.to_numeric(player_data["6s"], errors="coerce")
            player_data["Not Outs"] = pd.to_numeric(player_data["Not Outs"], errors="coerce")

            # Fill NaN values with 0
            player_data.fillna(0, inplace=True)

            # Convert to int
            player_data["Innings"] = player_data["Innings"].astype(int)
            player_data["Runs"] = player_data["Runs"].astype(int)
            player_data["Balls Faced"] = player_data["Balls Faced"].astype(int)
            player_data["4s"] = player_data["4s"].astype(int)
            player_data["6s"] = player_data["6s"].astype(int)
            player_data["Not Outs"] = player_data["Not Outs"].astype(int)

            # Aggregate batting data
            batting_table = player_data[player_data["Style"] == "batting"].groupby("Format").agg({
                "Innings": "sum",
                "Runs": "sum",
                "4s": "sum",
                "6s": "sum",
                "Balls Faced": "sum",
                "Average": "mean",
                "Not Outs": "sum"
            }).reset_index()

            # Check if table has data
            if batting_table.empty:
                st.markdown("### NO DATA")
            else:
                # Calculate Strike Rate
                batting_table["Strike Rate"] = (batting_table["Runs"] / batting_table["Balls Faced"].replace(0, np.nan)) * 100
                batting_table["Strike Rate"].fillna(0, inplace=True)

                # Calculate total statistics
                total_row = {
                    "Format": "Total",
                    "Innings": batting_table["Innings"].sum(),
                    "Runs": batting_table["Runs"].sum(),
                    "4s": batting_table["4s"].sum(),
                    "6s": batting_table["6s"].sum(),
                    "Balls Faced": batting_table["Balls Faced"].sum(),
                    "Average": batting_table["Runs"].sum() / max(batting_table["Innings"].sum() - batting_table["Not Outs"].sum(), 1),
                    "Strike Rate": 0,
                    "Not Outs": batting_table["Not Outs"].sum()
                }

                # Append total row
                batting_table = pd.concat([batting_table, pd.DataFrame([total_row])], ignore_index=True)

                # Drop "Balls Faced" and "Not Outs" from display
                batting_table.drop(columns=["Balls Faced", "Not Outs"], inplace=True)

                # Display the table
                st.table(batting_table.style.format({
                    "Strike Rate": "{:.2f}",
                    "Average": "{:.2f}",
                    "4s": "{:.0f}",
                    "6s": "{:.0f}"
                }))

            # Calculate Batting Average Over the Years
            batting_yearly = player_data[player_data["Style"] == "batting"].groupby("Year").agg({
                "Runs": "sum",
                "Innings": "sum",
                "Not Outs": "sum"
            }).reset_index()

            # Use the formula to calculate batting average
            batting_yearly["Average"] = batting_yearly["Runs"] / batting_yearly["Innings"].sub(batting_yearly["Not Outs"]).replace(0, 1)

            # Batting Average Bar Graph
            if not batting_yearly.empty:
                st.markdown("### Batting Average Over the Years")
                fig_batting_avg = px.bar(
                    batting_yearly,
                    x="Year",
                    y="Average",
                    title=f"Mean Batting Average Over Years for {selected_player}",
                    labels={"Average": "Batting Average", "Year": "Year"},
                    text_auto=".2f"
                )
                fig_batting_avg.update_layout(
                    yaxis=dict(title="Batting Average"),
                    xaxis=dict(title="Year"),
                    title=dict(x=0.5),
                )
                st.plotly_chart(fig_batting_avg, use_container_width=True)
            else:
                st.markdown("### No Batting Data Available for Mean Batting Average")

            # Batting Performance Chart
            st.subheader(f"Batting Performance of {selected_player}")
            batting_data = player_data[player_data["Style"] == "batting"].copy()

            # Check if batting data exists for plotting
            if batting_data.empty:
                st.markdown("### NO DATA")
            else:
                # Plot the batting averages over years
                fig_batting = px.line(
                    batting_data,
                    x="Year",
                    y="Average",
                    color="Format",
                    markers=True,
                    title="Batting Averages Over Years"
                )

                # Add predictions to the Batting Average chart
                # Add predictions to the Batting Average chart
                fig_batting.update_traces(connectgaps=True)
                fig_batting.update_yaxes(rangemode="tozero")  # Set y-axis range to zero

                # Display the chart
                st.plotly_chart(fig_batting)

                # Line plot for 4s and 6s
                st.markdown("### 4s and 6s Over Years")
                plot_option = st.radio("Select Metric", ["4s", "6s"], horizontal=True)
                chart_data = player_data.groupby(["Year", "Format"])[plot_option].sum().reset_index()

                if chart_data.empty:
                    st.markdown("### NO DATA")
                else:
                    fig_4s_6s = px.line(
                        chart_data,
                        x="Year",
                        y=plot_option,
                        color="Format",
                        markers=True,
                        title=f"{plot_option} Over Years",
                    )

                    # Add predictions to the 4s and 6s chart
                    fig_4s_6s.update_traces(connectgaps=True)
                    fig_4s_6s.update_yaxes(rangemode="tozero")  # Set y-axis range to zero       

                    # Display the chart
                    st.plotly_chart(fig_4s_6s)

            # Bowling Section
            st.markdown("## 🎯 Bowling Performance")
            st.markdown("### Bowling Summary (Detailed)")

            # Convert numeric columns safely for bowling
            player_data["Wickets"] = pd.to_numeric(player_data["Wickets"], errors="coerce")
            player_data["Innings"] = pd.to_numeric(player_data["Innings"], errors="coerce")
            player_data["Average"] = pd.to_numeric(player_data["Average"].replace("-", 0), errors="coerce")
            player_data["Economy Rate"] = pd.to_numeric(player_data["Economy Rate"].replace("-", 0), errors="coerce")
            player_data.fillna(0, inplace=True)

            # Aggregate bowling data
            bowling_table = player_data[player_data["Style"] == "bowling"].groupby("Format").agg({
                "Innings": "sum",
                "Wickets": "sum",
                "Average": "mean",
                "Economy Rate": "mean"
            }).reset_index()

            # Handle "NO DATA" for bowling summary table
            if bowling_table.empty:
                st.markdown("### NO DATA")
            else:
                # Calculate total statistics
                total_row = {
                    "Format": "Total",
                    "Innings": bowling_table["Innings"].sum(),
                    "Wickets": bowling_table["Wickets"].sum(),
                    "Average": None,  # Leave empty for total row
                    "Economy Rate": None  # Leave empty for total row
                }

                # Append total row
                bowling_table = pd.concat([bowling_table, pd.DataFrame([total_row])], ignore_index=True)

                # Display the table
                st.table(bowling_table.style.format({
                    "Average": "{:.2f}",
                    "Economy Rate": "{:.2f}",
                    "Wickets": "{:.0f}",
                    "Innings": "{:.0f}"
                }))

            # Bowling Economy Rate Over Years
            st.markdown("### Bowling Economy Rate Over Years")

            # Filter for relevant bowling data
            bowling_economy_data = player_data[(player_data["Style"] == "bowling") & (player_data["Economy Rate"] > 0)]

            if bowling_economy_data.empty:
                st.markdown("### NO DATA")
            else:
                # Group by Year and Format for average Economy Rate
                economy_rate_chart_data = bowling_economy_data.groupby(["Year", "Format"])["Economy Rate"].mean().reset_index()

                # Create the line plot
                fig_bowling = px.line(
                    economy_rate_chart_data,
                    x="Year",
                    y="Economy Rate",
                    color="Format",
                    markers=True,
                    title="Bowling Economy Rate Over Years"
                )

                # Add predictions to the Economy Rate chart
                fig_bowling.update_traces(connectgaps=True)
                fig_bowling.update_yaxes(rangemode="tozero")  # Set y-axis range to zero       

                # Display the chart
                st.plotly_chart(fig_bowling)

            # Calculate Bowling Average Over the Years
            bowling_yearly = player_data[player_data["Style"] == "bowling"].groupby("Year").agg({
                "Wickets": "sum",
                "Runs": "sum"  # Assuming this column represents "Runs Conceded"
            }).reset_index()

            # Use the formula to calculate bowling average
            bowling_yearly["Average"] = bowling_yearly["Runs"] / bowling_yearly["Wickets"].replace(0, 1)

            # Bowling Average Bar Graph
            if not bowling_yearly.empty:
                st.markdown("### Bowling Average Over the Years")
                fig_bowling_avg = px.bar(
                    bowling_yearly,
                    x="Year",
                    y="Average",
                    title=f"Mean Bowling Average Over Years for {selected_player}",
                    labels={"Average": "Bowling Average", "Year": "Year"},
                    text_auto=".2f"
                )
                fig_bowling_avg.update_layout(
                    yaxis=dict(title="Bowling Average"),
                    xaxis=dict(title="Year"),
                    title=dict(x=0.5),
                )
                st.plotly_chart(fig_bowling_avg, use_container_width=True)
            else:
                st.markdown("### No Bowling Data Available for Mean Bowling Average")

            # Wickets Over Years
            st.markdown("### Wickets Over Years")
            wickets_chart_data = player_data.groupby(["Year", "Format"])["Wickets"].sum().reset_index()

            if wickets_chart_data.empty:
                st.markdown("### NO DATA")
            else:
                fig_wickets = px.line(
                    wickets_chart_data,
                    x="Year",
                    y="Wickets",
                    color="Format",
                    markers=True,
                    title="Wickets Over Years"
                )

                # Add predictions to the Wickets chart
                fig_wickets.update_traces(connectgaps=True)
                fig_wickets.update_yaxes(rangemode="tozero")  # Set y-axis range to zero       

                # Display the chart
                st.plotly_chart(fig_wickets)

    elif filter_type == "Format Wise":
            st.header("📊 Format Wise Analysis")
            formats = ["test", "odi", "t20"]

            # Years Selection Logic
            years = [str(y) for y in range(2011, 2026)]
            if "start_year" not in st.session_state:
                st.session_state["start_year"] = "2011"
            if "end_year" not in st.session_state:
                st.session_state["end_year"] = "2025"

            col1, col2 = st.columns(2)
            with col1:
                valid_start_years = [y for y in years if int(y) <= int(st.session_state.get("end_year", "2025"))]
                start_year_index = valid_start_years.index(st.session_state["start_year"]) if st.session_state["start_year"] in valid_start_years else 0
                start_year = st.selectbox("Start Year", valid_start_years, index=start_year_index, key="start_year")

            with col2:
                valid_end_years = [y for y in years if int(y) >= int(st.session_state.get("start_year", "2011"))]
                end_year_index = valid_end_years.index(st.session_state["end_year"]) if st.session_state["end_year"] in valid_end_years else len(valid_end_years) - 1
                end_year = st.selectbox("End Year", valid_end_years, index=end_year_index, key="end_year")

            # Filter data based on the selected year range
            df["Year"] = pd.to_numeric(df["Year"], errors="coerce")  # Ensure 'Year' column is numeric
            filtered_df = df[(df["Year"] >= int(start_year)) & (df["Year"] <= int(end_year))]

            for format_type in formats:
                st.subheader(f"{format_type.upper()} Format Analysis")

                # Batting and Bowling Side-by-Side
                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Top Batting Performers**")
                    format_data = filtered_df[(filtered_df["Format"] == format_type) & (filtered_df["Style"] == "batting")]
                    aggregated_data = format_data.groupby("Player Name", as_index=False).agg({"Runs": "sum", "Average": "mean"})
                    top_performers = aggregated_data.nlargest(5, "Runs")[["Player Name", "Runs", "Average"]]
                    top_performers["Runs"] = top_performers["Runs"].astype(int)
                    top_performers["Average"] = top_performers["Average"].round(2)
                    st.table(top_performers)

                with col2:
                    st.write("**Top Bowling Performers**")
                    bowling_data = filtered_df[(filtered_df["Format"] == format_type) & (filtered_df["Style"] == "bowling")]
                    aggregated_bowling = bowling_data.groupby("Player Name", as_index=False).agg({"Wickets": "sum", "Average": "mean"})
                    top_bowling_performers = aggregated_bowling.nlargest(5, "Wickets")[["Player Name", "Wickets", "Average"]]
                    top_bowling_performers["Wickets"] = top_bowling_performers["Wickets"].astype(int)
                    top_bowling_performers["Average"] = top_bowling_performers["Average"].round(2)
                    st.table(top_bowling_performers)

    elif filter_type == "Year Wise":
            st.header("📊 Year Wise Analysis")
            years = sorted(df["Year"].dropna().unique())
            selected_year = st.sidebar.selectbox("Select Year", years)

            year_data = df[df["Year"] == selected_year]

            formats = ["test", "odi", "t20"]
            for format_type in formats:
                st.subheader(f"{format_type.upper()} Format in {selected_year}")

                # Batting and Bowling Side-by-Side
                col1, col2 = st.columns(2)

                with col1:
                    # Batting Contributions
                    batting_data = year_data[(year_data["Format"] == format_type) & (year_data["Style"] == "batting")]
                    batting_contributions = batting_data.groupby("Player Name", as_index=False).agg({"Runs": "sum"})
                    batting_top_5 = batting_contributions.nlargest(5, "Runs")
                    batting_others = pd.DataFrame({"Player Name": ["Others"], "Runs": [batting_contributions["Runs"].sum() - batting_top_5["Runs"].sum()]})
                    batting_final = pd.concat([batting_top_5, batting_others])

                    fig_batting = px.pie(
                        batting_final,
                        values="Runs",
                        names="Player Name",
                        title="Batting Contributions",
                        hole=0.4
                    )
                    st.plotly_chart(fig_batting)

                with col2:
                    # Bowling Contributions
                    bowling_data = year_data[(year_data["Format"] == format_type) & (year_data["Style"] == "bowling")]
                    bowling_contributions = bowling_data.groupby("Player Name", as_index=False).agg({"Wickets": "sum"})
                    bowling_top_5 = bowling_contributions.nlargest(5, "Wickets")
                    bowling_others = pd.DataFrame({"Player Name": ["Others"], "Wickets": [bowling_contributions["Wickets"].sum() - bowling_top_5["Wickets"].sum()]})
                    bowling_final = pd.concat([bowling_top_5, bowling_others])

                    fig_bowling = px.pie(
                        bowling_final,
                        values="Wickets",
                        names="Player Name",
                        title="Bowling Contributions",
                        hole=0.4
                    )
                    st.plotly_chart(fig_bowling)

    elif filter_type == "Player Comparison":
            #starts from here
            
            # Select Players for Comparison
            st.header("📊 Player Comparison")
            player_names = sorted(df["Player Name"].unique())
            player_1 = st.selectbox("Select Player 1", player_names)
            player_2 = st.selectbox("Select Player 2", [player for player in player_names if player != player_1])

            # Filter data for selected players
            player_1_data = df[df["Player Name"] == player_1]
            player_2_data = df[df["Player Name"] == player_2]
            
            # Style Selection (Batting vs Bowling)
            styles = ["batting", "bowling"]
            selected_style = st.selectbox("Select Style", styles)

            # Define the formats (Test, ODI, T20)
            formats = ["test", "odi", "t20"]

            # Function to filter and get data for each format
            def get_format_data(player_data, format_type, style):
                return player_data[(player_data["Format"] == format_type) & (player_data["Style"] == style)]

            # Create side-by-side comparison layout
            col1, col2 = st.columns(2)

            

            # Side-by-Side Comparison by Format
            for format_type in formats:
                st.subheader(f"{format_type.capitalize()} Format")

                # Filter data for the selected style and format
                player_1_format_data = get_format_data(player_1_data, format_type, selected_style)
                player_2_format_data = get_format_data(player_2_data, format_type, selected_style)

                # Merge the data for both players
                combined_data = pd.merge(
                    player_1_format_data[["Year", "Runs" if selected_style == "batting" else "Wickets"]],
                    player_2_format_data[["Year", "Runs" if selected_style == "batting" else "Wickets"]],
                    on="Year",
                    suffixes=(f" ({player_1})", f" ({player_2})")
                )

                # Rename columns for clarity
                combined_data.columns = ["Year", f"{player_1} {selected_style.capitalize()}", f"{player_2} {selected_style.capitalize()}"]

                # Show the combined table for comparison
                st.write(f"**{player_1} vs {player_2} in {format_type.capitalize()} Format**")
                st.dataframe(combined_data)

                # Show advanced metrics for batting/bowling
                if selected_style == "batting":
                    st.write(f"**Batting Average**")
                    st.write(f"{player_1}: {player_1_format_data['Average'].mean():.2f} | {player_2}: {player_2_format_data['Average'].mean():.2f}")
                    st.write(f"**Strike Rate**")
                    st.write(f"{player_1}: {player_1_format_data['Strike Rate'].mean():.2f} | {player_2}: {player_2_format_data['Strike Rate'].mean():.2f}")
                else:
                    st.write(f"**Bowling Economy Rate**")
                    st.write(f"{player_1}: {player_1_format_data['Economy Rate'].mean():.2f} | {player_2}: {player_2_format_data['Economy Rate'].mean():.2f}")
                    st.write(f"**Bowling Average**")
                    st.write(f"{player_1}: {player_1_format_data['Average'].mean():.2f} | {player_2}: {player_2_format_data['Average'].mean():.2f}")

            # Show overall comparison for each player and each format
            st.subheader("Overall Comparison Across All Formats")

            # For each player, show the total Runs or Wickets across all formats
            player_1_total = player_1_data[player_1_data["Style"] == selected_style].groupby("Format").agg({"Runs": "sum", "Wickets": "sum"})
            player_2_total = player_2_data[player_2_data["Style"] == selected_style].groupby("Format").agg({"Runs": "sum", "Wickets": "sum"})

            # Show the comparison as bar charts
            fig_overall_1 = px.bar(player_1_total, x=player_1_total.index, y="Runs" if selected_style == "batting" else "Wickets", title=f"{player_1} Total {selected_style.capitalize()} Across Formats")
            fig_overall_2 = px.bar(player_2_total, x=player_2_total.index, y="Runs" if selected_style == "batting" else "Wickets", title=f"{player_2} Total {selected_style.capitalize()} Across Formats")

            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(fig_overall_1, key=f"{player_1}_overall_chart")
            with col2:
                st.plotly_chart(fig_overall_2, key=f"{player_2}_overall_chart")

            # Final Conclusion/Comparison
            st.subheader(f"Final Comparison Summary Between {player_1} and {player_2}")
            if selected_style == "batting":
                st.write(f"In terms of batting, {player_1} has scored a total of {player_1_total['Runs'].sum()} runs across formats, while {player_2} has scored {player_2_total['Runs'].sum()} runs.")
            else:
                st.write(f"In terms of bowling, {player_1} has taken {player_1_total['Wickets'].sum()} wickets across formats, while {player_2} has taken {player_2_total['Wickets'].sum()} wickets.")
               
               
               
               
    elif filter_type == "Optimal Team Selector":
            from pulp import LpProblem, LpVariable, lpSum, LpMaximize, LpBinary

            formats = list(cricket_data.keys())
            format_selected = st.selectbox("Select Match Format", formats)

            years = [str(y) for y in range(2011, 2026)]
            if "start_year" not in st.session_state:
                st.session_state["start_year"] = "2011"
            if "end_year" not in st.session_state:
                st.session_state["end_year"] = "2025"

            col1, col2 = st.columns(2)
            with col1:
                valid_start_years = [y for y in years if int(y) <= int(st.session_state.get("end_year", "2025"))]
                start_year_index = valid_start_years.index(st.session_state["start_year"]) if st.session_state["start_year"] in valid_start_years else 0
                start_year = st.selectbox("Start Year", valid_start_years, index=start_year_index, key="start_year")

            with col2:
                valid_end_years = [y for y in years if int(y) >= int(st.session_state.get("start_year", "2011"))]
                end_year_index = valid_end_years.index(st.session_state["end_year"]) if st.session_state["end_year"] in valid_end_years else len(valid_end_years) - 1
                end_year = st.selectbox("End Year", valid_end_years, index=end_year_index, key="end_year")

            def overs_to_float(overs):
                try:
                    overs = str(overs)
                    if '.' in overs:
                        whole, fraction = overs.split('.')
                        return int(whole) + int(fraction) / 6
                    return float(overs)
                except:
                    return 0.0

            def economy_bonus(econ):
                if econ <= 4.0:
                    return 6
                elif econ <= 5.0:
                    return 4
                elif econ <= 6.0:
                    return 2
                elif econ > 9.0:
                    return -4
                return 0

            def infer_role(bat, bowl):
                if bat > 40 and bowl < 15:
                    return 'batter'
                elif bowl > 40 and bat < 15:
                    return 'bowler'
                elif bat >= 20 and bowl >= 20:
                    return 'allrounder'
                return 'other'

            def collect_player_data(cricket_data, format_selected, start_year, end_year):
                selected_years = [y for y in cricket_data[format_selected]["batting"] if int(start_year) <= int(y) <= int(end_year)]
                year_count = len(selected_years)
                batting_data, bowling_data = [], []
                for y in selected_years:
                    batting_data.extend(cricket_data[format_selected]["batting"][y])
                    bowling_data.extend(cricket_data[format_selected]["bowling"][y])

                bat_df = pd.DataFrame(batting_data)
                bat_df = bat_df[['Player Name', 'Runs', '4s', '6s', 'Ducks']].copy()
                for col in ['Runs', '4s', '6s', 'Ducks']:
                    bat_df[col] = pd.to_numeric(bat_df[col], errors='coerce').fillna(0)
                bat_df = bat_df.groupby('Player Name', as_index=False).sum()

                raw_bowl_df = pd.DataFrame(bowling_data)
                bowl_df = raw_bowl_df[['Player Name', 'Wickets', 'Runs', 'Overs']].copy()
                bowl_df[['Wickets', 'Runs']] = bowl_df[['Wickets', 'Runs']].apply(pd.to_numeric, errors='coerce').fillna(0)
                bowl_df['Overs'] = raw_bowl_df['Overs'].apply(overs_to_float)
                bowl_df = bowl_df.groupby('Player Name', as_index=False).sum()
                bowl_df['Economy Rate'] = bowl_df.apply(lambda x: x['Runs'] / x['Overs'] if x['Overs'] > 0 else 0.0, axis=1)

                bat_df['Bat_Points'] = (bat_df['Runs'] + bat_df['4s'] + 2 * bat_df['6s'] - 2 * bat_df['Ducks']) / year_count
                bowl_df['Bowl_Points'] = (bowl_df['Wickets'] * 25 / year_count) + bowl_df['Economy Rate'].apply(economy_bonus)

                df = pd.merge(bat_df, bowl_df, on='Player Name', how='outer').fillna(0)
                df['Total_Points'] = df['Bat_Points'] + df['Bowl_Points']
                df['Role'] = df.apply(lambda x: infer_role(x['Bat_Points'], x['Bowl_Points']), axis=1)
                return df

            def optimize_team(df):
                players = df['Player Name'].tolist()
                roles = df['Role'].tolist()
                points = df['Total_Points'].tolist()

                prob = LpProblem("Optimal_Team", LpMaximize)
                x = LpVariable.dicts("Player", players, cat=LpBinary)

                prob += lpSum([x[p] * pts for p, pts in zip(players, points)])
                prob += lpSum([x[p] for p in players]) == 11
                prob += lpSum([x[p] for p, r in zip(players, roles) if r in ['batter', 'allrounder']]) >= 6
                prob += lpSum([x[p] for p, r in zip(players, roles) if r in ['bowler', 'allrounder']]) >= 5

                prob.solve()
                selected_players = [p for p in players if x[p].varValue == 1]
                selected_df = df[df['Player Name'].isin(selected_players)].copy().sort_values(by='Total_Points', ascending=False)
                sorted_by_bat = selected_df.sort_values(by='Bat_Points', ascending=False)
                batters = sorted_by_bat.head(6)['Player Name'].tolist()
                selected_df['Assigned_Role'] = selected_df['Player Name'].apply(lambda p: 'batter' if p in batters else 'bowler')
                return selected_df

            st.subheader("🧠 Optimal Playing XI")
            df = collect_player_data(cricket_data, format_selected, start_year, end_year)
            optimal_df = optimize_team(df)
            st.dataframe(optimal_df[['Player Name', 'Assigned_Role', 'Bat_Points', 'Bowl_Points', 'Total_Points']].reset_index(drop=True))
            
    
if __name__ == "__main__":
    main()
