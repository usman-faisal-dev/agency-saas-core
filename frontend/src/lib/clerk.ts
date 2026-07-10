/**
 * Clerk re-exports and helpers.
 * Import from here rather than @clerk/nextjs directly — this gives us a
 * single place to swap Clerk or add custom wrappers if needed.
 */
export { useAuth, useUser, useClerk, useSession } from "@clerk/nextjs";
export { auth, currentUser } from "@clerk/nextjs/server";
