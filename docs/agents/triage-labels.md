# Triage Labels

The skills speak in terms of five canonical triage roles. This file maps those roles to the actual label strings used in this repo's issue tracker.

Because issues are local markdown files, each label is written as the value of a `Status:` line near the top of the issue file.

| Label in mattpocock/skills | Label in our tracker | Meaning                                  |
| -------------------------- | -------------------- | ---------------------------------------- |
| `needs-triage`             | `needs-triage`       | Maintainer needs to evaluate this issue  |
| `needs-info`               | `needs-info`         | Waiting on reporter for more information |
| `ready-for-agent`          | `ready-for-agent`    | Fully specified, ready for an AFK agent  |
| `ready-for-human`          | `ready-for-human`    | Requires human implementation            |
| `wontfix`                  | `wontfix`            | Will not be actioned                     |

A `Status:` line also carries one non-triage value: `resolved`, meaning the issue shipped (the release is recorded in a `Done in:` line). It is a terminal state, not a triage role.

When a skill mentions a role (e.g. "apply the AFK-ready triage label"), use the corresponding `Status:` value from this table.

Edit the "Label in our tracker" column to match whatever vocabulary you actually use.
