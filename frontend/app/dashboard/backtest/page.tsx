"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Slider } from "@/components/ui/slider";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import {
    FlaskConical,
    Loader2,
    TrendingUp,
    TrendingDown,
    DollarSign,
    Percent,
    BarChart3,
    LineChart,
} from "lucide-react";
import {
    LineChart as ReLineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Legend,
    AreaChart,
    Area,
    BarChart,
    Bar,
    ReferenceLine,
} from "recharts";

const ETF_OPTIONS = [
    { value: "0050", label: "0050 元大台灣50" },
    { value: "0056", label: "0056 元大高股息" },
    { value: "00878", label: "00878 國泰永續高股息" },
    { value: "00919", label: "00919 群益台灣精選高息" },
    { value: "2330", label: "2330 台積電" },
];

interface BacktestResult {
    regular: {
        records: Array<{
            Year: number;
            Month: number;
            "Net Equity": number;
            Principal: number;
            Monthly_Return: number;
        }>;
        summary: {
            final_equity: number;
            total_principal: number;
            net_profit: number;
            roi: number;
        };
    };
    leverage?: {
        records: Array<{
            Year: number;
            Month: number;
            "Net Equity": number;
            Principal: number;
        }>;
        summary: {
            final_equity: number;
            total_principal: number;
            net_profit: number;
            roi: number;
            outperformance: number;
        };
    };
}

