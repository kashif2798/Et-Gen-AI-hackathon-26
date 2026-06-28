"use client";

import { useMemo, useRef, useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Zap,
  TrendingUp,
  TrendingDown,
  Shield,
  User,
  Loader2,
  ArrowLeft,
  ChevronRight,
  Sparkles,
  BookOpen,
  Brain,
  RefreshCw,
  Calendar,
  Video,
  Play,
  PlayCircle,
  FileVideo,
} from "lucide-react";

import type { AnalysisResponse, Article, Persona, UserProfile, VideoResponse } from "@/types";
import { Skeleton, ArticleSkeleton, AnalysisSkeleton, StoryboardSkeleton } from "@/components/ui/Skeleton";
import { analyzeNews, fetchArticles, ingestFallback, ingestLive, generateVideo, API_BASE } from "@/lib/api";
import { prefetchVideoJobAssets } from "@/lib/videoPrefetch";
import { Player } from "@remotion/player";
import { ChatWidget } from "../components/ChatWidget";
import { NewsVideo } from "./video-studio/compositions/NewsVideo";
import { StoryArcScreen } from "@/components/StoryArcScreen";

function escapeXml(s: string) {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

function stringToHsl(input: string) {
  // Deterministically turn a string into a pleasant HSL color.
  let hash = 0;
  for (let i = 0; i < input.length; i++) hash = input.charCodeAt(i) + ((hash << 5) - hash);
  const hue = Math.abs(hash) % 360;
  return { h: hue, s: 78, l: 46 };
}

function getFallbackThumbnailDataUrl(article: Article) {
  const title = article.title ?? "";
  const tag = article.tags?.[0] ?? "News";
  const { h } = stringToHsl(title + "|" + tag);

  const bg1 = `hsl(${h} 78% 48%)`;
  const bg2 = `hsl(${(h + 35) % 360} 78% 42%)`;

  // Shorten text to fit the thumbnail while keeping it readable.
  const label = (tag || "News").slice(0, 18);
  const headline = (title || "E-newspaper").replace(/\s+/g, " ").slice(0, 44).trim();

  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="800" height="400" viewBox="0 0 800 400">
      <defs>
        <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="${bg1}" />
          <stop offset="1" stop-color="${bg2}" />
        </linearGradient>
        <filter id="noise">
          <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="2" stitchTiles="stitch" />
          <feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .18 0"/>
        </filter>
      </defs>
      <rect width="800" height="400" fill="url(#g)" />
      <rect width="800" height="400" filter="url(#noise)" opacity="0.35" />
      <rect x="30" y="30" width="740" height="340" rx="22" fill="rgba(255,255,255,0.14)" stroke="rgba(255,255,255,0.22)" />

      <text x="56" y="106" font-family="ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial"
            font-size="18" font-weight="800" fill="rgba(255,255,255,0.92)">
        ${escapeXml(label.toUpperCase())}
      </text>
      <text x="56" y="170" font-family="ui-serif, Georgia, Cambria, Times New Roman, Times, serif"
            font-size="32" font-weight="800" fill="rgba(255,255,255,0.96)">
        ${escapeXml(headline)}
      </text>

      <text x="56" y="344" font-family="ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial"
            font-size="14" font-weight="700" fill="rgba(255,255,255,0.85)">
        E-newspaper
      </text>
    </svg>
  `;

  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
}

// ─── Demo Personas ─────────────────────────────────────────────

const DEMO_PERSONAS: Persona[] = [
  {
    user_id: "student_01",
    name: "Student",
    persona: "curious_student",
    level: "beginner",
    portfolio: [],
    interests: ["technology", "startups", "AI"],
  },
  {
    user_id: "investor_01",
    name: "Retail Investor",
    persona: "retail_investor",
    level: "intermediate",
    portfolio: ["TATAMOTORS", "HDFCBANK", "INFY"],
    interests: ["auto", "banking", "IT"],
  },
  {
    user_id: "fund_mgr_01",
    name: "Fund Manager",
    persona: "fund_manager",
    level: "expert",
    portfolio: ["RELIANCE", "TCS", "HDFCBANK", "TATAMOTORS", "ICICIBANK"],
    interests: ["markets", "macro", "policy"],
  },
  {
    user_id: "founder_01",
    name: "Startup Founder",
    persona: "startup_founder",
    level: "intermediate",
    portfolio: ["INFY", "WIPRO"],
    interests: ["AI", "SaaS", "funding"],
  },
];

const PERSONA_META: Record<string, { role: string; icon: string; desc: string }> = {
  curious_student: { role: "Student", icon: "🎓", desc: "Simplified explanations with learning context" },
  retail_investor: { role: "Retail Investor", icon: "📈", desc: "Portfolio impact analysis with actionable insights" },
  fund_manager: { role: "Fund Manager", icon: "🏦", desc: "Deep macro analysis with risk quantification" },
  startup_founder: { role: "Startup Founder", icon: "🚀", desc: "Tech trends and funding ecosystem perspective" },
};

type Screen = "welcome" | "persona" | "home" | "article" | "video_studio" | "story_arc";

// ─── Main Page ─────────────────────────────────────────────────

export default function Home() {
  const [screen, setScreen] = useState<Screen>("welcome");
  const [selectedPersona, setSelectedPersona] = useState<Persona | null>(null);
  const [articles, setArticles] = useState<Article[]>([]);
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [isLoadingArticles, setIsLoadingArticles] = useState(false);
  const [isLoadingAnalysis, setIsLoadingAnalysis] = useState(false);
  const [isIngesting, setIsIngesting] = useState(false);
  const [ingested, setIngested] = useState(false);
  const [videoJob, setVideoJob] = useState<VideoResponse | null>(null);
  const [isGeneratingVideo, setIsGeneratingVideo] = useState(false);
  const [videoError, setVideoError] = useState<string | null>(null);

  // Load articles when reaching home screen - OPTIMIZED
  const hasLoadedRef = useRef(false);
  
  useEffect(() => {
    if (screen === "home" && !hasLoadedRef.current) {
      hasLoadedRef.current = true;
      
      // Load articles immediately (50 limit for fast performance)
      loadArticles();
      
      // Only ingest if we have very few or no articles
      const checkAndIngest = async () => {
        // Wait a bit to let initial load complete
        await new Promise(resolve => setTimeout(resolve, 500));
        
        if (articles.length === 0 && !ingested && !isIngesting) {
          console.log("📰 No articles found, starting quick ingestion...");
          await handleIngest(true);
        }
      };
      
      checkAndIngest();
    }
  }, [screen]); // Only depend on screen to prevent infinite loops

  const loadArticles = async (category?: string, limit: number = 50) => {
    setIsLoadingArticles(true);
    
    // Add timeout to prevent infinite loading
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
    
    try {
      const catParam = category === "All" ? undefined : category;
      const data = await fetchArticles(catParam, limit);
      setArticles(data);
      console.log(`✅ Loaded ${data.length} articles`);
      clearTimeout(timeoutId);
    } catch (error: any) {
      clearTimeout(timeoutId);
      if (error.name === 'AbortError') {
        console.error("❌ Article loading timed out");
      } else {
        console.error("❌ Failed to load articles:", error);
      }
      setArticles([]);
    } finally {
      setIsLoadingArticles(false);
    }
  };

  const handleIngest = async (quick = false) => {
    setIsIngesting(true);
    try {
      console.log(`🔴 Starting ${quick ? 'quick' : 'full'} ingestion...`);
      const url = quick ? `${API_BASE}/ingest/live?quick=true` : `${API_BASE}/ingest/live`;
      const res = await fetch(url, { method: "POST" });
      if (!res.ok) throw new Error("Failed to ingest live");
      const result = await res.json();
      console.log("✅ Ingestion complete:", result);
      setIngested(true);
      await loadArticles();
    } catch (error) {
      console.error("❌ Ingestion failed:", error);
      // Don't alert - just log, user can still see existing articles
    } finally {
      setIsIngesting(false);
    }
  };

  const handleSelectPersona = (p: Persona) => {
    setSelectedPersona(p);
    setScreen("home");
  };

  const handleSelectArticle = async (article: Article) => {
    setSelectedArticle(article);
    setAnalysis(null);
    setScreen("article");

    // Auto-run analysis
    if (!selectedPersona) return;
    setIsLoadingAnalysis(true);
    try {
      const userProfile: UserProfile = {
        user_id: selectedPersona.user_id,
        name: selectedPersona.name,
        persona: selectedPersona.persona,
        level: selectedPersona.level,
        portfolio: selectedPersona.portfolio,
        interests: selectedPersona.interests,
      };
      const result = await analyzeNews({ query: article.title, user_profile: userProfile });
      setAnalysis(result);
    } catch {
      setAnalysis(null);
    } finally {
      setIsLoadingAnalysis(false);
    }
  };

  const handleGenerateVideo = async (article: Article, analysisData: AnalysisResponse) => {
    setIsGeneratingVideo(true);
    setVideoError(null);
    setVideoJob(null);
    setScreen("video_studio");

    try {
      const data = await generateVideo({
        article_title: article.title,
        summary: analysisData.summary,
        bull_view: analysisData.ui_metadata.bull,
        bear_view: analysisData.ui_metadata.bear,
      });
      await prefetchVideoJobAssets(data, API_BASE);
      setVideoJob(data);
    } catch (err: any) {
      setVideoError(err.message || "Failed to generate video briefing");
    } finally {
      setIsGeneratingVideo(false);
    }
  };

  const handleBack = () => {
    if (screen === "article") {
      setScreen("home");
      setSelectedArticle(null);
      setAnalysis(null);
    } else if (screen === "home") {
      setScreen("persona");
    }
  };

  return (
    <div className="min-h-screen bg-white text-[#1A1A1A]">
      <AnimatePresence mode="wait">
        {screen === "welcome" && (
          <WelcomeScreen key="welcome" onStart={() => setScreen("persona")} />
        )}
        {screen === "persona" && (
          <PersonaScreen key="persona" onSelect={handleSelectPersona} />
        )}
        {screen === "home" && selectedPersona && (
          <HomeScreen
            key="home"
            persona={selectedPersona}
            articles={articles}
            isLoading={isLoadingArticles}
            isIngesting={isIngesting}
            ingested={ingested}
            onSelectArticle={handleSelectArticle}
            onIngest={handleIngest}
            onRefresh={loadArticles}
            onChangePersona={() => setScreen("persona")}
            onOpenVideoStudio={() => setScreen("video_studio")}
            onOpenStoryArc={() => setScreen("story_arc")}
          />
        )}
        {screen === "article" && selectedArticle && selectedPersona && (
          <ArticleScreen
            key="article"
            article={selectedArticle}
            persona={selectedPersona}
            analysis={analysis}
            isLoading={isLoadingAnalysis}
            onBack={handleBack}
            onGenerateVideo={handleGenerateVideo}
            onViewStoryArc={(article) => {
              setSelectedArticle(article);
              setScreen("story_arc");
            }}
          />
        )}
        {screen === "video_studio" && selectedPersona && (
          <VideoStudioScreen
            key="video_studio"
            persona={selectedPersona}
            articles={articles}
            videoJob={videoJob}
            isGenerating={isGeneratingVideo}
            error={videoError}
            onGenerate={handleGenerateVideo}
            onClearVideo={() => setVideoJob(null)}
            onBack={() => setScreen("home")}
          />
        )}
        {screen === "story_arc" && selectedPersona && (
          <StoryArcScreen
            key="story_arc"
            persona={selectedPersona}
            articles={articles}
            onBack={() => setScreen("home")}
          />
        )}
      </AnimatePresence>
      <ChatWidget 
        userName={selectedPersona?.name} 
        articleText={screen === "article" && selectedArticle ? (selectedArticle.content || `${selectedArticle.title}\n\n${analysis?.summary || ""}`) : undefined}
      />
    </div>
  );
}

// ─── Shared Components ────────────────────────────────────────

function Logo({ className = "", light = false }: { className?: string; light?: boolean }) {
  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <div className="flex items-center gap-2">
        <h1 className={`text-2xl font-serif font-bold tracking-tight leading-none ${light ? 'text-white' : ''}`}
            style={{
              background: light ? 'white' : 'linear-gradient(135deg, #DC2626 0%, #000000 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              fontFamily: 'Georgia, serif'
            }}>
          E-newspaper
        </h1>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// SCREEN 1: WELCOME
// ═══════════════════════════════════════════════════════════════

function WelcomeScreen({ onStart }: { onStart: () => void }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1, transition: { duration: 0.5, ease: [0.25, 0.1, 0.25, 1] } }}
      exit={{ opacity: 0, transition: { duration: 0.3 } }}
      className="min-h-screen flex flex-col items-center justify-center relative overflow-hidden bg-white px-5"
    >
      {/* Clean gradient background */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#F5F5F7] via-white to-white pointer-events-none" />

      <motion.div
        initial={{ y: 30, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.2, duration: 0.6, ease: [0.25, 0.1, 0.25, 1] }}
        className="relative z-10 text-center max-w-[692px] mx-auto"
      >
        <Logo className="mb-8 justify-center" />

        <p className="section-eyebrow mb-4">E-newspaper • AI-Native News</p>

        <h1 className="font-serif apple-headline mb-6 text-[#1d1d1f]"
            style={{ 
              fontSize: 'clamp(2.75rem, 6vw, 5.5rem)',
              lineHeight: '1.05',
              letterSpacing: '-0.03em'
            }}>
          Next-Gen News<br />
          <em className="text-[#ED1C24] not-italic">Reimagined.</em>
        </h1>

        <p className="text-[1.1875rem] text-[#6e6e73] leading-relaxed max-w-[500px] mx-auto mb-10">
          Personalized intelligence briefings powered by multi-agent AI.
        </p>

        <div className="flex items-center justify-center gap-4 flex-wrap">
          <motion.button
            whileHover={{ y: -4 }}
            whileTap={{ y: 0, scale: 0.99 }}
            transition={{ duration: 0.25, ease: "easeOut" }}
            onClick={onStart}
            className="inline-flex items-center justify-center px-6 py-2.5 rounded-full bg-[#ED1C24] text-white text-[0.9375rem] font-medium tracking-[-0.01em] hover:bg-[#c8151b] transition-colors duration-200"
          >
            Begin Discovery
          </motion.button>
          <motion.button
            whileHover={{ y: -4 }}
            whileTap={{ y: 0, scale: 0.99 }}
            transition={{ duration: 0.25, ease: "easeOut" }}
            className="inline-flex items-center justify-center px-6 py-2.5 rounded-full border border-[#ED1C24] text-[#ED1C24] text-[0.9375rem] font-medium tracking-[-0.01em] hover:bg-[#ED1C24] hover:text-white transition-colors duration-200"
          >
            Learn more
          </motion.button>
        </div>

        <div className="mt-16 pt-8 border-t border-[#d2d2d7]">
          <p className="section-eyebrow">
            Powered by Multi-Agent RAG • GenAI Hackathon 2026
          </p>
        </div>
      </motion.div>
    </motion.div>
  );
}

// ═══════════════════════════════════════════════════════════════
// SCREEN 2: PERSONA SELECTION
// ═══════════════════════════════════════════════════════════════

function PersonaScreen({ onSelect }: { onSelect: (p: Persona) => void }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1, transition: { duration: 0.5, ease: [0.25, 0.1, 0.25, 1] } }}
      exit={{ opacity: 0, transition: { duration: 0.3 } }}
      className="min-h-screen flex flex-col items-center justify-center px-5 py-24 md:py-32 bg-[#F5F5F7]"
    >
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.1, duration: 0.6, ease: [0.25, 0.1, 0.25, 1] }}
        className="text-center mb-12"
      >
        <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center mx-auto mb-4 border border-[#e8e8ed]">
          <User className="w-5 h-5 text-[#ED1C24]" />
        </div>
        <h2 className="font-serif apple-headline text-[clamp(2rem,4vw,2.75rem)] mb-3 text-[#1d1d1f]">
          Choose Your Persona
        </h2>
        <p className="text-[#6e6e73] text-[1.0625rem] max-w-md mx-auto leading-relaxed">
          E-newspaper tailors every insight to your experience level and interests.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 w-full max-w-3xl">
        {DEMO_PERSONAS.map((p, i) => {
          const meta = PERSONA_META[p.persona] || { role: p.persona, icon: "👤", desc: "" };
          return (
            <motion.button
              key={p.user_id}
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.15 + i * 0.08, duration: 0.6, ease: [0.25, 0.1, 0.25, 1] }}
              whileHover={{ y: -4 }}
              whileTap={{ y: 0, scale: 0.99 }}
              onClick={() => onSelect(p)}
              className="group p-6 text-left bg-white border border-[#e8e8ed] rounded-2xl hover:border-[#d2d2d7] hover:shadow-[0_4px_20px_rgba(0,0,0,0.08)] transition-all duration-300"
            >
              <div className="flex items-start gap-4">
                <div className="text-3xl">{meta.icon}</div>
                <div className="flex-1">
                  <p className="section-eyebrow mb-1">{meta.role}</p>
                  <span className="inline-block text-[0.6875rem] font-medium px-2 py-0.5 bg-[#F5F5F7] text-[#6e6e73] rounded-full mb-3">
                    Profile Active
                  </span>
                  <p className="text-[0.8125rem] text-[#6e6e73] leading-relaxed mb-3">{meta.desc}</p>
                  {p.portfolio.length > 0 && (
                    <div className="flex flex-wrap gap-1.5">
                      {p.portfolio.map(tk => (
                        <span key={tk} className="text-[0.6875rem] font-medium px-2 py-0.5 bg-[#F5F5F7] border border-[#e8e8ed] rounded text-[#6e6e73]">
                          {tk}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <ChevronRight className="w-5 h-5 text-[#aeaeb2] group-hover:text-[#ED1C24] transition-colors mt-1" />
              </div>
            </motion.button>
          );
        })}
      </div>
    </motion.div>
  );
}

// ═══════════════════════════════════════════════════════════════
// SCREEN 3: HOME — ARTICLE GRID
// ═══════════════════════════════════════════════════════════════

interface HomeScreenProps {
  persona: Persona;
  articles: Article[];
  isLoading: boolean;
  isIngesting: boolean;
  ingested: boolean;
  onSelectArticle: (a: Article) => void;
  onIngest: () => void;
  onRefresh: (category?: string) => void;
  onChangePersona: () => void;
  onOpenVideoStudio: () => void;
  onOpenStoryArc: () => void;
}

function HomeScreen({
  persona,
  articles,
  isLoading,
  isIngesting,
  ingested,
  onSelectArticle,
  onIngest,
  onRefresh,
  onChangePersona,
  onOpenVideoStudio,
  onOpenStoryArc,
}: HomeScreenProps) {
  const [activeCategory, setActiveCategory] = useState<string>("All");

  const categories = [
    "All", "Markets", "Politics", "Tech", "Economy", "Startups", 
    "Wealth", "Industry", "Environment", "International", "Opinion", "Mutual Funds"
  ];

  // Client-side filtering - no need to refetch from server for categories
  const filteredArticles = useMemo(() => {
    if (activeCategory === "All") return articles;
    return articles.filter(a => (a.tags ?? []).includes(activeCategory));
  }, [articles, activeCategory]);


  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1, transition: { duration: 0.5, ease: [0.25, 0.1, 0.25, 1] } }}
      exit={{ opacity: 0, transition: { duration: 0.3 } }}
      className="min-h-screen bg-white"
    >
      {/* ── Header ── */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-xl backdrop-saturate-150 border-b border-[#d2d2d7]/60">
        <div className="apple-container h-[52px] flex items-center justify-between">
          <Logo />

          <div className="flex items-center gap-4">
            <button
              onClick={onOpenVideoStudio}
              className="flex items-center gap-2 px-4 py-2 text-[0.8125rem] font-normal text-[#1d1d1f] hover:text-[#ED1C24] transition-colors"
            >
              <Video className="w-4 h-4" />
              <span>Video Studio</span>
            </button>
            <button
               onClick={() => onOpenStoryArc()}
               className="flex items-center gap-2 px-4 py-2 text-[0.8125rem] font-normal text-[#1d1d1f] hover:text-[#ED1C24] transition-colors"
             >
               <Brain className="w-4 h-4" />
               <span>Story Arc</span>
             </button>
            <button
              onClick={() => onRefresh(activeCategory)}
              className="p-2 text-[#6e6e73] hover:text-[#ED1C24] transition-colors rounded-lg"
              title="Refresh articles"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
            <button
              onClick={onIngest}
              disabled={isIngesting}
              className="px-4 py-1.5 text-[0.8125rem] font-normal border border-[#e8e8ed] rounded-full hover:bg-[#F5F5F7] transition-colors disabled:opacity-50"
            >
              {isIngesting ? "Loading..." : ingested ? "✓ Data Ready" : "Load Data"}
            </button>
            <button
              onClick={onChangePersona}
              className="flex items-center gap-2 px-3 py-1.5 bg-[#F5F5F7] border border-[#e8e8ed] rounded-full hover:border-[#d2d2d7] transition-colors"
            >
              <span className="text-base">{PERSONA_META[persona.persona]?.icon || "👤"}</span>
              <span className="text-[0.8125rem] font-medium text-[#1d1d1f]">{persona.name}</span>
            </button>
          </div>
        </div>
      </header>

      {/* ── Content ── */}
      <main className="apple-container py-16 md:py-24">
        <div className="flex items-center justify-between mb-12">
          <div>
            <h2 className="font-serif apple-headline text-[clamp(1.5rem,3vw,2rem)] text-[#1d1d1f]">Latest News</h2>
            <p className="text-[0.9375rem] text-[#6e6e73] mt-2 leading-relaxed">
              Choose a category, then tap any story for AI-powered analysis tailored to your profile
            </p>
          </div>
          <div className="text-right">
            <span className="text-[0.8125rem] font-medium text-[#6e6e73] block">
              {filteredArticles.length} articles
            </span>
            <span className="section-eyebrow">
              {activeCategory === "All" ? "All Categories" : activeCategory}
            </span>
          </div>
        </div>

        {isLoading ? (
          <div className="space-y-8">
            <div className="text-center py-8">
              <div className="inline-flex items-center gap-3 px-6 py-3 bg-[#F5F5F7] rounded-2xl">
                <Loader2 className="w-5 h-5 text-[#ED1C24] animate-spin" />
                <span className="text-[0.9375rem] text-[#6e6e73] font-medium">Loading articles...</span>
              </div>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <ArticleSkeleton key={i} />
              ))}
            </div>
          </div>
        ) : articles.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-24 border-2 border-dashed border-[#e8e8ed] rounded-2xl bg-[#F5F5F7]">
            <BookOpen className="w-10 h-10 text-[#aeaeb2] mb-4" />
            <p className="text-[#6e6e73] font-medium mb-2">No articles yet</p>
            <p className="text-[0.8125rem] text-[#aeaeb2] mb-6">Load live articles to get started</p>
            <button
              onClick={onIngest}
              disabled={isIngesting}
              className="inline-flex items-center justify-center px-6 py-2.5 rounded-full bg-[#ED1C24] text-white text-[0.9375rem] font-medium tracking-[-0.01em] hover:bg-[#c8151b] transition-colors duration-200 disabled:opacity-50"
            >
              {isIngesting ? "Loading..." : "Load Articles"}
            </button>
          </div>
        ) : (
          <div className="space-y-8">
            {/* Category chips */}
            <div className="flex flex-wrap items-center gap-2">
              <span className="section-eyebrow mr-2">Browse by topic</span>
              {categories.map(cat => {
                const selected = cat === activeCategory;
                return (
                  <button
                    key={cat}
                    type="button"
                    onClick={() => setActiveCategory(cat)}
                    className={
                      "px-4 py-1.5 rounded-full text-[0.8125rem] font-medium transition-colors duration-200 " +
                      (selected
                        ? "bg-[#1d1d1f] text-white"
                        : "bg-[#F5F5F7] text-[#1d1d1f] hover:bg-[#e8e8ed]")
                    }
                    aria-pressed={selected}
                    title={cat === "All" ? "Show all news" : `Show ${cat} news`}
                  >
                    {cat === "All" ? "All News" : cat}
                  </button>
                );
              })}
            </div>

            {/* Feed header */}
            <div className="flex items-center gap-3 pb-6 border-b border-[#e8e8ed]">
              <h3 className="font-serif apple-headline-sm text-[1.25rem] text-[#1d1d1f]">
                {activeCategory === "All" ? "Top Intelligence Briefs" : `${activeCategory} Special Reports`}
              </h3>
              <span className="section-eyebrow px-2 py-0.5 bg-[#F5F5F7] rounded-full">
                For {persona.name}
              </span>
            </div>

            {/* Articles Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
              {filteredArticles.map((article, i) => (
                <ArticleCard
                  key={article.id + i}
                  article={article}
                  index={i}
                  onClick={() => onSelectArticle(article)}
                />
              ))}
              {filteredArticles.length === 0 && (
                <div className="col-span-full border-2 border-dashed border-[#e8e8ed] rounded-2xl p-10 text-center bg-[#F5F5F7]">
                  <p className="text-[#6e6e73] font-medium mb-1">No stories in this category yet</p>
                  <p className="text-[0.8125rem] text-[#aeaeb2]">Try a different topic or load fresh data.</p>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </motion.div>
  );
}

// ─── Article Card Component ─────────────────────────────────────

function ArticleCard({ article, index, onClick }: { article: Article; index: number; onClick: () => void }) {
  const thumbnailUrl =
    article.image_url && article.image_url.trim().length > 0 && !article.image_url.includes("placeholder")
      ? article.image_url
      : getFallbackThumbnailDataUrl(article);

  return (
    <motion.div
      initial={{ y: 30, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay: index * 0.08, duration: 0.6, ease: [0.25, 0.1, 0.25, 1] }}
      whileHover={{ y: -4 }}
      whileTap={{ y: 0, scale: 0.99 }}
      onClick={onClick}
      className="group bg-white rounded-2xl border border-[#e8e8ed] overflow-hidden cursor-pointer hover:border-[#d2d2d7] hover:shadow-[0_4px_20px_rgba(0,0,0,0.08)] transition-all duration-300"
    >
      {/* Thumbnail */}
      <div className="overflow-hidden aspect-[16/10]">
        <img
          src={thumbnailUrl}
          alt={article.title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          loading="lazy"
        />
      </div>

      {/* Content */}
      <div className="p-6">
        {article.tags?.[0] && (
          <p className="section-eyebrow mb-2">{article.tags[0]}</p>
        )}
        <h3 className="font-serif apple-headline-sm text-[1.125rem] mb-2 line-clamp-2 text-[#1d1d1f] group-hover:text-[#ED1C24] transition-colors">
          {article.title}
        </h3>
        <p className="text-[0.8125rem] text-[#6e6e73] leading-relaxed line-clamp-2 mb-4">
          {article.summary}
        </p>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-[0.75rem] text-[#aeaeb2]">
            <Calendar className="w-3 h-3" />
            <span>{article.date}</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

// ═══════════════════════════════════════════════════════════════
// SCREEN 4: ARTICLE DETAIL + AI AGENTS
// ═══════════════════════════════════════════════════════════════

interface ArticleScreenProps {
  article: Article;
  persona: Persona;
  analysis: AnalysisResponse | null;
  isLoading: boolean;
  onBack: () => void;
  onGenerateVideo: (article: Article, analysis: AnalysisResponse) => void;
  onViewStoryArc: (article: Article) => void;
}

function ArticleScreen({ article, persona, analysis, isLoading, onBack, onGenerateVideo, onViewStoryArc }: ArticleScreenProps) {
  const meta = PERSONA_META[persona.persona] || { role: persona.persona, icon: "👤" };
  const hasImage = article.image_url && !article.image_url.includes("placeholder");

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1, transition: { duration: 0.5, ease: [0.25, 0.1, 0.25, 1] } }}
      exit={{ opacity: 0, transition: { duration: 0.3 } }}
      className="min-h-screen bg-white"
    >
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-xl backdrop-saturate-150 border-b border-[#d2d2d7]/60">
        <div className="apple-container h-[52px] flex items-center justify-between">
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-[0.8125rem] font-normal text-[#1d1d1f] hover:text-[#ED1C24] transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back</span>
          </button>
          <Logo />
          <div className="flex items-center gap-2 px-3 py-1.5 bg-[#F5F5F7] rounded-full border border-[#e8e8ed]">
            <span className="text-base">{meta.icon}</span>
            <span className="text-[0.8125rem] font-medium text-[#1d1d1f]">{persona.name}</span>
          </div>
        </div>
      </header>

      <div className="apple-container py-16 md:py-24">
        {/* Article Header */}
        <div className="mb-16">
          {/* Tags */}
          {article.tags && article.tags.length > 0 && (
            <div className="flex gap-2 mb-4">
              {article.tags.slice(0, 3).map(tag => (
                <span key={tag} className="section-eyebrow px-2 py-1 bg-[#F5F5F7] rounded-full">
                  {tag}
                </span>
              ))}
            </div>
          )}

          {/* Title */}
          <h1 className="font-serif apple-headline mb-6 text-[#1d1d1f]"
              style={{
                fontSize: 'clamp(1.75rem, 4vw, 3.25rem)',
                lineHeight: '1.08',
                letterSpacing: '-0.025em'
              }}>
            {article.title}
          </h1>

          {/* Meta */}
          <div className="flex items-center gap-4 text-[0.8125rem] text-[#6e6e73] mb-8">
            <div className="flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5" />
              <span>{article.date}</span>
            </div>
            <span>•</span>
            <span className="font-medium text-[#ED1C24]">E-newspaper</span>
          </div>

          {/* Banner Image */}
          {hasImage && (
            <div className="w-full aspect-[21/9] rounded-2xl overflow-hidden mb-8 bg-[#F5F5F7]">
              <img
                src={article.image_url!}
                alt={article.title}
                className="w-full h-full object-cover"
                onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
              />
            </div>
          )}

          {/* Article Summary */}
          <div className="prose max-w-none">
            <p className="text-[1.0625rem] leading-[1.65] text-[#1d1d1f] font-normal">
              {article.summary}
            </p>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-[#e8e8ed] pt-16 mb-12">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 bg-[#F5F5F7] rounded-full flex items-center justify-center">
              <Brain className="w-5 h-5 text-[#ED1C24]" />
            </div>
            <div>
              <h2 className="font-serif apple-headline-sm text-[1.25rem] text-[#1d1d1f]">AI Agent Analysis</h2>
              <p className="section-eyebrow">Personalized for {persona.name}</p>
            </div>
          </div>
        </div>

        {/* AI Analysis Section */}
        {isLoading ? (
          <div className="py-16">
            <div className="flex flex-col items-center gap-4 mb-12">
              <Loader2 className="w-8 h-8 text-[#ED1C24] animate-spin" />
              <p className="text-[0.9375rem] text-[#6e6e73]">Analyzing with multi-agent AI...</p>
            </div>
            <AnalysisSkeleton />
          </div>
        ) : analysis ? (
          <div className="space-y-8">
            {/* Video Generation CTA */}
            <div className="liquid-glass p-8 rounded-2xl flex flex-col md:flex-row items-center justify-between gap-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-[#ED1C24] rounded-2xl flex items-center justify-center">
                  <PlayCircle className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="font-serif apple-headline-sm text-[1.125rem] text-[#1d1d1f] mb-1">
                    Generate AI News Briefing
                  </h3>
                  <p className="text-[0.8125rem] text-[#6e6e73]">Transform this analysis into a 60-second broadcast video</p>
                </div>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => onGenerateVideo(article, analysis)}
                  className="inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-full bg-[#ED1C24] text-white text-[0.9375rem] font-medium tracking-[-0.01em] hover:bg-[#c8151b] transition-colors duration-200"
                >
                  <Sparkles className="w-4 h-4" />
                  Create Briefing
                </button>
                <button
                  onClick={() => onViewStoryArc(article)}
                  className="inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-full border border-[#ED1C24] text-[#ED1C24] text-[0.9375rem] font-medium tracking-[-0.01em] hover:bg-[#ED1C24] hover:text-white transition-colors duration-200"
                >
                  <Brain className="w-4 h-4" />
                  View Story Arc
                </button>
              </div>
            </div>

            {/* Executive Summary */}
            <div className="bg-[#F5F5F7] rounded-2xl p-8">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-[#1d1d1f] rounded-xl flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 className="font-serif apple-headline-sm text-[1.125rem] text-[#1d1d1f]">Executive Briefing</h3>
                  <p className="section-eyebrow">AI Synthesis • Confidence: {Math.round(analysis.confidence * 100)}%</p>
                </div>
              </div>
              <h4 className="font-serif apple-headline text-[clamp(1.25rem,3vw,1.75rem)] mb-4 text-[#1d1d1f]">
                {analysis.headline}
              </h4>
              <p className="text-[1.0625rem] leading-[1.65] text-[#1d1d1f] whitespace-pre-line">
                {analysis.summary}
              </p>
            </div>

            {/* Bull & Bear Analysis */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Bull Agent */}
              <div className="bg-white rounded-2xl p-6 border border-[#e8e8ed]">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center">
                    <TrendingUp className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <h3 className="text-[0.9375rem] font-semibold text-[#1d1d1f]">Bull Perspective</h3>
                    <p className="section-eyebrow">Optimistic View</p>
                  </div>
                </div>
                <p className="text-[0.9375rem] leading-relaxed text-[#6e6e73]">{analysis.ui_metadata.bull}</p>
              </div>

              {/* Bear Agent */}
              <div className="bg-white rounded-2xl p-6 border border-[#e8e8ed]">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-8 h-8 bg-red-500 rounded-lg flex items-center justify-center">
                    <TrendingDown className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <h3 className="text-[0.9375rem] font-semibold text-[#1d1d1f]">Bear Perspective</h3>
                    <p className="section-eyebrow">Cautious View</p>
                  </div>
                </div>
                <p className="text-[0.9375rem] leading-relaxed text-[#6e6e73]">{analysis.ui_metadata.bear}</p>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-16">
            <p className="text-[#6e6e73]">No analysis available</p>
          </div>
        )}
      </div>
    </motion.div>
  );
}

// ═══════════════════════════════════════════════════════════════
// SCREEN 5: VIDEO STUDIO
// ═══════════════════════════════════════════════════════════════

interface VideoStudioScreenProps {
  persona: Persona;
  articles: Article[];
  videoJob: VideoResponse | null;
  isGenerating: boolean;
  error: string | null;
  onGenerate: (article: Article, analysis: AnalysisResponse) => void;
  onClearVideo: () => void;
  onBack: () => void;
}

function VideoStudioScreen({
  persona,
  articles,
  videoJob,
  isGenerating,
  error,
  onGenerate,
  onClearVideo,
  onBack,
}: VideoStudioScreenProps) {
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(articles[0] || null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleStartGeneration = async () => {
    if (!selectedArticle) return;
    setIsAnalyzing(true);
    try {
      // First generate analysis if needed
      const res = await analyzeNews({
        query: selectedArticle.title,
        user_profile: {
          user_id: persona.user_id,
          persona: persona.persona,
          level: persona.level,
          portfolio: persona.portfolio,
          interests: persona.interests,
        },
      });
      onGenerate(selectedArticle, res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="min-h-screen bg-[#F5F5F7]"
    >
      {/* Apple-style 52px glass header */}
      <header className="h-[52px] bg-white/80 backdrop-blur-xl border-b border-black/5 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-full flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={onBack}
              className="w-7 h-7 flex items-center justify-center hover:bg-black/5 rounded-full transition-all"
            >
              <ArrowLeft className="w-4 h-4 text-[#1d1d1f]" />
            </button>
            <h1 className="text-[19px] font-semibold tracking-tight text-[#1d1d1f]">AI Video Studio</h1>
          </div>
          <div className="text-xl font-serif" style={{
            background: "linear-gradient(135deg, #ED1C24 0%, #1d1d1f 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            backgroundClip: "text",
          }}>
            E-newspaper
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-16">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left: Video Preview */}
          <div className="lg:col-span-8">
            <div className="aspect-video bg-[#1d1d1f] rounded-[18px] shadow-xl overflow-hidden relative">
              {isGenerating || isAnalyzing ? (
                <div className="absolute inset-0 flex flex-col bg-white overflow-hidden z-20">
                  <div className="p-8 border-b border-gray-100 flex items-center justify-between">
                    <div>
                      <Skeleton className="h-6 w-48 mb-2" />
                      <Skeleton className="h-4 w-32" />
                    </div>
                    <div className="flex gap-2">
                       <Skeleton className="h-8 w-20 rounded-lg" />
                       <Skeleton className="h-8 w-20 rounded-lg" />
                    </div>
                  </div>
                  <div className="flex-1 overflow-hidden">
                    <StoryboardSkeleton />
                  </div>
                  <div className="p-8 bg-[#F5F5F7] border-t border-gray-100 flex items-center justify-center gap-6">
                    <div className="flex flex-col items-center gap-3">
                      <div className="w-12 h-12 bg-[#ED1C24]/10 rounded-full flex items-center justify-center">
                        <Loader2 className="w-6 h-6 text-[#ED1C24] animate-spin" />
                      </div>
                      <p className="text-[13px] font-medium text-[#1d1d1f]">
                        {isAnalyzing ? "Analyzing Intelligence..." : "Synthesizing Video Briefing..."}
                      </p>
                    </div>
                  </div>
                </div>
              ) : videoJob ? (
                <Player
                  component={NewsVideo}
                  inputProps={{
                    script: videoJob.script,
                    audio_url: `${API_BASE}${videoJob.audio_url}`,
                    subtitles_url: `${API_BASE}${videoJob.subtitles_url}`,
                    subtitles_text: videoJob.subtitles_text,
                    article_title: selectedArticle?.title || "AI Briefing",
                    caption_words: videoJob.caption_words ?? [],
                  }}
                  durationInFrames={videoJob.total_frames ?? 1800}
                  fps={30}
                  compositionWidth={1280}
                  compositionHeight={720}
                  style={{
                    width: '100%',
                    height: '100%',
                  }}
                  controls
                />
              ) : (
                <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-12">
                  <PlayCircle className="w-20 h-20 text-white/10 mb-6" />
                  <h3 className="text-white text-[28px] font-semibold tracking-tight mb-2">Studio Ready</h3>
                  <p className="text-gray-400 text-[17px] max-w-sm mx-auto leading-relaxed">
                    Select an article and click 'Produce Briefing' to create your AI-powered video.
                  </p>
                </div>
              )}
            </div>

            {error && (
              <motion.div 
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-6 p-4 bg-red-50 border border-red-200 rounded-[12px] flex items-center gap-3 text-red-600"
              >
                <Zap className="w-5 h-5 flex-shrink-0" />
                <span className="text-[15px] font-medium">{error}</span>
              </motion.div>
            )}
          </div>

          {/* Right: Controls */}
          <div className="lg:col-span-4 space-y-6">
            {/* Article Selection Card */}
            <div className="liquid-glass rounded-[18px] p-6">
              <h3 className="text-[13px] font-semibold text-[#86868b] mb-4 flex items-center gap-2">
                <Play className="w-4 h-4" />
                News Desk
              </h3>
              <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2">
                {articles.slice(0, 10).map((article) => (
                  <button
                    key={article.id}
                    onClick={() => { setSelectedArticle(article); onClearVideo(); }}
                    className={`w-full text-left p-4 rounded-[12px] transition-all border ${
                      selectedArticle?.id === article.id
                        ? "bg-[#1d1d1f] border-[#1d1d1f] text-white shadow-lg"
                        : "bg-white border-black/5 hover:border-black/10 text-[#1d1d1f]"
                    }`}
                  >
                    <p className="text-[11px] font-medium opacity-60 mb-1">{article.date}</p>
                    <p className="font-semibold text-[15px] leading-tight line-clamp-2">{article.title}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Produce Button */}
            <button
              onClick={handleStartGeneration}
              disabled={!selectedArticle || isGenerating || isAnalyzing}
              className="w-full h-[56px] bg-[#0071e3] text-white rounded-full text-[17px] font-medium shadow-lg hover:bg-[#0077ED] transition-all active:scale-[0.98] flex items-center justify-center gap-3 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {isGenerating || isAnalyzing ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  Produce Briefing
                </>
              )}
            </button>

            {/* Info Card */}
            <div className="p-6 bg-[#F5F5F7] rounded-[18px] border border-black/5">
              <div className="flex items-center gap-2 mb-2">
                <Shield className="w-4 h-4 text-[#0071e3]" />
                <h4 className="text-[13px] font-semibold text-[#1d1d1f]">Studio Intelligence</h4>
              </div>
              <p className="text-[15px] text-[#6e6e73] leading-relaxed">
                Our AI Director automatically selects HD stock footage and synthesizes professional narration using the E-newspaper Intelligence voice system.
              </p>
            </div>
          </div>
        </div>
      </main>
    </motion.div>
  );
}
