+++
title = "Demystifying Supabase authorization"
description = "Supabase decides what a user may do with two Postgres checks: table privileges granted to a role, then Row Level Security (RLS) policies that read the user's id from their JWT."
date = "2026-09-08"
draft = false
tags = ["postgres", "supabase", "security", "rls"]
+++

I was playing with Supabase and Next.js, after years of Postgres and Django, and some concepts were new for me. Working out what they meant took me through Postgres roles, privileges, policies, and a couple of things I had assumed for years without checking. Maybe what was new for me is new for you too :)

<!--more-->

## The setup

Supabase is one way to put a Postgres database behind a Next.js app. It is a layer over Postgres. It handles authentication and serves the tables as an API through PostgREST, and each of those is a separate server behind one URL. That is how I ended up there: I wanted Postgres and I also wanted to test a new technology to serve it with Next.js.

The app is a personal finance tracker. Two tables matter here, `cards`, meaning credit cards, and `transactions`. A transaction belongs to a card, and both belong to whoever created them.

Everything below is real output from a local Supabase stack, Postgres 17. There are two test users, Ana and Bruno. Ana owns one card and one transaction, Bruno owns nothing, and the whole question is what each of them can see.

## What Django never made me think about

In Django the browser never touches the database:

{{< preformatted >}}
browser  →  Django view  →  Postgres   (as ONE app role)
{{< /preformatted >}}

There is one database user, it holds full privileges, and authorization happens in Python:

```python
Transaction.objects.filter(user=request.user)
```

Postgres has no idea who the end user is, and does not need to. The security boundary is your view. Forget that filter in one view and that endpoint leaks everything, which is the failure mode Django developers learn to watch for.

Supabase puts an HTTP server in front of Postgres, so the shape changes. That server is PostgREST, a separate open source project that reads your schema and serves it as a REST API. Supabase runs it for you, and my Next.js app makes HTTP calls to it:

{{< preformatted >}}
browser  →  PostgREST  →  Postgres   (as anon or authenticated)
{{< /preformatted >}}

The end user's identity now arrives at the database. It arrives as a JWT, a signed token that Supabase Auth issues when someone logs in to the app. The browser keeps it and sends it with every request, and PostgREST checks its signature and puts the user's id on the database connection, where Postgres can read it.

Logging in goes to Supabase Auth, not to PostgREST. The app sends it the email and password. Supabase Auth connects to Postgres as its own role, `supabase_auth_admin`, checks the password against the `auth.users` table and returns the JWT. Until then, every request the app sends to PostgREST carries only the publishable key, so it runs as `anon`.

So the database is where authorization has to happen, and the roles it uses are reachable from the internet. That second part is what I had not thought about. It makes authentication and authorization in Postgres critical. In Django I handled both in the app layer, and Postgres only ever saw my one app role. Every privilege the anonymous role holds in Supabase is a privilege anyone with your publishable key holds.

## Two gates, applied in order

There are two independent checks, done by Postgres and applied in order, and they are the key to understanding how Supabase authorization works:

{{< preformatted >}}
        Gate 1: PRIVILEGES     "may this role touch this table at all?"
              granted with GRANT
                    |
        Gate 2: POLICIES       "which rows may it see?"
              Row Level Security, created with CREATE POLICY
{{< /preformatted >}}

Gate 1 is the lock on the room door. Gate 2 decides which filing cabinets inside you can open.

Neither gate is a Supabase invention. Gate 1 is `GRANT`, which is as old as Postgres. Gate 2 is Row Level Security (RLS), in Postgres since 9.5. You turn it on per table, and each policy is one rule saying which rows a role may see or change. What Supabase adds is the set of roles below and the machinery that attaches a web request to one of them.

## What a role is, and the one attribute that matters

Postgres has no separate concept of a user. `CREATE USER` is `CREATE ROLE ... LOGIN` spelled differently, and both write a row to the same `pg_roles`. Everything in the table below is a role, `postgres` included, and "group" and "user" are conventions rather than kinds.

