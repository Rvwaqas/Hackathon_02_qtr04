"use client";

import { useState, useEffect } from "react";
import { Task, TaskInput } from "@/types/api";
import { Button } from "@/components/ui/Button";
import { TaskList } from "@/components/tasks/TaskList";
import { TaskForm } from "@/components/tasks/TaskForm";
import { SearchBar } from "@/components/tasks/SearchBar";
import { FilterPanel, FilterState } from "@/components/tasks/FilterPanel";
import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalTitle,
  ModalDescription,
} from "@/components/ui/Modal";
import {
  Plus,
  CheckCircle2,
  LogOut,
  Bell,
  Menu,
  X,
  Sparkles,
} from "lucide-react";
import { useRouter } from "next/navigation";
import { tasksApi, authApi, getAuthToken } from "@/lib/api";

// Mock data for development
const mockTasks: Task[] = [
  {
    id: 1,
    user_id: "user1",
    title: "Complete project documentation",
    description: "Write comprehensive documentation for the new features",
    completed: false,
    priority: "high",
    tags: ["work", "documentation"],
    due_date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(),
    reminder_offset_minutes: 60,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 2,
    user_id: "user1",
    title: "Review pull requests",
    description: "Review and merge pending PRs from the team",
    completed: false,
    priority: "medium",
    tags: ["work", "code-review"],
    created_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 3,
    user_id: "user1",
    title: "Buy groceries",
    description: "Milk, eggs, bread, and vegetables",
    completed: true,
    priority: "low",
    tags: ["personal", "shopping"],
    created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
  },
];

