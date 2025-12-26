"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Slider } from "@/components/ui/slider";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
    Sparkles,
    Loader2,
    TrendingUp,
    TrendingDown,
    BarChart3,
    Target,
    AlertTriangle,
} from "lucide-react";
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    BarChart,
    Bar,
    ReferenceLine,
} from "recharts";

interface SimulationResult {
    percentiles: {
        p5: number;
        p25: number;
        p50: number;
        p75: number;
        p95: number;
    };
    statistics: {
        mean: number;
        std: number;
        min: number;
        max: number;
        loss_probability: number;
        total_contribution: number;
    };
    paths: {
        time_points: number[];
        p5: number[];
        p50: number[];
        p95: number[];
    };
    summary_table: Array<{
        Scenario: string;
        Final_Wealth: number;
        Total_Return: number;
        ROI: number;
    }>;
}

export default function SimulationPage() {
    const [initialCapital, setInitialCapital] = useState(1000000);
    const [monthlyContribution, setMonthlyContribution] = useState(20000);
    const [years, setYears] = useState(10);
    const [numSimulations, setNumSimulations] = useState(1000);
    const [mu, setMu] = useState(8); // %
    const [sigma, setSigma] = useState(15); // %
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<SimulationResult | null>(null);

    const handleSimulate = async () => {
        setLoading(true);

        try {
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080"}/api/v1/simulation/monte-carlo`,
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        portfolio: { "0050": 100 },
                        initial_capital: initialCapital,
                        monthly_contribution: monthlyContribution,
                        years,
                        num_simulations: numSimulations,
                        mu: mu / 100,
                        sigma: sigma / 100,
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
    const pathChartData = result?.paths.time_points.map((t, i) => ({
        year: t,
        p5: result.paths.p5[i],
        p50: result.paths.p50[i],
        p95: result.paths.p95[i],
        principal: initialCapital + monthlyContribution * t * 12,
    }));

    return (
        <div className="space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
                        <Sparkles className="w-6 h-6 text-white" />
                    </div>
                    水晶球模擬
                </h1>
                <p className="text-muted-foreground mt-2">使用蒙地卡羅模擬預測未來投資表現</p>
            </div>

            <div className="grid lg:grid-cols-4 gap-8">
                {/* Parameters */}
                <div className="lg:col-span-1 space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>模擬參數</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            <div className="space-y-2">
                                <label className="text-sm font-medium">初始資金（元）</label>
                                <Input
                                    type="number"
                                    value={initialCapital}
                                    onChange={(e) => setInitialCapital(parseInt(e.target.value) || 0)}
                                    step={100000}
                                />
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium">每月定投（元）</label>
                                <Input
                                    type="number"
                                    value={monthlyContribution}
                                    onChange={(e) => setMonthlyContribution(parseInt(e.target.value) || 0)}
                                    step={5000}
                                />
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium flex justify-between">
                                    <span>模擬年數</span>
                                    <Badge variant="secondary">{years} 年</Badge>
                                </label>
                                <Slider value={[years]} onValueChange={(v) => setYears(v[0])} min={1} max={30} />
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium flex justify-between">
                                    <span>預期年化報酬率</span>
                                    <Badge variant="secondary">{mu}%</Badge>
                                </label>
                                <Slider value={[mu]} onValueChange={(v) => setMu(v[0])} min={-10} max={20} step={0.5} />
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium flex justify-between">
                                    <span>年化波動度</span>
                                    <Badge variant="secondary">{sigma}%</Badge>
                                </label>
                                <Slider value={[sigma]} onValueChange={(v) => setSigma(v[0])} min={5} max={40} />
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium flex justify-between">
                                    <span>模擬次數</span>
                                    <Badge variant="secondary">{numSimulations}</Badge>
                                </label>
                                <Slider value={[numSimulations]} onValueChange={(v) => setNumSimulations(v[0])} min={100} max={5000} step={100} />
                            </div>

                            <Button
                                onClick={handleSimulate}
                                disabled={loading}
                                className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:opacity-90"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                        模擬中...
                                    </>
                                ) : (
                                    <>
                                        <Sparkles className="w-4 h-4 mr-2" />
                                        執行模擬
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
                            {/* Percentile Cards */}
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <Card>
                                    <CardContent className="pt-6 text-center">
                                        <TrendingDown className="w-6 h-6 mx-auto text-red-500 mb-2" />
                                        <div className="text-sm text-muted-foreground">最差情況 (5%)</div>
                                        <div className="text-xl font-bold">{formatCurrency(result.percentiles.p5)}</div>
                                    </CardContent>
                                </Card>
                                <Card>
                                    <CardContent className="pt-6 text-center">
                                        <Target className="w-6 h-6 mx-auto text-primary mb-2" />
                                        <div className="text-sm text-muted-foreground">中位數 (50%)</div>
                                        <div className="text-xl font-bold text-primary">{formatCurrency(result.percentiles.p50)}</div>
                                    </CardContent>
                                </Card>
                                <Card>
                                    <CardContent className="pt-6 text-center">
                                        <TrendingUp className="w-6 h-6 mx-auto text-green-500 mb-2" />
                                        <div className="text-sm text-muted-foreground">最佳情況 (95%)</div>
                                        <div className="text-xl font-bold text-green-500">{formatCurrency(result.percentiles.p95)}</div>
                                    </CardContent>
                                </Card>
                                <Card>
                                    <CardContent className="pt-6 text-center">
                                        <AlertTriangle className={`w-6 h-6 mx-auto mb-2 ${result.statistics.loss_probability > 10 ? "text-red-500" : "text-amber-500"}`} />
                                        <div className="text-sm text-muted-foreground">虧損機率</div>
                                        <div className={`text-xl font-bold ${result.statistics.loss_probability > 10 ? "text-red-500" : "text-amber-500"}`}>
                                            {result.statistics.loss_probability.toFixed(1)}%
                                        </div>
                                    </CardContent>
                                </Card>
                            </div>

                            {/* Confidence Interval Chart */}
                            <Card>
                                <CardHeader>
                                    <CardTitle>信賴區間預測</CardTitle>
                                    <CardDescription>陰影區域為 90% 信賴區間</CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <div className="h-[400px]">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <AreaChart data={pathChartData}>
                                                <defs>
                                                    <linearGradient id="colorConfidence" x1="0" y1="0" x2="0" y2="1">
                                                        <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                                                        <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.05} />
                                                    </linearGradient>
                                                </defs>
                                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                                <XAxis dataKey="year" stroke="#94A3B8" fontSize={12} tickFormatter={(v) => `${v}年`} />
                                                <YAxis stroke="#94A3B8" fontSize={12} tickFormatter={(v) => `${(v / 1000000).toFixed(1)}M`} />
                                                <Tooltip
                                                    contentStyle={{ backgroundColor: "#1E293B", border: "1px solid #334155" }}
                                                    formatter={(value) => [formatCurrency(value as number), ""]}
                                                />
                                                <Area type="monotone" dataKey="p95" stackId="1" stroke="none" fill="url(#colorConfidence)" />
                                                <Area type="monotone" dataKey="p5" stackId="2" stroke="none" fill="#0F172A" />
                                                <Area type="monotone" dataKey="p50" stroke="#3B82F6" strokeWidth={3} fill="none" name="中位數" />
                                                <Area type="monotone" dataKey="principal" stroke="#F59E0B" strokeWidth={2} strokeDasharray="5 5" fill="none" name="累計本金" />
                                            </AreaChart>
                                        </ResponsiveContainer>
                                    </div>
                                </CardContent>
                            </Card>

                            {/* Summary Table */}
                            <Card>
                                <CardHeader>
                                    <CardTitle>關鍵百分位數分析</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="overflow-x-auto">
                                        <table className="w-full text-sm">
                                            <thead>
                                                <tr className="border-b border-border">
                                                    <th className="text-left py-3 px-4">情境</th>
                                                    <th className="text-right py-3 px-4">最終財富</th>
                                                    <th className="text-right py-3 px-4">總報酬</th>
                                                    <th className="text-right py-3 px-4">ROI</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {result.summary_table.map((row, i) => (
                                                    <tr key={i} className="border-b border-border/50 hover:bg-muted/50">
                                                        <td className="py-3 px-4 font-medium">{row.Scenario}</td>
                                                        <td className="text-right py-3 px-4">{formatCurrency(row.Final_Wealth)}</td>
                                                        <td className={`text-right py-3 px-4 ${row.Total_Return >= 0 ? "text-green-500" : "text-red-500"}`}>
                                                            {formatCurrency(row.Total_Return)}
                                                        </td>
                                                        <td className={`text-right py-3 px-4 ${row.ROI >= 0 ? "text-green-500" : "text-red-500"}`}>
                                                            {row.ROI.toFixed(1)}%
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </CardContent>
                            </Card>
                        </>
                    ) : (
                        <Card className="flex flex-col items-center justify-center min-h-[400px] border-dashed">
                            <Sparkles className="w-16 h-16 text-muted-foreground/50 mb-4" />
                            <p className="text-muted-foreground text-center">
                                設定參數後點擊「執行模擬」
                                <br />
                                預測未來投資可能結果
                            </p>
                        </Card>
                    )}
                </div>
            </div>
        </div>
    );
}
