"""MCP Server Evaluation Harness.

This script evaluates MCP servers by running test questions against them using Claude.
"""

import asyncio
import json
import re
import sys
import time
import traceback
from pathlib import Path

from anthropic import Anthropic
from connections import MCPConnection, create_connection
from defusedxml import ElementTree as DelTree

EVALUATION_PROMPT = """You are an AI assistant with access to tools.

When given a task, you MUST:
1. Use the available tools to complete the task
2. Provide summary of each step in your approach, wrapped in <summary> tags
3. Provide feedback on the tools provided, wrapped in <feedback> tags
4. Provide your final response, wrapped in <response> tags

Summary Requirements:
- In your <summary> tags, you must explain:
  - The steps you took to complete the task
  - Which tools you used, in what order, and why
  - The inputs you provided to each tool
  - The outputs you received from each tool
  - A summary for how you arrived at the response

Feedback Requirements:
- In your <feedback> tags, provide constructive feedback on the tools:
  - Comment on tool names: Are they clear and descriptive?
  - Comment on input parameters: Are they well-documented? Are required vs optional parameters clear?
  - Comment on descriptions: Do they accurately describe what the tool does?
  - Comment on any errors encountered during tool usage: Did the tool fail to execute? Did the tool return too many tokens?
  - Identify specific areas for improvement and explain WHY they would help
  - Be specific and actionable in your suggestions

Response Requirements:
- Your response should be concise and directly address what was asked
- Always wrap your final response in <response> tags
- If you cannot solve the task return <response>NOT_FOUND</response>
- For numeric responses, provide just the number
- For IDs, provide just the ID
- For names or text, provide the exact text requested
- Your response should go last"""


def parse_evaluation_file(file_path: Path) -> list[dict[str, str]]:
    """Parse XML evaluation file with qa_pair elements."""
    tree = DelTree.parse(file_path)
    root = tree.getroot()
    return [
        {
            "question": (qa_pair.find("question").text or "").strip(),
            "answer": (qa_pair.find("answer").text or "").strip(),
        }
        for qa_pair in root.findall(".//qa_pair")
        if qa_pair.find("question") is not None and qa_pair.find("answer") is not None
    ]


def extract_xml_content(text: str, tag: str) -> str | None:
    """Extract content from XML tags."""
    pattern = rf"<{tag}>(.*?)</{tag}>"
    matches = re.findall(pattern, text, re.DOTALL)
    return matches[-1].strip() if matches else None


async def agent_loop(
    client: Anthropic,
    model: str,
    question: str,
    tools: list[dict[str, object]],
    connection: MCPConnection,
) -> tuple[str | None, dict[str, object]]:
    """Run the agent loop with MCP tools."""
    messages: list[dict[str, object]] = [{"role": "user", "content": question}]

    response = await asyncio.to_thread(
        client.messages.create,
        model=model,
        max_tokens=4096,
        system=EVALUATION_PROMPT,
        messages=messages,
        tools=tools,
    )

    messages.append({"role": "assistant", "content": response.content})

    tool_metrics: dict[str, dict[str, object]] = {}

    while response.stop_reason == "tool_use":
        tool_use = next(block for block in response.content if block.type == "tool_use")
        tool_name = tool_use.name
        tool_input = tool_use.input

        tool_start_ts = time.time()
        try:
            tool_result = await connection.call_tool(tool_name, tool_input)
            tool_response = (
                json.dumps(tool_result)
                if isinstance(tool_result, (dict, list))
                else str(tool_result)
            )
        except (RuntimeError, OSError, ValueError) as e:
            tool_response = f"Error executing tool {tool_name}: {e!s}\n"
            tool_response += traceback.format_exc()
        tool_duration = time.time() - tool_start_ts

        if tool_name not in tool_metrics:
            tool_metrics[tool_name] = {"count": 0, "durations": []}
        tool_metrics[tool_name]["count"] += 1
        tool_metrics[tool_name]["durations"].append(tool_duration)

        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": tool_response,
                }
            ],
        })

        response = await asyncio.to_thread(
            client.messages.create,
            model=model,
            max_tokens=4096,
            system=EVALUATION_PROMPT,
            messages=messages,
            tools=tools,
        )
        messages.append({"role": "assistant", "content": response.content})

    response_text = next(
        (block.text for block in response.content if hasattr(block, "text")), None
    )
    return response_text, tool_metrics


