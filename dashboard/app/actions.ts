"use server";

import { revalidatePath } from "next/cache";
import { istToday, upsert } from "@/lib/db";

async function setControl(key: string, value: unknown, message: string) {
  const now = new Date().toISOString();
  await upsert("control", { key, value, updated_at: now });
  await upsert("events", { id: crypto.randomUUID(), created_at: now, kind: "dashboard", message, data: { key, value } });
  revalidatePath("/");
}

export async function engageKillSwitch() {
  await setControl("kill_switch", true, "kill switch engaged from dashboard");
}

export async function releaseKillSwitch() {
  await setControl("kill_switch", false, "kill switch released from dashboard");
}

export async function pauseEntries() {
  await setControl("paused", true, "new entries paused from dashboard");
}

export async function resumeEntries() {
  await setControl("paused", false, "new entries resumed from dashboard");
}

export async function confirmLogin() {
  const today = istToday();
  await setControl("login_confirmed_for", today, `operator confirmed broker login for ${today}`);
}
