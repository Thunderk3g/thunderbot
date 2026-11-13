import App from "@/components/App";

export const dynamic = "force-dynamic";

// One client shell serves every page, and each has a real address that can be bookmarked and shared:
// /  /portfolio/plan  /lab  /lab/desk  /journal  /journal/<decision id>  /harness  /setup  /guide
// The addresses are listed as explicit routes (not one catch-all at the root) so that nothing here can
// ever sit in front of /api/worker, the Python function that runs the worker.
export default function Page() {
  return <App initialPath={[]} />;
}