A role carries two kinds of power, and neither is a table privilege. Attributes are permissions on the role itself, set with `CREATE ROLE` or `ALTER ROLE`: `LOGIN`, `SUPERUSER`, `BYPASSRLS`, `INHERIT`, which is what the table below lists. Membership in another role, granted with `GRANT one TO other`, lets a role reach what that other one holds. `GRANT` doing both jobs is what kept this muddled for me. `grant select on cards to authenticated` is Gate 1, a privilege on a table; `grant authenticated to authenticator` names no table at all. Same keyword, two unrelated operations, and it is why the GRANT page is in the references.

Four of the five roles below come from the stack rather than from Postgres. `authenticator` is PostgREST's own convention, the role it opens its pooled connections as. `anon`, `authenticated` and `service_role` are created by Supabase in every project, and each one is what you get by presenting a particular key: the key that ships in the browser gets you `anon`, a signed-in user's token gets you `authenticated`, and the secret key gets you `service_role`, which is meant for a server you control. PostgREST reads the role out of the token and switches to it for that one request. `postgres` is the only one Postgres itself would have given you.

```
    rolname    | superuser | can_login | bypasses_rls
---------------+-----------+-----------+--------------
 postgres      |     f     |     t     |      t
 authenticator |     f     |     t     |      f
 anon          |     f     |     f     |      f
 authenticated |     f     |     f     |      f
 service_role  |     f     |     f     |      t
```

Only two can log in. `anon` and `authenticated` cannot, which confused me until I understood that they are not connection identities at all. They are personas that one connection switches between, per request.

PostgREST holds a pool of connections logged in as `authenticator`, and per request it does roughly this:

```sql
set local role authenticated;
set local request.jwt.claims = '{"sub":"<the user id>"}';
```

`set local` is transaction scoped, so the role resets when the transaction ends.

`authenticator` is deliberately powerless:

{{< preformatted >}}
authenticator: has SELECT on cards → false
authenticated: has SELECT on cards → true
{{< /preformatted >}}

It holds no table privileges of its own. Its only power is membership, the right to become one of the other three. And it is `NOINHERIT`:

```
    rolname    | rolinherit
---------------+------------
 authenticator |     f
 authenticated |     t
```

That flag is the good part of the design. If `authenticator` inherited, every pooled connection would hold full privileges all the time, and a bug that forgot to `set role` would expose everything. With `NOINHERIT`, forgetting to set the role leaves you with no access at all. It fails in the safe direction.

## Running the same query as each role

Here is the same query against one row in `cards`, a credit card that belongs to Ana, run as different roles, with and without a user's token. The role and the token are all Postgres has to go on:

{{< preformatted >}}
as postgres (owner)      → 1 row
as authenticated, no JWT → 0 rows
as authenticated, Ana    → 1 row
as authenticated, Bruno  → 0 rows
as service_role          → ERROR: permission denied for table cards
{{< /preformatted >}}

The last line surprised me. The roles table in the previous section shows that `service_role` bypasses RLS, so I expected it to see every row. It never got the chance, because I had granted it nothing, and Gate 1 comes first. Bypassing policies is not the same as holding privileges.

The failure modes are worth committing to memory, because they look nothing alike:

- A privilege problem raises `permission denied`.
- A policy problem returns an empty result, silently.

When a query mysteriously comes back empty, it is Gate 2.

## How the user's id reaches a policy

A policy needs something to compare against, which means every table carries the owner:

```sql
user_id uuid not null default auth.uid() references auth.users (id)
```

`auth.uid()` is a small SQL function that reads what PostgREST put on the connection:

```sql
CREATE OR REPLACE FUNCTION auth.uid() RETURNS uuid AS $$
  select coalesce(
    nullif(current_setting('request.jwt.claim.sub', true), ''),
    (nullif(current_setting('request.jwt.claims', true), '')::jsonb ->> 'sub')
  )::uuid
$$
```

