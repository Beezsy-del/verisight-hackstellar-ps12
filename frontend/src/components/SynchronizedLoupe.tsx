import React from "react";
import { ZoomIn, Crosshair } from "lucide-react";

interface SynchronizedLoupeProps {
  visible: boolean;
  x: number; // percentage (0 - 100)
  y: number; // percentage (0 - 100)
  originalImgSrc: string;
  spectralImgSrc?: string;
  spectralLabel?: string;
  imgWidth: number;
  imgHeight: number;
}

export const SynchronizedLoupe: React.FC<SynchronizedLoupeProps> = ({
  visible,
  x,
  y,
  originalImgSrc,
  spectralImgSrc,
  spectralLabel = "Forensic Spectral Layer",
  imgWidth,
  imgHeight,
}) => {
  if (!visible) return null;

  const actualX = Math.round((x / 100) * imgWidth);
  const actualY = Math.round((y / 100) * imgHeight);

  // Loupe diameter
  const size = 150;
  const zoomFactor = 3.0;

  return (
    <div
      className="absolute bottom-4 right-4 z-30 bg-[#070b14]/95 border border-[#334155] rounded-xl p-3 shadow-2xl backdrop-blur flex flex-col space-y-2 pointer-events-none"
      style={{ width: size * 2 + 32, maxWidth: "calc(100% - 16px)" }}
    >
      <div className="flex items-center justify-between border-b border-[#1e293b] pb-1.5 text-[11px] font-mono text-[#94a3b8]">
        <div className="flex items-center space-x-1.5 text-sky-400">
          <ZoomIn className="w-3.5 h-3.5" />
          <span className="font-semibold tracking-wide">
            3X SYNCHRONIZED LOUPE
          </span>
        </div>
        <div className="flex items-center space-x-1 text-[#64748b]">
          <Crosshair className="w-3 h-3 text-sky-400" />
          <span>
            X: {actualX}px | Y: {actualY}px
          </span>
        </div>
      </div>

      <div className="flex items-center space-x-2">
        {/* Loupe 1: Original */}
        <div className="flex flex-col items-center">
          <span className="text-[10px] font-mono text-[#64748b] mb-1">
            ORIGINAL SCREENSHOT
          </span>
          <div
            className="rounded-lg border border-[#38bdf8]/40 overflow-hidden relative shadow-inner"
            style={{
              width: size,
              height: size,
              backgroundImage: `url(${originalImgSrc})`,
              backgroundPosition: `${size/2 - actualX * zoomFactor}px ${size/2 - actualY * zoomFactor}px`,
              backgroundSize: `${imgWidth * zoomFactor}px ${imgHeight * zoomFactor}px`,
              backgroundRepeat: "no-repeat",
            }}
          >
            {/* Center Crosshair */}
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="w-full h-[1px] bg-sky-400/40" />
              <div className="h-full w-[1px] bg-sky-400/40 absolute" />
              <div className="w-3 h-3 rounded-full border border-sky-400/60 absolute" />
            </div>
          </div>
        </div>

        {/* Loupe 2: Active Spectral Layer */}
        {spectralImgSrc && (
          <div className="flex flex-col items-center">
            <span className="text-[10px] font-mono text-[#64748b] mb-1 truncate max-w-[150px]">
              {spectralLabel.toUpperCase()}
            </span>
            <div
              className="rounded-lg border border-[#f43f5e]/40 overflow-hidden relative shadow-inner"
              style={{
                width: size,
                height: size,
                backgroundImage: `url(${spectralImgSrc})`,
                backgroundPosition: `${size/2 - actualX * zoomFactor}px ${size/2 - actualY * zoomFactor}px`,
                backgroundSize: `${imgWidth * zoomFactor}px ${imgHeight * zoomFactor}px`,
                backgroundRepeat: "no-repeat",
              }}
            >
              {/* Center Crosshair */}
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div className="w-full h-[1px] bg-rose-400/40" />
                <div className="h-full w-[1px] bg-rose-400/40 absolute" />
                <div className="w-3 h-3 rounded-full border border-rose-400/60 absolute" />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
