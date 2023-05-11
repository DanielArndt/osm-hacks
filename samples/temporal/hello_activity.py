#!/usr/bin/env python3

""" This is a simple example of a Temporal workflow that invokes an activity.

To run this example, you will need to have a Temporal server running.

You can run the server via docker using this repository:

https://github.com/temporalio/docker-compose

For convenience, the quick start instructions are copied here. Assuming you have
docker and docker compose installed, you can run the following commands to start
the server:

    git clone https://github.com/temporalio/docker-compose.git
    cd docker-compose
    docker compose up

Then, run the following command in a separate terminal:

    python3 workflow_worker.py
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import timedelta

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.common import RetryPolicy
from temporalio.worker import Worker

retry_policy = RetryPolicy(maximum_attempts=3)


# While we could use multiple parameters in the activity, Temporal strongly
# encourages using a single dataclass instead which can have fields added to it
# in a backwards-compatible way.
@dataclass
class ComposeGreetingInput:
    greeting: str
    name: str


@dataclass
class ComposeGreetingOutput:
    greeting: str
    name: str


# Basic activity that logs and does string concatenation
@activity.defn
async def compose_greeting(input: ComposeGreetingInput) -> ComposeGreetingOutput:
    activity.logger.info("Running activity with parameter %s" % input)
    return ComposeGreetingOutput(f"{input.greeting}, {input.name}!", input.name)


@activity.defn
async def throw_exception(input: ComposeGreetingInput) -> ComposeGreetingOutput:
    """Activity that throws an exception."""
    raise Exception("Exception from activity")


@workflow.defn
class ExceptionWorkflow:
    @workflow.run
    async def run(self, name: str) -> ComposeGreetingOutput:
        workflow.logger.info("Running workflow with parameter %s" % name)
        return await workflow.execute_activity(
            throw_exception,
            ComposeGreetingInput("Hello", name),
            start_to_close_timeout=timedelta(seconds=10),
        )


# Basic workflow that logs and invokes an activity
@workflow.defn
class GreetingWorkflow:
    @workflow.run
    async def run(self, name: str) -> ComposeGreetingOutput:
        workflow.logger.info("Running workflow with parameter %s" % name)
        return await workflow.execute_activity(
            compose_greeting,
            ComposeGreetingInput("Hello", name),
            start_to_close_timeout=timedelta(seconds=10),
        )


async def main():
    # Uncomment the line below to see logging
    logging.basicConfig(level=logging.INFO)

    # Start client
    client = await Client.connect("localhost:7233")

    # Run a worker for the workflow
    async with Worker(
        client,
        task_queue="hello-activity-task-queue",
        workflows=[GreetingWorkflow, ExceptionWorkflow],
        activities=[compose_greeting, throw_exception],
    ):
        # While the worker is running, use the client to run the workflow and
        # print out its result. Note, in many production setups, the client
        # would be in a completely separate process from the worker.
        result = await client.execute_workflow(
            ExceptionWorkflow.run,
            "World",
            id="hello-activity-workflow-id",
            task_queue="hello-activity-task-queue",
        )
        print(f"Type: {type(result)} Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
