"use client";

import { useState, useEffect, useCallback, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { OrbitReactor } from "@/components/3d/OrbitReactor";
import { Play, Pause, RotateCcw, ChevronDown, Check } from "lucide-react";
import Link from "next/link";

/* ─── SCENE DATA ─── */

const SCENES = [
  {
    id: 0,
    label: "Change Detected",
    subtitle: "AST Diff Engine",
    duration: 2500,
  },
  {
    id: 1,
    label: "Orbit Query Generated",
    subtitle: "DSL Translation",
    duration: 2500,
  },
  {
    id: 2,
    label: "Traversal Begins",
    subtitle: "Graph Execution",
    duration: 2000,
  },
  {
    id: 3,
    label: "Dependency Discovery",
    subtitle: "Impact Mapping",
    duration: 2500,
  },
  {
    id: 4,
    label: "Test Discovery",
    subtitle: "Ecosystem Reduction",
    duration: 3500,
  },
  {
    id: 5,
    label: "Explainability",
    subtitle: "Selection Reasoning",
    duration: 3000,
  },
  {
    id: 6,
    label: "Pipeline Execution",
    subtitle: "Targeted CI",
    duration: 2500,
  },
  {
    id: 7,
    label: "Results",
    subtitle: "Mission Complete",
    duration: 4000,
  },
];

const IMPACTED_TESTS = [
  { name: "test_checkout_flow.py", type: "Direct caller", depth: 1, status: "passed" },
  { name: "test_subscription_flow.py", type: "Transitive dependency", depth: 3, status: "passed" },
  { name: "test_refund_flow.py", type: "Shared payload", depth: 1, status: "passed" },
  { name: "test_risk_scoring.py", type: "Validation chain", depth: 2, status: "passed" },
  { name: "test_token_claims.py", type: "Region parameter", depth: 3, status: "passed" },
];

const PIPELINE_JOBS = [
  "test_checkout_flow.py",
  "test_subscription_flow.py",
  "test_refund_flow.py",
  "test_risk_scoring.py",
  "test_token_claims.py",
  "test_billing_validation.py",
];

/* ─── FLOATING PANELS ─── */

const panelMotion = {
  initial: { opacity: 0, y: 20, scale: 0.96 },
  animate: { opacity: 1, y: 0, scale: 1 },
  exit: { opacity: 0, y: -10, scale: 0.98 },
  transition: { duration: 0.6, ease: "easeOut" as const },
};

function SceneLabel({ scene }: { scene: number }) {
  const s = SCENES[scene];
  if (!s) return null;
  return (
    <motion.div
      key={scene}
      {...panelMotion}
      className="absolute top-8 left-1/2 -translate-x-1/2 z-30 text-center pointer-events-none"
    >
      <div className="text-[10px] font-bold uppercase tracking-[0.2em] text-[#C68A3A] mb-1">
        Scene {scene + 1} of {SCENES.length}
      </div>
      <div className="text-2xl font-bold text-[#1E1E1E] tracking-tight">{s.label}</div>
      <div className="text-xs text-[#8B8D86] mt-1">{s.subtitle}</div>
    </motion.div>
  );
}

function DiffPanel() {
  return (
    <motion.div
      {...panelMotion}
      className="absolute bottom-32 left-8 z-30 w-[340px]"
    >
      <div className="bg-white/90 backdrop-blur-lg border border-[#E5E5E2] rounded-xl shadow-lg overflow-hidden">
        <div className="px-5 py-3 border-b border-[#E5E5E2] bg-[#FAFAF8]">
          <div className="text-[10px] font-bold uppercase tracking-widest text-[#8B8D86]">
            Signature Change Detected
          </div>
        </div>
        <div className="p-5 font-mono text-xs leading-relaxed">
          <div className="text-[#8B8D86] mb-2">payment-library/validation.py</div>
          <div className="text-[#E5484D] line-through opacity-60">
            def validate_payment(amount, currency):
          </div>
          <div className="text-[#10b981] font-bold mt-1">
            def validate_payment(amount, currency, region):
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function OrbitQueryPanel() {
  return (
    <motion.div
      {...panelMotion}
      className="absolute bottom-32 right-8 z-30 w-[320px]"
    >
      <div className="bg-white/90 backdrop-blur-lg border border-[#E5E5E2] rounded-xl shadow-lg overflow-hidden">
        <div className="px-5 py-3 border-b border-[#E5E5E2] bg-[#FAFAF8]">
          <div className="text-[10px] font-bold uppercase tracking-widest text-[#8B8D86]">
            Orbit Cypher DSL
          </div>
        </div>
        <div className="p-5 font-mono text-[10px] leading-relaxed text-[#1E1E1E]">
          <div><span className="text-[#C68A3A]">MATCH</span> (f:Function &#123;name: &quot;validate_payment&quot;&#125;)</div>
          <div>&lt;-[r:<span className="text-[#E5484D]">CALLS</span>*1..5]-(caller:Function)</div>
          <div><span className="text-[#C68A3A]">WITH</span> f, caller, r</div>
          <div><span className="text-[#C68A3A]">MATCH</span> (caller)-[:DEFINED_IN]-&gt;(file:File)</div>
          <div>&lt;-[:CONTAINS]-(repo:Repository)</div>
          <div><span className="text-[#C68A3A]">RETURN</span> repo.name, caller.name, length(r) as depth</div>
        </div>
      </div>
    </motion.div>
  );
}

function TraversalPanel() {
  return (
    <motion.div
      {...panelMotion}
      className="absolute top-24 right-8 z-30 w-[240px]"
    >
      <div className="bg-white/90 backdrop-blur-lg border border-[#E5E5E2] rounded-xl shadow-lg overflow-hidden">
        <div className="px-5 py-3 border-b border-[#E5E5E2] bg-[#FAFAF8]">
          <div className="text-[10px] font-bold uppercase tracking-widest text-[#8B8D86]">
            Orbit Traversal
          </div>
        </div>
        <div className="p-5 space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-[10px] font-bold uppercase tracking-widest text-[#8B8D86]">Depth</span>
            <span className="text-lg font-bold text-[#1E1E1E]">4</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-[10px] font-bold uppercase tracking-widest text-[#8B8D86]">Repositories</span>
            <span className="text-lg font-bold text-[#C68A3A]">6</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-[10px] font-bold uppercase tracking-widest text-[#8B8D86]">Functions</span>
            <span className="text-lg font-bold text-[#1E1E1E]">23</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function ReductionCounter({ scene }: { scene: number }) {
  return (
    <motion.div
      {...panelMotion}
      className="absolute bottom-32 left-1/2 -translate-x-1/2 z-30"
    >
      <div className="bg-white/90 backdrop-blur-lg border border-[#E5E5E2] rounded-xl shadow-lg px-12 py-8 text-center">
        <div className="flex items-center gap-8">
          <div>
            <div className="text-5xl font-bold text-[#8B8D86] tracking-tight">418</div>
            <div className="text-[10px] font-bold uppercase tracking-widest text-[#8B8D86] mt-1">Ecosystem</div>
          </div>
          <div className="text-3xl text-[#C68A3A]">
            <ChevronDown size={32} />
          </div>
          <div>
            <div className="text-5xl font-bold text-[#E5484D] tracking-tight">12</div>
            <div className="text-[10px] font-bold uppercase tracking-widest text-[#E5484D] mt-1">Impacted</div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function ExplainabilityCards() {
  return (
    <motion.div
      {...panelMotion}
      className="absolute bottom-32 right-8 z-30 w-[280px] space-y-2"
    >
      {IMPACTED_TESTS.slice(0, 3).map((test, i) => (
        <motion.div
          key={test.name}
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: i * 0.3, duration: 0.5, ease: "easeOut" as const }}
          className="bg-white/90 backdrop-blur-lg border border-[#E5E5E2] rounded-lg shadow-md px-4 py-3"
        >
          <div className="text-xs font-semibold text-[#1E1E1E] truncate">{test.name}</div>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-[9px] font-bold uppercase tracking-widest text-[#8B8D86]">{test.type}</span>
            <span className="px-1.5 py-0.5 bg-[#F4F4F1] text-[#C68A3A] text-[9px] font-bold rounded">
              L{test.depth}
            </span>
          </div>
        </motion.div>
      ))}
    </motion.div>
  );
}

function PipelinePanel() {
  return (
    <motion.div
      {...panelMotion}
      className="absolute bottom-32 left-8 z-30 w-[300px]"
    >
      <div className="bg-white/90 backdrop-blur-lg border border-[#E5E5E2] rounded-xl shadow-lg overflow-hidden">
        <div className="px-5 py-3 border-b border-[#E5E5E2] bg-[#FAFAF8] flex items-center justify-between">
          <div className="text-[10px] font-bold uppercase tracking-widest text-[#8B8D86]">
            Pipeline Execution
          </div>
          <div className="text-[10px] font-bold uppercase tracking-widest text-[#10b981]">12 Jobs</div>
        </div>
        <div className="p-4 space-y-2">
          {PIPELINE_JOBS.map((job, i) => (
            <motion.div
              key={job}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.15, duration: 0.3 }}
              className="flex items-center gap-3"
            >
              <div className="w-4 h-4 rounded-full bg-[#10b981] flex items-center justify-center">
                <Check size={10} className="text-white" />
              </div>
              <span className="text-xs font-mono text-[#1E1E1E]">{job}</span>
            </motion.div>
          ))}
          <div className="text-[10px] text-[#8B8D86] font-bold pt-2 border-t border-[#E5E5E2]">
            + 6 additional tests passed
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function ResultsPanel() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 40, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 40, scale: 0.9 }}
      transition={{ duration: 0.8, ease: "easeOut" as const }}
      className="absolute bottom-24 left-1/2 -translate-x-1/2 z-30 w-full max-w-3xl px-4"
    >
      <div className="bg-white/95 backdrop-blur-xl border border-[#E5E5E2] rounded-2xl shadow-2xl overflow-hidden">
        <div className="grid grid-cols-5 divide-x divide-[#E5E5E2]">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="p-6 text-center"
          >
            <div className="text-3xl font-bold text-[#8B8D86] tracking-tight">418</div>
            <div className="text-[9px] font-bold uppercase tracking-widest text-[#8B8D86] mt-1">Tests</div>
          </motion.div>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="p-6 text-center"
          >
            <div className="text-3xl font-bold text-[#E5484D] tracking-tight">12</div>
            <div className="text-[9px] font-bold uppercase tracking-widest text-[#E5484D] mt-1">Targeted</div>
          </motion.div>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.9 }}
            className="p-6 text-center"
          >
            <div className="text-3xl font-bold text-[#1E1E1E] tracking-tight">97%</div>
            <div className="text-[9px] font-bold uppercase tracking-widest text-[#C68A3A] mt-1">Reduction</div>
          </motion.div>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.2 }}
            className="p-6 text-center"
          >
            <div className="text-3xl font-bold text-[#1E1E1E] tracking-tight">2m</div>
            <div className="text-[9px] font-bold uppercase tracking-widest text-[#8B8D86] mt-1">vs 38m</div>
          </motion.div>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.5 }}
            className="p-6 text-center"
          >
            <div className="text-lg font-bold text-[#10b981] tracking-tight">✓</div>
            <div className="text-[9px] font-bold uppercase tracking-widest text-[#10b981] mt-1">All Passed</div>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}

