"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
    LayoutDashboard,
    Brain,
    FlaskConical,
    Sparkles,
    PieChart,
    TrendingUp,
    Settings,
    ChevronLeft,
    ChevronRight,
    Menu,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { useState } from "react";

const navigation = [
    { name: "總覽", href: "/dashboard", icon: LayoutDashboard },
    { name: "AI 投資顧問", href: "/dashboard/advisor", icon: Brain },
    { name: "回測實驗室", href: "/dashboard/backtest", icon: FlaskConical },
    { name: "水晶球模擬", href: "/dashboard/simulation", icon: Sparkles },
    { name: "市場總覽", href: "/dashboard/market", icon: PieChart },
];

function Sidebar({ collapsed, onToggle }: { collapsed: boolean; onToggle: () => void }) {
    const pathname = usePathname();

    return (
        <aside
            className={cn(
                "fixed left-0 top-0 h-screen bg-sidebar border-r border-sidebar-border transition-all duration-300 z-40",
                collapsed ? "w-16" : "w-64"
            )}
        >
            <div className="flex flex-col h-full">
                {/* Logo */}
                <div className="flex items-center gap-3 p-4 border-b border-sidebar-border">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-chart-3 flex items-center justify-center flex-shrink-0">
                        <TrendingUp className="w-6 h-6 text-primary-foreground" />
                    </div>
                    {!collapsed && (
                        <span className="text-lg font-bold text-sidebar-foreground">SmartWealth</span>
                    )}
                </div>

                {/* Navigation */}
                <nav className="flex-1 p-3 space-y-1">
                    {navigation.map((item) => {
                        const isActive = pathname === item.href;
                        return (
                            <Link
                                key={item.name}
                                href={item.href}
                                className={cn(
                                    "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all",
                                    isActive
                                        ? "bg-sidebar-primary text-sidebar-primary-foreground"
                                        : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                                )}
                            >
                                <item.icon className={cn("w-5 h-5 flex-shrink-0", collapsed && "mx-auto")} />
                                {!collapsed && <span className="font-medium">{item.name}</span>}
                            </Link>
                        );
                    })}
                </nav>

                {/* Toggle Button */}
                <div className="p-3 border-t border-sidebar-border">
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={onToggle}
                        className="w-full justify-center"
                    >
                        {collapsed ? (
                            <ChevronRight className="w-4 h-4" />
                        ) : (
                            <ChevronLeft className="w-4 h-4" />
                        )}
                    </Button>
                </div>
            </div>
        </aside>
    );
}

function MobileNav() {
    const pathname = usePathname();

    return (
        <Sheet>
            <SheetTrigger asChild>
                <Button variant="ghost" size="icon" className="md:hidden">
                    <Menu className="w-5 h-5" />
                </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-64 p-0">
                <div className="flex flex-col h-full bg-sidebar">
                    <div className="flex items-center gap-3 p-4 border-b border-sidebar-border">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-chart-3 flex items-center justify-center">
                            <TrendingUp className="w-6 h-6 text-primary-foreground" />
                        </div>
                        <span className="text-lg font-bold">SmartWealth</span>
                    </div>
                    <nav className="flex-1 p-3 space-y-1">
                        {navigation.map((item) => {
                            const isActive = pathname === item.href;
                            return (
                                <Link
                                    key={item.name}
                                    href={item.href}
                                    className={cn(
                                        "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all",
                                        isActive
                                            ? "bg-sidebar-primary text-sidebar-primary-foreground"
                                            : "text-sidebar-foreground hover:bg-sidebar-accent"
                                    )}
                                >
                                    <item.icon className="w-5 h-5" />
                                    <span className="font-medium">{item.name}</span>
                                </Link>
                            );
                        })}
                    </nav>
                </div>
            </SheetContent>
        </Sheet>
    );
}

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const [collapsed, setCollapsed] = useState(false);

    return (
        <div className="min-h-screen bg-background">
            {/* Desktop Sidebar */}
            <div className="hidden md:block">
                <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />
            </div>

            {/* Main Content */}
            <div
                className={cn(
                    "transition-all duration-300",
                    collapsed ? "md:ml-16" : "md:ml-64"
                )}
            >
                {/* Top Bar */}
                <header className="sticky top-0 z-30 h-14 border-b border-border bg-background/95 backdrop-blur flex items-center px-4 gap-4">
                    <MobileNav />
                    <div className="flex-1" />
                    <Link href="/">
                        <Button variant="ghost" size="sm">
                            返回首頁
                        </Button>
                    </Link>
                </header>

                {/* Page Content */}
                <main className="p-4 md:p-6 lg:p-8">{children}</main>
            </div>
        </div>
    );
}