With no session it returns NULL, `user_id = NULL` is never true, and nothing comes back. That is the `authenticated, no JWT` line in the output above.

The policy itself is then unremarkable:

```sql
create policy transactions_select_own on transactions
  for select to authenticated using (user_id = auth.uid());
```

One thing I got wrong at first: a policy for SQL `UPDATE` needs two clauses, not one.

```sql
create policy transactions_update_own on transactions
  for update to authenticated
  using (user_id = auth.uid())          -- which rows I may update
  with check (user_id = auth.uid());    -- what they may become
```

`using` restricts which rows the statement may touch. `with check` validates the result. Without the second clause I could update my own row and set `user_id` to somebody else, handing it away. `insert` needs only `with check`, because there is no existing row to filter.

## Who skips the policies

Two separate reasons a role ignores RLS, and I had only known about one:

```
    tablename     | tableowner
------------------+------------
 cards            | postgres
 transactions     | postgres
```

The `BYPASSRLS` attribute is the well-known one. The second is ownership: **a table's owner is exempt from its policies by default**, attribute or no attribute. `postgres` here has both.

This is the detail that decides an architectural question. An ORM like Prisma or Drizzle connecting with the standard database URL connects as the owner. Your policies are then not violated, they are never consulted. Nothing errors, the tests pass, and the protection is simply absent. `alter table x force row level security` makes even the owner obey, at the cost of breaking your own migrations.

## The join table needs more than a policy

My transactions can carry several tags, so there is a join table. Protect `transactions` and `tags`, leave the join open, and you leak which tags sit on which transactions.

Giving it a `user_id` column and the same policy looks sufficient. It is not, and this is the part I would have shipped without noticing. A foreign key checks that the parent row **exists**, never who owns it:

{{< preformatted >}}
NAIVE   mismatched owner → ACCEPTED (the flaw)
{{< /preformatted >}}

Bruno can insert a link row claiming he owns it, pointing at Ana's transaction. Both foreign keys are satisfied. Then his own policy on the join table shows it to him.

The fix is a composite foreign key:

```sql
create table transactions (
  id       uuid primary key default gen_random_uuid(),
  user_id  uuid not null default auth.uid(),
  unique (id, user_id)            -- so a composite key can reference the pair
);

create table transaction_tags (
  transaction_id uuid not null,
  tag_id         uuid not null,
  user_id        uuid not null default auth.uid(),
  primary key (transaction_id, tag_id),
  foreign key (transaction_id, user_id) references transactions (id, user_id),
  foreign key (tag_id, user_id)         references tags (id, user_id)
);
```

Now the **pair** has to exist:

{{< preformatted >}}
GUARDED mismatched owner → REJECTED by the composite FK
GUARDED matching owner   → ACCEPTED
{{< /preformatted >}}

The `unique (id, user_id)` looks redundant, since `id` is already the primary key. Postgres requires a unique constraint on exactly the columns a foreign key references and will not infer it.

I like this better than the alternative, which is deriving ownership with a subquery in the policy. That works, but RLS applies inside policy expressions too, so a policy reading `transactions` gets tangled in that table's own policies. Getting out of that usually means a `security definer` function, which runs as its owner and so ignores them. The composite key gives the same guarantee with no machinery, and it makes the illegal state unrepresentable rather than merely checked.

## What RLS does not cover

Supabase leaves `TRUNCATE`, `REFERENCES` and `TRIGGER` granted to `anon` and `authenticated` on new tables. RLS filters rows; `TRUNCATE` empties the table wholesale, so no policy applies to it:

{{< preformatted >}}
authenticated TRUNCATE transaction_tags      → SUCCEEDED
anon          TRUNCATE transaction_tags      → SUCCEEDED
authenticated TRUNCATE transactions CASCADE  → SUCCEEDED (took both tables)
{{< /preformatted >}}

