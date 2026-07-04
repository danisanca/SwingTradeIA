using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using SwingTradeIA.Api.Data;
using SwingTradeIA.Api.Models;
using SwingTradeIA.Api.Services;

namespace SwingTradeIA.Api.Controllers;

[ApiController]
[Route("api/analysis")]
public class AnalysisController : ControllerBase
{
    private readonly AppDbContext _db;
    private readonly IAiServiceClient _aiClient;
    private readonly ILogger<AnalysisController> _logger;

    public AnalysisController(AppDbContext db, IAiServiceClient aiClient, ILogger<AnalysisController> logger)
    {
        _db = db;
        _aiClient = aiClient;
        _logger = logger;
    }

    /// <summary>
    /// Retorna análise técnica completa + recomendação DQN para uma ação.
    /// Persiste o resultado no banco de dados.
    /// </summary>
    [HttpGet("{ticker}")]
    public async Task<IActionResult> GetAnalysis(string ticker)
    {
        ticker = ticker.ToUpper();

        var stock = await _db.Stocks.FirstOrDefaultAsync(s => s.Ticker == ticker);
        if (stock is null) return NotFound(new { error = $"Ação {ticker} não encontrada" });

        var analysis = await _aiClient.GetRecommendationAsync(ticker);
        if (analysis is null) return StatusCode(503, new { error = "AI Service indisponível" });

        // Persistir análise no banco
        try
        {
            var dbAnalysis = new Analysis
            {
                StockId = stock.Id,
                Signal = analysis.FinalSignal.Signal,
                Confidence = (decimal)analysis.FinalSignal.Confidence,
                Source = analysis.FinalSignal.Source,
                Rsi = analysis.Indicators.Rsi.Value.HasValue ? (decimal?)analysis.Indicators.Rsi.Value : null,
                Macd = analysis.Indicators.MacdData.Macd.HasValue ? (decimal?)analysis.Indicators.MacdData.Macd : null,
                MacdSignal = analysis.Indicators.MacdData.Signal.HasValue ? (decimal?)analysis.Indicators.MacdData.Signal : null,
                BollingerUpper = analysis.Indicators.BollingerBands.Upper.HasValue ? (decimal?)analysis.Indicators.BollingerBands.Upper : null,
                BollingerLower = analysis.Indicators.BollingerBands.Lower.HasValue ? (decimal?)analysis.Indicators.BollingerBands.Lower : null,
                Ma9 = analysis.Indicators.MovingAverages.Ma9.HasValue ? (decimal?)analysis.Indicators.MovingAverages.Ma9 : null,
                Ma21 = analysis.Indicators.MovingAverages.Ma21.HasValue ? (decimal?)analysis.Indicators.MovingAverages.Ma21 : null,
            };
            _db.Analyses.Add(dbAnalysis);
            await _db.SaveChangesAsync();
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Falha ao persistir análise de {Ticker}", ticker);
        }

        return Ok(analysis);
    }

    /// <summary>Histórico de análises de uma ação</summary>
    [HttpGet("{ticker}/history")]
    public async Task<IActionResult> GetAnalysisHistory(string ticker, [FromQuery] int limit = 30)
    {
        ticker = ticker.ToUpper();
        var stock = await _db.Stocks.FirstOrDefaultAsync(s => s.Ticker == ticker);
        if (stock is null) return NotFound(new { error = $"Ação {ticker} não encontrada" });

        var history = await _db.Analyses
            .Where(a => a.StockId == stock.Id)
            .OrderByDescending(a => a.AnalyzedAt)
            .Take(limit)
            .Select(a => new
            {
                a.Id, a.AnalyzedAt, a.Signal, a.Confidence, a.Source,
                a.Rsi, a.Macd, a.Ma9, a.Ma21
            })
            .ToListAsync();

        return Ok(history);
    }
}
