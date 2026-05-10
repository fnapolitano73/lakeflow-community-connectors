# **Alpha Vantage API Documentation**

## **Authorization**

- **Chosen method**: API Key authentication via query parameter.
- **Base URL**: `https://www.alphavantage.co/query`
- **Auth placement**:
  - Query parameter: `apikey=<YOUR_API_KEY>`
  - The API key must be included in every API request as a query parameter.
- **How to obtain an API key**:
  - Free tier: Register at https://www.alphavantage.co/support/#api-key to get a free API key.
  - Premium tier: Purchase from https://www.alphavantage.co/premium/ for higher rate limits.
- **Other supported methods**: None. Alpha Vantage exclusively uses API key authentication.

Example authenticated request:

```bash
curl -X GET \
  "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=IBM&apikey=YOUR_API_KEY"
```

Notes:
- Rate limits are enforced based on the API key.
- **Free tier**: 25 requests per day, 5 requests per minute.
- **Premium tiers**: Higher limits based on subscription level (75 to 1200+ requests per minute).
- Rate limit errors return a JSON response with a `Note` field containing the rate limit message.


## **Object List**

For connector purposes, Alpha Vantage API endpoints are treated as **objects/tables**.
The object list is **static** (defined by the connector), not discovered dynamically from an API.

Alpha Vantage does not provide a discovery API for available endpoints. The connector defines which "tables" are supported based on the official API documentation.

### Core Stock APIs

| Object Name | Description | API Function | Required Parameters | Ingestion Type |
|-------------|-------------|--------------|---------------------|----------------|
| `time_series_intraday` | Intraday time series (1min, 5min, 15min, 30min, 60min) | `TIME_SERIES_INTRADAY` | `symbol`, `interval` | `append` |
| `time_series_daily` | Daily time series (open, high, low, close, volume) | `TIME_SERIES_DAILY` | `symbol` | `append` |
| `time_series_daily_adjusted` | Daily adjusted time series including dividends and splits | `TIME_SERIES_DAILY_ADJUSTED` | `symbol` | `append` |
| `time_series_weekly` | Weekly time series | `TIME_SERIES_WEEKLY` | `symbol` | `append` |
| `time_series_weekly_adjusted` | Weekly adjusted time series | `TIME_SERIES_WEEKLY_ADJUSTED` | `symbol` | `append` |
| `time_series_monthly` | Monthly time series | `TIME_SERIES_MONTHLY` | `symbol` | `append` |
| `time_series_monthly_adjusted` | Monthly adjusted time series | `TIME_SERIES_MONTHLY_ADJUSTED` | `symbol` | `append` |
| `global_quote` | Latest price and volume information | `GLOBAL_QUOTE` | `symbol` | `snapshot` |
| `symbol_search` | Search for stocks by keywords | `SYMBOL_SEARCH` | `keywords` | `snapshot` |
| `market_status` | Global market open/close status | `MARKET_STATUS` | (none) | `snapshot` |

### Fundamental Data

| Object Name | Description | API Function | Required Parameters | Ingestion Type |
|-------------|-------------|--------------|---------------------|----------------|
| `company_overview` | Company fundamentals and key statistics | `OVERVIEW` | `symbol` | `snapshot` |
| `etf_profile` | ETF profile and holdings data | `ETF_PROFILE` | `symbol` | `snapshot` |
| `income_statement` | Annual and quarterly income statements | `INCOME_STATEMENT` | `symbol` | `snapshot` |
| `balance_sheet` | Annual and quarterly balance sheets | `BALANCE_SHEET` | `symbol` | `snapshot` |
| `cash_flow` | Annual and quarterly cash flow statements | `CASH_FLOW` | `symbol` | `snapshot` |
| `earnings` | Annual and quarterly earnings (EPS) | `EARNINGS` | `symbol` | `snapshot` |
| `earnings_calendar` | Upcoming earnings announcements | `EARNINGS_CALENDAR` | (optional: `symbol`, `horizon`) | `snapshot` |
| `ipo_calendar` | Upcoming and recent IPOs | `IPO_CALENDAR` | (none) | `snapshot` |
| `listing_status` | Active and delisted stocks/ETFs | `LISTING_STATUS` | (optional: `date`, `state`) | `snapshot` |
| `dividends` | Historical dividend data | `DIVIDENDS` | `symbol` | `append` |
| `splits` | Historical stock split data | `SPLITS` | `symbol` | `append` |

### Forex (FX)

| Object Name | Description | API Function | Required Parameters | Ingestion Type |
|-------------|-------------|--------------|---------------------|----------------|
| `fx_exchange_rate` | Real-time exchange rate | `CURRENCY_EXCHANGE_RATE` | `from_currency`, `to_currency` | `snapshot` |
| `fx_daily` | Daily forex time series | `FX_DAILY` | `from_symbol`, `to_symbol` | `append` |
| `fx_weekly` | Weekly forex time series | `FX_WEEKLY` | `from_symbol`, `to_symbol` | `append` |
| `fx_monthly` | Monthly forex time series | `FX_MONTHLY` | `from_symbol`, `to_symbol` | `append` |

### Cryptocurrency

| Object Name | Description | API Function | Required Parameters | Ingestion Type |
|-------------|-------------|--------------|---------------------|----------------|
| `crypto_exchange_rate` | Real-time crypto exchange rate | `CURRENCY_EXCHANGE_RATE` | `from_currency`, `to_currency` | `snapshot` |
| `digital_currency_daily` | Daily crypto time series | `DIGITAL_CURRENCY_DAILY` | `symbol`, `market` | `append` |
| `digital_currency_weekly` | Weekly crypto time series | `DIGITAL_CURRENCY_WEEKLY` | `symbol`, `market` | `append` |
| `digital_currency_monthly` | Monthly crypto time series | `DIGITAL_CURRENCY_MONTHLY` | `symbol`, `market` | `append` |

### Commodities

| Object Name | Description | API Function | Required Parameters | Ingestion Type |
|-------------|-------------|--------------|---------------------|----------------|
| `wti` | WTI crude oil prices | `WTI` | (none) | `append` |
| `brent` | Brent crude oil prices | `BRENT` | (none) | `append` |
| `natural_gas` | Natural gas prices | `NATURAL_GAS` | (none) | `append` |
| `copper` | Copper prices | `COPPER` | (none) | `append` |
| `aluminum` | Aluminum prices | `ALUMINUM` | (none) | `append` |
| `wheat` | Wheat prices | `WHEAT` | (none) | `append` |
| `corn` | Corn prices | `CORN` | (none) | `append` |
| `cotton` | Cotton prices | `COTTON` | (none) | `append` |
| `sugar` | Sugar prices | `SUGAR` | (none) | `append` |
| `coffee` | Coffee prices | `COFFEE` | (none) | `append` |
| `all_commodities` | Global commodities price index | `ALL_COMMODITIES` | (none) | `append` |

### Economic Indicators

| Object Name | Description | API Function | Required Parameters | Ingestion Type |
|-------------|-------------|--------------|---------------------|----------------|
| `real_gdp` | US Real GDP | `REAL_GDP` | (none) | `append` |
| `real_gdp_per_capita` | US Real GDP per capita | `REAL_GDP_PER_CAPITA` | (none) | `append` |
| `treasury_yield` | US Treasury yields | `TREASURY_YIELD` | (none) | `append` |
| `federal_funds_rate` | Federal funds rate | `FEDERAL_FUNDS_RATE` | (none) | `append` |
| `cpi` | Consumer Price Index | `CPI` | (none) | `append` |
| `inflation` | Inflation rate | `INFLATION` | (none) | `append` |
| `retail_sales` | Retail sales | `RETAIL_SALES` | (none) | `append` |
| `durables` | Durable goods orders | `DURABLES` | (none) | `append` |
| `unemployment` | Unemployment rate | `UNEMPLOYMENT` | (none) | `append` |
| `nonfarm_payroll` | Non-farm payroll | `NONFARM_PAYROLL` | (none) | `append` |

