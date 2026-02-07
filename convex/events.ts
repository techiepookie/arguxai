import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

/**
 * Insert a batch of events
 */
export const insertBatch = mutation({
    args: {
        events: v.array(v.object({
            event_type: v.string(),
            session_id: v.string(),
            user_id: v.optional(v.string()),
            timestamp: v.number(),
            funnel_step: v.optional(v.string()),
            device_type: v.string(),
            country: v.string(),
            app_version: v.string(),
            error_type: v.optional(v.string()),
            error_message: v.optional(v.string()),
            properties: v.optional(v.any()),
        })),
    },
    handler: async (ctx, { events }) => {
        const now = Date.now();
        const ids = [];

        for (const event of events) {
            const id = await ctx.db.insert("events", {
                ...event,
                created_at: now,
            });
            ids.push(id);
        }

        return { insertedCount: ids.length, ids };
    },
});

/**
 * Query events by funnel step and time range
 */
export const queryByFunnelAndTime = query({
    args: {
        funnel_step: v.string(),
        start_time: v.number(),
        end_time: v.number(),
    },
    handler: async (ctx, { funnel_step, start_time, end_time }) => {
        const events = await ctx.db
            .query("events")
            .withIndex("by_funnel_and_time", (q) =>
                q.eq("funnel_step", funnel_step)
            )
            .filter((q) =>
                q.and(
                    q.gte(q.field("timestamp"), start_time),
                    q.lte(q.field("timestamp"), end_time)
                )
            )
            .collect();

        return events;
    },
});

/**
 * Query events in a time range (for metrics calculation)
 */
export const queryByTimeRange = query({
    args: {
        start_time: v.number(),
        end_time: v.number(),
    },
    handler: async (ctx, { start_time, end_time }) => {
        const events = await ctx.db
            .query("events")
            .withIndex("by_timestamp")
            .filter((q) =>
                q.and(
                    q.gte(q.field("timestamp"), start_time),
                    q.lte(q.field("timestamp"), end_time)
                )
            )
            .collect();

        return events;
    },
});

/**
 * Get all events (for debugging)
 */
export const list = query({
    handler: async (ctx) => {
        return await ctx.db.query("events").collect();
    },
});

/**
 * Count events by funnel step
 */
export const countByFunnelStep = query({
    args: {
        funnel_step: v.string(),
        start_time: v.number(),
        end_time: v.number(),
    },
    handler: async (ctx, { funnel_step, start_time, end_time }) => {
        const events = await ctx.db
            .query("events")
            .withIndex("by_funnel_and_time", (q) =>
                q.eq("funnel_step", funnel_step)
            )
            .filter((q) =>
                q.and(
                    q.gte(q.field("timestamp"), start_time),
                    q.lte(q.field("timestamp"), end_time)
                )
            )
            .collect();

        return events.length;
    },
});
