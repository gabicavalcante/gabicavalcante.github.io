+++
title = "Reliability in Django and Celery: how tasks get lost"
description = "Every way a Celery task can be lost between Django and the worker: transaction timing, broker failures, dead workers, and how to make retries safe."
date = "2026-08-12"
tags = ["python", "django", "celery", "reliability"]
+++

Every Django project I have worked on reaches the same moment. A request is too slow, someone moves the slow part into a Celery task, and the page gets fast. Quietly, the function has stopped being a function. It became a message, handed to a broker you do not control, to be run by a worker that might die halfway through. This post is my study guide for everything that can go wrong in that handoff, and what to do about each case.

<!--more-->

I wrote it from notes I collected while working on Django projects with Celery, plus the Vinta article [A guide to Django Celery tasks](https://www.vintasoftware.com/blog/guide-django-celery-tasks). Read that one too. Links to everything else are at the end.

## Where we start

Here is an ordinary function. It creates an order, emails the customer, and assigns a fulfillment center.

```python
@transaction.atomic
def create_order(cart, customer, source=ORDER_SOURCE.web, created_by=None):
    order = Order.objects.create(
        cart=cart,
        customer=customer,
        source=source,
        created_by=created_by,
    )

    send_order_confirmation_email(order)

    assign_fulfillment_center(order)
    return order
```

`@transaction.atomic` means the whole block commits together or not at all. Hold on to that, because the first thing Celery does is break it.

Right now this code is correct. It is only slow. The request takes four seconds, because the email goes out through a third party provider and assigning fulfillment scans inventory, and the customer is watching a spinner. So we move the slow part to Celery.

Report generation is the other classic case. I hit it [building PDFs out of LaTeX templates]({{< relref "creating-pdf-with-latex-and-django" >}}), and it ages into this same problem.

```python
@transaction.atomic
def create_order(cart, customer, source=ORDER_SOURCE.web, created_by=None):
    order = Order.objects.create(...)

    send_order_confirmation_email.delay(order=order)

    assign_fulfillment_center(order)
    return order


@celery_app.task
def send_order_confirmation_email(order):
    ...
```

That version has at least three bugs. Finding them is most of this post.

## What Celery actually is

```
APP  ─────────▶  Broker  ─────────▶  Worker
```

The APP is your Django process. It serializes the task and publishes it. The broker (RabbitMQ, Redis, SQS) holds the message until somebody takes it. The worker is a separate process, usually on a separate machine, with its own lifecycle and its own ways of dying.

Three processes, two network hops, no shared memory. Every guarantee you had inside a single Python process is now something you have to arrange yourself.

## Sending the task

### Pass simple data types

Look again at what we sent:

```python
send_order_confirmation_email.delay(
    order=order,   # a model instance
)
```

Since Celery 4.0 the default serializer is JSON, which supports a restricted set of types. Model instances and QuerySets are not among them. Pickle would accept them, and pickle is a remote code execution hole, so that is not a fix. Keep the arguments to integers, strings, lists and dicts.

```python
send_order_confirmation_email.delay(order_id=str(order.id))


@celery_app.task
def send_order_confirmation_email(order_id):
    order = Order.objects.get(id=order_id)
    ...
```

Serialization is only half the reason. The other half is staleness. A model instance is a snapshot of a row at the moment you queued the task. By the time a worker picks it up, the row may have changed, or somebody may have deleted it. Passing an ID forces the task to read the world as it is now instead of as it was.

So your task has to handle `DoesNotExist`. The row you queued for might be gone by the time anyone looks.

### Keep the payload small

Every argument gets copied into the broker's memory, and onto its disk if the queue is durable. Big payloads mean slow publishes and memory pressure, and some brokers cap message size outright. SQS stops at 256 KB.

So instead of pushing a 40 MB XML file through the queue, push a pointer to it.

```python
# app
blob_key = storage.upload(report_bytes)          # "reports/2026/08/abc123.xml"
process_report.delay(blob_key=blob_key)

# worker
@celery_app.task
def process_report(blob_key):
    report = storage.download(blob_key)
    ...
```

### The transaction trap

This is the bug I see most often, and the one that hides best.

```python
@transaction.atomic                          # transaction opens
def create_order(cart, customer, ...):
    order = Order.objects.create(...)        # not committed yet

    send_order_confirmation_email.delay(     # message sent right now
        order_id=str(order.id),
    )

    assign_fulfillment_center(order)         # slow, and might raise
    return order
```

The message goes out while the transaction is still open. What happens next depends on timing:

1. Django opens the transaction and inserts the order, uncommitted.
2. Django publishes `send_order_confirmation_email(order_id)`.
3. The broker delivers it to a worker.
4. The worker runs `Order.objects.get(id=...)` and gets `DoesNotExist`, because from its connection the row does not exist yet.
5. Meanwhile `assign_fulfillment_center` is still running.
6. Django commits, several hundred milliseconds too late.

The worse version of this is when `assign_fulfillment_center` raises. Then the transaction rolls back, so the order never existed, and you have emailed the customer to confirm it. That is the part worth sitting with: the database undid its half, and the email provider cannot undo yours.

It is timing dependent, and that is what makes it nasty. On your laptop, with one worker and a fast local database, the commit usually wins the race and everything passes. Under production load it starts failing, and the traceback points at the task, which is not where the bug is.

The fix is `transaction.on_commit`, which defers the publish until the transaction actually commits.

```python
@transaction.atomic
def create_order(cart, customer, ...):
    order = Order.objects.create(...)

    transaction.on_commit(
        lambda: send_order_confirmation_email.delay(
            order_id=str(order.id),
        )
    )

    assign_fulfillment_center(order)
    return order
```

Now the task is published only if the transaction commits. On rollback, no message.

### The on_commit gotcha

This one is easy to get wrong, and I have written it myself:

```python
# wrong
transaction.on_commit(
    send_order_confirmation_email.delay(order_id=oid)
)

# right
transaction.on_commit(
    lambda: send_order_confirmation_email.delay(order_id=oid)
)
```

In the wrong version, `.delay()` runs immediately, exactly as it did before, so the race is still there. You hand `on_commit` the resulting `AsyncResult` instead. If the transaction commits, Django tries to call it and you get `TypeError: 'AsyncResult' object is not callable`. If the transaction rolls back, Django never runs the callback, so there is no error at all. Just a task that fired for a transaction that never happened.

`on_commit` wants a callable. Pass a lambda, or `functools.partial`.

Celery 5.4 added a shortcut that removes the trap:

```python
send_order_confirmation_email.delay_on_commit(order_id=str(order.id))

send_order_confirmation_email.apply_async_on_commit(
    kwargs={"order_id": str(order.id)},
    countdown=30,
)
```

It wraps `transaction.on_commit` for you, so there is no lambda to forget. Outside a transaction it publishes immediately, the same as `.delay()`.

## Many ways to fail

With the sending side fixed, the message is on the wire. There are three places it can die.

```
APP  ──①──▶  Broker  ──②──▶  Worker ③
```

1. Never sent. The broker was unreachable, the publish failed, or the payload was rejected.
2. Sent but never delivered. The broker restarted, the queue was not durable, the message evaporated.
3. Delivered but never finished. The worker was killed, or the task raised.

Each one has a different answer.

## The message never reaches the broker

Celery already retries the publish. `task_publish_retry_policy` decides how hard it tries.

```python
task_publish_retry = True  # default

task_publish_retry_policy = {
    "max_retries": 3,       # then give up and raise
    "interval_start": 0,    # first retry is immediate
    "interval_step": 0.2,   # add 0.2s for each retry
    "interval_max": 0.2,
}
```

That covers connection blips: a broker restart, a dropped TCP connection. It does not cover a broker that is genuinely down for thirty seconds. When the retries run out, `.delay()` raises, and it raises inside your request.

Decide on purpose what should happen there. Should a broker outage return a 500 to the user, or should the request succeed and the work get picked up later? The second option is possible, and I get to it two sections down.

There is also a subtler failure. On RabbitMQ, a successful publish only means the bytes went into a socket. If you want the broker to confirm it stored the message, ask for it:

```python
broker_transport_options = {
    "confirm_publish": True,
}
```

Without it, a publish can succeed locally while the broker never keeps the message. With it, `.delay()` waits for the acknowledgement. It costs a round trip, which is worth paying for anything you cannot afford to lose.

## The broker loses it

Brokers lose messages more often than people expect. Redis without persistence keeps the queue in memory, so a restart is a clean slate. Non durable queues and transient delivery mode get dropped by RabbitMQ on restart. An unreplicated queue does not survive the node that held it. And under memory pressure, an eviction policy will happily discard keys.

Configuration helps here. Durable queues, persistent messages, replication, `appendonly yes`. But none of it is a guarantee, so plan for the message being gone.

The answer is persistence plus repetition. The database remembers, and Celery Beat retries. This is the single most useful pattern in this whole post.

### Step one: the database is the source of truth

Do not try to infer "did this happen?" from the queue. Record it.

```python
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    ...
    confirmation_email_sent_at = models.DateTimeField(null=True, blank=True)
```

A queue is a delivery mechanism, not a ledger. Once "not done yet" is a queryable state in your own database, recovery becomes possible.

### Step two: a Beat task that sweeps up

```python
@celery_app.task
def ensure_order_confirmation_emails():
    cutoff = timezone.now() - timedelta(minutes=5)
    order_ids = list(
        Order.objects.filter(
            confirmation_email_sent_at__isnull=True,
            created_at__lt=cutoff,
        )
        .values_list("id", flat=True)[:BATCH_SIZE]
    )

    for order_id in order_ids:
        send_order_confirmation_email.delay(order_id=str(order_id))

    LOGGER.info(
        "Re-queued pending confirmation emails. %(payload)s",
        {"payload": {"pending_count": len(order_ids)}},
    )
```

The happy path stays fast: `transaction.on_commit` fires the task and the email goes out in seconds, almost every time. The sad path heals itself. Broker down, message lost, worker killed halfway, it does not matter, because the column is still `NULL` and the next Beat run finds it. You have converted "lost forever" into "delayed by at most one Beat interval".

Two details in that code are load bearing.

The `cutoff` keeps the sweep from re-queueing orders whose first task is still running. Without it you manufacture exactly the duplicates you are trying to survive. Set the grace period comfortably above your p99 task duration.

`[:BATCH_SIZE]` matters for the same kind of reason. After a real outage the sweep might match four hundred thousand rows, and queueing all of them in one pass is its own incident.

Notice also what the log line contains: a count, and nothing else. Task arguments and log messages end up in log aggregators, error trackers and broker inspection tools, none of which are places for customer data. Log opaque IDs, never the data itself.

## The worker dies

By default, `task_acks_late = False`, which means the worker acknowledges the message as soon as it receives it, before running your code.

```
Broker ──▶ Worker    deliver
Broker ◀── Worker    ack, message deleted
           Worker    runs the task...
           Worker    killed
Broker              nothing left to redeliver
```

The message is gone, the work never happened, and nobody finds out. Turn it around:

```python
task_acks_late = True
```

Now the acknowledgement happens after the task finishes, so if the worker dies mid task, the broker gives the message to somebody else. That covers the worker being killed by the OOM killer, the machine restarting, the VM disappearing, a deploy, a scale down, a `kill -9`.

For long tasks, pair it with `worker_prefetch_multiplier = 1`. Otherwise a worker holds a batch of prefetched messages and takes all of them down with it.

Now the important limitation, which took me a while to internalize. `acks_late` is not a retry mechanism. If your task raises `DoesNotExist`, a `DatabaseError`, or any ordinary Python exception, the message is not redelivered. The task ran. It ran badly and it finished, so Celery acknowledges it and marks it `FAILURE`. Protecting against the worker dying and protecting against the task failing are two different problems, and `acks_late` only solves the first.

### task_reject_on_worker_lost

What about a catastrophic death: SIGKILL, a segfault, the OOM killer? That is `task_reject_on_worker_lost`, and the default is `False`, meaning the task is not redelivered.

That default sounds wrong until you think about a poison pill. If a specific message reliably kills whatever worker touches it, redelivering it forever will take down your entire pool, one worker at a time. The conservative default exists to stop that.

Setting it to `True` gets the task redelivered, which is what you want if you believe the crash was about the environment rather than the message. If you do flip it, cap the redeliveries and alert on them, or one bad message becomes an outage.

### Visibility timeout

Redis and SQS have no worker heartbeat. They use a timer instead: if nobody acknowledges within N seconds, assume the consumer is dead and hand the message to somebody else.

```python
broker_transport_options = {
    "visibility_timeout": 3600,  # seconds
}
```

A task that runs longer than that timeout gets redelivered while it is still running. Now the same task is executing twice, concurrently, on two workers. The classic symptom is a nightly report job that sent every customer two emails.

Set `visibility_timeout` above your longest task, including any `countdown` or ETA. Better still, keep tasks short enough that the question never comes up.

### Do not SIGKILL your workers on deploy

Celery 5.5 added a soft shutdown, a window between "stop taking new work" and "die".

```python
worker_soft_shutdown_timeout = 30
worker_enable_soft_shutdown_on_idle = True
```

A warm shutdown finishes the current tasks and exits. A soft shutdown gives a bounded grace period and then re-queues whatever is left. Without either, your orchestrator's SIGKILL is exactly the catastrophic loss case above, on every single deploy.

Check that your container platform's termination grace period is longer than this timeout. Otherwise you have configured a grace period that nothing honours.

## The task itself fails

The message arrived, the worker is healthy, and the code raises. That is governed by `task_acks_on_failure_or_timeout`, which defaults to `True`: a failed or timed out task is still acknowledged, with no automatic re-queue.

You can set it to `False`, so the message is not acknowledged and the broker eventually redelivers it. In practice that gives you infinite loops on deterministic bugs, with no backoff and no retry count. Leave it on `True` and handle failure inside the task, where you have the context to decide.

Explicit retries look like this:

```python
@celery_app.task(bind=True, default_retry_delay=60, max_retries=5)
def send_order_confirmation_email(self, order_id):
    try:
        response = email_provider.send(order_id=order_id)

        if response.status_code == 429:  # rate limited
            raise self.retry(
                exc=RateLimited("Rate limit hit"), countdown=300
            )

    except RequestException as exc:
        # transient network problem, try again soon
        raise self.retry(exc=exc, countdown=30)
    except Exception:
        # not retryable, let it fail loudly and reach the error tracker
        raise
```

Different failures deserve different delays. A rate limit wants minutes. A dropped connection wants seconds.

For the common case you can skip the `try/except` entirely:

```python
@celery_app.task(
    autoretry_for=(DatabaseError, RequestException),
    retry_kwargs={"max_retries": 5},
    retry_backoff=True,        # 1s, 2s, 4s, 8s...
    retry_backoff_max=600,
    retry_jitter=True,
)
def send_order_confirmation_email(order_id):
    ...
```

When a dependency goes down, thousands of tasks fail at the same instant. Without jitter they all retry at the same instant too, and the retry storm keeps the dependency down.

The judgement call is what deserves a retry at all. Connection timeouts, 429 and 503 from an upstream API, deadlocks and lock timeouts, a dependency in the middle of a deploy: all worth retrying. A `ValidationError`, a `DoesNotExist` for a row somebody deleted, a `TypeError` in your own code: retrying those five times just produces a slower failure, and it hides the error from whoever is reading the dashboard.

## Making retries safe

Every mechanism in this post makes duplicate execution more likely, not less. `acks_late`, `reject_on_worker_lost`, visibility timeouts, retries, Beat sweeps: all of them can run your task twice. At-least-once delivery is the guarantee you get, so the task has to be safe to run twice.

### Idempotency

A task is idempotent when running it twice with the same arguments has the same effect as running it once.

```python
# not idempotent: three redeliveries, three emails
def send_order_confirmation_email(order_id):
    order = Order.objects.get(id=order_id)
    send_email(order.customer.email, "Order confirmed!")


# better: the database decides whether the work is still needed
def send_order_confirmation_email(order_id):
    order = Order.objects.get(id=order_id)
    if not order.confirmation_email_sent_at:
        send_email(order.customer.email, "Order confirmed!")
        order.confirmation_email_sent_at = timezone.now()
        order.save()
```

Useful tools for this: `get_or_create` and `update_or_create` instead of a blind `create()`; unique constraints, so the database rejects the duplicate for you; idempotency keys, which most payment and messaging APIs accept and which the task ID fits nicely; state flags and timestamps like `confirmation_email_sent_at`.

The second version above still has a hole:

```python
if not order.confirmation_email_sent_at:   # worker A and worker B both read None
    send_email(...)                        # both send
    order.confirmation_email_sent_at = timezone.now()
    order.save()
```

Check-then-act is not atomic. Two workers can both pass the check before either writes. Close it by making the check and the write a single statement:

```python
updated = Order.objects.filter(
    pk=order_id, confirmation_email_sent_at__isnull=True
).update(confirmation_email_sent_at=timezone.now())

if updated:                    # only one worker gets 1 here
    send_email(...)
```

`update()` returns the number of rows it changed, so exactly one of the two workers sees `1` and the other sees `0`. A row lock with `select_for_update()` inside a transaction works too.

### Atomicity

An operation is atomic if it completes fully or not at all.

```python
# a crash in between leaves an order with no fulfillment center,
# and a retry creates a second order
def create_order(...):
    order = Order.objects.create(...)
    assign_fulfillment_center(order)


# a crash rolls everything back, and the retry starts clean
from django.db import transaction

@transaction.atomic
def create_order(...):
    order = Order.objects.create(...)
    assign_fulfillment_center(order)
```

Idempotency depends on atomicity. A half applied task is very hard to make safely repeatable, because you no longer know which half already happened.

### Side effects you cannot roll back

There is a warning in the Vinta guide that stuck with me: you can have side effects that are impossible to roll back, such as sending an email. The database will not un-send it. Payment captures, webhooks to third parties, files written to a bucket, all the same.

The trick is to couple the side effect to a database state change, so that even when the rollback cannot undo the act, it undoes the permission to repeat it:

```python
with transaction.atomic():
    updated = Order.objects.filter(
        pk=order_id, confirmation_email_sent_at__isnull=True
    ).update(confirmation_email_sent_at=timezone.now())

    if not updated:
        return  # somebody already did this

    send_email(...)   # if this raises, the timestamp rolls back
```

### Keep tasks short

Short tasks are cheaper to retry, because less work gets duplicated when they run again. They finish inside the visibility timeout and inside the shutdown grace period. They also fail sooner, so you find out sooner.

When you have a lot to do, fan out instead of looping:

```python
@celery_app.task
def process_pending_orders():
    for order_id in pending_order_ids()[:BATCH_SIZE]:
        process_order.delay(order_id=str(order_id))
```

A failure then costs you one order instead of the whole batch.

## Operating it

Correlation IDs are the thing I would set up first. Stamp the request ID onto the task and log it on both sides, because without it, connecting a 500 in the web logs to the task that caused it is archaeology.

After that: an error tracker with the Celery integration and `task_id` as a tag; APM if you have it, since Datadog and New Relic both trace Celery natively; Flower for a quick live view, keeping in mind that it shows you the present and not the past.

The metric I would actually alert on is queue depth, together with the age of the oldest message. Those are leading indicators. Error rate is not, because a worker pool that has quietly stopped consuming produces no errors at all, just a growing queue and a lot of confused users.

### Deploys will break your queue

A queue is a buffer of messages written by the old code and read by the new code.

```python
# old workers are running this
@celery_app.task
def send_order_confirmation_email(order_id): ...

# you deploy this
@celery_app.task
def send_order_confirmation_email(order_id, locale): ...
```

Every message already in the queue now fails with `TypeError`. Add new arguments with defaults, and never rename or remove one in the same deploy that starts using the new name. If you cannot avoid a breaking change, drain the queue first, or ship `send_order_confirmation_email_v2` alongside the old one and delete the old one a release later.

### Knowing when to stop

Celery's Canvas primitives (`chain`, `group`, `chord`) are fine for small compositions. As a workflow engine they hurt. Error handling across a chain is awkward, a failure in the middle of a chord is worse, and there is no built-in way to answer "where did this pipeline stop, and why?".

For multi step pipelines over millions of records, use something built for it, like Prefect, Temporal or Airflow. Retries, visibility and resume-from-step are their entire job. Celery is an excellent task queue and a mediocre workflow engine, so I try to use it as the former.

## Settings worth knowing

| Setting | Value | Why |
|---|---|---|
| `task_acks_late` | `True` | Survive the worker dying mid task |
| `worker_prefetch_multiplier` | `1` | Do not lose a whole prefetched batch |
| `task_reject_on_worker_lost` | `False` (default) | Avoid poison pill loops |
| `task_acks_on_failure_or_timeout` | `True` (default) | Handle failure explicitly instead |
| `task_serializer` | `"json"` (default) | Never pickle |
| `broker_transport_options.confirm_publish` | `True` | RabbitMQ: real publish confirms |
| `broker_transport_options.visibility_timeout` | above your longest task | Redis and SQS: avoid concurrent redelivery |
| `task_soft_time_limit` and `task_time_limit` | set both | Bound the damage of a hung task |
| `worker_soft_shutdown_timeout` | around 30 | Graceful deploys, Celery 5.5+ |
| `result_expires` | tune it | Do not let the result backend grow forever |

Several of those are already the default. The point is knowing why they are, so you can tell when your case is the exception.

## The checklist

When I send a task:

- Simple types only, IDs instead of objects
- Small payloads, with blob storage for anything big
- `delay_on_commit`, or `transaction.on_commit(lambda: ...)`
- The task handles `DoesNotExist`

When it runs:

- `task_acks_late = True`
- Retries scoped to transient errors, with backoff and jitter
- Idempotent
- Atomic
- Short

When it fails anyway:

- State lives in the database, not in the queue
- A Beat sweep re-queues whatever is still pending
- The sweep has a grace period and a batch size

While operating it:

- Correlation IDs from request to task
- Alerts on queue depth and oldest message age
- Logs carry opaque IDs, never customer data
- Task signatures change in a backward compatible way

Assume every task can be lost, duplicated, or run out of order, and design for all three.

## References

- [A guide to Django Celery tasks](https://www.vintasoftware.com/blog/guide-django-celery-tasks)
- [Celery: an overview of the architecture and how it works](https://www.vintasoftware.com/blog/celery-overview-archtecture-and-how-it-works)
- [Celery in the wild: tips and tricks to run async tasks in the real world](https://www.vintasoftware.com/blog/celery-wild-tips-and-tricks-run-async-tasks-real-world)
- [Dealing with resource-consuming tasks on Celery](https://www.vintasoftware.com/blog/dealing-resource-consuming-tasks-celery)
- [Celery documentation](https://docs.celeryq.dev/en/stable/), and specifically [should I use retry or acks_late?](https://docs.celeryq.dev/en/stable/faq.html#should-i-use-retry-or-acks-late) and [security serializers](https://docs.celeryq.dev/en/stable/userguide/security.html#security-serializers)
- [Working with asynchronous Celery tasks: lessons learned](https://blog.daftcode.pl/working-with-asynchronous-celery-tasks-lessons-learned-32bb7495586b)
