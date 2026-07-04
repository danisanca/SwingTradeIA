namespace SwingTradeIA.Api.Models;

public class Stock
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Ticker { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string? Sector { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