export default function DashboardPage() {
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [filteredTasks, setFilteredTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | undefined>();
  const [searchQuery, setSearchQuery] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const [filters, setFilters] = useState<FilterState>({
    status: "all",
    priority: "all",
    tag: "",
    sort: "created_at",
    order: "desc",
  });

  // Check auth and fetch tasks on mount
  useEffect(() => {
    const token = getAuthToken();
    if (!token) {
      router.push("/signin");
      return;
    }

    fetchTasks();
  }, []);

  // Fetch all tasks from API
  const fetchTasks = async () => {
    try {
      const data = await tasksApi.getAll();
      setTasks(data);
    } catch (error) {
      console.error("Failed to fetch tasks:", error);
    }
  };

  // Get unique tags from all tasks
  const availableTags = Array.from(
    new Set(tasks.flatMap((task) => task.tags))
  ).sort();

  // Apply filters and search
  useEffect(() => {
    let result = [...tasks];

    // Search
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(
        (task) =>
          task.title.toLowerCase().includes(query) ||
          task.description?.toLowerCase().includes(query)
      );
    }

    // Status filter
    if (filters.status !== "all") {
      result = result.filter((task) =>
        filters.status === "completed" ? task.completed : !task.completed
      );
    }

    // Priority filter
    if (filters.priority !== "all") {
      result = result.filter((task) => task.priority === filters.priority);
    }

    // Tag filter
    if (filters.tag) {
      result = result.filter((task) => task.tags.includes(filters.tag));
    }

    // Sort
    result.sort((a, b) => {
      let aVal, bVal;

      switch (filters.sort) {
        case "title":
          aVal = a.title.toLowerCase();
          bVal = b.title.toLowerCase();
          break;
        case "priority":
          const priorityOrder = { high: 3, medium: 2, low: 1, none: 0 };
          aVal = priorityOrder[a.priority];
          bVal = priorityOrder[b.priority];
          break;
        case "due_date":
          aVal = a.due_date ? new Date(a.due_date).getTime() : 0;
          bVal = b.due_date ? new Date(b.due_date).getTime() : 0;
          break;
        default:
          aVal = new Date(a.created_at).getTime();
          bVal = new Date(b.created_at).getTime();
      }

      if (aVal < bVal) return filters.order === "asc" ? -1 : 1;
      if (aVal > bVal) return filters.order === "asc" ? 1 : -1;
      return 0;
    });

    setFilteredTasks(result);
  }, [tasks, searchQuery, filters]);

  const handleCreateTask = async (data: TaskInput) => {
    setLoading(true);
    try {
      const newTask = await tasksApi.create(data);
      setTasks([newTask, ...tasks]);
      setIsModalOpen(false);
    } catch (error) {
      console.error("Failed to create task:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateTask = async (data: TaskInput) => {
    if (!editingTask) return;
    setLoading(true);
    try {
      const updatedTask = await tasksApi.update(editingTask.id, data);
      setTasks(tasks.map((t) => (t.id === editingTask.id ? updatedTask : t)));
      setEditingTask(undefined);
      setIsModalOpen(false);
    } catch (error) {
      console.error("Failed to update task:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleComplete = async (taskId: number) => {
    try {
      const result = await tasksApi.toggleComplete(taskId);
      setTasks(
        tasks.map((t) =>
          t.id === taskId ? result.current_task : t
        )
      );
      // If there's a next recurring task, add it
      if (result.next_task) {
        setTasks([result.next_task, ...tasks]);
      }
    } catch (error) {
      console.error("Failed to toggle task:", error);
    }
  };

  const handleDeleteTask = async (taskId: number) => {
    try {
      await tasksApi.delete(taskId);
      setTasks(tasks.filter((t) => t.id !== taskId));
    } catch (error) {
      console.error("Failed to delete task:", error);
    }
  };

  const handleEditTask = (task: Task) => {
    setEditingTask(task);
    setIsModalOpen(true);
  };

  const handleSignOut = async () => {
    await authApi.signout();
  };

  const taskStats = {
    total: tasks.length,
    completed: tasks.filter((t) => t.completed).length,
    pending: tasks.filter((t) => !t.completed).length,
    overdue: tasks.filter(
      (t) =>
        !t.completed &&
        t.due_date &&
        new Date(t.due_date) < new Date()
    ).length,
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-pink-50 dark:from-gray-900 dark:via-purple-900 dark:to-blue-900">
      {/* Header */}
      <header className="glass border-b border-white/20 sticky top-0 z-40">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden"
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              {sidebarOpen ? <X /> : <Menu />}
            </Button>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-6 w-6 text-primary" />
              <span className="text-xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                TaskFlow
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="h-5 w-5" />
              {taskStats.overdue > 0 && (
                <span className="absolute -top-1 -right-1 h-5 w-5 bg-destructive text-destructive-foreground text-xs rounded-full flex items-center justify-center">
                  {taskStats.overdue}
                </span>
              )}
            </Button>
            <Button variant="ghost" onClick={handleSignOut}>
              <LogOut className="h-4 w-4 mr-2" />
              Sign Out
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <aside
            className={cn(
              "lg:col-span-1 space-y-6",
              sidebarOpen ? "block" : "hidden lg:block"
            )}
          >
            {/* Stats Cards */}
            <div className="space-y-3">
              <div className="glass rounded-xl p-4 space-y-1">
                <p className="text-sm text-muted-foreground">Total Tasks</p>
                <p className="text-3xl font-bold">{taskStats.total}</p>
              </div>
              <div className="glass rounded-xl p-4 space-y-1">
                <p className="text-sm text-muted-foreground">Completed</p>
                <p className="text-3xl font-bold text-green-600">
                  {taskStats.completed}
                </p>
              </div>
              <div className="glass rounded-xl p-4 space-y-1">
                <p className="text-sm text-muted-foreground">Pending</p>
                <p className="text-3xl font-bold text-blue-600">
                  {taskStats.pending}
                </p>
              </div>
              {taskStats.overdue > 0 && (
                <div className="glass rounded-xl p-4 space-y-1 border-2 border-destructive/50">
                  <p className="text-sm text-muted-foreground">Overdue</p>
                  <p className="text-3xl font-bold text-destructive">
                    {taskStats.overdue}
                  </p>
                </div>
              )}
            </div>

            {/* Quick Actions */}
            <div className="glass rounded-xl p-4 space-y-3">
              <h3 className="font-semibold flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-primary" />
                Quick Actions
              </h3>
              <Button
                variant="gradient"
                className="w-full"
                onClick={() => {
                  setEditingTask(undefined);
                  setIsModalOpen(true);
                }}
              >
                <Plus className="h-4 w-4 mr-2" />
                New Task
              </Button>
            </div>
          </aside>

          {/* Main Area */}
          <main className="lg:col-span-3 space-y-6">
            {/* Welcome Banner */}
            <div className="glass rounded-2xl p-6 gradient-purple text-white">
              <h1 className="text-3xl font-bold mb-2">
                Welcome back! 👋
              </h1>
              <p className="text-white/90">
                You have {taskStats.pending} pending tasks.{" "}
                {taskStats.overdue > 0 && (
                  <span className="font-semibold">
                    {taskStats.overdue} are overdue!
                  </span>
                )}
              </p>
            </div>

            {/* Search */}
            <SearchBar value={searchQuery} onChange={setSearchQuery} />

            {/* Filters */}
            <div className="glass rounded-xl p-4">
              <FilterPanel
                filters={filters}
                onChange={(newFilters) =>
                  setFilters({ ...filters, ...newFilters })
                }
                onReset={() =>
                  setFilters({
                    status: "all",
                    priority: "all",
                    tag: "",
                    sort: "created_at",
                    order: "desc",
                  })
                }
                availableTags={availableTags}
              />
            </div>

            {/* Results Count */}
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">
                {filteredTasks.length} task{filteredTasks.length !== 1 && "s"}{" "}
                {searchQuery && `matching "${searchQuery}"`}
              </p>
            </div>

            {/* Task List */}
            <TaskList
              tasks={filteredTasks}
              loading={loading}
              onToggleComplete={handleToggleComplete}
              onEdit={handleEditTask}
              onDelete={handleDeleteTask}
            />
          </main>
        </div>
      </div>

      {/* Task Modal */}
      <Modal open={isModalOpen} onOpenChange={setIsModalOpen}>
        <ModalContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <ModalHeader>
            <ModalTitle>
              {editingTask ? "Edit Task" : "Create New Task"}
            </ModalTitle>
            <ModalDescription>
              {editingTask
                ? "Update your task details below"
                : "Add a new task to your list"}
            </ModalDescription>
          </ModalHeader>
          <TaskForm
            task={editingTask}
            onSubmit={editingTask ? handleUpdateTask : handleCreateTask}
            onCancel={() => {
              setIsModalOpen(false);
              setEditingTask(undefined);
            }}
            loading={loading}
          />
        </ModalContent>
      </Modal>
    </div>
  );
}

function cn(...classes: any[]) {
  return classes.filter(Boolean).join(" ");
}
