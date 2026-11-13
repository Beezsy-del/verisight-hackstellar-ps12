import React, { useEffect, useRef, createContext, useContext } from "react";

export type VerdictThemeType = "idle" | "authentic" | "suspicious" | "fraud";

export interface VerdictThemeContextValue {
  theme: VerdictThemeType;
  threatScore: number;
  verdict: string;
  isLoading: boolean;
  borderClass: string;
  glowClass: string;
  accentColor: string;
  badgeBg: string;
  badgeText: string;
  badgeBorder: string;
}

export const VerdictThemeContext = createContext<VerdictThemeContextValue>({
  theme: "idle",
  threatScore: 0,
  verdict: "",
  isLoading: false,
  borderClass: "border-cyan-500/30",
  glowClass: "shadow-[0_0_40px_-10px_rgba(6,182,212,0.2)]",
  accentColor: "cyan",
  badgeBg: "bg-cyan-950/80",
  badgeText: "text-cyan-300",
  badgeBorder: "border-cyan-800/50",
});

export const useVerdictTheme = () => useContext(VerdictThemeContext);

interface AmbientThreatBackgroundProps {
  threatScore?: number; // 0 to 100
  verdict?: string;
  isLoading?: boolean;
  className?: string;
  children?: React.ReactNode;
}

