"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { auth } from "@/lib/api/auth";
import { PageTransition } from "@/components/ui/PageTransition";
import {
  CreditCard,
  Check,
  Zap,
  Crown,
  Sparkles,
  Calendar,
  ArrowRight,
} from "lucide-react";

const PLANS = [
  {
    name: "Free",
    price: "$0",
    period: "forever",
    description: "Perfect for getting started",
    features: [
      "Up to 50 tasks",
      "Basic task management",
      "AI Assistant (limited)",
      "Email support",
      "Mobile app access",
    ],
    current: true,
    color: "from-gray-500 to-gray-600",
    icon: Zap,
  },
  {
    name: "Pro",
    price: "$9",
    period: "per month",
    description: "For power users and teams",
    features: [
      "Unlimited tasks",
      "Advanced analytics",
      "AI Assistant (unlimited)",
      "Priority support",
      "Custom integrations",
      "Team collaboration",
      "Advanced automation",
    ],
    popular: true,
    color: "from-blue-500 to-purple-600",
    icon: Crown,
  },
  {
    name: "Enterprise",
    price: "$29",
    period: "per month",
    description: "For large organizations",
    features: [
      "Everything in Pro",
      "Dedicated account manager",
      "Custom AI training",
      "SSO & Advanced security",
      "SLA guarantee",
      "Custom contracts",
      "Unlimited team members",
    ],
    color: "from-purple-500 to-pink-600",
    icon: Sparkles,
  },
];

export default function BillingPage() {
  const router = useRouter();
  const [user, setUser] = useState<{ email: string } | null>(null);

  // Route protection
  useEffect(() => {
    const currentUser = auth.getUser();
    if (!currentUser) {
      router.push("/login");
      return;
    }
    setUser(currentUser);
  }, [router]);

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <PageTransition>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:via-slate-900 dark:to-gray-900">
        {/* Header */}
        <div className="relative bg-white/70 dark:bg-gray-800/70 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-700/50 shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center shadow-lg">
                <CreditCard className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                  Billing & Plans
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Manage your subscription and billing
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <main className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
          {/* Current Plan */}
          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-700/50 p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Current Plan
                </h2>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  You are currently on the Free plan
                </p>
              </div>
              <div className="px-4 py-2 bg-gradient-to-r from-gray-500 to-gray-600 text-white rounded-lg font-semibold">
                Free Plan
              </div>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
              <Calendar className="w-4 h-4" />
              <span>No billing cycle • Upgrade anytime</span>
            </div>
          </div>

          {/* Pricing Plans */}
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
              Choose Your Plan
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {PLANS.map((plan) => {
                const Icon = plan.icon;
                return (
                  <div
                    key={plan.name}
                    className={`relative bg-white/80 dark:bg-gray-800/80 backdrop-blur-md rounded-2xl shadow-xl border ${
                      plan.popular
                        ? "border-blue-500 dark:border-blue-400 ring-2 ring-blue-500/20"
                        : "border-gray-200/50 dark:border-gray-700/50"
                    } p-6 hover:shadow-2xl transition-all`}
                  >
                    {plan.popular && (
                      <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                        <span className="px-4 py-1 bg-gradient-to-r from-blue-500 to-purple-600 text-white text-sm font-semibold rounded-full shadow-lg">
                          Most Popular
                        </span>
                      </div>
                    )}

                    <div className="text-center mb-6">
                      <div
                        className={`w-16 h-16 bg-gradient-to-br ${plan.color} rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg`}
                      >
                        <Icon className="w-8 h-8 text-white" />
                      </div>
                      <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                        {plan.name}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                        {plan.description}
                      </p>
                      <div className="flex items-baseline justify-center gap-1">
                        <span className="text-4xl font-bold text-gray-900 dark:text-white">
                          {plan.price}
                        </span>
                        <span className="text-sm text-gray-600 dark:text-gray-400">
                          /{plan.period}
                        </span>
                      </div>
                    </div>

                    <ul className="space-y-3 mb-6">
                      {plan.features.map((feature, index) => (
                        <li key={index} className="flex items-start gap-3">
                          <Check className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                          <span className="text-sm text-gray-700 dark:text-gray-300">
                            {feature}
                          </span>
                        </li>
                      ))}
                    </ul>

                    <button
                      className={`w-full py-3 rounded-xl font-semibold transition-all flex items-center justify-center gap-2 ${
                        plan.current
                          ? "bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400 cursor-not-allowed"
                          : plan.popular
                          ? "bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white shadow-lg hover:shadow-xl"
                          : "bg-gradient-to-r from-gray-700 to-gray-800 hover:from-gray-800 hover:to-gray-900 text-white shadow-lg hover:shadow-xl"
                      }`}
                      disabled={plan.current}
                    >
                      {plan.current ? (
                        "Current Plan"
                      ) : (
                        <>
                          Upgrade Now
                          <ArrowRight className="w-4 h-4" />
                        </>
                      )}
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        </main>
      </div>
    </PageTransition>
  );
}
