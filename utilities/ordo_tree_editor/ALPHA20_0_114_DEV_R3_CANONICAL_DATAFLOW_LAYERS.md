# alpha.20.0.114-dev

Auto Data Flow uses five canonical semantic layers in a fixed order:
1. Analyst input
2. Transformation
3. Derived state
4. Document
5. Archive / package

Selecting an entity renders only its complete upstream/downstream lineage and repacks that focused subgraph using the same five layers. Clicking empty graph space clears the focus and restores the complete graph. Free layout remains available for the complete graph; Auto always restores canonical semantic layering.
