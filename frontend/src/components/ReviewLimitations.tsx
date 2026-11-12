import React from "react";

/** Shared explanation beside a result or before a screenshot is submitted. */
export function ReviewLimitations({ verdict }: { verdict?: string }) {
  const hasResult = verdict !== undefined;
  return (
    <section aria-label={hasResult ? "How to interpret this result" : "Before submitting a screenshot"}
      className="rounded-lg border border-amber-400/30 bg-amber-950/20 px-3 py-2 text-xs leading-relaxed text-amber-100 print:border-gray-400 print:bg-white print:text-black">
      <p className="font-semibold">Private development prototype · authenticity not verified</p>
      {hasResult ? (
        <p className="mt-1">
          {verdict === "INCONCLUSIVE"
            ? "Likely accurate means no strong configured cue was found. Edited screenshots can still receive this result."
            : "Likely misleading means review is needed. Benign screenshots can also trigger these cues."}
          {" "}The score is review priority, not a probability of fraud. Real-world detection accuracy is not established.
        </p>
      ) : (
        <p className="mt-1">Upload only screenshots you are authorized to use. Analysis may create private previews with 10-minute links; summary saving is opt-in and each result shows its save status. The checks can miss edits or flag benign images; neither verdict verifies authenticity.</p>
      )}
      {hasResult ? (
        <p className="mt-1">Analysis may create private preview files on this server; their links expire after 10 minutes. Re-run the analysis if an image is unavailable.</p>
      ) : (
        <p className="mt-1">Supported screenshots: up to 20 MiB, 2 megapixels and 3200 pixels per side. This private server processes up to two analyses at once; public or multi-instance use is not supported.</p>
      )}
      <p className="mt-1">Do not release money or goods based on this result. Payment settlement requires an authorized bank or PSP transaction-status check.</p>
    </section>
  );
}
