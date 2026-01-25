"use client";

import { useState } from "react";
import { Task } from "@/types/api";
import { Badge } from "@/components/ui/Badge";
import { Checkbox } from "@/components/ui/Checkbox";
import { Button } from "@/components/ui/Button";
import {
  formatDate,
  calculateCountdown,
  getPriorityColor,
  getPriorityEmoji,
  getRecurrenceBadge,
} from "@/lib/utils";
import {
  Pencil,
  Trash2,
  Clock,
  Calendar,
  AlertCircle,
  MoreVertical,
} from "lucide-react";
import { cn } from "@/lib/utils";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";

interface TaskCardProps {
  task: Task;
  onToggleComplete?: (taskId: number) => void;
  onEdit?: (task: Task) => void;
  onDelete?: (taskId: number) => void;
}

export function TaskCard({
  task,
  onToggleComplete,
  onEdit,
  onDelete,
}: TaskCardProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [isToggling, setIsToggling] = useState(false);

  const isOverdue = task.due_date && new Date(task.due_date) < new Date() && !task.completed;

  const handleToggleComplete = async () => {
    if (isToggling || !onToggleComplete) return;
    setIsToggling(true);
    try {
      await onToggleComplete(task.id);
    } finally {
      setIsToggling(false);
    }
  };

  const handleDelete = async () => {
    if (!onDelete) return;
    if (window.confirm(`Delete "${task.title}"?`)) {
      setIsDeleting(true);
      try {
        await onDelete(task.id);
      } finally {
        setIsDeleting(false);
      }
    }
  };

  return (
    <div
      className={cn(
        "task-card glass rounded-xl p-4 border",
        isOverdue && "border-red-300 dark:border-red-800",
        task.completed && "opacity-60",
        isDeleting && "opacity-50 pointer-events-none"
      )}
    >
      <div className="flex items-start gap-3">
        {/* Checkbox */}
        <div className="pt-0.5">
          <Checkbox
            checked={task.completed}
            onCheckedChange={handleToggleComplete}
            disabled={isToggling}
            className={cn(
              "transition-all",
              task.completed && "bg-green-500 border-green-500"
            )}
          />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0 space-y-2">
          {/* Title and Actions */}
          <div className="flex items-start justify-between gap-2">
            <h3
              className={cn(
                "text-base font-semibold leading-tight break-words",
                task.completed && "line-through text-muted-foreground"
              )}
            >
              {task.title}
            </h3>

            {/* Actions Dropdown */}
            <DropdownMenu.Root>
              <DropdownMenu.Trigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 flex-shrink-0"
                >
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenu.Trigger>
              <DropdownMenu.Portal>
                <DropdownMenu.Content
                  className="z-50 min-w-[160px] overflow-hidden rounded-md border bg-popover p-1 text-popover-foreground shadow-md animate-in fade-in-80 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2"
                  sideOffset={5}
                >
                  <DropdownMenu.Item
                    className="relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50"
                    onSelect={() => onEdit?.(task)}
                  >
                    <Pencil className="mr-2 h-4 w-4" />
                    <span>Edit</span>
                  </DropdownMenu.Item>
                  <DropdownMenu.Item
                    className="relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-destructive hover:text-destructive-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50"
                    onSelect={handleDelete}
                  >
                    <Trash2 className="mr-2 h-4 w-4" />
                    <span>Delete</span>
                  </DropdownMenu.Item>
                </DropdownMenu.Content>
              </DropdownMenu.Portal>
            </DropdownMenu.Root>
          </div>

          {/* Description */}
          {task.description && (
            <p
              className={cn(
                "text-sm text-muted-foreground line-clamp-2",
                task.completed && "line-through"
              )}
            >
              {task.description}
            </p>
          )}

          {/* Badges and Meta */}
          <div className="flex flex-wrap items-center gap-2 text-xs">
            {/* Priority */}
            <Badge variant={task.priority as any} className="gap-1">
              <span>{getPriorityEmoji(task.priority)}</span>
              <span className="capitalize">{task.priority}</span>
            </Badge>

            {/* Tags */}
            {task.tags.map((tag) => (
              <Badge key={tag} variant="secondary" className="gap-1">
                <span>#</span>
                {tag}
              </Badge>
            ))}

            {/* Recurrence */}
            {task.recurrence && (
              <Badge variant="outline" className="gap-1">
                {getRecurrenceBadge(task.recurrence)}
              </Badge>
            )}

            {/* Due Date */}
            {task.due_date && (
              <Badge
                variant={isOverdue ? "destructive" : "outline"}
                className="gap-1"
              >
                {isOverdue && <AlertCircle className="h-3 w-3" />}
                <Clock className="h-3 w-3" />
                <span>{calculateCountdown(task.due_date)}</span>
              </Badge>
            )}

            {/* Created Date */}
            <span className="text-muted-foreground flex items-center gap-1">
              <Calendar className="h-3 w-3" />
              {formatDate(task.created_at)}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
