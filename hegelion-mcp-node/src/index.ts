import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
    CallToolRequestSchema,
    ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { createUIResource } from "@mcp-ui/server";
import { z } from "zod";

const showDebateArgsSchema = z.object({
    debateId: z
        .string()
        .trim()
        .min(1)
        .max(128)
        .regex(/^[a-zA-Z0-9._-]+$/, {
            message: "debateId may only include letters, numbers, dot, underscore, or dash",
        }),
});

const escapeHtml = (value: string) =>
    value
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");

// Create server instance
const server = new Server(
    {
        name: "hegelion-mcp-node",
        version: "0.1.0",
    },
    {
        capabilities: {
            tools: {},
        },
    }
);

// Define tool handlers
server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
        tools: [
            {
                name: "showHegelionDebate",
                description: "Show a Hegelion debate with UI support",
                inputSchema: {
                    type: "object",
                    properties: {
                        debateId: {
                            type: "string",
                            description: "ID of the debate to show",
                        },
                    },
                    required: ["debateId"],
                },
            },
        ],
    };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
    if (request.params.name === "showHegelionDebate") {
        const parsedArgs = showDebateArgsSchema.safeParse(request.params.arguments ?? {});

        if (!parsedArgs.success) {
            throw new Error(
                `Invalid arguments for showHegelionDebate: ${parsedArgs.error.issues
                    .map((issue) => issue.message)
                    .join(", ")}`
            );
        }

        const debateId = parsedArgs.data.debateId;

        // Mock debate data
        const debateJson = {
            id: debateId,
            thesis: "Consciousness is fundamental to the universe.",
            antithesis: "Consciousness is an emergent property of complex computation.",
            synthesis: "Consciousness is a fundamental field that couples with complex computation to manifest subjective experience.",
        };

        const html = `
      <html>
        <head>
          <style>
            body { font-family: sans-serif; padding: 20px; background: #f4f4f9; color: #333; }
            h1 { color: #2c3e50; }
            .step { background: white; padding: 15px; margin-bottom: 10px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .label { font-weight: bold; color: #7f8c8d; text-transform: uppercase; font-size: 0.8em; }
            .content { margin-top: 5px; font-size: 1.1em; }
          </style>
        </head>
        <body>
          <h1>Hegelion Debate Viewer</h1>
          <div class="step">
            <div class="label">Thesis</div>
            <div class="content">${escapeHtml(debateJson.thesis)}</div>
          </div>
          <div class="step">
            <div class="label">Antithesis</div>
            <div class="content">${escapeHtml(debateJson.antithesis)}</div>
          </div>
          <div class="step">
            <div class="label">Synthesis</div>
            <div class="content">${escapeHtml(debateJson.synthesis)}</div>
          </div>
          <hr/>
          <pre>${escapeHtml(JSON.stringify(debateJson, null, 2))}</pre>
        </body>
      </html>
    `;

        return {
            content: [
                { type: "text", text: `Rendered Hegelion debate ${debateId} as UI.` },
                createUIResource({
                    uri: `ui://hegelion/debate/${debateId}`,
                    content: { type: "rawHtml", htmlString: html },
                    encoding: "text",
                }),
            ],
        };
    }

    throw new Error("Tool not found");
});

// Start server
async function main() {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error("Hegelion Node MCP Server running on stdio");
}

main().catch((error) => {
    console.error("Server error:", error);
    process.exit(1);
});
