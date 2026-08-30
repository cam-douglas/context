# Context flow and state matrix

| State | Trigger | UI | Next |
|---|---|---|---|
| empty | device load, sidecar up | Prompt enabled, Run/Apply disabled until prompt + context | running |
| sidecar-down | health fail | Prompt/Run/Analyze/Apply disabled | empty when health returns |
| running | Run with non-empty prompt | progress | preview or error |
| preview | intent + arrange JSON valid | preview list, Audition/Apply enabled | applying or auditioning |
| auditioning | Audition | wet on host track, Apply still available | preview |
| applying | Apply | controls disabled | success or error |
| success | LOM write ok | undo hint | empty or preview |
| error | empty prompt, bad drop-in, analyze/apply fail | error line | empty or preview |

Modes are fields on one surface (track follow, drop-in, reference, project), not separate apps.