### Technical Indicators

| Object Name | Description | API Function | Required Parameters | Ingestion Type |
|-------------|-------------|--------------|---------------------|----------------|
| `sma` | Simple Moving Average | `SMA` | `symbol`, `interval`, `time_period`, `series_type` | `append` |
| `ema` | Exponential Moving Average | `EMA` | `symbol`, `interval`, `time_period`, `series_type` | `append` |
| `wma` | Weighted Moving Average | `WMA` | `symbol`, `interval`, `time_period`, `series_type` | `append` |
| `dema` | Double Exponential Moving Average | `DEMA` | `symbol`, `interval`, `time_period`, `series_type` | `append` |
| `tema` | Triple Exponential Moving Average | `TEMA` | `symbol`, `interval`, `time_period`, `series_type` | `append` |
| `trima` | Triangular Moving Average | `TRIMA` | `symbol`, `interval`, `time_period`, `series_type` | `append` |
| `kama` | Kaufman Adaptive Moving Average | `KAMA` | `symbol`, `interval`, `time_period`, `series_type` | `append` |
| `mama` | MESA Adaptive Moving Average | `MAMA` | `symbol`, `interval`, `series_type` | `append` |
| `vwap` | Volume Weighted Average Price (Premium) | `VWAP` | `symbol`, `interval` | `append` |
| `t3` | Triple Exponential Moving Average (T3) | `T3` | `symbol`, `interval`, `time_period`, `series_type` | `append` |
| `macd` | MACD | `MACD` | `symbol`, `interval`, `series_type` | `append` |
| `macdext` | MACD with Controllable MA Type | `MACDEXT` | `symbol`, `interval`, `series_type` | `append` |
| `stoch` | Stochastic Oscillator | `STOCH` | `symbol`, `interval` | `append` |
| `stochf` | Stochastic Fast | `STOCHF` | `symbol`, `interval` | `append` |
| `rsi` | Relative Strength Index | `RSI` | `symbol`, `interval`, `time_period`, `series_type` | `append` |
| `stochrsi` | Stochastic RSI | `STOCHRSI` | `symbol`, `interval`, `time_period`, `series_type` | `append` |
| `willr` | Williams %R | `WILLR` | `symbol`, `interval`, `time_period` | `append` |
| `adx` | Average Directional Index | `ADX` | `symbol`, `interval`, `time_period` | `append` |
| `adxr` | Average Directional Movement Index Rating | `ADXR` | `symbol`, `interval`, `time_period` | `append` |
| `apo` | Absolute Price Oscillator | `APO` | `symbol`, `interval`, `series_type` | `append` |
| `ppo` | Percentage Price Oscillator | `PPO` | `symbol`, `interval`, `series_type` | `append` |
| `mom` | Momentum | `MOM` | `symbol`, `interval`, `time_period`, `series_type` | `append` |
| `bop` | Balance of Power | `BOP` | `symbol`, `interval` | `append` |
| `cci` | Commodity Channel Index | `CCI` | `symbol`, `interval`, `time_period` | `append` |
| `cmo` | Chande Momentum Oscillator | `CMO` | `symbol`, `interval`, `time_period`, `series_type` | `append` |
| `roc` | Rate of Change | `ROC` | `symbol`, `interval`, `time_period`, `series_type` | `append` |
| `rocr` | Rate of Change Ratio | `ROCR` | `symbol`, `interval`, `time_period`, `series_type` | `append` |
| `aroon` | Aroon Indicator | `AROON` | `symbol`, `interval`, `time_period` | `append` |
| `aroonosc` | Aroon Oscillator | `AROONOSC` | `symbol`, `interval`, `time_period` | `append` |
| `mfi` | Money Flow Index | `MFI` | `symbol`, `interval`, `time_period` | `append` |
| `trix` | 1-day Rate of Change of Triple Smooth EMA | `TRIX` | `symbol`, `interval`, `time_period`, `series_type` | `append` |
| `ultosc` | Ultimate Oscillator | `ULTOSC` | `symbol`, `interval` | `append` |
| `dx` | Directional Movement Index | `DX` | `symbol`, `interval`, `time_period` | `append` |
| `minus_di` | Minus Directional Indicator | `MINUS_DI` | `symbol`, `interval`, `time_period` | `append` |
| `plus_di` | Plus Directional Indicator | `PLUS_DI` | `symbol`, `interval`, `time_period` | `append` |
| `minus_dm` | Minus Directional Movement | `MINUS_DM` | `symbol`, `interval`, `time_period` | `append` |
| `plus_dm` | Plus Directional Movement | `PLUS_DM` | `symbol`, `interval`, `time_period` | `append` |
| `bbands` | Bollinger Bands | `BBANDS` | `symbol`, `interval`, `time_period`, `series_type` | `append` |
| `midpoint` | Midpoint over Period | `MIDPOINT` | `symbol`, `interval`, `time_period`, `series_type` | `append` |
| `midprice` | Midpoint Price over Period | `MIDPRICE` | `symbol`, `interval`, `time_period` | `append` |
| `sar` | Parabolic SAR | `SAR` | `symbol`, `interval` | `append` |
| `trange` | True Range | `TRANGE` | `symbol`, `interval` | `append` |
| `atr` | Average True Range | `ATR` | `symbol`, `interval`, `time_period` | `append` |
| `natr` | Normalized Average True Range | `NATR` | `symbol`, `interval`, `time_period` | `append` |
| `ad` | Chaikin A/D Line | `AD` | `symbol`, `interval` | `append` |
| `adosc` | Chaikin A/D Oscillator | `ADOSC` | `symbol`, `interval` | `append` |
| `obv` | On Balance Volume | `OBV` | `symbol`, `interval` | `append` |
| `ht_trendline` | Hilbert Transform - Instantaneous Trendline | `HT_TRENDLINE` | `symbol`, `interval`, `series_type` | `append` |
| `ht_sine` | Hilbert Transform - SineWave | `HT_SINE` | `symbol`, `interval`, `series_type` | `append` |
| `ht_trendmode` | Hilbert Transform - Trend vs Cycle Mode | `HT_TRENDMODE` | `symbol`, `interval`, `series_type` | `append` |
| `ht_dcperiod` | Hilbert Transform - Dominant Cycle Period | `HT_DCPERIOD` | `symbol`, `interval`, `series_type` | `append` |
| `ht_dcphase` | Hilbert Transform - Dominant Cycle Phase | `HT_DCPHASE` | `symbol`, `interval`, `series_type` | `append` |
| `ht_phasor` | Hilbert Transform - Phasor Components | `HT_PHASOR` | `symbol`, `interval`, `series_type` | `append` |

### Alpha Intelligence

| Object Name | Description | API Function | Required Parameters | Ingestion Type |
|-------------|-------------|--------------|---------------------|----------------|
| `news_sentiment` | News and sentiment data | `NEWS_SENTIMENT` | (optional: `tickers`, `topics`, `time_from`, `time_to`) | `append` |
| `top_gainers_losers` | Top gainers, losers, and most active | `TOP_GAINERS_LOSERS` | (none) | `snapshot` |
| `insider_transactions` | Insider buying/selling transactions | `INSIDER_TRANSACTIONS` | `symbol` | `append` |
| `analytics_fixed_window` | Winning/losing portfolios analytics | `ANALYTICS_FIXED_WINDOW` | `SYMBOLS`, `RANGE`, `INTERVAL` | `snapshot` |
| `analytics_sliding_window` | Running analytics over sliding window | `ANALYTICS_SLIDING_WINDOW` | `SYMBOLS`, `RANGE`, `INTERVAL`, `WINDOW_SIZE` | `snapshot` |

