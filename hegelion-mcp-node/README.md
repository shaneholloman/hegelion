# Hegelion MCP Server (Node.js)

This is the Node.js implementation of the Model Context Protocol (MCP) server for Hegelion.

**Note:** The primary MCP implementation for Hegelion is written in Python and is distributed with the `hegelion` pip package. This Node.js version is maintained for compatibility with environments that prefer Node.js based MCP servers or for development of TypeScript-based extensions.

## Installation

```bash
npm install
```

## Usage

To start the MCP server:

```bash
npm start
```

This will start the server on stdio.

## Configuration

The server requires access to LLM backends. Ensure your environment variables are set, or configure them in a `.env` file if supported by your MCP client.

## Development

Build the project:
```bash
npm run build
```

Run tests:
```bash
npm test
```