I wrote "real hole" in my notes at that point, and then checked whether it was reachable. It is not. PostgREST exposes no truncate verb, and neither role can open a connection, so nothing can get far enough to issue one. It is an unnecessary privilege that RLS cannot mitigate, which is a good enough reason to revoke it, and not a vulnerability. I am recording both the finding and the correction because the gap between them is the whole lesson.

## Testing it

Policies are worth testing, and the tests are cheap once you know the trick. Connect as the owner, since that is the only way to create the `auth.users` rows a policy test needs, then switch role before asserting:

```ts
async function actAs(role: 'authenticated' | 'anon' | 'service_role', userId?: string) {
  await client.query('reset role')
  await client.query(`set local role ${role}`)
  await client.query('select set_config($1, $2, true)', [
    'request.jwt.claims',
    userId === undefined ? '' : JSON.stringify({ sub: userId }),
  ])
}
```

`set_config` rather than `SET`, because `SET` is a utility statement and will not take a parameter. The third argument, `true`, means transaction local.

Every test runs inside a transaction that is rolled back, so fixtures leave nothing behind and order does not matter. Ten of them cover the owner reading their own row, a second account seeing nothing, an insert that forges another `user_id`, an update that tries to reassign one, `anon` being denied outright, and the join table refusing a cross-owner link.

One decision worth making deliberately: these tests need a database, so they cannot be part of a default test run that has to work anywhere. I put them in a separate test project that **fails** when the database is unreachable, rather than skipping. A security test that quietly does not run is worse than no test, because it reports success.

## Three things I had wrong

**That a denial meant something was broken.** `service_role` being refused was correct behavior and better than the default. I had merged privileges and policies into one idea, so a role that bypasses one being stopped by the other looked like a contradiction.

**That the leftover `TRUNCATE` was exploitable.** It succeeded in a test, which is not the same as being reachable. I named it a hole before checking, and the checking took four commands.

**That `postgres` was the superuser.** It is not:

```
=== who is actually a superuser here? ===
    rolname
----------------
 supabase_admin
```

`postgres` has `rolsuper = f`. It bypasses RLS and owns the tables, which is enough to explain everything I saw, and Supabase deliberately keeps it below superuser.

## Before you deploy

What I check now before a Supabase project goes live:

- [ ] Every table the API exposes has RLS turned on, with a policy for each command the app uses.
- [ ] `anon` and `authenticated` hold only the table privileges the app needs. `TRUNCATE`, `REFERENCES` and `TRIGGER` are revoked, because RLS does not limit them.
- [ ] Every `update` policy has both `using` and `with check`. Every `insert` policy has `with check`.
- [ ] Every table has a `user_id` column that defaults to `auth.uid()`, and every join table has a composite foreign key that includes it.
- [ ] The secret key stays on servers I control. It never goes in the browser, a shipped app or the repo.
- [ ] Nothing that connects as the table owner, like an ORM using the standard database URL, is trusted to respect RLS.
- [ ] The policy tests run against a real database and fail when it is unreachable.

## Where I stop

RLS moves the ownership filter from code that can forget it into a database that cannot. That is the trade I wanted for financial data. The cost is that Postgres privileges become something I have to reason about, and defaults that were harmless behind Django are now worth reading.

## References

- [Row Security Policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html) in the Postgres manual, which is where the owner exemption and `FORCE ROW LEVEL SECURITY` are documented
- [GRANT](https://www.postgresql.org/docs/current/sql-grant.html), for the two different things the same keyword does
- [Supabase API keys](https://supabase.com/docs/guides/api/api-keys), which is blunt about the secret key: "A secret key bypasses every Row Level Security policy you have. Never put one in a browser, a shipped application, or source control."
- [Going into production](https://supabase.com/docs/guides/deployment/going-into-prod), the checklist that sent me to look at network restrictions and SSL enforcement
- [Effective ML revisited](https://blog.janestreet.com/effective-ml-revisited/), Yaron Minsky, where "make illegal states unrepresentable" comes from
