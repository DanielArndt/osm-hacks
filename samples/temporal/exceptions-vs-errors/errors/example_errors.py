#!/usr/bin/env python3

""" This is an example for testing how error return values might work with
temporal"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import Union

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.common import RetryPolicy
from temporalio.exceptions import FailureError
from temporalio.worker import Worker

retry_policy = RetryPolicy(maximum_attempts=3)
TASK_QUEUE = "hello-activity-task-queue"


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


@dataclass
class ComposeGreetingError:
    error: str


@activity.defn
async def return_error(
    input: ComposeGreetingInput,
) -> Union[ComposeGreetingOutput, ComposeGreetingError]:
    """Activity that throws an exception."""
    return ComposeGreetingError("Error from activity")


@workflow.defn
class ExceptionWorkflow:
    @workflow.run
    async def run(
        self, name: str
    ) -> Union[ComposeGreetingOutput, ComposeGreetingError]:
        workflow.logger.info("Running workflow with parameter %s" % name)
        try:
            value = await workflow.execute_activity(
                return_error,
                ComposeGreetingInput("Hello", name),
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=retry_policy,
            )
            if isinstance(value, ComposeGreetingError):
                return ComposeGreetingError(value.error)
            return value
        except Exception as e:
            logging.error(f"Exception in workflow of type {type(e)}")
            raise


@workflow.defn(sandboxed=False)
class ExceptionInChildWorkflow:
    @workflow.run
    async def run(self, name: str) -> ComposeGreetingOutput:
        workflow.logger.info("Running workflow with parameter %s" % name)
        try:
            value = await workflow.execute_child_workflow(
                workflow=ExceptionWorkflow, arg=name  # type: ignore
            )
            if isinstance(value, ComposeGreetingError):
                raise Exception(value.error)
            return value
        except FailureError as e:
            logging.info(f"e.cause: {e.cause}")
            logging.error("Exception in child workflow")
            raise


async def run__workflow_activity_exception(client):
    """Throws an exception in the activity"""
    try:
        await client.execute_workflow(
            ExceptionWorkflow.run,
            "World",
            id="hello-activity-workflow-id",
            task_queue=TASK_QUEUE,
        )
    except Exception:
        logging.error("Error executing workflow")


async def run__workflow_childworkflow_activity_exception(client):
    """Throws an exception in an activity inside a child workflow"""
    try:
        await client.execute_workflow(
            ExceptionInChildWorkflow.run,
            "World",
            id="hello-activity-workflow-id",
            task_queue=TASK_QUEUE,
        )
    except Exception:
        logging.error("Error executing workflow")


async def main():
    logging.basicConfig(level=logging.INFO)

    client = await Client.connect("localhost:7233")

    async with Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[ExceptionWorkflow, ExceptionInChildWorkflow],
        activities=[return_error],
        debug_mode=True,
    ):
        await run__workflow_activity_exception(client)
        await run__workflow_childworkflow_activity_exception(client)


if __name__ == "__main__":
    asyncio.run(main())