**Connector scope for initial implementation**:
- Initial implementation focuses on the most commonly used objects: `time_series_daily`, `global_quote`, `company_overview`, and `earnings`.
- Other objects are documented for future extension.


## **Object Schema**

### General notes

- Alpha Vantage provides static JSON schemas; fields are consistent per endpoint.
- For the connector, we define **tabular schemas** per object, derived from the JSON representation.
- Time series data is returned as nested objects keyed by date/timestamp; the connector will flatten these to rows.
- Numeric values are returned as strings and must be parsed to appropriate numeric types.

### `time_series_daily` object (primary table)

**Source endpoint**:
`GET /query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize={outputsize}&apikey={key}`

**Parameters**:
- `symbol` (required): Stock ticker symbol (e.g., "AAPL", "IBM")
- `outputsize` (optional): "compact" (last 100 data points) or "full" (full-length time series of 20+ years). Default: "compact"

**Response structure**:
```json
{
    "Meta Data": {
        "1. Information": "Daily Prices (open, high, low, close) and Volumes",
        "2. Symbol": "IBM",
        "3. Last Refreshed": "2024-01-15",
        "4. Output Size": "Compact",
        "5. Time Zone": "US/Eastern"
    },
    "Time Series (Daily)": {
        "2024-01-15": {
            "1. open": "185.0000",
            "2. high": "186.5000",
            "3. low": "184.2000",
            "4. close": "185.5000",
            "5. volume": "5234567"
        },
        "2024-01-14": {
            "1. open": "184.0000",
            "2. high": "185.0000",
            "3. low": "183.0000",
            "4. close": "184.5000",
            "5. volume": "4567890"
        }
    }
}
```

**High-level schema (connector view - flattened)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `symbol` | string (connector-derived) | Stock symbol from request parameter. |
| `date` | date | Trading date (key from time series object). |
| `open` | decimal | Opening price. |
| `high` | decimal | Highest price during the day. |
| `low` | decimal | Lowest price during the day. |
| `close` | decimal | Closing price. |
| `volume` | long | Trading volume. |
| `last_refreshed` | date | Last refresh date from meta data. |
| `time_zone` | string | Time zone of the data (from meta data). |

**Example request**:

```bash
curl -X GET \
  "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=IBM&outputsize=compact&apikey=YOUR_API_KEY"
```


### `time_series_daily_adjusted` object

**Source endpoint**:
`GET /query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize={outputsize}&apikey={key}`

**High-level schema (connector view - flattened)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `symbol` | string (connector-derived) | Stock symbol from request parameter. |
| `date` | date | Trading date. |
| `open` | decimal | Opening price. |
| `high` | decimal | Highest price during the day. |
| `low` | decimal | Lowest price during the day. |
| `close` | decimal | Closing price (unadjusted). |
| `adjusted_close` | decimal | Adjusted closing price (accounting for splits and dividends). |
| `volume` | long | Trading volume. |
| `dividend_amount` | decimal | Dividend amount on this date. |
| `split_coefficient` | decimal | Split coefficient (e.g., 2.0 for a 2-for-1 split). |


### `time_series_intraday` object

**Source endpoint**:
`GET /query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&outputsize={outputsize}&apikey={key}`

**Parameters**:
- `symbol` (required): Stock ticker symbol
- `interval` (required): "1min", "5min", "15min", "30min", or "60min"
- `outputsize` (optional): "compact" or "full"
- `adjusted` (optional): "true" or "false" (default: true)
- `extended_hours` (optional): "true" or "false" (default: true)
- `month` (optional): Filter to specific month in YYYY-MM format

**High-level schema (connector view - flattened)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `symbol` | string (connector-derived) | Stock symbol from request parameter. |
| `timestamp` | timestamp | Timestamp of the data point. |
| `interval` | string (connector-derived) | Interval from request parameter. |
| `open` | decimal | Opening price. |
| `high` | decimal | Highest price in the interval. |
| `low` | decimal | Lowest price in the interval. |
| `close` | decimal | Closing price. |
| `volume` | long | Trading volume in the interval. |


### `global_quote` object

**Source endpoint**:
`GET /query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={key}`

**Response structure**:
```json
{
    "Global Quote": {
        "01. symbol": "IBM",
        "02. open": "185.0000",
        "03. high": "186.5000",
        "04. low": "184.0000",
        "05. price": "185.5000",
        "06. volume": "5234567",
        "07. latest trading day": "2024-01-15",
        "08. previous close": "184.0000",
        "09. change": "1.5000",
        "10. change percent": "0.8152%"
    }
}
```

**High-level schema (connector view)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `symbol` | string | Stock symbol. |
| `open` | decimal | Opening price. |
| `high` | decimal | Day's high. |
| `low` | decimal | Day's low. |
| `price` | decimal | Current/latest price. |
| `volume` | long | Trading volume. |
| `latest_trading_day` | date | Latest trading day. |
| `previous_close` | decimal | Previous day's closing price. |
| `change` | decimal | Price change from previous close. |
| `change_percent` | string | Percentage change (includes % symbol). |


### `company_overview` object

**Source endpoint**:
`GET /query?function=OVERVIEW&symbol={symbol}&apikey={key}`

**High-level schema (connector view)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `symbol` | string | Stock ticker symbol. |
| `asset_type` | string | Type of asset (e.g., "Common Stock"). |
| `name` | string | Company name. |
| `description` | string | Company description (long text). |
| `cik` | string | SEC Central Index Key. |
| `exchange` | string | Stock exchange (e.g., "NASDAQ", "NYSE"). |
| `currency` | string | Trading currency. |
| `country` | string | Country of headquarters. |
| `sector` | string | Business sector. |
| `industry` | string | Specific industry. |
| `address` | string | Company headquarters address. |
| `fiscal_year_end` | string | Month when fiscal year ends. |
| `latest_quarter` | date | Most recent reported quarter end date. |
| `market_capitalization` | long | Market cap in currency units. |
| `ebitda` | long | EBITDA value. |
| `pe_ratio` | decimal | Price-to-earnings ratio. |
| `peg_ratio` | decimal | PEG ratio. |
| `book_value` | decimal | Book value per share. |
| `dividend_per_share` | decimal | Annual dividend per share. |
| `dividend_yield` | decimal | Dividend yield as decimal. |
| `eps` | decimal | Earnings per share. |
| `revenue_per_share_ttm` | decimal | Revenue per share (trailing twelve months). |
| `profit_margin` | decimal | Profit margin as decimal. |
| `operating_margin_ttm` | decimal | Operating margin TTM. |
| `return_on_assets_ttm` | decimal | Return on assets TTM. |
| `return_on_equity_ttm` | decimal | Return on equity TTM. |
| `revenue_ttm` | long | Revenue TTM. |
| `gross_profit_ttm` | long | Gross profit TTM. |
| `diluted_eps_ttm` | decimal | Diluted EPS TTM. |
| `quarterly_earnings_growth_yoy` | decimal | Quarterly earnings growth YoY. |
| `quarterly_revenue_growth_yoy` | decimal | Quarterly revenue growth YoY. |
| `analyst_target_price` | decimal | Analyst target price. |
| `analyst_rating_strong_buy` | integer | Number of strong buy ratings. |
| `analyst_rating_buy` | integer | Number of buy ratings. |
| `analyst_rating_hold` | integer | Number of hold ratings. |
| `analyst_rating_sell` | integer | Number of sell ratings. |
| `analyst_rating_strong_sell` | integer | Number of strong sell ratings. |
| `trailing_pe` | decimal | Trailing P/E ratio. |
| `forward_pe` | decimal | Forward P/E ratio. |
| `price_to_sales_ratio_ttm` | decimal | Price to sales ratio TTM. |
| `price_to_book_ratio` | decimal | Price to book ratio. |
| `ev_to_revenue` | decimal | Enterprise value to revenue. |
| `ev_to_ebitda` | decimal | Enterprise value to EBITDA. |
| `beta` | decimal | Beta coefficient. |
| `week_52_high` | decimal | 52-week high price. |
| `week_52_low` | decimal | 52-week low price. |
| `day_50_moving_average` | decimal | 50-day moving average. |
| `day_200_moving_average` | decimal | 200-day moving average. |
| `shares_outstanding` | long | Total shares outstanding. |
| `dividend_date` | date | Next dividend date. |
| `ex_dividend_date` | date | Ex-dividend date. |


