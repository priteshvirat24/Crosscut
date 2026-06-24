"use client";

import { useState } from "react";

interface SettingsForm {
  gitlab_url: string;
  orbit_mode: string;
  llm_provider: string;
  severity_threshold: string;
  auto_create_issues: boolean;
  notify_owners: boolean;
  max_dependency_depth: number;
  confidence_threshold: number;
}

const defaultSettings: SettingsForm = {
  gitlab_url: "https://gitlab.com",
  orbit_mode: "mock",
  llm_provider: "openai",
  severity_threshold: "medium",
  auto_create_issues: true,
  notify_owners: true,
  max_dependency_depth: 5,
  confidence_threshold: 0.7,
};

function SettingSection({ title, description, children }: {
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <div className="card" style={{ marginBottom: "var(--space-lg)" }}>
      <div style={{ marginBottom: "var(--space-lg)" }}>
        <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: 4 }}>{title}</h3>
        <p style={{ fontSize: "0.85rem", color: "var(--text-tertiary)" }}>{description}</p>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-lg)" }}>
        {children}
      </div>
    </div>
  );
}

function FormField({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, color: "var(--text-secondary)", marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.04em" }}>
        {label}
      </label>
      {children}
    </div>
  );
}

const inputStyle: React.CSSProperties = {
  width: "100%",
  padding: "10px 14px",
  background: "var(--bg-primary)",
  border: "1px solid var(--surface-border)",
  borderRadius: "var(--radius-md)",
  color: "var(--text-primary)",
  fontFamily: "var(--font-sans)",
  fontSize: "0.85rem",
  outline: "none",
  transition: "border-color var(--transition-fast)",
};

const selectStyle: React.CSSProperties = {
  ...inputStyle,
  cursor: "pointer",
  appearance: "none" as const,
  backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%236b6f80' d='M6 8L1 3h10z'/%3E%3C/svg%3E")`,
  backgroundRepeat: "no-repeat",
  backgroundPosition: "right 12px center",
  paddingRight: "32px",
};

export default function SettingsPage() {
  const [settings, setSettings] = useState<SettingsForm>(defaultSettings);
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="animate-fade-in">
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h1 className="page-header__title">
            <span className="page-header__gradient">Settings</span>
          </h1>
          <p className="page-header__subtitle">
            Configure Orbit Sentinel connections, providers, and behavior.
          </p>
        </div>
        <button className="btn btn--primary" onClick={handleSave} id="btn-save-settings">
          {saved ? "✅ Saved!" : "💾 Save Settings"}
        </button>
      </div>

      <div style={{ maxWidth: 700 }}>
        <SettingSection title="GitLab Connection" description="Configure your GitLab instance and authentication.">
          <FormField label="GitLab URL">
            <input
              style={inputStyle}
              value={settings.gitlab_url}
              onChange={(e) => setSettings({ ...settings, gitlab_url: e.target.value })}
              placeholder="https://gitlab.com"
              id="input-gitlab-url"
            />
          </FormField>
          <FormField label="GitLab Token">
            <input
              style={inputStyle}
              type="password"
              placeholder="glpat-xxxxxxxxxxxxxxxxxxxx"
              id="input-gitlab-token"
            />
          </FormField>
        </SettingSection>

        <SettingSection title="GitLab Orbit" description="Configure the Orbit knowledge graph connection.">
          <FormField label="Orbit Mode">
            <select
              style={selectStyle}
              value={settings.orbit_mode}
              onChange={(e) => setSettings({ ...settings, orbit_mode: e.target.value })}
              id="select-orbit-mode"
            >
              <option value="mock">Mock (Demo Data)</option>
              <option value="api">API (Orbit Remote)</option>
              <option value="cli">CLI (Orbit Local)</option>
            </select>
          </FormField>
        </SettingSection>

        <SettingSection title="LLM Provider" description="Select the AI model for analysis intelligence.">
          <FormField label="Provider">
            <select
              style={selectStyle}
              value={settings.llm_provider}
              onChange={(e) => setSettings({ ...settings, llm_provider: e.target.value })}
              id="select-llm-provider"
            >
              <option value="openai">OpenAI (GPT-4.1)</option>
              <option value="anthropic">Anthropic (Claude)</option>
              <option value="google">Google (Gemini)</option>
            </select>
          </FormField>
        </SettingSection>

        <SettingSection title="Analysis Behavior" description="Control how analyses are triggered and reported.">
          <FormField label="Severity Threshold">
            <select
              style={selectStyle}
              value={settings.severity_threshold}
              onChange={(e) => setSettings({ ...settings, severity_threshold: e.target.value })}
              id="select-severity-threshold"
            >
              <option value="low">Low (report everything)</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical only</option>
            </select>
          </FormField>

          <FormField label="Max Dependency Depth">
            <input
              style={inputStyle}
              type="number"
              min={1}
              max={10}
              value={settings.max_dependency_depth}
              onChange={(e) => setSettings({ ...settings, max_dependency_depth: Number(e.target.value) })}
              id="input-max-depth"
            />
          </FormField>

          <FormField label="Confidence Threshold">
            <input
              style={inputStyle}
              type="number"
              min={0}
              max={1}
              step={0.05}
              value={settings.confidence_threshold}
              onChange={(e) => setSettings({ ...settings, confidence_threshold: Number(e.target.value) })}
              id="input-confidence-threshold"
            />
          </FormField>

          <div style={{ display: "flex", gap: "var(--space-xl)" }}>
            <label style={{ display: "flex", alignItems: "center", gap: 8, cursor: "pointer", fontSize: "0.85rem" }}>
              <input
                type="checkbox"
                checked={settings.auto_create_issues}
                onChange={(e) => setSettings({ ...settings, auto_create_issues: e.target.checked })}
                id="check-auto-issues"
                style={{ accentColor: "var(--accent-primary)" }}
              />
              Auto-create issues
            </label>

            <label style={{ display: "flex", alignItems: "center", gap: 8, cursor: "pointer", fontSize: "0.85rem" }}>
              <input
                type="checkbox"
                checked={settings.notify_owners}
                onChange={(e) => setSettings({ ...settings, notify_owners: e.target.checked })}
                id="check-notify-owners"
                style={{ accentColor: "var(--accent-primary)" }}
              />
              Notify repo owners
            </label>
          </div>
        </SettingSection>
      </div>
    </div>
  );
}
