const configuredApiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const apiUrl = configuredApiUrl.replace(/\/$/, "");

export function apiEndpoint(path: string): string {
  return `${apiUrl}${path.startsWith("/") ? path : `/${path}`}`;
}
