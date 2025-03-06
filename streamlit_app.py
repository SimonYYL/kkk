import streamlit as st
import pandas as pd
import gdown
from io import BytesIO
import os

# Google Drive File ID
FILE_ID = "1IReM77tV2si3iyDpYBRMTmkD7xu1HBna"

# Local file path
LOCAL_FILE_PATH = "anes_timeseries_cdf_stata_20220916.dta"

@st.cache_data
def download_and_load_data():
    try:
        # If file does not exist locally, download it
        if not os.path.exists(LOCAL_FILE_PATH):
            file_url = f"https://drive.google.com/uc?id={FILE_ID}"
            gdown.download(file_url, LOCAL_FILE_PATH, quiet=False)

        # Load the dataset
        return pd.read_stata(LOCAL_FILE_PATH)

    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        return pd.DataFrame()

df = download_and_load_data()

st.title("Query-Based Column Selector -- DSCI320 SAT")

# Display available columns
if not df.empty:
    st.write("### Available Columns")
    st.code(", ".join(df.columns), language="python")

    # User input for column selection
    user_input = st.text_area(
        "Paste column names (comma-separated)",
        placeholder="e.g., col1, col2, col3"
    )

    # Process input: Remove duplicates, strip spaces, and ensure case-sensitivity matches
    selected_columns = list(set(col.strip() for col in user_input.split(",") if col.strip()))

    # Apply button
    if st.button("Apply"):
        if not selected_columns:
            st.warning("Please enter at least one column name.")
        else:
            # Identify invalid columns
            missing_cols = [col for col in selected_columns if col not in df.columns]

            if missing_cols:
                st.error(f"Invalid columns: {', '.join(missing_cols)}")
            else:
                subset_df = df[selected_columns]
                st.success("Subset generated successfully!")

                # Display the subset in an expandable section
                with st.expander("View Selected Data"):
                    st.dataframe(subset_df, use_container_width=True)

                # Convert DataFrame to CSV
                def convert_df_to_csv(df):
                    output = BytesIO()
                    df.to_csv(output, index=False)
                    output.seek(0)
                    return output

                csv_data = convert_df_to_csv(subset_df)

                # Provide Download Option
                st.download_button(
                    label="Save Subset as CSV",
                    data=csv_data,
                    file_name="subset.csv",
                    mime="text/csv"
                )
else:
    st.error("The dataset could not be loaded. Please check the Google Drive file link.")
