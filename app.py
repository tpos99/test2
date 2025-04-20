import streamlit as st
import requests
import pandas as pd
import datetime
import time

# Judul Aplikasi
st.title("Analisis Data BTC, Emas, dan SPY dari Yahoo Finance API (RapidAPI)")

# Rentang tanggal
start_date = st.date_input("Tanggal Mulai", datetime.date(2020, 1, 1))
end_date = st.date_input("Tanggal Akhir", datetime.date.today())

# API Key dan URL
url = "https://yahoo-finance1.p.rapidapi.com/stock/v2/get-historical-data"

headers = {
    "X-RapidAPI-Host": "yahoo-finance1.p.rapidapi.com",
    "X-RapidAPI-Key": "YOUR_RAPIDAPI_KEY"  # Ganti dengan API Key kamu
}

# Simbol dari Yahoo Finance
symbols = {
    "Bitcoin (BTC-USD)": "BTC-USD",
    "Gold (Emas - GC=F)": "GC=F",
    "SPY (S&P 500 ETF)": "SPY"
}

# Pilihan aset
selected_assets = st.multiselect(
    "Pilih aset yang ingin ditampilkan:",
    list(symbols.keys()),
    default=list(symbols.keys())
)

# Fungsi untuk mengambil data dari API Yahoo Finance (RapidAPI)
def get_data(symbol, start, end):
    params = {
        "symbol": symbol,
        "region": "US",
        "lang": "en",
        "interval": "1d",
        "start": int(datetime.datetime(start.year, start.month, start.day).timestamp()),
        "end": int(datetime.datetime(end.year, end.month, end.day).timestamp())
    }

    response = None
    attempt = 0
    while attempt < 3:  # Mencoba maksimal 3 kali
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            break
        elif response.status_code == 429:
            # Jika menerima status 429 (terlalu banyak permintaan), tunggu 60 detik
            st.warning("Terlalu banyak permintaan, menunggu selama 60 detik...")
            time.sleep(60)
            attempt += 1
        else:
            st.error(f"Error mengambil data untuk {symbol}: {response.status_code}")
            return pd.DataFrame()  # Kembalikan DataFrame kosong jika ada error selain 429

    if response and response.status_code == 200:
        data = response.json()
        
        if 'prices' in data:
            df = pd.DataFrame(data['prices'])
            df['date'] = pd.to_datetime(df['date'], unit='s')
            df.set_index('date', inplace=True)
            df = df[['close']]  # Ambil harga penutupan
            df.columns = [symbol]
            return df
        else:
            st.warning(f"Tidak ada data yang tersedia untuk {symbol}.")
            return pd.DataFrame()  # Jika tidak ada data
    else:
        return pd.DataFrame()  # Kembalikan DataFrame kosong jika tidak berhasil mengambil data

# Gabungkan data
if selected_assets:
    df_list = [get_data(symbols[asset], start_date, end_date) for asset in selected_assets]
    
    # Filter DataFrame kosong
    df_list = [df for df in df_list if not df.empty]
    
    if df_list:
        merged_data = pd.concat(df_list, axis=1)
        st.subheader("Data Harga Penutupan")
        st.dataframe(merged_data.tail())

        st.subheader("Visualisasi Harga")
        st.line_chart(merged_data)
    else:
        st.warning("Tidak ada data yang dapat ditampilkan.")
else:
    st.warning("Pilih setidaknya satu aset untuk ditampilkan.")
