# Lakeflow Alpha Vantage Community Connector

This documentation provides setup instructions and reference information for the Alpha Vantage source connector. The connector allows you to extract financial market data from the Alpha Vantage API and load it into your data lake or warehouse. It supports a wide range of financial data including stocks, forex, cryptocurrencies, commodities, economic indicators, technical analysis, and market intelligence.

## Key Features

- **103 supported tables** across stocks, forex, crypto, commodities, economic indicators, and technical analysis
- **Multi-symbol support** - Fetch data for multiple symbols in a single table configuration
- **Per-symbol error handling** - Failed symbols don't break the entire batch
- **Configurable rate limiting** - Supports free and premium API tiers
- **Incremental sync** - Cursor-based sync for time series data

## Prerequisites

- **Alpha Vantage account**: You need an Alpha Vantage account to obtain an API key.
- **API Key**:
  - Free tier: Obtain a free API key from [Alpha Vantage Support](https://www.alphavantage.co/support/#api-key).
  - Premium tier: For higher rate limits, subscribe at [Alpha Vantage Premium](https://www.alphavantage.co/premium/).
- **Network access**: The environment running the connector must be able to reach `https://www.alphavantage.co`.

## Setup

### Required Connection Parameters

To configure the connector, provide the following parameters in your connector options:

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `api_key` | string | Yes | Alpha Vantage API key for authentication | `ABCDEFGHIJ123456` |
| `externalOptionsAllowList` | string | Yes | Comma-separated list of table-specific options (see below) | `symbol,interval,outputsize,from_symbol,to_symbol,market,time_period,series_type,maturity,horizon,state,keywords,tickers,topics,time_from,time_to,limit,month` |

### Optional Connection Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `base_url` | string | No | Override base URL. Default: `https://www.alphavantage.co/query` | `https://www.alphavantage.co/query` |
| `tier` | string | No | Rate limit tier: `free`, `premium_30`, `premium_75`, `premium_150`, `premium_300`, `premium_600`, `premium_1200`. Default: `free` | `premium_75` |
| `requests_per_minute` | string | No | Override requests per minute (overrides tier setting) | `75` |
| `requests_per_day` | string | No | Override daily request limit. Set to very high number for unlimited | `10000` |

### Table-Specific Options (externalOptionsAllowList)

The following table-specific options must be included in the `externalOptionsAllowList` connection parameter:

```
symbol,interval,outputsize,from_symbol,to_symbol,market,time_period,series_type,maturity,horizon,state,keywords,tickers,topics,time_from,time_to,limit,month
```

### Rate Limits

Alpha Vantage enforces rate limits based on your subscription tier:

| Tier | Requests per Minute | Requests per Day |
|------|---------------------|------------------|
| Free | 5 | 25 |
| Premium (30) | 30 | Unlimited |
| Premium (75) | 75 | Unlimited |
| Premium (150) | 150 | Unlimited |
| Premium (300) | 300 | Unlimited |
| Premium (600) | 600 | Unlimited |
| Premium (1200) | 1200 | Unlimited |

### Getting Your Alpha Vantage API Key

1. Visit [Alpha Vantage Support](https://www.alphavantage.co/support/#api-key)
2. Enter your email address and click "GET FREE API KEY"
3. Copy the generated API key and store it securely
4. **Important**: Keep your API key secure - never share it publicly

For premium API keys with higher rate limits, visit [Alpha Vantage Premium](https://www.alphavantage.co/premium/).

### Using Databricks Secrets (Recommended)

For production deployments, store your API key in Databricks Secrets:

```bash
# Create a secret scope
databricks secrets create-scope --scope alpha_vantage_secrets

# Add your API key
databricks secrets put --scope alpha_vantage_secrets --key api_key
```

Then in your pipeline:
```python
API_KEY = dbutils.secrets.get("alpha_vantage_secrets", "api_key")
```

### Create a Unity Catalog Connection

A Unity Catalog connection for this connector can be created in two ways via the UI:

1. Follow the Lakeflow Community Connector UI flow from the "Add Data" page
2. Select any existing Lakeflow Community Connector connection for this source or create a new one
3. Set `externalOptionsAllowList` to: `symbol,interval,outputsize,from_symbol,to_symbol,market,time_period,series_type,maturity,horizon,state,keywords,tickers,topics,time_from,time_to,limit,month`

The connection can also be created using the standard Unity Catalog API.

## Supported Objects

The Alpha Vantage connector supports **103 tables** across multiple categories:

### Stock Time Series (7 tables)

| Table Name | Primary Key | Cursor Field | Ingestion Type |
|------------|-------------|--------------|----------------|
| `time_series_daily` | `symbol`, `date` | `date` | append |
| `time_series_daily_adjusted` | `symbol`, `date` | `date` | append |
| `time_series_intraday` | `symbol`, `timestamp`, `interval` | `timestamp` | append |
| `time_series_weekly` | `symbol`, `date` | `date` | append |
| `time_series_weekly_adjusted` | `symbol`, `date` | `date` | append |
| `time_series_monthly` | `symbol`, `date` | `date` | append |
| `time_series_monthly_adjusted` | `symbol`, `date` | `date` | append |

**Required Options**: `symbol`
**Optional Options**: `outputsize` (compact/full), `interval` (for intraday: 1min, 5min, 15min, 30min, 60min), `month` (for intraday)

### Quote and Search (3 tables)

| Table Name | Primary Key | Ingestion Type | Required Options |
|------------|-------------|----------------|------------------|
| `global_quote` | `symbol` | snapshot | `symbol` |
| `symbol_search` | `symbol` | snapshot | `keywords` |
| `market_status` | `market_type`, `region` | snapshot | (none) |

### Fundamental Data (11 tables)

| Table Name | Primary Key | Ingestion Type | Required Options |
|------------|-------------|----------------|------------------|
| `company_overview` | `symbol` | snapshot | `symbol` |
| `etf_profile` | `symbol` | snapshot | `symbol` |
| `income_statement` | `symbol`, `report_type`, `fiscal_date_ending` | snapshot | `symbol` |
| `balance_sheet` | `symbol`, `report_type`, `fiscal_date_ending` | snapshot | `symbol` |
| `cash_flow` | `symbol`, `report_type`, `fiscal_date_ending` | snapshot | `symbol` |
| `earnings` | `symbol`, `report_type`, `fiscal_date_ending` | snapshot | `symbol` |
| `listing_status` | `symbol` | snapshot | (none, optional: `state`) |
| `earnings_calendar` | `symbol`, `report_date` | snapshot | (none, optional: `symbol`, `horizon`) |
| `ipo_calendar` | `symbol`, `ipo_date` | snapshot | (none) |
| `dividends` | `symbol`, `ex_dividend_date` | append | `symbol` |
| `splits` | `symbol`, `effective_date` | append | `symbol` |

### Forex (3 tables)

| Table Name | Primary Key | Cursor Field | Ingestion Type |
|------------|-------------|--------------|----------------|
| `fx_daily` | `from_symbol`, `to_symbol`, `date` | `date` | append |
| `fx_weekly` | `from_symbol`, `to_symbol`, `date` | `date` | append |
| `fx_monthly` | `from_symbol`, `to_symbol`, `date` | `date` | append |

**Required Options**: `from_symbol`, `to_symbol`
**Optional Options**: `outputsize` (compact/full)

### Cryptocurrency (3 tables)

| Table Name | Primary Key | Cursor Field | Ingestion Type |
|------------|-------------|--------------|----------------|
| `digital_currency_daily` | `symbol`, `market`, `date` | `date` | append |
| `digital_currency_weekly` | `symbol`, `market`, `date` | `date` | append |
| `digital_currency_monthly` | `symbol`, `market`, `date` | `date` | append |

**Required Options**: `symbol`, `market`

### Commodities (11 tables)

| Table Name | Primary Key | Cursor Field | Ingestion Type |
|------------|-------------|--------------|----------------|
| `wti` | `date`, `interval` | `date` | append |
| `brent` | `date`, `interval` | `date` | append |
| `natural_gas` | `date`, `interval` | `date` | append |
| `copper` | `date`, `interval` | `date` | append |
| `aluminum` | `date`, `interval` | `date` | append |
| `wheat` | `date`, `interval` | `date` | append |
| `corn` | `date`, `interval` | `date` | append |
| `cotton` | `date`, `interval` | `date` | append |
| `sugar` | `date`, `interval` | `date` | append |
| `coffee` | `date`, `interval` | `date` | append |
| `all_commodities` | `date`, `interval` | `date` | append |

**Optional Options**: `interval` (daily, weekly, monthly - default: monthly)

### Economic Indicators (10 tables)

| Table Name | Primary Key | Cursor Field | Ingestion Type |
|------------|-------------|--------------|----------------|
| `real_gdp` | `date`, `interval` | `date` | append |
| `real_gdp_per_capita` | `date` | `date` | append |
| `cpi` | `date`, `interval` | `date` | append |
| `inflation` | `date` | `date` | append |
| `unemployment` | `date` | `date` | append |
| `treasury_yield` | `date`, `interval`, `maturity` | `date` | append |
| `federal_funds_rate` | `date`, `interval` | `date` | append |
| `retail_sales` | `date` | `date` | append |
| `durables` | `date` | `date` | append |
| `nonfarm_payroll` | `date` | `date` | append |

**Optional Options**: `interval` (annual, quarterly, monthly - varies by table), `maturity` (for treasury_yield: 3month, 2year, 5year, 10year, 30year)

### Technical Indicators (52 tables)

All technical indicators use `append` ingestion type.

#### Moving Averages & Smoothing

| Table Name | Primary Key | Description |
|------------|-------------|-------------|
| `sma` | `symbol`, `date`, `interval`, `time_period`, `series_type` | Simple Moving Average |
| `ema` | `symbol`, `date`, `interval`, `time_period`, `series_type` | Exponential Moving Average |
| `wma` | `symbol`, `date`, `interval`, `time_period`, `series_type` | Weighted Moving Average |
| `dema` | `symbol`, `date`, `interval`, `time_period`, `series_type` | Double EMA |
| `tema` | `symbol`, `date`, `interval`, `time_period`, `series_type` | Triple EMA |
| `trima` | `symbol`, `date`, `interval`, `time_period`, `series_type` | Triangular MA |
| `kama` | `symbol`, `date`, `interval`, `time_period`, `series_type` | Kaufman Adaptive MA |
| `t3` | `symbol`, `date`, `interval`, `time_period`, `series_type` | Triple Exponential MA (T3) |
| `mama` | `symbol`, `date`, `interval`, `series_type` | MESA Adaptive MA (returns MAMA + FAMA) |

**Required Options**: `symbol`, `interval`
**Optional Options**: `time_period` (varies), `series_type` (close, open, high, low)

#### Momentum Indicators

| Table Name | Primary Key | Description |
|------------|-------------|-------------|
| `rsi` | `symbol`, `date`, `interval`, `time_period`, `series_type` | Relative Strength Index |
| `macd` | `symbol`, `date`, `interval`, `series_type` | MACD (returns MACD, Signal, Histogram) |
| `macdext` | `symbol`, `date`, `interval`, `series_type` | MACD with controllable MA type |
| `stoch` | `symbol`, `date`, `interval` | Stochastic Oscillator (SlowK, SlowD) |
| `stochf` | `symbol`, `date`, `interval` | Stochastic Fast (FastK, FastD) |
| `stochrsi` | `symbol`, `date`, `interval`, `time_period`, `series_type` | Stochastic RSI |
| `willr` | `symbol`, `date`, `interval`, `time_period` | Williams %R |
| `mom` | `symbol`, `date`, `interval`, `time_period`, `series_type` | Momentum |
| `roc` | `symbol`, `date`, `interval`, `time_period`, `series_type` | Rate of Change |
| `rocr` | `symbol`, `date`, `interval`, `time_period`, `series_type` | Rate of Change Ratio |
| `cmo` | `symbol`, `date`, `interval`, `time_period`, `series_type` | Chande Momentum Oscillator |
| `ultosc` | `symbol`, `date`, `interval` | Ultimate Oscillator |
| `apo` | `symbol`, `date`, `interval`, `series_type` | Absolute Price Oscillator |
| `ppo` | `symbol`, `date`, `interval`, `series_type` | Percentage Price Oscillator |

#### Trend Indicators

| Table Name | Primary Key | Description |
|------------|-------------|-------------|
| `adx` | `symbol`, `date`, `interval`, `time_period` | Average Directional Index |
| `adxr` | `symbol`, `date`, `interval`, `time_period` | ADX Rating |
| `aroon` | `symbol`, `date`, `interval`, `time_period` | Aroon (Up + Down) |
| `aroonosc` | `symbol`, `date`, `interval`, `time_period` | Aroon Oscillator |
| `dx` | `symbol`, `date`, `interval`, `time_period` | Directional Movement Index |
| `minus_di` | `symbol`, `date`, `interval`, `time_period` | Minus Directional Indicator |
| `plus_di` | `symbol`, `date`, `interval`, `time_period` | Plus Directional Indicator |
| `minus_dm` | `symbol`, `date`, `interval`, `time_period` | Minus Directional Movement |
| `plus_dm` | `symbol`, `date`, `interval`, `time_period` | Plus Directional Movement |
| `sar` | `symbol`, `date`, `interval` | Parabolic SAR |

#### Volatility Indicators

| Table Name | Primary Key | Description |
|------------|-------------|-------------|
| `bbands` | `symbol`, `date`, `interval`, `time_period`, `series_type` | Bollinger Bands (Upper, Middle, Lower) |
| `atr` | `symbol`, `date`, `interval`, `time_period` | Average True Range |
| `natr` | `symbol`, `date`, `interval`, `time_period` | Normalized ATR |
| `trange` | `symbol`, `date`, `interval` | True Range |

#### Volume Indicators

| Table Name | Primary Key | Description |
|------------|-------------|-------------|
| `obv` | `symbol`, `date`, `interval` | On Balance Volume |
| `ad` | `symbol`, `date`, `interval` | Chaikin A/D Line |
| `adosc` | `symbol`, `date`, `interval` | Chaikin A/D Oscillator |
| `mfi` | `symbol`, `date`, `interval`, `time_period` | Money Flow Index |
| `bop` | `symbol`, `date`, `interval` | Balance of Power |

#### Other Indicators

| Table Name | Primary Key | Description |
|------------|-------------|-------------|
| `cci` | `symbol`, `date`, `interval`, `time_period` | Commodity Channel Index |
| `trix` | `symbol`, `date`, `interval`, `time_period`, `series_type` | 1-day ROC of Triple Smooth EMA |
| `midpoint` | `symbol`, `date`, `interval`, `time_period`, `series_type` | Midpoint over period |
| `midprice` | `symbol`, `date`, `interval`, `time_period` | Midpoint price over period |

#### Hilbert Transform

| Table Name | Primary Key | Description |
|------------|-------------|-------------|
| `ht_trendline` | `symbol`, `date`, `interval`, `series_type` | Instantaneous Trendline |
| `ht_sine` | `symbol`, `date`, `interval`, `series_type` | SineWave (SINE + LEAD SINE) |
| `ht_trendmode` | `symbol`, `date`, `interval`, `series_type` | Trend vs Cycle Mode |
| `ht_dcperiod` | `symbol`, `date`, `interval`, `series_type` | Dominant Cycle Period |
| `ht_dcphase` | `symbol`, `date`, `interval`, `series_type` | Dominant Cycle Phase |
| `ht_phasor` | `symbol`, `date`, `interval`, `series_type` | Phasor Components (PHASE + QUADRATURE) |

### Alpha Intelligence (3 tables)

| Table Name | Primary Key | Cursor Field | Ingestion Type | Required Options |
|------------|-------------|--------------|----------------|------------------|
| `news_sentiment` | `title`, `time_published` | `time_published` | append | (none, optional: tickers, topics, time_from, time_to, limit) |
| `top_gainers_losers` | `ticker`, `category` | - | snapshot | (none) |
| `insider_transactions` | `symbol`, `transaction_date`, `owner_name` | `transaction_date` | append | `symbol` |

> **Note**: Table names are case-sensitive. Use the exact names shown above (lowercase with underscores).

## Data Type Mapping

| Alpha Vantage Type | Spark Type | Notes |
|-------------------|------------|-------|
| String ID | StringType | Ticker symbols like `IBM` |
| String (numeric) | StringType | Prices, volumes - preserved as strings for precision |
| String (date) | StringType | ISO 8601 format (YYYY-MM-DD) |
| String (datetime) | StringType | ISO 8601 datetime format |
| String (text) | StringType | Names, descriptions, sectors |
| Null values | None | Empty strings, "None", "." converted to null |

> **Note**: All numeric values are stored as StringType to preserve precision. Cast to appropriate numeric types in downstream transformations.

## Multi-Symbol Support

The connector supports fetching data for **multiple symbols in a single table configuration** using comma-separated values. This allows you to load data for many stocks into ONE destination table, reducing the number of tables and simplifying your data model.

### How It Works

Instead of creating separate table configurations for each symbol:

```python
# OLD WAY - One table per symbol (creates many tables)
{"source_table": "time_series_daily", "symbol": "MSFT", ...}
{"source_table": "time_series_daily", "symbol": "AAPL", ...}
{"source_table": "time_series_daily", "symbol": "AMZN", ...}
```

Use comma-separated symbols:

```python
# NEW WAY - Multi-symbol (creates ONE table with all data)
{
    "source_table": "time_series_daily",
    "symbol": "MSFT,AAPL,AMZN,ORCL,SNOW",  # Comma-separated
    "destination_table": "time_series_daily",  # Single table
    ...
}
```

### Supported Tables

Multi-symbol support is available for all tables that accept a `symbol` parameter:

- **Stock Time Series**: `time_series_daily`, `time_series_weekly`, `time_series_monthly`, etc.
- **Fundamental Data**: `company_overview`, `earnings`, `income_statement`, `balance_sheet`, `cash_flow`, `dividends`, `splits`
- **Technical Indicators**: `sma`, `ema`, `rsi`, `macd`, `bbands`, `stoch`, and all other indicators
- **Other**: `global_quote`, `etf_profile`, `insider_transactions`

### Per-Symbol Error Handling

When using multi-symbol mode, if one symbol fails (e.g., invalid ticker, rate limit for that request), the connector:

1. **Logs a warning** with the error details
2. **Continues processing** the remaining symbols
3. **Returns data** for all successful symbols

This ensures that one bad symbol doesn't break your entire pipeline.

### Example: Multi-Symbol Pipeline

```python
# Symbols to ingest - comma-separated string
SYMBOLS = "MSFT,ORCL,AAPL,AMZN,SNOW"

pipeline_spec = {
    "connection_name": "alphavantage_connection",
    "objects": [
        # All 5 stocks loaded into ONE table
        {
            "table": {
                "source_table": "time_series_daily",
                "destination_catalog": "my_catalog",
                "destination_schema": "bronze",
                "destination_table": "stock_prices_daily",  # Single table
                "table_configuration": {
                    "api_key": API_KEY,
                    "symbol": SYMBOLS,  # Multi-symbol
                    "outputsize": "compact",
                },
            }
        },
        # SMA for all 5 stocks in ONE table
        {
            "table": {
                "source_table": "sma",
                "destination_catalog": "my_catalog",
                "destination_schema": "bronze",
                "destination_table": "technical_sma",  # Single table
                "table_configuration": {
                    "api_key": API_KEY,
                    "symbol": SYMBOLS,  # Multi-symbol
                    "interval": "daily",
                    "time_period": "50",
                    "series_type": "close",
                },
            }
        },
    ],
}
```

### Rate Limit Considerations for Multi-Symbol

When using multi-symbol mode, the connector makes **one API call per symbol**. For example:
- `symbol="MSFT,AAPL,AMZN"` makes **3 API calls**
- With free tier (5 req/min), this uses 3 of your 5 requests

**Recommendations:**
- Use a **premium tier** for multi-symbol with many stocks
- Set appropriate `tier` option (e.g., `"premium_75"`) to match your subscription
- The connector automatically handles rate limiting between calls

## How to Run

### Step 1: Clone/Copy the Source Connector Code

Follow the Lakeflow Community Connector UI, which will guide you through setting up a pipeline using the selected source connector code.

### Step 2: Configure Your Pipeline

1. Update the `pipeline_spec` in the main pipeline file (e.g., `ingest.py`).
2. Configure each table with its required options.

#### Single Symbol Example

```python
{
    "table": {
        "source_table": "time_series_daily",
        "destination_table": "time_series_daily_ibm",
        "table_configuration": {
            "api_key": API_KEY,
            "symbol": "IBM",
            "outputsize": "compact"
        }
    }
}
```

#### Multi-Symbol Example (Recommended)

```python
# Define symbols once, use everywhere
SYMBOLS = "MSFT,ORCL,AAPL,AMZN,SNOW"

pipeline_spec = {
    "connection_name": "my_alphavantage_connection",
    "objects": [
        # Stock prices for all symbols in ONE table
        {
            "table": {
                "source_table": "time_series_daily",
                "destination_catalog": "my_catalog",
                "destination_schema": "bronze",
                "destination_table": "stock_prices",
                "table_configuration": {
                    "api_key": API_KEY,
                    "tier": "premium_30",
                    "symbol": SYMBOLS,  # Multi-symbol!
                    "outputsize": "compact"
                }
            }
        },
        # Company fundamentals for all symbols in ONE table
        {
            "table": {
                "source_table": "company_overview",
                "destination_catalog": "my_catalog",
                "destination_schema": "bronze",
                "destination_table": "company_fundamentals",
                "table_configuration": {
                    "api_key": API_KEY,
                    "tier": "premium_30",
                    "symbol": SYMBOLS  # Multi-symbol!
                }
            }
        },
        # Technical indicator (SMA) for all symbols in ONE table
        {
            "table": {
                "source_table": "sma",
                "destination_catalog": "my_catalog",
                "destination_schema": "bronze",
                "destination_table": "technical_sma",
                "table_configuration": {
                    "api_key": API_KEY,
                    "tier": "premium_30",
                    "symbol": SYMBOLS,  # Multi-symbol!
                    "interval": "daily",
                    "time_period": "50",
                    "series_type": "close"
                }
            }
        },
        # Forex (no multi-symbol support for from_symbol/to_symbol)
        {
            "table": {
                "source_table": "fx_daily",
                "destination_catalog": "my_catalog",
                "destination_schema": "bronze",
                "destination_table": "forex_eur_usd",
                "table_configuration": {
                    "api_key": API_KEY,
                    "from_symbol": "EUR",
                    "to_symbol": "USD",
                    "outputsize": "compact"
                }
            }
        },
        # Economic indicator (no symbol required)
        {
            "table": {
                "source_table": "real_gdp",
                "destination_catalog": "my_catalog",
                "destination_schema": "bronze",
                "destination_table": "economic_gdp",
                "table_configuration": {
                    "api_key": API_KEY,
                    "interval": "quarterly"
                }
            }
        }
    ]
}
```

3. (Optional) Customize the source connector code if needed for special use cases.

### Step 3: Run and Schedule the Pipeline

#### Best Practices

- **Use Multi-Symbol Mode**: Combine multiple symbols into ONE table per source type (e.g., one `stock_prices` table for all stocks)
- **Start Small**: Begin by syncing a subset of symbols/tables to test your pipeline
- **Use Incremental Sync**: Leverage cursor-based sync for append tables (stock prices, forex, crypto)
- **Set Appropriate Schedules**: Balance data freshness requirements with API rate limits
- **Respect Rate Limits**: Alpha Vantage enforces strict rate limits - adjust your tier accordingly
- **Use `outputsize=compact`**: Reduces data from 20+ years to 100 most recent points
- **Use Premium Tier for Multi-Symbol**: With many symbols, use `tier="premium_30"` or higher
- **Store API Keys Securely**: Use Databricks Secrets instead of hardcoding keys

#### Rate Limit Considerations

- **Free tier**: 5 requests/minute, 25 requests/day - suitable for testing only
- **Premium 30**: 30 requests/minute - recommended for small production workloads
- **Premium 75+**: Recommended for multiple symbols or frequent updates

#### Troubleshooting

**Common Issues:**

1. **Rate Limit Exceeded** (`"Note"` in response):
   - You've hit the API rate limit
   - Wait before retrying or upgrade to premium tier
   - The connector will raise a RuntimeError with the rate limit message

2. **Invalid API Key** (`"Information"` mentioning demo key):
   - Verify your API key is correct
   - Ensure it's not the demo key (`demo`)
   - Check connection configuration

3. **Empty Data Returned**:
   - Verify the symbol is valid and actively traded
   - Some symbols may not have data for all time periods
   - International symbols may need exchange suffix (e.g., `BMW.DEX`)
   - `ipo_calendar` may return empty when no IPOs are scheduled

4. **Missing Required Options**:
   - Each table has specific required options (e.g., `symbol` for stock data)
   - Check the "Supported Objects" section for required options per table
   - Ensure options are included in `externalOptionsAllowList`

## References

- [Alpha Vantage Documentation](https://www.alphavantage.co/documentation/)
- [API Key Support](https://www.alphavantage.co/support/)
- [Premium Plans](https://www.alphavantage.co/premium/)
- [Stock Market Data API](https://www.alphavantage.co/documentation/#time-series-data)
- [Technical Indicators API](https://www.alphavantage.co/documentation/#technical-indicators)
- [Forex & Crypto API](https://www.alphavantage.co/documentation/#fx)
- [Economic Indicators API](https://www.alphavantage.co/documentation/#economic-indicators)
