using Microsoft.EntityFrameworkCore;
using SwingTradeIA.Api.Models;

namespace SwingTradeIA.Api.Data;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    public DbSet<Stock> Stocks => Set<Stock>();
    public DbSet<Analysis> Analyses => Set<Analysis>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Stock>(e =>
        {
            e.HasKey(s => s.Id);
            e.HasIndex(s => s.Ticker).IsUnique();
            e.Property(s => s.Ticker).HasMaxLength(10).IsRequired();
            e.Property(s => s.Name).HasMaxLength(200).IsRequired();
            e.Property(s => s.Sector).HasMaxLength(100);
        });

        modelBuilder.Entity<Analysis>(e =>
        {
            e.HasKey(a => a.Id);
            e.HasOne(a => a.Stock).WithMany().HasForeignKey(a => a.StockId);
        });

        // Seed data — ações padrão da B3
        var stocks = new[]
        {
            new Stock { Id = Guid.Parse("00000000-0000-0000-0000-000000000001"), Ticker = "PETR4", Name = "Petrobras PN", Sector = "Petróleo & Gás" },
            new Stock { Id = Guid.Parse("00000000-0000-0000-0000-000000000002"), Ticker = "VALE3", Name = "Vale ON", Sector = "Mineração" },
            new Stock { Id = Guid.Parse("00000000-0000-0000-0000-000000000003"), Ticker = "ITUB4", Name = "Itaú Unibanco PN", Sector = "Financeiro" },
            new Stock { Id = Guid.Parse("00000000-0000-0000-0000-000000000004"), Ticker = "BBDC4", Name = "Bradesco PN", Sector = "Financeiro" },
            new Stock { Id = Guid.Parse("00000000-0000-0000-0000-000000000005"), Ticker = "ABEV3", Name = "Ambev ON", Sector = "Bebidas" },
            new Stock { Id = Guid.Parse("00000000-0000-0000-0000-000000000006"), Ticker = "WEGE3", Name = "WEG ON", Sector = "Industrial" },
            new Stock { Id = Guid.Parse("00000000-0000-0000-0000-000000000007"), Ticker = "RENT3", Name = "Localiza ON", Sector = "Mobilidade" },
            new Stock { Id = Guid.Parse("00000000-0000-0000-0000-000000000008"), Ticker = "MGLU3", Name = "Magazine Luiza ON", Sector = "Varejo" },
            new Stock { Id = Guid.Parse("00000000-0000-0000-0000-000000000009"), Ticker = "BBAS3", Name = "Banco do Brasil ON", Sector = "Financeiro" },
            new Stock { Id = Guid.Parse("00000000-0000-0000-0000-000000000010"), Ticker = "EGIE3", Name = "Engie Brasil ON", Sector = "Energia Elétrica" },
            new Stock { Id = Guid.Parse("00000000-0000-0000-0000-000000000011"), Ticker = "VIVT3", Name = "Telefônica ON", Sector = "Telecomunicações" },
            new Stock { Id = Guid.Parse("00000000-0000-0000-0000-000000000012"), Ticker = "SUZB3", Name = "Suzano ON", Sector = "Papel & Celulose" },
            new Stock { Id = Guid.Parse("00000000-0000-0000-0000-000000000013"), Ticker = "LREN3", Name = "Lojas Renner ON", Sector = "Varejo" },
            new Stock { Id = Guid.Parse("00000000-0000-0000-0000-000000000014"), Ticker = "HAPV3", Name = "Hapvida ON", Sector = "Saúde" },
            new Stock { Id = Guid.Parse("00000000-0000-0000-0000-000000000015"), Ticker = "RADL3", Name = "Raia Drogasil ON", Sector = "Saúde" },
        };
        modelBuilder.Entity<Stock>().HasData(stocks);
    }
}
