import asyncio
import logging
from dataclasses import dataclass
from datetime import timedelta

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.common import RetryPolicy
from temporalio.exceptions import (ActivityError, ApplicationError,
                                   ChildWorkflowError, FailureError)
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


class UserError(ApplicationError):
    """An error that is not retryable."""

    def __init__(self, message):
        super().__init__(message, non_retryable=True)


class SystemError(ApplicationError):
    """An error that is retryable."""

    pass


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


@workflow.defn(sandboxed=False)
class ExceptionInGoActivityWorkflow:
    @workflow.run
    async def run(self, name: str) -> ComposeGreetingOutput:
        try:
            output = await workflow.execute_activity(
                "GetGreeting",
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=retry_policy,
                task_queue="greetings",
            )
            return output
        except ActivityError as e:
            logging.error(f"(Workflow) Activity error: {e.cause}")
            raise
        except Exception as e:
            logging.error(f"Uncaught exception in workflow of type {type(e)}")
            raise


@workflow.defn(sandboxed=False)
class ExceptionWorkflow:
    @workflow.run
    async def run(self, name: str) -> ComposeGreetingOutput:
        try:
            return await workflow.execute_activity(
                throw_exception,
                ComposeGreetingInput("Hello", name),
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=retry_policy,
            )
        except ActivityError as e:
            logging.error(f"(Workflow) Activity error: {e.cause}")
            raise
        except Exception as e:
            logging.error(f"Uncaught exception in workflow of type {type(e)}")
            raise


@workflow.defn(sandboxed=False)
class NonRetryableExceptionWorkflow:
    @workflow.run
    async def run(self, name: str) -> ComposeGreetingOutput:
        try:
            return await workflow.execute_activity(
                throw_non_retryable_exception,
                ComposeGreetingInput("Hello", name),
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=retry_policy,
            )
        except FailureError as e:
            logging.info(f"(Workflow) FailureError.cause: {e.cause}")
            raise
        except Exception as e:
            logging.error(f"Exception in workflow of type {type(e)}")
            raise


@workflow.defn(sandboxed=False)
class ExceptionInChildWorkflow:
    @workflow.run
    async def run(self, name: str) -> ComposeGreetingOutput:
        try:
            return await workflow.execute_child_workflow(
                workflow=ExceptionWorkflow, arg=name  # type: ignore
            )
        except ChildWorkflowError as e:  # noqa
            logging.exception("(Parent Workflow) Exception in child workflow")
            raise


async def main():
    logging.basicConfig(level=logging.INFO)

    client = await Client.connect("localhost:7233")

    await Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[
            ExceptionWorkflow,
            ExceptionInChildWorkflow,
            NonRetryableExceptionWorkflow,
            ExceptionInGoActivityWorkflow,
        ],
        activities=[throw_exception, throw_non_retryable_exception],
        debug_mode=True,
    ).run()


if __name__ == "__main__":
    asyncio.run(main())