export const AmbientThreatBackground: React.FC<AmbientThreatBackgroundProps> = ({
  threatScore = 0,
  verdict = "",
  isLoading = false,
  className = "",
  children,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  // Compute active theme state
  let theme: VerdictThemeType = "idle";
  let baseBg = "#060a12";
  let radialGradient =
    "radial-gradient(circle at 50% 35%, rgba(6, 182, 212, 0.12), rgba(6, 10, 18, 0.98) 75%)";
  let borderClass = "border-cyan-500/30";
  let glowClass = "shadow-[0_0_40px_-10px_rgba(6,182,212,0.2)]";
  let accentColor = "cyan";
  let badgeBg = "bg-cyan-950/80";
  let badgeText = "text-cyan-300";
  let badgeBorder = "border-cyan-800/50";
  let orbColor1 = "rgba(6, 182, 212, 0.16)";
  let orbColor2 = "rgba(14, 165, 233, 0.10)";
  let orbAccent = "rgba(6, 182, 212, 0.08)";

  if (isLoading) {
    theme = "idle";
    baseBg = "#060a12";
    radialGradient =
      "radial-gradient(circle at 50% 35%, rgba(6, 182, 212, 0.16), rgba(6, 10, 18, 0.98) 75%)";
    borderClass = "border-cyan-500/40";
    glowClass = "shadow-[0_0_45px_-10px_rgba(6,182,212,0.3)]";
    accentColor = "cyan";
    badgeBg = "bg-cyan-950/80";
    badgeText = "text-cyan-300";
    badgeBorder = "border-cyan-800/50";
    orbColor1 = "rgba(6, 182, 212, 0.22)";
    orbColor2 = "rgba(14, 165, 233, 0.14)";
    orbAccent = "rgba(6, 182, 212, 0.12)";
  } else if (
    threatScore >= 65 ||
    verdict === "CORROBORATED_ANOMALIES" ||
    verdict === "MANIPULATED_FORGERY"
  ) {
    theme = "fraud";
    baseBg = "#120205";
    radialGradient =
      "radial-gradient(circle at 50% 40%, rgba(225, 29, 72, 0.25), rgba(35, 6, 12, 0.95) 60%, #120205 100%)";
    borderClass = "border-rose-500/60";
    glowClass = "shadow-[0_0_65px_-10px_rgba(244,63,94,0.45)]";
    accentColor = "rose";
    badgeBg = "bg-rose-950/90";
    badgeText = "text-rose-300";
    badgeBorder = "border-rose-800/60";
    orbColor1 = "rgba(244, 63, 94, 0.28)";
    orbColor2 = "rgba(225, 29, 72, 0.20)";
    orbAccent = "rgba(244, 63, 94, 0.16)";
  } else if (
    threatScore >= 25 ||
    verdict === "REVIEW_REQUIRED" ||
    verdict === "SUSPICIOUS"
  ) {
    theme = "suspicious";
    baseBg = "#0f0902";
    radialGradient =
      "radial-gradient(circle at 50% 40%, rgba(245, 158, 11, 0.18), rgba(28, 17, 5, 0.94) 60%, #0f0902 100%)";
    borderClass = "border-amber-500/35";
    glowClass = "shadow-[0_0_50px_-12px_rgba(245,158,11,0.25)]";
    accentColor = "amber";
    badgeBg = "bg-amber-950/90";
    badgeText = "text-amber-300";
    badgeBorder = "border-amber-800/60";
    orbColor1 = "rgba(245, 158, 11, 0.22)";
    orbColor2 = "rgba(234, 88, 12, 0.14)";
    orbAccent = "rgba(245, 158, 11, 0.12)";
  } else {
    theme = "authentic";
    baseBg = "#020d0a";
    radialGradient =
      "radial-gradient(circle at 50% 40%, rgba(16, 185, 129, 0.16), rgba(4, 24, 18, 0.92) 60%, #020d0a 100%)";
    borderClass = "border-emerald-500/30";
    glowClass = "shadow-[0_0_50px_-12px_rgba(16,185,129,0.25)]";
    accentColor = "emerald";
    badgeBg = "bg-emerald-950/90";
    badgeText = "text-emerald-300";
    badgeBorder = "border-emerald-800/60";
    orbColor1 = "rgba(16, 185, 129, 0.20)";
    orbColor2 = "rgba(14, 165, 233, 0.12)";
    orbAccent = "rgba(16, 185, 129, 0.10)";
  }

  // Mouse proximity spotlight tracking
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handlePointerMove = (e: PointerEvent) => {
      const rect = container.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      container.style.setProperty("--mouse-x", `${x}px`);
      container.style.setProperty("--mouse-y", `${y}px`);
    };

    window.addEventListener("pointermove", handlePointerMove);
    return () => window.removeEventListener("pointermove", handlePointerMove);
  }, []);

  const contextValue: VerdictThemeContextValue = {
    theme,
    threatScore,
    verdict,
    isLoading,
    borderClass,
    glowClass,
    accentColor,
    badgeBg,
    badgeText,
    badgeBorder,
  };

  return (
    <VerdictThemeContext.Provider value={contextValue}>
      <div
        ref={containerRef}
        className={`relative w-full h-full overflow-hidden transition-all duration-700 ease-out ${className}`}
        style={
          {
            backgroundColor: baseBg,
            backgroundImage: radialGradient,
            "--mouse-x": "50%",
            "--mouse-y": "50%",
          } as React.CSSProperties
        }
      >
        {/* 1. Base Forensic Dual-Scale Grid: 16px micro-dots & 128px macro grid */}
        <div
          className="pointer-events-none absolute inset-0 z-0 opacity-80"
          style={{
            backgroundImage: `
              radial-gradient(circle at 1px 1px, rgba(255, 255, 255, 0.05) 1px, transparent 0),
              linear-gradient(to right, rgba(56, 189, 248, 0.035) 1px, transparent 1px),
              linear-gradient(to bottom, rgba(56, 189, 248, 0.035) 1px, transparent 1px)
            `,
            backgroundSize: "16px 16px, 128px 128px, 128px 128px",
          }}
        />

        {/* 2. Hardware-accelerated Cursor Proximity Spotlight (react-bits inspired) */}
        <div
          className="pointer-events-none absolute inset-0 z-0 transition-opacity duration-300"
          style={{
            background: `radial-gradient(420px circle at var(--mouse-x) var(--mouse-y), rgba(56, 189, 248, 0.09), transparent 80%)`,
          }}
        />

        {/* 3. Ambient Threat-State Backlight (slow breathing glow based on case risk) */}
        <div
          className="pointer-events-none absolute -top-40 left-1/4 h-[550px] w-[650px] rounded-full blur-[140px] transition-all duration-1000 ease-out"
          style={{
            background: `radial-gradient(circle, ${orbColor1} 0%, ${orbColor2} 50%, transparent 80%)`,
          }}
        />
        <div
          className="pointer-events-none absolute bottom-[-100px] right-10 h-[450px] w-[500px] rounded-full blur-[130px] transition-all duration-1000 ease-out"
          style={{
            background: `radial-gradient(circle, ${orbAccent} 0%, transparent 75%)`,
          }}
        />

        {/* Content wrapper */}
        <div className="relative z-10 flex h-full w-full flex-col">{children}</div>
      </div>
    </VerdictThemeContext.Provider>
  );
};
