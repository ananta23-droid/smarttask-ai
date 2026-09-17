import os
import json
import re
from typing import List
import httpx
from dotenv import load_dotenv
from fastapi import HTTPException, status

from app.schemas.task import AISummarizeRequestItem, AISummarizeResponse

load_dotenv()


OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"


def _extract_json_payload(raw_content: str) -> dict:
    """Extracts a JSON object from model output, including fenced JSON blocks."""
    cleaned = (raw_content or "").strip()
    if not cleaned:
        raise json.JSONDecodeError("Empty content", "", 0)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    fenced = re.search(r"```(?:json)?\s*(\{[\s\S]*\})\s*```", cleaned, flags=re.IGNORECASE)
    if fenced:
        return json.loads(fenced.group(1))

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(cleaned[start:end + 1])

    raise json.JSONDecodeError("No valid JSON object found", cleaned, 0)


def summarize_tasks_with_ai(tasks: List[AISummarizeRequestItem]) -> AISummarizeResponse:
    """Sends tasks to OpenRouter and generates a structured summary, ranking, and recommendation."""
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenRouter API key is not configured. Please add OPENROUTER_API_KEY to backend/.env."
        )

    model_name = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash").strip() or "google/gemini-2.5-flash"
    try:
        max_tokens = int(os.getenv("OPENROUTER_MAX_TOKENS", "1500"))
    except ValueError:
        max_tokens = 1500

    if not tasks:
        return AISummarizeResponse(
            summary="You currently have 0 tasks in your list.",
            highest_priority_tasks=[],
            recommended_order=[],
            recommendation="Your task list is empty! Enjoy your free time or add a new task to get started."
        )

    # Format the tasks into a clear prompt payload
    task_descriptions = []
    for idx, t in enumerate(tasks, 1):
        task_descriptions.append(
            f"{idx}. Title: {t.title} | Priority: {t.priority.value} | Status: {t.status.value} | Details: {t.description or 'None'}"
        )
    formatted_tasks = "\n".join(task_descriptions)

    system_prompt = (
        "You are SmartTask AI, an academic productivity assistant. "
        "Analyze the provided tasks considering their title, priority, status, and details.\n"
        "Your objectives:\n"
        "1. Provide an executive summary of current workload, progress, and key bottlenecks.\n"
        "2. Identify high-priority bottleneck tasks that need immediate focus.\n"
        "3. Determine an optimized execution order (ordered list of task titles).\n"
        "4. In 'recommendation', provide a clear, actionable recommendation with brief reasoning for why this execution order is optimal.\n\n"
        "Return strictly valid JSON with exactly these keys:\n"
        "- summary (string): Executive summary\n"
        "- highest_priority_tasks (array of strings): Urgent bottleneck task titles\n"
        "- recommended_order (array of strings): Complete prioritized list of all task titles\n"
        "- recommendation (string): Actionable advice and reasoning for the execution order\n"
        "Do not include any explanation outside the JSON."
    )

    user_prompt = f"Here is the list of user tasks:\n\n{formatted_tasks}\n\nPlease analyze and prioritize them."

    try:
        request_body = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5173",
            "X-Title": "SmartTask AI",
        }

        with httpx.Client(timeout=httpx.Timeout(30.0, connect=10.0)) as client:
            response = client.post(OPENROUTER_ENDPOINT, headers=headers, json=request_body)

        if response.status_code in (401, 403):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="OpenRouter authentication failed. Please verify OPENROUTER_API_KEY in backend/.env."
            )

        if response.status_code == 402:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="OpenRouter payment or credits required, or requested token limit exceeded. Check your credits or adjust OPENROUTER_MAX_TOKENS."
            )

        if response.status_code == 429:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="OpenRouter rate limit or quota exceeded. Please retry shortly or check your OpenRouter plan."
            )

        if response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Configured OpenRouter model '{model_name}' was not found. Please verify OPENROUTER_MODEL in backend/.env."
            )

        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="OpenRouter request failed. Verify OPENROUTER_MODEL, request parameters, and provider availability."
            )

        payload = response.json()
        choices = payload.get("choices") if isinstance(payload, dict) else None
        if not choices or not isinstance(choices, list):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Invalid response shape received from OpenRouter."
            )

        message = choices[0].get("message", {}) if isinstance(choices[0], dict) else {}
        content = message.get("content", "") if isinstance(message, dict) else ""
        if not content:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="OpenRouter returned an empty completion."
            )

        parsed = _extract_json_payload(content)

        return AISummarizeResponse(
            summary=str(parsed.get("summary") or f"You have {len(tasks)} tasks."),
            highest_priority_tasks=list(parsed.get("highest_priority_tasks") or []),
            recommended_order=list(parsed.get("recommended_order") or [t.title for t in tasks]),
            recommendation=str(parsed.get("recommendation") or "Focus on completing your high-priority items first.")
        )

    except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError, httpx.HTTPError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not connect to OpenRouter servers. Please check your internet connection."
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to parse structured JSON response from OpenRouter."
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during AI analysis."
        )
