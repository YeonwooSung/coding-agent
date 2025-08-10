import asyncio
import time

from app.agent.base import BaseAgent
from app.agent.umile import Umile
from app.flow.flow_factory import FlowFactory, FlowType
from app.logger import logger


async def _run_flow(prompt: str, agents: dict[str, BaseAgent]):
    flow = FlowFactory.create_flow(
        flow_type=FlowType.PLANNING,
        agents=agents,
    )
    logger.warning("Processing your request...")

    try:
        start_time = time.time()
        result = await asyncio.wait_for(
            flow.execute(prompt),
            timeout=3600,  # 60 minute timeout for the entire execution
        )
        elapsed_time = time.time() - start_time
        logger.info(f"Request processed in {elapsed_time:.2f} seconds")
        logger.info(result)
    except asyncio.TimeoutError:
        logger.error("Request processing timed out after 1 hour")
        logger.info(
            "Operation terminated due to timeout. Please try a simpler request."
        )


async def run_flow_from_prompt(prompt: str):
    """Run the flow with the provided prompt."""
    agents = {
        "umile": Umile(),
    }
    await _run_flow(prompt, agents)


async def run_flow():
    agents = {
        "umile": Umile(),
    }

    try:
        prompt = input("Enter your prompt: ")

        if prompt.strip().isspace() or not prompt:
            logger.warning("Empty prompt provided.")
            return

        await _run_flow(prompt, agents)

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user.")
    except Exception as e:
        logger.error(f"Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(run_flow())
