import { NextResponse, type NextRequest } from "next/server";

// The dashboard can engage the kill switch and confirm the daily broker login,
// so it must never be public. HTTP Basic Auth fails closed when unconfigured.
export function middleware(req: NextRequest) {
  const user = process.env.DASHBOARD_USER;
  const pass = process.env.DASHBOARD_PASSWORD;
  if (!user || !pass) {
    return new NextResponse("Dashboard auth is not configured (set DASHBOARD_USER and DASHBOARD_PASSWORD).", {
      status: 503,
    });
  }
  const header = req.headers.get("authorization") ?? "";
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
