import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Stock Exchange EDA Dashboard", page_icon="📈", layout="wide"
)

st.title("📈 Stock Exchange Exploratory Data Analysis")
st.write(
    "Explore historical stock prices, moving averages, trading volume, and correlations interactively."
)


# Load Dataset (with automatic fallback generation if file is missing)
@st.cache_data
def load_data():
    try:
        # Try loading your uploaded dataset filename
        df = pd.read_csv("stock_exchange_data.csv")
    except:
        # Fallback sample generator if file isn't uploaded yet
        np.random.seed(42)
        date_range = pd.date_range(start="2023-01-01", periods=250, freq="B")
        price = 150 * np.exp(
            np.cumsum(np.random.normal(0.0005, 0.015, size=250))
        )
        df = pd.DataFrame(
            {
                "Date": date_range.strftime("%Y-%m-%d"),
                "Open": np.round(price * 0.99, 2),
                "High": np.round(price * 1.02, 2),
                "Low": np.round(price * 0.98, 2),
                "Close": np.round(price, 2),
                "Volume": np.random.randint(1000000, 20000000, size=250),
            }
        )
    return df


df = load_data()

# Clean columns
df.columns = df.columns.str.strip()
if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)

# Sidebar controls
st.sidebar.header("📊 Dashboard Controls")
show_table = st.sidebar.checkbox("Show Raw Data Table", value=True)

# Main Metrics
col1, col2, col3 = st.columns(3)
close_col = [c for c in df.columns if "close" in c.lower()][0]
latest_price = df[close_col].iloc[-1]
price_change = latest_price - df[close_col].iloc[0]

col1.metric("Latest Close Price", f"${latest_price:,.2f}")
col2.metric(
    "Total Price Change",
    f"${price_change:,.2f}",
    delta=f"{(price_change/df[close_col].iloc[0])*100:.2f}%",
)
col3.metric("Total Trading Records", f"{len(df):,}")

# Show Raw Data
if show_table:
    st.subheader("📋 Dataset Preview")
    st.dataframe(df.tail(10))

# Closing Price & Moving Averages Chart
st.subheader("📉 Stock Price & Moving Averages")
df["MA_50"] = df[close_col].rolling(window=20).mean()
df["MA_200"] = df[close_col].rolling(window=50).mean()

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(
    df.index,
    df[close_col],
    label="Close Price",
    color="royalblue",
    linewidth=1.5,
)
ax.plot(
    df.index, df["MA_50"], label="20-Period MA", color="orange", linestyle="--"
)
ax.plot(
    df.index,
    df["MA_200"],
    label="50-Period MA",
    color="crimson",
    linestyle="--",
)
ax.set_title("Price Trend Analysis", fontsize=12, fontweight="bold")
ax.set_xlabel("Date")
ax.set_ylabel("Price")
ax.legend()
st.pyplot(fig)

# Volume Chart
vol_cols = [
    c for c in df.columns if "vol" in c.lower() or "volume" in c.lower()
]
if vol_cols:
    st.subheader("📊 Trading Volume")
    fig_vol, ax_vol = plt.subplots(figsize=(12, 3))
    ax_vol.bar(df.index, df[vol_cols[0]], color="forestgreen", alpha=0.6)
    ax_vol.set_title("Volume History", fontsize=12, fontweight="bold")
    st.pyplot(fig_vol)