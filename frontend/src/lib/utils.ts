import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatPercentage(value: number): string {
  return `${Math.round(value * 100)}%`;
}

export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(date));
}

export function getMasteryColor(mastery: number): string {
  if (mastery >= 0.85) return "text-accent-600";
  if (mastery >= 0.65) return "text-primary-600";
  if (mastery >= 0.4) return "text-warning-500";
  return "text-danger-500";
}

export function getRiskBadgeColor(tier: string): string {
  switch (tier) {
    case "critical": return "bg-danger-100 text-danger-700";
    case "high": return "bg-warning-100 text-warning-700";
    case "moderate": return "bg-primary-100 text-primary-700";
    case "low": return "bg-accent-100 text-accent-700";
    default: return "bg-gray-100 text-gray-700";
  }
}
