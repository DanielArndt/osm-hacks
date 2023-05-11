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
from temporalio.exceptions import ApplicationError, FailureError
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


@activity.defn
async def throw_exception(input: ComposeGreetingInput) -> ComposeGreetingOutput:
    """Activity that throws an exception."""
    raise Exception("Exception from activity")


@activity.defn
async def throw_non_retryable_exception(
    input: ComposeGreetingInput,
) -> ComposeGreetingOutput:
    """Activity that throws an exception."""
    raise ApplicationError("Exception from activity", non_retryable=True)


@workflow.defn
class ExceptionWorkflow:
    @workflow.run
    async def run(self, name: str) -> ComposeGreetingOutput:
        workflow.logger.info("Running workflow with parameter %s" % name)
        try:
            return await workflow.execute_activity(
                throw_exception,
                ComposeGreetingInput("Hello", name),
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=retry_policy,
            )
        except FailureError as e:
            logging.info(f"FailureError.cause: {e.cause}")
            raise
        except Exception as e:
            logging.exception(f"Exception in workflow of type {type(e)}")
            raise


@workflow.defn(sandboxed=False)
class ExceptionInChildWorkflow:
    @workflow.run
    async def run(self, name: str) -> ComposeGreetingOutput:
        workflow.logger.info("Running workflow with parameter %s" % name)
        try:
            return await workflow.execute_child_workflow(
                workflow=ExceptionWorkflow, arg=name  # type: ignore
            )
        except FailureError as e:
            logging.info(f"e.cause: {e.cause}")
            logging.exception("Exception in child workflow")
            raise


async def run__workflow_activity_exception(client):
    """Throws an exception in the activity"""
    try:
        await client.execute_workflow(
            ExceptionWorkflow.run,
            "World",
            id="hello-activity-workflow-id",
            task_queue="hello-activity-task-queue",
        )
    except Exception:
        logging.exception("Error executing workflow")


async def run__workflow_childworkflow_activity_exception(client):
    """Throws an exception in an activity inside a child workflow"""
    try:
        await client.execute_workflow(
            ExceptionInChildWorkflow.run,
            "World",
            id="hello-activity-workflow-id",
            task_queue="hello-activity-task-queue",
        )
    except Exception:
        logging.exception("Error executing workflow")


async def main():
    logging.basicConfig(level=logging.INFO)

    client = await Client.connect("localhost:7233")

    async with Worker(
        client,
        task_queue="hello-activity-task-queue",
        workflows=[ExceptionWorkflow, ExceptionInChildWorkflow],
        activities=[throw_exception],
        debug_mode=True,
    ):
        await run__workflow_activity_exception(client)
        await run__workflow_childworkflow_activity_exception(client)


if __name__ == "__main__":
    asyncio.run(main())
