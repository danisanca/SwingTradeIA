namespace SwingTradeIA.Api.Services;

public interface IAiServiceClient
{
    Task<StockListResponse?> GetStocksAsync();
    Task<HistoryResponse?> GetHistoryAsync(string ticker, string period);
    Task<AnalysisResponse?> GetRecommendationAsync(string ticker);
    Task<QuoteResponse?> GetQuoteAsync(string ticker);
    Task<List<QuoteResponse>?> GetAllQuotesAsync();
}

// ── Response DTOs do AI Service ────────────────────────────────────────────────

public record StockInfo(string Ticker, string Name, string Sector);
public record StockListResponse(List<StockInfo> Stocks);

public record CandleRecord(string Date, double Open, double High, double Low, double Close, long Volume);
public record HistoryResponse(string Ticker, string Period, int TotalCandles, List<CandleRecord> Candles);

public record QuoteResponse(
    string Ticker,
    string? Name,
    string? Sector,
    double? Price,
    double? Change,
    double? ChangePercent,
    long? Volume,
    double? PreviousClose,
    double? YearHigh,
    double? YearLow
);

public record PriceData(
    double Current, double Open, double High, double Low,
    double? PreviousClose, double? Change, double? ChangePercent,
    double High52w, double Low52w
);

public record RsiData(double? Value, string Signal, string Interpretation);
public record MacdData(double? Macd, double? Signal, double? Histogram, string Trend, string Interpretation);
public record BollingerData(double? Upper, double? Middle, double? Lower, string Position, string Interpretation);
public record MovingAveragesData(double? Ma9, double? Ma21, double? Ma50, double? Ma200, string CrossSignal, string Interpretation);
public record VolumeData(long? Current, long? Ma20, double? Ratio, string Signal, string Interpretation);

public record Indicators(
    PriceData Price,
    RsiData Rsi,
    MacdData MacdData,
    BollingerData BollingerBands,
    MovingAveragesData MovingAverages,
    VolumeData Volume
);

public record SignalInfo(string Signal, double Confidence, string Source);

public record AnalysisResponse(
    string Ticker,
    string Name,
    SignalInfo FinalSignal,
    SignalInfo TechnicalSignal,
    Indicators Indicators
);