### `income_statement` object

**Source endpoint**:
`GET /query?function=INCOME_STATEMENT&symbol={symbol}&apikey={key}`

**Response structure**:
```json
{
    "symbol": "IBM",
    "annualReports": [
        {
            "fiscalDateEnding": "2023-12-31",
            "reportedCurrency": "USD",
            "grossProfit": "32688000000",
            "totalRevenue": "61860000000",
            "costOfRevenue": "29172000000",
            "operatingIncome": "7478000000",
            "netIncome": "7502000000",
            "ebit": "8237000000",
            "ebitda": "12890000000",
            ...
        }
    ],
    "quarterlyReports": [...]
}
```

**High-level schema for annual reports (connector view)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `symbol` | string (connector-derived) | Stock symbol. |
| `report_type` | string (connector-derived) | "annual" or "quarterly". |
| `fiscal_date_ending` | date | End date of the fiscal period. |
| `reported_currency` | string | Currency of reported values. |
| `gross_profit` | long | Gross profit. |
| `total_revenue` | long | Total revenue. |
| `cost_of_revenue` | long | Cost of revenue. |
| `cost_of_goods_and_services_sold` | long | Cost of goods sold. |
| `operating_income` | long | Operating income. |
| `selling_general_and_administrative` | long | SG&A expenses. |
| `research_and_development` | long | R&D expenses. |
| `operating_expenses` | long | Total operating expenses. |
| `investment_income_net` | long | Net investment income. |
| `net_interest_income` | long | Net interest income. |
| `interest_income` | long | Interest income. |
| `interest_expense` | long | Interest expense. |
| `non_interest_income` | long | Non-interest income. |
| `other_non_operating_income` | long | Other non-operating income. |
| `depreciation` | long | Depreciation expense. |
| `depreciation_and_amortization` | long | D&A expense. |
| `income_before_tax` | long | Pre-tax income. |
| `income_tax_expense` | long | Income tax expense. |
| `interest_and_debt_expense` | long | Interest and debt expense. |
| `net_income_from_continuing_operations` | long | Net income from continuing operations. |
| `comprehensive_income_net_of_tax` | long | Comprehensive income. |
| `ebit` | long | EBIT. |
| `ebitda` | long | EBITDA. |
| `net_income` | long | Net income. |


### `balance_sheet` object

**Source endpoint**:
`GET /query?function=BALANCE_SHEET&symbol={symbol}&apikey={key}`

**High-level schema (connector view)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `symbol` | string (connector-derived) | Stock symbol. |
| `report_type` | string (connector-derived) | "annual" or "quarterly". |
| `fiscal_date_ending` | date | End date of the fiscal period. |
| `reported_currency` | string | Currency of reported values. |
| `total_assets` | long | Total assets. |
| `total_current_assets` | long | Total current assets. |
| `cash_and_cash_equivalents_at_carrying_value` | long | Cash and equivalents. |
| `cash_and_short_term_investments` | long | Cash and short-term investments. |
| `inventory` | long | Inventory value. |
| `current_net_receivables` | long | Current net receivables. |
| `total_non_current_assets` | long | Total non-current assets. |
| `property_plant_equipment` | long | PP&E value. |
| `accumulated_depreciation_amortization_ppe` | long | Accumulated depreciation. |
| `intangible_assets` | long | Intangible assets. |
| `intangible_assets_excluding_goodwill` | long | Intangibles excluding goodwill. |
| `goodwill` | long | Goodwill. |
| `investments` | long | Total investments. |
| `long_term_investments` | long | Long-term investments. |
| `short_term_investments` | long | Short-term investments. |
| `other_current_assets` | long | Other current assets. |
| `other_non_current_assets` | long | Other non-current assets. |
| `total_liabilities` | long | Total liabilities. |
| `total_current_liabilities` | long | Total current liabilities. |
| `current_accounts_payable` | long | Accounts payable (current). |
| `deferred_revenue` | long | Deferred revenue. |
| `current_debt` | long | Current portion of debt. |
| `short_term_debt` | long | Short-term debt. |
| `total_non_current_liabilities` | long | Total non-current liabilities. |
| `capital_lease_obligations` | long | Capital lease obligations. |
| `long_term_debt` | long | Long-term debt. |
| `current_long_term_debt` | long | Current portion of long-term debt. |
| `long_term_debt_noncurrent` | long | Non-current long-term debt. |
| `short_long_term_debt_total` | long | Total debt. |
| `other_current_liabilities` | long | Other current liabilities. |
| `other_non_current_liabilities` | long | Other non-current liabilities. |
| `total_shareholder_equity` | long | Total shareholder equity. |
| `treasury_stock` | long | Treasury stock. |
| `retained_earnings` | long | Retained earnings. |
| `common_stock` | long | Common stock. |
| `common_stock_shares_outstanding` | long | Shares outstanding. |


### `cash_flow` object

**Source endpoint**:
`GET /query?function=CASH_FLOW&symbol={symbol}&apikey={key}`

**High-level schema (connector view)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `symbol` | string (connector-derived) | Stock symbol. |
| `report_type` | string (connector-derived) | "annual" or "quarterly". |
| `fiscal_date_ending` | date | End date of the fiscal period. |
| `reported_currency` | string | Currency of reported values. |
| `operating_cashflow` | long | Operating cash flow. |
| `payments_for_operating_activities` | long | Payments for operations. |
| `proceeds_from_operating_activities` | long | Proceeds from operations. |
| `change_in_operating_liabilities` | long | Change in operating liabilities. |
| `change_in_operating_assets` | long | Change in operating assets. |
| `depreciation_depletion_and_amortization` | long | DD&A. |
| `capital_expenditures` | long | CapEx. |
| `change_in_receivables` | long | Change in receivables. |
| `change_in_inventory` | long | Change in inventory. |
| `profit_loss` | long | Profit or loss. |
| `cashflow_from_investment` | long | Cash flow from investing. |
| `cashflow_from_financing` | long | Cash flow from financing. |
| `proceeds_from_repayments_of_short_term_debt` | long | Proceeds/repayments from short-term debt. |
| `payments_for_repurchase_of_common_stock` | long | Buyback payments. |
| `payments_for_repurchase_of_equity` | long | Equity repurchase payments. |
| `payments_for_repurchase_of_preferred_stock` | long | Preferred stock repurchase. |
| `dividend_payout` | long | Dividend payments. |
| `dividend_payout_common_stock` | long | Common stock dividends. |
| `dividend_payout_preferred_stock` | long | Preferred stock dividends. |
| `proceeds_from_issuance_of_common_stock` | long | Common stock issuance proceeds. |
| `proceeds_from_issuance_of_long_term_debt_and_capital_securities_net` | long | Long-term debt issuance. |
| `proceeds_from_issuance_of_preferred_stock` | long | Preferred stock issuance. |
| `proceeds_from_repurchase_of_equity` | long | Equity repurchase proceeds. |
| `proceeds_from_sale_of_treasury_stock` | long | Treasury stock sale proceeds. |
| `change_in_cash_and_cash_equivalents` | long | Change in cash. |
| `change_in_exchange_rate` | long | FX impact on cash. |
| `net_income` | long | Net income. |


