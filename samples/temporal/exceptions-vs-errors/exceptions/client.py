#!/usr/bin/env python3

""" Example showing how exceptions are wrapped by the temporal framework.  """

import asyncio
import logging

from temporalio.client import Client, WorkflowFailureError
from worker import (TASK_QUEUE, ExceptionInChildWorkflow,
                    ExceptionInGoActivityWorkflow, ExceptionWorkflow,
                    NonRetryableExceptionWorkflow)


async def run_workflow_activity_exception(client: Client):
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


async def run_workflow_activity_nonretryableexception(client: Client):
    """Throws an exception in the activity"""
    try:
        await client.execute_workflow(
            NonRetryableExceptionWorkflow.run,
            "World",
            id="hello-activity-workflow-id",
            task_queue=TASK_QUEUE,
        )
    except Exception:
        logging.error("Error executing workflow")


async def run_workflow_childworkflow_activity_exception(client: Client):
    """Throws an exception in an activity inside a child workflow"""
    try:
        await client.execute_workflow(
            ExceptionInChildWorkflow.run,
            "World",
            id="hello-activity-workflow-id",
            task_queue=TASK_QUEUE,
        )
    except WorkflowFailureError as e:  # noqa
        logging.exception(f"Error executing workflow: {e}")


async def run_workflow_go_activity_exception(client: Client):
    """Throws an exception in a Go activity"""
    try:
        await client.execute_workflow(
            ExceptionInGoActivityWorkflow.run,
            "World",
            id="hello-activity-workflow-id",
            task_queue=TASK_QUEUE,
        )
    except Exception as e:
        logging.error(f"Error executing workflow: {e}")


async def main():
    logging.basicConfig(level=logging.INFO)

    client = await Client.connect("localhost:7233")
    # await run_workflow_activity_exception(client)
    # await run_workflow_activity_nonretryableexception(client)
    # await run_workflow_childworkflow_activity_exception(client)
    await run_workflow_go_activity_exception(client)


if __name__ == "__main__":
    asyncio.run(main())
