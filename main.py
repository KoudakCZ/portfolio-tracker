import pandas as pd
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import json
from zoneinfo import ZoneInfo

st.set_page_config(page_title="Portfolio Tracker", layout="wide")

CSV_PATH = "data/portfolio.csv"
WATCHLIST_PATH = "data/watchlist.csv"
ANALYSIS_PATH = "data/analysis.csv"
ANALYSIS_HISTORY_PATH = "data/analysis_history.csv"
LONG_TERM_PLANS_PATH = "data/long_term_plans.csv"
LONG_TERM_CHECKS_PATH = "data/long_term_checks.csv"
TRANSACTIONS_PATH = "data/transactions.csv"
EARNINGS_PATH = "data/earnings_calendar.csv"
SETTINGS_PATH = "settings.json"
HISTORY_PERIODS = {"1 mesic": "1mo", "3 mesice": "3mo", "1 rok": "1y"}
BENCHMARKS = {"SPY": "SPY", "MSCI World ETF": "URTH", "Nasdaq 100": "QQQ"}
DATE_FORMATS = {
    "DD.MM.YYYY": "%d.%m.%Y",
    "YYYY-MM-DD": "%Y-%m-%d",
    "MM/DD/YYYY": "%m/%d/%Y",
}
DEFAULT_VISIBLE_COLUMNS = [
    "Ticker",
    "Spolecnost",
    "Aktualni hodnota",
    "Denni pohyb %",
    "Denni pohyb",
    "Pocet",
    "Nakupni cena",
    "1 Year",
    "Current Value",
    "Kapitalovy zisk",
    "% Zisk",
    "PE",
    "EPS",
    "Earnings Yield",
    "Market Cap",
    "Beta",
]
DEFAULT_FX_PAIRS = ["CZK/USD", "CZK/EUR"]
FX_PAIR_CONFIG = {
    "CZK/USD": {"ticker": "USDCZK=X", "suffix": "Kc"},
    "CZK/EUR": {"ticker": "EURCZK=X", "suffix": "Kc"},
    "CZK/GBP": {"ticker": "GBPCZK=X", "suffix": "Kc"},
    "CZK/CHF": {"ticker": "CHFCZK=X", "suffix": "Kc"},
    "USD/EUR": {"ticker": "EURUSD=X", "suffix": ""},
    "EUR/USD": {"ticker": "EURUSD=X", "suffix": ""},
    "GBP/USD": {"ticker": "GBPUSD=X", "suffix": ""},
    "USD/JPY": {"ticker": "JPY=X", "suffix": ""},
    "EUR/GBP": {"ticker": "EURGBP=X", "suffix": ""},
    "EUR/CHF": {"ticker": "EURCHF=X", "suffix": ""},
    "GBP/CHF": {"ticker": "GBPCHF=X", "suffix": ""},
}
DEFAULT_SETTINGS = {
    "language": "cs",
    "base_currency": "USD",
    "date_format": "DD.MM.YYYY",
    "visible_columns": DEFAULT_VISIBLE_COLUMNS,
    "fx_pairs": DEFAULT_FX_PAIRS,
    "show_fx_rates": True,
    "theme": "dark",
}
TEXTS = {
    "cs": {
        "app_title": "Portfolio Tracker",
        "settings": "Nastaveni",
        "portfolio_management": "Sprava portfolia",
        "watchlist": "Watchlist",
        "watchlist_overview": "Prehled watchlistu",
        "analysis": "Plan portfolia",
        "long_term_plan": "Dlouhodoby plan",
        "reports": "Reporty",
        "transactions": "Transakce",
        "earnings": "Vysledky",
        "analysis_overview": "Detail akcie a plan",
        "analysis_update": "Upravit plan",
        "analysis_decision": "Nove rozhodnuti",
        "add": "Pridat",
        "edit": "Upravit",
        "delete": "Smazat",
        "language": "Jazyk aplikace",
        "base_currency": "Zakladni mena portfolia",
        "date_format": "Format data",
        "visible_columns": "Zobrazene sloupce v tabulce",
        "fx_pairs": "Zobrazene FX kurzy",
        "show_fx_rates": "Zobrazit FX kurzy v portfoliu",
        "theme": "Theme",
        "save_settings": "Ulozit nastaveni",
        "settings_saved": "Nastaveni bylo ulozeno.",
        "overview": "Prehled portfolia",
        "rates": "Kurzy",
        "summary": "Celkem",
        "allocation": "Rozlozeni portfolia",
        "profit_chart": "Zisk / ztrata podle tickeru",
        "history": "Historicky vyvoj portfolia",
        "period": "Obdobi",
        "benchmark": "Benchmark",
        "last_updated": "Posledni aktualizace",
        "best_position": "Nejlepsi pozice",
        "worst_position": "Nejhorsi pozice",
        "portfolio_return": "Portfolio return %",
        "benchmark_return": "Benchmark return %",
        "excess_return": "Excess return",
        "history_explainer": "Benchmark se porovnava od stejneho prvniho dne jako portfolio. Obe krivky zacinaji na 0 %, abys videl relativni vykonnost bez ohledu na rozdilnou velikost investice.",
        "missing_portfolio_history": "Pro vybrane obdobi nejsou k dispozici dostatecna historicka data portfolia.",
        "missing_benchmark_history": "Benchmark se nepodarilo nacist pro vybrane obdobi.",
        "missing_shared_history": "Portfolio a benchmark nemaji dost spolecnych historickych dat pro porovnani.",
        "missing_percent_history": "Pro vybrane obdobi neni dost dat pro vypocet procentniho porovnani.",
        "missing_tickers_warning": "U nekterych tickeru chybi historicka data, proto nejsou v grafu zapocitana: ",
    },
    "en": {
        "app_title": "Portfolio Tracker",
        "settings": "Settings",
        "portfolio_management": "Portfolio Management",
        "watchlist": "Watchlist",
        "watchlist_overview": "Watchlist Overview",
        "analysis": "Portfolio Plan",
        "long_term_plan": "Long-Term Plan",
        "reports": "Reports",
        "transactions": "Transactions",
        "earnings": "Earnings",
        "analysis_overview": "Stock detail and plan",
        "analysis_update": "Update plan",
        "analysis_decision": "New decision",
        "add": "Add",
        "edit": "Edit",
        "delete": "Delete",
        "language": "App language",
        "base_currency": "Portfolio base currency",
        "date_format": "Date format",
        "visible_columns": "Visible table columns",
        "fx_pairs": "Visible FX rates",
        "show_fx_rates": "Show FX rates in portfolio",
        "theme": "Theme",
        "save_settings": "Save settings",
        "settings_saved": "Settings were saved.",
        "overview": "Portfolio Overview",
        "rates": "FX Rates",
        "summary": "Summary",
        "allocation": "Portfolio Allocation",
        "profit_chart": "Profit / Loss by Ticker",
        "history": "Portfolio History",
        "period": "Period",
        "benchmark": "Benchmark",
        "last_updated": "Last updated",
        "best_position": "Best position",
        "worst_position": "Worst position",
        "portfolio_return": "Portfolio return %",
        "benchmark_return": "Benchmark return %",
        "excess_return": "Excess return",
        "history_explainer": "The benchmark is compared from the same starting day as the portfolio. Both lines start at 0% so you can compare relative performance regardless of portfolio size.",
        "missing_portfolio_history": "Not enough portfolio history is available for the selected period.",
        "missing_benchmark_history": "The benchmark could not be loaded for the selected period.",
        "missing_shared_history": "Portfolio and benchmark do not have enough shared history for comparison.",
        "missing_percent_history": "There is not enough data to calculate percentage comparison for the selected period.",
        "missing_tickers_warning": "Some tickers have missing history and were excluded from the chart: ",
    },
}

TABLE_COLUMN_HELP = {
    "Ticker": "Burzovni zkratka akcie, ETF nebo menoveho paru.",
    "Spolecnost": "Nazev firmy nebo fondu.",
    "Status": "Aktualni stav pozice, planu nebo kandidata ve watchlistu.",
    "Aktualni cena": "Posledni dostupna trzni cena jednoho kusu.",
    "Aktualni hodnota": "Posledni dostupna trzni cena jednoho kusu.",
    "Premarket cena": "Informacni cena pred otevrenim americkeho trhu. Nezapocitava se do vypoctu portfolia.",
    "Premarket zmena %": "Procentni zmena v US premarketu oproti poslednimu oficialnimu close. Jen informacni sloupec.",
    "Denni pohyb %": "Zmena oproti poslednimu oficialnimu close pro dany trh.",
    "Denni pohyb": "Penezni dopad posledni denni zmeny do tve zakladni meny.",
    "Pocet": "Pocet drzenych kusu akcie nebo ETF.",
    "Pocet kusu": "Pocet drzenych nebo uzavrenych kusu v danem obchodu.",
    "Nakupni cena": "Cena, za kterou byla pozice nakoupena.",
    "Prumerna nakupni cena": "Prumerna cena, za kterou je pozice nakoupena.",
    "Prumerna prodejni cena": "Prumerna cena, za kterou byla pozice prodana.",
    "Current Value": "Aktualni hodnota cele pozice v nastavene mene portfolia.",
    "Kapitalovy zisk": "Nerealizovany nebo souhrnny zisk po odecteni nakupni ceny.",
    "Nerealizovany zisk / ztrata": "Zisk nebo ztrata otevrene pozice, ktera jeste nebyla prodana.",
    "Nerealizovany zisk / ztrata %": "Procentni nerealizovany zisk nebo ztrata otevrene pozice.",
    "Realizovany zisk / ztrata": "Zisk nebo ztrata z uzavrene pozice po prodeji.",
    "Realizovany zisk / ztrata %": "Procentni zisk nebo ztrata z uzavrene pozice.",
    "% Zisk": "Procentni zhodnoceni pozice oproti nakupni cene.",
    "PE": "Price to Earnings. Kolikrat trh plati rocni zisk firmy v cene akcie.",
    "EPS": "Earnings per Share. Zisk firmy pripadajici na jednu akcii.",
    "Earnings Yield": "Obracena hodnota PE. Priblizny ziskovy vynos firmy vuci cene akcie.",
    "Market Cap": "Trzni kapitalizace, tedy celkova hodnota firmy na burze.",
    "Beta": "Citlivost akcie vuci pohybu trhu. Nad 1 = obvykle vyssi kolisavost nez trh.",
    "1 Year": "Zjednoduseny pohled na vyvoj ceny za posledni rok.",
    "Buy zone": "Cenove pasmo, ve kterem dává smysl uvazovat o nakupu.",
    "Plan nakupu": "Cena nebo uroven, kde chces nakup realizovat.",
    "Plan prodeje": "Cena nebo podminka, kde chces pozici castecne nebo uplne prodavat.",
    "Vzdalenost od buy zony": "O kolik procent je aktualni cena nad nebo pod buy zonou.",
    "Upside %": "Procentni rozdil mezi aktualni cenou a cilovou cenou.",
    "Conviction": "Jak silne veris investicni tezi pro danou pozici.",
    "Dalsi akce": "Nejblizsi konkretni krok, ktery planujes u dane pozice udelat.",
    "Posledni revize": "Kdy byl plan nebo analyza naposledy upraven.",
    "Cilova cena": "Cena, na kterou cilis podle investicniho planu.",
    "Invalidation level": "Uroven, kde by investicni teze prestala davat smysl a plan by se mel prehodnotit.",
    "Datum": "Datum udalosti, obchodu nebo zaznamu.",
    "Datum nakupu": "Den, kdy byl lot nebo pozice nakoupen.",
    "Datum prodeje": "Den, kdy byl lot nebo pozice prodan.",
    "Typ": "Typ zaznamu nebo rozhodnuti.",
    "Cena": "Cena na jeden kus nebo cena zaznamenana v danem rozhodnuti.",
    "Plan": "Strucny plan nebo zamysleny dalsi krok.",
    "Komentar": "Volna poznamka k rozhodnuti nebo obchodu.",
    "Mena": "Mena, ve ktere je aktivum nebo obchod veden.",
    "Broker": "Broker nebo platforma, pres kterou byl obchod proveden.",
    "Poznamka": "Doplnujici vlastni komentar.",
    "Rok realizace": "Kalendářní rok, ve kterem doslo k prodeji nebo realizaci vysledku.",
    "Prodejni obrat": "Celkovy objem prodanych cennych papiru za dane obdobi.",
    "Realizovany vysledek mimo 3lety test": "Zisk nebo ztrata z obchodu, ktery nesplnil casovy test.",
    "Poplatky mimo 3lety test": "Poplatky vztahujici se k obchodum mimo casovy test.",
    "Realizovane zisky": "Souhrn vsech ziskovych uzavrenych obchodu za dane obdobi.",
    "Realizovane ztraty": "Souhrn vsech ztratovych uzavrenych obchodu za dane obdobi.",
    "Realizovany vysledek": "Souhrnny realizovany vysledek po secteni zisku a ztrat.",
    "Poplatky": "Souhrn poplatku spojenych s obchody v danem prehledu.",
    "3lety test": "Informace, zda obchod splnil orientacni tri lety casovy test pro osvobozeni.",
    "Datum vysledku": "Planovane nebo skutecne datum zverejneni firemnich vysledku.",
    "Cas": "Kdy firma zverejnuje vysledky: pred open, po close nebo behem trhu.",
    "EPS odhad": "Ocekavany zisk na akcii podle analytiku pred vysledky.",
    "Revenue odhad": "Ocekavane trzby firmy podle analytiku pred vysledky.",
    "EPS realita": "Skutecne reportovany zisk na akcii po vysledcich.",
    "Revenue realita": "Skutecne reportovane trzby po vysledcich.",
    "EPS surprise": "Rozdil mezi odhadem analytiku a skutecnym EPS.",
    "Zdroj": "Udava, zda jsou data automaticka nebo rucne upravena.",
    "Instrument": "Srovnavany instrument nebo benchmark.",
    "Denni zmena %": "Procentni zmena za posledni obchodni den oproti predchozimu close.",
    "Rozdil vs portfolio": "Rozdil vykonu benchmarku oproti portfoliu v procentnich bodech.",
    "Hodnota": "Hodnota dane casti portfolia v nastavene mene.",
    "Podil %": "Jak velkou cast portfolia dany radek tvori.",
    "Region": "Zjednodusene geograficke zarazeni expozice.",
    "Velikost spolecnosti": "Zjednodusene rozdeleni podle velikosti trzni kapitalizace.",
    "Par": "Menovy par nebo sledovany FX kurz.",
    "Kurz": "Posledni dostupny kurz pro dany menovy par.",
    "Obdobi": "Sledovane casove obdobi vykonu nebo planu.",
    "Cisty vykon vc. uzavrenych pozic v penezich": "Cisty vykon portfolia v penezich vcetne uzavrenych obchodu.",
    "Cisty vykon vc. uzavrenych pozic %": "Cisty procentni vykon portfolia vcetne uzavrenych obchodu.",
    "SPY %": "Vykon benchmarku SPY za stejne obdobi.",
    "MSCI World ETF %": "Vykon benchmarku MSCI World ETF za stejne obdobi.",
    "Cisty vykon aktualniho portfolia %": "Vykon pouze aktualne drzenych pozic bez vlivu uzavrenych obchodu.",
}


def build_table_column_config(dataframe_or_columns, overrides: dict | None = None) -> dict:
    if isinstance(dataframe_or_columns, pd.DataFrame):
        columns = list(dataframe_or_columns.columns)
    else:
        columns = list(dataframe_or_columns)

    column_config = dict(overrides or {})
    for column in columns:
        if column in column_config:
            continue
        help_text = TABLE_COLUMN_HELP.get(column)
        if help_text:
            column_config[column] = st.column_config.TextColumn(help=help_text)
    return column_config


def load_portfolio() -> pd.DataFrame:
    # Nacte portfolio ze stejneho CSV souboru.
    try:
        df = pd.read_csv(CSV_PATH)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=["ticker", "company", "yfinance_ticker", "shares", "buy_price", "purchase_date"])

    for column in ["ticker", "company", "yfinance_ticker", "shares", "buy_price", "purchase_date"]:
        if column not in df.columns:
            df[column] = ""
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    df["shares"] = pd.to_numeric(df["shares"], errors="coerce").fillna(0.0)
    df["buy_price"] = pd.to_numeric(df["buy_price"], errors="coerce").fillna(0.0)
    if "purchase_date" not in df.columns:
        df["purchase_date"] = ""
    if "yfinance_ticker" not in df.columns:
        df["yfinance_ticker"] = df["ticker"]
    df["yfinance_ticker"] = df["yfinance_ticker"].fillna(df["ticker"]).replace("", pd.NA).fillna(df["ticker"])
    return df


def infer_transaction_currency(yfinance_ticker: str) -> str:
    # Jednoducha pomucka pro meny pri vytvareni transakci z existujiciho portfolia.
    ticker_text = str(yfinance_ticker).upper()
    if ticker_text.endswith(".AS") or ticker_text.endswith(".F") or ticker_text.endswith(".DE") or ticker_text.endswith(".PA"):
        return "EUR"
    return "USD"


def create_transactions_from_portfolio(raw_df: pd.DataFrame) -> pd.DataFrame:
    # Vytvori zakladni buy transakce z aktualniho portfolio.csv.
    if len(raw_df) == 0:
        return pd.DataFrame(
            columns=[
                "date",
                "ticker",
                "company",
                "transaction_type",
                "quantity",
                "price",
                "currency",
                "buy_fee",
                "sell_fee",
                "fx_fee",
                "tax_fx_rate",
                "tax_currency",
                "broker",
                "note",
            ]
        )

    rows = []
    for row in raw_df.itertuples(index=False):
        rows.append(
            {
                "date": row.purchase_date if pd.notna(row.purchase_date) and str(row.purchase_date).strip() else "",
                "ticker": row.ticker,
                "company": row.company if "company" in raw_df.columns and pd.notna(row.company) else "",
                "transaction_type": "buy",
                "quantity": float(row.shares),
                "price": float(row.buy_price),
                "currency": infer_transaction_currency(row.yfinance_ticker),
                "buy_fee": 0.0,
                "sell_fee": 0.0,
                "fx_fee": 0.0,
                "tax_fx_rate": None,
                "tax_currency": "CZK",
                "broker": "",
                "note": "Vytvoreno automaticky z portfolio.csv",
            }
        )
    return pd.DataFrame(rows)


def load_transactions(raw_df: pd.DataFrame) -> pd.DataFrame:
    # Nacte transakce nebo je jednorazove vytvori z portfolio.csv.
    try:
        df = pd.read_csv(TRANSACTIONS_PATH)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        df = create_transactions_from_portfolio(raw_df)
        if len(df) > 0:
            save_transactions(df)
        return df

    required_columns = [
        "date",
        "ticker",
        "company",
        "transaction_type",
        "quantity",
        "price",
        "currency",
        "buy_fee",
        "sell_fee",
        "fx_fee",
        "tax_fx_rate",
        "tax_currency",
        "broker",
        "note",
    ]
    for column in required_columns:
        if column not in df.columns:
            df[column] = ""

    # Migrace starsiho jednoho sloupce fee na oddelene poplatky.
    if "fee" in df.columns:
        fee_values = pd.to_numeric(df["fee"], errors="coerce").fillna(0.0)
        buy_mask = df["transaction_type"].astype(str).str.lower().str.strip() == "buy"
        sell_mask = df["transaction_type"].astype(str).str.lower().str.strip() == "sell"
        df.loc[buy_mask, "buy_fee"] = pd.to_numeric(df.loc[buy_mask, "buy_fee"], errors="coerce").fillna(fee_values[buy_mask])
        df.loc[sell_mask, "sell_fee"] = pd.to_numeric(df.loc[sell_mask, "sell_fee"], errors="coerce").fillna(fee_values[sell_mask])
        df = df.drop(columns=["fee"])

    if len(df) > 0:
        df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
        df["transaction_type"] = df["transaction_type"].astype(str).str.lower().str.strip()
        df["currency"] = df["currency"].apply(lambda value: str(value).upper().strip() if pd.notna(value) else "")
        df["currency"] = df["currency"].replace(["", "NAN", "NONE"], "USD")
        df["tax_currency"] = df["tax_currency"].apply(lambda value: str(value).upper().strip() if pd.notna(value) else "")
        df["tax_currency"] = df["tax_currency"].replace(["", "NAN", "NONE"], "CZK")
        for text_column in ["company", "broker", "note"]:
            df[text_column] = df[text_column].fillna("").replace("nan", "")
        for numeric_column in ["quantity", "price", "buy_fee", "sell_fee", "fx_fee", "tax_fx_rate"]:
            df[numeric_column] = pd.to_numeric(df[numeric_column], errors="coerce")
    return df


def load_watchlist() -> pd.DataFrame:
    # Nacte watchlist ze samostatneho CSV souboru.
    try:
        df = pd.read_csv(WATCHLIST_PATH)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(
            columns=[
                "ticker",
                "company",
                "yfinance_ticker",
                "buy_zone_low",
                "buy_zone_high",
                "buy_plan",
                "sell_target",
                "note_date",
                "note_price",
                "note_text",
            ]
        )

    for column in ["ticker", "company", "yfinance_ticker", "buy_zone_low", "buy_zone_high", "buy_plan", "sell_target", "note_date", "note_price", "note_text"]:
        if column not in df.columns:
            df[column] = ""

    if len(df) > 0:
        df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
        if "yfinance_ticker" not in df.columns:
            df["yfinance_ticker"] = df["ticker"]
        df["yfinance_ticker"] = df["yfinance_ticker"].fillna(df["ticker"]).replace("", pd.NA).fillna(df["ticker"])
        for numeric_column in ["buy_zone_low", "buy_zone_high", "buy_plan", "sell_target", "note_price"]:
            df[numeric_column] = pd.to_numeric(df[numeric_column], errors="coerce")
    return df


def load_analysis() -> pd.DataFrame:
    # Nacte aktualni analyzu a plan pro tickery.
    try:
        df = pd.read_csv(ANALYSIS_PATH)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(
            columns=[
                "ticker",
                "company",
                "avg_buy_price",
                "target_price",
                "invalidation_level",
                "status",
                "conviction",
                "next_action",
                "investment_thesis",
                "buy_plan",
                "sell_plan",
                "risk_notes",
                "last_note",
                "updated_at",
            ]
        )

    if len(df) > 0:
        df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    for column in [
        "company",
        "avg_buy_price",
        "target_price",
        "invalidation_level",
        "status",
        "conviction",
        "next_action",
        "investment_thesis",
        "buy_plan",
        "sell_plan",
        "risk_notes",
        "last_note",
        "updated_at",
    ]:
        if column not in df.columns:
            df[column] = ""
    return df


def load_analysis_history() -> pd.DataFrame:
    # Nacte historii rozhodnuti po jednotlivych zaznamech.
    try:
        df = pd.read_csv(ANALYSIS_HISTORY_PATH)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(
            columns=[
                "ticker",
                "decision_date",
                "decision_type",
                "price",
                "plan_text",
                "comment",
            ]
        )

    for column in ["ticker", "decision_date", "decision_type", "price", "plan_text", "comment"]:
        if column not in df.columns:
            df[column] = ""

    if len(df) > 0:
        df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
    return df


def load_long_term_plans() -> pd.DataFrame:
    # Nacte seznam dlouhodobych planu.
    try:
        df = pd.read_csv(LONG_TERM_PLANS_PATH)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(
            columns=[
                "plan_name",
                "start_period",
                "target_period",
                "start_value",
                "target_value",
                "monthly_contribution",
                "expected_return_pct",
                "plan_notes",
                "asset_notes",
            ]
        )
    for column in ["plan_name", "start_period", "target_period", "start_value", "target_value", "monthly_contribution", "expected_return_pct", "plan_notes", "asset_notes"]:
        if column not in df.columns:
            df[column] = ""
    for numeric_column in ["start_value", "target_value", "monthly_contribution", "expected_return_pct"]:
        df[numeric_column] = pd.to_numeric(df[numeric_column], errors="coerce")
    return df


def load_long_term_checks() -> pd.DataFrame:
    # Nacte kontroly dlouhodobeho planu po jednotlivych obdobich.
    try:
        df = pd.read_csv(LONG_TERM_CHECKS_PATH)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(
            columns=[
                "plan_name",
                "period_label",
                "period_date",
                "planned_value",
                "actual_value",
                "deviation",
                "completion_pct",
                "note_plan",
                "note_assets",
                "next_step",
                "source",
                "is_manual_override",
            ]
        )
    for column in ["plan_name", "period_label", "period_date", "planned_value", "actual_value", "deviation", "completion_pct", "note_plan", "note_assets", "next_step", "source", "is_manual_override"]:
        if column not in df.columns:
            df[column] = ""
    if "note" in df.columns and "note_plan" not in df.columns:
        df["note_plan"] = df["note"]
    for column in [
        "deviation",
        "completion_pct",
        "note_plan",
        "note_assets",
        "next_step",
        "source",
        "is_manual_override",
    ]:
        if column not in df.columns:
            df[column] = ""
    if "source" in df.columns:
        df["source"] = df["source"].replace("", "manual").fillna("manual")
    for numeric_column in ["planned_value", "actual_value", "deviation", "completion_pct"]:
        df[numeric_column] = pd.to_numeric(df[numeric_column], errors="coerce")
    if "is_manual_override" in df.columns:
        df["is_manual_override"] = (
            df["is_manual_override"]
            .astype(str)
            .str.lower()
            .map({"true": True, "false": False})
            .fillna(False)
        )
    return df


def load_earnings_calendar() -> pd.DataFrame:
    # Nacte earnings kalendar s auto i manual poli.
    try:
        df = pd.read_csv(EARNINGS_PATH)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(
            columns=[
                "ticker",
                "company",
                "yfinance_ticker",
                "earnings_date",
                "earnings_time",
                "eps_estimate",
                "revenue_estimate",
                "eps_actual",
                "revenue_actual",
                "eps_surprise_pct",
                "revenue_surprise_pct",
                "status",
                "source",
                "is_manual_override",
                "note",
                "updated_at",
            ]
        )

    required_columns = [
        "ticker",
        "company",
        "yfinance_ticker",
        "earnings_date",
        "earnings_time",
        "eps_estimate",
        "revenue_estimate",
        "eps_actual",
        "revenue_actual",
        "eps_surprise_pct",
        "revenue_surprise_pct",
        "status",
        "source",
        "is_manual_override",
        "note",
        "updated_at",
    ]
    for column in required_columns:
        if column not in df.columns:
            df[column] = ""

    if len(df) > 0:
        df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
        df["yfinance_ticker"] = df["yfinance_ticker"].fillna(df["ticker"]).replace("", pd.NA).fillna(df["ticker"])
        for numeric_column in [
            "eps_estimate",
            "revenue_estimate",
            "eps_actual",
            "revenue_actual",
            "eps_surprise_pct",
            "revenue_surprise_pct",
        ]:
            df[numeric_column] = pd.to_numeric(df[numeric_column], errors="coerce")
        df["source"] = df["source"].fillna("").replace("", "manual")
        df["is_manual_override"] = (
            df["is_manual_override"]
            .astype(str)
            .str.lower()
            .map({"true": True, "false": False})
            .fillna(False)
        )
        for text_column in ["company", "earnings_time", "status", "note", "updated_at"]:
            df[text_column] = df[text_column].fillna("").replace("nan", "")
    return df


def save_earnings_calendar(df: pd.DataFrame) -> None:
    # Ulozi earnings kalendar do CSV.
    columns_to_save = [
        "ticker",
        "company",
        "yfinance_ticker",
        "earnings_date",
        "earnings_time",
        "eps_estimate",
        "revenue_estimate",
        "eps_actual",
        "revenue_actual",
        "eps_surprise_pct",
        "revenue_surprise_pct",
        "status",
        "source",
        "is_manual_override",
        "note",
        "updated_at",
    ]
    df[columns_to_save].to_csv(EARNINGS_PATH, index=False)