async def evaluate_single_task(
    client: Anthropic,
    model: str,
    qa_pair: dict[str, str],
    tools: list[dict[str, object]],
    connection: MCPConnection,
) -> dict[str, object]:
    """Evaluate a single QA pair with the given tools."""
    start_time = time.time()

    response, tool_metrics = await agent_loop(client, model, qa_pair["question"],
                                              tools, connection)

    response_value = extract_xml_content(response, "response")
    summary = extract_xml_content(response, "summary")
    feedback = extract_xml_content(response, "feedback")

    duration_seconds = time.time() - start_time

    return {
        "question": qa_pair["question"],
        "expected": qa_pair["answer"],
        "actual": response_value,
        "score": int(response_value == qa_pair["answer"]) if response_value else 0,
        "total_duration": duration_seconds,
        "tool_calls": tool_metrics,
        "num_tool_calls": sum(
            len(metrics["durations"]) for metrics in tool_metrics.values()
        ),
        "summary": summary,
        "feedback": feedback,
    }


REPORT_HEADER = """
# Evaluation Report

## Summary

- **Accuracy**: {correct}/{total} ({accuracy:.1f}%)
- **Average Task Duration**: {average_duration_s:.2f}s
- **Average Tool Calls per Task**: {average_tool_calls:.2f}
- **Total Tool Calls**: {total_tool_calls}

---
"""

TASK_TEMPLATE = """
### Task {task_num}

**Question**: {question}
**Ground Truth Answer**: `{expected_answer}`
**Actual Answer**: `{actual_answer}`
**Correct**: {correct_indicator}
**Duration**: {total_duration:.2f}s
**Tool Calls**: {tool_calls}

**Summary**
{summary}

**Feedback**
{feedback}

---
"""


async def run_evaluation(
    eval_path: Path, connection: MCPConnection, model: str = "claude-3-7-sonnet-20250219"
) -> str:
    """Run evaluation with MCP server tools."""
    client = Anthropic()

    tools = await connection.list_tools()

    qa_pairs = parse_evaluation_file(eval_path)

    results = [await evaluate_single_task(client, model, qa_pair, tools, connection)
               for qa_pair in qa_pairs]

    correct = sum(r["score"] for r in results)
    accuracy = (correct / len(results)) * 100 if results else 0
    average_duration_s = (
        sum(r["total_duration"] for r in results) / len(results) if results else 0
    )
    average_tool_calls = (
        sum(r["num_tool_calls"] for r in results) / len(results) if results else 0
    )
    total_tool_calls = sum(r["num_tool_calls"] for r in results)

    report = REPORT_HEADER.format(
        correct=correct,
        total=len(results),
        accuracy=accuracy,
        average_duration_s=average_duration_s,
        average_tool_calls=average_tool_calls,
        total_tool_calls=total_tool_calls,
    )

    report += "".join([
        TASK_TEMPLATE.format(
            task_num=i + 1,
            question=qa_pair["question"],
            expected_answer=qa_pair["answer"],
            actual_answer=result["actual"] or "N/A",
            correct_indicator="✅" if result["score"] else "❌",
            total_duration=result["total_duration"],
            tool_calls=json.dumps(result["tool_calls"], indent=2),
            summary=result["summary"] or "N/A",
            feedback=result["feedback"] or "N/A",
        )
        for i, (qa_pair, result) in enumerate(zip(qa_pairs, results, strict=False))
    ])

    return report


