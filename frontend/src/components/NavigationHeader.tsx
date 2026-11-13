import React from "react";
import { ShieldCheck } from "lucide-react";
export type AppRoute = "/" | "/workbench" | "/evaluation" | "/why-verisight" | "/response" | "/guide";
interface Props {
  currentRoute: AppRoute;
  onNavigate: (route: AppRoute, query?: Record<string,string>) => void;
  databaseStatus?: "CHECKING" | "HEALTHY" | "UNAVAILABLE" | "NOT_CONFIGURED";
  backendStatus?: "CHECKING" | "HEALTHY" | "UNAVAILABLE" | "DEGRADED";
}
const routes: [AppRoute,string][] = [["/","Product Overview"],["/workbench","Forensic Workbench"],["/evaluation","Evaluation & Research"],["/response","Response & Guidance"],["/guide","Product Guide"]];
export const NavigationHeader: React.FC<Props> = ({currentRoute,onNavigate,databaseStatus="CHECKING",backendStatus="CHECKING"}) => (
  <header className="app-header">
    <button className="brand" onClick={() => onNavigate("/")}><ShieldCheck size={24}/><span>VERISIGHT<small className={backendStatus === "HEALTHY" ? "text-emerald-300" : "text-amber-300"}>API: {backendStatus.toLowerCase()} · Database: {databaseStatus.toLowerCase().replace(/_/g," ")}</small></span></button>
    <nav aria-label="Product navigation" className="product-nav">{routes.map(([route,label]) => <button key={route} aria-current={currentRoute===route ? "page" : undefined} onClick={()=>onNavigate(route)}>{label}</button>)}</nav>
  </header>
);
