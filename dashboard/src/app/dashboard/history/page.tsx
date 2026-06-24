"use client";

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
} from "recharts";

const trendData = [
  { date: "Jan", analyses: 12, accuracy: 82, avg_risk: 45 },
  { date: "Feb", analyses: 18, accuracy: 84, avg_risk: 52 },
  { date: "Mar", analyses: 24, accuracy: 86, avg_risk: 48 },
  { date: "Apr", analyses: 15, accuracy: 85, avg_risk: 55 },
  { date: "May", analyses: 31, accuracy: 88, avg_risk: 60 },
  { date: "Jun", analyses: 42, accuracy: 87, avg_risk: 58 },
];

const predictionHistory = [
  { id: "p1", project: "payment-library", mr: "!342", predicted_risk: 78, actual: "Correct", outcome: "3 pipeline failures prevented", date: "2 hours ago" },
  { id: "p2", project: "api-gateway", mr: "!89", predicted_risk: 45, actual: "Correct", outcome: "Configuration updated pre-merge", date: "5 hours ago" },
  { id: "p3", project: "notification-service", mr: "!201", predicted_risk: 22, actual: "Correct", outcome: "No issues post-merge", date: "1 day ago" },
  { id: "p4", project: "auth-service", mr: "!134", predicted_risk: 65, actual: "Over-estimated", outcome: "Only 2 of 8 predicted repos affected", date: "2 days ago" },
  { id: "p5", project: "user-service", mr: "!78", predicted_risk: 30, actual: "Under-estimated", outcome: "5 downstream failures occurred", date: "3 days ago" },
  { id: "p6", project: "search-service", mr: "!445", predicted_risk: 55, actual: "Correct", outcome: "Migration completed pre-merge", date: "4 days ago" },
];

const accuracyColor = (actual: string) => {
  if (actual === "Correct") return "var(--severity-low)";
  if (actual === "Over-estimated") return "var(--severity-medium)";
  return "var(--severity-high)";
};

export default function HistoryPage() {
  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1 className="page-header__title">
          <span className="page-header__gradient">Historical Predictions</span>
        </h1>
        <p className="page-header__subtitle">
          Track prediction accuracy and learn from past analyses.
        </p>
      </div>

      {/* Summary Stats */}
      <div className="stat-grid stagger-children" style={{ marginBottom: "var(--space-xl)" }}>
        <div className="card stat-card animate-fade-in">
          <div className="stat-card__icon stat-card__icon--green">🎯</div>
          <div className="card__title">Overall Accuracy</div>
          <div className="card__value" style={{ color: "var(--severity-low)" }}>87.5%</div>
        </div>
        <div className="card stat-card animate-fade-in">
          <div className="stat-card__icon stat-card__icon--purple">📊</div>
          <div className="card__title">Total Predictions</div>
          <div className="card__value">142</div>
        </div>
        <div className="card stat-card animate-fade-in">
          <div className="stat-card__icon stat-card__icon--cyan">✅</div>
          <div className="card__title">Correct Predictions</div>
          <div className="card__value">124</div>
        </div>
        <div className="card stat-card animate-fade-in">
          <div className="stat-card__icon stat-card__icon--pink">📈</div>
          <div className="card__title">Accuracy Trend</div>
          <div className="card__value" style={{ color: "var(--severity-low)" }}>+5.5%</div>
          <div className="card__subtitle">vs. last quarter</div>
        </div>
      </div>

      <div className="content-grid content-grid--2">
        {/* Trend Chart */}
        <div className="card" id="accuracy-trend-chart">
          <div className="card__header">
            <h3 className="card__title">Accuracy & Volume Trend</h3>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={trendData}>
              <defs>
                <linearGradient id="accuracyGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="rgba(255,255,255,0.04)" />
              <XAxis dataKey="date" tick={{ fill: "#6b6f80", fontSize: 12 }} />
              <YAxis tick={{ fill: "#6b6f80", fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  background: "#1a1b26",
                  border: "1px solid rgba(255,255,255,0.06)",
                  borderRadius: 10,
                  fontSize: 13,
                  color: "#e4e5f1",
                }}
              />
              <Area
                type="monotone"
                dataKey="accuracy"
                stroke="#22c55e"
                fill="url(#accuracyGrad)"
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Volume Chart */}
        <div className="card" id="volume-chart">
          <div className="card__header">
            <h3 className="card__title">Analysis Volume</h3>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={trendData}>
              <CartesianGrid stroke="rgba(255,255,255,0.04)" />
              <XAxis dataKey="date" tick={{ fill: "#6b6f80", fontSize: 12 }} />
              <YAxis tick={{ fill: "#6b6f80", fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  background: "#1a1b26",
                  border: "1px solid rgba(255,255,255,0.06)",
                  borderRadius: 10,
                  fontSize: 13,
                  color: "#e4e5f1",
                }}
              />
              <Bar dataKey="analyses" fill="#8b5cf6" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Prediction History Table */}
      <div className="card card--flat" style={{ marginTop: "var(--space-lg)" }} id="prediction-history-table">
        <div className="card__header">
          <h3 className="card__title">Recent Predictions</h3>
        </div>
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Project / MR</th>
                <th>Predicted Risk</th>
                <th>Accuracy</th>
                <th>Outcome</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              {predictionHistory.map((pred) => (
                <tr key={pred.id}>
                  <td>
                    <span style={{ fontWeight: 600, color: "var(--text-primary)" }}>{pred.project}</span>
                    <span style={{ color: "var(--text-tertiary)", marginLeft: 8, fontSize: "0.8rem" }}>{pred.mr}</span>
                  </td>
                  <td>
                    <span style={{ fontFamily: "var(--font-mono)", fontWeight: 600 }}>{pred.predicted_risk}/100</span>
                  </td>
                  <td>
                    <span style={{ fontWeight: 600, color: accuracyColor(pred.actual) }}>
                      {pred.actual === "Correct" ? "✅" : pred.actual === "Over-estimated" ? "⬆️" : "⬇️"} {pred.actual}
                    </span>
                  </td>
                  <td style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>{pred.outcome}</td>
                  <td style={{ whiteSpace: "nowrap", fontSize: "0.8rem", color: "var(--text-tertiary)" }}>{pred.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
