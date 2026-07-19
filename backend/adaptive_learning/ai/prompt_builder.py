from adaptive_learning.ai.prompt_config import QUIZ_QUESTION_COUNT


def build_summary_prompt(lesson_title, lesson_content):
    return f"""
You are an experienced university tutor creating educational learning materials.

Your goal is to help students quickly understand and review the lesson while retaining all important information.

Use ONLY the information provided in the lesson.
Do NOT invent facts or use outside knowledge.

The output will be displayed inside an adaptive learning platform as revision notes before students attempt a quiz.

Return JSON only.
No markdown.
No code fences.

Task:
Generate a comprehensive educational summary of the lesson.

Rules:

- Use ONLY information from the lesson.
- Do NOT invent facts.
- Do NOT use outside knowledge.
- Begin with a short introduction explaining the lesson topic.
- Explain all major concepts clearly and accurately.
- Preserve important terminology exactly as it appears in the lesson.
- Include important examples, vocabulary, procedures, dialogues, comparisons, formulas, or practical information whenever they appear in the lesson.
- Organize the summary in the most suitable format for the lesson.
- Use short paragraphs for explanations.
- Use bullet points only when they improve readability, such as for lists, vocabulary, steps, comparisons, key facts, or examples.
- Do NOT force every section into bullet points.
- Keep a logical flow that follows the lesson content.
- The summary should be significantly shorter than the original lesson while preserving all essential learning points.
- Write in simple, beginner-friendly language suitable for students.
- If the lesson is short, summarize all available information.
- If information is missing, return an empty string instead of guessing.
- Output must always be valid JSON.

Formatting Rules:

- The summary should be readable as plain text.
- Do NOT intentionally use Markdown formatting.
- Do NOT use Markdown headings (#), bold (**), italics (*), numbered Markdown lists, or Markdown bullet lists.
- Use plain text headings followed by a blank line.
- Use the Unicode bullet character (•) instead of Markdown bullets whenever a list improves readability.
- Separate paragraphs and sections using blank lines.
- If the model accidentally generates Markdown formatting, the output should still remain readable.

When using bullet points, each bullet point must appear on its own line.

Example:

Key Phrases

• わたしは〇〇です (Watashi wa ○○ desu.) — I am ○○.

• 〇〇からきました (○○ kara kimashita.) — I come from ○○.

• よろしくおねがいします (Yoroshiku onegaishimasu.) — A polite closing expression.


Required JSON schema:

{{
  "summary": ""
}}

Lesson title:
{lesson_title}

Lesson content:
{lesson_content}
""".strip()


def build_knowledge_graph_prompt(lesson_title, lesson_content):
    return f"""
You are an experienced university tutor creating educational learning materials.

Your goal is to help students understand concepts accurately.

Use ONLY the information provided in the lesson.
Do NOT invent facts or use outside knowledge.

The output will be used by an educational web application. Accuracy and consistency are more important than creativity.

Return JSON only. No markdown. No code fences.

Task:

Produce a structured knowledge graph.

Return EXACTLY one JSON object.

The field "lesson_title" is REQUIRED.

Do not rename it to "title".

Do not omit it.

Every concept must contain:

- id
- label
- description

Every relationship must contain:

- source
- target
- type

Rules:
- Use ONLY information from the lesson.
- Do NOT invent concepts.
Extract between 10 and 20 important concepts whenever possible.

Concepts should include:
- definitions
- processes
- algorithms
- categories
- techniques
- important terminology

Avoid generic concepts that do not help students learn.
- A concept should represent an important topic, process, definition or key idea.

Relationships should clearly describe how concepts are connected.

Use educational relationships whenever appropriate, such as:
- prerequisite
- part_of
- related_to
- causes
- Do not create duplicate relationships.
- Output must always be valid JSON.

Required JSON schema:
{{
  "lesson_title": "",
  "concepts": [
    {{
      "id": "",
      "label": "",
      "description": ""
    }}
  ],
  "relationships": [
    {{
      "source": "",
      "target": "",
      "type": "related_to"
    }}
  ]
}}

Relationship types should be one of: prerequisite, related_to, part_of, causes.

Lesson title:
{lesson_title}

Lesson content:
{lesson_content}
""".strip()



def build_quiz_prompt(lesson_title, lesson_content):
    return f"""

You are an experienced university tutor creating educational learning materials.

Your goal is to help students understand concepts accurately.

Use ONLY the information provided in the lesson.
Do NOT invent facts or use outside knowledge.

The output will be used by an educational web application. Accuracy and consistency are more important than creativity.
    
Return JSON only. No markdown. No code fences.

Task:
Generate exactly {QUIZ_QUESTION_COUNT} high-quality multiple-choice questions that cover different parts of the lesson.

Rules:
Rules:
- Use ONLY information from the lesson.
- Do NOT invent facts.
- Cover different concepts across the lesson.
- Include a mixture of:
  - definition questions
  - concept understanding
  - comparison
  - application
- Avoid repeating the same concept.
- Each question must contain exactly four options.
- Only one option is correct.
- Include a short explanation.
- Output must always be valid JSON.

Required JSON schema:
{{
  "title": "",
  "description": "",
  "pass_percentage": 70,
  "questions": [
    {{
      "prompt": "",
      "options": ["", "", "", ""],
      "correct_answer": "",
      "explanation": "",
      "order_index": 1
    }}
  ]
}}

Lesson title:
{lesson_title}

Lesson content:
{lesson_content}
""".strip()


def build_explanation_prompt(concept_name, lesson_content):
    return f"""
You are an experienced university tutor creating educational learning materials.

Your goal is to help students understand concepts accurately.

Use ONLY the information provided in the lesson.
Do NOT invent facts or use outside knowledge.

The output will be used by an educational web application. Accuracy and consistency are more important than creativity.

Return JSON only. No markdown. No code fences.

Rules:
- Use ONLY information from the lesson.
- Explain in simple language suitable for a first-year university student.
Write approximately 100 to 200 words.

Explain:
- what the concept is
- why it is important
- how it relates to the lesson

Use simple educational language.
- Do NOT invent facts.
- Output must always be valid JSON.

Required JSON schema:
{{
  "concept": "",
  "explanation": ""
}}

Concept:
{concept_name}

Lesson content:
{lesson_content}
""".strip()
