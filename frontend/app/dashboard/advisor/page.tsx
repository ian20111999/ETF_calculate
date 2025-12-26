"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Badge } from "@/components/ui/badge";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import Link from "next/link";
import {
    Brain,
    Loader2,
    ChevronRight,
    PieChart,
    TrendingUp,
    Clock,
    Percent,
    Wallet,
    FlaskConical,
    Sparkles,
} from "lucide-react";

interface Recommendation {
    strategy_name: string;
    portfolio: Record<string, number>;
    use_leverage: boolean;
    ltv: number;
    investment_horizon: number;
    expected_return: number;
    avg_dividend_yield: number;
    description: string;
    projected_wealth: {
        total_contribution: number;
        final_wealth: number;
        profit: number;
    };
}

export default function AdvisorPage() {
    const [age, setAge] = useState(30);
    const [riskLevel, setRiskLevel] = useState("穩健 - 可接受波動");
    const [goal, setGoal] = useState("退休");
    const [monthlySavings, setMonthlySavings] = useState(20000);
    const [loading, setLoading] = useState(false);
    const [recommendation, setRecommendation] = useState<Recommendation | null>(null);

    const handleSubmit = async () => {
        setLoading(true);

        try {
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080"}/api/v1/advisor/recommend`,
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        age,
                        risk_level: riskLevel,
                        goal,
                        monthly_savings: monthlySavings,
                    }),
                }
            );

            const data = await response.json();
            if (data.success) {
                setRecommendation(data.data);
            }
        } catch (error) {
            console.error("API Error:", error);
        } finally {
            setLoading(false);
        }
    };

    const formatCurrency = (value: number) =>
        new Intl.NumberFormat("zh-TW", { style: "currency", currency: "TWD", maximumFractionDigits: 0 }).format(value);

    return (
        <div className="space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
                        <Brain className="w-6 h-6 text-white" />
                    </div>
                    AI 投資顧問
                </h1>
                <p className="text-muted-foreground mt-2">回答幾個問題，讓 AI 為您量身打造投資組合</p>
            </div>

            <div className="grid lg:grid-cols-5 gap-8">
                {/* Input Form */}
                <div className="lg:col-span-2 space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>投資人問卷</CardTitle>
                            <CardDescription>請填寫以下資訊以獲得個人化建議</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            {/* Age */}
                            <div className="space-y-3">
                                <label className="text-sm font-medium flex items-center justify-between">
                                    <span>您的年齡</span>
                                    <Badge variant="secondary">{age} 歲</Badge>
                                </label>
                                <Slider
                                    value={[age]}
                                    onValueChange={(v) => setAge(v[0])}
                                    min={20}
                                    max={80}
                                    step={1}
                                />
                            </div>

                            {/* Risk Level */}
                            <div className="space-y-3">
                                <label className="text-sm font-medium">風險承受度</label>
                                <Select value={riskLevel} onValueChange={setRiskLevel}>
                                    <SelectTrigger>
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="保守 - 不想賠錢">🛡️ 保守 - 不想賠錢</SelectItem>
                                        <SelectItem value="穩健 - 可接受波動">⚖️ 穩健 - 可接受波動</SelectItem>
                                        <SelectItem value="積極 - 追求高報酬">🚀 積極 - 追求高報酬</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>

                            {/* Goal */}
                            <div className="space-y-3">
                                <label className="text-sm font-medium">投資目標</label>
                                <Select value={goal} onValueChange={setGoal}>
                                    <SelectTrigger>
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="存第一桶金">💰 存第一桶金</SelectItem>
                                        <SelectItem value="買房">🏠 買房</SelectItem>
                                        <SelectItem value="退休">🌴 退休</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>

                            {/* Monthly Savings */}
                            <div className="space-y-3">
                                <label className="text-sm font-medium">每月可存金額（元）</label>
                                <Input
                                    type="number"
                                    value={monthlySavings}
                                    onChange={(e) => setMonthlySavings(parseInt(e.target.value) || 0)}
                                    min={1000}
                                    step={1000}
                                />
                            </div>

                            <Button
                                onClick={handleSubmit}
                                disabled={loading}
                                className="w-full bg-gradient-to-r from-violet-500 to-purple-600 hover:opacity-90"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                        AI 分析中...
                                    </>
                                ) : (
                                    <>
                                        <Brain className="w-4 h-4 mr-2" />
                                        生成 AI 投資建議
                                    </>
                                )}
                            </Button>
                        </CardContent>
                    </Card>
                </div>

                {/* Results */}
                <div className="lg:col-span-3 space-y-6">
                    {recommendation ? (
                        <>
                            {/* Strategy Badge */}
                            <Card>
                                <CardContent className="pt-6">
                                    <div className="text-center">
                                        <Badge className="text-lg px-4 py-2 bg-gradient-to-r from-violet-500 to-purple-600">
                                            {recommendation.strategy_name}
                                        </Badge>
                                        <p className="text-muted-foreground mt-4">{recommendation.description}</p>
                                    </div>
                                </CardContent>
                            </Card>

                            {/* Key Metrics */}
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <Card>
                                    <CardContent className="pt-6 text-center">
                                        <Clock className="w-6 h-6 mx-auto text-muted-foreground mb-2" />
                                        <div className="text-2xl font-bold">{recommendation.investment_horizon}</div>
                                        <p className="text-xs text-muted-foreground">投資年限</p>
                                    </CardContent>
                                </Card>
                                <Card>
                                    <CardContent className="pt-6 text-center">
                                        <Percent className="w-6 h-6 mx-auto text-muted-foreground mb-2" />
                                        <div className="text-2xl font-bold text-green-500">{recommendation.expected_return}%</div>
                                        <p className="text-xs text-muted-foreground">預期年化報酬</p>
                                    </CardContent>
                                </Card>
                                <Card>
                                    <CardContent className="pt-6 text-center">
                                        <PieChart className="w-6 h-6 mx-auto text-muted-foreground mb-2" />
                                        <div className="text-2xl font-bold">{Object.keys(recommendation.portfolio).length}</div>
                                        <p className="text-xs text-muted-foreground">資產類別</p>
                                    </CardContent>
                                </Card>
                                <Card>
                                    <CardContent className="pt-6 text-center">
                                        <TrendingUp className="w-6 h-6 mx-auto text-muted-foreground mb-2" />
                                        <div className="text-2xl font-bold">
                                            {recommendation.use_leverage ? `${recommendation.ltv}%` : "否"}
                                        </div>
                                        <p className="text-xs text-muted-foreground">槓桿</p>
                                    </CardContent>
                                </Card>
                            </div>

                            {/* Portfolio Allocation */}
                            <Card>
                                <CardHeader>
                                    <CardTitle>投資組合配置</CardTitle>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    {Object.entries(recommendation.portfolio).map(([etf, weight]) => (
                                        <div key={etf} className="space-y-2">
                                            <div className="flex items-center justify-between text-sm">
                                                <span className="font-medium">{etf}</span>
                                                <span className="text-muted-foreground">{weight}%</span>
                                            </div>
                                            <Progress value={weight} className="h-2" />
                                        </div>
                                    ))}
                                </CardContent>
                            </Card>

                            {/* Projected Wealth */}
                            <Card>
                                <CardHeader>
                                    <CardTitle>預期投資成果</CardTitle>
                                    <CardDescription>假設年化報酬 {recommendation.expected_return}%</CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <div className="grid grid-cols-3 gap-4 text-center">
                                        <div>
                                            <div className="text-lg font-bold">
                                                {formatCurrency(recommendation.projected_wealth.total_contribution)}
                                            </div>
                                            <p className="text-xs text-muted-foreground">累計投入</p>
                                        </div>
                                        <div>
                                            <div className="text-lg font-bold text-green-500">
                                                {formatCurrency(recommendation.projected_wealth.final_wealth)}
                                            </div>
                                            <p className="text-xs text-muted-foreground">{recommendation.investment_horizon} 年後資產</p>
                                        </div>
                                        <div>
                                            <div className="text-lg font-bold text-green-500">
                                                {formatCurrency(recommendation.projected_wealth.profit)}
                                            </div>
                                            <p className="text-xs text-muted-foreground">預期獲利</p>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>

                            {/* Actions */}
                            <div className="flex gap-4">
                                <Link href="/dashboard/backtest" className="flex-1">
                                    <Button variant="outline" className="w-full">
                                        <FlaskConical className="w-4 h-4 mr-2" />
                                        帶入回測實驗室
                                    </Button>
                                </Link>
                                <Link href="/dashboard/simulation" className="flex-1">
                                    <Button variant="outline" className="w-full">
                                        <Sparkles className="w-4 h-4 mr-2" />
                                        模擬未來表現
                                    </Button>
                                </Link>
                            </div>
                        </>
                    ) : (
                        <Card className="flex flex-col items-center justify-center min-h-[400px] border-dashed">
                            <Brain className="w-16 h-16 text-muted-foreground/50 mb-4" />
                            <p className="text-muted-foreground text-center">
                                填寫左側問卷後
                                <br />
                                點擊「生成 AI 投資建議」查看結果
                            </p>
                        </Card>
                    )}
                </div>
            </div>
        </div>
    );
}
