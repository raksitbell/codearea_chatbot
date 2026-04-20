import { useEffect, useState, type ReactNode } from 'react'
import {
  Cpu,
  Activity,
  Check,
  AlertCircle,
  RefreshCw,
  ArrowLeft,
  Globe,
  Database,
  Rocket
} from 'lucide-react'
import {
  getOllamaConfig,
  updateOllamaConfig,
  getAvailableModels,
  getHealthCheck,
  testConnection,
  type OllamaConfig,
  type HealthStatus,
  type TestConnectionResult
} from './api'

// --- Shared Components matching Dashboard Style ---

interface ConfigCardProps {
  title: string;
  subtitle: string;
  icon: ReactNode;
  accentColor: string;
  children: ReactNode;
  footerRight: ReactNode;
  footerLeft?: ReactNode;
}

function ConfigCard({ title, subtitle, icon, accentColor, children, footerLeft, footerRight }: ConfigCardProps) {
  return (
    <section className="glass-card group relative">
      {/* Decorative Glow */}
      <div className={`absolute -right-20 -top-20 h-64 w-64 rounded-full bg-${accentColor}-500/5 blur-[100px] transition-opacity group-hover:opacity-100`} />

      {/* Header */}
      <div className="border-b border-white/5 bg-white/[0.01] px-8 py-7">
        <div className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/5 border border-white/5 shadow-inner transition-all duration-500 group-hover:scale-110">
            {icon}
          </div>
          <div>
            <h2 className="text-[13px] font-black uppercase tracking-[0.2em] text-white/90">{title}</h2>
            <p className="mt-1 text-[11px] font-medium tracking-wide text-white/40">{subtitle}</p>
          </div>
        </div>
      </div>

      {/* Body */}
      <div className="p-8 space-y-6">
        {children}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between border-t border-white/5 bg-white/[0.01] px-8 py-6">
        <div className="flex gap-3">{footerLeft}</div>
        <div>{footerRight}</div>
      </div>
    </section>
  )
}

