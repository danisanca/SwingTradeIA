using Microsoft.AspNetCore.Mvc;
using SwingTradeIA.Api.Services;

namespace SwingTradeIA.Api.Controllers;

[ApiController]
[Route("api/market-data")]
public class MarketDataController : ControllerBase
{
    private readonly IAiServiceClient _aiClient;

    public MarketDataController(IAiServiceClient aiClient)
    {
        _aiClient = aiClient;
    }

    /// <summary>Retorna histórico OHLCV de uma ação</summary>
    /// <param name="ticker">Código da ação (ex: PETR4)</param>
    /// <param name="period">Período: 1M, 3M, 6M, 1Y, 2Y, 5Y, MAX</param>
    [HttpGet("{ticker}/history")]
    public async Task<IActionResult> GetHistory(
        string ticker,
        [FromQuery] string period = "MAX")
    {
        var history = await _aiClient.GetHistoryAsync(ticker.ToUpper(), period.ToUpper());
        if (history is null) return StatusCode(503, new { error = "AI Service indisponível" });
        return Ok(history);
    }

    /// <summary>Retorna cotação atual de uma ação</summary>
    [HttpGet("{ticker}/quote")]
    public async Task<IActionResult> GetQuote(string ticker)
    {
        var quote = await _aiClient.GetQuoteAsync(ticker.ToUpper());
        if (quote is null) return StatusCode(503, new { error = "AI Service indisponível" });
        return Ok(quote);
    }
}