### `earnings` object

**Source endpoint**:
`GET /query?function=EARNINGS&symbol={symbol}&apikey={key}`

**Response structure**:
```json
{
    "symbol": "IBM",
    "annualEarnings": [
        {
            "fiscalDateEnding": "2023-12-31",
            "reportedEPS": "9.62"
        }
    ],
    "quarterlyEarnings": [
        {
            "fiscalDateEnding": "2023-12-31",
            "reportedDate": "2024-01-24",
            "reportedEPS": "3.87",
            "estimatedEPS": "3.78",
            "surprise": "0.09",
            "surprisePercentage": "2.381"
        }
    ]
}
```

**High-level schema for quarterly earnings (connector view)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `symbol` | string (connector-derived) | Stock symbol. |
| `report_type` | string (connector-derived) | "annual" or "quarterly". |
| `fiscal_date_ending` | date | End of fiscal period. |
| `reported_date` | date | Date earnings were reported (quarterly only). |
| `reported_eps` | decimal | Reported EPS. |
| `estimated_eps` | decimal | Analyst estimated EPS (quarterly only). |
| `surprise` | decimal | EPS surprise amount (quarterly only). |
| `surprise_percentage` | decimal | EPS surprise percentage (quarterly only). |


### `fx_daily` object

**Source endpoint**:
`GET /query?function=FX_DAILY&from_symbol={from}&to_symbol={to}&outputsize={outputsize}&apikey={key}`

**High-level schema (connector view - flattened)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `from_symbol` | string (connector-derived) | Base currency. |
| `to_symbol` | string (connector-derived) | Quote currency. |
| `date` | date | Trading date. |
| `open` | decimal | Opening exchange rate. |
| `high` | decimal | Day's high rate. |
| `low` | decimal | Day's low rate. |
| `close` | decimal | Closing exchange rate. |


### `digital_currency_daily` object

**Source endpoint**:
`GET /query?function=DIGITAL_CURRENCY_DAILY&symbol={symbol}&market={market}&apikey={key}`

**High-level schema (connector view - flattened)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `symbol` | string (connector-derived) | Cryptocurrency symbol (e.g., BTC). |
| `market` | string (connector-derived) | Market currency (e.g., USD). |
| `date` | date | Trading date. |
| `open` | decimal | Opening price in market currency. |
| `high` | decimal | Day's high price. |
| `low` | decimal | Day's low price. |
| `close` | decimal | Closing price. |
| `volume` | decimal | Trading volume. |
| `market_cap` | decimal | Market capitalization. |


### Commodity objects (`wti`, `brent`, `natural_gas`, etc.)

**Source endpoint** (example for WTI):
`GET /query?function=WTI&interval={interval}&apikey={key}`

**Parameters**:
- `interval` (optional): "daily", "weekly", or "monthly". Default: "monthly"

**Response structure**:
```json
{
    "name": "Crude Oil Prices WTI",
    "interval": "monthly",
    "unit": "dollars per barrel",
    "data": [
        {"date": "2024-01-01", "value": "75.50"},
        {"date": "2023-12-01", "value": "72.30"}
    ]
}
```

**High-level schema (connector view)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `commodity` | string (connector-derived) | Commodity name (e.g., "WTI", "BRENT"). |
| `date` | date | Data point date. |
| `value` | decimal | Price value. |
| `unit` | string | Unit of measurement (from response). |
| `interval` | string (connector-derived) | Data interval. |


### Economic indicator objects (`real_gdp`, `cpi`, `unemployment`, etc.)

**Source endpoint** (example for REAL_GDP):
`GET /query?function=REAL_GDP&interval={interval}&apikey={key}`

**Parameters**:
- `interval` (optional): "annual" or "quarterly". Default: "annual"

**Response structure**:
```json
{
    "name": "Real Gross Domestic Product",
    "interval": "quarterly",
    "unit": "billions of dollars",
    "data": [
        {"date": "2024-01-01", "value": "22225.350"},
        {"date": "2023-10-01", "value": "22031.900"}
    ]
}
```

**High-level schema (connector view)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `indicator` | string (connector-derived) | Indicator name (e.g., "real_gdp", "cpi"). |
| `date` | date | Data point date. |
| `value` | decimal | Indicator value. |
| `unit` | string | Unit of measurement (from response). |
| `interval` | string (connector-derived) | Data interval. |


### Technical indicator objects (`sma`, `ema`, `rsi`, `macd`, etc.)

**Source endpoint** (example for SMA):
`GET /query?function=SMA&symbol={symbol}&interval={interval}&time_period={period}&series_type={type}&apikey={key}`

**Parameters**:
- `symbol` (required): Stock symbol
- `interval` (required): "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
- `time_period` (required): Number of data points (e.g., 14, 50, 200)
- `series_type` (required): "close", "open", "high", or "low"

**Response structure** (SMA example):
```json
{
    "Meta Data": {
        "1: Symbol": "IBM",
        "2: Indicator": "Simple Moving Average (SMA)",
        "3: Last Refreshed": "2024-01-15",
        "4: Interval": "daily",
        "5: Time Period": 14,
        "6: Series Type": "close",
        "7: Time Zone": "US/Eastern"
    },
    "Technical Analysis: SMA": {
        "2024-01-15": {"SMA": "185.2500"},
        "2024-01-14": {"SMA": "184.8000"}
    }
}
```

**High-level schema for SMA (connector view)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `symbol` | string (connector-derived) | Stock symbol. |
| `date` | date/timestamp | Data point date/time. |
| `indicator` | string (connector-derived) | Indicator name (e.g., "SMA"). |
| `interval` | string (connector-derived) | Data interval. |
| `time_period` | integer (connector-derived) | Number of periods. |
| `series_type` | string (connector-derived) | Price type used. |
| `value` | decimal | Indicator value. |

**High-level schema for MACD (connector view)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `symbol` | string (connector-derived) | Stock symbol. |
| `date` | date/timestamp | Data point date/time. |
| `interval` | string (connector-derived) | Data interval. |
| `macd` | decimal | MACD line value. |
| `macd_signal` | decimal | Signal line value. |
| `macd_hist` | decimal | MACD histogram value. |


### `symbol_search` object

**Source endpoint**:
`GET /query?function=SYMBOL_SEARCH&keywords={keywords}&apikey={key}`

**Parameters**:
- `keywords` (required): Search keywords (e.g., "microsoft", "AAPL")

**Response structure**:
```json
{
    "bestMatches": [
        {
            "1. symbol": "MSFT",
            "2. name": "Microsoft Corporation",
            "3. type": "Equity",
            "4. region": "United States",
            "5. marketOpen": "09:30",
            "6. marketClose": "16:00",
            "7. timezone": "UTC-04",
            "8. currency": "USD",
            "9. matchScore": "1.0000"
        }
    ]
}
```

**High-level schema (connector view)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `symbol` | string | Stock ticker symbol. |
| `name` | string | Company/security name. |
| `type` | string | Security type (Equity, ETF, etc.). |
| `region` | string | Geographic region. |
| `market_open` | string | Market opening time. |
| `market_close` | string | Market closing time. |
| `timezone` | string | Market timezone. |
| `currency` | string | Trading currency. |
| `match_score` | decimal | Search relevance score (0.0 to 1.0). |


