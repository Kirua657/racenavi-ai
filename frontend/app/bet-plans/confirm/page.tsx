import { ConfirmBetPlanClient, type BetPlanRequest } from "./ConfirmBetPlanClient";

type SearchParams = Record<string, string | string[] | undefined>;
type Objective = BetPlanRequest["objective"];
type RiskLevel = BetPlanRequest["riskLevel"];

const OBJECTIVES: Objective[] = ["hit_rate", "balanced", "return"];
const RISK_LEVELS: RiskLevel[] = ["low", "medium", "high"];

function paramValue(params: SearchParams, key: string) {
  const value = params[key];
  return Array.isArray(value) ? value[0] ?? "" : value ?? "";
}

function parseObjective(value: string): Objective {
  return OBJECTIVES.includes(value as Objective) ? (value as Objective) : "balanced";
}

function parseRiskLevel(value: string): RiskLevel {
  return RISK_LEVELS.includes(value as RiskLevel) ? (value as RiskLevel) : "medium";
}

function parseBudget(value: string) {
  const budget = Number(value);
  if (!Number.isFinite(budget)) return 3000;
  return Math.min(Math.max(Math.round(budget), 100), 100000);
}

export default async function ConfirmBetPlanPage({ searchParams }: { searchParams: Promise<SearchParams> }) {
  const params = await searchParams;
  const request: BetPlanRequest = {
    raceId: paramValue(params, "raceId"),
    budget: parseBudget(paramValue(params, "budget")),
    objective: parseObjective(paramValue(params, "objective")),
    riskLevel: parseRiskLevel(paramValue(params, "riskLevel")),
    allowTrifecta: paramValue(params, "allowTrifecta") === "true",
  };

  return <ConfirmBetPlanClient request={request} />;
}