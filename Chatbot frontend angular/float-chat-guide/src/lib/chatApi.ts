const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export interface QuestionPayload {
  question: string;
  provider?: string;
  temperature?: number;
  max_tokens?: number;
  top_k?: number;
}

export interface QuestionResponse {
  id: string;
  answer: string;
  context_found?: boolean;
  provider_used?: string;
  model_used?: string;
  response_time_ms?: number;
}

export interface SatisfactionPayload {
  response_id: string;
  is_satisfied: boolean;
}

async function parseError(response: Response): Promise<string> {
  try {
    const data = await response.json();
    if (typeof data?.detail === "string") return data.detail;
    if (Array.isArray(data?.detail)) {
      return data.detail.map((e: { msg?: string }) => e.msg ?? "").join(", ");
    }
  } catch {
    // ignore
  }
  return `Erreur HTTP ${response.status}`;
}

export async function askQuestionUltra(
  question: string
): Promise<QuestionResponse> {
  const payload: QuestionPayload = {
    question,
    top_k: 3,
    temperature: 0.3,
    max_tokens: 512,
  };

  const response = await fetch(`${API_BASE_URL}/ask-question-ultra`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  return response.json();
}

export async function recordSatisfaction(
  payload: SatisfactionPayload
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/record-satisfaction`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(await parseError(response));
  }
}