### `market_status` object

**Source endpoint**:
`GET /query?function=MARKET_STATUS&apikey={key}`

**Response structure**:
```json
{
    "endpoint": "Global Market Open & Close Status",
    "markets": [
        {
            "market_type": "Equity",
            "region": "United States",
            "primary_exchanges": "NYSE, NASDAQ, NYSE American, ...",
            "local_open": "09:30",
            "local_close": "16:00",
            "current_status": "closed",
            "notes": ""
        }
    ]
}
```

**High-level schema (connector view)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `market_type` | string | Type of market (Equity, Forex, Crypto). |
| `region` | string | Geographic region. |
| `primary_exchanges` | string | List of primary exchanges. |
| `local_open` | string | Local market open time. |
| `local_close` | string | Local market close time. |
| `current_status` | string | Current status (open/closed). |
| `notes` | string | Additional notes. |


### `etf_profile` object

**Source endpoint**:
`GET /query?function=ETF_PROFILE&symbol={symbol}&apikey={key}`

**High-level schema (connector view)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `symbol` | string | ETF ticker symbol. |
| `name` | string | ETF name. |
| `asset_type` | string | Asset type (ETF). |
| `description` | string | ETF description. |
| `inception_date` | date | ETF inception date. |
| `expense_ratio` | decimal | Annual expense ratio. |
| `net_assets` | long | Net assets under management. |
| `nav` | decimal | Net asset value. |
| `total_holdings` | integer | Number of holdings. |
| `sector_breakdown` | struct | Sector allocation breakdown. |
| `top_holdings` | array<struct> | Top holdings list. |


### `listing_status` object

**Source endpoint**:
`GET /query?function=LISTING_STATUS&apikey={key}`

**Parameters**:
- `date` (optional): Specific date for historical data (YYYY-MM-DD)
- `state` (optional): "active" or "delisted" (default: "active")

**High-level schema (connector view)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `symbol` | string | Stock ticker symbol. |
| `name` | string | Company name. |
| `exchange` | string | Stock exchange. |
| `asset_type` | string | Asset type (Stock, ETF). |
| `ipo_date` | date | IPO date. |
| `delisting_date` | date or null | Delisting date (if delisted). |
| `status` | string | Listing status (active/delisted). |


### `earnings_calendar` object

**Source endpoint**:
`GET /query?function=EARNINGS_CALENDAR&apikey={key}`

**Parameters**:
- `symbol` (optional): Filter to specific symbol
- `horizon` (optional): "3month", "6month", or "12month"

**High-level schema (connector view)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `symbol` | string | Stock ticker symbol. |
| `name` | string | Company name. |
| `report_date` | date | Expected earnings report date. |
| `fiscal_date_ending` | date | Fiscal period end date. |
| `estimate` | decimal | Consensus EPS estimate. |
| `currency` | string | Reporting currency. |


### `ipo_calendar` object

**Source endpoint**:
`GET /query?function=IPO_CALENDAR&apikey={key}`

**High-level schema (connector view)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `symbol` | string | Stock ticker symbol. |
| `name` | string | Company name. |
| `ipo_date` | date | IPO date. |
| `price_range_low` | decimal | Low end of IPO price range. |
| `price_range_high` | decimal | High end of IPO price range. |
| `currency` | string | Pricing currency. |
| `exchange` | string | Target exchange. |


### `insider_transactions` object

**Source endpoint**:
`GET /query?function=INSIDER_TRANSACTIONS&symbol={symbol}&apikey={key}`

**High-level schema (connector view)**:

| Column Name | Type | Description |
|-------------|------|-------------|
| `symbol` | string | Stock ticker symbol. |
| `transaction_date` | date | Transaction date. |
| `owner_name` | string | Name of the insider. |
| `owner_title` | string | Insider's title/role. |
| `transaction_type` | string | Buy/Sell/Exercise. |
| `shares` | long | Number of shares. |
| `value` | decimal | Transaction value. |
| `shares_owned` | long | Total shares owned after transaction. |


## **Get Object Primary Keys**

There is no dedicated metadata endpoint to get primary keys for Alpha Vantage objects.
Instead, primary keys are defined **statically** based on the resource schema and connector design.

### Primary keys by object type:

| Object | Primary Key(s) | Type | Notes |
|--------|---------------|------|-------|
| `time_series_daily` | `symbol`, `date` | string, date | Composite key: symbol + trading date. |
| `time_series_daily_adjusted` | `symbol`, `date` | string, date | Composite key. |
| `time_series_intraday` | `symbol`, `timestamp`, `interval` | string, timestamp, string | Composite key includes interval. |
| `time_series_weekly` | `symbol`, `date` | string, date | Composite key. |
| `time_series_monthly` | `symbol`, `date` | string, date | Composite key. |
| `global_quote` | `symbol` | string | Single key; one record per symbol. |
| `symbol_search` | `symbol` | string | Symbol is unique per search result. |
| `market_status` | `market_type`, `region` | string, string | Composite key. |
| `company_overview` | `symbol` | string | Single key; one record per symbol. |
| `etf_profile` | `symbol` | string | Single key; one record per ETF. |
| `income_statement` | `symbol`, `report_type`, `fiscal_date_ending` | string, string, date | Composite key. |
| `balance_sheet` | `symbol`, `report_type`, `fiscal_date_ending` | string, string, date | Composite key. |
| `cash_flow` | `symbol`, `report_type`, `fiscal_date_ending` | string, string, date | Composite key. |
| `earnings` | `symbol`, `report_type`, `fiscal_date_ending` | string, string, date | Composite key. |
| `earnings_calendar` | `symbol`, `report_date` | string, date | Composite key. |
| `ipo_calendar` | `symbol`, `ipo_date` | string, date | Composite key. |
| `listing_status` | `symbol` | string | Single key per listing. |
| `dividends` | `symbol`, `ex_dividend_date` | string, date | Composite key. |
| `splits` | `symbol`, `effective_date` | string, date | Composite key. |
| `fx_daily` | `from_symbol`, `to_symbol`, `date` | string, string, date | Composite key. |
| `digital_currency_daily` | `symbol`, `market`, `date` | string, string, date | Composite key. |
| `wti`, `brent`, etc. | `date`, `interval` | date, string | Composite key for commodities. |
| `all_commodities` | `date`, `interval` | date, string | Composite key. |
| `real_gdp`, `cpi`, etc. | `date`, `interval` | date, string | Composite key for economic indicators. |
| `sma`, `ema`, `rsi` | `symbol`, `date`, `interval`, `time_period`, `series_type` | composite | Full parameter set forms key. |
| `macd` | `symbol`, `date`, `interval`, `series_type` | composite | Full parameter set forms key. |
| `news_sentiment` | `title`, `time_published` | string, timestamp | Title + timestamp as deduplication key. |
| `top_gainers_losers` | `ticker`, `category` | string, string | Ticker + category (gainer/loser/active). |
| `insider_transactions` | `symbol`, `transaction_date`, `owner_name` | string, date, string | Composite key. |
| `analytics_fixed_window` | `symbol` | string | Per-symbol analytics. |
| `analytics_sliding_window` | `symbol`, `date` | string, date | Composite key with date. |

The connector will:
- Use these composite keys for upserts during ingestion.
- The `symbol` (or equivalent identifier) is always derived from the request parameters and included in the output.


## **Object's Ingestion Type**

Supported ingestion types (framework-level definitions):
- `cdc`: Change data capture; supports upserts and/or deletes incrementally.
- `snapshot`: Full replacement snapshot; no inherent incremental support.
- `append`: Incremental but append-only (no updates/deletes to historical data).

### Ingestion types for Alpha Vantage objects:

