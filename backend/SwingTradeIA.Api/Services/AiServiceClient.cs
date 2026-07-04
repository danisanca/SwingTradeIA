using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace SwingTradeIA.Api.Services;

public class AiServiceClient : IAiServiceClient
{
    private readonly HttpClient _http;
    private readonly ILogger<AiServiceClient> _logger;

    private static readonly JsonSerializerOptions _opts = new()
    {
        PropertyNameCaseInsensitive = true,
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
    };

    public AiServiceClient(HttpClient http, ILogger<AiServiceClient> logger)
    {
        _http = http;
        _logger = logger;
    }

    public async Task<StockListResponse?> GetStocksAsync()
    {
        var response = await _http.GetFromJsonAsync<List<StockInfo>>("/market-data/stocks", _opts);
        return response is not null ? new StockListResponse(response) : null;
    }

    public async Task<HistoryResponse?> GetHistoryAsync(string ticker, string period)
    {
        return await _http.GetFromJsonAsync<HistoryResponse>(
            $"/market-data/history/{ticker}?period={period}", _opts);
    }

    public async Task<AnalysisResponse?> GetRecommendationAsync(string ticker)
    {
        return await _http.GetFromJsonAsync<AnalysisResponse>(
            $"/dqn/recommend/{ticker}", _opts);
    }

    public async Task<QuoteResponse?> GetQuoteAsync(string ticker)
    {
        return await _http.GetFromJsonAsync<QuoteResponse>(
            $"/market-data/quote/{ticker}", _opts);
    }

    public async Task<List<QuoteResponse>?> GetAllQuotesAsync()
    {
        return await _http.GetFromJsonAsync<List<QuoteResponse>>(
            "/market-data/quotes/all", _opts);
    }
}
