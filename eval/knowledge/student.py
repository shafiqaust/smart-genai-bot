import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from eval.knowledge.KB import Node

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class Student:
    def __init__(self, known_nodes: list[Node]):
        self.known: set[Node] = set(known_nodes)

    def can_understand(self, node: Node) -> bool:
        """True if every prerequisite of node is already in known."""
        return all(prereq in self.known for prereq in node.point_from)

    def missing_prerequisites(self, node: Node) -> list[Node]:
        """Return prerequisites of node that are not yet known."""
        return [prereq for prereq in node.point_from if prereq not in self.known]

    def next_question(self, node: Node, bot_answer: str, phase: str) -> str:
        """
        Generate the student's next question.

        phase: "what" | "how" | "why"
        If the bot's answer contains a term the student doesn't recognise,
        the student asks about that term first instead of advancing the phase.
        """
        known_names = [n.name for n in self.known]

        unknown_term = self._first_unknown_term(bot_answer)

        if unknown_term:
            instruction = (
                f"The teacher just said: '{bot_answer}'. "
                f"You do not know what '{unknown_term}' means. Ask about it in one sentence."
            )
        else:
            instruction = {
                "what": f"Ask what {node.name} is. One sentence.",
                "how": f"Ask how {node.name} works. One sentence.",
                "why": f"Ask why {node.name} is needed. One sentence.",
            }[phase]

        system = (
            f"You are a student. You only know these concepts: {known_names}. "
            f"You must not use or reference any concept outside that list. "
            f"Stay in character — you are genuinely trying to understand {node.name}."
        )

        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": instruction},
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    def is_leaf(self, node: Node) -> bool:
        """True if the node has no prerequisites (point_from is empty)."""
        return len(node.point_from) == 0

    def try_understand(self, node: Node, conversation: list[dict]) -> bool:
        """
        Attempt to mark node as understood.

        Leaf node: no prerequisites — if the bot mentioned/explained it, the student
        understands it immediately. Added to known and returns True right away.

        Non-leaf node: prerequisites must already be in known. Student explains the
        concept in their own words; an LLM judge checks against the node description
        and vocabulary constraint. Added to known only if the judge agrees.
        """
        if self.is_leaf(node):
            self.known.add(node)
            return True

        if not self.can_understand(node):
            return False

        known_names = [n.name for n in self.known]

        # Student produces an explanation using only known vocabulary
        explanation_prompt = (
            f"You are a student who only knows: {known_names}. "
            f"Based on what the teacher just explained, describe {node.name} in your own words. "
            f"Use only concepts from your known list. Two to three sentences."
        )
        explanation_response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "system", "content": explanation_prompt}] + conversation,
            temperature=0.7,
        )
        explanation = explanation_response.choices[0].message.content.strip()

        # Judge checks explanation against ground truth and vocabulary constraint
        judge_prompt = f"""You are a strict evaluator.

Concept: {node.name}
Ground truth: {node.description}
Student's known vocabulary: {known_names}
Student's explanation: "{explanation}"

Rules:
1. The explanation must capture the core idea from the ground truth.
2. The explanation must not rely on concepts outside the student's known vocabulary.

Respond with JSON only:
{{"understood": true or false, "reason": "one sentence"}}"""

        judge_response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": judge_prompt}],
            temperature=0.0,
        )
        result = json.loads(judge_response.choices[0].message.content.strip())

        if result["understood"]:
            self.known.add(node)

        return result["understood"]

    def _first_unknown_term(self, text: str) -> str | None:
        """
        Ask an LLM to extract technical terms from text and return the first
        one not covered by the student's known vocabulary.
        Returns None if all terms are known.
        """
        known_names = [n.name.lower() for n in self.known]

        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract all distinct technical terms or concepts from the text. "
                        "Return a JSON array of strings only. No explanation."
                    ),
                },
                {"role": "user", "content": text},
            ],
            temperature=0.0,
        )
        terms: list[str] = json.loads(response.choices[0].message.content.strip())

        for term in terms:
            if term.lower() not in known_names:
                return term
        return None
