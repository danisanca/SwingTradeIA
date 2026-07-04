namespace SwingTradeIA.Api.Models;

public class Analysis
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid StockId { get; set; }
    public Stock? Stock { get; set; }
    public DateTime AnalyzedAt { get; set; } = DateTime.UtcNow;
    public string Signal { get; set; } = "HOLD"; // BUY, SELL, HOLD
    public decimal Confidence { get; set; }
    public string Source { get; set; } = "technical"; // dqn, technical
    public decimal? Rsi { get; set; }
    public decimal? Macd { get; set; }
    public decimal? MacdSignal { get; set; }
    public decimal? BollingerUpper { get; set; }
    public decimal? BollingerLower { get; set; }
    public decimal? Ma9 { get; set; }
    public decimal? Ma21 { get; set; }
    public string? Notes { get; set; }
}
