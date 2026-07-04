export interface Candle {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface HistoryResponse {
  ticker: string;
  period: string;
  totalCandles: number;
  candles: Candle[];
}

export type Period = '1M' | '3M' | '6M' | '1Y' | '2Y' | '5Y' | 'MAX';

export interface PeriodOption {
  label: string;
  value: Period;
}

export const PERIOD_OPTIONS: PeriodOption[] = [
  { label: '1M', value: '1M' },
  { label: '3M', value: '3M' },
  { label: '6M', value: '6M' },
  { label: '1A', value: '1Y' },
  { label: '2A', value: '2Y' },
  { label: '5A', value: '5Y' },
  { label: 'MÁX', value: 'MAX' },
];
