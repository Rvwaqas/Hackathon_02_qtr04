'use client';

import React, { createContext, useContext, useEffect } from 'react';

// Define custom event name
const TASK_REFRESH_EVENT = 'taskRefresh';

interface TaskRefreshContextType {
  refreshTasks: () => void;
}

const TaskRefreshContext = createContext<TaskRefreshContextType | undefined>(undefined);

export function TaskRefreshProvider({ children }: { children: React.ReactNode }) {
  // Function to dispatch the refresh event
  const refreshTasks = () => {
    window.dispatchEvent(new CustomEvent(TASK_REFRESH_EVENT));
  };

  return (
    <TaskRefreshContext.Provider value={{ refreshTasks }}>
      {children}
    </TaskRefreshContext.Provider>
  );
}

export function useTaskRefresh() {
  const context = useContext(TaskRefreshContext);
  if (context === undefined) {
    throw new Error('useTaskRefresh must be used within a TaskRefreshProvider');
  }
  return context;
}

// Hook to listen for refresh events
export function useTaskRefreshListener(callback: () => void) {
  useEffect(() => {
    const handleRefresh = () => {
      callback();
    };

    window.addEventListener(TASK_REFRESH_EVENT, handleRefresh);

    return () => {
      window.removeEventListener(TASK_REFRESH_EVENT, handleRefresh);
    };
  }, [callback]);
}