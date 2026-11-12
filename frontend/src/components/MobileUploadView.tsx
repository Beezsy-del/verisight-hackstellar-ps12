import { ReviewLimitations } from "./ReviewLimitations";
import React, { useState, useRef } from "react";
import {
  Camera,
  Upload,
  CheckCircle2,
  ShieldAlert,
  Loader2,
  ArrowRight,
} from "lucide-react";
import { uploadMobile } from "../services/api";

export const MobileUploadView: React.FC = () => {
  const sessionId = new URLSearchParams(window.location.search).get("session_id");
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploaded, setUploaded] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;

    setIsUploading(true);
    setErrorMsg(null);

    try {
      if (!sessionId) throw new Error("Open this page from the desktop workbench QR code to link your upload.");
      await uploadMobile(file, sessionId);
      setUploaded(true);
    } catch (err: any) {
      setErrorMsg(err.message || "Upload failed. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#070b14] text-[#f1f5f9] flex flex-col items-center justify-between p-6">
      {/* Mobile Top Header */}
      <div className="w-full flex items-center justify-between border-b border-[#1e293b] pb-4">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-sky-500 to-indigo-600 flex items-center justify-center">
            <ShieldAlert className="w-4 h-4 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-sm tracking-wide bg-gradient-to-r from-sky-400 to-purple-400 bg-clip-text text-transparent">
              VERISIGHT
            </h1>
            <span className="text-[10px] font-mono text-[#64748b]">
              JUDGE LIVE UPLOAD PORTAL
            </span>
          </div>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">
          CONNECTED
        </span>
      </div>

      {/* Main Upload Body */}
      <div className="w-full max-w-sm flex-1 flex flex-col items-center justify-center my-8 text-center space-y-6">
        {uploaded ? (
          <div className="space-y-4 animate-fade-in">
            <div className="w-16 h-16 rounded-full bg-emerald-950 border-2 border-emerald-500 flex items-center justify-center mx-auto shadow-xl shadow-emerald-500/20">
              <CheckCircle2 className="w-8 h-8 text-emerald-400" />
            </div>
            <div className="space-y-1">
              <h2 className="text-lg font-bold text-emerald-300">
                Evidence Transmitted!
              </h2>
              <p className="text-xs text-[#94a3b8] max-w-xs mx-auto">
                Your screenshot was securely queued for the paired desktop
                workbench. Switch back there to view its 4-layer investigation.
              </p>
            </div>
            <button
              onClick={() => {
                setUploaded(false);
                if (fileInputRef.current) fileInputRef.current.value = "";
              }}
              className="mt-4 px-4 py-2 rounded-xl bg-[#1e293b] text-xs font-semibold text-[#f1f5f9] hover:bg-[#334155] transition-all inline-flex items-center space-x-2"
            >
              <span>Upload Another Screenshot</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        ) : (
          <div className="space-y-6 w-full">
            <div className="space-y-2">
              <h2 className="text-xl font-bold tracking-tight text-[#f1f5f9]">
                Live Stage Judge Capture
              </h2>
              <p className="text-xs text-[#94a3b8] leading-relaxed">
                Take a photo or choose any digital payment screenshot from your
                phone to run real-time forensic tamper analysis on the stage
                screen.
              </p>
            </div>

            <ReviewLimitations />

            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFile}
              accept="image/png,image/jpeg,image/webp,image/bmp,.png,.jpg,.jpeg,.webp,.bmp"
              className="hidden"
            />

            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading || !sessionId}
              className="w-full py-4 rounded-2xl bg-gradient-to-r from-sky-600 via-indigo-600 to-purple-600 hover:from-sky-500 hover:to-purple-500 font-bold text-sm text-white shadow-xl shadow-indigo-600/30 transition-all flex flex-col items-center justify-center space-y-2 active:scale-95 disabled:opacity-50"
            >
              {isUploading ? (
                <>
                  <Loader2 className="w-7 h-7 animate-spin text-white" />
                  <span className="font-mono text-xs">
                    TRANSMITTING EVIDENCE PAYLOAD...
                  </span>
                </>
              ) : (
                <>
                  <Camera className="w-8 h-8 text-white" />
                  <span>SNAP OR CHOOSE SCREENSHOT</span>
                  <span className="text-[10px] font-normal text-sky-200">
                    iOS & Android Camera Ready
                  </span>
                </>
              )}
            </button>

            {!sessionId && (
              <p className="text-xs text-amber-300 bg-amber-950/40 p-2.5 rounded-lg border border-amber-800">
                Open this page by scanning the QR code in the desktop workbench so your upload can be linked to that session.
              </p>
            )}

            {errorMsg && (
              <p className="text-xs text-rose-400 bg-rose-950/40 p-2.5 rounded-lg border border-rose-800">
                {errorMsg}
              </p>
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="w-full border-t border-[#1e293b] pt-3 text-center text-[10px] font-mono text-[#64748b]">
        VeriSight Forensics Engine // HackStellar Problem Statement 12
      </div>
    </div>
  );
};