export default function BacktestPage() {
    const [selectedETF, setSelectedETF] = useState("0050");
    const [portfolioWeight, setPortfolioWeight] = useState(100);
    const [initialCapital, setInitialCapital] = useState(1000000);
    const [monthlyContribution, setMonthlyContribution] = useState(20000);
    const [years, setYears] = useState(10);
    const [useLeverage, setUseLeverage] = useState(false);
    const [ltv, setLtv] = useState(60);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<BacktestResult | null>(null);

    const currentYear = new Date().getFullYear() - 1;

    const handleBacktest = async () => {
        setLoading(true);

        try {
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080"}/api/v1/backtest`,
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        portfolio: { [selectedETF]: portfolioWeight },
                        initial_capital: initialCapital,
                        monthly_contribution: monthlyContribution,
                        start_year: currentYear - years + 1,
                        end_year: currentYear,
                        use_leverage: useLeverage,
                        leverage_config: useLeverage ? { ltv } : undefined,
                        dividend_frequency: 4,
                        transaction_fee_buy: 0.1425,
                        transaction_fee_sell: 0.4425,
                        dividend_tax_rate: 2.11,
                    }),
                }
            );

            const data = await response.json();
            if (data.success) {
                setResult(data.data);
            }
        } catch (error) {
            console.error("API Error:", error);
        } finally {
            setLoading(false);
        }
    };

    const formatCurrency = (value: number) =>
        new Intl.NumberFormat("zh-TW", { style: "currency", currency: "TWD", maximumFractionDigits: 0 }).format(value);

    // Prepare chart data
    const chartData = result?.regular.records
        .filter((_, i) => i % 3 === 0) // 每 3 個月取一個點
        .map((record, i) => ({
            period: `${record.Year}/${record.Month}`,
            regular: record["Net Equity"],
            leverage: result.leverage?.records[i * 3]?.["Net Equity"] || null,
            principal: record.Principal,
        }));

    return (
        <div className="space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500 to-rose-600 flex items-center justify-center">
                        <FlaskConical className="w-6 h-6 text-white" />
                    </div>
                    回測實驗室
                </h1>
                <p className="text-muted-foreground mt-2">使用歷史數據驗證您的投資策略</p>
            </div>

            <div className="grid lg:grid-cols-4 gap-8">
                {/* Parameters Panel */}
                <div className="lg:col-span-1 space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>參數設定</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            {/* ETF Selection */}
                            <div className="space-y-2">
                                <label className="text-sm font-medium">選擇 ETF</label>
                                <Select value={selectedETF} onValueChange={setSelectedETF}>
                                    <SelectTrigger>
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {ETF_OPTIONS.map((etf) => (
                                            <SelectItem key={etf.value} value={etf.value}>
                                                {etf.label}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>

                            {/* Initial Capital */}
                            <div className="space-y-2">
                                <label className="text-sm font-medium">初始資金（元）</label>
                                <Input
                                    type="number"
                                    value={initialCapital}
                                    onChange={(e) => setInitialCapital(parseInt(e.target.value) || 0)}
                                    step={100000}
                                />
                            </div>

                            {/* Monthly Contribution */}
                            <div className="space-y-2">
                                <label className="text-sm font-medium">每月定投（元）</label>
                                <Input
                                    type="number"
                                    value={monthlyContribution}
                                    onChange={(e) => setMonthlyContribution(parseInt(e.target.value) || 0)}
                                    step={5000}
                                />
                            </div>

                            {/* Years */}
                            <div className="space-y-2">
                                <label className="text-sm font-medium flex items-center justify-between">
                                    <span>回測年數</span>
                                    <Badge variant="secondary">{years} 年</Badge>
                                </label>
                                <Slider
                                    value={[years]}
                                    onValueChange={(v) => setYears(v[0])}
                                    min={1}
                                    max={20}
                                    step={1}
                                />
                                <p className="text-xs text-muted-foreground">
                                    {currentYear - years + 1} - {currentYear}
                                </p>
                            </div>

                            {/* Leverage Toggle */}
                            <div className="space-y-2">
                                <label className="flex items-center gap-2 text-sm font-medium">
                                    <input
                                        type="checkbox"
                                        checked={useLeverage}
                                        onChange={(e) => setUseLeverage(e.target.checked)}
                                        className="rounded"
                                    />
                                    使用槓桿
                                </label>
                            </div>

                            {useLeverage && (
                                <div className="space-y-2">
                                    <label className="text-sm font-medium flex items-center justify-between">
                                        <span>質押成數</span>
                                        <Badge variant="secondary">{ltv}%</Badge>
                                    </label>
                                    <Slider
                                        value={[ltv]}
                                        onValueChange={(v) => setLtv(v[0])}
                                        min={10}
                                        max={70}
                                        step={10}
                                    />
                                </div>
                            )}

                            <Button
                                onClick={handleBacktest}
                                disabled={loading}
                                className="w-full bg-gradient-to-r from-pink-500 to-rose-600 hover:opacity-90"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                        計算中...
                                    </>
                                ) : (
                                    <>
                                        <FlaskConical className="w-4 h-4 mr-2" />
                                        開始回測
                                    </>
                                )}
                            </Button>
                        </CardContent>
                    </Card>
                </div>

                {/* Results */}
                <div className="lg:col-span-3 space-y-6">
                    {result ? (
                        <>
                            {/* Summary Cards */}
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <Card>
                                    <CardContent className="pt-6">
                                        <div className="flex items-center gap-2 text-muted-foreground mb-2">
                                            <DollarSign className="w-4 h-4" />
                                            <span className="text-sm">最終淨資產</span>
                                        </div>
                                        <div className="text-2xl font-bold">
                                            {formatCurrency(result.regular.summary.final_equity)}
                                        </div>
                                    </CardContent>
                                </Card>
                                <Card>
                                    <CardContent className="pt-6">
                                        <div className="flex items-center gap-2 text-muted-foreground mb-2">
                                            <TrendingUp className="w-4 h-4" />
                                            <span className="text-sm">累計投入</span>
                                        </div>
                                        <div className="text-2xl font-bold">
                                            {formatCurrency(result.regular.summary.total_principal)}
                                        </div>
                                    </CardContent>
                                </Card>
                                <Card>
                                    <CardContent className="pt-6">
                                        <div className="flex items-center gap-2 text-muted-foreground mb-2">
                                            <BarChart3 className="w-4 h-4" />
                                            <span className="text-sm">淨收益</span>
                                        </div>
                                        <div className={`text-2xl font-bold ${result.regular.summary.net_profit >= 0 ? "text-green-500" : "text-red-500"}`}>
                                            {formatCurrency(result.regular.summary.net_profit)}
                                        </div>
                                    </CardContent>
                                </Card>
                                <Card>
                                    <CardContent className="pt-6">
                                        <div className="flex items-center gap-2 text-muted-foreground mb-2">
                                            <Percent className="w-4 h-4" />
                                            <span className="text-sm">總報酬率</span>
                                        </div>
                                        <div className={`text-2xl font-bold ${result.regular.summary.roi >= 0 ? "text-green-500" : "text-red-500"}`}>
                                            {result.regular.summary.roi.toFixed(1)}%
                                        </div>
                                    </CardContent>
                                </Card>
                            </div>

                            {/* Leverage Comparison */}
                            {result.leverage && (
                                <Card className="border-primary/30 bg-primary/5">
                                    <CardContent className="pt-6">
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <p className="text-sm text-muted-foreground">槓桿策略表現</p>
                                                <p className="text-2xl font-bold">{formatCurrency(result.leverage.summary.final_equity)}</p>
                                            </div>
                                            <Badge className="text-lg px-4 py-2 bg-green-500/20 text-green-500">
                                                +{result.leverage.summary.outperformance.toFixed(1)}% 超額報酬
                                            </Badge>
                                        </div>
                                    </CardContent>
                                </Card>
                            )}

                            {/* Chart */}
                            <Card>
                                <CardHeader>
                                    <CardTitle>累積財富趨勢</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="h-[400px]">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <AreaChart data={chartData}>
                                                <defs>
                                                    <linearGradient id="colorRegular" x1="0" y1="0" x2="0" y2="1">
                                                        <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                                                        <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                                                    </linearGradient>
                                                    <linearGradient id="colorLeverage" x1="0" y1="0" x2="0" y2="1">
                                                        <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.3} />
                                                        <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0} />
                                                    </linearGradient>
                                                </defs>
                                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                                <XAxis dataKey="period" stroke="#94A3B8" fontSize={12} />
                                                <YAxis stroke="#94A3B8" fontSize={12} tickFormatter={(v) => `${(v / 1000000).toFixed(1)}M`} />
                                                <Tooltip
                                                    contentStyle={{ backgroundColor: "#1E293B", border: "1px solid #334155" }}
                                                    formatter={(value) => [formatCurrency(value as number), ""]}
                                                />
                                                <Legend />
                                                <Area
                                                    type="monotone"
                                                    dataKey="principal"
                                                    name="累計本金"
                                                    stroke="#F59E0B"
                                                    strokeDasharray="5 5"
                                                    fill="none"
                                                />
                                                <Area
                                                    type="monotone"
                                                    dataKey="regular"
                                                    name="無槓桿"
                                                    stroke="#3B82F6"
                                                    fillOpacity={1}
                                                    fill="url(#colorRegular)"
                                                />
                                                {result.leverage && (
                                                    <Area
                                                        type="monotone"
                                                        dataKey="leverage"
                                                        name="槓桿"
                                                        stroke="#8B5CF6"
                                                        fillOpacity={1}
                                                        fill="url(#colorLeverage)"
                                                    />
                                                )}
                                            </AreaChart>
                                        </ResponsiveContainer>
                                    </div>
                                </CardContent>
                            </Card>
                        </>
                    ) : (
                        <Card className="flex flex-col items-center justify-center min-h-[400px] border-dashed">
                            <FlaskConical className="w-16 h-16 text-muted-foreground/50 mb-4" />
                            <p className="text-muted-foreground text-center">
                                設定參數後點擊「開始回測」
                                <br />
                                查看歷史回測結果
                            </p>
                        </Card>
                    )}
                </div>
            </div>
        </div>
    );
}
