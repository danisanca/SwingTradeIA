import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Stock, StockQuote } from '../models/stock.model';
import { HistoryResponse, Period } from '../models/candle.model';

@Injectable({ providedIn: 'root' })
export class StockService {
  private readonly api = environment.apiUrl;

  constructor(private http: HttpClient) {}

  /** Lista todas as ações monitoradas */
  getStocks(): Observable<Stock[]> {
    return this.http.get<Stock[]>(`${this.api}/stocks`);
  }

  /** Retorna cotações de todas as ações */
  getAllQuotes(): Observable<StockQuote[]> {
    return this.http.get<StockQuote[]>(`${this.api}/stocks/quotes`);
  }

  /** Retorna dados de uma ação específica */
  getStockByTicker(ticker: string): Observable<{ stock: Stock; quote: StockQuote }> {
    return this.http.get<{ stock: Stock; quote: StockQuote }>(`${this.api}/stocks/${ticker}`);
  }

  /** Retorna histórico OHLCV */
  getHistory(ticker: string, period: Period = 'MAX'): Observable<HistoryResponse> {
    return this.http.get<HistoryResponse>(
      `${this.api}/market-data/${ticker}/history?period=${period}`
    );
  }

  /** Retorna cotação atual de uma ação */
  getQuote(ticker: string): Observable<StockQuote> {
    return this.http.get<StockQuote>(`${this.api}/market-data/${ticker}/quote`);
  }
}
