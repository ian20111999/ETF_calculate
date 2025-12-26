import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import {
    Brain,
    FlaskConical,
    Sparkles,
    PieChart,
    TrendingUp,
    TrendingDown,
    ArrowUpRight,
} from "lucide-react";

export default function DashboardPage() {
    return (
        <div className="space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold">儀表板</h1>
                <p className="text-muted-foreground mt-1">歡迎回來，探索您的投資分析工具</p>
            </div>

            {/* Quick Stats */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">支援 ETF</CardTitle>
                        <PieChart className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">5</div>
                        <p className="text-xs text-muted-foreground">0050, 0056, 00878, 00919, 2330</p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">歷史數據</CardTitle>
                        <TrendingUp className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">20+ 年</div>
                        <p className="text-xs text-muted-foreground">來自 Yahoo Finance</p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">模擬能力</CardTitle>
                        <Sparkles className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">5,000+</div>
                        <p className="text-xs text-muted-foreground">蒙地卡羅模擬次數</p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">版本</CardTitle>
                        <Badge variant="secondary">V3.0</Badge>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">專業版</div>
                        <p className="text-xs text-muted-foreground">含槓桿模擬功能</p>
                    </CardContent>
                </Card>
            </div>

            {/* Feature Cards */}
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-2">
                <Card className="group hover:border-primary/50 transition-colors">
                    <CardHeader>
                        <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center mb-4">
                            <Brain className="w-7 h-7 text-white" />
                        </div>
                        <CardTitle className="text-xl">AI 投資顧問</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <p className="text-muted-foreground">
                            回答幾個簡單問題，讓 AI 根據您的風險偏好與目標，為您打造專屬投資組合。
                        </p>
                        <Link href="/dashboard/advisor">
                            <Button className="group-hover:bg-primary transition-colors">
                                開始規劃 <ArrowUpRight className="w-4 h-4 ml-2" />
                            </Button>
                        </Link>
                    </CardContent>
                </Card>

                <Card className="group hover:border-primary/50 transition-colors">
                    <CardHeader>
                        <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-pink-500 to-rose-600 flex items-center justify-center mb-4">
                            <FlaskConical className="w-7 h-7 text-white" />
                        </div>
                        <CardTitle className="text-xl">回測實驗室</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <p className="text-muted-foreground">
                            使用真實歷史數據驗證您的投資策略，支援槓桿模擬、多資產配置。
                        </p>
                        <Link href="/dashboard/backtest">
                            <Button variant="outline" className="group-hover:bg-accent transition-colors">
                                進入實驗室 <ArrowUpRight className="w-4 h-4 ml-2" />
                            </Button>
                        </Link>
                    </CardContent>
                </Card>

                <Card className="group hover:border-primary/50 transition-colors">
                    <CardHeader>
                        <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center mb-4">
                            <Sparkles className="w-7 h-7 text-white" />
                        </div>
                        <CardTitle className="text-xl">水晶球模擬</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <p className="text-muted-foreground">
                            使用蒙地卡羅模擬預測未來投資表現，評估風險與報酬的可能性。
                        </p>
                        <Link href="/dashboard/simulation">
                            <Button variant="outline" className="group-hover:bg-accent transition-colors">
                                模擬未來 <ArrowUpRight className="w-4 h-4 ml-2" />
                            </Button>
                        </Link>
                    </CardContent>
                </Card>

                <Card className="group hover:border-primary/50 transition-colors">
                    <CardHeader>
                        <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center mb-4">
                            <PieChart className="w-7 h-7 text-white" />
                        </div>
                        <CardTitle className="text-xl">市場總覽</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <p className="text-muted-foreground">
                            查看所有支援 ETF 的詳細資訊，包含殖利率、成長率與即時價格。
                        </p>
                        <Link href="/dashboard/market">
                            <Button variant="outline" className="group-hover:bg-accent transition-colors">
                                查看市場 <ArrowUpRight className="w-4 h-4 ml-2" />
                            </Button>
                        </Link>
                    </CardContent>
                </Card>
            </div>

            {/* Risk Warning */}
            <Card className="border-amber-500/30 bg-amber-500/5">
                <CardContent className="pt-6">
                    <div className="flex items-start gap-4">
                        <div className="p-2 rounded-lg bg-amber-500/10">
                            <TrendingDown className="w-5 h-5 text-amber-500" />
                        </div>
                        <div>
                            <h3 className="font-semibold text-amber-500 mb-1">風險提示</h3>
                            <p className="text-sm text-muted-foreground">
                                本工具僅供教育與研究用途，不構成投資建議。歷史回測結果不代表未來表現，投資有風險，請謹慎評估自身風險承受能力。
                            </p>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
