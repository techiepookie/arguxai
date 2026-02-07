import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

/**
 * ArguxAI Convex Database Schema
 * 
 * This schema defines the structure for storing user events,
 * issues, and diagnostic data for conversion optimization.
 */

export default defineSchema({
    // Events table - stores all user interaction events
    events: defineTable({
        // Event identification
        event_type: v.string(),
        session_id: v.string(),
        user_id: v.optional(v.string()),

        // Timing
        timestamp: v.number(), // Unix timestamp in milliseconds

        // Funnel context
        funnel_step: v.optional(v.string()),
        device_type: v.string(),
        country: v.string(),
        app_version: v.string(),

        // Error tracking (optional)
        error_type: v.optional(v.string()),
        error_message: v.optional(v.string()),

        // Custom properties (stored as JSON)
        properties: v.optional(v.any()),

        // Metadata
        created_at: v.number(), // When the event was stored
    })
        .index("by_timestamp", ["timestamp"])
        .index("by_session", ["session_id"])
        .index("by_funnel_step", ["funnel_step"])
        .index("by_user", ["user_id"])
        .index("by_funnel_and_time", ["funnel_step", "timestamp"]),

    // Issues table - stores detected anomalies
    issues: defineTable({
        issue_id: v.string(),
        funnel_step: v.string(),
        detected_at: v.number(),

        // Anomaly details
        current_conversion_rate: v.number(),
        baseline_conversion_rate: v.number(),
        drop_percentage: v.number(),
        sigma_value: v.number(),
        is_significant: v.boolean(),

        // Sample sizes
        current_sessions: v.number(),
        baseline_sessions: v.number(),

        // Status
        status: v.string(), // "detected", "diagnosed", "resolved"
        severity: v.string(), // "low", "medium", "high", "critical"

        // Diagnosis (optional, filled after AI analysis)
        diagnosis: v.optional(v.any()),

        // Integration tracking
        jira_ticket: v.optional(v.any()),
        github_pr: v.optional(v.any()),

        // Timestamps
        updated_at: v.number(),
    })
        .index("by_funnel_step", ["funnel_step"])
        .index("by_status", ["status"])
        .index("by_detected_at", ["detected_at"]),
});