| Object | Ingestion Type | Rationale |
|--------|----------------|-----------|
| `time_series_daily` | `append` | Historical prices are immutable. New trading days are appended. Use `date` as cursor. |
| `time_series_daily_adjusted` | `append` | Same as daily, but adjusted values may be recalculated retroactively. Consider periodic full refresh. |
| `time_series_intraday` | `append` | Intraday data is append-only within the day. Use `timestamp` as cursor. |
| `time_series_weekly` | `append` | Weekly data is append-only. |
| `time_series_monthly` | `append` | Monthly data is append-only. |
| `global_quote` | `snapshot` | Returns only latest quote; replaced on each sync. |
| `symbol_search` | `snapshot` | Search results are point-in-time; no incremental. |
| `market_status` | `snapshot` | Real-time market status; no historical tracking. |
| `company_overview` | `snapshot` | Company fundamentals change periodically; full snapshot refresh. |
| `etf_profile` | `snapshot` | ETF data changes periodically; full snapshot refresh. |
| `income_statement` | `snapshot` | Financial statements are released quarterly; snapshot with upsert by fiscal date. |
| `balance_sheet` | `snapshot` | Same as income statement. |
| `cash_flow` | `snapshot` | Same as income statement. |
| `earnings` | `snapshot` | Earnings data is upserted as new quarters are reported. |
| `earnings_calendar` | `snapshot` | Forward-looking calendar; refreshed periodically. |
| `ipo_calendar` | `snapshot` | Forward-looking calendar; refreshed periodically. |
| `listing_status` | `snapshot` | Listing status is point-in-time; full refresh recommended. |
| `dividends` | `append` | Historical dividends are immutable; new ones appended. |
| `splits` | `append` | Historical splits are immutable; new ones appended. |
| `fx_daily` | `append` | FX rates are append-only by date. |
| `digital_currency_daily` | `append` | Crypto prices are append-only by date. |
| `wti`, `brent`, commodities | `append` | Commodity prices are append-only by date. |
| `all_commodities` | `append` | Commodities index is append-only by date. |
| `real_gdp`, economic indicators | `append` | Economic data is append-only; historical values rarely change. |
| `sma`, `ema`, technical indicators | `append` | Technical indicators are calculated per timestamp; append-only. |
| `news_sentiment` | `append` | News articles are append-only. |
| `top_gainers_losers` | `snapshot` | Point-in-time snapshot; changes daily. |
| `insider_transactions` | `append` | Transaction history is append-only. |
| `analytics_fixed_window` | `snapshot` | Analytics results are point-in-time. |
| `analytics_sliding_window` | `snapshot` | Analytics results are point-in-time. |

### Incremental strategy for time series objects:

- **Cursor field**: `date` (or `timestamp` for intraday)
- **Sort order**: Chronological (oldest to newest)
- **Lookback window**: None required for time series; data is immutable once published.
- **Deletes**: Alpha Vantage does not support deletes; all data is append-only or snapshot-replaced.

### Handling data corrections:

- Adjusted time series (`time_series_daily_adjusted`) may have retroactive adjustments for dividends and splits.
- Recommendation: Periodic full refresh (e.g., weekly) for adjusted data to capture any corrections.


## **Read API for Data Retrieval**

### General API Pattern

All Alpha Vantage APIs use the same base URL and query parameter structure:

- **HTTP method**: `GET`
- **Base URL**: `https://www.alphavantage.co/query`
- **Common parameters**:
  - `function` (required): API function name (e.g., `TIME_SERIES_DAILY`)
  - `apikey` (required): Your API key

### Pagination

**Alpha Vantage does NOT support pagination.** Each API call returns all available data for the requested parameters.

- For time series endpoints, use `outputsize=full` to get full historical data (20+ years for stocks).
- For intraday data, use the `month` parameter to filter to specific months.
- Rate limits are the primary constraint; connector must respect them.

### Rate Limits

| Tier | Requests per Minute | Requests per Day | Notes |
|------|---------------------|------------------|-------|
| Free | 5 | 25 | Suitable for development/testing only. |
| Premium (30) | 30 | Unlimited | Entry-level premium. |
| Premium (75) | 75 | Unlimited | Standard premium. |
| Premium (150) | 150 | Unlimited | Higher throughput. |
| Premium (300+) | 300-1200+ | Unlimited | Enterprise tiers. |

**Rate limit handling**:
- When rate limit is exceeded, API returns a `Note` field instead of data.
- Connector should implement exponential backoff with retry.
- Recommended: Track request timestamps and throttle proactively.

### Example API Requests

**Time Series Daily (full history)**:
```bash
curl -X GET \
  "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=IBM&outputsize=full&apikey=YOUR_API_KEY"
```

**Intraday with month filter**:
```bash
curl -X GET \
  "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&month=2024-01&apikey=YOUR_API_KEY"
```

**Company Overview**:
```bash
curl -X GET \
  "https://www.alphavantage.co/query?function=OVERVIEW&symbol=IBM&apikey=YOUR_API_KEY"
```

**Forex Daily**:
```bash
curl -X GET \
  "https://www.alphavantage.co/query?function=FX_DAILY&from_symbol=EUR&to_symbol=USD&outputsize=full&apikey=YOUR_API_KEY"
```

**Technical Indicator (RSI)**:
```bash
curl -X GET \
  "https://www.alphavantage.co/query?function=RSI&symbol=IBM&interval=daily&time_period=14&series_type=close&apikey=YOUR_API_KEY"
```

### Incremental Read Strategy

Since Alpha Vantage doesn't support server-side filtering by date (except `month` for intraday):

1. **Initial load**: Fetch full history with `outputsize=full`.
2. **Incremental reads**: Fetch with `outputsize=compact` (last 100 data points) and upsert.
3. **Deduplication**: Use composite primary key (symbol + date) to avoid duplicates.
4. **Optimization**: For intraday, iterate through months using the `month` parameter.

### Error Responses

**Rate Limit Exceeded**:
```json
{
    "Note": "Thank you for using Alpha Vantage! Our standard API rate limit is 25 requests per day. Please subscribe to any of the premium plans at https://www.alphavantage.co/premium/ if you would like to target a higher API call frequency."
}
```

**Invalid API Call**:
```json
{
    "Error Message": "Invalid API call. Please retry or visit the documentation (https://www.alphavantage.co/documentation/) for TIME_SERIES_DAILY."
}
```

**Invalid/Demo API Key**:
```json
{
    "Information": "The demo API key is for demo purposes only. Please claim your free API key at https://www.alphavantage.co/support/#api-key. It should take less than 20 seconds."
}
```

**No Data Available**:
```json
{}
```
(Empty JSON object indicates no data for the requested symbol/parameters)

### Connector Implementation Notes

1. **Retry logic**: Implement exponential backoff for rate limit errors (check for `Note` field).
2. **Empty responses**: Handle empty `{}` responses gracefully.
3. **Symbol validation**: Invalid symbols return empty responses, not errors.
4. **Date parsing**: Time series keys use ISO date format (YYYY-MM-DD); intraday uses datetime.
5. **Numeric parsing**: All numeric values are returned as strings; parse to appropriate types.


## **Field Type Mapping**

### General mapping (Alpha Vantage JSON → Connector logical types)

| Alpha Vantage JSON Type | Example Fields | Connector Logical Type | Notes |
|-------------------------|----------------|------------------------|-------|
| string (numeric) | "185.0000", "5234567" | `decimal` / `long` | Parse as decimal for prices, long for volumes. |
| string (date) | "2024-01-15" | `date` | ISO 8601 date format. |
| string (datetime) | "2024-01-15 16:00:00" | `timestamp` | US/Eastern timezone for stock data. |
| string (percentage) | "0.8152%" | `string` or `decimal` | Keep as string or strip % and parse as decimal. |
| string (text) | "Common Stock", "TECHNOLOGY" | `string` | UTF-8 text. |
| string (null marker) | "None", "-" | `null` | Convert to null. |
| object | Time series data, Meta Data | `struct` or flatten to rows | Connector flattens time series to rows. |

