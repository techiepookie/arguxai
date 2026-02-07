import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

/**
 * Create a new issue
 */
export const create = mutation({
    args: {
        issue_id: v.string(),
        funnel_step: v.string(),
        detected_at: v.number(),
        current_conversion_rate: v.number(),
        baseline_conversion_rate: v.number(),
        drop_percentage: v.number(),
        sigma_value: v.number(),
        is_significant: v.boolean(),
        current_sessions: v.number(),
        baseline_sessions: v.number(),
        status: v.string(),
        severity: v.string(),
        diagnosis: v.optional(v.any()),
    },
    handler: async (ctx, args) => {
        const id = await ctx.db.insert("issues", {
            ...args,
            updated_at: Date.now(),
        });

        return id;
    },
});

/**
 * Update issue with diagnosis
 */
export const updateDiagnosis = mutation({
    args: {
        issue_id: v.string(),
        diagnosis: v.any(),
    },
    handler: async (ctx, { issue_id, diagnosis }) => {
        const issue = await ctx.db
            .query("issues")
            .filter((q) => q.eq(q.field("issue_id"), issue_id))
            .first();

        if (!issue) {
            throw new Error(`Issue ${issue_id} not found`);
        }

        await ctx.db.patch(issue._id, {
            diagnosis,
            status: "diagnosed",
            updated_at: Date.now(),
        });

        return { success: true };
    },
});

/**
 * Update issue with Jira ticket info
 */
export const updateJiraTicket = mutation({
    args: {
        issue_id: v.string(),
        jira_ticket: v.any(),
    },
    handler: async (ctx, { issue_id, jira_ticket }) => {
        const issue = await ctx.db
            .query("issues")
            .filter((q) => q.eq(q.field("issue_id"), issue_id))
            .first();

        if (!issue) {
            throw new Error(`Issue ${issue_id} not found`);
        }

        await ctx.db.patch(issue._id, {
            jira_ticket,
            updated_at: Date.now(),
        });

        return { success: true };
    },
});

/**
 * Update issue with GitHub PR info
 */
export const updateGitHubPR = mutation({
    args: {
        issue_id: v.string(),
        github_pr: v.any(),
    },
    handler: async (ctx, { issue_id, github_pr }) => {
        const issue = await ctx.db
            .query("issues")
            .filter((q) => q.eq(q.field("issue_id"), issue_id))
            .first();

        if (!issue) {
            throw new Error(`Issue ${issue_id} not found`);
        }

        await ctx.db.patch(issue._id, {
            github_pr,
            updated_at: Date.now(),
        });

        return { success: true };
    },
});

/**
 * Get issue by ID
 */
export const getById = query({
    args: {
        issue_id: v.string(),
    },
    handler: async (ctx, { issue_id }) => {
        return await ctx.db
            .query("issues")
            .filter((q) => q.eq(q.field("issue_id"), issue_id))
            .first();
    },
});

/**
 * List all issues
 */
export const list = query({
    handler: async (ctx) => {
        return await ctx.db
            .query("issues")
            .order("desc")
            .collect();
    },
});
