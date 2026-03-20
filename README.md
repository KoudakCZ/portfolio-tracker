# Portfolio Tracker ve Streamlit

Jednoducha webova aplikace pro sledovani akcioveho portfolia.

## Soubory

- `main.py` - cela aplikace
- `data/portfolio.csv` - vstupni data
- `requirements.txt` - potrebne knihovny

## CSV format

Soubor `data/portfolio.csv` musi obsahovat:

```csv
ticker,shares,buy_price
AAPL,10,175.50
MSFT,5,320.00
GOOGL,3,140.00
```

## Co aplikace ukazuje

- tabulku portfolia
- aktualni hodnotu portfolia
- celkovy zisk nebo ztratu
- jednoduchy graf hodnoty jednotlivych pozic

## Spusteni ve Windows

1. Otevri PowerShell.
2. Prejdi do slozky projektu:

```powershell
cd "C:\Users\socia\OneDrive\Ostatní\Plocha\Codex projekt"
```

3. Nainstaluj knihovny:

```powershell
pip install -r requirements.txt
```

4. Spust aplikaci:

```powershell
streamlit run main.py
```

5. Pokud `streamlit` nefunguje, zkus:

```powershell
python -m streamlit run main.py
```
