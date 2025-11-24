import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

async function main() {
    const transport = new StdioClientTransport({
        command: "node",
        args: ["dist/index.js"],
    });

    const client = new Client(
        {
            name: "test-client",
            version: "1.0.0",
        },
        {
            capabilities: {},
        }
    );

    await client.connect(transport);

    console.log("Connected to server");

    const tools = await client.listTools();
    console.log("Tools:", tools.tools.map((t) => t.name));

    const result = await client.callTool({
        name: "showHegelionDebate",
        arguments: { debateId: "test-debate" },
    });

    console.log("Tool Result:", JSON.stringify(result, null, 2));

    await client.close();
}

main().catch((error) => {
    console.error("Error:", error);
    process.exit(1);
});
