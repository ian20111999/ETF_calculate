"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { PieChart, TrendingUp, Percent, RefreshCw, Loader2 } from "lucide-react";

interface ETFData {
    name: string;
    yield: number;
    cagr: number;
    stock_dividend: number;
    yahoo_symbol: string;
}

export default function MarketPage() {
    const [etfs, setEtfs] = useState<Record<string, ETFData>>({});
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);

    const fetchETFs = async () => {
        try {
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080"}/api/v1/etf`
            );
            const data = await response.json();
            if (data.success) {
                setEtfs(data.data);
            }
        } catch (error) {
            console.error("API Error:", error);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    useEffect(() => {
        fetchETFs();
    }, []);

    const handleRefresh = () => {
        setRefreshing(true);
        fetchETFs();
    };

    const getTypeColor = (symbol: string) => {
        if (symbol === "0050" || symbol === "2330") return "from-blue-500 to-cyan-500";
        return "from-emerald-500 to-green-500";
    };

    const getTypeLabel = (symbol: string) => {
        if (symbol === "0050" || symbol === "2330") return "市值型";
        return "高股息";
    };

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center">
                            <PieChart className="w-6 h-6 text-white" />
                        </div>
                        市場總覽
                    </h1>
                    <p className="text-muted-foreground mt-2">查看所有支援 ETF 的詳細資訊</p>
                </div>
                <Button variant="outline" onClick={handleRefresh} disabled={refreshing}>
                    {refreshing ? (
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    ) : (
                        <RefreshCw className="w-4 h-4 mr-2" />
                    )}
                    重新整理
                </Button>
            </div>

            {/* ETF Grid */}
            {loading ? (
                <div className="flex items-center justify-center min-h-[400px]">
                    <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
                </div>
            ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {Object.entries(etfs).map(([symbol, data]) => (
                        <Card key={symbol} className="group hover:border-primary/50 transition-all hover:-translate-y-1">
                            <CardHeader>
                                <div className="flex items-start justify-between">
                                    <div>
                                        <CardTitle className="text-2xl">{symbol}</CardTitle>
                                        <CardDescription>{data.name}</CardDescription>
                                    </div>
                                    <Badge className={`bg-gradient-to-r ${getTypeColor(symbol)} text-white`}>
                                        {getTypeLabel(symbol)}
                                    </Badge>
                                </div>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="bg-muted/50 rounded-lg p-3">
                                        <div className="flex items-center gap-2 text-muted-foreground mb-1">
                                            <Percent className="w-4 h-4" />
                                            <span className="text-xs">殖利率</span>
                                        </div>
                                        <div className="text-xl font-bold text-green-500">{data.yield}%</div>
                                    </div>
                                    <div className="bg-muted/50 rounded-lg p-3">
                                        <div className="flex items-center gap-2 text-muted-foreground mb-1">
                                            <TrendingUp className="w-4 h-4" />
                                            <span className="text-xs">年化成長</span>
                                        </div>
                                        <div className="text-xl font-bold text-primary">{data.cagr}%</div>
                                    </div>
                                </div>

                                <div className="text-sm text-muted-foreground">
                                    <span className="font-medium">Yahoo 代碼: </span>
                                    <code className="bg-muted px-2 py-0.5 rounded">{data.yahoo_symbol}</code>
                                </div>

                                {data.stock_dividend > 0 && (
                                    <div className="text-sm text-muted-foreground">
                                        <span className="font-medium">股票股利: </span>
                                        {data.stock_dividend}%
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}

            {/* Info Card */}
            <Card className="border-primary/30 bg-primary/5">
                <CardContent className="pt-6">
                    <div className="flex items-start gap-4">
                        <div className="p-2 rounded-lg bg-primary/10">
                            <PieChart className="w-5 h-5 text-primary" />
                        </div>
                        <div>
                            <h3 className="font-semibold text-primary mb-1">ETF 類型說明</h3>
                            <div className="text-sm text-muted-foreground space-y-1">
                                <p><span className="font-medium text-blue-400">市值型</span>：追蹤市場指數，追求資本利得成長（如 0050、台積電）</p>
                                <p><span className="font-medium text-green-400">高股息型</span>：精選高殖利率股票，追求穩定現金流（如 0056、00878、00919）</p>
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