def clean_text_value(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    return "" if text.lower() == "nan" else text


def format_large_number(value: float | None, currency: str = "USD") -> str:
    if value is None or pd.isna(value):
        return "N/A"
    absolute_value = abs(float(value))
    if absolute_value >= 1_000_000_000:
        return f"{currency} {value / 1_000_000_000:.2f}B"
    if absolute_value >= 1_000_000:
        return f"{currency} {value / 1_000_000:.2f}M"
    if absolute_value >= 1_000:
        return f"{currency} {value / 1_000:.2f}K"
    return f"{currency} {value:.2f}"


def format_earnings_date_value(value, date_format_label: str) -> str:
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return "N/A"
    return format_date_display(str(parsed.date()), date_format_label)


def normalize_earnings_time_label(value) -> str:
    text = clean_text_value(value).lower()
    mapping = {
        "amc": "After close",
        "after market close": "After close",
        "after close": "After close",
        "bmo": "Before open",
        "before market open": "Before open",
        "before open": "Before open",
        "dmh": "During market",
        "during market": "During market",
        "tbd": "TBD",
    }
    return mapping.get(text, clean_text_value(value) if clean_text_value(value) else "TBD")


def infer_earnings_status(row: pd.Series) -> str:
    earnings_date = pd.to_datetime(row.get("earnings_date", ""), errors="coerce")
    eps_actual = safe_float(row.get("eps_actual"))
    revenue_actual = safe_float(row.get("revenue_actual"))
    if eps_actual is not None or revenue_actual is not None:
        return "Vyhlaseno"
    if pd.isna(earnings_date):
        return "Bez dat"
    today = pd.Timestamp(datetime.now().date())
    if earnings_date.normalize() < today:
        return "Ceka se na realitu"
    if earnings_date.normalize() == today:
        return "Dnes"
    return "Ceka se"


def build_earnings_universe(raw_df: pd.DataFrame, watchlist_df: pd.DataFrame, analysis_df: pd.DataFrame) -> pd.DataFrame:
    # Posklada unikatni seznam tickeru z portfolia, watchlistu a analyzy.
    rows: list[dict] = []
    seen: set[str] = set()
    for frame in [raw_df, watchlist_df, analysis_df]:
        if len(frame) == 0 or "ticker" not in frame.columns:
            continue
        for row in frame.itertuples(index=False):
            ticker = clean_text_value(getattr(row, "ticker", "")).upper()
            if not ticker or ticker in seen:
                continue
            company = clean_text_value(getattr(row, "company", ""))
            yfinance_ticker = clean_text_value(getattr(row, "yfinance_ticker", "")) or ticker
            rows.append(
                {
                    "ticker": ticker,
                    "company": company,
                    "yfinance_ticker": yfinance_ticker,
                }
            )
            seen.add(ticker)
    return pd.DataFrame(rows)


def classify_earnings_membership(ticker: str, portfolio_tickers: set[str], watchlist_tickers: set[str]) -> str:
    ticker_text = clean_text_value(ticker).upper()
    in_portfolio = ticker_text in portfolio_tickers
    in_watchlist = ticker_text in watchlist_tickers
    if in_portfolio and in_watchlist:
        return "Portfolio + watchlist"
    if in_portfolio:
        return "Portfolio"
    if in_watchlist:
        return "Watchlist"
    return "Mimo seznam"


def extract_calendar_value(calendar_data, label: str):
    if calendar_data is None:
        return None
    if isinstance(calendar_data, dict):
        return calendar_data.get(label)
    if isinstance(calendar_data, pd.DataFrame):
        if label in calendar_data.index:
            selected = calendar_data.loc[label]
            if isinstance(selected, pd.Series) and len(selected) > 0:
                return selected.iloc[0]
            return selected
        if label in calendar_data.columns and len(calendar_data[label]) > 0:
            return calendar_data[label].iloc[0]
    if isinstance(calendar_data, pd.Series):
        return calendar_data.get(label)
    return None


@st.cache_data(ttl=21600, show_spinner=False)
def fetch_earnings_snapshot(yfinance_ticker: str) -> dict:
    # Nacte nejblizsi earnings datum a dostupne odhady/skutecnost z Yahoo Finance.
    result = {
        "earnings_date": "",
        "earnings_time": "",
        "eps_estimate": None,
        "revenue_estimate": None,
        "eps_actual": None,
        "revenue_actual": None,
        "eps_surprise_pct": None,
        "revenue_surprise_pct": None,
        "source": "auto",
    }
    ticker_text = clean_text_value(yfinance_ticker)
    if not ticker_text:
        return result

    try:
        ticker = yf.Ticker(ticker_text)
    except Exception:
        return result

    try:
        calendar_data = ticker.calendar
    except Exception:
        calendar_data = None

    earnings_date_value = extract_calendar_value(calendar_data, "Earnings Date")
    if isinstance(earnings_date_value, (list, tuple)) and earnings_date_value:
        earnings_date_value = earnings_date_value[0]
    parsed_earnings_date = pd.to_datetime(earnings_date_value, errors="coerce")
    if pd.notna(parsed_earnings_date):
        result["earnings_date"] = str(parsed_earnings_date.date())

    result["eps_estimate"] = safe_float(extract_calendar_value(calendar_data, "EPS Estimate"))
    result["revenue_estimate"] = safe_float(extract_calendar_value(calendar_data, "Revenue Estimate"))

    try:
        earnings_dates_df = ticker.get_earnings_dates(limit=8)
    except Exception:
        earnings_dates_df = pd.DataFrame()

    if isinstance(earnings_dates_df, pd.DataFrame) and len(earnings_dates_df) > 0:
        earnings_dates_df = earnings_dates_df.copy().reset_index()
        date_column = earnings_dates_df.columns[0]
        earnings_dates_df["event_date"] = pd.to_datetime(earnings_dates_df[date_column], errors="coerce")
        earnings_dates_df = earnings_dates_df.dropna(subset=["event_date"])
        if len(earnings_dates_df) > 0:
            today = pd.Timestamp(datetime.now().date())
            future_rows = earnings_dates_df[earnings_dates_df["event_date"] >= (today - timedelta(days=2))]
            if not future_rows.empty:
                nearest_row = future_rows.sort_values("event_date").iloc[0]
                if not result["earnings_date"]:
                    result["earnings_date"] = str(nearest_row["event_date"].date())
                if result["eps_estimate"] is None and "EPS Estimate" in future_rows.columns:
                    result["eps_estimate"] = safe_float(nearest_row.get("EPS Estimate"))

            if "Reported EPS" in earnings_dates_df.columns:
                realized_rows = earnings_dates_df[earnings_dates_df["Reported EPS"].notna()].copy()
            else:
                realized_rows = pd.DataFrame()
            if len(realized_rows) > 0:
                latest_realized = realized_rows.sort_values("event_date", ascending=False).iloc[0]
                result["eps_actual"] = safe_float(latest_realized.get("Reported EPS"))
                if "EPS Estimate" in realized_rows.columns and result["eps_estimate"] is None:
                    result["eps_estimate"] = safe_float(latest_realized.get("EPS Estimate"))
                if "Surprise(%)" in realized_rows.columns:
                    result["eps_surprise_pct"] = safe_float(latest_realized.get("Surprise(%)"))

    try:
        info = ticker.info
    except Exception:
        info = {}

    earnings_timestamp = info.get("earningsTimestamp") or info.get("earningsTimestampStart")
    if earnings_timestamp and not result["earnings_date"]:
        parsed_timestamp = pd.to_datetime(earnings_timestamp, unit="s", errors="coerce")
        if pd.notna(parsed_timestamp):
            result["earnings_date"] = str(parsed_timestamp.date())

    result["earnings_time"] = normalize_earnings_time_label(info.get("earningsCallTime") or info.get("earningsCallTimeShort"))
    if result["revenue_estimate"] is None:
        result["revenue_estimate"] = safe_float(info.get("revenueEstimate"))
    return result


def merge_auto_earnings_data(
    earnings_df: pd.DataFrame,
    universe_df: pd.DataFrame,
    force_manual_override: bool = False,
) -> tuple[pd.DataFrame, list[str]]:
    # Doplni nebo obnovi earnings data z online zdroje.
    working_df = earnings_df.copy()
    refreshed_tickers: list[str] = []
    timestamp_now = datetime.now().strftime("%Y-%m-%d %H:%M")

    for row in universe_df.itertuples(index=False):
        ticker = clean_text_value(row.ticker).upper()
        if not ticker:
            continue
        company = clean_text_value(row.company)
        yfinance_ticker = clean_text_value(row.yfinance_ticker) or ticker
        existing_index = working_df.index[working_df["ticker"] == ticker].tolist()
        existing_row = working_df.loc[existing_index[0]] if existing_index else pd.Series(dtype=object)
        is_manual_override = bool(existing_row.get("is_manual_override", False)) if not existing_row.empty else False
        if is_manual_override and not force_manual_override:
            if existing_index:
                if not clean_text_value(existing_row.get("company", "")) and company:
                    working_df.loc[existing_index[0], "company"] = company
                if not clean_text_value(existing_row.get("yfinance_ticker", "")) and yfinance_ticker:
                    working_df.loc[existing_index[0], "yfinance_ticker"] = yfinance_ticker
            else:
                new_row = {
                    "ticker": ticker,
                    "company": company,
                    "yfinance_ticker": yfinance_ticker,
                    "earnings_date": "",
                    "earnings_time": "TBD",
                    "eps_estimate": None,
                    "revenue_estimate": None,
                    "eps_actual": None,
                    "revenue_actual": None,
                    "eps_surprise_pct": None,
                    "revenue_surprise_pct": None,
                    "status": "Bez dat",
                    "source": "manual",
                    "is_manual_override": True,
                    "note": "",
                    "updated_at": timestamp_now,
                }
                working_df = pd.concat([working_df, pd.DataFrame([new_row])], ignore_index=True)
            continue

        snapshot = fetch_earnings_snapshot(yfinance_ticker)
        row_data = {
            "ticker": ticker,
            "company": company or clean_text_value(existing_row.get("company", "")),
            "yfinance_ticker": yfinance_ticker,
            "earnings_date": clean_text_value(snapshot.get("earnings_date", "")),
            "earnings_time": clean_text_value(snapshot.get("earnings_time", "")) or "TBD",
            "eps_estimate": snapshot.get("eps_estimate"),
            "revenue_estimate": snapshot.get("revenue_estimate"),
            "eps_actual": snapshot.get("eps_actual"),
            "revenue_actual": snapshot.get("revenue_actual"),
            "eps_surprise_pct": snapshot.get("eps_surprise_pct"),
            "revenue_surprise_pct": snapshot.get("revenue_surprise_pct"),
            "source": "auto",
            "is_manual_override": False,
            "note": clean_text_value(existing_row.get("note", "")),
            "updated_at": timestamp_now,
        }
        row_data["status"] = infer_earnings_status(pd.Series(row_data))

        if existing_index:
            working_df.loc[existing_index[0], list(row_data.keys())] = list(row_data.values())
        else:
            working_df = pd.concat([working_df, pd.DataFrame([row_data])], ignore_index=True)
        refreshed_tickers.append(ticker)

    if len(working_df) > 0:
        working_df["status"] = working_df.apply(infer_earnings_status, axis=1)
    return working_df, refreshed_tickers


def load_settings() -> dict:
    # Nacte nastaveni z JSON souboru, nebo vrati vychozi hodnoty.
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as file:
            saved_settings = json.load(file)
    except FileNotFoundError:
        saved_settings = {}
    except json.JSONDecodeError:
        saved_settings = {}

    settings = DEFAULT_SETTINGS.copy()
    settings.update(saved_settings)
    if settings.get("language") not in ["cs", "en"]:
        settings["language"] = DEFAULT_SETTINGS["language"]
    if settings.get("base_currency") not in ["USD", "EUR", "CZK"]:
        settings["base_currency"] = DEFAULT_SETTINGS["base_currency"]
    if settings.get("date_format") not in DATE_FORMATS:
        settings["date_format"] = DEFAULT_SETTINGS["date_format"]
    if settings.get("theme") not in ["dark", "light"]:
        settings["theme"] = DEFAULT_SETTINGS["theme"]
    settings["show_fx_rates"] = bool(settings.get("show_fx_rates", DEFAULT_SETTINGS["show_fx_rates"]))

    # Jednoducha migrace starsich nazvu sloupcu v nastaveni.
    if "visible_columns" in settings:
        migrated_columns = [
            "Denni pohyb" if column == "Dnes" else column
            for column in settings["visible_columns"]
        ]
        settings["visible_columns"] = [
            column for column in migrated_columns if column in DEFAULT_VISIBLE_COLUMNS
        ] or DEFAULT_VISIBLE_COLUMNS.copy()
        if "1 Year" not in settings["visible_columns"]:
            nakupni_index = settings["visible_columns"].index("Nakupni cena") + 1 if "Nakupni cena" in settings["visible_columns"] else len(settings["visible_columns"])
            settings["visible_columns"].insert(nakupni_index, "1 Year")
    settings["fx_pairs"] = [
        pair for pair in settings.get("fx_pairs", DEFAULT_FX_PAIRS)
        if pair in FX_PAIR_CONFIG
    ] or DEFAULT_FX_PAIRS.copy()
    return settings


def save_settings(settings: dict) -> None:
    # Ulozi nastaveni do jednoducheho JSON souboru.
    with open(SETTINGS_PATH, "w", encoding="utf-8") as file:
        json.dump(settings, file, ensure_ascii=False, indent=2)


def t(key: str, language: str) -> str:
    # Vrati kratky preklad pro hlavni casti aplikace.
    return TEXTS.get(language, TEXTS["cs"]).get(key, key)


def render_page_header(title: str, subtitle: str, eyebrow: str = "Workspace") -> None:
    st.markdown(
        f"""
        <div class="page-hero">
            <div class="page-eyebrow">{eyebrow}</div>
            <div class="page-title">{title}</div>
            <div class="page-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_cards(cards: list[dict]) -> None:
    columns = st.columns(len(cards))
    for column, card in zip(columns, cards):
        delta = card.get("delta", "")
        tone = card.get("tone", "neutral")
        with column:
            st.markdown(
                f"""
                <div class="metric-card tone-{tone}">
                    <div class="metric-label">{card.get("label", "")}</div>
                    <div class="metric-value">{card.get("value", "N/A")}</div>
                    <div class="metric-delta">{delta}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_section_intro(title: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div class="section-head">
            <div class="section-title">{title}</div>
            <div class="section-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_currency_metric(
    value: float | None,
    currency: str,
    decimals: int = 2,
    thousands_sep: str = ",",
    decimal_sep: str = ".",
) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    formatted = f"{value:,.{decimals}f}"
    if thousands_sep != "," or decimal_sep != ".":
        formatted = formatted.replace(",", "__THOUSANDS__").replace(".", "__DECIMAL__")
        formatted = formatted.replace("__THOUSANDS__", thousands_sep).replace("__DECIMAL__", decimal_sep)
    return f"{currency} {formatted}"


def prepare_export_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    export_df = df.copy()
    export_df = export_df.fillna("")
    for column in export_df.columns:
        export_df[column] = export_df[column].apply(lambda value: value.strftime("%d.%m.%Y") if isinstance(value, (pd.Timestamp, datetime)) else value)
    return export_df


def dataframe_to_excel_bytes(df: pd.DataFrame, sheet_name: str = "Export") -> bytes:
    try:
        import xlsxwriter  # noqa: F401
    except ModuleNotFoundError as exc:
        raise RuntimeError("Pro export do Excelu je potreba nainstalovat xlsxwriter.") from exc

    export_df = prepare_export_dataframe(df)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        export_df.to_excel(writer, index=False, sheet_name=sheet_name)
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]

        header_format = workbook.add_format(
            {
                "bold": True,
                "font_color": "#17302d",
                "bg_color": "#d8eeea",
                "border": 1,
                "border_color": "#a7cfc8",
                "align": "left",
                "valign": "vcenter",
            }
        )
        cell_format = workbook.add_format(
            {
                "border": 1,
                "border_color": "#d7e4e0",
                "valign": "top",
                "text_wrap": True,
            }
        )

        for col_num, column_name in enumerate(export_df.columns):
            worksheet.write(0, col_num, column_name, header_format)
            column_values = [str(column_name)] + export_df.iloc[:, col_num].astype(str).tolist()
            max_len = min(max(len(value) for value in column_values) + 2, 28)
            worksheet.set_column(col_num, col_num, max(12, max_len), cell_format)

        worksheet.freeze_panes(1, 0)
        worksheet.autofilter(0, 0, len(export_df), max(len(export_df.columns) - 1, 0))

    output.seek(0)
    return output.getvalue()


def dataframe_to_pdf_bytes(df: pd.DataFrame, title: str) -> bytes:
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ModuleNotFoundError as exc:
        raise RuntimeError("Pro export do PDF je potreba nainstalovat reportlab.") from exc

    export_df = prepare_export_dataframe(df)
    output = BytesIO()
    doc = SimpleDocTemplate(
        output,
        pagesize=landscape(A4),
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = styles["Heading2"]
    title_style.textColor = colors.HexColor("#17302d")
    meta_style = styles["BodyText"]
    meta_style.textColor = colors.HexColor("#5f716e")

    data = [list(export_df.columns)] + export_df.astype(str).values.tolist()
    safe_data = [[Paragraph(str(cell).replace("\n", "<br/>"), styles["BodyText"]) for cell in row] for row in data]

    available_width = landscape(A4)[0] - doc.leftMargin - doc.rightMargin
    col_count = max(len(export_df.columns), 1)
    col_width = available_width / col_count
    table = Table(safe_data, colWidths=[col_width] * col_count, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d8eeea")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#17302d")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("LEADING", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#bfdad4")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4fbf9")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    story = [
        Paragraph(title, title_style),
        Spacer(1, 4 * mm),
        Paragraph(f"Vygenerovano: {datetime.now().strftime('%d.%m.%Y %H:%M')}", meta_style),
        Spacer(1, 5 * mm),
        table,
    ]
    doc.build(story)
    output.seek(0)
    return output.getvalue()


def format_percent_metric(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:.2f} %"


def is_us_regular_market_open_now() -> bool:
    # Hlavni americka seance 9:30-16:00 New York cas v pracovni dny.
    ny_now = datetime.now(ZoneInfo("America/New_York"))
    if ny_now.weekday() >= 5:
        return False
    market_open = ny_now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = ny_now.replace(hour=16, minute=0, second=0, microsecond=0)
    return market_open <= ny_now < market_close


def is_us_premarket_now() -> bool:
    # Premarket pro US akcie bereme orientacne jako 4:00-9:30 New York cas v pracovni dny.
    ny_now = datetime.now(ZoneInfo("America/New_York"))
    if ny_now.weekday() >= 5:
        return False
    market_open = ny_now.replace(hour=4, minute=0, second=0, microsecond=0)
    regular_open = ny_now.replace(hour=9, minute=30, second=0, microsecond=0)
    return market_open <= ny_now < regular_open


def format_watchlist_badge(status: str) -> str:
    if status == "V nakupni zone":
        return "🟢 V nakupni zone"
    if status == "Pod nakupni zonou":
        return "🔵 Pod nakupni zonou"
    if status == "Nad nakupni zonou":
        return "🟠 Nad nakupni zonou"
    return "N/A"


def format_watchlist_badge(status: str) -> str:
    # ASCII badge text kvuli konzistentnimu zobrazeni v dataframe.
    if status == "V nakupni zone":
        return "BUY ZONA"
    if status == "Pod nakupni zonou":
        return "POD ZONOU"
    if status == "Nad nakupni zonou":
        return "NAD ZONOU"
    return "N/A"


def apply_theme(theme: str) -> None:
    # Jednoduchy light/dark vzhled pomoci CSS.
    if theme == "light":
        st.markdown(
            """
            <style>
            .stApp { background-color: #f7f7f7; color: #111; }
            section[data-testid="stSidebar"] {
                background: linear-gradient(180deg, #ffffff 0%, #f1f4f8 100%);
                border-right: 1px solid #d9e1ea;
            }
            [data-testid="stSidebar"] .sidebar-brand {
                padding: 0.35rem 0.15rem 1rem 0.15rem;
                margin: 0 0 1.15rem 0;
                border-radius: 0;
                background: transparent;
                border: none;
                box-shadow: none;
                position: relative;
            }
            [data-testid="stSidebar"] .sidebar-brand::after {
                content: "";
                display: block;
                width: 100%;
                height: 1px;
                margin-top: 0.95rem;
                background: linear-gradient(90deg, rgba(185, 220, 214, 0.95) 0%, rgba(217, 225, 234, 0.85) 62%, rgba(217, 225, 234, 0) 100%);
            }
            [data-testid="stSidebar"] .sidebar-kicker {
                font-size: 0.74rem;
                letter-spacing: 0.16em;
                text-transform: uppercase;
                color: #6c8b87;
                margin-bottom: 0.3rem;
                font-weight: 600;
            }
            [data-testid="stSidebar"] .sidebar-title {
                font-size: 1.52rem;
                font-weight: 800;
                color: #17302d;
                line-height: 1.05;
            }
            [data-testid="stSidebar"] .sidebar-section {
                font-size: 0.78rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                color: #64748b;
                margin: 0.8rem 0 0.35rem 0.15rem;
            }
            [data-testid="stSidebar"] div[role="radiogroup"] {
                padding: 0.1rem 0;
                background: transparent;
                border: none;
                box-shadow: none;
            }
            [data-testid="stSidebar"] div[role="radiogroup"] label {
                width: 100%;
                border-radius: 18px;
                padding: 0.86rem 1.15rem;
                margin-bottom: 0.48rem;
                border: 1px solid transparent;
                background: transparent;
                transition: background-color 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease;
            }
            [data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
                display: none;
            }
            [data-testid="stSidebar"] div[role="radiogroup"] label p {
                font-size: 1.02rem;
                font-weight: 500;
                color: #627471;
            }
            [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
                background: linear-gradient(180deg, #e5f4f1 0%, #dcefea 100%);
                border-color: #d4e9e3;
                transform: translateY(-1px);
            }
            [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
                background: linear-gradient(180deg, #d8eeea 0%, #d2e9e4 100%);
                border-color: rgba(29, 33, 38, 0.92);
                box-shadow: 0 10px 24px rgba(143, 184, 176, 0.16);
            }
            [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
                color: #203433;
                font-weight: 600;
            }
            .page-hero {
                margin: 0 0 1.2rem 0;
                padding: 1.2rem 1.3rem;
                border-radius: 24px;
                background: linear-gradient(135deg, #ffffff 0%, #f3f7fb 100%);
                border: 1px solid #d9e1ea;
            }
            .page-eyebrow, .section-subtitle {
                font-size: 0.85rem;
                color: #64748b;
            }
            .page-title {
                font-size: 2.2rem;
                font-weight: 800;
                color: #0f172a;
                margin: 0.25rem 0;
            }
            .page-subtitle {
                color: #475569;
                max-width: 900px;
            }
            .metric-card {
                padding: 1rem 1.05rem;
                border-radius: 20px;
                border: 1px solid #d9e1ea;
                background: #ffffff;
                box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05);
            }
            .metric-label {
                font-size: 0.8rem;
                text-transform: uppercase;
                letter-spacing: 0.06em;
                color: #64748b;
                margin-bottom: 0.45rem;
            }
            .metric-value {
                font-size: 1.8rem;
                font-weight: 800;
                color: #0f172a;
            }
            .metric-delta {
                margin-top: 0.35rem;
                color: #475569;
                font-size: 0.92rem;
            }
            .section-head {
                margin: 1rem 0 0.75rem 0;
            }
            .section-title {
                font-size: 1.2rem;
                font-weight: 700;
                color: #0f172a;
            }
            .stTabs [data-baseweb="tab-list"] {
                gap: 0.35rem;
                border-bottom: 1px solid #d9e1ea;
                padding-bottom: 0.32rem;
            }
            .stTabs {
                margin-top: 0.35rem;
            }
            .stTabs [data-baseweb="tab"] {
                height: auto;
                background: transparent;
                border-radius: 0.8rem 0.8rem 0 0;
                padding: 0.68rem 1rem 0.72rem 1rem;
                margin: 0;
                color: #64748b;
                font-weight: 600;
                transition: background-color 0.18s ease, color 0.18s ease, box-shadow 0.18s ease;
            }
            .stTabs [data-baseweb="tab"]:hover {
                background: rgba(148, 163, 184, 0.12);
                color: #0f172a;
            }
            .stTabs [data-baseweb="tab"][aria-selected="true"] {
                background: linear-gradient(180deg, rgba(216, 238, 234, 0.95) 0%, rgba(210, 233, 228, 0.98) 100%);
                color: #dc2626;
                font-weight: 800;
                border: 1px solid rgba(29, 33, 38, 0.92);
                box-shadow: 0 8px 18px rgba(143, 184, 176, 0.12);
                border-bottom: 2px solid rgba(255, 90, 95, 0.75);
            }
            [data-testid="stHorizontalBlock"]:has(.fake-toolbar-anchor) {
                align-items: center;
                margin: 0.2rem 0 0.35rem 0;
            }
            [data-testid="stHorizontalBlock"]:has(.fake-toolbar-anchor) [data-testid="column"] {
                display: flex;
                align-items: center;
            }
            .fake-toolbar-anchor {
                display: block;
                min-height: 1px;
            }
            .fake-toolbar-title {
                font-size: 1.08rem;
                font-weight: 700;
                color: #0f172a;
                margin: 0;
            }
            [data-testid="stHorizontalBlock"]:has(.fake-toolbar-anchor) button[kind] {
                min-height: 2rem;
                padding: 0.15rem 0.6rem;
                border-radius: 0.65rem;
                border: 1px solid #d9e1ea;
                background: #ffffff;
                color: #0f172a;
                font-size: 0.76rem;
                font-weight: 700;
                letter-spacing: 0.04em;
            }
            [data-testid="stHorizontalBlock"]:has(.fake-toolbar-anchor) button[kind]:hover {
                border-color: #c7d2e0;
                background: #f8fafc;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <style>
            .stApp { background-color: #0f1116; color: #f4f4f4; }
            section[data-testid="stSidebar"] {
                background: linear-gradient(180deg, #141923 0%, #0f141c 100%);
                border-right: 1px solid #232b38;
            }
            [data-testid="stSidebar"] .sidebar-brand {
                padding: 0.35rem 0.15rem 1rem 0.15rem;
                margin: 0 0 1.15rem 0;
                border-radius: 0;
                background: transparent;
                border: none;
                box-shadow: none;
                position: relative;
            }
            [data-testid="stSidebar"] .sidebar-brand::after {
                content: "";
                display: block;
                width: 100%;
                height: 1px;
                margin-top: 0.95rem;
                background: linear-gradient(90deg, rgba(190, 230, 223, 0.88) 0%, rgba(62, 77, 98, 0.72) 62%, rgba(62, 77, 98, 0) 100%);
            }
            [data-testid="stSidebar"] .sidebar-kicker {
                font-size: 0.74rem;
                letter-spacing: 0.16em;
                text-transform: uppercase;
                color: #9dbdb8;
                margin-bottom: 0.3rem;
                font-weight: 600;
            }
            [data-testid="stSidebar"] .sidebar-title {
                font-size: 1.52rem;
                font-weight: 800;
                color: #f2f7f6;
                line-height: 1.05;
            }
            [data-testid="stSidebar"] .sidebar-section {
                font-size: 0.78rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                color: #8b9bb2;
                margin: 0.8rem 0 0.35rem 0.15rem;
            }
            [data-testid="stSidebar"] div[role="radiogroup"] {
                padding: 0.1rem 0;
                background: transparent;
                border: none;
                box-shadow: none;
            }
            [data-testid="stSidebar"] div[role="radiogroup"] label {
                width: 100%;
                border-radius: 18px;
                padding: 0.86rem 1.15rem;
                margin-bottom: 0.48rem;
                border: 1px solid transparent;
                background: transparent;
                transition: background-color 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease;
            }
            [data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
                display: none;
            }
            [data-testid="stSidebar"] div[role="radiogroup"] label p {
                font-size: 1.02rem;
                font-weight: 500;
                color: #d3ddd9;
            }
            [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
                background: linear-gradient(180deg, rgba(196, 233, 226, 0.18) 0%, rgba(173, 217, 210, 0.14) 100%);
                border-color: rgba(186, 223, 216, 0.14);
                transform: translateY(-1px);
            }
            [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
                background: linear-gradient(180deg, rgba(201, 234, 228, 0.96) 0%, rgba(183, 223, 216, 0.92) 100%);
                border-color: rgba(11, 16, 21, 0.96);
                box-shadow: 0 12px 24px rgba(0, 0, 0, 0.14);
            }
            [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
                color: #132624;
                font-weight: 600;
            }
            .page-hero {
                margin: 0 0 1.2rem 0;
                padding: 1.2rem 1.3rem;
                border-radius: 24px;
                background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(20,28,39,0.95) 100%);
                border: 1px solid #273244;
                box-shadow: 0 18px 44px rgba(0, 0, 0, 0.24);
            }
            .page-eyebrow, .section-subtitle {
                font-size: 0.85rem;
                color: #8b9bb2;
            }
            .page-title {
                font-size: 2.4rem;
                font-weight: 800;
                color: #f8fafc;
                margin: 0.25rem 0;
            }
            .page-subtitle {
                color: #b6c2d2;
                max-width: 900px;
            }
            .metric-card {
                padding: 1rem 1.05rem;
                border-radius: 20px;
                border: 1px solid #263142;
                background: linear-gradient(180deg, rgba(255,255,255,0.04) 0%, rgba(15,17,22,0.92) 100%);
                box-shadow: 0 16px 34px rgba(0, 0, 0, 0.28);
            }
            .metric-label {
                font-size: 0.8rem;
                text-transform: uppercase;
                letter-spacing: 0.06em;
                color: #8b9bb2;
                margin-bottom: 0.45rem;
            }
            .metric-value {
                font-size: 1.85rem;
                font-weight: 800;
                color: #f8fafc;
            }
            .metric-delta {
                margin-top: 0.35rem;
                color: #b6c2d2;
                font-size: 0.92rem;
            }
            .section-head {
                margin: 1rem 0 0.75rem 0;
            }
            .section-title {
                font-size: 1.2rem;
                font-weight: 700;
                color: #f8fafc;
            }
            .stTabs [data-baseweb="tab-list"] {
                gap: 0.4rem;
                border-bottom: 1px solid #263142;
                padding-bottom: 0.38rem;
            }
            .stTabs {
                margin-top: 0.35rem;
            }
            .stTabs [data-baseweb="tab"] {
                height: auto;
                background: transparent;
                border-radius: 0.85rem 0.85rem 0 0;
                padding: 0.72rem 1.02rem 0.76rem 1.02rem;
                margin: 0;
                color: #a8b5c7;
                font-weight: 600;
                transition: background-color 0.18s ease, color 0.18s ease, box-shadow 0.18s ease;
            }
            .stTabs [data-baseweb="tab"]:hover {
                background: rgba(255,255,255,0.05);
                color: #f8fafc;
            }
            .stTabs [data-baseweb="tab"][aria-selected="true"] {
                background: linear-gradient(180deg, rgba(201, 234, 228, 0.16) 0%, rgba(183, 223, 216, 0.12) 100%);
                color: #ff676c;
                font-weight: 800;
                border: 1px solid rgba(92, 125, 118, 0.42);
                box-shadow: 0 10px 24px rgba(143, 184, 176, 0.1);
                border-bottom: 2px solid rgba(255, 90, 95, 0.72);
            }
            [data-testid="stHorizontalBlock"]:has(.fake-toolbar-anchor) {
                align-items: center;
                margin: 0.2rem 0 0.35rem 0;
            }
            [data-testid="stHorizontalBlock"]:has(.fake-toolbar-anchor) [data-testid="column"] {
                display: flex;
                align-items: center;
            }
            .fake-toolbar-anchor {
                display: block;
                min-height: 1px;
            }
            .fake-toolbar-title {
                font-size: 1.08rem;
                font-weight: 700;
                color: #f8fafc;
                margin: 0;
            }
            [data-testid="stHorizontalBlock"]:has(.fake-toolbar-anchor) button[kind] {
                min-height: 2rem;
                padding: 0.15rem 0.6rem;
                border-radius: 0.65rem;
                border: 1px solid #2c3646;
                background: linear-gradient(180deg, rgba(25, 30, 40, 0.98) 0%, rgba(18, 22, 31, 0.98) 100%);
                color: #f8fafc;
                font-size: 0.76rem;
                font-weight: 700;
                letter-spacing: 0.04em;
                box-shadow: 0 8px 18px rgba(0, 0, 0, 0.18);
            }
            [data-testid="stHorizontalBlock"]:has(.fake-toolbar-anchor) button[kind]:hover {
                border-color: #41506a;
                background: linear-gradient(180deg, rgba(31, 37, 48, 1) 0%, rgba(22, 27, 36, 1) 100%);
            }
            </style>
            """,
            unsafe_allow_html=True,
        )


def save_portfolio(df: pd.DataFrame) -> None:
    # Ulozi aktualni portfolio zpet do CSV.
    columns_to_save = ["ticker", "shares", "buy_price"]

    # Pokud CSV obsahuje i dalsi podrobnosti, zachovame je.
    if "company" in df.columns:
        columns_to_save.insert(1, "company")
    if "yfinance_ticker" in df.columns:
        columns_to_save.insert(2 if "company" in df.columns else 1, "yfinance_ticker")
    if "purchase_date" in df.columns:
        columns_to_save.append("purchase_date")

    df[columns_to_save].to_csv(CSV_PATH, index=False)


def save_watchlist(df: pd.DataFrame) -> None:
    # Ulozi watchlist do jednoducheho CSV souboru.
    columns_to_save = [
        "ticker",
        "company",
        "yfinance_ticker",
        "buy_zone_low",
        "buy_zone_high",
        "buy_plan",
        "sell_target",
        "note_date",
        "note_price",
        "note_text",
    ]
    df[columns_to_save].to_csv(WATCHLIST_PATH, index=False)


def save_analysis(df: pd.DataFrame) -> None:
    # Ulozi aktualni analyzu a plan ke kazdemu tickeru.
    columns_to_save = [
        "ticker",
        "company",
        "avg_buy_price",
        "target_price",
        "invalidation_level",
        "status",
        "conviction",
        "next_action",
        "investment_thesis",
        "buy_plan",
        "sell_plan",
        "risk_notes",
        "last_note",
        "updated_at",
    ]
    df[columns_to_save].to_csv(ANALYSIS_PATH, index=False)


def save_analysis_history(df: pd.DataFrame) -> None:
    # Ulozi historii rozhodnuti do samostatneho CSV.
    columns_to_save = [
        "ticker",
        "decision_date",
        "decision_type",
        "price",
        "plan_text",
        "comment",
    ]
    df[columns_to_save].to_csv(ANALYSIS_HISTORY_PATH, index=False)


def save_long_term_plans(df: pd.DataFrame) -> None:
    # Ulozi dlouhodobe plany.
    columns_to_save = [
        "plan_name",
        "start_period",
        "target_period",
        "start_value",
        "target_value",
        "monthly_contribution",
        "expected_return_pct",
        "plan_notes",
        "asset_notes",
    ]
    df[columns_to_save].to_csv(LONG_TERM_PLANS_PATH, index=False)


def save_long_term_checks(df: pd.DataFrame) -> None:
    # Ulozi jednotlive kontroly planu.
    columns_to_save = [
        "plan_name",
        "period_label",
        "period_date",
        "planned_value",
        "actual_value",
        "deviation",
        "completion_pct",
        "note_plan",
        "note_assets",
        "next_step",
        "source",
        "is_manual_override",
    ]
    df[columns_to_save].to_csv(LONG_TERM_CHECKS_PATH, index=False)


def save_transactions(df: pd.DataFrame) -> None:
    # Ulozi transakce do samostatneho CSV souboru.
    columns_to_save = [
        "date",
        "ticker",
        "company",
        "transaction_type",
        "quantity",
        "price",
        "currency",
        "buy_fee",
        "sell_fee",
        "fx_fee",
        "tax_fx_rate",
        "tax_currency",
        "broker",
        "note",
    ]
    for column in columns_to_save:
        if column not in df.columns:
            df[column] = ""
    df[columns_to_save].to_csv(TRANSACTIONS_PATH, index=False)


def aggregate_portfolio(df: pd.DataFrame) -> pd.DataFrame:
    # Slouci vice nakupu stejneho tickeru do jedne pozice.
    if len(df) == 0:
        return df.copy()

    rows = []
    for (ticker, yfinance_ticker), group in df.groupby(["ticker", "yfinance_ticker"], dropna=False):
        shares_sum = group["shares"].sum()
        if shares_sum == 0:
            continue

        company_value = None
        if "company" in group.columns:
            non_empty_company = group["company"].dropna()
            if len(non_empty_company) > 0:
                company_value = non_empty_company.iloc[0]

        rows.append(
            {
                "ticker": ticker,
                "company": company_value,
                "yfinance_ticker": yfinance_ticker,
                "shares": shares_sum,
                "buy_price": (group["shares"] * group["buy_price"]).sum() / shares_sum,
            }
        )

    return pd.DataFrame(rows)


def get_price(ticker: str) -> float:
    # Stahne posledni zaviraci cenu akcie.
    history = yf.Ticker(ticker).history(period="1d")
    return float(history["Close"].iloc[-1])


@st.cache_data(ttl=3600)
def get_fx_rate_to_usd(currency: str) -> float:
    # Vrati jednoduchy kurz do USD.
    if currency == "USD":
        return 1.0
    if currency == "EUR":
        history = yf.Ticker("EURUSD=X").history(period="5d")
        return float(history["Close"].iloc[-1])
    if currency == "CZK":
        history = yf.Ticker("USDCZK=X").history(period="5d")
        usdczk = float(history["Close"].iloc[-1])
        return 1 / usdczk
    return 1.0


@st.cache_data(ttl=3600)
def get_historical_fx_rate_to_usd(currency: str, date_value) -> float:
    # Vrati historicky kurz do USD k danemu datu, fallback je aktualni kurz.
    if currency == "USD":
        return 1.0

    target_date = pd.to_datetime(date_value, errors="coerce")
    if pd.isna(target_date):
        return get_fx_rate_to_usd(currency)
    target_date = target_date.normalize()

    if currency == "EUR":
        fx_df = get_price_history("EURUSD=X", "max")
        if fx_df.empty:
            return get_fx_rate_to_usd(currency)

        fx_df["Date"] = pd.to_datetime(fx_df["Date"], errors="coerce").dt.normalize()
        historical = fx_df[fx_df["Date"] <= target_date]
        if len(historical) == 0:
            return get_fx_rate_to_usd(currency)
        return float(historical["close"].iloc[-1])

    if currency == "CZK":
        fx_df = get_price_history("USDCZK=X", "max")
        if fx_df.empty:
            return get_fx_rate_to_usd(currency)

        fx_df["Date"] = pd.to_datetime(fx_df["Date"], errors="coerce").dt.normalize()
        historical = fx_df[fx_df["Date"] <= target_date]
        if len(historical) == 0:
            return get_fx_rate_to_usd(currency)
        usdczk = float(historical["close"].iloc[-1])
        return 1 / usdczk if usdczk else get_fx_rate_to_usd(currency)

    return get_fx_rate_to_usd(currency)


@st.cache_data(ttl=3600)
def convert_from_usd(amount: float, target_currency: str) -> float:
    # Prevede castku z USD do zvolene meny.
    if pd.isna(amount) or amount is None:
        return None
    if target_currency == "USD":
        return float(amount)
    if target_currency == "EUR":
        return float(amount) / get_fx_rate_to_usd("EUR")
    if target_currency == "CZK":
        return float(amount) / get_fx_rate_to_usd("CZK")
    return float(amount)


@st.cache_data(ttl=3600)
def get_ticker_details(ticker: str) -> dict:
    # Nacte detailni data o akcii pro tabulku.
    stock = yf.Ticker(ticker)
    history = stock.history(period="1y")
    info = stock.info

    if history.empty:
        raise ValueError(f"Pro ticker {ticker} se nepodarilo nacist data.")

    regular_market_price = pd.to_numeric(info.get("regularMarketPrice"), errors="coerce")
    regular_market_previous_close = pd.to_numeric(info.get("regularMarketPreviousClose"), errors="coerce")
    history_latest_close = float(history["Close"].iloc[-1])
    history_previous_close = float(history["Close"].iloc[-2]) if len(history) > 1 else history_latest_close
    use_live_us_session = is_us_regular_market_open_now()

    if use_live_us_session and pd.notna(regular_market_price) and regular_market_price:
        current_price = float(regular_market_price)
        previous_close = (
            float(regular_market_previous_close)
            if pd.notna(regular_market_previous_close) and regular_market_previous_close
            else history_previous_close
        )
    else:
        current_price = history_latest_close
        previous_close = history_previous_close

    daily_change = current_price - previous_close
    daily_change_pct = (daily_change / previous_close * 100) if previous_close else 0.0
    premarket_reference_close = (
        float(regular_market_previous_close)
        if pd.notna(regular_market_previous_close) and regular_market_previous_close
        else history_previous_close
    )
    premarket_price_raw = pd.to_numeric(info.get("preMarketPrice"), errors="coerce")
    premarket_price = float(premarket_price_raw) if pd.notna(premarket_price_raw) and float(premarket_price_raw) > 0 else None
    premarket_change_pct = (
        ((premarket_price - premarket_reference_close) / premarket_reference_close * 100)
        if premarket_price is not None and premarket_reference_close
        else None
    )

    currency = info.get("currency", "USD")
    fx_rate = get_fx_rate_to_usd(currency)
    current_price_usd = current_price * fx_rate
    daily_change_usd = daily_change * fx_rate

    eps = info.get("trailingEps")
    pe = info.get("trailingPE")
    beta = info.get("beta")
    market_cap = info.get("marketCap")

    if pe:
        earnings_yield = 100 / pe
    elif eps:
        earnings_yield = (eps / current_price) * 100
    else:
        earnings_yield = None

    return {
        "price": current_price,
        "daily_change_pct": daily_change_pct,
        "daily_change_usd": daily_change_usd,
        "currency": currency,
        "current_price_usd": current_price_usd,
        "one_year": history["Close"].tail(60).round(2).tolist(),
        "pe": pe,
        "eps": eps,
        "earnings_yield": earnings_yield,
        "market_cap": market_cap,
        "beta": beta,
        "company_live": info.get("shortName"),
        "premarket_price": premarket_price,
        "premarket_change_pct": premarket_change_pct,
    }


@st.cache_data(ttl=3600)
def get_price_history(ticker: str, period: str) -> pd.DataFrame:
    # Nacte historicke zaviraci ceny pro zvolene obdobi.
    history = yf.Ticker(ticker).history(period=period)
    if history.empty:
        return pd.DataFrame()

    history = history.reset_index()[["Date", "Close"]].copy()
    history["Date"] = pd.to_datetime(history["Date"]).dt.tz_localize(None)
    history = history.rename(columns={"Close": "close"})
    return history


def convert_history_to_usd(history_df: pd.DataFrame, currency: str) -> pd.DataFrame:
    # Prevede historii do USD jen pro meny, ktere v aplikaci pouzivame.
    if history_df.empty or currency == "USD":
        return history_df

    if currency == "EUR":
        fx_df = get_price_history("EURUSD=X", "max")
        if fx_df.empty:
            return pd.DataFrame()

        fx_df = fx_df.rename(columns={"close": "fx_close"})
        merged = history_df.merge(fx_df, on="Date", how="left")
        merged["fx_close"] = merged["fx_close"].ffill().bfill()
        merged["close"] = merged["close"] * merged["fx_close"]
        return merged[["Date", "close"]]

    if currency == "CZK":
        fx_df = get_price_history("USDCZK=X", "max")
        if fx_df.empty:
            return pd.DataFrame()

        fx_df = fx_df.rename(columns={"close": "fx_close"})
        merged = history_df.merge(fx_df, on="Date", how="left")
        merged["fx_close"] = merged["fx_close"].ffill().bfill()
        merged["close"] = merged["close"] / merged["fx_close"]
        return merged[["Date", "close"]]

    return history_df


def build_portfolio_history(raw_df: pd.DataFrame, period: str) -> tuple[pd.DataFrame, list[str]]:
    # Spocita jednoduchy historicky vyvoj portfolia z jednotlivych nakupu.
    if len(raw_df) == 0:
        return pd.DataFrame(), []

    all_series = []
    missing_tickers = []

    for row in raw_df.itertuples(index=False):
        history_df = get_price_history(row.yfinance_ticker, period)
        if history_df.empty:
            missing_tickers.append(row.ticker)
            continue

        try:
            details = get_ticker_details(row.yfinance_ticker)
            currency = details["currency"]
        except Exception:
            currency = "USD"

        history_df = convert_history_to_usd(history_df, currency)
        if history_df.empty:
            missing_tickers.append(row.ticker)
            continue

        purchase_date = pd.to_datetime(row.purchase_date, errors="coerce")
        if pd.notna(purchase_date):
            history_df = history_df[history_df["Date"] >= purchase_date]

        if history_df.empty:
            continue

        position_series = history_df.copy()
        position_series["value"] = position_series["close"] * float(row.shares)
        position_series = position_series[["Date", "value"]].rename(columns={"value": row.ticker})
        all_series.append(position_series.set_index("Date"))

    if not all_series:
        return pd.DataFrame(), missing_tickers

    combined = pd.concat(all_series, axis=1).sort_index().ffill().fillna(0.0)
    combined["portfolio_value"] = combined.sum(axis=1)
    return combined.reset_index()[["Date", "portfolio_value"]], sorted(set(missing_tickers))


def get_open_transaction_tickers(transactions_df: pd.DataFrame) -> list[str]:
    # Vrati tickery, kde po zapocteni buy/sell zustava otevrena pozice.
    if len(transactions_df) == 0:
        return []

    working_df = transactions_df.copy()
    working_df["ticker"] = working_df["ticker"].astype(str).str.upper().str.strip()
    working_df["transaction_type"] = working_df["transaction_type"].astype(str).str.lower().str.strip()
    working_df["quantity"] = pd.to_numeric(working_df["quantity"], errors="coerce").fillna(0.0)
    working_df = working_df[working_df["transaction_type"].isin(["buy", "sell"])]
    if len(working_df) == 0:
        return []

    working_df["signed_quantity"] = working_df.apply(
        lambda row: row["quantity"] if row["transaction_type"] == "buy" else -row["quantity"],
        axis=1,
    )
    summary = working_df.groupby("ticker", as_index=False)["signed_quantity"].sum()
    return summary[summary["signed_quantity"] > 0]["ticker"].tolist()


def build_open_lot_transactions(
    transactions_df: pd.DataFrame,
    include_tickers: list[str] | None = None,
) -> pd.DataFrame:
    # Vrati synteticke buy radky pouze pro loty, ktere jsou stale otevrene.
    if len(transactions_df) == 0:
        return pd.DataFrame(columns=transactions_df.columns)

    working_df = transactions_df.copy()
    working_df["ticker"] = working_df["ticker"].astype(str).str.upper().str.strip()
    working_df["transaction_type"] = working_df["transaction_type"].astype(str).str.lower().str.strip()
    working_df["quantity"] = pd.to_numeric(working_df["quantity"], errors="coerce").fillna(0.0)
    working_df["buy_fee"] = pd.to_numeric(working_df["buy_fee"], errors="coerce").fillna(0.0)
    working_df["sell_fee"] = pd.to_numeric(working_df["sell_fee"], errors="coerce").fillna(0.0)
    working_df["fx_fee"] = pd.to_numeric(working_df["fx_fee"], errors="coerce").fillna(0.0)
    working_df["date_sort"] = pd.to_datetime(working_df["date"], errors="coerce")
    working_df = working_df.dropna(subset=["date_sort"])
    working_df = working_df[working_df["transaction_type"].isin(["buy", "sell"])]

    if include_tickers is not None:
        allowed_tickers = {str(ticker).upper().strip() for ticker in include_tickers}
        working_df = working_df[working_df["ticker"].isin(allowed_tickers)]

    if len(working_df) == 0:
        return pd.DataFrame(columns=transactions_df.columns)

    open_lot_rows = []
    for ticker in sorted(working_df["ticker"].unique().tolist()):
        ticker_df = working_df[working_df["ticker"] == ticker].sort_values(["date_sort"]).copy()
        open_lots = []

        for row in ticker_df.itertuples(index=False):
            if row.transaction_type == "buy":
                row_dict = row._asdict()
                row_dict["remaining_quantity"] = float(row.quantity)
                open_lots.append(row_dict)
                continue

            remaining_sell = float(row.quantity)
            while remaining_sell > 0 and open_lots:
                first_lot = open_lots[0]
                available_quantity = float(first_lot["remaining_quantity"])
                matched_quantity = min(available_quantity, remaining_sell)
                first_lot["remaining_quantity"] = available_quantity - matched_quantity
                remaining_sell -= matched_quantity
                if first_lot["remaining_quantity"] <= 1e-9:
                    open_lots.pop(0)

        for lot in open_lots:
            original_quantity = float(lot["quantity"])
            remaining_quantity = float(lot["remaining_quantity"])
            if remaining_quantity <= 1e-9 or original_quantity <= 0:
                continue

            ratio = remaining_quantity / original_quantity
            cleaned_lot = {column: lot.get(column) for column in transactions_df.columns}
            cleaned_lot["transaction_type"] = "buy"
            cleaned_lot["quantity"] = remaining_quantity
            cleaned_lot["buy_fee"] = float(lot.get("buy_fee", 0.0)) * ratio
            cleaned_lot["fx_fee"] = float(lot.get("fx_fee", 0.0)) * ratio
            cleaned_lot["sell_fee"] = 0.0
            open_lot_rows.append(cleaned_lot)

    if not open_lot_rows:
        return pd.DataFrame(columns=transactions_df.columns)

    return pd.DataFrame(open_lot_rows)


def filter_history_by_period(history_df: pd.DataFrame, period: str) -> pd.DataFrame:
    # Oreze historii na zvolene obdobi pri zachovani poslednich dostupnych obchodnich dni.
    if history_df.empty or period == "max":
        return history_df.copy()

    max_date = pd.to_datetime(history_df["Date"], errors="coerce").max()
    if pd.isna(max_date):
        return history_df.copy()

    if period == "1mo":
        start_date = max_date - pd.DateOffset(months=1)
    elif period == "3mo":
        start_date = max_date - pd.DateOffset(months=3)
    elif period == "1y":
        start_date = max_date - pd.DateOffset(years=1)
    else:
        return history_df.copy()

    filtered = history_df[pd.to_datetime(history_df["Date"], errors="coerce") >= start_date].copy()
    return filtered.reset_index(drop=True)


def build_transaction_portfolio_history(
    transactions_df: pd.DataFrame,
    ticker_map: dict,
    period: str = "max",
    include_tickers: list[str] | None = None,
) -> tuple[pd.DataFrame, list[str]]:
    # Presnejsi historie portfolia podle transakci buy/sell pro vybrane tickery.
    if len(transactions_df) == 0:
        return pd.DataFrame(), []

    working_df = transactions_df.copy()
    working_df["ticker"] = working_df["ticker"].astype(str).str.upper().str.strip()
    working_df["transaction_type"] = working_df["transaction_type"].astype(str).str.lower().str.strip()
    working_df["quantity"] = pd.to_numeric(working_df["quantity"], errors="coerce").fillna(0.0)
    working_df["date_sort"] = pd.to_datetime(working_df["date"], errors="coerce").dt.normalize()
    working_df = working_df[working_df["transaction_type"].isin(["buy", "sell"])]
    working_df = working_df[working_df["ticker"] != ""]
    working_df = working_df.dropna(subset=["date_sort"])

    if include_tickers is not None:
        allowed_tickers = {str(ticker).upper().strip() for ticker in include_tickers}
        working_df = working_df[working_df["ticker"].isin(allowed_tickers)]

    if len(working_df) == 0:
        return pd.DataFrame(), []

    all_series = []
    missing_tickers = []
    for ticker in sorted(working_df["ticker"].unique().tolist()):
        ticker_transactions = working_df[working_df["ticker"] == ticker].copy()
        first_transaction_date = pd.to_datetime(ticker_transactions["date_sort"], errors="coerce").min()
        ticker_transactions["quantity_delta"] = ticker_transactions.apply(
            lambda row: row["quantity"] if row["transaction_type"] == "buy" else -row["quantity"],
            axis=1,
        )
        quantity_changes = (
            ticker_transactions.groupby("date_sort", as_index=False)["quantity_delta"]
            .sum()
            .rename(columns={"date_sort": "Date"})
        )

        yfinance_ticker = ticker_map.get(ticker, {}).get("yfinance_ticker", ticker)
        history_df = get_price_history(yfinance_ticker, "max")
        if history_df.empty:
            missing_tickers.append(ticker)
            continue

        currency_candidates = (
            ticker_transactions["currency"]
            .dropna()
            .astype(str)
            .str.upper()
            .replace(["", "NAN", "NONE"], pd.NA)
            .dropna()
        )
        currency = currency_candidates.iloc[0] if len(currency_candidates) > 0 else "USD"
        history_df = convert_history_to_usd(history_df, currency)
        if history_df.empty:
            missing_tickers.append(ticker)
            continue

        if pd.notna(first_transaction_date):
            history_df = history_df[history_df["Date"] >= first_transaction_date]
        if history_df.empty:
            missing_tickers.append(ticker)
            continue

        ticker_history = history_df.merge(quantity_changes, on="Date", how="outer").sort_values("Date")
        ticker_history["quantity_delta"] = ticker_history["quantity_delta"].fillna(0.0)
        ticker_history["quantity"] = ticker_history["quantity_delta"].cumsum()
        ticker_history["quantity"] = ticker_history["quantity"].ffill().fillna(0.0)
        ticker_history = ticker_history[ticker_history["close"].notna()].copy()
        ticker_history["value"] = ticker_history["close"] * ticker_history["quantity"]
        ticker_history = ticker_history[["Date", "value"]].rename(columns={"value": ticker})
        all_series.append(ticker_history.set_index("Date"))

    if not all_series:
        return pd.DataFrame(), sorted(set(missing_tickers))

    combined = pd.concat(all_series, axis=1).sort_index().ffill().fillna(0.0)
    combined["portfolio_value"] = combined.sum(axis=1)
    positive_mask = combined["portfolio_value"] > 0
    if positive_mask.any():
        first_positive_date = combined.index[positive_mask][0]
        combined = combined[combined.index >= first_positive_date]
    combined = combined.reset_index()[["Date", "portfolio_value"]]
    combined = filter_history_by_period(combined, period)
    return combined, sorted(set(missing_tickers))


def build_benchmark_history(period: str, benchmark_ticker: str) -> pd.DataFrame:
    # Nacte historii benchmarku a vrati ji v USD.
    history_df = get_price_history(benchmark_ticker, period)
    if history_df.empty:
        return pd.DataFrame()

    currency = "USD"
    try:
        currency = get_ticker_details(benchmark_ticker)["currency"]
    except Exception:
        pass

    history_df = convert_history_to_usd(history_df, currency)
    if history_df.empty:
        return pd.DataFrame()

    return history_df.rename(columns={"close": "benchmark_value"})


def calculate_performance(series: pd.Series) -> tuple[float | None, float | None]:
    # Vrati absolutni a procentni vykonnost mezi prvni a posledni hodnotou.
    cleaned = series.dropna()
    if len(cleaned) < 2:
        return None, None

    start_value = float(cleaned.iloc[0])
    end_value = float(cleaned.iloc[-1])
    absolute = end_value - start_value
    percent = (absolute / start_value * 100) if start_value else None
    return absolute, percent


def normalize_to_percent(series: pd.Series) -> pd.Series:
    # Prevede radu na procentni vykonnost od prvni dostupne hodnoty.
    cleaned = series.dropna()
    if len(cleaned) < 2:
        return pd.Series(dtype=float)

    start_value = float(cleaned.iloc[0])
    if start_value == 0:
        return pd.Series(dtype=float)

    return ((cleaned / start_value) - 1) * 100


def get_latest_history_change_pct(history_df: pd.DataFrame) -> float | None:
    # Vrati procentni zmenu mezi poslednimi dvema dostupnymi body historie.
    if history_df.empty or "close" not in history_df.columns:
        return None

    cleaned = history_df.dropna(subset=["close"]).copy()
    if len(cleaned) < 2:
        return None

    previous_close = safe_float(cleaned["close"].iloc[-2])
    current_close = safe_float(cleaned["close"].iloc[-1])
    if previous_close in (None, 0) or current_close is None:
        return None
    return ((current_close - previous_close) / previous_close) * 100


def calculate_performance_from_date(history_df: pd.DataFrame, start_date: pd.Timestamp) -> tuple[float | None, float | None]:
    # Spocte vykonnost od prvni dostupne hodnoty po zadanem datu.
    if history_df.empty:
        return None, None

    filtered = history_df[history_df["Date"] >= start_date].copy()
    if len(filtered) < 2:
        return None, None

    return calculate_performance(filtered["portfolio_value"])


def calculate_performance_between_dates(history_df: pd.DataFrame, start_date: pd.Timestamp, end_date: pd.Timestamp) -> tuple[float | None, float | None]:
    # Spocte vykonnost mezi dvema daty vcetne.
    if history_df.empty:
        return None, None

    filtered = history_df[(history_df["Date"] >= start_date) & (history_df["Date"] <= end_date)].copy()
    if len(filtered) < 2:
        return None, None

    return calculate_performance(filtered["portfolio_value"])


def calculate_series_performance_from_date(history_df: pd.DataFrame, value_column: str, start_date: pd.Timestamp) -> tuple[float | None, float | None]:
    # Obecna varianta vykonnosti od data pro libovolny sloupec.
    if history_df.empty or value_column not in history_df.columns:
        return None, None

    filtered = history_df[history_df["Date"] >= start_date].copy()
    if len(filtered) < 2:
        return None, None

    return calculate_performance(filtered[value_column])


def calculate_series_performance_between_dates(history_df: pd.DataFrame, value_column: str, start_date: pd.Timestamp, end_date: pd.Timestamp) -> tuple[float | None, float | None]:
    # Obecna varianta vykonnosti mezi daty pro libovolny sloupec.
    if history_df.empty or value_column not in history_df.columns:
        return None, None

    filtered = history_df[(history_df["Date"] >= start_date) & (history_df["Date"] <= end_date)].copy()
    if len(filtered) < 2:
        return None, None

    return calculate_performance(filtered[value_column])


def get_period_start_value(history_df: pd.DataFrame, start_date: pd.Timestamp, end_date: pd.Timestamp | None = None) -> float | None:
    # Vrati prvni hodnotu portfolia v danem obdobi.
    if history_df.empty or "portfolio_value" not in history_df.columns:
        return None

    filtered = history_df[history_df["Date"] >= start_date].copy()
    if end_date is not None:
        filtered = filtered[filtered["Date"] <= end_date]
    if filtered.empty:
        return None
    return safe_float(filtered["portfolio_value"].iloc[0])


def calculate_realized_result_between_dates(closed_positions_df: pd.DataFrame, start_date: pd.Timestamp, end_date: pd.Timestamp | None = None) -> float:
    # Secte realizovany vysledek za zvolene obdobi.
    if closed_positions_df.empty or "Datum prodeje" not in closed_positions_df.columns:
        return 0.0

    closed_df = closed_positions_df.copy()
    closed_df["sale_date_sort"] = pd.to_datetime(closed_df["Datum prodeje"], errors="coerce")
    filtered = closed_df[closed_df["sale_date_sort"] >= start_date]
    if end_date is not None:
        filtered = filtered[filtered["sale_date_sort"] <= end_date]
    if filtered.empty:
        return 0.0
    return float(filtered["Realizovany zisk / ztrata USD"].sum())


def calculate_combined_performance_pct(
    clean_performance_pct: float | None,
    realized_result_usd: float,
    start_value_usd: float | None,
) -> float | None:
    # Priblizne spoji cisty vykon otevreneho portfolia s realizovanym vysledkem za stejne obdobi.
    if start_value_usd in (None, 0):
        return clean_performance_pct

    clean_pct = clean_performance_pct if clean_performance_pct is not None else 0.0
    realized_pct = (realized_result_usd / start_value_usd) * 100
    return clean_pct + realized_pct


def calculate_clean_performance_value(
    clean_performance_pct: float | None,
    start_value_usd: float | None,
) -> float | None:
    # Prevede cisty vykon z procent i do penezni hodnoty za stejne obdobi.
    if clean_performance_pct is None or start_value_usd in (None, 0):
        return None
    return start_value_usd * (clean_performance_pct / 100)


def calculate_combined_performance_value(
    clean_performance_value_usd: float | None,
    realized_result_usd: float,
) -> float | None:
    # Penezni varianta cisteho vykonu vcetne uzavrenych pozic.
    if clean_performance_value_usd is None:
        return realized_result_usd if realized_result_usd != 0 else None
    return clean_performance_value_usd + realized_result_usd


def build_portfolio_cash_flows(raw_df: pd.DataFrame) -> pd.DataFrame:
    # Sestavi externi cash flow podle trzni hodnoty pozice v den zarazeni do historie.
    if len(raw_df) == 0 or "purchase_date" not in raw_df.columns:
        return pd.DataFrame(columns=["Date", "net_flow_usd"])

    cash_flow_rows = []
    for row in raw_df.itertuples(index=False):
        purchase_date = pd.to_datetime(row.purchase_date, errors="coerce")
        if pd.isna(purchase_date):
            continue

        history_df = get_price_history(row.yfinance_ticker, "max")
        if history_df.empty:
            continue

        currency = "USD"
        try:
            currency = get_ticker_details(row.yfinance_ticker)["currency"]
        except Exception:
            pass

        history_df = convert_history_to_usd(history_df, currency)
        if history_df.empty:
            continue

        position_history = history_df[history_df["Date"] >= purchase_date]
        if position_history.empty:
            continue

        cash_flow_rows.append(
            {
                "Date": pd.to_datetime(position_history["Date"].iloc[0]).normalize(),
                "net_flow_usd": float(position_history["close"].iloc[0]) * float(row.shares),
            }
        )

    if not cash_flow_rows:
        return pd.DataFrame(columns=["Date", "net_flow_usd"])

    cash_flows_df = pd.DataFrame(cash_flow_rows)
    return cash_flows_df.groupby("Date", as_index=False)["net_flow_usd"].sum()


def build_transaction_cash_flows(
    transactions_df: pd.DataFrame,
    include_tickers: list[str] | None = None,
) -> pd.DataFrame:
    # Cash flow vrstva z transakci pro presnejsi vypocet cisteho vykonu otevrenych pozic.
    if len(transactions_df) == 0:
        return pd.DataFrame(columns=["Date", "net_flow_usd"])

    working_df = transactions_df.copy()
    working_df["ticker"] = working_df["ticker"].astype(str).str.upper().str.strip()
    working_df["transaction_type"] = working_df["transaction_type"].astype(str).str.lower().str.strip()
    working_df["date_sort"] = pd.to_datetime(working_df["date"], errors="coerce").dt.normalize()
    working_df["quantity"] = pd.to_numeric(working_df["quantity"], errors="coerce").fillna(0.0)
    working_df["price"] = pd.to_numeric(working_df["price"], errors="coerce").fillna(0.0)
    working_df["buy_fee"] = pd.to_numeric(working_df["buy_fee"], errors="coerce").fillna(0.0)
    working_df["sell_fee"] = pd.to_numeric(working_df["sell_fee"], errors="coerce").fillna(0.0)
    working_df["fx_fee"] = pd.to_numeric(working_df["fx_fee"], errors="coerce").fillna(0.0)
    working_df = working_df.dropna(subset=["date_sort"])

    if include_tickers is not None:
        allowed_tickers = {str(ticker).upper().strip() for ticker in include_tickers}
        ticker_related_mask = working_df["ticker"].isin(allowed_tickers)
        cash_like_mask = working_df["transaction_type"].isin(["fee"])
        working_df = working_df[ticker_related_mask | cash_like_mask]

    flow_rows = []
    for row in working_df.itertuples(index=False):
        currency = str(row.currency).upper().strip() if pd.notna(row.currency) and str(row.currency).strip() else "USD"
        fx_rate = get_historical_fx_rate_to_usd(currency, row.date_sort)
        gross_amount_usd = float(row.quantity) * float(row.price) * fx_rate
        buy_fee_usd = float(row.buy_fee) * fx_rate
        sell_fee_usd = float(row.sell_fee) * fx_rate
        fx_fee_usd = float(row.fx_fee) * fx_rate
        transaction_type = str(row.transaction_type).lower().strip()

        net_flow_usd = 0.0
        if transaction_type == "buy":
            net_flow_usd = gross_amount_usd + buy_fee_usd + fx_fee_usd
        elif transaction_type == "sell":
            net_flow_usd = -(gross_amount_usd - sell_fee_usd - fx_fee_usd)
        elif transaction_type == "dividend":
            net_flow_usd = -(gross_amount_usd - fx_fee_usd)
        elif transaction_type == "fee":
            net_flow_usd = float(max(gross_amount_usd, buy_fee_usd + sell_fee_usd + fx_fee_usd))
        else:
            continue

        flow_rows.append({"Date": row.date_sort, "net_flow_usd": net_flow_usd})

    if not flow_rows:
        return pd.DataFrame(columns=["Date", "net_flow_usd"])

    cash_flows_df = pd.DataFrame(flow_rows)
    return cash_flows_df.groupby("Date", as_index=False)["net_flow_usd"].sum()


def align_cash_flows_to_history_dates(cash_flows_df: pd.DataFrame, history_df: pd.DataFrame) -> pd.DataFrame:
    # Zarovna cash flow z neobchodnich dni na nejblizsi dalsi obchodni den v historii.
    if cash_flows_df.empty or history_df.empty:
        return cash_flows_df.copy()

    aligned_flows = cash_flows_df.copy()
    history_dates = pd.to_datetime(history_df["Date"], errors="coerce").dropna().sort_values().drop_duplicates().tolist()
    if not history_dates:
        return aligned_flows

    mapped_dates = []
    for flow_date in pd.to_datetime(aligned_flows["Date"], errors="coerce").dt.normalize():
        if pd.isna(flow_date):
            mapped_dates.append(pd.NaT)
            continue

        mapped_date = next((history_date for history_date in history_dates if history_date >= flow_date), None)
        if mapped_date is None:
            mapped_date = history_dates[-1]
        mapped_dates.append(mapped_date)

    aligned_flows["Date"] = mapped_dates
    aligned_flows = aligned_flows.dropna(subset=["Date"])
    return aligned_flows.groupby("Date", as_index=False)["net_flow_usd"].sum()


def build_account_clean_performance_history(
    history_df: pd.DataFrame,
    transactions_df: pd.DataFrame,
    include_tickers: list[str] | None = None,
) -> pd.DataFrame:
    # Synteticka account-equity krivka: drzi vykon prodanych aktiv v cashi bez schodu z realizace.
    if history_df.empty:
        return pd.DataFrame()

    working_df = transactions_df.copy()
    if len(working_df) == 0:
        return pd.DataFrame()

    working_df["ticker"] = working_df["ticker"].astype(str).str.upper().str.strip()
    working_df["transaction_type"] = working_df["transaction_type"].astype(str).str.lower().str.strip()
    working_df["date_sort"] = pd.to_datetime(working_df["date"], errors="coerce").dt.normalize()
    working_df["quantity"] = pd.to_numeric(working_df["quantity"], errors="coerce").fillna(0.0)
    working_df["price"] = pd.to_numeric(working_df["price"], errors="coerce").fillna(0.0)
    working_df["buy_fee"] = pd.to_numeric(working_df["buy_fee"], errors="coerce").fillna(0.0)
    working_df["sell_fee"] = pd.to_numeric(working_df["sell_fee"], errors="coerce").fillna(0.0)
    working_df["fx_fee"] = pd.to_numeric(working_df["fx_fee"], errors="coerce").fillna(0.0)
    working_df = working_df.dropna(subset=["date_sort"])

    if include_tickers is not None:
        allowed_tickers = {str(ticker).upper().strip() for ticker in include_tickers}
        ticker_related_mask = working_df["ticker"].isin(allowed_tickers)
        cash_like_mask = working_df["transaction_type"].isin(["fee", "dividend"])
        working_df = working_df[ticker_related_mask | cash_like_mask]

    if len(working_df) == 0:
        return pd.DataFrame()

    cash_change_rows = []
    for row in working_df.itertuples(index=False):
        currency = str(row.currency).upper().strip() if pd.notna(row.currency) and str(row.currency).strip() else "USD"
        fx_rate = get_historical_fx_rate_to_usd(currency, row.date_sort)
        gross_amount_usd = float(row.quantity) * float(row.price) * fx_rate
        buy_fee_usd = float(row.buy_fee) * fx_rate
        sell_fee_usd = float(row.sell_fee) * fx_rate
        fx_fee_usd = float(row.fx_fee) * fx_rate
        transaction_type = str(row.transaction_type).lower().strip()

        cash_change_usd = 0.0
        if transaction_type == "buy":
            cash_change_usd = -(gross_amount_usd + buy_fee_usd + fx_fee_usd)
        elif transaction_type == "sell":
            cash_change_usd = gross_amount_usd - sell_fee_usd - fx_fee_usd
        elif transaction_type == "dividend":
            cash_change_usd = gross_amount_usd - fx_fee_usd
        elif transaction_type == "fee":
            cash_change_usd = -float(max(gross_amount_usd, buy_fee_usd + sell_fee_usd + fx_fee_usd))
        else:
            continue

        cash_change_rows.append({"Date": row.date_sort, "cash_change_usd": cash_change_usd})

    if not cash_change_rows:
        return pd.DataFrame()

    cash_change_df = pd.DataFrame(cash_change_rows)
    cash_change_df = cash_change_df.groupby("Date", as_index=False)["cash_change_usd"].sum()
    cash_change_df = align_cash_flows_to_history_dates(
        cash_change_df.rename(columns={"cash_change_usd": "net_flow_usd"}),
        history_df,
    ).rename(columns={"net_flow_usd": "cash_change_usd"})

    account_df = history_df.copy()
    account_df["Date"] = pd.to_datetime(account_df["Date"], errors="coerce").dt.normalize()
    account_df = account_df.merge(cash_change_df, on="Date", how="left")
    account_df["cash_change_usd"] = account_df["cash_change_usd"].fillna(0.0)

    cash_balance = 0.0
    external_flows = []
    cash_balances = []
    for row in account_df.itertuples(index=False):
        day_cash_change = float(row.cash_change_usd)
        external_flow = 0.0
        if cash_balance + day_cash_change < 0:
            external_flow = -(cash_balance + day_cash_change)
        cash_balance = cash_balance + day_cash_change + external_flow
        external_flows.append(external_flow)
        cash_balances.append(cash_balance)

    account_df["external_flow_usd"] = external_flows
    account_df["cash_balance_usd"] = cash_balances
    account_df["equity_value"] = account_df["portfolio_value"] + account_df["cash_balance_usd"]
    account_df["previous_equity_value"] = account_df["equity_value"].shift(1)
    account_df["period_clean_return"] = 0.0

    valid_mask = account_df["previous_equity_value"] > 0
    account_df.loc[valid_mask, "period_clean_return"] = (
        (
            account_df.loc[valid_mask, "equity_value"]
            - account_df.loc[valid_mask, "previous_equity_value"]
            - account_df.loc[valid_mask, "external_flow_usd"]
        )
        / account_df.loc[valid_mask, "previous_equity_value"]
    )
    account_df["clean_growth_factor"] = (1 + account_df["period_clean_return"].fillna(0.0)).cumprod()
    account_df["clean_return_pct"] = (account_df["clean_growth_factor"] - 1) * 100
    return account_df


def build_clean_performance_history_from_transactions(
    history_df: pd.DataFrame,
    transactions_df: pd.DataFrame,
    include_tickers: list[str] | None = None,
) -> pd.DataFrame:
    # Presnejsi cisty vykon nad historii z transakci a cash flow.
    if history_df.empty:
        return pd.DataFrame()

    clean_df = history_df.copy()
    clean_df["Date"] = pd.to_datetime(clean_df["Date"]).dt.normalize()
    cash_flows_df = build_transaction_cash_flows(transactions_df, include_tickers)
    cash_flows_df = align_cash_flows_to_history_dates(cash_flows_df, clean_df)
    clean_df = clean_df.merge(cash_flows_df, on="Date", how="left")
    clean_df["net_flow_usd"] = clean_df["net_flow_usd"].fillna(0.0)
    clean_df["previous_value"] = clean_df["portfolio_value"].shift(1)
    clean_df["period_clean_return"] = 0.0

    valid_mask = clean_df["previous_value"] > 0
    clean_df.loc[valid_mask, "period_clean_return"] = (
        (clean_df.loc[valid_mask, "portfolio_value"] - clean_df.loc[valid_mask, "previous_value"] - clean_df.loc[valid_mask, "net_flow_usd"])
        / clean_df.loc[valid_mask, "previous_value"]
    )
    clean_df["clean_growth_factor"] = (1 + clean_df["period_clean_return"].fillna(0.0)).cumprod()
    clean_df["clean_return_pct"] = (clean_df["clean_growth_factor"] - 1) * 100
    return clean_df


def build_clean_with_closed_history(
    clean_history_df: pd.DataFrame,
    closed_positions_df: pd.DataFrame,
) -> pd.DataFrame:
    # Prida ke krivce aktualniho portfolia i realizovany vysledek uzavrenych pozic.
    if clean_history_df.empty:
        return pd.DataFrame()

    combined_df = clean_history_df.copy()
    combined_df["Date"] = pd.to_datetime(combined_df["Date"], errors="coerce").dt.normalize()
    combined_df["clean_with_closed_pct"] = combined_df["clean_return_pct"]

    if closed_positions_df.empty or "Datum prodeje" not in closed_positions_df.columns:
        return combined_df

    closed_df = closed_positions_df.copy()
    closed_df["Datum prodeje"] = pd.to_datetime(closed_df["Datum prodeje"], errors="coerce").dt.normalize()
    closed_df["Realizovany zisk / ztrata USD"] = pd.to_numeric(
        closed_df.get("Realizovany zisk / ztrata USD"),
        errors="coerce",
    ).fillna(0.0)
    closed_df = closed_df.dropna(subset=["Datum prodeje"])

    if len(closed_df) == 0:
        return combined_df

    combined_values = []
    for row in combined_df.itertuples(index=False):
        current_date = pd.to_datetime(row.Date, errors="coerce")
        realized_result = float(
            closed_df.loc[closed_df["Datum prodeje"] <= current_date, "Realizovany zisk / ztrata USD"].sum()
        )
        combined_pct = calculate_combined_performance_pct(
            safe_float(row.clean_return_pct),
            safe_float(row.portfolio_value),
            realized_result,
        )
        combined_values.append(combined_pct)

    combined_df["clean_with_closed_pct"] = combined_values
    return combined_df


def build_clean_performance_history(history_df: pd.DataFrame, raw_df: pd.DataFrame) -> pd.DataFrame:
    # Priblizny cisty vykon portfolia bez vlivu novych nakupu.
    if history_df.empty:
        return pd.DataFrame()

    clean_df = history_df.copy()
    clean_df["Date"] = pd.to_datetime(clean_df["Date"]).dt.normalize()
    cash_flows_df = build_portfolio_cash_flows(raw_df)
    clean_df = clean_df.merge(cash_flows_df, on="Date", how="left")
    clean_df["net_flow_usd"] = clean_df["net_flow_usd"].fillna(0.0)
    clean_df["previous_value"] = clean_df["portfolio_value"].shift(1)
    clean_df["period_clean_return"] = 0.0

    valid_mask = clean_df["previous_value"] > 0
    clean_df.loc[valid_mask, "period_clean_return"] = (
        (clean_df.loc[valid_mask, "portfolio_value"] - clean_df.loc[valid_mask, "previous_value"] - clean_df.loc[valid_mask, "net_flow_usd"])
        / clean_df.loc[valid_mask, "previous_value"]
    )
    clean_df["clean_growth_factor"] = (1 + clean_df["period_clean_return"].fillna(0.0)).cumprod()
    clean_df["clean_return_pct"] = (clean_df["clean_growth_factor"] - 1) * 100
    return clean_df


def calculate_clean_performance_from_date(clean_history_df: pd.DataFrame, start_date: pd.Timestamp) -> float | None:
    # Spocte cisty vykon od zadaneho data bez vlivu pozdejsich cash flow.
    if clean_history_df.empty or "clean_growth_factor" not in clean_history_df.columns:
        return None

    filtered = clean_history_df[clean_history_df["Date"] >= start_date].copy()
    if len(filtered) < 2:
        return None

    start_factor = safe_float(filtered["clean_growth_factor"].iloc[0])
    end_factor = safe_float(filtered["clean_growth_factor"].iloc[-1])
    if start_factor in (None, 0) or end_factor is None:
        return None
    return ((end_factor / start_factor) - 1) * 100


def calculate_clean_performance_between_dates(clean_history_df: pd.DataFrame, start_date: pd.Timestamp, end_date: pd.Timestamp) -> float | None:
    # Spocte cisty vykon mezi dvema daty vcetne.
    if clean_history_df.empty or "clean_growth_factor" not in clean_history_df.columns:
        return None

    filtered = clean_history_df[(clean_history_df["Date"] >= start_date) & (clean_history_df["Date"] <= end_date)].copy()
    if len(filtered) < 2:
        return None

    start_factor = safe_float(filtered["clean_growth_factor"].iloc[0])
    end_factor = safe_float(filtered["clean_growth_factor"].iloc[-1])
    if start_factor in (None, 0) or end_factor is None:
        return None
    return ((end_factor / start_factor) - 1) * 100


def build_report_performance_rows(
    history_df: pd.DataFrame,
    clean_history_df: pd.DataFrame,
    closed_positions_df: pd.DataFrame,
    spy_history_df: pd.DataFrame,
    msci_history_df: pd.DataFrame,
    total_daily_change_usd: float,
    total_daily_change_pct: float,
) -> pd.DataFrame:
    # Pripravi jednoduche vykonnostni radky pro report.
    today = pd.Timestamp.today().normalize()
    start_of_week = today - pd.Timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)
    start_of_year = today.replace(month=1, day=1)
    previous_years = [today.year - 1, today.year - 2, today.year - 3]

    rows = [
        {"Obdobi": "Dnes", "value_change_usd": total_daily_change_usd, "value_change_pct": total_daily_change_pct, "clean_performance_pct": None, "clean_performance_value_usd": None, "clean_with_closed_pct": None, "clean_with_closed_value_usd": None, "spy_pct": None, "msci_pct": None},
        {"Obdobi": "Predchozi obchodni den", "value_change_usd": None, "value_change_pct": None, "clean_performance_pct": None, "clean_performance_value_usd": None, "clean_with_closed_pct": None, "clean_with_closed_value_usd": None, "spy_pct": None, "msci_pct": None},
        {"Obdobi": "Od zacatku tydne", "value_change_usd": None, "value_change_pct": None, "clean_performance_pct": None, "clean_performance_value_usd": None, "clean_with_closed_pct": None, "clean_with_closed_value_usd": None, "spy_pct": None, "msci_pct": None},
        {"Obdobi": "Od zacatku mesice", "value_change_usd": None, "value_change_pct": None, "clean_performance_pct": None, "clean_performance_value_usd": None, "clean_with_closed_pct": None, "clean_with_closed_value_usd": None, "spy_pct": None, "msci_pct": None},
        {"Obdobi": "Od zacatku roku", "value_change_usd": None, "value_change_pct": None, "clean_performance_pct": None, "clean_performance_value_usd": None, "clean_with_closed_pct": None, "clean_with_closed_value_usd": None, "spy_pct": None, "msci_pct": None},
        {"Obdobi": str(previous_years[0]), "value_change_usd": None, "value_change_pct": None, "clean_performance_pct": None, "clean_performance_value_usd": None, "clean_with_closed_pct": None, "clean_with_closed_value_usd": None, "spy_pct": None, "msci_pct": None},
        {"Obdobi": str(previous_years[1]), "value_change_usd": None, "value_change_pct": None, "clean_performance_pct": None, "clean_performance_value_usd": None, "clean_with_closed_pct": None, "clean_with_closed_value_usd": None, "spy_pct": None, "msci_pct": None},
        {"Obdobi": str(previous_years[2]), "value_change_usd": None, "value_change_pct": None, "clean_performance_pct": None, "clean_performance_value_usd": None, "clean_with_closed_pct": None, "clean_with_closed_value_usd": None, "spy_pct": None, "msci_pct": None},
        {"Obdobi": "Od nakupu", "value_change_usd": None, "value_change_pct": None, "clean_performance_pct": None, "clean_performance_value_usd": None, "clean_with_closed_pct": None, "clean_with_closed_value_usd": None, "spy_pct": None, "msci_pct": None},
    ]

    anchor_dates = [start_of_week, start_of_month, start_of_year]

    for index, anchor_date in enumerate(anchor_dates, start=2):
        absolute, percent = calculate_performance_from_date(history_df, anchor_date)
        rows[index]["value_change_usd"] = absolute
        rows[index]["value_change_pct"] = percent
        rows[index]["clean_performance_pct"] = calculate_clean_performance_from_date(clean_history_df, anchor_date)
        period_start_value = get_period_start_value(history_df, anchor_date)
        rows[index]["clean_performance_value_usd"] = calculate_clean_performance_value(
            rows[index]["clean_performance_pct"],
            period_start_value,
        )
        realized_result = calculate_realized_result_between_dates(closed_positions_df, anchor_date)
        rows[index]["clean_with_closed_value_usd"] = calculate_combined_performance_value(
            rows[index]["clean_performance_value_usd"],
            realized_result,
        )
        rows[index]["clean_with_closed_pct"] = calculate_combined_performance_pct(
            rows[index]["clean_performance_pct"],
            realized_result,
            period_start_value,
        )
        rows[index]["spy_pct"] = calculate_series_performance_from_date(spy_history_df, "benchmark_value", anchor_date)[1]
        rows[index]["msci_pct"] = calculate_series_performance_from_date(msci_history_df, "benchmark_value", anchor_date)[1]

    for offset, year_value in enumerate(previous_years, start=5):
        year_start = pd.Timestamp(year=year_value, month=1, day=1)
        year_end = pd.Timestamp(year=year_value, month=12, day=31)
        absolute, percent = calculate_performance_between_dates(history_df, year_start, year_end)
        rows[offset]["value_change_usd"] = absolute
        rows[offset]["value_change_pct"] = percent
        rows[offset]["clean_performance_pct"] = calculate_clean_performance_between_dates(clean_history_df, year_start, year_end)
        period_start_value = get_period_start_value(history_df, year_start, year_end)
        rows[offset]["clean_performance_value_usd"] = calculate_clean_performance_value(
            rows[offset]["clean_performance_pct"],
            period_start_value,
        )
        realized_result = calculate_realized_result_between_dates(closed_positions_df, year_start, year_end)
        rows[offset]["clean_with_closed_value_usd"] = calculate_combined_performance_value(
            rows[offset]["clean_performance_value_usd"],
            realized_result,
        )
        rows[offset]["clean_with_closed_pct"] = calculate_combined_performance_pct(
            rows[offset]["clean_performance_pct"],
            realized_result,
            period_start_value,
        )
        rows[offset]["spy_pct"] = calculate_series_performance_between_dates(spy_history_df, "benchmark_value", year_start, year_end)[1]
        rows[offset]["msci_pct"] = calculate_series_performance_between_dates(msci_history_df, "benchmark_value", year_start, year_end)[1]

    absolute, percent = calculate_performance(history_df["portfolio_value"]) if not history_df.empty else (None, None)
    rows[8]["value_change_usd"] = absolute
    rows[8]["value_change_pct"] = percent
    start_date_all = pd.to_datetime(clean_history_df["Date"].min(), errors="coerce") if not clean_history_df.empty else None
    rows[8]["clean_performance_pct"] = calculate_clean_performance_from_date(
        clean_history_df,
        start_date_all,
    ) if start_date_all is not None else None
    period_start_value = get_period_start_value(history_df, start_date_all) if start_date_all is not None else None
    rows[8]["clean_performance_value_usd"] = calculate_clean_performance_value(
        rows[8]["clean_performance_pct"],
        period_start_value,
    )
    realized_result = calculate_realized_result_between_dates(closed_positions_df, start_date_all) if start_date_all is not None else 0.0
    rows[8]["clean_with_closed_value_usd"] = calculate_combined_performance_value(
        rows[8]["clean_performance_value_usd"],
        realized_result,
    )
    rows[8]["clean_with_closed_pct"] = calculate_combined_performance_pct(
        rows[8]["clean_performance_pct"],
        realized_result,
        period_start_value,
    )
    portfolio_start_date = pd.to_datetime(history_df["Date"].min(), errors="coerce") if not history_df.empty else None
    if pd.notna(portfolio_start_date):
        rows[8]["spy_pct"] = calculate_series_performance_from_date(spy_history_df, "benchmark_value", portfolio_start_date)[1]
        rows[8]["msci_pct"] = calculate_series_performance_from_date(msci_history_df, "benchmark_value", portfolio_start_date)[1]

    previous_day_start = None
    report_end_date = None
    if not history_df.empty and "portfolio_value" in history_df.columns:
        latest_history = history_df.dropna(subset=["portfolio_value"]).copy()
        if len(latest_history) >= 2:
            previous_day_start = safe_float(latest_history["portfolio_value"].iloc[-2])
            latest_end_value = safe_float(latest_history["portfolio_value"].iloc[-1])
            if previous_day_start not in (None, 0) and latest_end_value is not None:
                rows[0]["value_change_usd"] = latest_end_value - previous_day_start
                rows[0]["value_change_pct"] = ((latest_end_value / previous_day_start) - 1) * 100
            report_end_date = pd.to_datetime(latest_history["Date"].iloc[-1], errors="coerce")
        elif len(latest_history) == 1:
            report_end_date = pd.to_datetime(latest_history["Date"].iloc[-1], errors="coerce")

    rows[0]["clean_performance_pct"] = total_daily_change_pct
    rows[0]["clean_performance_value_usd"] = total_daily_change_usd
    today_realized_result = calculate_realized_result_between_dates(
        closed_positions_df,
        report_end_date if pd.notna(report_end_date) else today,
        report_end_date if pd.notna(report_end_date) else today,
    )
    rows[0]["clean_with_closed_value_usd"] = calculate_combined_performance_value(
        rows[0]["clean_performance_value_usd"],
        today_realized_result,
    )
    rows[0]["clean_with_closed_pct"] = calculate_combined_performance_pct(
        rows[0]["clean_performance_pct"],
        today_realized_result,
        previous_day_start,
    )
    if len(spy_history_df) >= 2:
        rows[0]["spy_pct"] = calculate_performance(spy_history_df["benchmark_value"])[1]
        if pd.notna(rows[0]["spy_pct"]):
            rows[0]["spy_pct"] = ((float(spy_history_df["benchmark_value"].iloc[-1]) / float(spy_history_df["benchmark_value"].iloc[-2])) - 1) * 100
    if len(msci_history_df) >= 2:
        rows[0]["msci_pct"] = calculate_performance(msci_history_df["benchmark_value"])[1]
        if pd.notna(rows[0]["msci_pct"]):
            rows[0]["msci_pct"] = ((float(msci_history_df["benchmark_value"].iloc[-1]) / float(msci_history_df["benchmark_value"].iloc[-2])) - 1) * 100

    if not history_df.empty and "portfolio_value" in history_df.columns:
        latest_history = history_df.dropna(subset=["portfolio_value"]).copy()
        if len(latest_history) >= 3:
            previous_trading_start = safe_float(latest_history["portfolio_value"].iloc[-3])
            previous_trading_end = safe_float(latest_history["portfolio_value"].iloc[-2])
            if previous_trading_start not in (None, 0) and previous_trading_end is not None:
                rows[1]["value_change_usd"] = previous_trading_end - previous_trading_start
                rows[1]["value_change_pct"] = ((previous_trading_end / previous_trading_start) - 1) * 100
            rows[1]["clean_performance_pct"] = rows[1]["value_change_pct"]
            rows[1]["clean_performance_value_usd"] = rows[1]["value_change_usd"]
            previous_trading_start_date = pd.to_datetime(latest_history["Date"].iloc[-2], errors="coerce")
            previous_day_realized_result = calculate_realized_result_between_dates(
                closed_positions_df,
                previous_trading_start_date,
                previous_trading_start_date,
            ) if pd.notna(previous_trading_start_date) else 0.0
            rows[1]["clean_with_closed_value_usd"] = calculate_combined_performance_value(
                rows[1]["clean_performance_value_usd"],
                previous_day_realized_result,
            )
            rows[1]["clean_with_closed_pct"] = calculate_combined_performance_pct(
                rows[1]["clean_performance_pct"],
                previous_day_realized_result,
                previous_trading_start,
            )

    if len(spy_history_df) >= 3:
        rows[1]["spy_pct"] = ((float(spy_history_df["benchmark_value"].iloc[-2]) / float(spy_history_df["benchmark_value"].iloc[-3])) - 1) * 100
    if len(msci_history_df) >= 3:
        rows[1]["msci_pct"] = ((float(msci_history_df["benchmark_value"].iloc[-2]) / float(msci_history_df["benchmark_value"].iloc[-3])) - 1) * 100

    return pd.DataFrame(rows)


def get_report_change_tables(raw_df: pd.DataFrame, analysis_df: pd.DataFrame, analysis_history_df: pd.DataFrame, date_format_label: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # Vytvori jednoduche tabulky poslednich zmen z dostupnych CSV souboru.
    portfolio_changes = pd.DataFrame()
    if len(raw_df) > 0 and "purchase_date" in raw_df.columns:
        portfolio_changes = raw_df.copy()
        portfolio_changes["purchase_date_sort"] = pd.to_datetime(portfolio_changes["purchase_date"], errors="coerce")
        portfolio_changes = portfolio_changes.sort_values("purchase_date_sort", ascending=False)
        portfolio_changes["Datum"] = portfolio_changes["purchase_date"].apply(lambda value: format_date_display(value, date_format_label))
        portfolio_changes = portfolio_changes.rename(
            columns={"ticker": "Ticker", "company": "Spolecnost", "shares": "Kusy", "buy_price": "Nakupni cena"}
        )
        portfolio_changes = portfolio_changes[["Datum", "Ticker", "Spolecnost", "Kusy", "Nakupni cena"]].head(5)
        portfolio_changes = portfolio_changes.fillna("N/A").replace("", "N/A")

    plan_changes = pd.DataFrame()
    if len(analysis_df) > 0:
        plan_changes = analysis_df.copy()
        plan_changes["updated_at_sort"] = pd.to_datetime(plan_changes["updated_at"], errors="coerce")
        plan_changes = plan_changes.sort_values("updated_at_sort", ascending=False)
        plan_changes["Posledni revize"] = plan_changes["updated_at"].apply(lambda value: format_date_display(value, date_format_label))
        plan_changes = plan_changes.rename(
            columns={"ticker": "Ticker", "company": "Spolecnost", "status": "Status", "next_action": "Dalsi akce"}
        )
        plan_changes = plan_changes[["Posledni revize", "Ticker", "Spolecnost", "Status", "Dalsi akce"]].head(5)
        plan_changes = plan_changes.fillna("N/A").replace("", "N/A")

    decision_changes = pd.DataFrame()
    if len(analysis_history_df) > 0:
        decision_changes = analysis_history_df.copy()
        decision_changes["decision_date_sort"] = pd.to_datetime(decision_changes["decision_date"], errors="coerce")
        decision_changes = decision_changes.sort_values("decision_date_sort", ascending=False)
        decision_changes["Datum"] = decision_changes["decision_date"].apply(lambda value: format_date_display(value, date_format_label))
        decision_changes = decision_changes.rename(
            columns={"ticker": "Ticker", "decision_type": "Typ", "plan_text": "Plan", "comment": "Komentar"}
        )
        decision_changes = decision_changes[["Datum", "Ticker", "Typ", "Plan", "Komentar"]].head(5)
        decision_changes = decision_changes.fillna("N/A").replace("", "N/A")

    return portfolio_changes, plan_changes, decision_changes


@st.cache_data(ttl=3600)
def get_czk_rates(selected_pairs: tuple[str, ...] = tuple(DEFAULT_FX_PAIRS)) -> dict:
    # Nacte vybrane FX pary vcetne 1Y trendu.
    rates = {}
    for pair in selected_pairs:
        pair_config = FX_PAIR_CONFIG.get(pair)
        if not pair_config:
            continue
        history_df = yf.Ticker(pair_config["ticker"]).history(period="1y")
        if history_df.empty:
            continue
        rates[pair] = {
            "value": float(history_df["Close"].iloc[-1]),
            "history": history_df["Close"].round(2).tolist(),
            "suffix": pair_config.get("suffix", ""),
        }
    return rates


def format_market_cap(value) -> str:
    # Prevede market cap na kratky text.
    if pd.isna(value) or value is None:
        return "N/A"
    if value >= 200_000_000_000:
        return "Mega (+200B)"
    if value >= 10_000_000_000:
        return "Large (10-200B)"
    if value >= 2_000_000_000:
        return "Mid (2-10B)"
    if value >= 300_000_000:
        return "Small (0.3-2B)"
    return "Micro (<0.3B)"


def infer_investment_region(ticker: str, company: str | None = None) -> str:
    # Jednoducha regioni mapa podle emitenta, ne podle burzy nakupu.
    region_map = {
        "MA": "USA",
        "AMZN": "USA",
        "MSFT": "USA",
        "SPGI": "USA",
        "AMD": "USA",
        "DUOL": "USA",
        "GOOGL": "USA",
        "LRCX": "USA",
        "META": "USA",
        "TTD": "USA",
        "S": "USA",
        "NOW": "USA",
        "V": "USA",
        "SOFI": "USA",
        "HOOD": "USA",
        "BTG": "Amerika / Kanada",
        "NFLX": "USA",
        "ANET": "USA",
        "PLTR": "USA",
        "DG": "USA",
        "CVS": "USA",
        "GRPN": "USA",
        "NVO": "Evropa",
        "IWDA": "Globalni ETF",
        "BY6": "Asie",
        "JD": "Asie",
        "BABA": "Asie",
        "NIO": "Asie",
        "CEZ": "Evropa",
        "ASML": "Evropa",
        "VW": "Evropa",
        "SQM": "Latinska Amerika",
    }
    ticker_text = str(ticker).upper().strip()
    if ticker_text in region_map:
        return region_map[ticker_text]

    company_text = str(company).lower() if company else ""
    if "etf" in company_text or "ucits" in company_text:
        return "Globalni ETF"
    return "Ostatni"


def normalize_size_bucket(size_text: str) -> str:
    # U ETF nebo chybejicich dat vrati neutralni kategorii.
    if not size_text or size_text == "N/A" or size_text == "nan":
        return "ETF / N/A"
    return size_text


def format_price_with_currency(value, currency) -> str:
    # Prida k cene menu pro zobrazeni v tabulce.
    if pd.isna(value) or value is None:
        return "N/A"
    if pd.isna(currency) or currency is None:
        return f"{value:.2f}"
    return f"{value:.2f} {currency}"


def build_transaction_ticker_map(raw_df: pd.DataFrame, watchlist_df: pd.DataFrame) -> dict:
    # Sestavi jednoduchou mapu ticker -> firma / yfinance ticker.
    ticker_map = {}
    for frame in [raw_df, watchlist_df]:
        if len(frame) == 0 or "ticker" not in frame.columns:
            continue
        for row in frame.itertuples(index=False):
            ticker_map[str(row.ticker).upper()] = {
                "company": row.company if hasattr(row, "company") and pd.notna(row.company) else "",
                "yfinance_ticker": row.yfinance_ticker if hasattr(row, "yfinance_ticker") and pd.notna(row.yfinance_ticker) else row.ticker,
            }
    return ticker_map


def process_transactions(transactions_df: pd.DataFrame, ticker_map: dict, base_currency: str) -> dict:
    # Z transakci dopocte otevrene loty, uzavrene obchody a zakladni vysledky.
    open_position_columns = [
        "Ticker",
        "Spolecnost",
        "Pocet kusu",
        "Prumerna nakupni cena",
        "Aktualni cena",
        "Current Value USD",
        "Nerealizovany zisk / ztrata USD",
        "Nerealizovany zisk / ztrata %",
        "Mena",
    ]
    closed_position_columns = [
        "Ticker",
        "Spolecnost",
        "Datum nakupu",
        "Datum prodeje",
        "3lety test",
        "Pocet kusu",
        "Prumerna nakupni cena",
        "Prumerna prodejni cena",
        "Prodejni obrat USD",
        "Realizovany vysledek mimo 3lety test USD",
        "Poplatky mimo 3lety test USD",
        "Poplatky",
        "Poplatky USD",
        "Realizovany zisk / ztrata USD",
        "Realizovany zisk / ztrata %",
        "Rok realizace",
        "Mena",
        "Broker",
        "Poznamka",
    ]
    annual_summary_columns = ["Rok realizace", "Prodejni obrat USD", "Realizovany vysledek mimo 3lety test USD", "Poplatky mimo 3lety test USD", "Realizovane zisky USD", "Realizovane ztraty USD", "Realizovany vysledek USD", "Poplatky USD", "Pocet uzavrenych obchodu"]

    if len(transactions_df) == 0:
        return {
            "open_positions": pd.DataFrame(columns=open_position_columns + ["Current Value", "Nerealizovany zisk / ztrata"]),
            "closed_positions": pd.DataFrame(columns=closed_position_columns + ["Realizovany zisk / ztrata"]),
            "annual_summary": pd.DataFrame(columns=annual_summary_columns + ["Realizovany vysledek"]),
            "realized_total_base": 0.0,
            "unrealized_total_base": 0.0,
            "dividend_total_base": 0.0,
            "fee_total_base": 0.0,
            "total_result_base": 0.0,
        }

    working_df = transactions_df.copy()
    working_df["date_sort"] = pd.to_datetime(working_df["date"], errors="coerce")
    working_df = working_df.sort_values(["date_sort", "ticker", "transaction_type"]).reset_index(drop=True)

    lots_by_ticker: dict[str, list[dict]] = {}
    closed_rows = []
    dividend_total_usd = 0.0
    standalone_fee_total_usd = 0.0

    for row in working_df.itertuples(index=False):
        ticker = str(row.ticker).upper() if pd.notna(row.ticker) else ""
        transaction_type = str(row.transaction_type).lower()
        quantity = safe_float(row.quantity) or 0.0
        price = safe_float(row.price) or 0.0
        buy_fee = safe_float(getattr(row, "buy_fee", None)) or 0.0
        sell_fee = safe_float(getattr(row, "sell_fee", None)) or 0.0
        fx_fee = safe_float(getattr(row, "fx_fee", None)) or 0.0
        currency = str(row.currency).upper() if pd.notna(row.currency) and str(row.currency).strip() else "USD"
        fx_rate = get_fx_rate_to_usd(currency)

        if transaction_type == "buy":
            if ticker not in lots_by_ticker:
                lots_by_ticker[ticker] = []
            total_buy_fee = buy_fee + fx_fee
            fee_per_share = (total_buy_fee / quantity) if quantity else 0.0
            lots_by_ticker[ticker].append(
                {
                    "buy_date": row.date,
                    "ticker": ticker,
                    "company": row.company if pd.notna(row.company) else ticker_map.get(ticker, {}).get("company", ""),
                    "currency": currency,
                    "buy_fx_rate": fx_rate,
                    "buy_price": price,
                    "buy_fee_per_share": fee_per_share,
                    "cost_per_share_with_fee": price + fee_per_share,
                    "remaining_quantity": quantity,
                    "broker": getattr(row, "broker", "") if pd.notna(getattr(row, "broker", "")) else "",
                    "note": row.note if pd.notna(row.note) else "",
                }
            )
        elif transaction_type == "sell":
            sell_quantity_left = quantity
            lots = lots_by_ticker.get(ticker, [])
            total_sell_fee = sell_fee + fx_fee
            sell_fee_per_share = (total_sell_fee / quantity) if quantity else 0.0

            while sell_quantity_left > 0 and lots:
                lot = lots[0]
                matched_quantity = min(sell_quantity_left, lot["remaining_quantity"])
                matched_buy_fee = matched_quantity * lot.get("buy_fee_per_share", 0.0)
                matched_sell_fee = matched_quantity * sell_fee_per_share
                matched_total_fee = matched_buy_fee + matched_sell_fee
                buy_date_value = pd.to_datetime(lot["buy_date"], errors="coerce")
                sell_date_value = pd.to_datetime(row.date, errors="coerce")
                passes_three_year_test = False
                if pd.notna(buy_date_value) and pd.notna(sell_date_value):
                    passes_three_year_test = sell_date_value > (buy_date_value + pd.DateOffset(years=3))
                buy_cost_total_usd = matched_quantity * lot["cost_per_share_with_fee"] * lot.get("buy_fx_rate", 1.0)
                sell_value_total_usd = matched_quantity * max(price - sell_fee_per_share, 0) * fx_rate
                realized_usd = sell_value_total_usd - buy_cost_total_usd
                invested_usd = buy_cost_total_usd
                realized_pct = (realized_usd / invested_usd * 100) if invested_usd else None
                closed_rows.append(
                    {
                        "Ticker": ticker,
                        "Spolecnost": lot["company"] or ticker_map.get(ticker, {}).get("company", "N/A"),
                        "Datum nakupu": lot["buy_date"],
                        "Datum prodeje": row.date,
                        "3lety test": "Ano" if passes_three_year_test else "Ne",
                        "Pocet kusu": matched_quantity,
                        "Prumerna nakupni cena": lot["buy_price"],
                        "Prumerna prodejni cena": price,
                        "Prodejni obrat USD": matched_quantity * price * fx_rate,
                        "Realizovany vysledek mimo 3lety test USD": 0.0 if passes_three_year_test else realized_usd,
                        "Poplatky mimo 3lety test USD": 0.0 if passes_three_year_test else (matched_buy_fee * lot.get("buy_fx_rate", 1.0)) + (matched_sell_fee * fx_rate),
                        "Poplatky": matched_total_fee,
                        "Poplatky USD": (matched_buy_fee * lot.get("buy_fx_rate", 1.0)) + (matched_sell_fee * fx_rate),
                        "Realizovany zisk / ztrata USD": realized_usd,
                        "Realizovany zisk / ztrata %": realized_pct,
                        "Rok realizace": extract_year(row.date),
                        "Mena": currency,
                        "Broker": getattr(row, "broker", "") if pd.notna(getattr(row, "broker", "")) and str(getattr(row, "broker", "")).strip() else lot.get("broker", ""),
                        "Poznamka": row.note if pd.notna(row.note) and str(row.note).strip() else lot["note"],
                    }
                )
                lot["remaining_quantity"] -= matched_quantity
                sell_quantity_left -= matched_quantity
                if lot["remaining_quantity"] <= 0:
                    lots.pop(0)

            lots_by_ticker[ticker] = lots
        elif transaction_type == "dividend":
            dividend_total_usd += (quantity * price - fx_fee) * fx_rate
        elif transaction_type == "fee":
            standalone_fee_total_usd += max(quantity * price, buy_fee + sell_fee + fx_fee) * fx_rate

    open_rows = []
    for ticker, lots in lots_by_ticker.items():
        remaining_lots = [lot for lot in lots if lot["remaining_quantity"] > 0]
        if not remaining_lots:
            continue

        total_quantity = sum(lot["remaining_quantity"] for lot in remaining_lots)
        avg_buy_price = (
            sum(lot["remaining_quantity"] * lot["buy_price"] for lot in remaining_lots) / total_quantity
            if total_quantity
            else None
        )
        cost_usd = sum(lot["remaining_quantity"] * lot["cost_per_share_with_fee"] * get_fx_rate_to_usd(lot["currency"]) for lot in remaining_lots)
        currency = remaining_lots[0]["currency"]
        yfinance_ticker = ticker_map.get(ticker, {}).get("yfinance_ticker", ticker)

        current_price = None
        current_value_usd = None
        unrealized_usd = None
        unrealized_pct = None
        try:
            details = get_ticker_details(yfinance_ticker)
            current_price = details["price"]
            current_value_usd = details["current_price_usd"] * total_quantity
            unrealized_usd = current_value_usd - cost_usd
            unrealized_pct = (unrealized_usd / cost_usd * 100) if cost_usd else None
            currency = details["currency"]
        except Exception:
            pass

        open_rows.append(
            {
                "Ticker": ticker,
                "Spolecnost": remaining_lots[0]["company"] or ticker_map.get(ticker, {}).get("company", "N/A"),
                "Pocet kusu": total_quantity,
                "Prumerna nakupni cena": avg_buy_price,
                "Aktualni cena": current_price,
                "Current Value USD": current_value_usd,
                "Nerealizovany zisk / ztrata USD": unrealized_usd,
                "Nerealizovany zisk / ztrata %": unrealized_pct,
                "Mena": currency,
            }
        )

    open_positions_df = pd.DataFrame(open_rows, columns=open_position_columns)
    closed_positions_df = pd.DataFrame(closed_rows, columns=closed_position_columns)

    if len(closed_positions_df) > 0:
        annual_summary_df = (
            closed_positions_df.groupby("Rok realizace", dropna=False)
            .agg(
                **{
                    "Prodejni obrat USD": ("Prodejni obrat USD", "sum"),
                    "Realizovany vysledek mimo 3lety test USD": ("Realizovany vysledek mimo 3lety test USD", "sum"),
                    "Poplatky mimo 3lety test USD": ("Poplatky mimo 3lety test USD", "sum"),
                    "Realizovane zisky USD": ("Realizovany zisk / ztrata USD", lambda values: float(pd.Series(values)[pd.Series(values) > 0].sum())),
                    "Realizovane ztraty USD": ("Realizovany zisk / ztrata USD", lambda values: float(pd.Series(values)[pd.Series(values) < 0].sum())),
                    "Realizovany vysledek USD": ("Realizovany zisk / ztrata USD", "sum"),
                    "Poplatky USD": ("Poplatky USD", "sum"),
                    "Pocet uzavrenych obchodu": ("Ticker", "count"),
                }
            )
            .reset_index()
            .sort_values("Rok realizace", ascending=False)
        )
    else:
        annual_summary_df = pd.DataFrame(columns=annual_summary_columns)

    realized_total_usd = float(closed_positions_df["Realizovany zisk / ztrata USD"].sum()) if len(closed_positions_df) > 0 else 0.0
    unrealized_total_usd = float(open_positions_df["Nerealizovany zisk / ztrata USD"].fillna(0.0).sum()) if len(open_positions_df) > 0 else 0.0
    fee_total_usd = float(standalone_fee_total_usd)
    total_result_usd = realized_total_usd + unrealized_total_usd + dividend_total_usd - fee_total_usd

    open_positions_df["Current Value"] = open_positions_df["Current Value USD"].apply(lambda value: convert_from_usd(value, base_currency) if pd.notna(value) else None)
    open_positions_df["Nerealizovany zisk / ztrata"] = open_positions_df["Nerealizovany zisk / ztrata USD"].apply(lambda value: convert_from_usd(value, base_currency) if pd.notna(value) else None)
    closed_positions_df["Prodejni obrat"] = closed_positions_df["Prodejni obrat USD"].apply(lambda value: convert_from_usd(value, base_currency) if pd.notna(value) else None)
    closed_positions_df["Realizovany vysledek mimo 3lety test"] = closed_positions_df["Realizovany vysledek mimo 3lety test USD"].apply(lambda value: convert_from_usd(value, base_currency) if pd.notna(value) else None)
    closed_positions_df["Poplatky mimo 3lety test"] = closed_positions_df["Poplatky mimo 3lety test USD"].apply(lambda value: convert_from_usd(value, base_currency) if pd.notna(value) else None)
    closed_positions_df["Realizovany zisk / ztrata"] = closed_positions_df["Realizovany zisk / ztrata USD"].apply(lambda value: convert_from_usd(value, base_currency) if pd.notna(value) else None)
    closed_positions_df["Poplatky v nastavene mene"] = closed_positions_df["Poplatky USD"].apply(lambda value: convert_from_usd(value, base_currency) if pd.notna(value) else None)
    annual_summary_df["Prodejni obrat"] = annual_summary_df["Prodejni obrat USD"].apply(lambda value: convert_from_usd(value, base_currency) if pd.notna(value) else None)
    annual_summary_df["Realizovany vysledek mimo 3lety test"] = annual_summary_df["Realizovany vysledek mimo 3lety test USD"].apply(lambda value: convert_from_usd(value, base_currency) if pd.notna(value) else None)
    annual_summary_df["Poplatky mimo 3lety test"] = annual_summary_df["Poplatky mimo 3lety test USD"].apply(lambda value: convert_from_usd(value, base_currency) if pd.notna(value) else None)
    annual_summary_df["Realizovane zisky"] = annual_summary_df["Realizovane zisky USD"].apply(lambda value: convert_from_usd(value, base_currency) if pd.notna(value) else None)
    annual_summary_df["Realizovane ztraty"] = annual_summary_df["Realizovane ztraty USD"].apply(lambda value: convert_from_usd(value, base_currency) if pd.notna(value) else None)
    annual_summary_df["Realizovany vysledek"] = annual_summary_df["Realizovany vysledek USD"].apply(lambda value: convert_from_usd(value, base_currency) if pd.notna(value) else None)
    annual_summary_df["Poplatky"] = annual_summary_df["Poplatky USD"].apply(lambda value: convert_from_usd(value, base_currency) if pd.notna(value) else None)

    return {
        "open_positions": open_positions_df,
        "closed_positions": closed_positions_df,
        "annual_summary": annual_summary_df,
        "realized_total_base": convert_from_usd(realized_total_usd, base_currency),
        "unrealized_total_base": convert_from_usd(unrealized_total_usd, base_currency),
        "dividend_total_base": convert_from_usd(dividend_total_usd, base_currency),
        "fee_total_base": convert_from_usd(fee_total_usd, base_currency),
        "total_result_base": convert_from_usd(total_result_usd, base_currency),
    }
def format_number(value, suffix: str = "") -> str:
    # Bezpecne zobrazi cislo nebo N/A.
    if pd.isna(value) or value is None:
        return "N/A"
    return f"{value:.2f}{suffix}"


def format_date_display(date_value: str, date_format_label: str) -> str:
    # Prevede datum do zvoleneho formatu.
    parsed = pd.to_datetime(date_value, errors="coerce")
    if pd.isna(parsed):
        return "N/A"
    return parsed.strftime(DATE_FORMATS[date_format_label])


def evaluate_buy_zone(current_price: float, buy_zone_low: float, buy_zone_high: float) -> tuple[str, float | None]:
    # Vyhodnoti, jestli je cena v nakupni zone a jak daleko od ni je.
    if pd.isna(current_price) or pd.isna(buy_zone_low) or pd.isna(buy_zone_high):
        return "N/A", None

    if buy_zone_low <= current_price <= buy_zone_high:
        return "V nakupni zone", 0.0
    if current_price < buy_zone_low:
        return "Pod nakupni zonou", ((buy_zone_low - current_price) / buy_zone_low) * 100
    return "Nad nakupni zonou", ((current_price - buy_zone_high) / buy_zone_high) * 100


def build_watchlist_overview(watchlist_df: pd.DataFrame) -> pd.DataFrame:
    # Doplni watchlist o aktualni cenu, status a vzdalenost od buy zony.
    if len(watchlist_df) == 0:
        return watchlist_df.copy()

    rows = []
    for row in watchlist_df.itertuples(index=False):
        try:
            details = get_ticker_details(row.yfinance_ticker)
            current_price = details["price"]
            currency = details["currency"]
            company_live = details["company_live"]
        except Exception:
            current_price = None
            currency = None
            company_live = None

        status, distance_pct = evaluate_buy_zone(current_price, row.buy_zone_low, row.buy_zone_high)

        rows.append(
            {
                "Ticker": row.ticker,
                "Spolecnost": row.company if pd.notna(row.company) and str(row.company).strip() else company_live if company_live else "N/A",
                "Aktualni cena": format_price_with_currency(current_price, currency),
                "Buy zone": f"{format_number(row.buy_zone_low)} - {format_number(row.buy_zone_high)}",
                "Plan nakupu": format_number(row.buy_plan),
                "Plan prodeje": format_number(row.sell_target),
                "Status": status,
                "Vzdalenost od buy zony": format_number(distance_pct, " %"),
                "Poznamka": f"{format_date_display(row.note_date, date_format_label)} / {format_number(row.note_price)} / {row.note_text if pd.notna(row.note_text) and row.note_text else 'N/A'}",
                "_current_price_value": current_price,
                "_buy_plan_value": row.buy_plan,
                "_watchlist_status": status,
                "_distance_pct_value": distance_pct,
            }
        )

    return pd.DataFrame(rows)


def sort_watchlist_priority(overview_df: pd.DataFrame) -> pd.DataFrame:
    # Seradi kandidaty podle investicni priority, ne podle poradi v CSV.
    if len(overview_df) == 0:
        return overview_df.copy()

    sorted_df = overview_df.copy()
    priority_map = {
        "V nakupni zone": 0,
        "Pod nakupni zonou": 1,
        "Nad nakupni zonou": 2,
        "N/A": 3,
    }
    sorted_df["_priority_rank"] = sorted_df["_watchlist_status"].map(priority_map).fillna(3)
    sorted_df["_distance_sort"] = pd.to_numeric(sorted_df["_distance_pct_value"], errors="coerce").fillna(999999.0)
    sorted_df = sorted_df.sort_values(
        by=["_priority_rank", "_distance_sort", "Ticker"],
        ascending=[True, True, True],
        na_position="last",
    ).drop(columns=["_priority_rank", "_distance_sort"], errors="ignore")
    return sorted_df.reset_index(drop=True)


def style_watchlist_row(row: pd.Series) -> list[str]:
    # Zvýrazni radky, kde se cena dostala do nakupni oblasti.
    current_price = row.get("_current_price_value")
    buy_plan = row.get("_buy_plan_value")
    status = row.get("_watchlist_status")

    if pd.notna(current_price) and pd.notna(buy_plan) and current_price <= buy_plan:
        return ["background-color: rgba(34, 197, 94, 0.22); border-left: 3px solid #22c55e"] * len(row)
    if status in ["V nakupni zone", "Pod nakupni zonou"]:
        return ["background-color: rgba(34, 197, 94, 0.12)"] * len(row)
    return [""] * len(row)


def get_analysis_ticker_options(raw_df: pd.DataFrame, watchlist_df: pd.DataFrame, analysis_df: pd.DataFrame) -> list[str]:
    # Vrati jednoduchy sjednoceny seznam tickeru pro analyzu.
    tickers = set()
    if "ticker" in raw_df.columns:
        tickers.update(raw_df["ticker"].dropna().astype(str).str.upper().tolist())
    if "ticker" in watchlist_df.columns:
        tickers.update(watchlist_df["ticker"].dropna().astype(str).str.upper().tolist())
    if "ticker" in analysis_df.columns:
        tickers.update(analysis_df["ticker"].dropna().astype(str).str.upper().tolist())
    return sorted(tickers)


def upsert_analysis_row(analysis_df: pd.DataFrame, ticker: str, company: str, thesis: str, buy_plan: str, sell_plan: str, risk_notes: str, last_note: str) -> pd.DataFrame:
    # Aktualizuje existujici analyzu nebo vytvori novou.
    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    existing_index = analysis_df.index[analysis_df["ticker"] == ticker].tolist()

    row_data = {
        "ticker": ticker,
        "company": company,
        "avg_buy_price": "",
        "target_price": "",
        "invalidation_level": "",
        "status": "",
        "conviction": "",
        "next_action": "",
        "investment_thesis": thesis,
        "buy_plan": buy_plan,
        "sell_plan": sell_plan,
        "risk_notes": risk_notes,
        "last_note": last_note,
        "updated_at": updated_at,
    }

    if existing_index:
        analysis_df.loc[existing_index[0], list(row_data.keys())] = list(row_data.values())
        return analysis_df

    return pd.concat([analysis_df, pd.DataFrame([row_data])], ignore_index=True)


def format_status_badge(status: str) -> str:
    # Jednoduchy textovy status pro tabulku.
    if not status or status == "nan":
        return "N/A"
    status_map = {
        "Building": "🟡 Building",
        "Hold": "🟢 Hold",
        "Review": "🟠 Review",
        "Trim": "🟣 Trim",
        "Exit": "🔴 Exit",
    }
    return status_map.get(status, status)


def format_status_badge(status: str) -> str:
    # Oprava rozbiteho kodovani ve status badge.
    if not status or status == "nan":
        return "N/A"
    status_map = {
        "Building": "Building",
        "Hold": "Hold",
        "Review": "Review",
        "Trim": "Trim",
        "Exit": "Exit",
    }
    return status_map.get(status, status)


def safe_number_input_value(value, default: float = 0.0) -> float:
    # Bezpecny fallback pro Streamlit number_input.
    numeric_value = safe_float(value)
    return default if numeric_value is None else float(numeric_value)


def build_analysis_overview(raw_df: pd.DataFrame, analysis_df: pd.DataFrame, base_currency: str) -> pd.DataFrame:
    # Sestavi prehled vsech vlastnenych firem pro sekci analyza.
    holdings_df = aggregate_portfolio(raw_df)
    if len(holdings_df) == 0:
        return pd.DataFrame()

    rows = []
    for row in holdings_df.itertuples(index=False):
        try:
            details = get_ticker_details(row.yfinance_ticker)
            current_price = details["price"]
            current_price_text = format_price_with_currency(current_price, details["currency"])
            current_price_base = convert_from_usd(details["current_price_usd"], base_currency)
        except Exception:
            current_price = None
            current_price_text = "N/A"
            current_price_base = None

        analysis_match = analysis_df[analysis_df["ticker"] == row.ticker]
        plan_row = analysis_match.iloc[0] if len(analysis_match) > 0 else pd.Series(dtype=object)
        target_price = pd.to_numeric(plan_row.get("target_price", None), errors="coerce")
        avg_buy_price = pd.to_numeric(plan_row.get("avg_buy_price", None), errors="coerce")
        if pd.isna(avg_buy_price):
            avg_buy_price = float(row.buy_price)

        if pd.notna(target_price) and current_price is not None and current_price != 0:
            upside_pct = ((target_price - current_price) / current_price) * 100
        else:
            upside_pct = None

        rows.append(
            {
                "Ticker": row.ticker,
                "Spolecnost": (
                    plan_row.get("company")
                    if pd.notna(plan_row.get("company", None)) and str(plan_row.get("company", "")).strip()
                    else row.company if pd.notna(row.company) and str(row.company).strip()
                    else "N/A"
                ),
                "Aktualni cena": current_price_text,
                "Prumerna nakupni cena": format_number(avg_buy_price),
                "Cilova cena": format_number(target_price),
                "Upside %": format_number(upside_pct, " %"),
                "Status": format_status_badge(str(plan_row.get("status", ""))),
                "Conviction": plan_row.get("conviction", "N/A") if pd.notna(plan_row.get("conviction", None)) and str(plan_row.get("conviction", "")).strip() else "N/A",
                "Dalsi akce": plan_row.get("next_action", "N/A") if pd.notna(plan_row.get("next_action", None)) and str(plan_row.get("next_action", "")).strip() else "N/A",
                "Posledni revize": format_date_display(plan_row.get("updated_at", ""), date_format_label) if pd.notna(plan_row.get("updated_at", None)) and str(plan_row.get("updated_at", "")).strip() else "N/A",
                "_current_price_base": current_price_base,
                "_status_raw": str(plan_row.get("status", "")).strip(),
            }
        )

    return pd.DataFrame(rows)


def calculate_future_value(start_value: float, monthly_contribution: float, annual_return_pct: float, years: float) -> float:
    # Jednoducha kalkulacka budouci hodnoty pri mesicnim prispevku.
    monthly_rate = annual_return_pct / 100 / 12
    months = int(max(years * 12, 0))
    future_value = float(start_value)

    for _ in range(months):
        future_value = future_value * (1 + monthly_rate) + monthly_contribution

    return future_value


def safe_float(value) -> float | None:
    # Bezpecne prevede hodnotu na cislo, jinak vrati None.
    numeric_value = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric_value):
        return None
    return float(numeric_value)


def extract_year(period_value) -> int | None:
    # Z textu obdobi vezme prvni ctyrciferny rok.
    text = str(period_value).strip()
    if len(text) >= 4 and text[:4].isdigit():
        return int(text[:4])
    digits = "".join(character for character in text if character.isdigit())
    if len(digits) >= 4:
        return int(digits[:4])
    return None


def calculate_check_metrics(planned_value, actual_value) -> tuple[float | None, float | None]:
    # Odchylku a splneni planu pocita az kdyz je vyplnena skutecnost.
    planned = safe_float(planned_value)
    actual = safe_float(actual_value)
    if planned is None or actual is None:
        return None, None
    deviation = actual - planned
    completion_pct = (actual / planned * 100) if planned else None
    return deviation, completion_pct


def build_future_value_schedule(start_value: float, monthly_contribution: float, annual_return_pct: float, start_year: int, target_year: int) -> list[dict]:
    # Vytvori rocni tabulku planovanych hodnot stejnou logikou jako kalkulacka.
    schedule = []
    if target_year < start_year:
        return schedule

    for current_year in range(start_year, target_year + 1):
        years_elapsed = current_year - start_year + 1
        planned_value = calculate_future_value(start_value, monthly_contribution, annual_return_pct, years_elapsed)
        schedule.append(
            {
                "period_label": str(current_year),
                "period_date": f"{current_year}-12-31",
                "planned_value": planned_value,
            }
        )

    return schedule


def generate_long_term_checks(
    checks_df: pd.DataFrame,
    selected_plan: pd.Series,
    mode: str,
) -> tuple[pd.DataFrame, int, int]:
    # Vygeneruje rocni kontroly planu a podle rezimu je prepise nebo jen doplni.
    start_year = extract_year(selected_plan.get("start_period", ""))
    target_year = extract_year(selected_plan.get("target_period", ""))

    if start_year is None or target_year is None:
        raise ValueError("U planu chybi platny startovni nebo cilovy rok.")

    schedule = build_future_value_schedule(
        safe_number_input_value(selected_plan.get("start_value", 0.0)),
        safe_number_input_value(selected_plan.get("monthly_contribution", 0.0)),
        safe_number_input_value(selected_plan.get("expected_return_pct", 0.0)),
        start_year,
        target_year,
    )

    updated_df = checks_df.copy()
    created_count = 0
    updated_count = 0
    plan_name = selected_plan["plan_name"]

    for item in schedule:
        row_mask = (
            (updated_df["plan_name"] == plan_name)
            & (updated_df["period_label"].astype(str) == item["period_label"])
        )
        existing_rows = updated_df[row_mask]

        if len(existing_rows) == 0:
            new_row = pd.DataFrame(
                [
                    {
                        "plan_name": plan_name,
                        "period_label": item["period_label"],
                        "period_date": item["period_date"],
                        "planned_value": round(item["planned_value"], 2),
                        "actual_value": "",
                        "deviation": "",
                        "completion_pct": "",
                        "note_plan": "Automaticky vygenerovano z kalkulacky",
                        "note_assets": "",
                        "next_step": "",
                        "source": "auto",
                        "is_manual_override": False,
                    }
                ]
            )
            updated_df = pd.concat([updated_df, new_row], ignore_index=True)
            created_count += 1
            continue

        if mode != "overwrite":
            continue

        existing_index = existing_rows.index[0]
        actual_value = updated_df.loc[existing_index, "actual_value"]
        note_assets = updated_df.loc[existing_index, "note_assets"]
        next_step = updated_df.loc[existing_index, "next_step"]
        deviation, completion_pct = calculate_check_metrics(item["planned_value"], actual_value)

        updated_df.loc[existing_index, "period_date"] = item["period_date"]
        updated_df.loc[existing_index, "planned_value"] = round(item["planned_value"], 2)
        updated_df.loc[existing_index, "deviation"] = "" if deviation is None else round(deviation, 2)
        updated_df.loc[existing_index, "completion_pct"] = "" if completion_pct is None else round(completion_pct, 2)
        updated_df.loc[existing_index, "note_plan"] = "Automaticky vygenerovano z kalkulacky"
        updated_df.loc[existing_index, "note_assets"] = note_assets
        updated_df.loc[existing_index, "next_step"] = next_step
        updated_df.loc[existing_index, "source"] = "auto"
        updated_df.loc[existing_index, "is_manual_override"] = False
        updated_count += 1

    return updated_df, created_count, updated_count


def get_long_term_row_status(row: pd.Series) -> str:
    # Jednoduchy textovy status zaznamu.
    source = str(row.get("source", "manual")).strip().lower()
    manual_override = bool(row.get("is_manual_override", False))
    if source == "auto" and manual_override:
        return "Auto + rucni uprava"
    if source == "auto":
        return "Auto"
    return "Manual"


def upsert_long_term_plan(plans_df: pd.DataFrame, row_data: dict) -> pd.DataFrame:
    # Aktualizuje plan podle nazvu nebo vytvori novy.
    existing_index = plans_df.index[plans_df["plan_name"] == row_data["plan_name"]].tolist()
    if existing_index:
        plans_df.loc[existing_index[0], list(row_data.keys())] = list(row_data.values())
        return plans_df
    return pd.concat([plans_df, pd.DataFrame([row_data])], ignore_index=True)


def build_long_term_chart_df(selected_plan: pd.Series, checks_df: pd.DataFrame) -> pd.DataFrame:
    # Sestavi jednoduchou trajektorii planu a skutecnosti pro graf.
    if selected_plan.empty:
        return pd.DataFrame()

    sorted_checks = checks_df.copy()
    if len(sorted_checks) > 0:
        sorted_checks["period_year_sort"] = sorted_checks["period_label"].apply(extract_year)
        sorted_checks["period_date_sort"] = pd.to_datetime(sorted_checks["period_date"], errors="coerce")
        sorted_checks = sorted_checks.sort_values(
            by=["period_year_sort", "period_date_sort", "period_label"],
            na_position="last",
        )

    rows = [
        {
            "Period": str(selected_plan["start_period"]),
            "Planned": pd.to_numeric(selected_plan["start_value"], errors="coerce"),
            "Actual": pd.to_numeric(selected_plan["start_value"], errors="coerce"),
        }
    ]

    for row in sorted_checks.itertuples(index=False):
        actual_value = pd.to_numeric(row.actual_value, errors="coerce")
        rows.append(
            {
                "Period": str(row.period_label),
                "Planned": pd.to_numeric(row.planned_value, errors="coerce"),
                "Actual": actual_value if pd.notna(actual_value) else None,
            }
        )

    rows.append(
        {
            "Period": str(selected_plan["target_period"]),
            "Planned": pd.to_numeric(selected_plan["target_value"], errors="coerce"),
            "Actual": None,
        }
    )

    chart_df = pd.DataFrame(rows).drop_duplicates(subset=["Period"], keep="last")
    return chart_df


settings = load_settings()
language = settings["language"]
base_currency = settings["base_currency"]
date_format_label = settings["date_format"]
visible_columns = settings["visible_columns"]
selected_fx_pairs = settings["fx_pairs"]
show_fx_rates = settings["show_fx_rates"]
apply_theme(settings["theme"])

if not st.session_state.get("market_data_cache_reset_done", False):
    get_ticker_details.clear()
    get_price_history.clear()
    st.session_state["market_data_cache_reset_done"] = True

raw_df = load_portfolio()
watchlist_df = load_watchlist()
analysis_df = load_analysis()
analysis_history_df = load_analysis_history()
long_term_plans_df = load_long_term_plans()
long_term_checks_df = load_long_term_checks()
transactions_df = load_transactions(raw_df)
earnings_df = load_earnings_calendar()

with st.sidebar:
    st.markdown(
        f"""
        <div class="sidebar-brand">
            <div class="sidebar-kicker">Dashboard</div>
            <div class="sidebar-title">{t("app_title", language)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="sidebar-section">Menu</div>', unsafe_allow_html=True)
    current_page = st.radio(
        "Menu",
        ["Dashboard", "Portfolio", "Watchlist", "Planovani", t("earnings", language), t("transactions", language), t("reports", language), t("settings", language)],
        label_visibility="collapsed",
    )

planning_subpage = None
if current_page == "Planovani":
    planning_subpage = st.radio(
        "Podsekce",
        [t("analysis", language), t("long_term_plan", language)],
        index=0,
        horizontal=True,
        key="planning_subpage",
    )

if current_page == t("settings", language):
    render_page_header("Nastaveni", "Ovladej jazyk, menu, formaty a vzhled aplikace.", "System")
    with st.form("settings_form"):
        new_language = st.selectbox(t("language", language), ["cs", "en"], index=["cs", "en"].index(language))
        new_base_currency = st.selectbox(t("base_currency", language), ["USD", "EUR", "CZK"], index=["USD", "EUR", "CZK"].index(base_currency))
        new_date_format = st.selectbox(t("date_format", language), list(DATE_FORMATS.keys()), index=list(DATE_FORMATS.keys()).index(date_format_label))
        new_visible_columns = st.multiselect(
            t("visible_columns", language),
            DEFAULT_VISIBLE_COLUMNS,
            default=visible_columns,
        )
        new_fx_pairs = st.multiselect(
            t("fx_pairs", language),
            list(FX_PAIR_CONFIG.keys()),
            default=selected_fx_pairs,
        )
        new_show_fx_rates = st.checkbox(
            t("show_fx_rates", language),
            value=show_fx_rates,
        )
        new_theme = st.selectbox(t("theme", language), ["dark", "light"], index=["dark", "light"].index(settings["theme"]))
        save_settings_button = st.form_submit_button(t("save_settings", language))

        if save_settings_button:
            settings = {
                "language": new_language,
                "base_currency": new_base_currency,
                "date_format": new_date_format,
                "visible_columns": new_visible_columns or DEFAULT_VISIBLE_COLUMNS,
                "fx_pairs": new_fx_pairs or DEFAULT_FX_PAIRS,
                "show_fx_rates": bool(new_show_fx_rates),
                "theme": new_theme,
            }
            save_settings(settings)
            st.success(t("settings_saved", new_language))
            st.rerun()

if current_page == t("watchlist", language):
    render_page_header("Watchlist", "Decision board pro kandidaty, ktere sledujes pro dalsi krok.", "Market radar")
    watchlist_overview_data = build_watchlist_overview(watchlist_df)
    watchlist_priority_data = sort_watchlist_priority(watchlist_overview_data)
    in_zone_count = int((watchlist_overview_data["Status"] == "V nakupni zone").sum()) if len(watchlist_overview_data) > 0 else 0
    below_zone_count = int((watchlist_overview_data["Status"] == "Pod nakupni zonou").sum()) if len(watchlist_overview_data) > 0 else 0
    total_watchlist = len(watchlist_overview_data)
    nearest_candidate = watchlist_priority_data.iloc[0]["Ticker"] if len(watchlist_priority_data) > 0 else "N/A"
    render_kpi_cards(
        [
            {"label": "Sledovane tituly", "value": str(total_watchlist), "delta": "Aktivni decision board"},
            {"label": "V nakupni zone", "value": str(in_zone_count), "delta": "Okamzite kandidaty", "tone": "positive"},
            {"label": "Pod buy zonou", "value": str(below_zone_count), "delta": "Zajimave pod supportem"},
            {"label": "Prvni kandidat", "value": nearest_candidate, "delta": "Vyber z aktualniho seznamu"},
        ]
    )
    watchlist_overview_tab, watchlist_add_tab, watchlist_edit_tab, watchlist_delete_tab = st.tabs(
        [t("watchlist_overview", language), t("add", language), t("edit", language), t("delete", language)]
    )

    with watchlist_overview_tab:
        overview_df = watchlist_overview_data.copy()
        if len(overview_df) > 0:
            overview_df["Status"] = overview_df["Status"].apply(format_watchlist_badge)
            helper_columns = ["_current_price_value", "_buy_plan_value", "_watchlist_status", "_distance_pct_value"]
            visible_overview_df = overview_df.drop(columns=helper_columns, errors="ignore")
            styled_overview_df = visible_overview_df.style.apply(
                lambda row: style_watchlist_row(overview_df.loc[row.name])[0:len(row)],
                axis=1,
            )
            primary_col, secondary_col = st.columns([1.5, 0.8])
            with primary_col:
                render_section_intro("Decision board", "Hlavni prehled s barevnymi statusy, buy zónami a prioritami.")
                st.dataframe(
                    styled_overview_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config=build_table_column_config(visible_overview_df),
                )
            with secondary_col:
                render_section_intro("Priority", "Rychly shortlist kandidatu, kteri si zaslouzi pozornost.")
                priority_source_df = watchlist_priority_data.copy()
                priority_source_df["Status"] = priority_source_df["Status"].apply(format_watchlist_badge)
                priority_df = priority_source_df[["Ticker", "Status", "Vzdalenost od buy zony"]].head(6)
                st.dataframe(
                    priority_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config=build_table_column_config(priority_df),
                )
        else:
            st.info("Watchlist je prazdny.")

    with watchlist_add_tab:
        with st.form("watchlist_add_form"):
            watch_ticker = st.text_input("Ticker", placeholder="AAPL")
            watch_buy_zone_low = st.number_input("Buy zone od", min_value=0.0, step=0.01)
            watch_buy_zone_high = st.number_input("Buy zone do", min_value=0.0, step=0.01)
            watch_buy_plan = st.number_input("Plan nakupu", min_value=0.0, step=0.01)
            watch_sell_target = st.number_input("Plan prodeje", min_value=0.0, step=0.01)
            watch_note_date = st.date_input("Datum poznamky")
            watch_note_price = st.number_input("Cena v poznamce", min_value=0.0, step=0.01)
            watch_note_text = st.text_input("Poznamka", placeholder="Napriklad vysledky, support, cekam na breakout")
            watch_add_button = st.form_submit_button("Pridat")

            if watch_add_button:
                if not watch_ticker.strip():
                    st.error("Zadej ticker.")
                else:
                    clean_ticker = watch_ticker.strip().upper()
                    existing_match = watchlist_df[watchlist_df["ticker"] == clean_ticker]
                    company_value = existing_match["company"].iloc[0] if "company" in watchlist_df.columns and len(existing_match) > 0 else None
                    yfinance_value = existing_match["yfinance_ticker"].iloc[0] if len(existing_match) > 0 else clean_ticker
                    new_row = pd.DataFrame(
                        [
                            {
                                "ticker": clean_ticker,
                                "company": company_value,
                                "yfinance_ticker": yfinance_value,
                                "buy_zone_low": float(watch_buy_zone_low),
                                "buy_zone_high": float(watch_buy_zone_high),
                                "buy_plan": float(watch_buy_plan),
                                "sell_target": float(watch_sell_target),
                                "note_date": str(watch_note_date),
                                "note_price": float(watch_note_price),
                                "note_text": watch_note_text,
                            }
                        ]
                    )
                    watchlist_df = pd.concat([watchlist_df, new_row], ignore_index=True)
                    save_watchlist(watchlist_df)
                    st.success("Akcie byla pridana do watchlistu.")
                    st.rerun()

    with watchlist_edit_tab:
        if len(watchlist_df) > 0:
            edit_options = [
                f"{row.ticker} | buy zone {row.buy_zone_low}-{row.buy_zone_high} | {format_date_display(row.note_date, date_format_label)}"
                for row in watchlist_df.itertuples(index=True)
            ]
            selected_watch_edit = st.selectbox("Vyber polozku k uprave", edit_options)
            selected_watch_edit_index = edit_options.index(selected_watch_edit)
            selected_watch_row = watchlist_df.iloc[selected_watch_edit_index]
            watch_note_date_value = pd.to_datetime(selected_watch_row["note_date"], errors="coerce")
            if pd.isna(watch_note_date_value):
                watch_note_date_value = pd.Timestamp.today()

            with st.form("watchlist_edit_form"):
                edit_watch_ticker = st.text_input("Ticker ", value=str(selected_watch_row["ticker"]))
                edit_buy_zone_low = st.number_input("Buy zone od ", min_value=0.0, value=safe_number_input_value(selected_watch_row["buy_zone_low"]), step=0.01)
                edit_buy_zone_high = st.number_input("Buy zone do ", min_value=0.0, value=safe_number_input_value(selected_watch_row["buy_zone_high"]), step=0.01)
                edit_buy_plan = st.number_input("Plan nakupu ", min_value=0.0, value=safe_number_input_value(selected_watch_row["buy_plan"]), step=0.01)
                edit_sell_target = st.number_input("Plan prodeje ", min_value=0.0, value=safe_number_input_value(selected_watch_row["sell_target"]), step=0.01)
                edit_note_date = st.date_input("Datum poznamky ", value=watch_note_date_value.date())
                edit_note_price = st.number_input("Cena v poznamce ", min_value=0.0, value=safe_number_input_value(selected_watch_row["note_price"]), step=0.01)
                edit_note_text = st.text_input("Poznamka ", value=str(selected_watch_row["note_text"]) if pd.notna(selected_watch_row["note_text"]) else "")
                watch_edit_button = st.form_submit_button("Ulozit")

                if watch_edit_button:
                    clean_ticker = edit_watch_ticker.strip().upper()
                    existing_yfinance = selected_watch_row["yfinance_ticker"] if pd.notna(selected_watch_row.get("yfinance_ticker", None)) and str(selected_watch_row.get("yfinance_ticker", "")).strip() else clean_ticker
                    watchlist_df.loc[selected_watch_edit_index, "ticker"] = clean_ticker
                    watchlist_df.loc[selected_watch_edit_index, "yfinance_ticker"] = existing_yfinance if clean_ticker == str(selected_watch_row["ticker"]).strip().upper() else clean_ticker
                    watchlist_df.loc[selected_watch_edit_index, "buy_zone_low"] = float(edit_buy_zone_low)
                    watchlist_df.loc[selected_watch_edit_index, "buy_zone_high"] = float(edit_buy_zone_high)
                    watchlist_df.loc[selected_watch_edit_index, "buy_plan"] = float(edit_buy_plan)
                    watchlist_df.loc[selected_watch_edit_index, "sell_target"] = float(edit_sell_target)
                    watchlist_df.loc[selected_watch_edit_index, "note_date"] = str(edit_note_date)
                    watchlist_df.loc[selected_watch_edit_index, "note_price"] = float(edit_note_price)
                    watchlist_df.loc[selected_watch_edit_index, "note_text"] = edit_note_text
                    save_watchlist(watchlist_df)
                    st.success("Watchlist byl upraven.")
                    st.rerun()
        else:
            st.info("Watchlist je prazdny.")

    with watchlist_delete_tab:
        if len(watchlist_df) > 0:
            delete_options = [
                f"{row.ticker} | buy zone {row.buy_zone_low}-{row.buy_zone_high} | {format_date_display(row.note_date, date_format_label)}"
                for row in watchlist_df.itertuples(index=True)
            ]
            selected_watch_delete = st.selectbox("Vyber polozku", delete_options)
            if st.button("Smazat watchlist polozku"):
                selected_watch_delete_index = delete_options.index(selected_watch_delete)
                watchlist_df = watchlist_df.drop(index=selected_watch_delete_index).reset_index(drop=True)
                save_watchlist(watchlist_df)
                st.success("Polozka byla smazana.")
                st.rerun()
        else:
            st.info("Watchlist je prazdny.")

if current_page == "Planovani" and planning_subpage == t("analysis", language):
    render_page_header("Planovani", "Portfolio plan se zamerenim na vybrane firmy, tezi a dalsi rozhodnuti.", "Strategy")
    analysis_overview_df = build_analysis_overview(raw_df, analysis_df, base_currency)
    analysis_tickers = analysis_overview_df["Ticker"].tolist() if len(analysis_overview_df) > 0 else []

    if analysis_overview_df.empty:
        st.info("Zatim nejsou dostupne zadne tickery pro analyzu.")
    else:
        active_status_count = int((analysis_overview_df["Status"] != "N/A").sum())
        review_count = int((analysis_overview_df["Status"] == "Review").sum())
        avg_upside_value = pd.to_numeric(
            analysis_overview_df["Upside %"].astype(str).str.replace(" %", "", regex=False),
            errors="coerce",
        ).mean()
        render_kpi_cards(
            [
                {"label": "Pokryte firmy", "value": str(len(analysis_overview_df)), "delta": "Tituly s detailnim planem"},
                {"label": "Aktivni statusy", "value": str(active_status_count), "delta": "Building / Hold / Review"},
                {"label": "K revizi", "value": str(review_count), "delta": "Ticker ready for review"},
                {"label": "Prumerny upside", "value": format_percent_metric(avg_upside_value), "delta": "Napric sledovanymi firmami"},
            ]
        )
        display_overview_df = analysis_overview_df[
            [
                "Ticker",
                "Spolecnost",
                "Aktualni cena",
                "Prumerna nakupni cena",
                "Cilova cena",
                "Upside %",
                "Status",
                "Conviction",
                "Dalsi akce",
                "Posledni revize",
            ]
        ]
        analysis_selection_key = "analysis_overview_table_selection"
        selected_analysis_ticker = st.session_state.get("analysis_selected_ticker", analysis_tickers[0])
        if selected_analysis_ticker not in analysis_tickers:
            selected_analysis_ticker = analysis_tickers[0]

        selected_plan = analysis_df[analysis_df["ticker"] == selected_analysis_ticker]
        selected_history = analysis_history_df[analysis_history_df["ticker"] == selected_analysis_ticker].copy()
        selected_overview = analysis_overview_df[analysis_overview_df["Ticker"] == selected_analysis_ticker].iloc[0]

        company_name = "N/A"
        if len(selected_plan) > 0 and pd.notna(selected_plan.iloc[0]["company"]):
            company_name = selected_plan.iloc[0]["company"]
        else:
            portfolio_match = raw_df[raw_df["ticker"] == selected_analysis_ticker]
            if len(portfolio_match) > 0 and pd.notna(portfolio_match.iloc[0]["company"]):
                company_name = portfolio_match.iloc[0]["company"]
            else:
                watchlist_match = watchlist_df[watchlist_df["ticker"] == selected_analysis_ticker]
                if len(watchlist_match) > 0 and pd.notna(watchlist_match.iloc[0]["company"]):
                    company_name = watchlist_match.iloc[0]["company"]

        overview_col, detail_col = st.columns([1.45, 1])

        with overview_col:
            render_section_intro("Coverage overview", "Dominantni prehled firem, upside a dalsiho kroku.")
            overview_event = st.dataframe(
                display_overview_df,
                use_container_width=True,
                hide_index=True,
                key=analysis_selection_key,
                on_select="rerun",
                selection_mode="single-row",
                column_config={
                    "Ticker": st.column_config.TextColumn(help="Burzovni zkratka akcie nebo ETF."),
                    "Spolecnost": st.column_config.TextColumn(help="Nazev firmy nebo fondu."),
                    "Aktualni cena": st.column_config.TextColumn(help="Posledni dostupna trzni cena."),
                    "Prumerna nakupni cena": st.column_config.TextColumn(help="Prumerna cena, za kterou mas pozici nakoupenou."),
                    "Cilova cena": st.column_config.TextColumn(help="Cena, na kterou cilis podle sveho investicniho planu."),
                    "Upside %": st.column_config.TextColumn(help="O kolik procent je cilova cena vyse nebo nize oproti aktualni cene."),
                    "Status": st.column_config.TextColumn(help="Aktualni stav tveho planu, napriklad Hold, Review nebo Exit."),
                    "Conviction": st.column_config.TextColumn(help="Jak silne veris investicni tezi pro danou akcii."),
                    "Dalsi akce": st.column_config.TextColumn(help="Co chces udelat jako dalsi krok, napriklad cekat, dokoupit nebo trimovat."),
                    "Posledni revize": st.column_config.TextColumn(help="Kdy jsi plan naposledy upravil."),
                },
            )
            selected_rows = overview_event.selection.get("rows", []) if overview_event and hasattr(overview_event, "selection") else []
            if selected_rows:
                selected_row_index = selected_rows[0]
                selected_analysis_ticker = str(display_overview_df.iloc[selected_row_index]["Ticker"])
                st.session_state["analysis_selected_ticker"] = selected_analysis_ticker
            elif st.session_state.get("analysis_selected_ticker") not in analysis_tickers:
                st.session_state["analysis_selected_ticker"] = analysis_tickers[0]

        selected_analysis_ticker = st.session_state.get("analysis_selected_ticker", selected_analysis_ticker)
        selected_plan = analysis_df[analysis_df["ticker"] == selected_analysis_ticker]
        selected_history = analysis_history_df[analysis_history_df["ticker"] == selected_analysis_ticker].copy()
        selected_overview = analysis_overview_df[analysis_overview_df["Ticker"] == selected_analysis_ticker].iloc[0]

        company_name = "N/A"
        if len(selected_plan) > 0 and pd.notna(selected_plan.iloc[0]["company"]):
            company_name = selected_plan.iloc[0]["company"]
        else:
            portfolio_match = raw_df[raw_df["ticker"] == selected_analysis_ticker]
            if len(portfolio_match) > 0 and pd.notna(portfolio_match.iloc[0]["company"]):
                company_name = portfolio_match.iloc[0]["company"]
            else:
                watchlist_match = watchlist_df[watchlist_df["ticker"] == selected_analysis_ticker]
                if len(watchlist_match) > 0 and pd.notna(watchlist_match.iloc[0]["company"]):
                    company_name = watchlist_match.iloc[0]["company"]

        with detail_col:
            render_section_intro("Vybrana firma", "Detail zvolene pozice a investicniho planu.")
            detail_company_name = company_name if company_name and str(company_name).strip() else "N/A"
            st.markdown(f"### {selected_analysis_ticker}: {detail_company_name}")
            st.write(f"**Aktualni cena:** {selected_overview['Aktualni cena']}")
            st.write(f"**Prumerna nakupni cena:** {selected_overview['Prumerna nakupni cena']}")
            st.write(f"**Cilova cena:** {selected_overview['Cilova cena']}")
            st.write(f"**Upside %:** {selected_overview['Upside %']}")
            st.write(f"**Status:** {selected_overview['Status']}")
            st.write(f"**Conviction:** {selected_overview['Conviction']}")
            st.write(f"**Dalsi akce:** {selected_overview['Dalsi akce']}")

            if len(selected_plan) > 0:
                plan_row = selected_plan.iloc[0]
                st.write(f"**Investicni teze:** {plan_row['investment_thesis'] if pd.notna(plan_row['investment_thesis']) and plan_row['investment_thesis'] else 'N/A'}")
                st.write(f"**Buy plan:** {plan_row['buy_plan'] if pd.notna(plan_row['buy_plan']) and plan_row['buy_plan'] else 'N/A'}")
                st.write(f"**Sell plan:** {plan_row['sell_plan'] if pd.notna(plan_row['sell_plan']) and plan_row['sell_plan'] else 'N/A'}")
                st.write(f"**Risk notes:** {plan_row['risk_notes'] if pd.notna(plan_row['risk_notes']) and plan_row['risk_notes'] else 'N/A'}")
                st.write(f"**Posledni poznamka:** {plan_row['last_note'] if pd.notna(plan_row['last_note']) and plan_row['last_note'] else 'N/A'}")
                st.caption(f"Naposledy upraveno: {format_date_display(plan_row['updated_at'], date_format_label) if pd.notna(plan_row['updated_at']) and str(plan_row['updated_at']).strip() else 'N/A'}")
            else:
                st.info("Pro tento ticker zatim neni ulozeny zadny plan.")

        plan_col, history_col = st.columns([0.95, 1.25])

        with plan_col:
            render_section_intro("Editace planu", "Kompaktni formular ponechany jako sekundarni blok.")
            current_plan = selected_plan.iloc[0] if len(selected_plan) > 0 else pd.Series(dtype=object)

            with st.form("analysis_plan_form"):
                avg_buy_price_value = pd.to_numeric(current_plan.get("avg_buy_price", None), errors="coerce")
                if pd.isna(avg_buy_price_value):
                    portfolio_avg_value = pd.to_numeric(selected_overview["Prumerna nakupni cena"].replace(" %", ""), errors="coerce")
                    avg_buy_price_value = float(portfolio_avg_value) if pd.notna(portfolio_avg_value) else 0.0
                target_price_value = pd.to_numeric(current_plan.get("target_price", None), errors="coerce")
                invalidation_value = pd.to_numeric(current_plan.get("invalidation_level", None), errors="coerce")
                status_value = current_plan.get("status", "") if pd.notna(current_plan.get("status", None)) else ""
                conviction_value = current_plan.get("conviction", "") if pd.notna(current_plan.get("conviction", None)) else ""
                next_action_value = current_plan.get("next_action", "") if pd.notna(current_plan.get("next_action", None)) else ""
                thesis_value = current_plan.get("investment_thesis", "")
                thesis_value = "" if pd.isna(thesis_value) else str(thesis_value)
                buy_plan_value = current_plan.get("buy_plan", "")
                buy_plan_value = "" if pd.isna(buy_plan_value) else str(buy_plan_value)
                sell_plan_value = current_plan.get("sell_plan", "")
                sell_plan_value = "" if pd.isna(sell_plan_value) else str(sell_plan_value)
                risk_notes_value = current_plan.get("risk_notes", "")
                risk_notes_value = "" if pd.isna(risk_notes_value) else str(risk_notes_value)
                last_note_value = current_plan.get("last_note", "")
                last_note_value = "" if pd.isna(last_note_value) else str(last_note_value)

                avg_buy_price_input = st.number_input(
                    "Prumerna nakupni cena",
                    min_value=0.0,
                    value=float(avg_buy_price_value) if pd.notna(avg_buy_price_value) else 0.0,
                    step=0.01,
                    help="Prumerna cena, za kterou mas tuto pozici nakoupenou. Pomaha porovnat, jak daleko je aktualni cena od tveho nakupu.",
                )
                target_price_input = st.number_input(
                    "Cilova cena",
                    min_value=0.0,
                    value=float(target_price_value) if pd.notna(target_price_value) else 0.0,
                    step=0.01,
                    help="Cena, na kterou cilis podle sve teze. Mela by odpovidat tomu, kde vidis ferovou hodnotu nebo misto pro prodej casti pozice.",
                )
                invalidation_input = st.number_input(
                    "Invalidation level",
                    min_value=0.0,
                    value=float(invalidation_value) if pd.notna(invalidation_value) else 0.0,
                    step=0.01,
                    help="Uroven, kde by se tvoje teze prestala potvrzovat. Typicky cena nebo hranice, pri ktere plan znovu prehodnotis.",
                )
                status_input = st.selectbox(
                    "Status",
                    ["N/A", "Building", "Hold", "Review", "Trim", "Exit"],
                    index=["N/A", "Building", "Hold", "Review", "Trim", "Exit"].index(status_value) if status_value in ["N/A", "Building", "Hold", "Review", "Trim", "Exit"] else 0,
                    help="Aktualni stav pozice v planu. Building = budujes pozici, Hold = pouze drzis, Review = chces znovu proverit, Trim = zvazujes ubrani, Exit = uvazujes odchod.",
                )
                conviction_input = st.selectbox(
                    "Conviction",
                    ["N/A", "Low", "Medium", "High"],
                    index=["N/A", "Low", "Medium", "High"].index(conviction_value) if conviction_value in ["N/A", "Low", "Medium", "High"] else 0,
                    help="Jak silne veris sve tezi. Low = nizka jistota, Medium = rozumna duvera, High = vysoka duvera v dlouhodoby plan.",
                )
                next_action_input = st.text_input(
                    "Dalsi akce",
                    value=next_action_value,
                    help="Kratky dalsi konkretni krok. Napriklad: pockat na vysledky, dokoupit pri poklesu, zkontrolovat valuation.",
                    placeholder="Napriklad pockat na pullback k supportu",
                )
                thesis = st.text_area(
                    "Investicni teze",
                    value=thesis_value,
                    help="Proc tuto firmu drzis nebo sledujes. Strucne shrnuti hlavnich duvodu, proc ma investice smysl.",
                    placeholder="Napriklad silny rust cash flow, AI poptavka, kvalitni management...",
                )
                buy_plan = st.text_area(
                    "Buy plan",
                    value=buy_plan_value,
                    help="Za jakych podminek chces prikupovat. Muze obsahovat cenove urovne, valuaci nebo situace, ktere chces videt.",
                    placeholder="Napriklad dalsi nakup pri cene 180-190 USD nebo po potvrzeni rustu marzi",
                )
                sell_plan = st.text_area(
                    "Sell plan",
                    value=sell_plan_value,
                    help="Kdy a proc bys prodaval. Muze jit o cilovou cenu, zhorseni teze nebo prilis vysokou valuaci.",
                    placeholder="Napriklad cast pozice prodat nad 260 USD nebo pri zhorseni fundamentals",
                )
                risk_notes = st.text_area(
                    "Risk notes",
                    value=risk_notes_value,
                    help="Hlavni rizika, ktera mohou plan pokazit. Napriklad dluh, konkurence, regulace, pokles poptavky.",
                    placeholder="Napriklad cyklicnost trhu, tlak na marze, slabe vysledky",
                )
                last_note = st.text_area(
                    "Posledni poznamka",
                    value=last_note_value,
                    help="Posledni kratka poznamka k tomu, co se zmenilo nebo co je potreba sledovat pri dalsi revizi.",
                    placeholder="Napriklad po earnings potvrzen vyhled, dalsi kontrola za 3 mesice",
                )
                save_plan_button = st.form_submit_button("Ulozit plan")

                if save_plan_button:
                    analysis_df = upsert_analysis_row(
                        analysis_df,
                        selected_analysis_ticker,
                        company_name if company_name != "N/A" else "",
                        thesis,
                        buy_plan,
                        sell_plan,
                        risk_notes,
                        last_note,
                    )
                    plan_index = analysis_df.index[analysis_df["ticker"] == selected_analysis_ticker][0]
                    analysis_df.loc[plan_index, "avg_buy_price"] = float(avg_buy_price_input) if avg_buy_price_input else ""
                    analysis_df.loc[plan_index, "target_price"] = float(target_price_input) if target_price_input else ""
                    analysis_df.loc[plan_index, "invalidation_level"] = float(invalidation_input) if invalidation_input else ""
                    analysis_df.loc[plan_index, "status"] = "" if status_input == "N/A" else status_input
                    analysis_df.loc[plan_index, "conviction"] = "" if conviction_input == "N/A" else conviction_input
                    analysis_df.loc[plan_index, "next_action"] = next_action_input
                    save_analysis(analysis_df)
                    st.success("Plan byl ulozen.")
                    st.rerun()

        with history_col:
            render_section_intro("Historie rozhodnuti", "Sekundarni blok pod hlavnim coverage overview.")
            if len(selected_history) > 0:
                selected_history["decision_date"] = selected_history["decision_date"].apply(
                    lambda value: format_date_display(value, date_format_label)
                )
                selected_history = selected_history.rename(
                    columns={
                        "decision_date": "Datum",
                        "decision_type": "Typ",
                        "price": "Cena",
                        "plan_text": "Plan",
                        "comment": "Komentar",
                    }
                )
                st.dataframe(
                    selected_history[["Datum", "Typ", "Cena", "Plan", "Komentar"]],
                    use_container_width=True,
                    hide_index=True,
                    column_config=build_table_column_config(selected_history[["Datum", "Typ", "Cena", "Plan", "Komentar"]]),
                )
            else:
                st.info("Historie rozhodnuti je zatim prazdna.")

        with st.expander("Pridat rozhodnuti"):
            with st.form("analysis_decision_form"):
                decision_date = st.date_input("Datum rozhodnuti")
                decision_type = st.selectbox("Typ rozhodnuti", ["Poznamka", "Revize", "Dokup plan", "Prodej plan"])
                decision_price = st.number_input("Cena", min_value=0.0, step=0.01)
                decision_plan_text = st.text_input("Plan", placeholder="Napriklad cekam na pullback do supportu")
                decision_comment = st.text_area("Komentar", placeholder="Proc menim plan nebo co sleduji")
                save_decision_button = st.form_submit_button("Zapsat rozhodnuti")

                if save_decision_button:
                    new_history_row = pd.DataFrame(
                        [
                            {
                                "ticker": selected_analysis_ticker,
                                "decision_date": str(decision_date),
                                "decision_type": decision_type,
                                "price": float(decision_price),
                                "plan_text": decision_plan_text,
                                "comment": decision_comment,
                            }
                        ]
                    )
                    analysis_history_df = pd.concat([analysis_history_df, new_history_row], ignore_index=True)
                    save_analysis_history(analysis_history_df)
                    st.success("Rozhodnuti bylo ulozeno.")
                    st.rerun()

if current_page == "Planovani" and planning_subpage == t("long_term_plan", language):
    render_page_header("Dlouhodoby plan", "Planning dashboard pro cile, trajektorii majetku a pravidelne kontroly.", "Capital planning")

    if len(long_term_plans_df) > 0:
        total_target_value = float(pd.to_numeric(long_term_plans_df["target_value"], errors="coerce").fillna(0.0).sum())
        total_monthly_contribution = float(pd.to_numeric(long_term_plans_df["monthly_contribution"], errors="coerce").fillna(0.0).sum())
        average_expected_return = float(pd.to_numeric(long_term_plans_df["expected_return_pct"], errors="coerce").dropna().mean()) if len(long_term_plans_df) > 0 else None
        render_kpi_cards(
            [
                {"label": "Aktivni plany", "value": str(len(long_term_plans_df)), "delta": "Dlouhodobe scenare"},
                {"label": "Cilova hodnota", "value": format_currency_metric(total_target_value, base_currency), "delta": "Soucet vsech planu"},
                {"label": "Mesicni vklad", "value": format_currency_metric(total_monthly_contribution, base_currency), "delta": "Kapital flow"},
                {"label": "Prumerny vynos", "value": format_percent_metric(average_expected_return), "delta": "Napric plany"},
            ]
        )
        render_section_intro("Prehled planu", "Horni seznam planu funguje jako vstupni rozcestnik pro detail a kontrolu.")
        st.dataframe(
            long_term_plans_df.rename(
                columns={
                    "plan_name": "Plan",
                    "start_period": "Zacatek",
                    "target_period": "Cilove obdobi",
                    "start_value": "Start value",
                    "target_value": "Target value",
                    "monthly_contribution": "Mesicni vklad",
                    "expected_return_pct": "Ocekavany vynos %",
                    "plan_notes": "Poznamky k planu",
                    "asset_notes": "Poznamky k aktivum",
                }
            ),
            use_container_width=True,
            hide_index=True,
            column_config=build_table_column_config(
                long_term_plans_df.rename(
                    columns={
                        "plan_name": "Plan",
                        "start_period": "Zacatek",
                        "target_period": "Cilove obdobi",
                        "start_value": "Start value",
                        "target_value": "Target value",
                        "monthly_contribution": "Mesicni vklad",
                        "expected_return_pct": "Ocekavany vynos %",
                        "plan_notes": "Poznamky k planu",
                        "asset_notes": "Poznamky k aktivum",
                    }
                )
            ),
        )
    else:
        st.info("Zatim nemas ulozeny zadny dlouhodoby plan.")

    plan_names = long_term_plans_df["plan_name"].tolist() if len(long_term_plans_df) > 0 else []
    planning_mode = st.radio(
        "Rezim planu",
        ["Existujici plan", "Novy plan"],
        horizontal=True,
        key="long_term_plan_page_mode",
    )
    if planning_mode == "Existujici plan" and plan_names:
        selected_plan_name = st.selectbox("Vyber plan", plan_names)
        selected_plan = long_term_plans_df[long_term_plans_df["plan_name"] == selected_plan_name].iloc[0]
        selected_checks = long_term_checks_df[long_term_checks_df["plan_name"] == selected_plan_name].copy()
    else:
        selected_plan_name = None
        selected_plan = pd.Series(dtype=object)
        selected_checks = pd.DataFrame()

    if len(selected_checks) > 0:
        selected_checks["period_year_sort"] = selected_checks["period_label"].apply(extract_year)
        selected_checks["period_date_sort"] = pd.to_datetime(selected_checks["period_date"], errors="coerce")
        selected_checks = selected_checks.sort_values(
            by=["period_year_sort", "period_date_sort", "period_label"],
            na_position="last",
        ).drop(columns=["period_year_sort", "period_date_sort"])

    calculated_years = 10.0
    start_year_for_calc = extract_year(selected_plan.get("start_period", ""))
    target_year_for_calc = extract_year(selected_plan.get("target_period", ""))
    if start_year_for_calc is not None and target_year_for_calc is not None and target_year_for_calc >= start_year_for_calc:
        calculated_years = float(target_year_for_calc - start_year_for_calc + 1)

    top_plan_col, top_calc_col = st.columns([1.35, 0.9])
    with top_plan_col:
        render_section_intro("Trajektorie planu", "Dominantni blok s vyvojem planu a skutecnosti.")
        if selected_plan_name:
            chart_df = build_long_term_chart_df(selected_plan, selected_checks)
            if len(chart_df) > 0:
                chart_fig = go.Figure()
                chart_fig.add_trace(go.Scatter(x=chart_df["Period"], y=chart_df["Planned"], mode="lines+markers", name="Plan"))
                chart_fig.add_trace(go.Scatter(x=chart_df["Period"], y=chart_df["Actual"], mode="lines+markers", name="Skutecnost"))
                chart_fig.update_layout(
                    margin=dict(l=20, r=20, t=20, b=20),
                    xaxis_title="Obdobi",
                    yaxis_title=f"Hodnota ({base_currency})",
                )
                st.plotly_chart(chart_fig, use_container_width=True)
            else:
                st.info("Trajektorie se zobrazi po ulozeni planu nebo kontrol.")
        else:
            st.info("Vyber plan pro zobrazeni trajektorie.")

    with top_calc_col:
        render_section_intro("Kalkulacka", "Kompaktni model budouci hodnoty a rychla kontrola mezery.")
        calc_start_value = st.number_input("Start value", min_value=0.0, value=safe_number_input_value(selected_plan.get("start_value", 0.0)), step=100.0, key="lt_calc_start_value")
        calc_monthly_contribution = st.number_input("Mesicni vklad", min_value=0.0, value=safe_number_input_value(selected_plan.get("monthly_contribution", 0.0)), step=50.0, key="lt_calc_monthly_contribution")
        calc_expected_return = st.number_input("Vynos %", min_value=0.0, value=safe_number_input_value(selected_plan.get("expected_return_pct", 0.0)), step=0.5, key="lt_calc_expected_return")
        calc_years = st.number_input("Pocet let", min_value=0.0, value=calculated_years, step=1.0, key="lt_calc_years")
        future_value = calculate_future_value(calc_start_value, calc_monthly_contribution, calc_expected_return, calc_years)
        completion_avg = pd.to_numeric(selected_checks["completion_pct"], errors="coerce").mean() if len(selected_checks) > 0 else None
        selected_target_value = safe_float(selected_plan.get("target_value", None))
        plan_gap_value = (selected_target_value - future_value) if selected_target_value is not None else None
        st.metric("Budouci hodnota", f"{base_currency} {future_value:,.2f}")
        st.metric("Mezera proti cili", format_currency_metric(plan_gap_value, base_currency))
        st.metric("Prumerne splneni kontrol", format_percent_metric(completion_avg))

    plan_form_col, checks_col = st.columns([0.92, 1.2])

    with plan_form_col:
        render_section_intro("Editace planu", "Formular zustava sekundarni vedle analytickych bloku.")
        if planning_mode == "Novy plan":
            st.caption("Rezim noveho planu: formular je prazdny a ulozeni vytvori novy zaznam.")
        with st.form("long_term_plan_form"):
            plan_name = st.text_input("Nazev planu", value=str(selected_plan.get("plan_name", "")))
            start_period = st.text_input("Zacatek obdobi", value=str(selected_plan.get("start_period", "")), placeholder="Napriklad 2026")
            target_period = st.text_input("Cilove obdobi", value=str(selected_plan.get("target_period", "")), placeholder="Napriklad 2030")
            start_value = st.number_input("Stav na zacatku", min_value=0.0, value=safe_number_input_value(selected_plan.get("start_value", 0.0)), step=100.0)
            target_value = st.number_input("Planovany stav", min_value=0.0, value=safe_number_input_value(selected_plan.get("target_value", 0.0)), step=100.0)
            monthly_contribution = st.number_input("Mesicni vklad", min_value=0.0, value=safe_number_input_value(selected_plan.get("monthly_contribution", 0.0)), step=50.0)
            expected_return_pct = st.number_input("Ocekavany vynos %", min_value=0.0, value=safe_number_input_value(selected_plan.get("expected_return_pct", 0.0)), step=0.5)
            plan_notes = st.text_area("Poznamky k planu", value=str(selected_plan.get("plan_notes", "")))
            asset_notes = st.text_area("Poznamky k vyvoji aktiv", value=str(selected_plan.get("asset_notes", "")))
            save_long_term_plan_button = st.form_submit_button("Ulozit plan")

            if save_long_term_plan_button:
                if not plan_name.strip():
                    st.error("Zadej nazev planu.")
                else:
                    long_term_plans_df = upsert_long_term_plan(
                        long_term_plans_df,
                        {
                            "plan_name": plan_name.strip(),
                            "start_period": start_period,
                            "target_period": target_period,
                            "start_value": float(start_value),
                            "target_value": float(target_value),
                            "monthly_contribution": float(monthly_contribution),
                            "expected_return_pct": float(expected_return_pct),
                            "plan_notes": plan_notes,
                            "asset_notes": asset_notes,
                        },
                    )
                    save_long_term_plans(long_term_plans_df)
                    st.success("Dlouhodoby plan byl ulozen.")
                    st.rerun()

    with checks_col:
        render_section_intro("Kontroly planu", "Operativni prehled odchylek, splneni a dalsich kroku.")
        if selected_plan_name:
            with st.container(border=True):
                st.write("**Automaticke generovani kontrol**")
                st.caption("Pouzije stejnou logiku jako kalkulacka: pocatecni vklad, mesicni vklad, rocni vynos a slozene urocenI. Vytvori konec kazdeho roku jako samostatnou kontrolu.")

                existing_auto_rows = selected_checks[selected_checks["source"].astype(str).str.lower() == "auto"] if len(selected_checks) > 0 else pd.DataFrame()
                if len(selected_checks) > 0:
                    st.warning("Pro tento plan uz kontroly existuji. Muzes bud prepocitat automaticke roky, nebo jen doplnit chybejici.")

                generation_mode = st.radio(
                    "Rezim generovani",
                    [
                        "Doplnit chybejici roky a zachovat rucni upravy",
                        "Prepsat existujici automaticke kontroly",
                    ],
                    horizontal=False,
                    key="long_term_generation_mode",
                )

                if st.button("Automaticky vygenerovat kontroly planu", use_container_width=True):
                    try:
                        mode_value = "fill_missing" if generation_mode.startswith("Doplnit") else "overwrite"
                        long_term_checks_df, created_count, updated_count = generate_long_term_checks(
                            long_term_checks_df,
                            selected_plan,
                            mode_value,
                        )
                        save_long_term_checks(long_term_checks_df)
                        if mode_value == "overwrite":
                            st.success(f"Kontroly byly vygenerovany. Pridano: {created_count}, prepocitano automatickych: {updated_count}.")
                        else:
                            st.success(f"Kontroly byly vygenerovany. Pridano chybejicich roku: {created_count}.")
                        st.rerun()
                    except ValueError as error:
                        st.error(str(error))

            if len(selected_checks) > 0:
                display_checks = selected_checks.copy()
                display_checks["deviation"] = display_checks.apply(
                    lambda row: calculate_check_metrics(row["planned_value"], row["actual_value"])[0],
                    axis=1,
                )
                display_checks["completion_pct"] = display_checks.apply(
                    lambda row: calculate_check_metrics(row["planned_value"], row["actual_value"])[1],
                    axis=1,
                )
                display_checks["Rezim"] = display_checks.apply(get_long_term_row_status, axis=1)
                display_checks["Datum"] = display_checks["period_date"].apply(lambda value: format_date_display(value, date_format_label))
                display_checks["Obdobi"] = display_checks["period_label"]
                display_checks["Plan"] = display_checks["planned_value"]
                display_checks["Skutecnost"] = display_checks["actual_value"].replace("", "N/A")
                display_checks["Odchylka"] = display_checks["deviation"].apply(lambda value: "N/A" if pd.isna(value) else round(float(value), 2))
                display_checks["Splneni %"] = display_checks["completion_pct"].apply(lambda value: "N/A" if pd.isna(value) else f"{float(value):.2f} %")
                display_checks["Poznamka plan"] = display_checks["note_plan"].replace("", "N/A")
                display_checks["Poznamka aktiva"] = display_checks["note_assets"].replace("", "N/A")
                display_checks["Dalsi krok"] = display_checks["next_step"].replace("", "N/A")
                st.dataframe(
                    display_checks[
                        [
                            "Obdobi",
                            "Datum",
                            "Plan",
                            "Skutecnost",
                            "Odchylka",
                            "Splneni %",
                            "Rezim",
                            "Poznamka plan",
                            "Poznamka aktiva",
                            "Dalsi krok",
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True,
                    column_config=build_table_column_config(
                        display_checks[
                            [
                                "Obdobi",
                                "Datum",
                                "Plan",
                                "Skutecnost",
                                "Odchylka",
                                "Splneni %",
                                "Rezim",
                                "Poznamka plan",
                                "Poznamka aktiva",
                                "Dalsi krok",
                            ]
                        ]
                    ),
                )

                edit_options = [
                    f"{row.period_label} | {format_date_display(row.period_date, date_format_label)} | {get_long_term_row_status(pd.Series(row._asdict()))}"
                    for row in selected_checks.itertuples(index=True)
                ]
                selected_check_edit = st.selectbox("Vyber kontrolu k uprave", edit_options)
                selected_check_index = edit_options.index(selected_check_edit)
                selected_check_row = selected_checks.iloc[selected_check_index]
                selected_check_global_index = selected_check_row.name
                selected_check_date = pd.to_datetime(selected_check_row["period_date"], errors="coerce")
                if pd.isna(selected_check_date):
                    selected_check_date = pd.Timestamp.today()
                selected_planned_value = safe_float(selected_check_row["planned_value"])
                if selected_planned_value is None:
                    selected_planned_value = 0.0
                actual_text_value = ""
                if pd.notna(pd.to_numeric(selected_check_row["actual_value"], errors="coerce")):
                    actual_text_value = str(float(pd.to_numeric(selected_check_row["actual_value"], errors="coerce")))

                with st.form("long_term_check_edit_form"):
                    edit_period_label = st.text_input("Obdobi", value=str(selected_check_row["period_label"]))
                    edit_period_date = st.date_input("Datum kontroly", value=selected_check_date.date())
                    edit_planned_value = st.number_input(
                        "Planovana hodnota",
                        min_value=0.0,
                        value=float(selected_planned_value),
                        step=100.0,
                    )
                    edit_actual_value = st.text_input("Skutecna hodnota", value=actual_text_value, placeholder="Nech prazdne, pokud ji jeste neznas")
                    edit_note_plan = st.text_area("Poznamka k planu", value=str(selected_check_row.get("note_plan", "")))
                    edit_note_assets = st.text_area("Poznamka k aktivum", value=str(selected_check_row.get("note_assets", "")))
                    edit_next_step = st.text_input("Dalsi krok", value=str(selected_check_row.get("next_step", "")))
                    save_check_edit_button = st.form_submit_button("Ulozit upravu kontroly")

                    if save_check_edit_button:
                        actual_numeric = safe_float(edit_actual_value)
                        deviation, completion_pct = calculate_check_metrics(edit_planned_value, actual_numeric)
                        long_term_checks_df.loc[selected_check_global_index, "period_label"] = edit_period_label
                        long_term_checks_df.loc[selected_check_global_index, "period_date"] = str(edit_period_date)
                        long_term_checks_df.loc[selected_check_global_index, "planned_value"] = float(edit_planned_value)
                        long_term_checks_df.loc[selected_check_global_index, "actual_value"] = "" if actual_numeric is None else float(actual_numeric)
                        long_term_checks_df.loc[selected_check_global_index, "deviation"] = "" if deviation is None else round(deviation, 2)
                        long_term_checks_df.loc[selected_check_global_index, "completion_pct"] = "" if completion_pct is None else round(completion_pct, 2)
                        long_term_checks_df.loc[selected_check_global_index, "note_plan"] = edit_note_plan
                        long_term_checks_df.loc[selected_check_global_index, "note_assets"] = edit_note_assets
                        long_term_checks_df.loc[selected_check_global_index, "next_step"] = edit_next_step
                        long_term_checks_df.loc[selected_check_global_index, "is_manual_override"] = True
                        save_long_term_checks(long_term_checks_df)
                        st.success("Kontrola planu byla upravena.")
                        st.rerun()
            else:
                st.info("Zatim nejsou zadane zadne kontroly planu.")

            with st.expander("Pridat rucni kontrolu"):
                with st.form("long_term_check_form"):
                    period_label = st.text_input("Obdobi", placeholder="Napriklad 2026 nebo Q1 2027")
                    period_date = st.date_input("Datum kontroly")
                    planned_value = st.number_input("Planovana hodnota", min_value=0.0, step=100.0)
                    actual_value = st.text_input("Skutecna hodnota", placeholder="Volitelne")
                    note_plan = st.text_area("Poznamka k planu")
                    note_assets = st.text_area("Poznamka k vyvoji aktiv")
                    next_step = st.text_input("Dalsi krok")
                    save_check_button = st.form_submit_button("Pridat kontrolu")

                    if save_check_button:
                        actual_numeric = safe_float(actual_value)
                        deviation, completion_pct = calculate_check_metrics(planned_value, actual_numeric)
                        new_check_row = pd.DataFrame(
                            [
                                {
                                    "plan_name": selected_plan_name,
                                    "period_label": period_label,
                                    "period_date": str(period_date),
                                    "planned_value": float(planned_value),
                                    "actual_value": "" if actual_numeric is None else float(actual_numeric),
                                    "deviation": "" if deviation is None else round(deviation, 2),
                                    "completion_pct": "" if completion_pct is None else round(completion_pct, 2),
                                    "note_plan": note_plan,
                                    "note_assets": note_assets,
                                    "next_step": next_step,
                                    "source": "manual",
                                    "is_manual_override": True,
                                }
                            ]
                        )
                        long_term_checks_df = pd.concat([long_term_checks_df, new_check_row], ignore_index=True)
                        save_long_term_checks(long_term_checks_df)
                        st.success("Kontrola planu byla ulozena.")
                        st.rerun()
        else:
            if planning_mode == "Novy plan":
                st.info("Nejdriv uloz novy plan. Potom se zobrazi trajektorie i kontroly.")
            else:
                st.info("Nejdriv uloz alespon jeden plan.")

if current_page == t("earnings", language):
    render_page_header("Vysledky", "Kalendar vysledku firem s auto doplnenim terminu a odhadu a s moznosti rucni upravy.", "Earnings")
    earnings_universe_df = build_earnings_universe(raw_df, watchlist_df, analysis_df)
    portfolio_tickers = set(raw_df["ticker"].astype(str).str.upper().tolist()) if len(raw_df) > 0 else set()
    watchlist_tickers = set(watchlist_df["ticker"].astype(str).str.upper().tolist()) if len(watchlist_df) > 0 else set()

    if len(earnings_universe_df) == 0:
        st.info("V portfoliu, watchlistu ani planu zatim nejsou zadne firmy pro earnings kalendar.")
    else:
        if len(earnings_df) == 0:
            with st.spinner("Nacitam earnings data pro firmy z portfolia a watchlistu..."):
                earnings_df, _ = merge_auto_earnings_data(earnings_df, earnings_universe_df)
                save_earnings_calendar(earnings_df)
                st.rerun()

        known_tickers = set(earnings_df["ticker"].astype(str).str.upper().tolist()) if len(earnings_df) > 0 else set()
        missing_rows = earnings_universe_df[~earnings_universe_df["ticker"].astype(str).str.upper().isin(known_tickers)].copy()
        if len(missing_rows) > 0:
            timestamp_now = datetime.now().strftime("%Y-%m-%d %H:%M")
            for row in missing_rows.itertuples(index=False):
                earnings_df = pd.concat(
                    [
                        earnings_df,
                        pd.DataFrame(
                            [
                                {
                                    "ticker": clean_text_value(row.ticker).upper(),
                                    "company": clean_text_value(row.company),
                                    "yfinance_ticker": clean_text_value(row.yfinance_ticker) or clean_text_value(row.ticker).upper(),
                                    "earnings_date": "",
                                    "earnings_time": "TBD",
                                    "eps_estimate": None,
                                    "revenue_estimate": None,
                                    "eps_actual": None,
                                    "revenue_actual": None,
                                    "eps_surprise_pct": None,
                                    "revenue_surprise_pct": None,
                                    "status": "Bez dat",
                                    "source": "manual",
                                    "is_manual_override": False,
                                    "note": "",
                                    "updated_at": timestamp_now,
                                }
                            ]
                        ),
                    ],
                    ignore_index=True,
                )
            save_earnings_calendar(earnings_df)

        if len(earnings_df) > 0:
            earnings_df["status"] = earnings_df.apply(infer_earnings_status, axis=1)

        upcoming_count = int((earnings_df["status"] == "Ceka se").sum()) if len(earnings_df) > 0 else 0
        today_count = int((earnings_df["status"] == "Dnes").sum()) if len(earnings_df) > 0 else 0
        manual_count = int(earnings_df["is_manual_override"].fillna(False).sum()) if len(earnings_df) > 0 else 0
        reported_count = int((earnings_df["status"] == "Vyhlaseno").sum()) if len(earnings_df) > 0 else 0
        render_kpi_cards(
            [
                {"label": "Sledovane firmy", "value": str(len(earnings_df)), "delta": "Portfolio + watchlist + plan"},
                {"label": "Ceka se", "value": str(upcoming_count), "delta": "Budouci earnings"},
                {"label": "Dnes", "value": str(today_count), "delta": "Vysledky dnes"},
                {"label": "Vyhlaseno", "value": str(reported_count), "delta": "Se skutecnosti"},
            ]
        )

        st.caption("Data se zkousi doplnit automaticky z Yahoo Finance. Kdyz neco chybi nebo chces vlastni cisla, muzes radek rucne upravit a zamknout proti dalsimu prepisu.")
        refresh_col, force_col = st.columns([1.2, 2.4])
        force_override = force_col.checkbox(
            "Pri refreshi prepsat i rucne upravene radky",
            value=False,
            help="Kdyz zapnes, automaticke nacteni prepise i radky, ktere sis rucne zamkl.",
        )
        if refresh_col.button("Obnovit auto data", use_container_width=True):
            with st.spinner("Obnovuji earnings data..."):
                earnings_df, refreshed_tickers = merge_auto_earnings_data(
                    earnings_df,
                    earnings_universe_df,
                    force_manual_override=force_override,
                )
                save_earnings_calendar(earnings_df)
            if refreshed_tickers:
                st.success(f"Auto data obnovena pro: {', '.join(refreshed_tickers)}")
            else:
                st.info("Nebyly nalezeny zadne tickery pro obnovu.")
            st.rerun()

        display_earnings_df = earnings_df.copy()
        if len(display_earnings_df) > 0:
            display_earnings_df["Seznam"] = display_earnings_df["ticker"].apply(
                lambda ticker: classify_earnings_membership(ticker, portfolio_tickers, watchlist_tickers)
            )
            display_earnings_df["Datum vysledku"] = display_earnings_df["earnings_date"].apply(
                lambda value: format_earnings_date_value(value, date_format_label)
            )
            display_earnings_df["Cas"] = display_earnings_df["earnings_time"].apply(normalize_earnings_time_label)
            display_earnings_df["EPS odhad"] = display_earnings_df["eps_estimate"].apply(
                lambda value: "N/A" if pd.isna(value) else f"{float(value):.2f}"
            )
            display_earnings_df["Revenue odhad"] = display_earnings_df["revenue_estimate"].apply(
                lambda value: format_large_number(value) if pd.notna(value) else "N/A"
            )
            display_earnings_df["EPS realita"] = display_earnings_df["eps_actual"].apply(
                lambda value: "N/A" if pd.isna(value) else f"{float(value):.2f}"
            )
            display_earnings_df["Revenue realita"] = display_earnings_df["revenue_actual"].apply(
                lambda value: format_large_number(value) if pd.notna(value) else "N/A"
            )
            display_earnings_df["EPS surprise"] = display_earnings_df["eps_surprise_pct"].apply(
                lambda value: "N/A" if pd.isna(value) else f"{float(value):.2f} %"
            )
            display_earnings_df["Zdroj"] = display_earnings_df.apply(
                lambda row: "Manual lock" if bool(row.get("is_manual_override", False)) else ("Auto" if clean_text_value(row.get("source", "")) == "auto" else "Manual"),
                axis=1,
            )
            display_earnings_df = display_earnings_df.sort_values(by=["earnings_date", "ticker"], na_position="last")

        earnings_tickers = display_earnings_df["ticker"].astype(str).tolist() if len(display_earnings_df) > 0 else earnings_universe_df["ticker"].astype(str).tolist()
        selected_earnings_ticker = st.session_state.get("selected_earnings_ticker", earnings_tickers[0])
        if selected_earnings_ticker not in earnings_tickers:
            selected_earnings_ticker = earnings_tickers[0]

        earnings_selection_key = "earnings_overview_selection"
        overview_col, detail_col = st.columns([1.55, 1.0])

        with overview_col:
            render_section_intro("Earnings kalendar", "Prehled terminu, odhadu analytiku a skutecnosti po vyhlaseni.")
            earnings_overview_df = display_earnings_df[
                [
                    "ticker",
                    "company",
                    "Seznam",
                    "Datum vysledku",
                    "Cas",
                    "EPS odhad",
                    "Revenue odhad",
                    "EPS realita",
                    "Revenue realita",
                    "EPS surprise",
                    "status",
                    "Zdroj",
                ]
            ].rename(
                columns={
                    "ticker": "Ticker",
                    "company": "Spolecnost",
                    "status": "Status",
                }
            ).reset_index(drop=True)
            earnings_overview_event = st.dataframe(
                earnings_overview_df,
                use_container_width=True,
                hide_index=True,
                key=earnings_selection_key,
                on_select="rerun",
                selection_mode="single-row",
                column_config=build_table_column_config(
                    earnings_overview_df
                ),
            )
            selected_rows = earnings_overview_event.selection.get("rows", []) if earnings_overview_event and hasattr(earnings_overview_event, "selection") else []
            if selected_rows:
                selected_row_index = selected_rows[0]
                selected_earnings_ticker = str(earnings_overview_df.iloc[selected_row_index]["Ticker"])
                st.session_state["selected_earnings_ticker"] = selected_earnings_ticker
            elif st.session_state.get("selected_earnings_ticker") not in earnings_tickers:
                st.session_state["selected_earnings_ticker"] = earnings_tickers[0]

        selected_earnings_ticker = st.session_state.get("selected_earnings_ticker", selected_earnings_ticker)
        selected_earnings_row = earnings_df[earnings_df["ticker"] == selected_earnings_ticker].iloc[0]

        with detail_col:
            render_section_intro("Vybrana firma", "Detail zvolene firmy a moznost okamzite manualni upravy.")
            detail_date_text = format_earnings_date_value(selected_earnings_row.get("earnings_date", ""), date_format_label)
            detail_time_text = normalize_earnings_time_label(selected_earnings_row.get("earnings_time", ""))
            detail_eps_estimate = "N/A" if pd.isna(selected_earnings_row.get("eps_estimate")) else f"{float(selected_earnings_row.get('eps_estimate')):.2f}"
            detail_revenue_estimate = format_large_number(selected_earnings_row.get("revenue_estimate")) if pd.notna(selected_earnings_row.get("revenue_estimate")) else "N/A"
            detail_eps_actual = "N/A" if pd.isna(selected_earnings_row.get("eps_actual")) else f"{float(selected_earnings_row.get('eps_actual')):.2f}"
            detail_revenue_actual = format_large_number(selected_earnings_row.get("revenue_actual")) if pd.notna(selected_earnings_row.get("revenue_actual")) else "N/A"
            detail_eps_surprise = "N/A" if pd.isna(selected_earnings_row.get("eps_surprise_pct")) else f"{float(selected_earnings_row.get('eps_surprise_pct')):.2f} %"
            detail_company_name = clean_text_value(selected_earnings_row.get("company", "")) or "N/A"
            detail_membership = classify_earnings_membership(selected_earnings_ticker, portfolio_tickers, watchlist_tickers)
            st.markdown(f"### {selected_earnings_ticker}: {detail_company_name}")
            st.write(f"**Seznam:** {detail_membership}")
            st.write(f"**Datum vysledku:** {detail_date_text}")
            st.write(f"**Cas:** {detail_time_text}")
            st.write(f"**EPS odhad:** {detail_eps_estimate}")
            st.write(f"**Revenue odhad:** {detail_revenue_estimate}")
            st.write(f"**EPS realita:** {detail_eps_actual}")
            st.write(f"**Revenue realita:** {detail_revenue_actual}")
            st.write(f"**EPS surprise:** {detail_eps_surprise}")
            st.write(f"**Status:** {clean_text_value(selected_earnings_row.get('status', '')) or 'N/A'}")
            st.write(f"**Poznamka:** {clean_text_value(selected_earnings_row.get('note', '')) or 'N/A'}")
            st.caption(f"Naposledy aktualizovano: {clean_text_value(selected_earnings_row.get('updated_at', '')) or 'N/A'}")

        edit_col, guide_col = st.columns([1.2, 0.8])
        with edit_col:
            render_section_intro("Rucni uprava", "Auto data muzes upravit a pripadne zamknout proti dalsimu refreshi.")
            if st.button("Doplnit automaticky pro vybranou firmu", use_container_width=False):
                selected_universe = earnings_universe_df[earnings_universe_df["ticker"] == selected_earnings_ticker]
                if len(selected_universe) > 0:
                    with st.spinner("Nacitam auto data pro vybranou firmu..."):
                        earnings_df, _ = merge_auto_earnings_data(earnings_df, selected_universe, force_manual_override=True)
                        save_earnings_calendar(earnings_df)
                    st.success(f"Auto data obnovena pro {selected_earnings_ticker}.")
                    st.rerun()

            current_date_value = pd.to_datetime(selected_earnings_row.get("earnings_date", ""), errors="coerce")
            if pd.isna(current_date_value):
                current_date_value = pd.Timestamp(datetime.now().date())
            current_time_value = normalize_earnings_time_label(selected_earnings_row.get("earnings_time", "")) or "TBD"
            earnings_time_options = ["TBD", "Before open", "After close", "During market"]

            with st.form("earnings_manual_edit_form"):
                manual_use_empty_date = st.checkbox(
                    "Datum vysledku zatim nezname",
                    value=pd.isna(pd.to_datetime(selected_earnings_row.get("earnings_date", ""), errors="coerce")),
                )
                manual_date = st.date_input(
                    "Datum vysledku",
                    value=current_date_value.date(),
                    help="Planovane datum zverejneni vysledku. Kdyz firma termin jeste nema potvrzeny, nech checkbox vyse zapnuty.",
                )
                manual_time = st.selectbox(
                    "Cas",
                    earnings_time_options,
                    index=earnings_time_options.index(current_time_value) if current_time_value in earnings_time_options else 0,
                    help="Kdy firma typicky zverejni vysledky: pred otevrenim trhu, po zavreni nebo behem dne.",
                )
                manual_eps_estimate = st.text_input("EPS odhad", value="" if pd.isna(selected_earnings_row.get("eps_estimate")) else str(selected_earnings_row.get("eps_estimate")))
                manual_revenue_estimate = st.text_input("Revenue odhad", value="" if pd.isna(selected_earnings_row.get("revenue_estimate")) else str(selected_earnings_row.get("revenue_estimate")))
                manual_eps_actual = st.text_input("EPS realita", value="" if pd.isna(selected_earnings_row.get("eps_actual")) else str(selected_earnings_row.get("eps_actual")))
                manual_revenue_actual = st.text_input("Revenue realita", value="" if pd.isna(selected_earnings_row.get("revenue_actual")) else str(selected_earnings_row.get("revenue_actual")))
                manual_eps_surprise = st.text_input("EPS surprise %", value="" if pd.isna(selected_earnings_row.get("eps_surprise_pct")) else str(selected_earnings_row.get("eps_surprise_pct")))
                manual_revenue_surprise = st.text_input("Revenue surprise %", value="" if pd.isna(selected_earnings_row.get("revenue_surprise_pct")) else str(selected_earnings_row.get("revenue_surprise_pct")))
                manual_note = st.text_area(
                    "Poznamka",
                    value=clean_text_value(selected_earnings_row.get("note", "")),
                    help="Vlastni komentar, co sledovat. Napriklad guidance, marze, objednavky nebo komentar managementu.",
                )
                manual_lock = st.checkbox(
                    "Zamknout rucni upravy proti automatickemu refreshi",
                    value=bool(selected_earnings_row.get("is_manual_override", False)),
                )
                save_earnings_button = st.form_submit_button("Ulozit upravu")

                if save_earnings_button:
                    selected_index = earnings_df.index[earnings_df["ticker"] == selected_earnings_ticker][0]
                    earnings_df.loc[selected_index, "earnings_date"] = "" if manual_use_empty_date else str(manual_date)
                    earnings_df.loc[selected_index, "earnings_time"] = manual_time
                    earnings_df.loc[selected_index, "eps_estimate"] = safe_float(manual_eps_estimate)
                    earnings_df.loc[selected_index, "revenue_estimate"] = safe_float(manual_revenue_estimate)
                    earnings_df.loc[selected_index, "eps_actual"] = safe_float(manual_eps_actual)
                    earnings_df.loc[selected_index, "revenue_actual"] = safe_float(manual_revenue_actual)
                    earnings_df.loc[selected_index, "eps_surprise_pct"] = safe_float(manual_eps_surprise)
                    earnings_df.loc[selected_index, "revenue_surprise_pct"] = safe_float(manual_revenue_surprise)
                    earnings_df.loc[selected_index, "note"] = manual_note
                    earnings_df.loc[selected_index, "source"] = "manual"
                    earnings_df.loc[selected_index, "is_manual_override"] = bool(manual_lock)
                    earnings_df.loc[selected_index, "updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    earnings_df.loc[selected_index, "status"] = infer_earnings_status(earnings_df.loc[selected_index])
                    save_earnings_calendar(earnings_df)
                    st.success("Earnings radek byl ulozen.")
                    st.rerun()

        with guide_col:
            render_section_intro("Jak to pouzivat", "Strucna logika cele sekce.")
            st.write("**Auto data:** aplikace zkousi doplnit datum, cas a cast odhadu z Yahoo Finance.")
            st.write("**Rucni uprava:** kdyz neco chybi, cisla muzes doplnit sam.")
            st.write("**Zamek:** zamcene radky se pri beznem refreshi neprepisi.")
            st.write("**Revenue:** kdyz zdroj nedoda trzby, pole nech prazdne a dopln je po vysledcich.")
            st.write("**Poznamka:** hod se na vlastni checklist k earnings callu.")

# Hlavni prehled pracuje se sloucenymi pozicemi.
df = aggregate_portfolio(raw_df)

# Pro kazdy ticker doplni detailni trzni data.
if len(df) > 0:
    details = []

    for row in df.itertuples(index=False):
        try:
            details.append(get_ticker_details(row.yfinance_ticker))
        except Exception:
            details.append(
                {
                    "price": None,
                    "daily_change_pct": None,
                    "daily_change_usd": None,
                    "currency": None,
                    "current_price_usd": None,
                    "one_year": [],
                    "pe": None,
                    "eps": None,
                    "earnings_yield": None,
                    "market_cap": None,
                    "beta": None,
                    "company_live": None,
                    "premarket_price": None,
                    "premarket_change_pct": None,
                }
            )

    details_df = pd.DataFrame(details)
    df = pd.concat([df.reset_index(drop=True), details_df], axis=1)

    # Kdyz v CSV neni nazev firmy, vezme se z online dat.
    if "company" not in df.columns:
        df["company"] = df["company_live"]
    else:
        df["company"] = df["company"].fillna(df["company_live"])

    # Spocita hodnoty portfolia v USD.
    df["cost_usd"] = df["shares"] * df["buy_price"] * df["currency"].map(
        lambda x: get_fx_rate_to_usd(x) if pd.notna(x) else 1.0
    )
    df["value_usd"] = df["shares"] * df["current_price_usd"]
    df["profit_loss_usd"] = df["value_usd"] - df["cost_usd"]
    df["profit_loss_pct"] = (df["profit_loss_usd"] / df["cost_usd"]) * 100
    df["market_cap_text"] = df["market_cap"].apply(format_market_cap)
else:
    df["price"] = []
    df["daily_change_pct"] = []
    df["daily_change_usd"] = []
    df["currency"] = []
    df["current_price_usd"] = []
    df["one_year"] = []
    df["pe"] = []
    df["eps"] = []
    df["earnings_yield"] = []
    df["market_cap"] = []
    df["beta"] = []
    df["premarket_price"] = []
    df["premarket_change_pct"] = []
    df["cost_usd"] = []
    df["value_usd"] = []
    df["profit_loss_usd"] = []
    df["profit_loss_pct"] = []
    df["market_cap_text"] = []

df["daily_change_position_usd"] = df["daily_change_usd"] * df["shares"]
df["daily_change_base"] = df["daily_change_position_usd"].apply(lambda value: convert_from_usd(value, base_currency))
df["value_base"] = df["value_usd"].apply(lambda value: convert_from_usd(value, base_currency))
df["profit_loss_base"] = df["profit_loss_usd"].apply(lambda value: convert_from_usd(value, base_currency))
df["price_display"] = df.apply(lambda row: format_price_with_currency(row["price"], row["currency"]), axis=1) if len(df) > 0 else []
df["premarket_price_display"] = df.apply(
    lambda row: format_price_with_currency(row["premarket_price"], row["currency"]) if pd.notna(row["premarket_price"]) else "N/A",
    axis=1,
) if len(df) > 0 else []
df["buy_price_display"] = df.apply(
    lambda row: format_price_with_currency(row["buy_price"], row["currency"] if pd.notna(row["currency"]) else "USD"),
    axis=1,
) if len(df) > 0 else []
df["company_display"] = df["company"].fillna("").replace("", "N/A")
df["pe_display"] = df["pe"].apply(format_number)
df["eps_display"] = df["eps"].apply(format_number)
df["earnings_yield_display"] = df["earnings_yield"].apply(lambda value: format_number(value, " %"))
df["beta_display"] = df["beta"].apply(format_number)

total_value = df["value_base"].sum()
total_profit_loss = df["profit_loss_base"].sum()
last_updated = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
transaction_ticker_map = build_transaction_ticker_map(raw_df, watchlist_df)
transaction_summary = process_transactions(transactions_df, transaction_ticker_map, base_currency)
open_transaction_tickers = get_open_transaction_tickers(transactions_df)
open_lot_transactions_df = build_open_lot_transactions(transactions_df, open_transaction_tickers)

if current_page == "Dashboard":
    render_page_header("Dashboard", "Executive overview s nejdulezitejsimi metrikami, vykonem, alokaci a top movers.", "Executive overview")
    total_cost_base = convert_from_usd(df["cost_usd"].sum(), base_currency) if len(df) > 0 else 0.0
    total_return_pct = (total_profit_loss / total_cost_base * 100) if total_cost_base else None
    total_daily_change = float(df["daily_change_base"].sum()) if len(df) > 0 else 0.0
    previous_total_value = total_value - total_daily_change
    total_daily_change_pct = (total_daily_change / previous_total_value * 100) if previous_total_value else None
    dashboard_earnings_df = earnings_df.copy() if len(earnings_df) > 0 else pd.DataFrame()
    if len(dashboard_earnings_df) > 0:
        today = pd.Timestamp(datetime.now().date())
        current_week_start = today - pd.to_timedelta(today.weekday(), unit="D")
        next_week_end = current_week_start + pd.Timedelta(days=13)
        dashboard_earnings_df["earnings_date_sort"] = pd.to_datetime(dashboard_earnings_df["earnings_date"], errors="coerce")
        dashboard_earnings_df = dashboard_earnings_df.dropna(subset=["earnings_date_sort"])
        dashboard_earnings_df = dashboard_earnings_df[
            dashboard_earnings_df["earnings_date_sort"] >= today
        ].sort_values("earnings_date_sort")
        dashboard_earnings_df["Firma"] = dashboard_earnings_df["company"].apply(lambda value: clean_text_value(value) or "N/A")
        dashboard_earnings_df["Datum"] = dashboard_earnings_df["earnings_date"].apply(
            lambda value: format_earnings_date_value(value, date_format_label)
        )
    else:
        today = pd.Timestamp(datetime.now().date())
        current_week_start = today - pd.to_timedelta(today.weekday(), unit="D")
        next_week_end = current_week_start + pd.Timedelta(days=13)

    owned_tickers = set(raw_df["ticker"].astype(str).str.upper().tolist()) if len(raw_df) > 0 else set()
    watchlist_tickers = set(watchlist_df["ticker"].astype(str).str.upper().tolist()) if len(watchlist_df) > 0 else set()
    render_kpi_cards(
        [
            {"label": "Hodnota portfolia", "value": format_currency_metric(total_value, base_currency, decimals=0, thousands_sep="."), "delta": "Executive view"},
            {"label": "Denni zmena", "value": format_currency_metric(total_daily_change, base_currency, decimals=0, thousands_sep="."), "delta": f"Vs poslednimu close | {format_percent_metric(total_daily_change_pct)}"},
            {"label": "Celkovy zisk", "value": format_currency_metric(total_profit_loss, base_currency, decimals=0, thousands_sep="."), "delta": format_percent_metric(total_return_pct)},
            {"label": "Zhodnoceni", "value": format_percent_metric(total_return_pct), "delta": "Od nakupu"},
            {"label": "Posledni update", "value": last_updated, "delta": "Live market snapshot"},
        ]
    )

    history_card, side_card = st.columns([1.7, 1])
    with history_card:
        render_section_intro("Vykon portfolia", "Dominantni pohled na cisty vykon portfolia proti SPY.")
        dashboard_history_df, _ = build_transaction_portfolio_history(
            open_lot_transactions_df,
            transaction_ticker_map,
            period="max",
            include_tickers=open_transaction_tickers,
        )
        dashboard_clean_history_df = build_clean_performance_history_from_transactions(
            dashboard_history_df,
            open_lot_transactions_df,
            include_tickers=open_transaction_tickers,
        )
        dashboard_benchmark_df = build_benchmark_history("max", BENCHMARKS["SPY"])
        if not dashboard_clean_history_df.empty and not dashboard_benchmark_df.empty:
            investment_start_date = pd.to_datetime(dashboard_clean_history_df["Date"], errors="coerce").min()
            investment_end_date = pd.to_datetime(dashboard_clean_history_df["Date"], errors="coerce").max()
            if pd.notna(investment_start_date):
                dashboard_benchmark_df = dashboard_benchmark_df[
                    pd.to_datetime(dashboard_benchmark_df["Date"], errors="coerce") >= investment_start_date
                ].copy()
            if pd.notna(investment_end_date):
                dashboard_benchmark_df = dashboard_benchmark_df[
                    pd.to_datetime(dashboard_benchmark_df["Date"], errors="coerce") <= investment_end_date
                ].copy()
            dashboard_compare_df = dashboard_clean_history_df.merge(
                dashboard_benchmark_df[["Date", "benchmark_value"]],
                on="Date",
                how="inner",
            )
            dashboard_compare_df = dashboard_compare_df.dropna(subset=["clean_return_pct", "benchmark_value"])
            dashboard_compare_df["benchmark_return_pct"] = normalize_to_percent(dashboard_compare_df["benchmark_value"])
            dashboard_compare_df = dashboard_compare_df.dropna(subset=["benchmark_return_pct"])
            dashboard_fig = go.Figure()
            dashboard_fig.add_trace(
                go.Scatter(
                    x=dashboard_compare_df["Date"],
                    y=dashboard_compare_df["clean_return_pct"],
                    mode="lines",
                    name="Cisty vykon",
                )
            )
            dashboard_fig.add_trace(
                go.Scatter(
                    x=dashboard_compare_df["Date"],
                    y=dashboard_compare_df["benchmark_return_pct"],
                    mode="lines",
                    name="SPY",
                )
            )
            dashboard_fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), yaxis_title="Cisty vykon (%)", xaxis_title="Datum")
            st.plotly_chart(dashboard_fig, use_container_width=True)
        else:
            st.info("Pro dashboard zatim nejsou dostupna historicka data.")

        render_section_intro("Alokace", "Aktualni rozlozeni portfolia podle nejvetsich pozic.")
        if len(df) > 0 and total_value != 0:
            allocation_fig = px.pie(df, names="ticker", values="value_base", hole=0.62)
            allocation_fig.update_layout(
                margin=dict(l=20, r=20, t=10, b=10),
                showlegend=True,
                height=430,
            )
            st.plotly_chart(allocation_fig, use_container_width=True)
        else:
            st.info("N/A")
    with side_card:
        render_section_intro("Top movers", "Nejlepsi a nejslabsi pohyb dne v kompaktnim prehledu.")
        if len(df) > 0:
            movers_df = df[["ticker", "company_display", "value_base", "daily_change_base", "daily_change_pct"]].copy()
            movers_df = movers_df.rename(
                columns={
                    "ticker": "Ticker",
                    "company_display": "Spolecnost",
                    "value_base": "Aktualni hodnota",
                    "daily_change_base": "Denni pohyb",
                    "daily_change_pct": "Denni pohyb %",
                }
            )
            movers_df["Aktualni hodnota"] = movers_df["Aktualni hodnota"].apply(
                lambda value: format_currency_metric(value, base_currency)
            )
            movers_df["Denni pohyb"] = movers_df["Denni pohyb"].apply(
                lambda value: format_currency_metric(value, base_currency)
            )
            movers_df["Denni pohyb % raw"] = pd.to_numeric(movers_df["Denni pohyb %"], errors="coerce")
            movers_df["Denni pohyb %"] = movers_df["Denni pohyb % raw"].apply(
                lambda value: "N/A" if pd.isna(value) else f"{value:.2f} %"
            )

            top_gainers_df = movers_df[movers_df["Denni pohyb % raw"] > 0].sort_values(
                ["Denni pohyb % raw"], ascending=False
            )
            top_losers_df = movers_df[movers_df["Denni pohyb % raw"] < 0].sort_values(
                ["Denni pohyb % raw"], ascending=True
            )

            st.caption("Top gainers dnes")
            if len(top_gainers_df) > 0:
                st.dataframe(
                    top_gainers_df[["Ticker", "Aktualni hodnota", "Denni pohyb %", "Denni pohyb"]].head(3),
                    use_container_width=True,
                    hide_index=True,
                    column_config=build_table_column_config(top_gainers_df[["Ticker", "Aktualni hodnota", "Denni pohyb %", "Denni pohyb"]].head(3)),
                )
            else:
                st.info("N/A")

            st.caption("Top losers dnes")
            if len(top_losers_df) > 0:
                st.dataframe(
                    top_losers_df[["Ticker", "Aktualni hodnota", "Denni pohyb %", "Denni pohyb"]].head(3),
                    use_container_width=True,
                    hide_index=True,
                    column_config=build_table_column_config(top_losers_df[["Ticker", "Aktualni hodnota", "Denni pohyb %", "Denni pohyb"]].head(3)),
                )
            else:
                st.info("N/A")

            render_section_intro("Dnes vs trh", "Kompaktni procentni srovnani portfolia a hlavnich benchmarku za posledni obchodni den.")
            market_rows = [
                {
                    "Instrument": "Portfolio",
                    "Denni zmena %": "N/A" if total_daily_change_pct is None else f"{total_daily_change_pct:.2f} %",
                    "Rozdil vs portfolio": "N/A",
                }
            ]
            for benchmark_label in ["SPY", "MSCI World ETF", "Nasdaq 100"]:
                benchmark_history = get_price_history(BENCHMARKS[benchmark_label], "5d")
                benchmark_change_pct = get_latest_history_change_pct(benchmark_history)
                difference_vs_portfolio = (
                    None
                    if benchmark_change_pct is None or total_daily_change_pct is None
                    else total_daily_change_pct - benchmark_change_pct
                )
                market_rows.append(
                    {
                        "Instrument": benchmark_label,
                        "Denni zmena %": "N/A" if benchmark_change_pct is None else f"{benchmark_change_pct:.2f} %",
                        "Rozdil vs portfolio": "N/A" if difference_vs_portfolio is None else f"{difference_vs_portfolio:.2f} p. b.",
                    }
                )
            st.dataframe(
                pd.DataFrame(market_rows),
                use_container_width=True,
                hide_index=True,
                column_config=build_table_column_config(pd.DataFrame(market_rows)),
            )

            render_section_intro("Akcni radar", "Kratsi seznam kandidatu z watchlistu a jejich aktualni status.")
            dashboard_watchlist_df = sort_watchlist_priority(build_watchlist_overview(watchlist_df))
            if len(dashboard_watchlist_df) > 0:
                dashboard_watchlist_df["Status"] = dashboard_watchlist_df["Status"].apply(format_watchlist_badge)
                dashboard_watchlist_display = dashboard_watchlist_df[
                    ["Ticker", "Aktualni cena", "Buy zone", "Plan nakupu", "Status"]
                ].head(6)
                dashboard_watchlist_hidden = dashboard_watchlist_df[
                    ["_current_price_value", "_buy_plan_value", "_watchlist_status"]
                ].head(6)

                def style_dashboard_watchlist_row(row: pd.Series) -> list[str]:
                    hidden_row = dashboard_watchlist_hidden.loc[row.name]
                    current_price = hidden_row.get("_current_price_value")
                    buy_plan = hidden_row.get("_buy_plan_value")
                    status = hidden_row.get("_watchlist_status")

                    if pd.notna(current_price) and pd.notna(buy_plan) and current_price <= buy_plan:
                        return ["background-color: rgba(34, 197, 94, 0.22); border-left: 3px solid #22c55e"] * len(row)
                    if status in ["V nakupni zone", "Pod nakupni zonou"]:
                        return ["background-color: rgba(34, 197, 94, 0.12)"] * len(row)
                    return [""] * len(row)

                st.dataframe(
                    dashboard_watchlist_display.style.apply(style_dashboard_watchlist_row, axis=1),
                    use_container_width=True,
                    hide_index=True,
                    column_config=build_table_column_config(dashboard_watchlist_display),
                )
            else:
                st.info("N/A")

            render_section_intro("Earnings tento a pristi tyden", "Jen nejblizsi vysledky, rozdelene na portfolio a watchlist.")
            st.caption("Vlastnene firmy")
            if len(dashboard_earnings_df) > 0:
                owned_all_earnings = dashboard_earnings_df[
                    dashboard_earnings_df["ticker"].astype(str).str.upper().isin(owned_tickers)
                ].copy()
                owned_dashboard_earnings = owned_all_earnings[
                    owned_all_earnings["earnings_date_sort"] <= next_week_end
                ][["Firma", "Datum"]].head(5)
                if len(owned_dashboard_earnings) < 2:
                    owned_dashboard_earnings = owned_all_earnings[["Firma", "Datum"]].head(2)
                if len(owned_dashboard_earnings) > 0:
                    st.dataframe(
                        owned_dashboard_earnings,
                        use_container_width=True,
                        hide_index=True,
                        column_config=build_table_column_config(owned_dashboard_earnings),
                    )
                else:
                    st.info("N/A")
            else:
                st.info("N/A")

            st.caption("Watchlist")
            if len(dashboard_earnings_df) > 0:
                watchlist_all_earnings = dashboard_earnings_df[
                    dashboard_earnings_df["ticker"].astype(str).str.upper().isin(watchlist_tickers - owned_tickers)
                ].copy()
                watchlist_dashboard_earnings = watchlist_all_earnings[
                    watchlist_all_earnings["earnings_date_sort"] <= next_week_end
                ][["Firma", "Datum"]].head(5)
                if len(watchlist_dashboard_earnings) < 2:
                    watchlist_dashboard_earnings = watchlist_all_earnings[["Firma", "Datum"]].head(2)
                if len(watchlist_dashboard_earnings) > 0:
                    st.dataframe(
                        watchlist_dashboard_earnings,
                        use_container_width=True,
                        hide_index=True,
                        column_config=build_table_column_config(watchlist_dashboard_earnings),
                    )
                else:
                    st.info("N/A")
            else:
                st.info("N/A")
        else:
            st.info("N/A")


if current_page == t("transactions", language):
    render_page_header("Transakce", "Evidence obchodu, otevrenych lotu, uzavrenych pozic a danoveho pohledu.", "Execution")
    render_kpi_cards(
        [
            {"label": "Realizovany vysledek", "value": format_currency_metric(transaction_summary["realized_total_base"], base_currency, decimals=0, thousands_sep="."), "delta": "Uzavrene obchody"},
            {"label": "Nerealizovany vysledek", "value": format_currency_metric(transaction_summary["unrealized_total_base"], base_currency, decimals=0, thousands_sep="."), "delta": "Aktualne otevrene pozice"},
            {"label": "Celkovy vysledek", "value": format_currency_metric(transaction_summary["total_result_base"], base_currency, decimals=0, thousands_sep="."), "delta": "Realized + unrealized"},
            {"label": "Uzavrene obchody", "value": str(len(transaction_summary["closed_positions"])), "delta": "FIFO evidence"},
        ]
    )
    all_transactions_tab, open_positions_tab, closed_positions_tab, tax_overview_tab = st.tabs(
        ["Vsechny transakce", "Otevrene pozice", "Uzavrene pozice", "Danovy prehled"]
    )
    open_positions_df = transaction_summary["open_positions"].copy()
    closed_positions_df = transaction_summary["closed_positions"].copy()
    annual_summary_df = transaction_summary["annual_summary"].copy()

    with all_transactions_tab:
        render_section_intro("Vsechny transakce", "Hlavni evidence obchodnich zaznamu a navazujicich uprav.")
        st.caption("Jednoducha evidence transakci. Otevrene a uzavrene pozice se pocitaji metodou FIFO.")
        trans_col1, trans_col2, trans_col3 = st.columns(3)
        trans_col1.metric("Realizovany vysledek", f"{base_currency} {transaction_summary['realized_total_base']:,.2f}")
        trans_col2.metric("Nerealizovany vysledek", f"{base_currency} {transaction_summary['unrealized_total_base']:,.2f}")
        trans_col3.metric("Celkovy vysledek", f"{base_currency} {transaction_summary['total_result_base']:,.2f}")

        st.write("**Vsechny transakce**")
        transactions_display_df = transactions_df.copy()
        if len(transactions_display_df) > 0:
            transactions_display_df["date"] = pd.to_datetime(transactions_display_df["date"], errors="coerce")
            transactions_display_df = transactions_display_df.rename(
                columns={
                    "date": "Datum",
                    "ticker": "Ticker",
                    "company": "Spolecnost",
                    "transaction_type": "Typ",
                    "quantity": "Mnozstvi",
                    "price": "Cena",
                    "currency": "Mena",
                    "buy_fee": "Nakupni poplatek",
                    "sell_fee": "Prodejni poplatek",
                    "fx_fee": "FX poplatek",
                    "tax_fx_rate": "Danovy kurz",
                    "tax_currency": "Danova mena",
                    "broker": "Broker",
                    "note": "Poznamka",
                }
            )
            st.dataframe(
                transactions_display_df,
                use_container_width=True,
                hide_index=True,
                column_config=build_table_column_config(
                    transactions_display_df,
                    {
                    "Datum": st.column_config.DateColumn(format=date_format_label),
                    },
                ),
            )
        else:
            st.info("N/A")

    with all_transactions_tab:
        with st.expander("Pridat transakci"):
            with st.form("transactions_add_form"):
                transaction_type_options = ["buy", "sell", "dividend", "fee", "deposit", "withdrawal"]
                add_col1, add_col2, add_col3, add_col4 = st.columns(4)
                transaction_date = add_col1.date_input("Datum")
                transaction_ticker = add_col2.text_input("Ticker", placeholder="AAPL")
                transaction_company = add_col3.text_input("Spolecnost")
                transaction_type = add_col4.selectbox("Typ transakce", transaction_type_options)

                add_col5, add_col6, add_col7, add_col8 = st.columns(4)
                transaction_quantity = add_col5.number_input("Mnozstvi", value=0.0, step=1.0)
                transaction_price = add_col6.number_input("Cena", value=0.0, step=0.01)
                transaction_currency = add_col7.selectbox("Mena", ["USD", "EUR", "CZK"])
                transaction_broker = add_col8.text_input("Broker", placeholder="Degiro / IBKR")

                add_col9, add_col10, add_col11, add_col12, add_col13 = st.columns(5)
                transaction_buy_fee = add_col9.number_input("Nakupni poplatek", value=0.0, step=0.01)
                transaction_sell_fee = add_col10.number_input("Prodejni poplatek", value=0.0, step=0.01)
                transaction_fx_fee = add_col11.number_input("FX poplatek", value=0.0, step=0.01)
                transaction_tax_fx_rate = add_col12.number_input("Danovy kurz", value=0.0, step=0.0001)
                transaction_tax_currency = add_col13.selectbox("Danova mena", ["CZK", "EUR", "USD"])
                transaction_note = st.text_input("Poznamka")
                add_transaction_button = st.form_submit_button("Pridat transakci")

                if add_transaction_button:
                    new_transaction = pd.DataFrame(
                        [
                            {
                                "date": str(transaction_date),
                                "ticker": transaction_ticker.strip().upper(),
                                "company": transaction_company,
                                "transaction_type": transaction_type,
                                "quantity": float(transaction_quantity),
                                "price": float(transaction_price),
                                "currency": transaction_currency,
                                "buy_fee": float(transaction_buy_fee),
                                "sell_fee": float(transaction_sell_fee),
                                "fx_fee": float(transaction_fx_fee),
                                "tax_fx_rate": float(transaction_tax_fx_rate) if transaction_tax_fx_rate else None,
                                "tax_currency": transaction_tax_currency,
                                "broker": transaction_broker.strip(),
                                "note": transaction_note,
                            }
                        ]
                    )
                    transactions_df = pd.concat([transactions_df, new_transaction], ignore_index=True)
                    save_transactions(transactions_df)
                    st.success("Transakce byla ulozena.")
                    st.rerun()

    with all_transactions_tab:
        with st.expander("Upravit transakci"):
            if len(transactions_df) > 0:
                edit_options = [
                    f"{format_date_display(row.date, date_format_label)} | {row.transaction_type} | {row.ticker} | {row.quantity} @ {row.price}"
                    for row in transactions_df.itertuples(index=False)
                ]
                selected_transaction_edit = st.selectbox("Vyber transakci k uprave", edit_options)
                selected_transaction_index = edit_options.index(selected_transaction_edit)
                selected_transaction_row = transactions_df.iloc[selected_transaction_index]
                transaction_edit_date = pd.to_datetime(selected_transaction_row["date"], errors="coerce")
                if pd.isna(transaction_edit_date):
                    transaction_edit_date = pd.Timestamp.today()

                with st.form("transactions_edit_form"):
                    transaction_type_options = ["buy", "sell", "dividend", "fee", "deposit", "withdrawal"]
                    edit_col1, edit_col2, edit_col3, edit_col4 = st.columns(4)
                    edit_transaction_date = edit_col1.date_input("Datum ", value=transaction_edit_date.date())
                    edit_transaction_ticker = edit_col2.text_input("Ticker ", value=str(selected_transaction_row["ticker"]))
                    edit_transaction_company = edit_col3.text_input("Spolecnost ", value=str(selected_transaction_row["company"]) if pd.notna(selected_transaction_row["company"]) else "")
                    edit_transaction_type = edit_col4.selectbox("Typ transakce ", transaction_type_options, index=transaction_type_options.index(str(selected_transaction_row["transaction_type"])))

                    edit_col5, edit_col6, edit_col7, edit_col8 = st.columns(4)
                    edit_transaction_quantity = edit_col5.number_input("Mnozstvi ", value=float(pd.to_numeric(selected_transaction_row["quantity"], errors="coerce") or 0.0), step=1.0)
                    edit_transaction_price = edit_col6.number_input("Cena ", value=float(pd.to_numeric(selected_transaction_row["price"], errors="coerce") or 0.0), step=0.01)
                    edit_transaction_currency = edit_col7.selectbox("Mena ", ["USD", "EUR", "CZK"], index=["USD", "EUR", "CZK"].index(str(selected_transaction_row["currency"]).upper()) if str(selected_transaction_row["currency"]).upper() in ["USD", "EUR", "CZK"] else 0)
                    edit_transaction_broker = edit_col8.text_input("Broker ", value=str(selected_transaction_row.get("broker", "")) if pd.notna(selected_transaction_row.get("broker", "")) else "")

                    edit_col9, edit_col10, edit_col11, edit_col12, edit_col13 = st.columns(5)
                    edit_transaction_buy_fee = edit_col9.number_input("Nakupni poplatek ", value=float(pd.to_numeric(selected_transaction_row.get("buy_fee"), errors="coerce") or 0.0), step=0.01)
                    edit_transaction_sell_fee = edit_col10.number_input("Prodejni poplatek ", value=float(pd.to_numeric(selected_transaction_row.get("sell_fee"), errors="coerce") or 0.0), step=0.01)
                    edit_transaction_fx_fee = edit_col11.number_input("FX poplatek ", value=float(pd.to_numeric(selected_transaction_row.get("fx_fee"), errors="coerce") or 0.0), step=0.01)
                    edit_transaction_tax_fx_rate = edit_col12.number_input("Danovy kurz ", value=float(pd.to_numeric(selected_transaction_row.get("tax_fx_rate"), errors="coerce") or 0.0), step=0.0001)
                    tax_currency_value = str(selected_transaction_row.get("tax_currency", "CZK")).upper()
                    edit_transaction_tax_currency = edit_col13.selectbox("Danova mena ", ["CZK", "EUR", "USD"], index=["CZK", "EUR", "USD"].index(tax_currency_value) if tax_currency_value in ["CZK", "EUR", "USD"] else 0)
                    edit_transaction_note = st.text_input("Poznamka ", value=str(selected_transaction_row["note"]) if pd.notna(selected_transaction_row["note"]) else "")
                    save_transaction_edit_button = st.form_submit_button("Ulozit transakci")

                    if save_transaction_edit_button:
                        transactions_df.loc[selected_transaction_index, "date"] = str(edit_transaction_date)
                        transactions_df.loc[selected_transaction_index, "ticker"] = edit_transaction_ticker.strip().upper()
                        transactions_df.loc[selected_transaction_index, "company"] = edit_transaction_company
                        transactions_df.loc[selected_transaction_index, "transaction_type"] = edit_transaction_type
                        transactions_df.loc[selected_transaction_index, "quantity"] = float(edit_transaction_quantity)
                        transactions_df.loc[selected_transaction_index, "price"] = float(edit_transaction_price)
                        transactions_df.loc[selected_transaction_index, "currency"] = edit_transaction_currency
                        transactions_df.loc[selected_transaction_index, "buy_fee"] = float(edit_transaction_buy_fee)
                        transactions_df.loc[selected_transaction_index, "sell_fee"] = float(edit_transaction_sell_fee)
                        transactions_df.loc[selected_transaction_index, "fx_fee"] = float(edit_transaction_fx_fee)
                        transactions_df.loc[selected_transaction_index, "tax_fx_rate"] = float(edit_transaction_tax_fx_rate) if edit_transaction_tax_fx_rate else None
                        transactions_df.loc[selected_transaction_index, "tax_currency"] = edit_transaction_tax_currency
                        transactions_df.loc[selected_transaction_index, "broker"] = edit_transaction_broker.strip()
                        transactions_df.loc[selected_transaction_index, "note"] = edit_transaction_note
                        save_transactions(transactions_df)
                        st.success("Transakce byla upravena.")
                        st.rerun()
            else:
                st.info("N/A")

    with all_transactions_tab:
        with st.expander("Smazat transakci"):
            if len(transactions_df) > 0:
                delete_options = [
                    f"{format_date_display(row.date, date_format_label)} | {row.transaction_type} | {row.ticker} | {row.quantity} @ {row.price}"
                    for row in transactions_df.itertuples(index=False)
                ]
                selected_transaction_delete = st.selectbox("Vyber transakci", delete_options)
                if st.button("Smazat transakci"):
                    selected_transaction_delete_index = delete_options.index(selected_transaction_delete)
                    transactions_df = transactions_df.drop(index=selected_transaction_delete_index).reset_index(drop=True)
                    save_transactions(transactions_df)
                    st.success("Transakce byla smazana.")
                    st.rerun()
            else:
                st.info("N/A")

    with open_positions_tab:
        render_section_intro("Otevrene pozice", "Aktualni loty po zapocteni nakupu, prodeju a poplatku.")
        st.caption("Aktualne otevrene loty po zapocteni nakupu, prodeju a poplatku.")
        if len(open_positions_df) > 0:
            open_positions_display = open_positions_df.copy()
            open_positions_display["Prumerna nakupni cena"] = open_positions_display["Prumerna nakupni cena"].apply(lambda value: "N/A" if pd.isna(value) else f"{value:.2f}")
            open_positions_display["Aktualni cena"] = open_positions_display["Aktualni cena"].apply(lambda value: "N/A" if pd.isna(value) else f"{value:.2f}")
            open_positions_display["Current Value"] = open_positions_display["Current Value"].apply(lambda value: "N/A" if pd.isna(value) else f"{base_currency} {value:,.2f}")
            open_positions_display["Nerealizovany zisk / ztrata"] = open_positions_display["Nerealizovany zisk / ztrata"].apply(lambda value: "N/A" if pd.isna(value) else f"{base_currency} {value:,.2f}")
            open_positions_display["Nerealizovany zisk / ztrata %"] = open_positions_display["Nerealizovany zisk / ztrata %"].apply(lambda value: "N/A" if pd.isna(value) else f"{value:.2f} %")
            st.dataframe(
                open_positions_display[
                    [
                        "Ticker",
                        "Spolecnost",
                        "Pocet kusu",
                        "Prumerna nakupni cena",
                        "Aktualni cena",
                        "Current Value",
                        "Nerealizovany zisk / ztrata",
                        "Nerealizovany zisk / ztrata %",
                        "Mena",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
                column_config=build_table_column_config(
                    open_positions_display[
                        [
                            "Ticker",
                            "Spolecnost",
                            "Pocet kusu",
                            "Prumerna nakupni cena",
                            "Aktualni cena",
                            "Current Value",
                            "Nerealizovany zisk / ztrata",
                            "Nerealizovany zisk / ztrata %",
                            "Mena",
                        ]
                    ]
                ),
            )
        else:
            st.info("N/A")

    with closed_positions_tab:
        render_section_intro("Uzavrene pozice", "Historie realizovanych obchodu sparovana metodou FIFO.")
        st.caption("Uzavrene obchody sparovane jednoduse metodou FIFO.")
        if len(closed_positions_df) > 0:
            closed_positions_display = closed_positions_df.copy()
            closed_positions_display["Datum nakupu"] = closed_positions_display["Datum nakupu"].apply(lambda value: format_date_display(value, date_format_label))
            closed_positions_display["Datum prodeje"] = closed_positions_display["Datum prodeje"].apply(lambda value: format_date_display(value, date_format_label))
            closed_positions_display["Prumerna nakupni cena"] = closed_positions_display["Prumerna nakupni cena"].apply(lambda value: "N/A" if pd.isna(value) else f"{value:.2f}")
            closed_positions_display["Prumerna prodejni cena"] = closed_positions_display["Prumerna prodejni cena"].apply(lambda value: "N/A" if pd.isna(value) else f"{value:.2f}")
            closed_positions_display["Poplatky v nastavene mene"] = closed_positions_display["Poplatky v nastavene mene"].apply(lambda value: "N/A" if pd.isna(value) else f"{base_currency} {value:,.2f}")
            closed_positions_display["Realizovany zisk / ztrata"] = closed_positions_display["Realizovany zisk / ztrata"].apply(lambda value: "N/A" if pd.isna(value) else f"{base_currency} {value:,.2f}")
            closed_positions_display["Realizovany zisk / ztrata %"] = closed_positions_display["Realizovany zisk / ztrata %"].apply(lambda value: "N/A" if pd.isna(value) else f"{value:.2f} %")
            closed_positions_display["Broker"] = closed_positions_display["Broker"].fillna("N/A").replace("", "N/A")
            closed_positions_display["Poznamka"] = closed_positions_display["Poznamka"].fillna("N/A").replace("", "N/A")
            st.dataframe(
                closed_positions_display[
                    [
                        "Ticker",
                        "Spolecnost",
                        "Datum nakupu",
                        "Datum prodeje",
                        "Pocet kusu",
                        "Prumerna nakupni cena",
                        "Prumerna prodejni cena",
                        "Poplatky v nastavene mene",
                        "Realizovany zisk / ztrata",
                        "Realizovany zisk / ztrata %",
                        "Rok realizace",
                        "Mena",
                        "Broker",
                        "Poznamka",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
                column_config=build_table_column_config(
                    closed_positions_display[
                        [
                            "Ticker",
                            "Spolecnost",
                            "Datum nakupu",
                            "Datum prodeje",
                            "Pocet kusu",
                            "Prumerna nakupni cena",
                            "Prumerna prodejni cena",
                            "Poplatky v nastavene mene",
                            "Realizovany zisk / ztrata",
                            "Realizovany zisk / ztrata %",
                            "Mena",
                            "Broker",
                            "Poznamka",
                        ]
                    ]
                ),
            )
        else:
            st.info("N/A")

    with tax_overview_tab:
        render_section_intro("Danovy prehled", "Rocni souhrn uzavrenych obchodu a export pracovniho prehledu.")
        st.caption("Jednoduchy evidencni danovy prehled z uzavrenych obchodu. Neni to plna danova legislativa, ale prakticky rocni souhrn.")
        st.caption("Podle Financni spravy se u cennych papiru nejdriv posuzuje limit prijmu 100 000 Kc a az potom casovy test; osvobozeni nelze kombinovat. Sloupce mimo 3lety test proto ber jako orientacni pracovni pohled.")
        if len(annual_summary_df) > 0:
            tax_summary_display = annual_summary_df.copy()
            tax_summary_display["Prodejni obrat"] = tax_summary_display["Prodejni obrat"].apply(lambda value: "N/A" if pd.isna(value) else f"{base_currency} {value:,.2f}")
            tax_summary_display["Realizovany vysledek mimo 3lety test"] = tax_summary_display["Realizovany vysledek mimo 3lety test"].apply(lambda value: "N/A" if pd.isna(value) else f"{base_currency} {value:,.2f}")
            tax_summary_display["Poplatky mimo 3lety test"] = tax_summary_display["Poplatky mimo 3lety test"].apply(lambda value: "N/A" if pd.isna(value) else f"{base_currency} {value:,.2f}")
            tax_summary_display["Realizovane zisky"] = tax_summary_display["Realizovane zisky"].apply(lambda value: "N/A" if pd.isna(value) else f"{base_currency} {value:,.2f}")
            tax_summary_display["Realizovane ztraty"] = tax_summary_display["Realizovane ztraty"].apply(lambda value: "N/A" if pd.isna(value) else f"{base_currency} {value:,.2f}")
            tax_summary_display["Realizovany vysledek"] = tax_summary_display["Realizovany vysledek"].apply(lambda value: "N/A" if pd.isna(value) else f"{base_currency} {value:,.2f}")
            tax_summary_display["Poplatky"] = tax_summary_display["Poplatky"].apply(lambda value: "N/A" if pd.isna(value) else f"{base_currency} {value:,.2f}")
            tax_summary_export_df = tax_summary_display[
                [
                    "Rok realizace",
                    "Prodejni obrat",
                    "Realizovany vysledek mimo 3lety test",
                    "Poplatky mimo 3lety test",
                    "Realizovane zisky",
                    "Realizovane ztraty",
                    "Realizovany vysledek",
                    "Poplatky",
                    "Pocet uzavrenych obchodu",
                ]
            ].copy()

            annual_excel_export_bytes = None
            annual_pdf_export_bytes = None
            annual_excel_export_error = None
            annual_pdf_export_error = None

            try:
                annual_excel_export_bytes = dataframe_to_excel_bytes(tax_summary_export_df, sheet_name="Rocni souhrn")
            except RuntimeError as exc:
                annual_excel_export_error = str(exc)

            try:
                annual_pdf_export_bytes = dataframe_to_pdf_bytes(tax_summary_export_df, title="Danovy prehled - Rocni souhrn")
            except RuntimeError as exc:
                annual_pdf_export_error = str(exc)

            toolbar_title_col, toolbar_spacer_col, toolbar_csv_col, toolbar_excel_col, toolbar_pdf_col = st.columns(
                [2.4, 8.6, 1.1, 1.1, 1.1]
            )
            with toolbar_title_col:
                st.markdown('<span class="fake-toolbar-anchor"></span><div class="fake-toolbar-title">Rocni souhrn</div>', unsafe_allow_html=True)
            with toolbar_csv_col:
                st.download_button(
                    "CSV",
                    data=tax_summary_export_df.to_csv(index=False).encode("utf-8-sig"),
                    file_name="danovy_prehled_rocni_souhrn.csv",
                    mime="text/csv",
                    key="annual_summary_toolbar_csv",
                    use_container_width=True,
                )
            with toolbar_excel_col:
                if annual_excel_export_bytes is not None:
                    st.download_button(
                        "XLSX",
                        data=annual_excel_export_bytes,
                        file_name="danovy_prehled_rocni_souhrn.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="annual_summary_toolbar_excel",
                        use_container_width=True,
                    )
                elif annual_excel_export_error:
                    st.caption(annual_excel_export_error)
            with toolbar_pdf_col:
                if annual_pdf_export_bytes is not None:
                    st.download_button(
                        "PDF",
                        data=annual_pdf_export_bytes,
                        file_name="danovy_prehled_rocni_souhrn.pdf",
                        mime="application/pdf",
                        key="annual_summary_toolbar_pdf",
                        use_container_width=True,
                    )
                elif annual_pdf_export_error:
                    st.caption(annual_pdf_export_error)

            st.dataframe(
                tax_summary_export_df,
                use_container_width=True,
                hide_index=True,
                column_config=build_table_column_config(tax_summary_export_df),
            )

            available_tax_years = tax_summary_display["Rok realizace"].dropna().astype(str).tolist()
            selected_tax_year = st.selectbox("Vyber rok", available_tax_years)

            tax_year_df = closed_positions_df[closed_positions_df["Rok realizace"].astype(str) == str(selected_tax_year)].copy()
            selected_tax_summary = annual_summary_df[annual_summary_df["Rok realizace"].astype(str) == str(selected_tax_year)]
            if len(selected_tax_summary) > 0:
                selected_turnover = selected_tax_summary["Prodejni obrat"].iloc[0]
                turnover_text = "N/A" if pd.isna(selected_turnover) else f"{base_currency} {selected_turnover:,.2f}"
                st.caption(f"Prodejni obrat za rok {selected_tax_year}: {turnover_text}. Limit 100 000 Kc pro cesky casovy test / oznameni ber jen orientacne, presny danovy pohled zavisi na tvych kurzech a dalsich okolnostech.")
            st.write("**Detail uzavrenych obchodu pro vybrany rok**")
            if len(tax_year_df) > 0:
                tax_year_display = tax_year_df.copy()
                tax_year_display["Datum nakupu"] = tax_year_display["Datum nakupu"].apply(lambda value: format_date_display(value, date_format_label))
                tax_year_display["Datum prodeje"] = tax_year_display["Datum prodeje"].apply(lambda value: format_date_display(value, date_format_label))
                tax_year_display["3lety test"] = tax_year_display["3lety test"].fillna("N/A").replace("", "N/A")
                tax_year_display["Prumerna nakupni cena"] = tax_year_display["Prumerna nakupni cena"].apply(lambda value: "N/A" if pd.isna(value) else f"{value:.2f}")
                tax_year_display["Prumerna prodejni cena"] = tax_year_display["Prumerna prodejni cena"].apply(lambda value: "N/A" if pd.isna(value) else f"{value:.2f}")
                tax_year_display["Prodejni obrat"] = tax_year_display["Prodejni obrat"].apply(lambda value: "N/A" if pd.isna(value) else f"{base_currency} {value:,.2f}")
                tax_year_display["Realizovany vysledek mimo 3lety test"] = tax_year_display["Realizovany vysledek mimo 3lety test"].apply(lambda value: "N/A" if pd.isna(value) else f"{base_currency} {value:,.2f}")
                tax_year_display["Poplatky mimo 3lety test"] = tax_year_display["Poplatky mimo 3lety test"].apply(lambda value: "N/A" if pd.isna(value) else f"{base_currency} {value:,.2f}")
                tax_year_display["Poplatky v nastavene mene"] = tax_year_display["Poplatky v nastavene mene"].apply(lambda value: "N/A" if pd.isna(value) else f"{base_currency} {value:,.2f}")
                tax_year_display["Realizovany zisk / ztrata"] = tax_year_display["Realizovany zisk / ztrata"].apply(lambda value: "N/A" if pd.isna(value) else f"{base_currency} {value:,.2f}")
                tax_year_display["Broker"] = tax_year_display["Broker"].fillna("N/A").replace("", "N/A")
                tax_year_display["Poznamka"] = tax_year_display["Poznamka"].fillna("N/A").replace("", "N/A")

                tax_export_df = tax_year_display[
                    [
                        "Ticker",
                        "Spolecnost",
                        "Datum nakupu",
                        "Datum prodeje",
                        "3lety test",
                        "Pocet kusu",
                        "Prumerna nakupni cena",
                        "Prumerna prodejni cena",
                        "Prodejni obrat",
                        "Realizovany vysledek mimo 3lety test",
                        "Poplatky mimo 3lety test",
                        "Poplatky v nastavene mene",
                        "Realizovany zisk / ztrata",
                        "Mena",
                        "Broker",
                        "Poznamka",
                    ]
                ].rename(columns={"Poplatky v nastavene mene": "Poplatky"})

                st.dataframe(
                    tax_export_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config=build_table_column_config(tax_export_df),
                )
                excel_export_bytes = None
                pdf_export_bytes = None
                excel_export_error = None
                pdf_export_error = None

                try:
                    excel_export_bytes = dataframe_to_excel_bytes(tax_export_df, sheet_name="Danovy prehled")
                except RuntimeError as exc:
                    excel_export_error = str(exc)

                try:
                    pdf_export_bytes = dataframe_to_pdf_bytes(tax_export_df, title=f"Danovy prehled {selected_tax_year}")
                except RuntimeError as exc:
                    pdf_export_error = str(exc)

                csv_col, excel_col, pdf_col = st.columns(3)
                with csv_col:
                    st.download_button(
                        "Export CSV",
                        data=tax_export_df.to_csv(index=False).encode("utf-8-sig"),
                        file_name=f"danovy_prehled_{selected_tax_year}.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )
                with excel_col:
                    if excel_export_bytes is not None:
                        st.download_button(
                            "Export Excel",
                            data=excel_export_bytes,
                            file_name=f"danovy_prehled_{selected_tax_year}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True,
                        )
                    elif excel_export_error:
                        st.caption(excel_export_error)
                with pdf_col:
                    if pdf_export_bytes is not None:
                        st.download_button(
                            "Export PDF",
                            data=pdf_export_bytes,
                            file_name=f"danovy_prehled_{selected_tax_year}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )
                    elif pdf_export_error:
                        st.caption(pdf_export_error)
            else:
                st.info("N/A")
        else:
            st.info("N/A")

if current_page == t("reports", language):
    render_page_header("Reporty", "Vykonnost, benchmark, zmeny a riziko v premium reportovacim rozlozeni.", "Insights")
    reports_total_result_base = transaction_summary["total_result_base"]
    reports_total_cost_base = total_value - total_profit_loss
    reports_total_return_pct = (reports_total_result_base / reports_total_cost_base * 100) if reports_total_cost_base else None
    render_kpi_cards(
        [
            {"label": "Hodnota portfolia", "value": format_currency_metric(total_value, base_currency, decimals=0, thousands_sep="."), "delta": "Aktualni snapshot"},
            {"label": "Celkovy vysledek", "value": format_currency_metric(reports_total_result_base, base_currency, decimals=0, thousands_sep="."), "delta": "Vcetne realizovanych pozic"},
            {"label": "Zhodnoceni", "value": format_percent_metric(reports_total_return_pct), "delta": "Vcetne realizovanych pozic"},
            {"label": "Posledni update", "value": last_updated, "delta": "Reporting layer"},
        ]
    )
    report_summary_tab, report_performance_tab, report_benchmark_tab, report_changes_tab, report_risk_tab = st.tabs(
        ["Souhrn", "Vykon", "Benchmark", "Zmeny", "Riziko"]
    )

    with report_summary_tab:
        render_section_intro("Executive summary", "Rychly souhrn portfolia, pozic a vysledku.")
        st.caption("Rychly souhrn aktualniho stavu portfolia a nejdulezitejsich metrik.")
        summary_col1, summary_col2, summary_col3 = st.columns(3)
        summary_col1.metric("Aktualni hodnota portfolia", f"{base_currency} {total_value:,.2f}")
        summary_col2.metric("Celkovy zisk / ztrata", f"{base_currency} {total_profit_loss:,.2f}")
        total_return_pct = (total_profit_loss / (total_value - total_profit_loss) * 100) if (total_value - total_profit_loss) else None
        summary_col3.metric("Zhodnoceni v %", "N/A" if total_return_pct is None else f"{total_return_pct:.2f} %")

        detail_col1, detail_col2, detail_col3 = st.columns(3)
        valid_positions_df = df.dropna(subset=["profit_loss_pct"]) if len(df) > 0 else pd.DataFrame()
        if len(valid_positions_df) > 0:
            best_position = valid_positions_df.loc[valid_positions_df["profit_loss_pct"].idxmax()]
            worst_position = valid_positions_df.loc[valid_positions_df["profit_loss_pct"].idxmin()]
            detail_col1.metric("Nejlepsi pozice", f"{best_position['ticker']} ({best_position['profit_loss_pct']:.2f} %)")
            detail_col2.metric("Nejhorsi pozice", f"{worst_position['ticker']} ({worst_position['profit_loss_pct']:.2f} %)")
        else:
            detail_col1.metric("Nejlepsi pozice", "N/A")
            detail_col2.metric("Nejhorsi pozice", "N/A")
        detail_col3.metric(t("last_updated", language), last_updated)

        result_col1, result_col2, result_col3 = st.columns(3)
        result_col1.metric("Realizovany vysledek", f"{base_currency} {transaction_summary['realized_total_base']:,.2f}")
        result_col2.metric("Nerealizovany vysledek", f"{base_currency} {transaction_summary['unrealized_total_base']:,.2f}")
        result_col3.metric("Celkovy vysledek", f"{base_currency} {transaction_summary['total_result_base']:,.2f}")

    with report_performance_tab:
        render_section_intro("Vykon", "Hlavni graf a tabulka cisteho vykonu proti portfolio value.")
        st.caption("Zmena hodnoty ukazuje, o kolik se portfolio zvetsilo nebo zmensilo. Cisty vykon se snazi odfiltrovat vliv novych nakupu. Radky 2025, 2024 a 2023 predstavuji cele kalendarni roky.")
        full_history_df, missing_report_tickers = build_transaction_portfolio_history(
            open_lot_transactions_df,
            transaction_ticker_map,
            period="max",
            include_tickers=open_transaction_tickers,
        )
        clean_history_df = build_clean_performance_history_from_transactions(
            full_history_df,
            open_lot_transactions_df,
            include_tickers=open_transaction_tickers,
        )
        full_history_with_closed_df, _ = build_transaction_portfolio_history(
            transactions_df,
            transaction_ticker_map,
            period="max",
            include_tickers=None,
        )
        clean_with_closed_history_df = build_clean_with_closed_history(
            clean_history_df,
            transaction_summary["closed_positions"],
        )
        smooth_clean_with_closed_history_df = build_account_clean_performance_history(
            full_history_with_closed_df,
            transactions_df,
            include_tickers=None,
        )
        spy_history_df = build_benchmark_history("max", BENCHMARKS["SPY"])
        msci_history_df = build_benchmark_history("max", BENCHMARKS["MSCI World ETF"])
        performance_view = st.radio(
            "Zobrazeni",
            ["Cisty vykon", "Hodnota portfolia", "Oboje"],
            horizontal=True,
            key="report_performance_view",
        )
        performance_rows = build_report_performance_rows(
            full_history_df,
            clean_history_df,
            transaction_summary["closed_positions"],
            spy_history_df,
            msci_history_df,
            float(df["daily_change_position_usd"].sum()) if len(df) > 0 else 0.0,
            float((df["daily_change_base"].sum() / (total_value - df["daily_change_base"].sum()) * 100)) if len(df) > 0 and (total_value - df["daily_change_base"].sum()) else 0.0,
        )
        performance_rows["Zmena hodnoty"] = performance_rows["value_change_usd"].apply(
            lambda value: "N/A" if pd.isna(value) or value is None else f"{base_currency} {convert_from_usd(value, base_currency):,.2f}"
        )
        performance_rows["Zmena hodnoty %"] = performance_rows["value_change_pct"].apply(
            lambda value: "N/A" if pd.isna(value) or value is None else f"{value:.2f} %"
        )
        performance_rows["Cisty vykon %"] = performance_rows["clean_performance_pct"].apply(
            lambda value: "N/A" if pd.isna(value) or value is None else f"{value:.2f} %"
        )
        performance_rows["Cisty vykon vc. uzavrenych pozic v penezich"] = performance_rows["clean_with_closed_value_usd"].apply(
            lambda value: "N/A" if pd.isna(value) or value is None else f"{base_currency} {convert_from_usd(value, base_currency):,.2f}"
        )
        performance_rows["Cisty vykon aktualniho portfolia %"] = performance_rows["clean_performance_pct"].apply(
            lambda value: "N/A" if pd.isna(value) or value is None else f"{value:.2f} %"
        )
        performance_rows["Cisty vykon vc. uzavrenych pozic %"] = performance_rows["clean_with_closed_pct"].apply(
            lambda value: "N/A" if pd.isna(value) or value is None else f"{value:.2f} %"
        )
        performance_rows["SPY %"] = performance_rows["spy_pct"].apply(
            lambda value: "N/A" if pd.isna(value) or value is None else f"{value:.2f} %"
        )
        performance_rows["MSCI World ETF %"] = performance_rows["msci_pct"].apply(
            lambda value: "N/A" if pd.isna(value) or value is None else f"{value:.2f} %"
        )
        st.caption("SPY slouzi jako jednoducha proxy pro S&P 500. MSCI World ETF je zde reprezentovany tickerem URTH. Cisty vykon vc. uzavrenych pozic navic pripocte realizovany vysledek uzavrenych obchodu za stejne obdobi.")

        performance_columns = ["Obdobi"]
        if performance_view in ["Hodnota portfolia", "Oboje"]:
            performance_columns.extend(["Zmena hodnoty", "Zmena hodnoty %"])
        if performance_view in ["Cisty vykon", "Oboje"]:
            performance_columns.extend([
                "Cisty vykon vc. uzavrenych pozic v penezich",
                "Cisty vykon vc. uzavrenych pozic %",
                "SPY %",
                "MSCI World ETF %",
                "Cisty vykon aktualniho portfolia %",
            ])

        st.dataframe(
            performance_rows[performance_columns],
            use_container_width=True,
            hide_index=True,
            column_config=build_table_column_config(performance_rows[performance_columns]),
        )

        if missing_report_tickers:
            st.info(f"Nektere tickery chybely v historickych datech: {', '.join(missing_report_tickers)}")
        if performance_view in ["Cisty vykon", "Oboje"] and clean_history_df.empty:
            st.info("Cisty vykon se zatim nepodarilo spolehlive spocitat z dostupnych dat.")
        if performance_view in ["Cisty vykon", "Oboje"] and (spy_history_df.empty or msci_history_df.empty):
            st.info("Nektery benchmark nema dost historickych dat pro vsechna obdobi, proto muze byt v tabulce N/A.")

        if not full_history_df.empty:
            chart_history = full_history_df.copy()
            chart_history["portfolio_value_base"] = chart_history["portfolio_value"].apply(lambda value: convert_from_usd(value, base_currency))
            performance_fig = go.Figure()
            if performance_view in ["Hodnota portfolia", "Oboje"]:
                performance_fig.add_trace(
                    go.Scatter(
                        x=chart_history["Date"],
                        y=chart_history["portfolio_value_base"],
                        mode="lines",
                        name="Hodnota portfolia",
                        yaxis="y",
                    )
                )
            if performance_view in ["Cisty vykon", "Oboje"] and not clean_history_df.empty:
                performance_fig.add_trace(
                    go.Scatter(
                        x=clean_history_df["Date"],
                        y=clean_history_df["clean_return_pct"],
                        mode="lines",
                        name="Cisty vykon aktualniho portfolia",
                        yaxis="y2" if performance_view == "Oboje" else "y",
                    )
                )
            if performance_view in ["Cisty vykon", "Oboje"] and not clean_with_closed_history_df.empty:
                performance_fig.add_trace(
                    go.Scatter(
                        x=smooth_clean_with_closed_history_df["Date"] if not smooth_clean_with_closed_history_df.empty else clean_with_closed_history_df["Date"],
                        y=smooth_clean_with_closed_history_df["clean_return_pct"] if not smooth_clean_with_closed_history_df.empty else clean_with_closed_history_df["clean_with_closed_pct"],
                        mode="lines",
                        name="Cisty vykon vc. uzavrenych pozic",
                        yaxis="y2" if performance_view == "Oboje" else "y",
                    )
                )
            performance_fig.update_layout(
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis_title="Datum",
            )
            if performance_view == "Hodnota portfolia":
                performance_fig.update_layout(yaxis_title=f"Hodnota ({base_currency})")
            elif performance_view == "Cisty vykon":
                performance_fig.update_layout(yaxis_title="Cisty vykon (%)")
            else:
                performance_fig.update_layout(
                    yaxis=dict(title=f"Hodnota ({base_currency})"),
                    yaxis2=dict(title="Cisty vykon (%)", overlaying="y", side="right"),
                )
            st.plotly_chart(performance_fig, use_container_width=True)
        else:
            st.info("Historicky vykon portfolia zatim nelze bezpecne spocitat z dostupnych dat.")

        st.caption("Omezeni: cisty vykon je nově stavěný z transakcni historie otevrenych pozic, buy/sell cash flow a dividend. Je výrazne presnejsi nez puvodni verze z portfolio.csv, ale stale nejde o plny account-level TWR, protoze aplikace nevede samostatny cash ucet.")

    with report_benchmark_tab:
        render_section_intro("Benchmark srovnani", "Portfolio proti zvolenemu benchmarku od stejneho startu.")
        st.caption("Srovnani portfolia a benchmarku jako vykon v % od stejneho pocatecniho bodu.")
        benchmark_period_options = ["1 mesic", "3 mesice", "1 rok", "Od nakupu"]
        benchmark_col1, benchmark_col2 = st.columns(2)
        selected_report_period = benchmark_col1.selectbox("Obdobi", benchmark_period_options, key="reports_benchmark_period")
        selected_report_benchmark = benchmark_col2.selectbox("Benchmark", list(BENCHMARKS.keys()), key="reports_benchmark_ticker")
        report_benchmark_mode = st.radio(
            "Rezim vykonu",
            ["Aktualni portfolio", "Vcetne uzavrenych pozic"],
            horizontal=True,
            key="reports_benchmark_mode",
        )
        st.caption(t("history_explainer", language))

        benchmark_period = HISTORY_PERIODS.get(selected_report_period, "max")
        if selected_report_period == "Od nakupu":
            benchmark_period = "max"

        report_history_source_df = open_lot_transactions_df if report_benchmark_mode == "Aktualni portfolio" else transactions_df
        report_history_include_tickers = open_transaction_tickers if report_benchmark_mode == "Aktualni portfolio" else None
        report_portfolio_history_df, missing_benchmark_tickers = build_transaction_portfolio_history(
            report_history_source_df,
            transaction_ticker_map,
            period=benchmark_period,
            include_tickers=report_history_include_tickers,
        )
        if missing_benchmark_tickers:
            st.info(f"Nektere tickery nejsou v benchmark porovnani zapocitane: {', '.join(missing_benchmark_tickers)}")

        if report_portfolio_history_df.empty:
            st.info(t("missing_portfolio_history", language))
        else:
            if report_benchmark_mode == "Vcetne uzavrenych pozic":
                report_clean_history_df = build_account_clean_performance_history(
                    report_portfolio_history_df,
                    report_history_source_df,
                    include_tickers=report_history_include_tickers,
                )
            else:
                report_clean_history_df = build_clean_performance_history_from_transactions(
                    report_portfolio_history_df,
                    report_history_source_df,
                    include_tickers=report_history_include_tickers,
                )
            report_benchmark_history_df = build_benchmark_history(benchmark_period, BENCHMARKS[selected_report_benchmark])
            if report_benchmark_history_df.empty:
                st.info(t("missing_benchmark_history", language))
            else:
                report_comparison_df = report_clean_history_df.merge(report_benchmark_history_df, on="Date", how="inner")
                report_comparison_df["portfolio_return_pct_raw"] = pd.to_numeric(
                    report_comparison_df["clean_return_pct"],
                    errors="coerce",
                )
                portfolio_growth = (report_comparison_df["portfolio_return_pct_raw"] / 100.0) + 1.0
                portfolio_growth = portfolio_growth.replace([float("inf"), float("-inf")], pd.NA).dropna()
                if len(portfolio_growth) < 2:
                    st.info(t("missing_percent_history", language))
                    report_comparison_df = pd.DataFrame()
                else:
                    start_growth = float(portfolio_growth.iloc[0])
                    if start_growth == 0:
                        st.info(t("missing_percent_history", language))
                        report_comparison_df = pd.DataFrame()
                    else:
                        report_comparison_df["portfolio_return_pct"] = (((report_comparison_df["portfolio_return_pct_raw"] / 100.0) + 1.0) / start_growth - 1.0) * 100
                report_comparison_df["benchmark_return_pct"] = normalize_to_percent(report_comparison_df["benchmark_value"])
                if not report_comparison_df.empty:
                    report_comparison_df = report_comparison_df.dropna(subset=["portfolio_return_pct", "benchmark_return_pct"])

                if len(report_comparison_df) < 2:
                    st.info(t("missing_percent_history", language))
                else:
                    report_fig = go.Figure()
                    report_fig.add_trace(
                        go.Scatter(
                            x=report_comparison_df["Date"],
                            y=report_comparison_df["portfolio_return_pct"],
                            mode="lines",
                            name=report_benchmark_mode,
                        )
                    )
                    report_fig.add_trace(
                        go.Scatter(
                            x=report_comparison_df["Date"],
                            y=report_comparison_df["benchmark_return_pct"],
                            mode="lines",
                            name=selected_report_benchmark,
                        )
                    )
                    report_fig.update_layout(
                        margin=dict(l=20, r=20, t=20, b=20),
                        yaxis_title="Vykon (%)",
                        xaxis_title="Datum",
                    )
                    st.plotly_chart(report_fig, use_container_width=True)

                    report_portfolio_pct = float(report_comparison_df["portfolio_return_pct"].iloc[-1])
                    report_benchmark_pct = float(report_comparison_df["benchmark_return_pct"].iloc[-1])
                    report_diff_pct = report_portfolio_pct - report_benchmark_pct

                    benchmark_metric_col1, benchmark_metric_col2, benchmark_metric_col3 = st.columns(3)
                    benchmark_metric_col1.metric(report_benchmark_mode, f"{report_portfolio_pct:.2f} %")
                    benchmark_metric_col2.metric(selected_report_benchmark, f"{report_benchmark_pct:.2f} %")
                    benchmark_metric_col3.metric("Rozdil oproti benchmarku", f"{report_diff_pct:.2f} p. b.")

    with report_changes_tab:
        render_section_intro("Zmeny", "Posledni pohyby v portfoliu, planu a investicnich rozhodnutich.")
        st.caption("Posledni dostupne zmeny z CSV souboru. Portfolio nema plnou historii stavu, proto se zobrazuji hlavne posledni nakupy, upravy planu a rozhodnuti.")
        portfolio_changes_df, plan_changes_df, decision_changes_df = get_report_change_tables(
            raw_df, analysis_df, analysis_history_df, date_format_label
        )

        changes_col1, changes_col2 = st.columns(2)
        with changes_col1:
            st.write("**Posledni zmeny v portfoliu**")
            if len(portfolio_changes_df) > 0:
                st.dataframe(
                    portfolio_changes_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config=build_table_column_config(portfolio_changes_df),
                )
            else:
                st.info("N/A")

            st.write("**Posledni zmeny planu portfolia**")
            if len(plan_changes_df) > 0:
                st.dataframe(
                    plan_changes_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config=build_table_column_config(plan_changes_df),
                )
            else:
                st.info("N/A")

        with changes_col2:
            st.write("**Posledni rozhodnuti**")
            if len(decision_changes_df) > 0:
                st.dataframe(
                    decision_changes_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config=build_table_column_config(decision_changes_df),
                )
            else:
                st.info("N/A")

    with report_risk_tab:
        render_section_intro("Riziko a koncentrace", "Rozlozeni portfolia, koncentrace a pomocne pohledy na expozici.")
        st.caption("Jednoduchy pohled na rozlozeni portfolia a koncentraci nejvetsich pozic.")
        if len(df) == 0 or total_value == 0:
            st.info("N/A")
        else:
            allocation_df = df[["ticker", "company", "value_base", "currency", "market_cap_text"]].copy()
            allocation_df["weight_pct"] = allocation_df["value_base"] / total_value * 100
            allocation_df["Region"] = allocation_df.apply(
                lambda row: infer_investment_region(row["ticker"], row["company"]),
                axis=1,
            )
            allocation_df["Velikost spolecnosti"] = allocation_df["market_cap_text"].apply(normalize_size_bucket)
            allocation_df = allocation_df.sort_values("weight_pct", ascending=False)
            allocation_df["Podil %"] = allocation_df["weight_pct"].apply(lambda value: f"{value:.2f} %")
            allocation_df["Hodnota"] = allocation_df["value_base"].apply(lambda value: f"{base_currency} {value:,.2f}")
            st.dataframe(
                allocation_df[["ticker", "Hodnota", "Podil %"]].rename(columns={"ticker": "Ticker"}),
                use_container_width=True,
                hide_index=True,
                column_config=build_table_column_config(allocation_df[["ticker", "Hodnota", "Podil %"]].rename(columns={"ticker": "Ticker"})),
            )

            risk_fig = px.pie(
                allocation_df,
                names="ticker",
                values="value_base",
                hole=0.55,
            )
            risk_fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), showlegend=True)
            st.plotly_chart(risk_fig, use_container_width=True)

            top3_pct = float(allocation_df["weight_pct"].head(3).sum())
            top5_pct = float(allocation_df["weight_pct"].head(5).sum())
            top_position = allocation_df.iloc[0]

            risk_metric_col1, risk_metric_col2, risk_metric_col3 = st.columns(3)
            risk_metric_col1.metric("Top 3 pozice", f"{top3_pct:.2f} %")
            risk_metric_col2.metric("Top 5 pozic", f"{top5_pct:.2f} %")
            risk_metric_col3.metric("Nejvetsi pozice", f"{top_position['ticker']} ({top_position['weight_pct']:.2f} %)")

            st.write("**Rozdeleni podle lokace investice**")
            st.caption("Lokace je zjednodusene odvozena podle regionu firmy nebo ETF, ne podle burzy.")
            region_split = allocation_df.groupby("Region", dropna=False)["value_base"].sum().reset_index()
            region_split = region_split.sort_values("value_base", ascending=False)
            region_split["Podil %"] = region_split["value_base"] / total_value * 100
            region_split["Hodnota"] = region_split["value_base"].apply(lambda value: f"{base_currency} {value:,.2f}")
            region_col1, region_col2 = st.columns([1.2, 1])
            with region_col1:
                st.dataframe(
                    region_split[["Region", "Hodnota", "Podil %"]].assign(
                        **{"Podil %": region_split["Podil %"].map(lambda value: f"{value:.2f} %")}
                    ),
                    use_container_width=True,
                    hide_index=True,
                    column_config=build_table_column_config(
                        region_split[["Region", "Hodnota", "Podil %"]].assign(
                            **{"Podil %": region_split["Podil %"].map(lambda value: f"{value:.2f} %")}
                        )
                    ),
                )
            with region_col2:
                region_fig = px.pie(
                    region_split,
                    names="Region",
                    values="value_base",
                    hole=0.55,
                )
                region_fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), showlegend=True)
                st.plotly_chart(region_fig, use_container_width=True)

            st.write("**Rozdeleni podle velikosti spolecnosti**")
            st.caption("Velikost vychazi z market cap. ETF a chybejici data jsou spojene do jedne skupiny.")
            size_split = allocation_df.groupby("Velikost spolecnosti", dropna=False)["value_base"].sum().reset_index()
            size_split = size_split.sort_values("value_base", ascending=False)
            size_split["Podil %"] = size_split["value_base"] / total_value * 100
            size_split["Hodnota"] = size_split["value_base"].apply(lambda value: f"{base_currency} {value:,.2f}")
            size_col1, size_col2 = st.columns([1.2, 1])
            with size_col1:
                st.dataframe(
                    size_split[["Velikost spolecnosti", "Hodnota", "Podil %"]].assign(
                        **{"Podil %": size_split["Podil %"].map(lambda value: f"{value:.2f} %")}
                    ),
                    use_container_width=True,
                    hide_index=True,
                    column_config=build_table_column_config(
                        size_split[["Velikost spolecnosti", "Hodnota", "Podil %"]].assign(
                            **{"Podil %": size_split["Podil %"].map(lambda value: f"{value:.2f} %")}
                        )
                    ),
                )
            with size_col2:
                size_fig = px.pie(
                    size_split,
                    names="Velikost spolecnosti",
                    values="value_base",
                    hole=0.55,
                )
                size_fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), showlegend=True)
                st.plotly_chart(size_fig, use_container_width=True)

            currency_split = allocation_df.groupby("currency", dropna=False)["value_base"].sum().reset_index()
            currency_split["Podil %"] = (currency_split["value_base"] / total_value * 100).round(2)
            currency_split["Mena"] = currency_split["currency"].fillna("N/A")
            st.write("**Rozdeleni podle men**")
            st.dataframe(
                currency_split[["Mena", "Podil %"]].rename(columns={"Podil %": "Podil %"}),
                use_container_width=True,
                hide_index=True,
                column_config=build_table_column_config(currency_split[["Mena", "Podil %"]].rename(columns={"Podil %": "Podil %"})),
            )

            if float(top_position["weight_pct"]) >= 25:
                st.warning(f"Pozice {top_position['ticker']} tvori {top_position['weight_pct']:.2f} % portfolia. To uz je vyssi koncentrace.")

if current_page == "Portfolio":
    render_page_header("Portfolio", "Pracovni prostor pro holdings, detail pozice a spravu portfolia.", "Holdings")
    portfolio_cost_base_for_cards = convert_from_usd(df["cost_usd"].sum(), base_currency) if len(df) > 0 else 0.0
    portfolio_return_pct = (total_profit_loss / portfolio_cost_base_for_cards * 100) if portfolio_cost_base_for_cards else None
    render_kpi_cards(
        [
            {"label": "Hodnota portfolia", "value": format_currency_metric(total_value, base_currency, decimals=0, thousands_sep="."), "delta": "Aktualni velikost portfolia"},
            {"label": "Denni zmena", "value": format_currency_metric(df["daily_change_base"].sum() if len(df) > 0 else 0.0, base_currency, decimals=0, thousands_sep="."), "delta": f"Vs poslednimu close | {format_percent_metric((df['daily_change_base'].sum() / (total_value - df['daily_change_base'].sum()) * 100) if len(df) > 0 and (total_value - df['daily_change_base'].sum()) else 0.0)}"},
            {"label": "Celkovy zisk", "value": format_currency_metric(total_profit_loss, base_currency, decimals=0, thousands_sep="."), "delta": format_percent_metric(portfolio_return_pct)},
            {"label": "Pocet pozic", "value": str(len(df)), "delta": "Agregovane holdings"},
        ]
    )
    portfolio_overview_tab, portfolio_add_tab, portfolio_edit_tab, portfolio_delete_tab = st.tabs(
        [t("overview", language), t("add", language), t("edit", language), t("delete", language)]
    )

    with portfolio_add_tab:
        with st.form("add_position_form"):
            new_ticker = st.text_input("Ticker", placeholder="AAPL")
            new_shares = st.number_input("Kusy", min_value=0.0, step=1.0)
            new_buy_price = st.number_input("Nakupni cena", min_value=0.0, step=0.01)
            new_purchase_date = st.date_input("Datum nakupu")
            add_button = st.form_submit_button("Pridat")

            if add_button:
                if not new_ticker.strip():
                    st.error("Zadej ticker.")
                else:
                    clean_ticker = new_ticker.strip().upper()
                    existing_match = raw_df[raw_df["ticker"] == clean_ticker]
                    company_value = existing_match["company"].iloc[0] if "company" in raw_df.columns and len(existing_match) > 0 else None
                    yfinance_value = existing_match["yfinance_ticker"].iloc[0] if len(existing_match) > 0 else clean_ticker
                    new_row = pd.DataFrame(
                        [
                            {
                                "ticker": clean_ticker,
                                "company": company_value,
                                "yfinance_ticker": yfinance_value,
                                "shares": float(new_shares),
                                "buy_price": float(new_buy_price),
                                "purchase_date": str(new_purchase_date),
                            }
                        ]
                    )
                    raw_df = pd.concat([raw_df, new_row], ignore_index=True)
                    save_portfolio(raw_df)
                    st.success("Pozice byla pridana.")
                    st.rerun()

    with portfolio_edit_tab:
        if len(raw_df) > 0:
            edit_options = [
                f"{row.ticker} | {format_date_display(row.purchase_date, date_format_label)} | {row.shares} ks | nakup {row.buy_price}"
                for row in raw_df.itertuples(index=True)
            ]
            selected_edit_option = st.selectbox("Vyber pozici k uprave", edit_options)
            selected_edit_index = edit_options.index(selected_edit_option)
            selected_row = raw_df.iloc[selected_edit_index]
            edit_date_value = pd.to_datetime(selected_row["purchase_date"], errors="coerce")
            if pd.isna(edit_date_value):
                edit_date_value = pd.Timestamp.today()

            with st.form("edit_position_form"):
                edit_ticker = st.text_input("Ticker ", value=str(selected_row["ticker"]))
                edit_shares = st.number_input("Kusy ", min_value=0.0, value=safe_number_input_value(selected_row["shares"]), step=1.0)
                edit_buy_price = st.number_input("Nakupni cena ", min_value=0.0, value=safe_number_input_value(selected_row["buy_price"]), step=0.01)
                edit_purchase_date = st.date_input("Datum nakupu ", value=edit_date_value.date())
                edit_button = st.form_submit_button("Ulozit")

                if edit_button:
                    if not edit_ticker.strip():
                        st.error("Zadej ticker.")
                    else:
                        clean_ticker = edit_ticker.strip().upper()
                        other_match = raw_df[(raw_df["ticker"] == clean_ticker) & (raw_df.index != selected_edit_index)]
                        existing_yfinance = selected_row["yfinance_ticker"] if pd.notna(selected_row.get("yfinance_ticker", None)) and str(selected_row.get("yfinance_ticker", "")).strip() else clean_ticker
                        raw_df.loc[selected_edit_index, "ticker"] = clean_ticker
                        raw_df.loc[selected_edit_index, "yfinance_ticker"] = (
                            other_match["yfinance_ticker"].iloc[0]
                            if len(other_match) > 0
                            else existing_yfinance if clean_ticker == str(selected_row["ticker"]).strip().upper()
                            else clean_ticker
                        )
                        raw_df.loc[selected_edit_index, "shares"] = float(edit_shares)
                        raw_df.loc[selected_edit_index, "buy_price"] = float(edit_buy_price)
                        raw_df.loc[selected_edit_index, "purchase_date"] = str(edit_purchase_date)
                        save_portfolio(raw_df)
                        st.success("Pozice byla upravena.")
                        st.rerun()
        else:
            st.info("Portfolio je prazdne.")

    with portfolio_delete_tab:
        if len(raw_df) > 0:
            delete_options = [
                f"{row.ticker} | {format_date_display(row.purchase_date, date_format_label)} | {row.shares} ks | nakup {row.buy_price}"
                for row in raw_df.itertuples(index=True)
            ]
            selected_option = st.selectbox("Vyber pozici", delete_options)

            if st.button("Smazat pozici"):
                selected_index = delete_options.index(selected_option)
                raw_df = raw_df.drop(index=selected_index).reset_index(drop=True)
                save_portfolio(raw_df)
                st.success("Pozice byla smazana.")
                st.rerun()
        else:
            st.info("Portfolio je prazdne.")

    with portfolio_overview_tab:
        render_section_intro("Holdings overview", "Hlavni tabulka zustava dominantni, detail a doplnkove grafy jsou az vedle a pod ni.")
        show_premarket_columns = is_us_premarket_now()
        table_df = df[
            [
                "ticker",
                "company_display",
                "price_display",
                "premarket_price_display",
                "premarket_change_pct",
                "daily_change_pct",
                "daily_change_base",
                "shares",
                "buy_price_display",
                "one_year",
                "value_base",
                "profit_loss_base",
                "profit_loss_pct",
                "pe_display",
                "eps_display",
                "earnings_yield_display",
                "market_cap_text",
                "beta_display",
            ]
        ].rename(
            columns={
                "ticker": "Ticker",
                "company_display": "Spolecnost",
                "price_display": "Aktualni hodnota",
                "premarket_price_display": "Premarket cena",
                "premarket_change_pct": "Premarket zmena %",
                "daily_change_pct": "Denni pohyb %",
                "daily_change_base": "Denni pohyb",
                "shares": "Pocet",
                "buy_price_display": "Nakupni cena",
                "one_year": "1 Year",
                "value_base": "Current Value",
                "profit_loss_base": "Kapitalovy zisk",
                "profit_loss_pct": "% Zisk",
                "pe_display": "PE",
                "eps_display": "EPS",
                "earnings_yield_display": "Earnings Yield",
                "market_cap_text": "Market Cap",
                "beta_display": "Beta",
            }
        ).reset_index(drop=True)
        if not show_premarket_columns:
            table_df = table_df.drop(columns=["Premarket cena", "Premarket zmena %"], errors="ignore")
        visible_table_columns = [column for column in visible_columns if column in table_df.columns]
        if show_premarket_columns:
            price_insert_index = visible_table_columns.index("Aktualni hodnota") + 1 if "Aktualni hodnota" in visible_table_columns else 0
            for premarket_column in ["Premarket cena", "Premarket zmena %"]:
                if premarket_column in table_df.columns and premarket_column not in visible_table_columns:
                    visible_table_columns.insert(price_insert_index, premarket_column)
                    price_insert_index += 1
        if not visible_table_columns:
            visible_table_columns = table_df.columns.tolist()
        visible_row_count = len(table_df[visible_table_columns])
        dataframe_kwargs = {
            "use_container_width": True,
            "hide_index": True,
            "column_config": build_table_column_config(
                table_df[visible_table_columns],
                {
                    "Aktualni hodnota": st.column_config.TextColumn(help="Aktualni cena jedne akcie v jeji mene."),
                    "Premarket cena": st.column_config.TextColumn(help="Informacni premarket cena pred otevrenim americkeho trhu. Nezapocitava se do zadnych vypoctu."),
                    "Premarket zmena %": st.column_config.NumberColumn(format="%.2f %%", help=TABLE_COLUMN_HELP["Premarket zmena %"]),
                    "Denni pohyb %": st.column_config.NumberColumn(format="%.2f %%", help=TABLE_COLUMN_HELP["Denni pohyb %"]),
                    "Denni pohyb": st.column_config.NumberColumn(format="%.2f", help=TABLE_COLUMN_HELP["Denni pohyb"]),
                    "Pocet": st.column_config.NumberColumn(format="%.2f", help=TABLE_COLUMN_HELP["Pocet"]),
                    "Nakupni cena": st.column_config.TextColumn(help=TABLE_COLUMN_HELP["Nakupni cena"]),
                    "Current Value": st.column_config.NumberColumn(format=f"{base_currency} %.2f", help=TABLE_COLUMN_HELP["Current Value"]),
                    "Kapitalovy zisk": st.column_config.NumberColumn(format=f"{base_currency} %.2f", help=TABLE_COLUMN_HELP["Kapitalovy zisk"]),
                    "% Zisk": st.column_config.NumberColumn(format="%.2f %%", help=TABLE_COLUMN_HELP["% Zisk"]),
                    "1 Year": st.column_config.LineChartColumn("1 Year", help=TABLE_COLUMN_HELP["1 Year"]),
                    "PE": st.column_config.TextColumn(help=TABLE_COLUMN_HELP["PE"]),
                    "EPS": st.column_config.TextColumn(help=TABLE_COLUMN_HELP["EPS"]),
                    "Earnings Yield": st.column_config.TextColumn(help=TABLE_COLUMN_HELP["Earnings Yield"]),
                    "Beta": st.column_config.TextColumn(help=TABLE_COLUMN_HELP["Beta"]),
                },
            ),
        }
        if visible_row_count <= 20:
            dataframe_kwargs["height"] = 36 + visible_row_count * 35
        else:
            dataframe_kwargs["height"] = 740

        st.dataframe(
            table_df[visible_table_columns],
            **dataframe_kwargs,
        )

        if show_fx_rates:
            st.divider()
            render_section_intro("FX kurzy", "Decentni doplnkovy blok pod hlavnim holdings overview.")
            fx_left_space, fx_main_col, fx_right_space = st.columns([0.2, 1, 0.2])
            with fx_main_col:
                if not selected_fx_pairs:
                    st.info("V nastaveni neni vybran zadny FX kurz.")
                else:
                    try:
                        rates = get_czk_rates(tuple(selected_fx_pairs))
                        if len(rates) == 0:
                            st.info("Vybrane kurzy se nepodarilo nacist.")
                        else:
                            rates_df = pd.DataFrame(
                                [
                                    {
                                        "Par": pair,
                                        "Kurz": f"{rate_data['value']:.2f}{(' ' + rate_data['suffix']) if rate_data.get('suffix') else ''}",
                                        "1 Year": rate_data["history"],
                                    }
                                    for pair, rate_data in rates.items()
                                ]
                            )
                            st.dataframe(
                                rates_df,
                                use_container_width=True,
                                hide_index=True,
                                column_config=build_table_column_config(
                                    rates_df,
                                    {
                                        "Par": st.column_config.TextColumn(width="small", help=TABLE_COLUMN_HELP["Par"]),
                                        "Kurz": st.column_config.TextColumn(width="small", help=TABLE_COLUMN_HELP["Kurz"]),
                                        "1 Year": st.column_config.LineChartColumn("1 Year", width="medium", help=TABLE_COLUMN_HELP["1 Year"]),
                                    },
                                ),
                            )
                    except Exception:
                        st.info("Kurzy se nepodarilo nacist.")

        lower_left_col, lower_right_col = st.columns([1.05, 1])
        with lower_left_col:
            render_section_intro("Alokace", "Rozlozeni portfolia podle velikosti jednotlivych pozic.")
            if len(df) > 0 and total_value != 0:
                chart_df = df[["ticker", "value_usd", "value_base"]].copy()
                chart_df["label"] = chart_df["ticker"] + " (" + ((chart_df["value_base"] / total_value) * 100).round(1).astype(str) + "%)"
                fig = px.pie(chart_df, names="label", values="value_usd", hole=0.5)
                fig.update_traces(textposition="outside", textinfo="label")
                fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Zatim neni co zobrazit v grafu.")

        with lower_right_col:
            render_section_intro("Profit leaderboard", "Sekundarni pohled na ziskove a ztratove tituly.")
            if len(df) > 0:
                profit_chart_df = df.sort_values("profit_loss_usd", ascending=False)
                profit_chart = px.bar(
                    profit_chart_df,
                    x="ticker",
                    y="profit_loss_base",
                    color="profit_loss_base",
                    color_continuous_scale=["#d9534f", "#f0ad4e", "#5cb85c"],
                    labels={"ticker": "Ticker", "profit_loss_base": f"Zisk / ztrata ({base_currency})"},
                )
                profit_chart.update_layout(coloraxis_showscale=False, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(profit_chart, use_container_width=True)
            else:
                st.info("Zatim neni co zobrazit v grafu zisku a ztraty.")

        render_section_intro("Historie a benchmark", "Spodni analyticky blok pro vykonnost proti zvolenemu benchmarku.")
        history_col, benchmark_col = st.columns([1, 1])
        with history_col:
            selected_period_label = st.selectbox(
                t("period", language),
                list(HISTORY_PERIODS.keys()),
                index=0,
            )
        with benchmark_col:
            selected_benchmark_label = st.selectbox(
                t("benchmark", language),
                list(BENCHMARKS.keys()),
                index=0,
            )
        portfolio_history_mode = st.radio(
            "Rezim vykonu",
            ["Aktualni portfolio", "Vcetne uzavrenych pozic"],
            horizontal=True,
            key="portfolio_history_mode",
        )

        st.caption(t("history_explainer", language))

        benchmark_period = HISTORY_PERIODS.get(selected_period_label, "max")
        if selected_period_label == "Od nakupu":
            benchmark_period = "max"

        history_source_df = open_lot_transactions_df if portfolio_history_mode == "Aktualni portfolio" else transactions_df
        history_include_tickers = open_transaction_tickers if portfolio_history_mode == "Aktualni portfolio" else None
        portfolio_history_df, missing_history_tickers = build_transaction_portfolio_history(
            history_source_df,
            transaction_ticker_map,
            benchmark_period,
            include_tickers=history_include_tickers,
        )

        if missing_history_tickers:
            st.warning(t("missing_tickers_warning", language) + ", ".join(missing_history_tickers))

        if not portfolio_history_df.empty:
            if portfolio_history_mode == "Vcetne uzavrenych pozic":
                portfolio_clean_history_df = build_account_clean_performance_history(
                    portfolio_history_df,
                    history_source_df,
                    include_tickers=history_include_tickers,
                )
            else:
                portfolio_clean_history_df = build_clean_performance_history_from_transactions(
                    portfolio_history_df,
                    history_source_df,
                    include_tickers=history_include_tickers,
                )
            benchmark_history_df = build_benchmark_history(
                benchmark_period, BENCHMARKS[selected_benchmark_label]
            )
            if benchmark_history_df.empty:
                st.info(t("missing_benchmark_history", language))
            else:
                comparison_df = portfolio_clean_history_df.merge(benchmark_history_df, on="Date", how="inner")

                if len(comparison_df) < 2:
                    st.info(t("missing_shared_history", language))
                else:
                    comparison_df = comparison_df.dropna(subset=["clean_return_pct"])
                    comparison_df["portfolio_return_pct_raw"] = pd.to_numeric(
                        comparison_df["clean_return_pct"],
                        errors="coerce",
                    )
                    portfolio_growth = (comparison_df["portfolio_return_pct_raw"] / 100.0) + 1.0
                    portfolio_growth = portfolio_growth.replace([float("inf"), float("-inf")], pd.NA).dropna()
                    if len(portfolio_growth) < 2:
                        st.info(t("missing_percent_history", language))
                        comparison_df = pd.DataFrame()
                    else:
                        start_growth = float(portfolio_growth.iloc[0])
                        if start_growth == 0:
                            st.info(t("missing_percent_history", language))
                            comparison_df = pd.DataFrame()
                        else:
                            comparison_df["portfolio_return_pct"] = (((comparison_df["portfolio_return_pct_raw"] / 100.0) + 1.0) / start_growth - 1.0) * 100
                    comparison_df["benchmark_return_pct"] = normalize_to_percent(comparison_df["benchmark_value"])
                    if not comparison_df.empty:
                        comparison_df = comparison_df.dropna(subset=["portfolio_return_pct", "benchmark_return_pct"])

                    if len(comparison_df) < 2:
                        st.info(t("missing_percent_history", language))
                    else:
                        chart_fig = go.Figure()
                        chart_fig.add_trace(
                            go.Scatter(
                                x=comparison_df["Date"],
                                y=comparison_df["portfolio_return_pct"],
                                mode="lines",
                                name=portfolio_history_mode,
                            )
                        )
                        chart_fig.add_trace(
                            go.Scatter(
                                x=comparison_df["Date"],
                                y=comparison_df["benchmark_return_pct"],
                                mode="lines",
                                name=selected_benchmark_label,
                            )
                        )
                        chart_fig.update_layout(
                            margin=dict(l=20, r=20, t=20, b=20),
                            xaxis_title="Datum",
                            yaxis_title="Vykonnost (%)",
                        )
                        st.plotly_chart(chart_fig, use_container_width=True)

                        portfolio_return_pct = float(comparison_df["portfolio_return_pct"].iloc[-1])
                        benchmark_return_pct = float(comparison_df["benchmark_return_pct"].iloc[-1])
                        excess_return_pct_points = portfolio_return_pct - benchmark_return_pct

                        render_kpi_cards(
                            [
                                {"label": t("portfolio_return", language), "value": format_percent_metric(portfolio_return_pct), "delta": portfolio_history_mode},
                                {"label": t("benchmark_return", language), "value": format_percent_metric(benchmark_return_pct), "delta": selected_benchmark_label},
                                {"label": t("excess_return", language), "value": f"{excess_return_pct_points:.2f} p. b.", "delta": "Rozdil oproti benchmarku"},
                            ]
                        )
        else:
            st.info(t("missing_portfolio_history", language))
