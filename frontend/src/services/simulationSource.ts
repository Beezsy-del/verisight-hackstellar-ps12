/** Prefer uploaded bytes over derived or expiring previews. */
export async function loadSimulationSource(
  source: Blob | null,
  sampleUrl: string | undefined,
  previewUrl: string,
  fetcher: typeof fetch = fetch,
): Promise<Blob> {
  if (source) return source;
  const response = await fetcher(sampleUrl || previewUrl, { credentials: "same-origin", cache: "no-store" });
  if (!response.ok) {
    throw new Error(sampleUrl
      ? "Original sample could not be loaded."
      : "Screenshot preview is unavailable or expired. Re-run the analysis before simulating.");
  }
  return response.blob();
}
