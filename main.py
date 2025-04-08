import asyncio
import argparse
import os

from app.agent.umile import Umile
from app.logger import logger


def get_args():
    parser = argparse.ArgumentParser(description="Run the Umile agent.")
    parser.add_argument(
        "--use_prompt",
        type=str,
        default="n",
        choices=["y", "n"],
        help="Whether to use a prompt file (y/n).",
    )
    parser.add_argument(
        "--prompt_path",
        type=str,
        default=None,
        help="Path to the prompt file to use for the agent.",
    )
    return parser.parse_args()


async def _main(prompt: str):
    agent = Umile()
    logger.warning("Processing your request...")
    await agent.run(prompt)
    logger.info("Request processing completed.")


async def main():
    try:
        prompt = input("Enter your prompt: ")
        if not prompt.strip():
            logger.warning("Empty prompt provided.")
            return

        await _main(prompt)
    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")


async def main_with_prompt(prompt: str):
    try:
        await _main(prompt)
    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")


if __name__ == "__main__":
    args = get_args()
    if args.use_prompt == "y" and args.prompt_path:
        if not os.path.exists(args.prompt_path):
            logger.error(f"Prompt file not found: {args.prompt_path}")
            exit(1)

        with open(args.prompt_path, "r") as f:
            prompt = f.read()
        if not prompt.strip():
            logger.warning("Empty prompt provided.")
            exit(1)
        asyncio.run(main_with_prompt(prompt))
    else:
        asyncio.run(main())
