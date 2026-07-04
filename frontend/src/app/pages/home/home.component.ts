import {
  Component,
  OnInit,
  OnDestroy,
  ViewChild,
  ElementRef,
  AfterViewInit,
  ChangeDetectionStrategy,
  ChangeDetectorRef,
} from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Subject } from 'rxjs';
import { takeUntil, catchError } from 'rxjs/operators';
import { of } from 'rxjs';

import { StockService } from '../../core/services/stock.service';
import { AnalysisService } from '../../core/services/analysis.service';
import { StockQuote } from '../../core/models/stock.model';
import { Candle, Period, PERIOD_OPTIONS } from '../../core/models/candle.model';
import { AnalysisResult, SignalType } from '../../core/models/analysis.model';

import {
  createChart,
  IChartApi,
  ISeriesApi,
  CandlestickSeries,
  HistogramSeries,
  ColorType,
  CrosshairMode,
  LineStyle,
} from 'lightweight-charts';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, FormsModule, DatePipe],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HomeComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('chartContainer') chartContainer!: ElementRef<HTMLDivElement>;
  @ViewChild('volumeContainer') volumeContainer!: ElementRef<HTMLDivElement>;

  private destroy$ = new Subject<void>();
  private chart: IChartApi | null = null;
  private candleSeries: ISeriesApi<'Candlestick'> | null = null;
  private volumeSeries: ISeriesApi<'Histogram'> | null = null;
  private resizeObserver: ResizeObserver | null = null;

  // Template references
  readonly today = new Date();
  readonly Math = Math;

  // State
  quotes: StockQuote[] = [];
  filteredQuotes: StockQuote[] = [];
  selectedTicker: string | null = null;
  selectedPeriod: Period = 'MAX';
  searchQuery = '';

  candles: Candle[] = [];
  analysis: AnalysisResult | null = null;

  // Loading states
  loadingQuotes = true;
  loadingChart = false;
  loadingAnalysis = false;
  chartError: string | null = null;

  periodOptions = PERIOD_OPTIONS;

  constructor(
    private stockService: StockService,
    private analysisService: AnalysisService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadAllQuotes();
  }

  ngAfterViewInit(): void {
    // Delay to allow Angular to render the DOM fully before creating the chart
    setTimeout(() => {
      this.setupChart();
      this.setupResizeObserver();
    }, 0);
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
    this.resizeObserver?.disconnect();
    this.chart?.remove();
  }

  // ── Data Loading ──────────────────────────────────────────────────────────

  loadAllQuotes(): void {
    this.loadingQuotes = true;
    this.stockService
      .getAllQuotes()
      .pipe(
        takeUntil(this.destroy$),
        catchError(() => {
          // Fallback: lista de ações sem cotações
          return this.stockService.getStocks().pipe(
            catchError(() => of([]))
          );
        })
      )
      .subscribe((quotes) => {
        this.quotes = quotes as StockQuote[];
        this.filteredQuotes = [...this.quotes];
        this.loadingQuotes = false;

        // Selecionar PETR4 por padrão
        const default_ticker = this.quotes.find(q => q.ticker === 'PETR4');
        if (default_ticker) {
          this.selectStock(default_ticker.ticker);
        }
        this.cdr.markForCheck();
      });
  }

  selectStock(ticker: string): void {
    if (this.selectedTicker === ticker) return;
    this.selectedTicker = ticker;
    this.analysis = null;
    this.chartError = null;
    this.cdr.markForCheck();

    // If chart hasn't been initialized yet (e.g. first selection), init it now
    setTimeout(() => {
      if (!this.chart) {
        this.setupChart();
        this.setupResizeObserver();
      }
      this.loadChartData();
      this.loadAnalysis();
    }, 50);
  }

  loadChartData(): void {
    if (!this.selectedTicker) return;
    this.loadingChart = true;
    this.chartError = null;

    this.stockService
      .getHistory(this.selectedTicker, this.selectedPeriod)
      .pipe(takeUntil(this.destroy$), catchError((err) => {
        this.chartError = 'Erro ao carregar dados do gráfico';
        this.loadingChart = false;
        this.cdr.markForCheck();
        return of(null);
      }))
      .subscribe((res) => {
        if (res) {
          this.candles = res.candles;
          this.updateChart(res.candles);
        }
        this.loadingChart = false;
        this.cdr.markForCheck();
      });
  }

  loadAnalysis(): void {
    if (!this.selectedTicker) return;
    this.loadingAnalysis = true;

    this.analysisService
      .getAnalysis(this.selectedTicker)
      .pipe(takeUntil(this.destroy$), catchError(() => of(null)))
      .subscribe((result) => {
        this.analysis = result;
        this.loadingAnalysis = false;
        this.cdr.markForCheck();
      });
  }

  changePeriod(period: Period): void {
    this.selectedPeriod = period;
    this.loadChartData();
  }

  onSearch(): void {
    const q = this.searchQuery.toLowerCase();
    this.filteredQuotes = q
      ? this.quotes.filter(
          (s) =>
            s.ticker.toLowerCase().includes(q) ||
            (s.name?.toLowerCase() ?? '').includes(q)
        )
      : [...this.quotes];
  }

  // ── Chart ─────────────────────────────────────────────────────────────────

  setupChart(): void {
    if (!this.chartContainer) return;

    this.chart = createChart(this.chartContainer.nativeElement, {
      layout: {
        background: { type: ColorType.Solid, color: '#141928' },
        textColor: '#8892a4',
        fontFamily: "'Inter', sans-serif",
        fontSize: 11,
      },
      grid: {
        vertLines: { color: 'rgba(255,255,255,0.04)' },
        horzLines: { color: 'rgba(255,255,255,0.04)' },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: { color: 'rgba(99,179,237,0.4)', style: LineStyle.Dashed, labelBackgroundColor: '#1a2035' },
        horzLine: { color: 'rgba(99,179,237,0.4)', style: LineStyle.Dashed, labelBackgroundColor: '#1a2035' },
      },
      rightPriceScale: {
        borderColor: 'rgba(255,255,255,0.07)',
        scaleMargins: { top: 0.1, bottom: 0.1 },
      },
      timeScale: {
        borderColor: 'rgba(255,255,255,0.07)',
        timeVisible: true,
        secondsVisible: false,
        fixLeftEdge: true,
        fixRightEdge: true,
      },
      handleScale: { mouseWheel: true, pinch: true },
      handleScroll: { mouseWheel: true, pressedMouseMove: true },
    });

    this.candleSeries = this.chart.addSeries(CandlestickSeries, {
      upColor: '#48bb78',
      downColor: '#fc8181',
      borderVisible: false,
      wickUpColor: '#48bb78',
      wickDownColor: '#fc8181',
    });

    // Volume na parte inferior do mesmo gráfico (usando escala separada)
    this.volumeSeries = this.chart.addSeries(HistogramSeries, {
      color: 'rgba(66, 153, 225, 0.3)',
      priceFormat: { type: 'volume' },
      priceScaleId: 'volume',
    });

    this.chart.priceScale('volume').applyOptions({
      scaleMargins: { top: 0.85, bottom: 0 },
    });
  }

  updateChart(candles: Candle[]): void {
    if (!this.candleSeries || !this.volumeSeries || !candles.length) return;

    const candleData = candles.map((c) => ({
      time: c.date as any,
      open: c.open,
      high: c.high,
      low: c.low,
      close: c.close,
    }));

    const volumeData = candles.map((c) => ({
      time: c.date as any,
      value: c.volume,
      color: c.close >= c.open
        ? 'rgba(72, 187, 120, 0.4)'
        : 'rgba(252, 129, 129, 0.4)',
    }));

    this.candleSeries.setData(candleData);
    this.volumeSeries.setData(volumeData);
    this.chart?.timeScale().fitContent();
  }

  setupResizeObserver(): void {
    if (!this.chartContainer) return;
    this.resizeObserver = new ResizeObserver(() => {
      if (this.chart && this.chartContainer) {
        const el = this.chartContainer.nativeElement;
        this.chart.resize(el.clientWidth, el.clientHeight);
      }
    });
    this.resizeObserver.observe(this.chartContainer.nativeElement);
  }

  // ── Helpers ───────────────────────────────────────────────────────────────

  getSignalClass(signal: SignalType | string | undefined): string {
    if (!signal) return '';
    const map: Record<string, string> = { BUY: 'buy', SELL: 'sell', HOLD: 'hold' };
    return map[signal] ?? '';
  }

  getSignalLabel(signal: SignalType | string | undefined): string {
    const map: Record<string, string> = { BUY: 'COMPRAR', SELL: 'VENDER', HOLD: 'MANTER' };
    return signal ? (map[signal] ?? signal) : '—';
  }

  getSignalIcon(signal: SignalType | string | undefined): string {
    const map: Record<string, string> = { BUY: '▲', SELL: '▼', HOLD: '●' };
    return signal ? (map[signal] ?? '●') : '●';
  }

  formatPrice(v: number | null | undefined): string {
    if (v == null) return '—';
    return v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  formatChange(v: number | null | undefined): string {
    if (v == null) return '—';
    return (v >= 0 ? '+' : '') + v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  formatPercent(v: number | null | undefined): string {
    if (v == null) return '—';
    return (v >= 0 ? '+' : '') + v.toFixed(2) + '%';
  }

  formatVolume(v: number | null | undefined): string {
    if (v == null) return '—';
    if (v >= 1_000_000) return (v / 1_000_000).toFixed(1) + 'M';
    if (v >= 1_000) return (v / 1_000).toFixed(0) + 'K';
    return v.toString();
  }

  getRsiBarWidth(rsi: number | null | undefined): number {
    return rsi != null ? Math.min(100, Math.max(0, rsi)) : 0;
  }

  getRsiColor(rsi: number | null | undefined): string {
    if (rsi == null) return '#4a5568';
    if (rsi > 70) return '#fc8181';
    if (rsi < 30) return '#48bb78';
    return '#4299e1';
  }

  getSelectedQuote(): StockQuote | undefined {
    return this.quotes.find(q => q.ticker === this.selectedTicker);
  }

  trackByTicker(_: number, item: StockQuote): string {
    return item.ticker;
  }
}
