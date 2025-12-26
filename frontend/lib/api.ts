const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

export interface ETFData {
    name: string;
    yield: number;
    cagr: number;
    stock_dividend: number;
    yahoo_symbol: string;
}

export interface BacktestRequest {
    portfolio: Record<string, number>;
    initial_capital: number;
    monthly_contribution: number;
    start_year: number;
    end_year: number;
    use_leverage: boolean;
    leverage_config?: {
        ltv: number;
        margin_interest_rate: number;
        maintenance_ratio: number;
        liquidation_ratio: number;
        re_leverage_ratio: number;
    };
    dividend_frequency: number;
    transaction_fee_buy: number;
    transaction_fee_sell: number;
    dividend_tax_rate: number;
}

export interface AdvisorRequest {
    age: number;
    risk_level: string;
    goal: string;
    monthly_savings: number;
}

export interface SimulationRequest {
    portfolio: Record<string, number>;
    initial_capital: number;
    monthly_contribution: number;
    years: number;
    num_simulations: number;
    mu: number;
    sigma: number;
}

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
            "Content-Type": "application/json",
        },
        ...options,
    });

    if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
}

// ETF API
export async function getAllETFs(): Promise<{ success: boolean; data: Record<string, ETFData> }> {
    return fetchAPI("/api/v1/etf");
}

export async function getETFDetail(symbol: string) {
    return fetchAPI(`/api/v1/etf/${symbol}`);
}

export async function getETFPrice(symbol: string) {
    return fetchAPI(`/api/v1/etf/${symbol}/price`);
}

// Backtest API
export async function runBacktest(request: BacktestRequest) {
    return fetchAPI("/api/v1/backtest", {
        method: "POST",
        body: JSON.stringify(request),
    });
}

// Advisor API
export async function getRecommendation(request: AdvisorRequest) {
    return fetchAPI("/api/v1/advisor/recommend", {
        method: "POST",
        body: JSON.stringify(request),
    });
}

// Simulation API
export async function runMonteCarlo(request: SimulationRequest) {
    return fetchAPI("/api/v1/simulation/monte-carlo", {
        method: "POST",
        body: JSON.stringify(request),
    });
}
