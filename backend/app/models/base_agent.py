from typing import Any
from dating_plan_ai_agents.objects.state import GraphState
from dating_plan_ai_agents.interface.abstract_agent import AbstractAgent


class BaseAgent(AbstractAgent):
    """Base class for a general agent with memory and tools."""

    def __init__(self):
        super().__init__()

    def _get_current_state(self, state: GraphState):
        self.location_feedback = state.get(
            "location_feedback", "No specific location yet"
        )
        self.budget_feedback = state.get("budget_feedback", "No budget feedback yet")
        self.input_feedback = state.get("input_feedback", "No input feedback yet")
        self.schedule_feedback = state.get(
            "schedule_feedback", "No schedule feedback yet"
        )

    def _parse_query(self, query: str, kwargs) -> str:
        """Create first query"""
        agent_feedback = self.llm_caller.get_llm_response(query.format(**kwargs))
        return agent_feedback

    def _summarize_query(self, query: str, kwargs) -> str:
        """Summarize the user's query using the chosen LLM."""
        summary_feedback = self._parse_query(query, kwargs)
        return summary_feedback

    def _retrieve_documents(self, query: str, top_k: int) -> list[str]:
        """Retrieve relevant documents for the query."""
        results = self.pinecone_manager.retrieve_similar_documents(query, top_k=top_k)
        results = ("\n").join(results)
        return results

    def _augment_query(self, query: str, documents: list[str]) -> str:
        """Combine the query with retrieved documents."""
        context = "\n".join(documents)
        return f"Query: {query}\nContext:\n{context}\nAnswer:"

    def _generate_final_query(self, original_query: str, augmented_query: str) -> str:
        """Generate a response using the chosen LLM."""
        final_query = "\n".join([original_query, augmented_query])
        return final_query

    def _execute_action(self, action: str, query_details: any) -> str:
        """Execute the decided action."""
        if action == "retrieve_and_generate":
            documents = self._retrieve_documents(query_details, top_k=5)
            augmented_query = self._augment_query(query_details, documents)
            return self._generate_response(augmented_query)
        elif action.startswith("tool:"):
            tool_name = action.split(":", 1)[1]
            return self.tools.execute(tool_name, query_details)
        else:
            return self._generate_response(query_details)

    def _generate_response(self, augmented_query: str) -> str:
        pass

    def run(self, state) -> str:
        """Main workflow for handling user queries."""
        pass
