# alpha.20.0.118-dev

Fixed a merge regression introduced while combining focused Data Flow slicing with the All/Issues filter.
The bundle accidentally contained two `lineageVisibleNodeIds()` definitions. The obsolete later definition overrode the new implementation and attempted to spread the structured `{visible, transit}` result returned by `lineageMonotonicReachable()`, causing `TypeError: upstream is not iterable` whenever a Data Flow node was selected.

The obsolete duplicate is removed. Focused selection now always uses `lineageFocusedSlice(...).visible`.
