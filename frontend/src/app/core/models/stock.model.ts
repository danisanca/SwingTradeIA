export interface Stock {
  id?: string;
  ticker: string;
  name: string;
  sector?: string;
}

export interface StockQuote {
  ticker: string;
  name?: string;
  sector?: string;
  price: number | null;
  change: number | null;
  changePercent: number | null;
  volume: number | null;
  previousClose: number | null;
  yearHigh: number | null;
  yearLow: number | null;
  error?: boolean;
}
