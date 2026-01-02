import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { format, formatDistanceToNow, isPast, isToday, isTomorrow } from "date-fns";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string | Date): string {
  const dateObj = typeof date === "string" ? new Date(date) : date;

  if (isToday(dateObj)) {
    return `Today at ${format(dateObj, "h:mm a")}`;
  }

  if (isTomorrow(dateObj)) {
    return `Tomorrow at ${format(dateObj, "h:mm a")}`;
  }

  return format(dateObj, "MMM d, yyyy 'at' h:mm a");
}

export function calculateCountdown(dueDate: string | Date): string {
  const dateObj = typeof dueDate === "string" ? new Date(dueDate) : dueDate;

  if (isPast(dateObj)) {
    return `Overdue by ${formatDistanceToNow(dateObj)}`;
  }

  return `Due in ${formatDistanceToNow(dateObj)}`;
}

export function normalizeTags(tags: string[]): string[] {
  return tags
    .map((tag) => tag.toLowerCase().trim())
    .filter((tag) => /^[a-z0-9-_]+$/i.test(tag))
    .filter((tag, index, self) => self.indexOf(tag) === index) // Remove duplicates
    .slice(0, 10); // Max 10 tags
}

export function getPriorityColor(priority: string): string {
  switch (priority) {
    case "high":
      return "priority-high";
    case "medium":
      return "priority-medium";
    case "low":
      return "priority-low";
    default:
      return "priority-none";
  }
}

export function getPriorityEmoji(priority: string): string {
  switch (priority) {
    case "high":
      return "🔴";
    case "medium":
      return "🟡";
    case "low":
      return "🔵";
    default:
      return "⚪";
  }
}

export function getRecurrenceBadge(recurrence: any): string {
  if (!recurrence) return "";

  switch (recurrence.type) {
    case "daily":
      return "🔄 Daily";
    case "weekly":
      const days = recurrence.days?.map((d: number) => ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][d - 1]).join(", ");
      return `🔄 Weekly ${days ? `(${days})` : ""}`;
    case "monthly":
      return "🔄 Monthly";
    default:
      return "";
  }
}
