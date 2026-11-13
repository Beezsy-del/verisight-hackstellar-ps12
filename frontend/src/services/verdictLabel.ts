/** Only these two product labels are displayed. Internal assessment states remain separate. */
export function verdictLabel(verdict: string, _score?: number): string {
  return verdict === "INCONCLUSIVE" ? "Likely accurate" : "Likely misleading";
}
