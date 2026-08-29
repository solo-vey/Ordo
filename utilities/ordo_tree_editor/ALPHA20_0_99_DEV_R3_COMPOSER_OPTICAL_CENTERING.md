# alpha.20.0.99-dev — Composer optical centering

The previous equal top/bottom padding did not solve the visible imbalance because the attach and send/stop controls still overrode the grid's centered alignment with `align-self:end`.

For single-line mode, attach, text input and send/stop are now explicitly centered on the same vertical axis. Multiline and expanded modes are unchanged.
