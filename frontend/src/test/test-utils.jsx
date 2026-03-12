import React from "react";
import { render as rtlRender } from "@testing-library/react";

// Simple wrapper for tests - no complex providers needed for demo
function render(ui, options = {}) {
  return rtlRender(ui, {
    // Add any global providers here if needed
    wrapper: ({ children }) => <div data-testid="test-wrapper">{children}</div>,
    ...options,
  });
}

// Re-export everything
export * from "@testing-library/react";
export { render };
