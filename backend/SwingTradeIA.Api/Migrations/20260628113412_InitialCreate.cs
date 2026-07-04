using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

#pragma warning disable CA1814 // Prefer jagged arrays over multidimensional

namespace SwingTradeIA.Api.Migrations
{
    /// <inheritdoc />
    public partial class InitialCreate : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "Stocks",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    Ticker = table.Column<string>(type: "character varying(10)", maxLength: 10, nullable: false),
                    Name = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: false),
                    Sector = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: true),
                    CreatedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Stocks", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "Analyses",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uuid", nullable: false),
                    StockId = table.Column<Guid>(type: "uuid", nullable: false),
                    AnalyzedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    Signal = table.Column<string>(type: "text", nullable: false),
                    Confidence = table.Column<decimal>(type: "numeric", nullable: false),
                    Source = table.Column<string>(type: "text", nullable: false),
                    Rsi = table.Column<decimal>(type: "numeric", nullable: true),
                    Macd = table.Column<decimal>(type: "numeric", nullable: true),
                    MacdSignal = table.Column<decimal>(type: "numeric", nullable: true),
                    BollingerUpper = table.Column<decimal>(type: "numeric", nullable: true),
                    BollingerLower = table.Column<decimal>(type: "numeric", nullable: true),
                    Ma9 = table.Column<decimal>(type: "numeric", nullable: true),
                    Ma21 = table.Column<decimal>(type: "numeric", nullable: true),
                    Notes = table.Column<string>(type: "text", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Analyses", x => x.Id);
                    table.ForeignKey(
                        name: "FK_Analyses_Stocks_StockId",
                        column: x => x.StockId,
                        principalTable: "Stocks",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.InsertData(
                table: "Stocks",
                columns: new[] { "Id", "CreatedAt", "Name", "Sector", "Ticker" },
                values: new object[,]
                {
                    { new Guid("00000000-0000-0000-0000-000000000001"), new DateTime(2026, 6, 28, 11, 34, 11, 124, DateTimeKind.Utc).AddTicks(3811), "Petrobras PN", "Petróleo & Gás", "PETR4" },
                    { new Guid("00000000-0000-0000-0000-000000000002"), new DateTime(2026, 6, 28, 11, 34, 11, 124, DateTimeKind.Utc).AddTicks(3833), "Vale ON", "Mineração", "VALE3" },
                    { new Guid("00000000-0000-0000-0000-000000000003"), new DateTime(2026, 6, 28, 11, 34, 11, 124, DateTimeKind.Utc).AddTicks(3838), "Itaú Unibanco PN", "Financeiro", "ITUB4" },
                    { new Guid("00000000-0000-0000-0000-000000000004"), new DateTime(2026, 6, 28, 11, 34, 11, 124, DateTimeKind.Utc).AddTicks(3841), "Bradesco PN", "Financeiro", "BBDC4" },
                    { new Guid("00000000-0000-0000-0000-000000000005"), new DateTime(2026, 6, 28, 11, 34, 11, 124, DateTimeKind.Utc).AddTicks(3847), "Ambev ON", "Bebidas", "ABEV3" },
                    { new Guid("00000000-0000-0000-0000-000000000006"), new DateTime(2026, 6, 28, 11, 34, 11, 124, DateTimeKind.Utc).AddTicks(3849), "WEG ON", "Industrial", "WEGE3" },
                    { new Guid("00000000-0000-0000-0000-000000000007"), new DateTime(2026, 6, 28, 11, 34, 11, 124, DateTimeKind.Utc).AddTicks(3863), "Localiza ON", "Mobilidade", "RENT3" },
                    { new Guid("00000000-0000-0000-0000-000000000008"), new DateTime(2026, 6, 28, 11, 34, 11, 124, DateTimeKind.Utc).AddTicks(3866), "Magazine Luiza ON", "Varejo", "MGLU3" },
                    { new Guid("00000000-0000-0000-0000-000000000009"), new DateTime(2026, 6, 28, 11, 34, 11, 124, DateTimeKind.Utc).AddTicks(3868), "Banco do Brasil ON", "Financeiro", "BBAS3" },
                    { new Guid("00000000-0000-0000-0000-000000000010"), new DateTime(2026, 6, 28, 11, 34, 11, 124, DateTimeKind.Utc).AddTicks(3870), "Engie Brasil ON", "Energia Elétrica", "EGIE3" },
                    { new Guid("00000000-0000-0000-0000-000000000011"), new DateTime(2026, 6, 28, 11, 34, 11, 124, DateTimeKind.Utc).AddTicks(3872), "Telefônica ON", "Telecomunicações", "VIVT3" },
                    { new Guid("00000000-0000-0000-0000-000000000012"), new DateTime(2026, 6, 28, 11, 34, 11, 124, DateTimeKind.Utc).AddTicks(3874), "Suzano ON", "Papel & Celulose", "SUZB3" },
                    { new Guid("00000000-0000-0000-0000-000000000013"), new DateTime(2026, 6, 28, 11, 34, 11, 124, DateTimeKind.Utc).AddTicks(3877), "Lojas Renner ON", "Varejo", "LREN3" },
                    { new Guid("00000000-0000-0000-0000-000000000014"), new DateTime(2026, 6, 28, 11, 34, 11, 124, DateTimeKind.Utc).AddTicks(3879), "Hapvida ON", "Saúde", "HAPV3" },
                    { new Guid("00000000-0000-0000-0000-000000000015"), new DateTime(2026, 6, 28, 11, 34, 11, 124, DateTimeKind.Utc).AddTicks(3884), "Raia Drogasil ON", "Saúde", "RADL3" }
                });

            migrationBuilder.CreateIndex(
                name: "IX_Analyses_StockId",
                table: "Analyses",
                column: "StockId");

            migrationBuilder.CreateIndex(
                name: "IX_Stocks_Ticker",
                table: "Stocks",
                column: "Ticker",
                unique: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "Analyses");

            migrationBuilder.DropTable(
                name: "Stocks");
        }
    }
}
