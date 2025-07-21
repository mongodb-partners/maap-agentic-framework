# Framework Overview

## Introduction
The MAAP (MongoDB AI Applications Program) Agentic Framework represents a significant advancement in AI application development, extending beyond traditional RAG systems to create truly intelligent, autonomous applications. At its core, this framework combines sophisticated agent architectures with MongoDB's powerful database capabilities, enabling applications that can reason, learn, and execute complex tasks with contextual awareness.

## Architecture and Core Components

The framework is built around a modular architecture that emphasizes flexibility and extensibility. At its heart lies a powerful agent system that combines several key components working in harmony:

### MCP (Model Context Protocol) Server
The MCP Server acts as the central nervous system of the framework, managing communication and context flow between components. It provides:
- Standardized protocol for model-agent interactions
- Real-time context management and routing
- Efficient message handling and prioritization
- Built-in support for multiple model providers
- Secure and monitored communication channels

**Referenced Github**
For more information, visit the [Memory MCP](https://github.com/mongodb-partners/memory-mcp).

### Agent Builder
The Agent Builder serves as the foundation for creating and customizing intelligent agents. It provides a structured approach to defining agent behaviors, capabilities, and interaction patterns. Key features include:
- A declarative configuration system using YAML for agent definition
- Flexible component integration for custom agent capabilities
- Built-in templates for common agent patterns
- Dynamic runtime behavior modification

**Referenced Github**
For more information, visit the [Agentic Builder](https://github.com/ashwin-gangadhar-mdb/maap-agent-builder).

### Data Loader Components
The Data Loader system provides robust and flexible data ingestion capabilities, essential for building the agent's knowledge base:
- Support for multiple data sources (PDF, DOCX, Excel, JSON, Web, YouTube)
- Real-time data streaming and processing
- Intelligent chunking and preprocessing
- Automated metadata extraction
- Integration with MongoDB's vector storage

**Referenced Github**
For more information, visit the [Data Loader](https://github.com/mongodb-partners/maap-data-loader).
