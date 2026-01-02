"use client";

import { Priority } from "@/types/api";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/Select";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Filter, X, SortAsc } from "lucide-react";

export interface FilterState {
  status: "all" | "pending" | "completed";
  priority: Priority | "all";
  tag: string;
  sort: "created_at" | "title" | "priority" | "due_date";
  order: "asc" | "desc";
}

interface FilterPanelProps {
  filters: FilterState;
  onChange: (filters: Partial<FilterState>) => void;
  onReset: () => void;
  availableTags?: string[];
}

export function FilterPanel({
  filters,
  onChange,
  onReset,
  availableTags = [],
}: FilterPanelProps) {
  const hasActiveFilters =
    filters.status !== "all" ||
    filters.priority !== "all" ||
    filters.tag !== "" ||
    filters.sort !== "created_at" ||
    filters.order !== "desc";

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium flex items-center gap-2">
          <Filter className="h-4 w-4" />
          Filters & Sort
        </h3>
        {hasActiveFilters && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onReset}
            className="h-8 text-xs"
          >
            <X className="h-3 w-3 mr-1" />
            Clear All
          </Button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
        {/* Status Filter */}
        <div className="space-y-1.5">
          <label className="text-xs text-muted-foreground">Status</label>
          <Select
            value={filters.status}
            onValueChange={(value) =>
              onChange({ status: value as FilterState["status"] })
            }
          >
            <SelectTrigger className="h-9">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Tasks</SelectItem>
              <SelectItem value="pending">Pending</SelectItem>
              <SelectItem value="completed">Completed</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Priority Filter */}
        <div className="space-y-1.5">
          <label className="text-xs text-muted-foreground">Priority</label>
          <Select
            value={filters.priority}
            onValueChange={(value) =>
              onChange({ priority: value as FilterState["priority"] })
            }
          >
            <SelectTrigger className="h-9">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Priorities</SelectItem>
              <SelectItem value="high">🔴 High</SelectItem>
              <SelectItem value="medium">🟡 Medium</SelectItem>
              <SelectItem value="low">🔵 Low</SelectItem>
              <SelectItem value="none">⚪ None</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Tag Filter */}
        <div className="space-y-1.5">
          <label className="text-xs text-muted-foreground">Tag</label>
          <Select
            value={filters.tag}
            onValueChange={(value) => onChange({ tag: value })}
          >
            <SelectTrigger className="h-9">
              <SelectValue placeholder="All Tags" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Tags</SelectItem>
              {availableTags.map((tag) => (
                <SelectItem key={tag} value={tag}>
                  #{tag}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Sort */}
        <div className="space-y-1.5">
          <label className="text-xs text-muted-foreground flex items-center gap-1">
            <SortAsc className="h-3 w-3" />
            Sort By
          </label>
          <div className="flex gap-2">
            <Select
              value={filters.sort}
              onValueChange={(value) =>
                onChange({ sort: value as FilterState["sort"] })
              }
            >
              <SelectTrigger className="h-9 flex-1">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="created_at">Created Date</SelectItem>
                <SelectItem value="title">Title</SelectItem>
                <SelectItem value="priority">Priority</SelectItem>
                <SelectItem value="due_date">Due Date</SelectItem>
              </SelectContent>
            </Select>
            <Button
              variant="outline"
              size="icon"
              className="h-9 w-9 flex-shrink-0"
              onClick={() =>
                onChange({ order: filters.order === "asc" ? "desc" : "asc" })
              }
            >
              {filters.order === "asc" ? "↑" : "↓"}
            </Button>
          </div>
        </div>
      </div>

      {/* Active Filters Display */}
      {hasActiveFilters && (
        <div className="flex flex-wrap gap-2 pt-2">
          {filters.status !== "all" && (
            <Badge variant="secondary" className="gap-1">
              Status: {filters.status}
              <button
                onClick={() => onChange({ status: "all" })}
                className="hover:bg-destructive/20 rounded-full"
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          )}
          {filters.priority !== "all" && (
            <Badge variant="secondary" className="gap-1">
              Priority: {filters.priority}
              <button
                onClick={() => onChange({ priority: "all" })}
                className="hover:bg-destructive/20 rounded-full"
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          )}
          {filters.tag && (
            <Badge variant="secondary" className="gap-1">
              Tag: #{filters.tag}
              <button
                onClick={() => onChange({ tag: "" })}
                className="hover:bg-destructive/20 rounded-full"
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          )}
        </div>
      )}
    </div>
  );
}