function App() {
  const [config, setConfig] = useState<OllamaConfig>({ url: '', model: '' })
  const [models, setModels] = useState<string[]>([])
  const [health, setHealth] = useState<HealthStatus | null>(null)

  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState<TestConnectionResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    load()
  }, [])

  const load = async () => {
    setLoading(true)
    try {
      const [confRes, healthRes] = await Promise.all([getOllamaConfig(), getHealthCheck()])
      setConfig(confRes.data)
      setHealth(healthRes.data)

      // Fetch models for existing config
      const modelRes = await getAvailableModels()
      setModels(modelRes.data.models)
    } catch (err) {
      setError("Unable to reach AI Tutor Service.")
    } finally {
      setLoading(false)
    }
  }

  const handleTest = async () => {
    setTesting(true)
    setTestResult(null)
    try {
      const res = await testConnection(config)
      setTestResult(res.data)
      if (res.data.connected && res.data.models) {
        setModels(res.data.models)
      }
    } catch (err: any) {
      setTestResult({ connected: false, message: "Testing failed." })
    } finally {
      setTesting(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      await updateOllamaConfig(config)
      await load() // Refresh
    } catch (err) {
      setError("Failed to save configuration.")
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#05070f] flex items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#05070f] text-white selection:bg-indigo-500/30">
      {/* Background Orbs */}
      <div className="pointer-events-none fixed inset-0 opacity-70">
        <div className="absolute -left-36 top-[-120px] h-[380px] w-[380px] rounded-full bg-violet-700/10 blur-3xl" />
        <div className="absolute right-[-120px] top-1/4 h-[360px] w-[360px] rounded-full bg-blue-600/10 blur-3xl" />
      </div>

      {/* Header */}
      <header className="relative z-50 border-b border-white/5 bg-[#05070f]/80 backdrop-blur-3xl sticky top-0">
        <div className="mx-auto flex h-20 max-w-5xl items-center justify-between px-8">
          <div className="flex items-center gap-4">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-indigo-600/20 border border-indigo-500/20 shadow-[0_0_20px_rgba(99,102,241,0.1)]">
              <Rocket className="h-5 w-5 text-indigo-400" />
            </div>
            <div>
              <h1 className="text-[13px] font-black uppercase tracking-[0.2em] text-white/90">CodeArea AI Tutor</h1>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <a href="/docs" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/5 text-[10px] font-bold uppercase tracking-wider text-white/60 hover:bg-white/10 hover:text-white transition-all">
              <Globe className="h-3 w-3" />
              API Docs
            </a>
            <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/5 text-[10px] font-bold uppercase tracking-wider text-white/40">
              <Activity className="h-3 w-3" />
              API: {health?.status === 'ok' ? 'ออนไลน์' : 'ออฟไลน์'}
            </div>
          </div>
        </div>
      </header>

      <main className="relative z-10 mx-auto max-w-5xl px-8 py-12 flex flex-col gap-10">

        {error && (
          <div className="glass-card border-rose-500/20 bg-rose-500/5 p-6 flex items-center gap-4 animate-in fade-in slide-in-from-top-4 duration-500">
            <AlertCircle className="h-6 w-6 text-rose-500" />
            <p className="text-sm font-medium text-rose-200">{error}</p>
          </div>
        )}

        <ConfigCard
          title="การกำหนดค่าการเชื่อมต่อ Ollama"
          subtitle="กำหนด URL สำหรับ Ollama Instance"
          icon={<Cpu className="h-6 w-6 text-indigo-400" />}
          accentColor="indigo"
          footerLeft={
            <button
              onClick={handleTest}
              disabled={testing || !config.url}
              className="h-11 px-5 rounded-2xl bg-white/5 border border-white/5 text-xs font-bold text-white/80 hover:bg-white/10 transition-all flex items-center gap-2 active:scale-95 disabled:opacity-50"
            >
              {testing ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Globe className="h-4 w-4" />}
              ทดสอบการเชื่อมต่อ
            </button>
          }
          footerRight={
            <button
              onClick={handleSave}
              disabled={saving || !config.url || !config.model}
              className="h-11 px-8 rounded-2xl bg-indigo-600 shadow-[0_4px_20px_rgba(99,102,241,0.3)] text-xs font-black uppercase tracking-widest text-white hover:bg-indigo-500 hover:scale-[1.02] transition-all flex items-center gap-2 active:scale-95 disabled:opacity-50"
            >
              {saving ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Check className="h-4 w-4" />}
              บันทึกการกำหนดค่า
            </button>
          }
        >
          {/* Input Fields */}
          <div className="grid gap-8 sm:grid-cols-2">
            <div className="space-y-3">
              <label className="text-[10px] font-black uppercase tracking-widest text-white/30 ml-1">Ollama API URL</label>
              <input
                type="text"
                value={config.url}
                onChange={(e) => setConfig({ ...config, url: e.target.value })}
                placeholder="http://localhost:11434"
                className="premium-input"
              />
            </div>

            <div className="space-y-4">
              <label className="text-[10px] font-black uppercase tracking-widest text-white/30 ml-1">โมเดลที่พร้อมใช้งาน</label>
              {models.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {models.map(m => (
                    <button
                      key={m}
                      onClick={() => setConfig({ ...config, model: m })}
                      className={`px-4 py-3.5 rounded-2xl text-[11px] font-black uppercase tracking-widest transition-all border flex items-center gap-3 relative overflow-hidden group ${config.model === m
                        ? 'bg-indigo-500/10 border-indigo-500/50 text-indigo-400 shadow-[0_0_20px_rgba(99,102,241,0.1)]'
                        : 'bg-white/[0.02] border-white/5 text-white/20 hover:bg-white/[0.05] hover:border-white/10 hover:text-white/60'
                        }`}
                    >
                      <div className={`h-1.5 w-1.5 rounded-full ${config.model === m ? 'bg-indigo-400 animate-pulse' : 'bg-white/10 group-hover:bg-white/30'}`} />
                      <span className="truncate">{m}</span>
                      <Database className={`h-3.5 w-3.5 ml-auto opacity-20 ${config.model === m ? 'opacity-40' : ''}`} />
                    </button>
                  ))}
                </div>
              ) : (
                <div className="rounded-[2rem] border border-dashed border-white/5 bg-white/[0.01] p-10 text-center flex flex-col items-center gap-3">
                  <Database className="h-8 w-8 text-white/5" />
                  <p className="text-[10px] font-bold uppercase tracking-widest text-white/20">ไม่พบโมเดล</p>
                  <p className="text-[9px] font-medium text-white/10 max-w-[200px]">กด "ทดสอบการเชื่อมต่อ" เพื่อแสดงโมเดลที่พร้อมใช้งาน</p>
                </div>
              )}
            </div>
          </div>

          {/* Test Status Alert */}
          {testResult && (
            <div className={`p-4 rounded-2xl border transition-all animate-in zoom-in-95 duration-300 ${testResult.connected ? 'bg-emerald-500/5 border-emerald-500/20 text-emerald-400' : 'bg-rose-500/5 border-rose-500/20 text-rose-400'}`}>
              <div className="flex items-center gap-3">
                {testResult.connected ? <Check className="h-4 w-4" /> : <AlertCircle className="h-4 w-4" />}
                <p className="text-xs font-bold uppercase tracking-wider">{testResult.message}</p>
              </div>
              {testResult.connected && (
                <p className="mt-2 text-[10px] font-medium opacity-60">พบโมเดล {testResult.models_count}</p>
              )}
            </div>
          )}
        </ConfigCard>

        {/* Footer */}
        <div className="flex items-center justify-between opacity-30 mt-4">
          <p className="text-[10px] font-bold uppercase tracking-widest">CodeArea Ai Tutor Services</p>
          <a href="/" className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest hover:opacity-100 transition-opacity">
            <ArrowLeft className="h-3 w-3" />
            กลับไปยังแดชบอร์ด
          </a>
        </div>
      </main>
    </div>
  )
}

export default App
