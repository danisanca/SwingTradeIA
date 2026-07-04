FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY SwingTradeIA.Api/SwingTradeIA.Api.csproj SwingTradeIA.Api/
RUN dotnet restore SwingTradeIA.Api/SwingTradeIA.Api.csproj
COPY . .
RUN dotnet publish SwingTradeIA.Api/SwingTradeIA.Api.csproj -c Release -o /app/publish

FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY --from=build /app/publish .
EXPOSE 8080
ENTRYPOINT ["dotnet", "SwingTradeIA.Api.dll"]
