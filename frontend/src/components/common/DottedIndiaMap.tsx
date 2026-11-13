import React, { useState } from "react";
import { RealWorldFraudCase } from "../../data/realWorldCases";
import {
  INDIA_MAP_VIEWBOX,
  INDIA_BOUNDARY_PATH,
  INDIA_DOT_MATRIX,
  CITY_GEOPOINTS,
} from "../../data/indiaGeospatial";
import { ArrowRight, ShieldCheck } from "lucide-react";

interface DottedIndiaMapProps {
  cases: RealWorldFraudCase[];
  activeCaseId: string;
  onSelectCase: (caseId: string) => void;
  className?: string;
}

export const DottedIndiaMap: React.FC<DottedIndiaMapProps> = ({
  cases,
  activeCaseId,
  onSelectCase,
  className = "",
}) => {
  const [hoveredCaseId, setHoveredCaseId] = useState<string | null>(null);

  const activeCase = cases.find((c) => c.id === activeCaseId) || cases[0];
  const displayCase = cases.find((c) => c.id === hoveredCaseId) || activeCase;

  // Find coordinates for the currently displayed case
  const activeCityPoint = displayCase ? CITY_GEOPOINTS[displayCase.city] : null;

  // Calculate smart anchor position for callout card
  // If city is on right side of India (x > 220), place card to the left, otherwise place to the right
  const isRightSide = activeCityPoint ? activeCityPoint.x > 220 : false;
  const isBottom = activeCityPoint ? activeCityPoint.y > 320 : false;

  const cardX = activeCityPoint
    ? isRightSide
      ? Math.max(10, activeCityPoint.x - 180)
      : Math.min(260, activeCityPoint.x + 35)
    : 190;

  const cardY = activeCityPoint
    ? isBottom
      ? Math.max(100, activeCityPoint.y - 70)
      : Math.min(380, activeCityPoint.y - 20)
    : 140;

  return (
    <div className={`relative flex flex-col items-center select-none w-full ${className}`}>
      {/* SVG Canvas for Dotted Map */}
      <div className="relative w-full max-w-[380px] aspect-[440/500] overflow-visible">
        <svg
          viewBox={INDIA_MAP_VIEWBOX}
          className="w-full h-full overflow-visible"
          aria-label="Official Survey of India Geospatial Matrix showing verified incident locations"
        >
          <defs>
            {/* Subtle glow filter */}
            <filter id="cyanGlow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
            <filter id="pinGlow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="4" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>

            {/* Gradient for subtle map backdrop */}
            <radialGradient id="mapBackdrop" cx="45%" cy="45%" r="55%">
              <stop offset="0%" stopColor="#0284c7" stopOpacity="0.08" />
              <stop offset="70%" stopColor="#0f766e" stopOpacity="0.03" />
              <stop offset="100%" stopColor="#000000" stopOpacity="0" />
            </radialGradient>
          </defs>

          {/* Authentic Boundary Backdrop & Subtle Glow */}
          <path
            d={INDIA_BOUNDARY_PATH}
            fill="url(#mapBackdrop)"
            stroke="rgba(56, 189, 248, 0.14)"
            strokeWidth="0.8"
            className="transition-colors duration-500"
          />

          {/* Authentic Clipped Dot Matrix */}
          <g className="dot-matrix">
            {INDIA_DOT_MATRIX.map((dot) => {
              // Check proximity to active city for subtle interactive reactive glow
              const distToActive = activeCityPoint
                ? Math.hypot(dot.x - activeCityPoint.x, dot.y - activeCityPoint.y)
                : 999;
              const isNearby = distToActive < 35;

              return (
                <circle
                  key={dot.id}
                  cx={dot.x}
                  cy={dot.y}
                  r={isNearby ? 1.6 : 1.3}
                  fill={isNearby ? "rgba(52, 211, 153, 0.75)" : "rgba(16, 185, 129, 0.35)"}
                  className="transition-colors duration-300"
                />
              );
            })}
          </g>

          {/* Connecting Line to Active Floating Card */}
          {activeCityPoint && (
            <path
              d={`M ${activeCityPoint.x} ${activeCityPoint.y} L ${
                isRightSide ? cardX + 170 : cardX
              } ${cardY + 30}`}
              stroke="rgba(52, 211, 153, 0.4)"
              strokeWidth="1.2"
              strokeDasharray="3 3"
              fill="none"
              className="pointer-events-none transition-all duration-300"
            />
          )}

          {/* Real Verified Case Markers */}
          {cases.map((c) => {
            const pt = CITY_GEOPOINTS[c.city];
            if (!pt) return null;

            const isActive = c.id === displayCase?.id;
            const isRedPin = c.city === "New Delhi" || c.city === "Pune";

            const pinColor = isRedPin ? "#ef4444" : "#10b981";
            const pingColor = isRedPin ? "stroke-red-500" : "stroke-emerald-400";

            return (
              <g
                key={c.id}
                className="cursor-pointer group"
                onClick={() => onSelectCase(c.id)}
                onMouseEnter={() => setHoveredCaseId(c.id)}
                onMouseLeave={() => setHoveredCaseId(null)}
              >
                {/* Radar ripple for active pin */}
                {isActive && (
                  <>
                    <circle
                      cx={pt.x}
                      cy={pt.y}
                      r={14}
                      fill="none"
                      stroke={pinColor}
                      strokeWidth="1.5"
                      className="animate-ping opacity-75 origin-center"
                    />
                    <circle
                      cx={pt.x}
                      cy={pt.y}
                      r={10}
                      fill={pinColor}
                      fillOpacity="0.2"
                    />
                  </>
                )}

                {/* Outer halo */}
                <circle
                  cx={pt.x}
                  cy={pt.y}
                  r={isActive ? 7 : 5}
                  fill={pinColor}
                  fillOpacity={isActive ? "0.9" : "0.75"}
                  filter="url(#pinGlow)"
                  className="transition-all duration-200"
                />

                {/* Inner White Core Dot */}
                <circle
                  cx={pt.x}
                  cy={pt.y}
                  r={isActive ? 2.5 : 1.8}
                  fill="#ffffff"
                  className="transition-all duration-200"
                />
              </g>
            );
          })}
        </svg>

        {/* Floating Callout Card Attached to Active Pin */}
        {displayCase && activeCityPoint && (
          <div
            style={{
              position: "absolute",
              left: `${(cardX / 440) * 100}%`,
              top: `${(cardY / 500) * 100}%`,
              transform: "translate(0, 0)",
            }}
            className="w-44 rounded-xl border border-emerald-500/40 bg-[#06111E]/95 p-3 shadow-[0_8px_32px_rgba(0,0,0,0.8)] backdrop-blur-md text-left z-20 pointer-events-auto transition-all duration-300"
          >
            <div className="text-white font-bold text-xs tracking-wide">
              {displayCase.city}
            </div>
            <div className="text-slate-300 text-[11px] leading-tight mt-0.5 line-clamp-2">
              {displayCase.scamCategory}
            </div>
            <button
              type="button"
              onClick={() => onSelectCase(displayCase.id)}
              className="mt-2 text-emerald-400 hover:text-emerald-300 text-[11px] font-semibold flex items-center gap-1 transition-colors"
            >
              <span>View Case</span>
              <ArrowRight className="h-3 w-3" />
            </button>
          </div>
        )}
      </div>

      {/* Trust Indicator Footer */}
      <div className="mt-4 flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-950/40 px-3.5 py-1 text-xs text-emerald-300 shadow-sm">
        <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
        <span>Published-source stories; not independently verified by VeriSight</span>
      </div>
    </div>
  );
};
