export async function register() {
  // Node.js 22+ exposes a broken localStorage global (object without working methods)
  // which causes Next.js SSR to crash. Remove it so typeof checks return 'undefined'.
  if (typeof window === "undefined" && typeof localStorage !== "undefined") {
    delete (globalThis as Record<string, unknown>).localStorage;
  }
}
