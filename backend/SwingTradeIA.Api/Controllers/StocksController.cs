using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using SwingTradeIA.Api.Data;
using SwingTradeIA.Api.Services;

namespace SwingTradeIA.Api.Controllers;

[ApiController]
[Route("api/stocks")]
public class StocksController : ControllerBase
{
    private readonly AppDbContext _db;
    private readonly IAiServiceClient _aiClient;

    public StocksController(AppDbContext db, IAiServiceClient aiClient)
    {
        _db = db;
        _aiClient = aiClient;
    }

    /// <summary>Lista todas as ações monitoradas</summary>
    [HttpGet]
    public async Task<IActionResult> GetAll()
    {
        var stocks = await _db.Stocks
            .OrderBy(s => s.Ticker)
            .Select(s => new { s.Id, s.Ticker, s.Name, s.Sector })
            .ToListAsync();
        return Ok(stocks);
    }

    /// <summary>Retorna cotação de todas as ações (via AI Service)</summary>
    [HttpGet("quotes")]
    public async Task<IActionResult> GetAllQuotes()
    {
        var quotes = await _aiClient.GetAllQuotesAsync();
        if (quotes is null) return StatusCode(503, new { error = "AI Service indisponível" });
        return Ok(quotes);
    }

    /// <summary>Retorna dados de uma ação específica</summary>
    [HttpGet("{ticker}")]
    public async Task<IActionResult> GetByTicker(string ticker)
    {
        ticker = ticker.ToUpper();
        var stock = await _db.Stocks.FirstOrDefaultAsync(s => s.Ticker == ticker);
        if (stock is null) return NotFound(new { error = $"Ação {ticker} não encontrada" });

        var quote = await _aiClient.GetQuoteAsync(ticker);
        return Ok(new { stock.Id, stock.Ticker, stock.Name, stock.Sector, quote });
    }
}
