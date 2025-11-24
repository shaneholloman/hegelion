import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

async function main() {
    const transport = new StdioClientTransport({
        command: "node",
        args: ["dist/index.js"],
    });

    const client = new Client(
        { name: "security-test", version: "1.0.0" },
        { capabilities: {} }
    );

    await client.connect(transport);
    console.log("Connected to server");

    const testCases = [
        { id: "valid-id", shouldPass: true },
        { id: "valid_id.123", shouldPass: true },
        { id: "<script>alert(1)</script>", shouldPass: false },
        { id: "id with spaces", shouldPass: false },
        { id: "../parent", shouldPass: false },
        { id: "a".repeat(129), shouldPass: false }, // Too long
        { id: "", shouldPass: false }, // Empty
    ];

    for (const test of testCases) {
        console.log(`Testing debateId: "${test.id}" (Expect pass: ${test.shouldPass})`);
        try {
            await client.callTool({
                name: "showHegelionDebate",
                arguments: { debateId: test.id },
            });
            if (!test.shouldPass) {
                console.error("❌ FAILED: Invalid ID was accepted!");
            } else {
                console.log("✅ PASSED: Valid ID accepted.");
            }
        } catch (error: any) {
            if (test.shouldPass) {
                console.error(`❌ FAILED: Valid ID rejected! Error: ${error.message}`);
            } else {
                console.log(`✅ PASSED: Invalid ID rejected. Error: ${error.message}`);
            }
        }
    }

    await client.close();
}

main().catch(console.error);
