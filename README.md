# NCI resource tools

A series of scripts and notebooks to help automate the monitoring and planning
of gadi resources for the Centre of Excellence 21st Century Weather.

## Gadi stocktakes

The `Generate Gadi stocktakes` GitHub Action submits a PBS scan on Gadi every
48 hours. The scan loads the `rudu` module and runs `rudu-linux` for the five
`/g/data` projects and four `/scratch` projects, writing both reports under
`.stocktake_runs/`. A separate
Action check runs every two hours. After both reports are complete, it connects
to the Gadi login node and commits and pushes the two HTML pages in `docs/`.
Run the Action manually with `workflow_dispatch` to start a scan immediately.

The Action uses the same `HOST`, `USER`, `SSH_KEY`, and `PASSPHRASE` secrets as
the dashboard Action. The Gadi account needs `qsub` access under `gb02` and
GitHub push credentials on the login node. PBS output is in `.stocktake_logs/`;
each run's reports and status are in `.stocktake_runs/`.
