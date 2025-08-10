# STK - Stock Market Analysis Tool

A comprehensive Python-based stock market analysis application that provides real-time stock data, technical analysis, and market insights for NSE (National Stock Exchange) stocks.

## 🚀 Features

### Main Application (`tb.py`)
- **Real-time Stock Data**: Fetch live stock prices, volume, and OHLC data
- **Technical Analysis**: Get TradingView technical analysis recommendations for multiple timeframes
- **Interactive GUI**: Modern Tkinter-based interface with color-coded recommendations
- **Auto-updates**: Automatic data refresh every minute
- **Excel Integration**: Export and update data in Excel format
- **Multiple Timeframes**: Support for 1 minute, 15 minutes, 1 hour, and 1 day intervals

### NSE Data Tools
- **Open Interest Tracker** (`nse.py`): Monitor futures open interest for BANKNIFTY
- **NIFTY Tracker** (`nse_full.py`): Track NIFTY index open interest data

## 📋 Prerequisites

- Python 3.7 or higher
- Windows OS (tested on Windows 10/11)
- Internet connection for real-time data

## 🛠️ Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd stk
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv stkapp
   stkapp\Scripts\activate  # Windows
   ```

3. **Install required packages**
   ```bash
   pip install tkinter pandas openpyxl requests
   pip install tvDatafeed tradingview-ta
   ```

## 📦 Dependencies

The project uses the following key libraries:
- `tkinter` - GUI framework
- `pandas` - Data manipulation and Excel operations
- `openpyxl` - Excel file handling
- `tvDatafeed` - TradingView data integration
- `tradingview-ta` - Technical analysis
- `requests` - HTTP requests for NSE data

## 🚀 Usage

### Main Application
Run the main stock analysis tool:
```bash
python tb.py
```

**Features:**
- Select stocks from dropdown menu
- Choose time intervals (1 min, 15 min, 1 hour, 1 day)
- View real-time OHLC data and volume
- Get color-coded technical analysis recommendations
- Auto-updates every minute
- Excel export functionality

### NSE Tools
Run individual NSE tracking tools:
```bash
python nse.py          # BANKNIFTY open interest
python nse_full.py     # NIFTY open interest
```

## 📊 Data Sources

- **Stock Data**: TradingView API (public data, no login required)
- **Technical Analysis**: TradingView Technical Analysis
- **NSE Data**: NSE India official APIs
- **Excel Storage**: Local Excel files for data persistence

## 🎨 Interface Features

- **Color-coded Recommendations**:
  - 🟢 Green: BUY/STRONG_BUY
  - 🔴 Red: SELL/STRONG_SELL
  - ⚪ Gray: NEUTRAL

- **Real-time Updates**: Automatic refresh every 60 seconds
- **Responsive Design**: Scrollable tables with proper column headers
- **Error Handling**: User-friendly error messages and warnings

## 📁 File Structure

```
stk/
├── tb.py                 # Main application
├── nse.py               # BANKNIFTY open interest tracker
├── nse_full.py          # NIFTY open interest tracker
├── stock_data.xlsx      # Stock data storage
├── README.md            # This file
└── stkapp/              # Virtual environment
```

## ⚠️ Important Notes

1. **Excel File Access**: Ensure `stock_data.xlsx` is not open in Excel while the application is running
2. **API Limits**: Be mindful of API rate limits when fetching data
3. **Internet Connection**: Requires stable internet for real-time data
4. **Windows Compatibility**: Designed for Windows OS

## 🔧 Troubleshooting

### Common Issues:
1. **Excel File Locked**: Close Excel before running the application
2. **API Errors**: Check internet connection and API availability
3. **Import Errors**: Ensure all dependencies are installed correctly

### Solutions:
- Restart the application if data stops updating
- Check firewall settings for API access
- Verify Python environment and package installations

## 📈 Future Enhancements

- [ ] Add more technical indicators
- [ ] Implement chart visualization
- [ ] Add portfolio tracking
- [ ] Support for more exchanges
- [ ] Historical data analysis
- [ ] Alert system for price movements

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve the project.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 📞 Support

For questions or support, please open an issue in the project repository.

---

**Disclaimer**: This tool is for educational and informational purposes only. It does not constitute financial advice. Always do your own research before making investment decisions.
