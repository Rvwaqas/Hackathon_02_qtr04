"use client";

import { useState, useEffect } from "react";
import { Task, TaskInput, Priority, RecurrenceType } from "@/types/api";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/Select";
import { normalizeTags } from "@/lib/utils";
import { X, Plus, Calendar, Clock, Repeat } from "lucide-react";

interface TaskFormProps {
  task?: Task;
  onSubmit: (data: TaskInput) => void;
  onCancel: () => void;
  loading?: boolean;
}

export function TaskForm({ task, onSubmit, onCancel, loading }: TaskFormProps) {
  const [formData, setFormData] = useState<TaskInput>({
    title: task?.title || "",
    description: task?.description || "",
    priority: task?.priority || "none",
    tags: task?.tags || [],
    due_date: task?.due_date || null,
    reminder_offset_minutes: task?.reminder_offset_minutes || null,
    recurrence: task?.recurrence || null,
  });

  const [tagInput, setTagInput] = useState("");
  const [showAdvanced, setShowAdvanced] = useState(
    !!(task?.due_date || task?.recurrence)
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const addTag = () => {
    if (!tagInput.trim()) return;
    const newTags = normalizeTags([...formData.tags, tagInput]);
    if (newTags.length <= 10) {
      setFormData({ ...formData, tags: newTags });
      setTagInput("");
    }
  };

  const removeTag = (tagToRemove: string) => {
    setFormData({
      ...formData,
      tags: formData.tags.filter((tag) => tag !== tagToRemove),
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      addTag();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Title */}
      <div className="space-y-2">
        <label htmlFor="title" className="text-sm font-medium">
          Task Title <span className="text-destructive">*</span>
        </label>
        <Input
          id="title"
          type="text"
          placeholder="What needs to be done?"
          value={formData.title}
          onChange={(e) =>
            setFormData({ ...formData, title: e.target.value })
          }
          required
          maxLength={200}
          autoFocus
        />
      </div>

      {/* Description */}
      <div className="space-y-2">
        <label htmlFor="description" className="text-sm font-medium">
          Description
        </label>
        <textarea
          id="description"
          placeholder="Add more details..."
          className="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-none transition-all"
          value={formData.description || ""}
          onChange={(e) =>
            setFormData({ ...formData, description: e.target.value })
          }
          maxLength={2000}
        />
      </div>

      {/* Priority */}
      <div className="space-y-2">
        <label htmlFor="priority" className="text-sm font-medium">
          Priority
        </label>
        <Select
          value={formData.priority}
          onValueChange={(value) =>
            setFormData({ ...formData, priority: value as Priority })
          }
        >
          <SelectTrigger>
            <SelectValue placeholder="Select priority" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="high">🔴 High</SelectItem>
            <SelectItem value="medium">🟡 Medium</SelectItem>
            <SelectItem value="low">🔵 Low</SelectItem>
            <SelectItem value="none">⚪ None</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Tags */}
      <div className="space-y-2">
        <label htmlFor="tags" className="text-sm font-medium">
          Tags {formData.tags.length > 0 && `(${formData.tags.length}/10)`}
        </label>
        <div className="flex gap-2">
          <Input
            id="tags"
            type="text"
            placeholder="Add a tag (alphanumeric only)"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={formData.tags.length >= 10}
          />
          <Button
            type="button"
            variant="outline"
            onClick={addTag}
            disabled={!tagInput.trim() || formData.tags.length >= 10}
          >
            <Plus className="h-4 w-4" />
          </Button>
        </div>
        {formData.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 pt-2">
            {formData.tags.map((tag) => (
              <Badge
                key={tag}
                variant="secondary"
                className="gap-2 pr-1 cursor-pointer hover:bg-secondary/80"
              >
                <span>#{tag}</span>
                <button
                  type="button"
                  onClick={() => removeTag(tag)}
                  className="hover:bg-destructive/20 rounded-full p-0.5"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            ))}
          </div>
        )}
      </div>

      {/* Advanced Options Toggle */}
      <Button
        type="button"
        variant="ghost"
        onClick={() => setShowAdvanced(!showAdvanced)}
        className="w-full"
      >
        <span className="flex items-center gap-2">
          {showAdvanced ? "Hide" : "Show"} Advanced Options
          <span className="text-xs text-muted-foreground">
            (Due Date, Reminders, Recurrence)
          </span>
        </span>
      </Button>

      {/* Advanced Options */}
      {showAdvanced && (
        <div className="space-y-4 p-4 rounded-lg border bg-muted/30">
          {/* Due Date */}
          <div className="space-y-2">
            <label htmlFor="due_date" className="text-sm font-medium flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              Due Date
            </label>
            <Input
              id="due_date"
              type="datetime-local"
              value={formData.due_date || ""}
              onChange={(e) =>
                setFormData({ ...formData, due_date: e.target.value || null })
              }
            />
          </div>

          {/* Reminder */}
          {formData.due_date && (
            <div className="space-y-2">
              <label htmlFor="reminder" className="text-sm font-medium flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Reminder
              </label>
              <Select
                value={formData.reminder_offset_minutes?.toString() || "none"}
                onValueChange={(value) =>
                  setFormData({
                    ...formData,
                    reminder_offset_minutes: (value && value !== "none") ? parseInt(value) : null,
                  })
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="No reminder" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">No reminder</SelectItem>
                  <SelectItem value="5">5 minutes before</SelectItem>
                  <SelectItem value="15">15 minutes before</SelectItem>
                  <SelectItem value="30">30 minutes before</SelectItem>
                  <SelectItem value="60">1 hour before</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}

          {/* Recurrence */}
          <div className="space-y-2">
            <label htmlFor="recurrence" className="text-sm font-medium flex items-center gap-2">
              <Repeat className="h-4 w-4" />
              Recurrence
            </label>
            <Select
              value={formData.recurrence?.type || "none"}
              onValueChange={(value) => {
                if (value === "none" || value === "") {
                  setFormData({ ...formData, recurrence: null });
                } else {
                  setFormData({
                    ...formData,
                    recurrence: {
                      type: value as RecurrenceType,
                      interval: 1,
                    },
                  });
                }
              }}
            >
              <SelectTrigger>
                <SelectValue placeholder="Does not repeat" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">Does not repeat</SelectItem>
                <SelectItem value="daily">Daily</SelectItem>
                <SelectItem value="weekly">Weekly</SelectItem>
                <SelectItem value="monthly">Monthly</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3 pt-4">
        <Button
          type="submit"
          variant="gradient"
          className="flex-1"
          disabled={loading || !formData.title.trim()}
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <span className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Saving...
            </span>
          ) : (
            <span>{task ? "Update Task" : "Create Task"}</span>
          )}
        </Button>
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          disabled={loading}
        >
          Cancel
        </Button>
      </div>
    </form>
  );
}
