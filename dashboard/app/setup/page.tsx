import App from "@/components/App";

export const dynamic = "force-dynamic";

export default async function Page({ params }: { params: Promise<{ path?: string[] }> }) {
  const { path } = await params;
  return <App initialPath={["setup", ...(path ?? [])]} />;
}