### Specific type mappings:

| Field Category | Fields | Target Type |
|----------------|--------|-------------|
| Prices | open, high, low, close, price | `decimal(18,4)` |
| Volume | volume | `long` |
| Financial values | revenue, income, assets | `long` |
| Ratios | pe_ratio, peg_ratio, beta | `decimal(18,6)` |
| Percentages | dividend_yield, change_percent | `decimal(10,6)` or `string` |
| Dates | date, fiscal_date_ending | `date` |
| Timestamps | timestamp (intraday) | `timestamp` |
| Identifiers | symbol, cik | `string` |
| Descriptions | name, description, sector | `string` |
| Counts | analyst_rating_buy, shares_outstanding | `long` |

### Special behaviors:

1. **String numerics**: All price/volume data comes as strings. Parse carefully.
2. **Null values**: "None", "-", "N/A", empty strings should be treated as null.
3. **Percentage fields**: Some fields include "%" suffix; strip before parsing.
4. **Time zones**: Stock market data is in US/Eastern; store as UTC or preserve timezone.
5. **Large numbers**: Market cap, revenue can exceed 32-bit integer range; use long.
6. **Precision**: Prices typically have 4 decimal places; ratios may have 6.


## **Write API**

Alpha Vantage is a **read-only data API**. There are no write endpoints available for creating, updating, or deleting any data.

The API is designed exclusively for:
- Retrieving market data (stocks, forex, crypto)
- Accessing fundamental data (financial statements, company info)
- Querying technical indicators
- Reading news and sentiment data

For workflows that require writing data back to a source system, Alpha Vantage is not applicable.


## **Known Quirks & Edge Cases**

1. **No pagination**: Alpha Vantage returns all data in a single response. For large historical datasets, this can be a large payload.

2. **Rate limiting**: The free tier is very restrictive (25/day, 5/min). Production use requires a premium subscription.

3. **String numerics**: All numeric values are returned as strings, requiring parsing.

4. **Inconsistent null representation**: Missing data may be represented as "None", "-", "N/A", empty string, or omitted entirely.

5. **Symbol case sensitivity**: Symbols should be uppercase (e.g., "IBM", not "ibm").

6. **Adjusted vs unadjusted data**: Daily adjusted data may be retroactively modified when splits/dividends occur.

7. **Intraday data availability**: Intraday data is only available for the trailing 30 days for free tier; extended history requires premium with `month` parameter.

8. **Weekend/holiday handling**: No data points for non-trading days; gaps in time series are expected.

9. **International markets**: Some international symbols require exchange suffix (e.g., "BMW.DEX" for German stocks).

10. **Crypto market hours**: Cryptocurrency data is 24/7; no trading day concept.

11. **Empty responses**: Invalid or delisted symbols return empty JSON `{}` instead of an error.

12. **Response structure varies**: Different endpoints use different key names and structures.

13. **Premium-only endpoints**: Some features (like extended intraday history, real-time data) require premium subscriptions.


## **Research Log**

| Source Type | URL | Accessed (UTC) | Confidence | What it confirmed |
|------------|-----|----------------|------------|-------------------|
| Official Docs | https://www.alphavantage.co/documentation/ | 2025-01-02 | Highest | Full API reference, all endpoints, parameters, response formats. Added 50+ technical indicators, symbol search, market status, ETF profile, earnings/IPO calendars, insider transactions. |
| Official Docs | https://www.alphavantage.co/support/ | 2025-01-02 | Highest | API key acquisition, support resources. |
| Official Docs | https://www.alphavantage.co/premium/ | 2025-01-02 | Highest | Premium tier pricing and rate limits. VWAP and Options APIs are premium-only. |
| Web Search | Alpha Vantage rate limits documentation | 2025-01-02 | High | Free tier: 25/day, 5/min. Premium tiers vary. |
| Existing Implementation | sources/alphavantage/alphavantage.py (local repo) | 2025-01-02 | High | Connector patterns, table definitions. |
| Existing Implementation | sources/github/github_api_doc.md (local repo) | 2025-01-02 | High | Reference for documentation structure and completeness. |


## **Sources and References**

- **Official Alpha Vantage API documentation** (highest confidence)
  - Main documentation: https://www.alphavantage.co/documentation/
  - API key support: https://www.alphavantage.co/support/
  - Premium plans: https://www.alphavantage.co/premium/

- **Key endpoints documented**:
  - Core Stock APIs: TIME_SERIES_INTRADAY, TIME_SERIES_DAILY, TIME_SERIES_DAILY_ADJUSTED, TIME_SERIES_WEEKLY, TIME_SERIES_WEEKLY_ADJUSTED, TIME_SERIES_MONTHLY, TIME_SERIES_MONTHLY_ADJUSTED, GLOBAL_QUOTE, SYMBOL_SEARCH, MARKET_STATUS
  - Fundamental Data: OVERVIEW, ETF_PROFILE, INCOME_STATEMENT, BALANCE_SHEET, CASH_FLOW, EARNINGS, EARNINGS_CALENDAR, IPO_CALENDAR, LISTING_STATUS, DIVIDENDS, SPLITS
  - Forex: CURRENCY_EXCHANGE_RATE, FX_DAILY, FX_WEEKLY, FX_MONTHLY
  - Cryptocurrency: DIGITAL_CURRENCY_DAILY, DIGITAL_CURRENCY_WEEKLY, DIGITAL_CURRENCY_MONTHLY
  - Commodities: WTI, BRENT, NATURAL_GAS, COPPER, ALUMINUM, WHEAT, CORN, COTTON, SUGAR, COFFEE, ALL_COMMODITIES
  - Economic Indicators: REAL_GDP, REAL_GDP_PER_CAPITA, TREASURY_YIELD, FEDERAL_FUNDS_RATE, CPI, INFLATION, RETAIL_SALES, DURABLES, UNEMPLOYMENT, NONFARM_PAYROLL
  - Technical Indicators (50+): SMA, EMA, WMA, DEMA, TEMA, TRIMA, KAMA, MAMA, VWAP, T3, MACD, MACDEXT, STOCH, STOCHF, RSI, STOCHRSI, WILLR, ADX, ADXR, APO, PPO, MOM, BOP, CCI, CMO, ROC, ROCR, AROON, AROONOSC, MFI, TRIX, ULTOSC, DX, MINUS_DI, PLUS_DI, MINUS_DM, PLUS_DM, BBANDS, MIDPOINT, MIDPRICE, SAR, TRANGE, ATR, NATR, AD, ADOSC, OBV, HT_TRENDLINE, HT_SINE, HT_TRENDMODE, HT_DCPERIOD, HT_DCPHASE, HT_PHASOR
  - Alpha Intelligence: NEWS_SENTIMENT, TOP_GAINERS_LOSERS, INSIDER_TRANSACTIONS, ANALYTICS_FIXED_WINDOW, ANALYTICS_SLIDING_WINDOW

- **Premium-only endpoints** (noted but not fully documented):
  - Options Data: REALTIME_OPTIONS, HISTORICAL_OPTIONS
  - VWAP (Technical Indicator)
  - CRYPTO_INTRADAY, FX_INTRADAY
  - Realtime Bulk Quotes

- **Existing connector implementation** (high confidence for patterns):
  - Local repository implementation for reference

When conflicts arise, **official Alpha Vantage documentation** is treated as the source of truth.

