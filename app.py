import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Options Ratio Spread Scanner", page_icon="📊", layout="wide")
st.title("📊 F&O Options Ratio Spread Scanner (Call Side)")
st.subheader("Strategy: BUY 1 CE / SELL 3 CE — Upstox Engine Proto")

st.sidebar.header("⚙️ Scanner Settings")
min_credit_a = st.sidebar.slider("Minimum Credit A (₹)", 0.0, 5.0, 0.0, 0.1)
min_credit_b = st.sidebar.slider("Minimum Credit B (₹)", 0.0, 10.0, 0.0, 0.1)
max_net_debit = st.sidebar.number_input("Maximum Allowed Net Debit (₹)", value=1.0, step=0.5)

@st.cache_data
def get_mock_fo_stocks():
    return ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "BHARTIARTL", "ITC", "LT", "MARUTI"]

def generate_mock_option_chain(stock_name):
    base_prices = {"RELIANCE": 900, "SBIN": 800, "TCS": 4000, "INFY": 1500, "MARUTI": 10000}
    base = base_prices.get(stock_name, 1000)
    step = 100 if base >= 4000 else (20 if base >= 1500 else 10)
    strikes = [base + (i * step) for i in range(-5, 10)]
    chain = {}
    start_price = base * 0.03
    for idx, strike in enumerate(strikes):
        price = start_price * (0.75 ** idx) + random.uniform(-0.5, 0.5)
        chain[strike] = max(round(price, 2), 0.5)
    return chain

def scan_ratio_spreads(stock_name, option_chain, step_gap=4):
    sorted_strikes = sorted(list(option_chain.keys()))
    results = []
    for i in range(len(sorted_strikes)):
        if i < step_gap: continue
        j = i + step_gap
        if j >= len(sorted_strikes): break
        buy_strike, sell_strike = sorted_strikes[i], sorted_strikes[j]
        buy_price, sell_price = option_chain[buy_strike], option_chain[sell_strike]
        net_debit = buy_price - (3 * sell_price)
        credit_a = option_chain[sorted_strikes[i - 1]] - (3 * option_chain[sorted_strikes[j - 1]])
        condition_a = credit_a > min_credit_a
        credit_b = option_chain[sorted_strikes[i - step_gap]] - (3 * option_chain[sorted_strikes[j - step_gap]])
        condition_b = credit_b > min_credit_b
        if (condition_a or condition_b) and (net_debit <= max_net_debit):
            results.append({
                "Stock": stock_name,
                "Buy Strike": f"{buy_strike} CE (@₹{buy_price})",
                "Sell Strike": f"3 × {sell_strike} CE (@₹{sell_price})",
                "Net Debit/Credit": round(net_debit, 2),
                "Cond A (Credit)": f"✅ (₹{round(credit_a, 2)})" if condition_a else f"❌ (₹{round(credit_a, 2)})",
                "Cond B (Credit)": f"✅ (₹{round(credit_b, 2)})" if condition_b else f"❌ (₹{round(credit_b, 2)})",
            })
    return results

stocks_list = get_mock_fo_stocks()
if st.button("🚀 RUN FULL F&O SCAN", type="primary", use_container_width=True):
    all_qualified_trades = []
    for stock in stocks_list:
        all_qualified_trades.extend(scan_ratio_spreads(stock, generate_mock_option_chain(stock)))
    if all_qualified_trades:
        st.success(f"Scanning Complete! Found {len(all_qualified_trades)} qualified setup(s).")
        st.dataframe(pd.DataFrame(all_qualified_trades), use_container_width=True)
    else:
        st.warning("No stocks qualified today.")
else:
    st.info("💡 Click the button above to screen the market structures dynamically.")
