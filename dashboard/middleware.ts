import { NextResponse, type NextRequest } from "next/server";

// The dashboard can start and stop trading, so it must never be public.
// HTTP Basic Auth on every path, failing closed when unconfigured.
export function middleware(req: NextRequest) {
  const user = process.env.DASHBOARD_USER;
  const pass = process.env.DASHBOARD_PASSWORD;
  if (!user || !pass) {
    return new NextResponse("Dashboard auth is not configured (set DASHBOARD_USER and DASHBOARD_PASSWORD).", {
      status: 503,
    });
  }
  const header = req.headers.get("authorization") ?? "";
  // Schedulers (Vercel Cron, Supabase pg_cron) cannot answer a Basic Auth prompt. They reach the
  // worker function, and only it, with the shared cron secret; the function checks it again.
  const cron = process.env.CRON_SECRET;
  if (cron && req.nextUrl.pathname === "/api/worker" && header.startsWith("Bearer ") && timingSafeEqual(header.slice(7), cron)) {
    return NextResponse.next();
  }
  if (header.startsWith("Basic ")) {
    try {
      const [u, ...rest] = atob(header.slice(6)).split(":");
      if (timingSafeEqual(u, user) && timingSafeEqual(rest.join(":"), pass)) {
        return NextResponse.next();
      }
    } catch {
      // fall through to challenge
    }
  }
  return new NextResponse("Authentication required", {
    status: 401,
    headers: { "WWW-Authenticate": 'Basic realm="thunderbot", charset="UTF-8"' },
  });
}

function timingSafeEqual(a: string, b: string): boolean {
  let diff = a.length ^ b.length;
  for (let i = 0; i < Math.max(a.length, b.length); i++) {
    diff |= (a.charCodeAt(i) || 0) ^ (b.charCodeAt(i) || 0);
  }
  return diff === 0;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
