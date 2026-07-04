export type SignalType = 'BUY' | 'SELL' | 'HOLD';

export interface SignalInfo {
  signal: SignalType;
  confidence: number;
  source: 'dqn' | 'technical';
}

export interface PriceData {
  current: number;
  open: number;
  high: number;
  low: number;
  previousClose: number | null;
  change: number | null;
  changePercent: number | null;
  high52w: number;
  low52w: number;
}

export interface RsiData {
  value: number | null;
  signal: string;
  interpretation: string;
}

export interface MacdData {
  macd: number | null;
  signal: number | null;
  histogram: number | null;
  trend: string;
  interpretation: string;
}

export interface BollingerData {
  upper: number | null;
  middle: number | null;
  lower: number | null;
  position: string;
  interpretation: string;
}

export interface MovingAveragesData {
  ma9: number | null;
  ma21: number | null;
  ma50: number | null;
  ma200: number | null;
  crossSignal: string;
  interpretation: string;
}

export interface VolumeData {
  current: number | null;
  ma20: number | null;
  ratio: number | null;
  signal: string;
  interpretation: string;
}

export interface Indicators {
  price: PriceData;
  rsi: RsiData;
  macdData: MacdData;
  bollingerBands: BollingerData;
  movingAverages: MovingAveragesData;
  volume: VolumeData;
}

export interface AnalysisResult {
  ticker: string;
  name: string;
  finalSignal: SignalInfo;
  technicalSignal: SignalInfo;
  dqn?: {
    available: boolean;
    signal?: string;
    confidence?: number;
    reason?: string;
  };
  indicators: Indicators;
}
