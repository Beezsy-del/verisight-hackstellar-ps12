/** Only a failed private preview belonging to the active report affects its viewer. */
export function isReportPreviewFailure(tagName: string, src: string | null, previewSources: string[]): boolean {
  return tagName.toUpperCase() === "IMG" && !!src && src.startsWith("/api/artifacts/") && previewSources.includes(src);
}
