# alpha.20.0.145-dev

Fixes Model Chat artifact delivery:
- adds generic `workspace.archive`;
- discovers files created/changed anywhere in the workspace turn, excluding uploads/extracted source material;
- adds direct binary workspace-file download endpoint with Content-Disposition;
- file cards use real binary downloads instead of JSON/sandbox markdown links.
