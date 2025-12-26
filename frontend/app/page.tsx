import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Brain,
  FlaskConical,
  Sparkles,
  TrendingUp,
  Shield,
  Zap,
  ChevronRight,
  BarChart3,
  PieChart,
  Target,
  LineChart,
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass border-b">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-chart-3 flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-primary-foreground" />
            </div>
            <span className="text-xl font-bold">SmartWealth AI</span>
          </div>
          <div className="hidden md:flex items-center gap-8">
            <Link href="#features" className="text-muted-foreground hover:text-foreground transition">
              功能
            </Link>
            <Link href="#how-it-works" className="text-muted-foreground hover:text-foreground transition">
              運作方式
            </Link>
            <Link href="/dashboard" className="text-muted-foreground hover:text-foreground transition">
              儀表板
            </Link>
          </div>
          <Link href="/dashboard">
            <Button className="bg-gradient-to-r from-primary to-chart-3 hover:opacity-90">
              開始使用 <ChevronRight className="w-4 h-4 ml-1" />
            </Button>
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 overflow-hidden">
        {/* Background Gradient */}
        <div className="absolute inset-0 bg-gradient-to-b from-primary/5 via-transparent to-transparent" />
        <div className="absolute top-20 left-1/4 w-96 h-96 bg-primary/10 rounded-full blur-3xl" />
        <div className="absolute top-40 right-1/4 w-64 h-64 bg-chart-3/10 rounded-full blur-3xl" />

        <div className="container mx-auto px-6 relative">
          <div className="max-w-4xl mx-auto text-center">
            <Badge variant="outline" className="mb-6 px-4 py-2 text-sm border-primary/30">
              <Sparkles className="w-4 h-4 mr-2" />
              V3.0 - 全新專業版
            </Badge>

            <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
              <span className="text-gradient">SmartWealth AI</span>
              <br />
              <span className="text-foreground">智慧存股領航員</span>
            </h1>

            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              使用 AI 與數據科學為您的財富保駕護航。歷史回測、蒙地卡羅模擬、智能投資組合建議 — 一站式專業分析平台。
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/dashboard/advisor">
                <Button size="lg" className="bg-gradient-to-r from-primary to-chart-3 hover:opacity-90 text-lg px-8 py-6">
                  <Brain className="w-5 h-5 mr-2" />
                  開始智能規劃
                </Button>
              </Link>
              <Link href="/dashboard/backtest">
                <Button size="lg" variant="outline" className="text-lg px-8 py-6">
                  <FlaskConical className="w-5 h-5 mr-2" />
                  進入回測實驗室
                </Button>
              </Link>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-16">
              {[
                { value: "5+", label: "支援 ETF", icon: PieChart },
                { value: "20+", label: "歷史年份", icon: LineChart },
                { value: "1000+", label: "模擬次數", icon: BarChart3 },
                { value: "V3.0", label: "專業版本", icon: Target },
              ].map((stat, i) => (
                <div
                  key={i}
                  className="glass rounded-2xl p-6 animate-fade-in"
                  style={{ animationDelay: `${i * 100}ms` }}
                >
                  <stat.icon className="w-8 h-8 text-primary mb-3 mx-auto" />
                  <div className="text-3xl font-bold text-gradient">{stat.value}</div>
                  <div className="text-sm text-muted-foreground">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">功能特色</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              結合專業金融分析與現代 AI 技術，為您提供全方位的投資決策支援
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: Brain,
                title: "AI 智能顧問",
                description: "根據您的風險偏好與目標，AI 為您量身打造最佳投資組合配置。",
                gradient: "from-violet-500 to-purple-600",
              },
              {
                icon: FlaskConical,
                title: "歷史回測",
                description: "使用 20+ 年真實歷史數據，驗證您的投資策略表現。",
                gradient: "from-pink-500 to-rose-600",
              },
              {
                icon: Sparkles,
                title: "蒙地卡羅模擬",
                description: "執行 1000+ 次模擬，預測未來可能的投資結果與風險。",
                gradient: "from-cyan-500 to-blue-600",
              },
              {
                icon: Shield,
                title: "槓桿風險管理",
                description: "完整模擬質押融資、維持率、追繳與斷頭機制。",
                gradient: "from-emerald-500 to-green-600",
              },
              {
                icon: PieChart,
                title: "多資產組合",
                description: "支援多 ETF 組合配置，自由調整權重比例。",
                gradient: "from-orange-500 to-amber-600",
              },
              {
                icon: Zap,
                title: "即時數據",
                description: "串接 Yahoo Finance API，獲取最新市場數據。",
                gradient: "from-indigo-500 to-blue-600",
              },
            ].map((feature, i) => (
              <Card
                key={i}
                className="group bg-card/50 border-border/50 hover:border-primary/30 transition-all duration-300 hover:-translate-y-1"
              >
                <CardContent className="p-6">
                  <div
                    className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-5 group-hover:scale-110 transition-transform`}
                  >
                    <feature.icon className="w-7 h-7 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                  <p className="text-muted-foreground">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section id="how-it-works" className="py-20 bg-gradient-to-b from-card/30 to-transparent">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">簡單三步驟</h2>
            <p className="text-muted-foreground">快速開始您的智能投資之旅</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            {[
              { step: "01", title: "設定目標", description: "輸入年齡、風險偏好與投資目標" },
              { step: "02", title: "AI 分析", description: "系統為您規劃最佳投資組合" },
              { step: "03", title: "驗證策略", description: "使用回測與模擬驗證您的投資計畫" },
            ].map((item, i) => (
              <div key={i} className="text-center">
                <div className="text-6xl font-bold text-gradient mb-4">{item.step}</div>
                <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
                <p className="text-muted-foreground">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="container mx-auto px-6">
          <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-primary/20 via-chart-3/20 to-primary/20 p-12 md:p-20 text-center">
            <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-chart-3/5" />
            <div className="relative">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">準備好開始了嗎？</h2>
              <p className="text-muted-foreground mb-8 max-w-xl mx-auto">
                立即使用 SmartWealth AI，讓數據科學為您的財富保駕護航
              </p>
              <Link href="/dashboard">
                <Button size="lg" className="bg-gradient-to-r from-primary to-chart-3 hover:opacity-90 text-lg px-10 py-6">
                  免費開始使用
                  <ChevronRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border/50 py-12">
        <div className="container mx-auto px-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-chart-3 flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-primary-foreground" />
              </div>
              <span className="font-semibold">SmartWealth AI</span>
            </div>
            <p className="text-sm text-muted-foreground text-center">
              ⚠️ 本工具僅供教育與研究用途，不構成投資建議。投資有風險，請謹慎評估。
            </p>
            <p className="text-sm text-muted-foreground">
              © 2024 SmartWealth AI. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
