import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";
import type { ReactNode } from "react";
import styles from "./layout.module.css";

export default async function DashboardLayout({
  children,
}: {
  children: ReactNode;
}) {
  const { userId } = auth();
  if (!userId) redirect("/sign-in");

  return (
    <div className={styles.shell}>
      <aside className={styles.sidebar}>
        <div className={styles.logo}>
          <span className={styles.logoMark}>⬡</span>
          <span className={styles.logoText}>Agency SaaS</span>
        </div>
        <nav className={styles.nav}>
          <a href="/dashboard" className={styles.navItem} id="nav-dashboard">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" />
              <rect x="14" y="14" width="7" height="7" /><rect x="3" y="14" width="7" height="7" />
            </svg>
            Dashboard
          </a>
        </nav>
      </aside>
      <main className={styles.main}>{children}</main>
    </div>
  );
}
