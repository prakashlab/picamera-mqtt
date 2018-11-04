"""Convenience code for running asyncio code."""
import asyncio
import contextlib
import logging
import signal

logger = logging.getLogger(__name__)

def raise_keyboard_interrupt(signum, frame):
    """Raise a KeyboardInterrupt.

    Useful for translating SIGINTs sent from other processes into a KeyboardInterrupt.
    """
    raise KeyboardInterrupt

def register_keyboard_interrupt_signals(signals=(signal.SIGINT,)):
    """Register the specified signals to raise keyboard interrupts."""
    for interrupt_signal in signals:
        signal.signal(interrupt_signal, raise_keyboard_interrupt)

def cancel_task(task, loop):
    """Cancel a task and wait for it to exit."""
    task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        loop.run_until_complete(task)

def cancel_all_tasks(loop):
    """Cancel all tasks and wait for them to exit."""
    pending = asyncio.Task.all_tasks(loop=loop)
    for task in pending:
        task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        loop.run_until_complete(asyncio.gather(*pending))

def run_function(
        function, function_args=(), function_kwargs={},
        cancel_pending_on_interrupt=True
    ):
    """Run a function and handle interrupt signals."""
    loop = asyncio.get_event_loop()
    task = loop.create_task(function(*function_args, **function_kwargs))
    with contextlib.suppress(KeyboardInterrupt):
        try:
            loop.run_until_complete(task)
        except KeyboardInterrupt:
            logger.info('Stopping all tasks and quitting...')
            if cancel_pending_on_interrupt:
                cancel_all_tasks(loop)
            else:
                cancel_task(task, loop)
        finally:
            loop.close()