def parse_headers(header_list: list[str]) -> dict[str, str]:
    """Parse header strings in format 'Key: Value' into a dictionary."""
    headers = {}
    if not header_list:
        return headers

    for header in header_list:
        if ":" in header:
            key, value = header.split(":", 1)
            headers[key.strip()] = value.strip()
    return headers


def parse_env_vars(env_list: list[str]) -> dict[str, str]:
    """Parse environment variable strings in format 'KEY=VALUE' into a dictionary."""
    env = {}
    if not env_list:
        return env

    for env_var in env_list:
        if "=" in env_var:
            key, value = env_var.split("=", 1)
            env[key.strip()] = value.strip()
    return env


USAGE = """usage: evaluation.py [-h] eval_file
                      [-t {stdio,sse,http}] [-m MODEL] [-c COMMAND] [-a [ARGS ...]]
                      [-e [ENV ...]] [-u URL] [-H [HEADERS ...]] [-o OUTPUT]

Examples:
  python evaluation.py -t stdio -c python -a my_server.py eval.xml
  python evaluation.py -t sse -u https://example.com/mcp -H "Authorization: Bearer token" eval.xml
  python evaluation.py -t http -u https://example.com/mcp -m claude-3-5-sonnet-20241022 eval.xml"""


class UsageError(ValueError):
    """Command-line usage error reported to the caller."""


def parse_args(argv: list[str]) -> dict[str, object]:
    """Parse the evaluation-harness command line without a CLI framework."""
    args: dict[str, object] = {"transport": "stdio"}
    positional: list[str] = []
    flags_getting_value = {
        "-t": "transport",
        "--transport": "transport",
        "-m": "model",
        "--model": "model",
        "-c": "command",
        "--command": "command",
        "-e": "env",
        "--env": "env",
        "-u": "url",
        "--url": "url",
        "-o": "output",
        "--output": "output",
    }

    index = 0
    while index < len(argv):
        spell = argv[index]
        if spell in {"-a", "--args"}:
            collected: list[str] = []
            index += 1
            while index < len(argv) and not argv[index].startswith("-"):
                collected.append(argv[index])
                index += 1
            args["args"] = collected
            continue
        if spell in {"-H", "--header"}:
            received: list[str] = []
            index += 1
            while index < len(argv) and not argv[index].startswith("-"):
                received.append(argv[index])
                index += 1
            args["headers"] = received
            continue
        if spell in {"-h", "--help"}:
            sys.stdout.write(USAGE + "\n")
            sys.exit(0)
        if spell in flags_getting_value:
            index += 1
            if index >= len(argv):
                msg = f"Missing value for {spell}"
                raise UsageError(msg)
            args[flags_getting_value[spell]] = argv[index]
            index += 1
            continue
        if spell.startswith("-"):
            msg = f"Unknown option: {spell}"
            raise UsageError(msg)
        positional.append(spell)
        index += 1

    args["eval_file"] = Path(positional[0])
    return args


async def main() -> None:
    """Evaluate MCP servers using test questions from the command line."""
    try:
        args = parse_args(sys.argv[1:])
    except UsageError:
        sys.exit(1)

    eval_file = args["eval_file"]
    if not isinstance(eval_file, Path) or not eval_file.exists():
        sys.exit(1)

    transport: str = args["transport"]
    model: str = args.get("model", "claude-3-7-sonnet-20250219")

    headers = parse_headers(args["headers"]) if args.get("headers") else None
    env_vars = parse_env_vars(args["env"]) if args.get("env") else None

    try:
        connection = create_connection(
            transport=transport,
            command=args.get("command"),
            args=args.get("args"),
            env=env_vars,
            url=args.get("url"),
            headers=headers,
        )
    except ValueError:
        sys.exit(1)

    async with connection:
        report = await run_evaluation(eval_file, connection, model)

        output = args.get("output")
        if output:
            output.write_text(report)


if __name__ == "__main__":
    asyncio.run(main())