/* ─── PROGRESS BAR ─── */

function ProgressBar({ scene, progress }: { scene: number; progress: number }) {
  return (
    <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-40 flex items-center gap-1.5">
      {SCENES.map((s, i) => (
        <div key={i} className="flex items-center gap-1.5">
          <div
            className={`h-1 rounded-full transition-all duration-500 ${
              i < scene
                ? "w-6 bg-[#1E1E1E]"
                : i === scene
                ? "w-10 bg-[#C68A3A]"
                : "w-4 bg-[#E5E5E2]"
            }`}
          >
            {i === scene && (
              <motion.div
                className="h-full rounded-full bg-[#1E1E1E]"
                initial={{ width: "0%" }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.3, ease: "linear" }}
              />
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

/* ─── MAIN EXPERIENCE ─── */

function RunModeContent() {
  const searchParams = useSearchParams();
  const autoPlay = searchParams.get("autoplay") === "true";

  const [judgeMode, setJudgeMode] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [scene, setScene] = useState(-1);
  const [progress, setProgress] = useState(0);

  // Auto-start if linked from landing
  useEffect(() => {
    if (autoPlay) {
      const t = setTimeout(() => {
        setJudgeMode(true);
        setPlaying(true);
        setScene(0);
      }, 500);
      return () => clearTimeout(t);
    }
  }, [autoPlay]);

  // Scene progression
  useEffect(() => {
    if (!playing || scene < 0) return;

    const sceneDuration = SCENES[scene]?.duration || 4000;
    const tick = 50;
    let elapsed = 0;

    const interval = setInterval(() => {
      elapsed += tick;
      setProgress(Math.min((elapsed / sceneDuration) * 100, 100));

      if (elapsed >= sceneDuration) {
        clearInterval(interval);
        if (scene < SCENES.length - 1) {
          setScene(prev => prev + 1);
          setProgress(0);
        } else {
          // Loop
          setTimeout(() => {
            setScene(0);
            setProgress(0);
          }, 2000);
        }
      }
    }, tick);

    return () => clearInterval(interval);
  }, [scene, playing]);

  const handleStart = useCallback(() => {
    setJudgeMode(true);
    // 1 second pause before starting
    setTimeout(() => {
      setPlaying(true);
      setScene(0);
    }, 1000);
  }, []);

  const handlePause = useCallback(() => {
    setPlaying(prev => !prev);
  }, []);

  const handleReplay = useCallback(() => {
    setScene(0);
    setProgress(0);
    setPlaying(true);
  }, []);

  return (
    <div className="fixed inset-0 bg-[#FAFAF8] text-[#1E1E1E] flex flex-col z-[100] overflow-hidden font-sans">

      {/* ─── PRE-JUDGE MODE: Ambient graph with header ─── */}
      <AnimatePresence>
        {!judgeMode && (
          <motion.header
            exit={{ opacity: 0, y: -40 }}
            transition={{ duration: 0.6 }}
            className="absolute top-0 left-0 right-0 px-8 py-4 flex justify-between items-center z-30 bg-white/80 backdrop-blur-md border-b border-[#E5E5E2]"
          >
            <Link href="/" className="flex items-center gap-4 group cursor-pointer">
              <div className="w-8 h-8 bg-[#1E1E1E] flex items-center justify-center rounded">
                <span className="text-white font-bold">C</span>
              </div>
              <span className="font-semibold text-sm tracking-tight group-hover:text-[#E5484D] transition-colors">Crosscut</span>
            </Link>
            <button
              onClick={handleStart}
              className="button-vermilion text-xs px-6 h-9 flex items-center gap-2 cursor-pointer"
            >
              <Play size={12} fill="currentColor" />
              Run Judge Mode
            </button>
          </motion.header>
        )}
      </AnimatePresence>

      {/* ─── GRAPH: Always present, fills entire screen ─── */}
      <div className="absolute inset-0 z-0">
        <OrbitReactor currentStage={scene} />
      </div>

      {/* ─── JUDGE MODE UI LAYER ─── */}
      <AnimatePresence mode="wait">
        {judgeMode && (
          <>
            {/* Scene Label — top center */}
            <AnimatePresence mode="wait">
              <SceneLabel key={`label-${scene}`} scene={scene} />
            </AnimatePresence>

            {/* Scene 0: Diff Panel */}
            <AnimatePresence>
              {scene === 0 && <DiffPanel key="diff" />}
            </AnimatePresence>

            {/* Scene 1: Orbit Query */}
            <AnimatePresence>
              {scene === 1 && <OrbitQueryPanel key="orbit-query" />}
            </AnimatePresence>

            {/* Scene 2: Traversal Stats */}
            <AnimatePresence>
              {scene === 2 && <TraversalPanel key="traversal" />}
            </AnimatePresence>

            {/* Scene 3: Discovery — graph expanding, just label */}

            {/* Scene 4: Test Discovery — Reduction Counter */}
            <AnimatePresence>
              {scene === 4 && <ReductionCounter key="reduction" scene={scene} />}
            </AnimatePresence>

            {/* Scene 5: Explainability Cards */}
            <AnimatePresence>
              {scene === 5 && <ExplainabilityCards key="explain" />}
            </AnimatePresence>

            {/* Scene 6: Pipeline Execution */}
            <AnimatePresence>
              {scene === 6 && <PipelinePanel key="pipeline" />}
            </AnimatePresence>

            {/* Scene 7: Results */}
            <AnimatePresence>
              {scene === 7 && <ResultsPanel key="results" />}
            </AnimatePresence>

            {/* Progress Bar */}
            <ProgressBar scene={scene} progress={progress} />

            {/* Controls — bottom right */}
            <div className="absolute bottom-5 right-8 z-40 flex items-center gap-2">
              <button
                onClick={handlePause}
                className="w-8 h-8 bg-white/80 backdrop-blur-md border border-[#E5E5E2] rounded-full flex items-center justify-center hover:bg-white transition-colors cursor-pointer"
              >
                {playing ? <Pause size={12} /> : <Play size={12} fill="#1E1E1E" />}
              </button>
              <button
                onClick={handleReplay}
                className="w-8 h-8 bg-white/80 backdrop-blur-md border border-[#E5E5E2] rounded-full flex items-center justify-center hover:bg-white transition-colors cursor-pointer"
              >
                <RotateCcw size={12} />
              </button>
            </div>

            {/* Crosscut Badge — top left */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="absolute top-6 left-8 z-30"
            >
              <Link href="/" className="flex items-center gap-3 group cursor-pointer">
                <div className="w-6 h-6 bg-[#1E1E1E] flex items-center justify-center rounded">
                  <span className="text-white text-xs font-bold">C</span>
                </div>
                <span className="text-xs font-semibold text-[#8B8D86] group-hover:text-[#1E1E1E] transition-colors">Crosscut</span>
              </Link>
            </motion.div>

            {/* Orbit Engine Label — top right */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="absolute top-6 right-8 z-30 flex items-center gap-2"
            >
              <span className={`w-2 h-2 rounded-full ${playing ? 'bg-[#10b981] animate-pulse' : 'bg-[#8B8D86]'}`} />
              <span className="text-[10px] font-bold uppercase tracking-widest text-[#8B8D86]">
                Orbit Dependency Engine
              </span>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* ─── PRE-JUDGE MODE: Center prompt ─── */}
      <AnimatePresence>
        {!judgeMode && (
          <motion.div
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.4 }}
            className="absolute inset-0 z-20 flex items-center justify-center pointer-events-none"
          >
            <div className="text-center pointer-events-auto">
              <div className="text-[10px] font-bold uppercase tracking-[0.2em] text-[#8B8D86] mb-4">
                Orbit Dependency Engine
              </div>
              <h1 className="text-4xl font-bold text-[#1E1E1E] tracking-tight mb-3">
                Crosscut
              </h1>
              <p className="text-sm text-[#8B8D86] mb-8 max-w-md">
                Watch the automated GitLab Duo Agent Platform Flow traverse the Orbit Knowledge Graph and generate a targeted CI pipeline.
              </p>
              <button
                onClick={handleStart}
                className="button-vermilion text-sm px-8 py-3 flex items-center gap-3 cursor-pointer mx-auto"
              >
                <Play size={14} fill="currentColor" />
                Run Judge Mode
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function RunModePage() {
  return (
    <Suspense fallback={<div className="fixed inset-0 bg-[#FAFAF8]" />}>
      <RunModeContent />
    </Suspense>
  );
}
