import io
import requests
import pdfplumber
import pandas as pd


def download_pdf(url: str, path: str) -> None:
    resp = requests.get(url)
    resp.raise_for_status()
    with open(path, "wb") as f:
        f.write(resp.content)


def extract_tables_to_dataframe(path: str) -> pd.DataFrame:
    dfs = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            try:
                tables = page.extract_tables()
            except Exception:
                tables = []
            for table in tables:
                if not table:
                    continue
                # first row as header when possible
                if len(table) > 1:
                    df = pd.DataFrame(table[1:], columns=table[0])
                else:
                    df = pd.DataFrame(table)
                dfs.append(df)
    if dfs:
        df = pd.concat(dfs, ignore_index=True, sort=False)
        # strip whitespace from string columns
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        return df
    return pd.DataFrame()


def extract_text_to_file(path: str, out_txt: str) -> None:
    texts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                texts.append(t)
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write("\n\n".join(texts))


def main():
    url = "https://www.nyc.gov/assets/opa/downloads/pdf/pay-dates-covered-final-2026.pdf"
    pdf_path = "pay-dates-covered-final-2026.pdf"

    download_pdf(url, pdf_path)

    df = extract_tables_to_dataframe(pdf_path)
    if df.empty:
        print("No structured tables found — falling back to text extraction.")
        extract_text_to_file(pdf_path, "pay_dates_2026.txt")
        print("Saved extracted text to pay_dates_2026.txt")
    else:
        out_csv = "pay_dates_2026.csv"
        df.to_csv(out_csv, index=False)
        print(f"Extracted {len(df)} rows into {out_csv}")
        print(df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
