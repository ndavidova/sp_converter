### Todo

- [ ] Solve the issue of TOC, sometimes it conflicts with chapter mapping, could be removed manually after some warning / exception or it could be automated
- [ ] Have a look at parsing 206bc84a380b29ac - there is .0 in every top chapter, there can be more such cases
- [ ] Have a look at 0a38b4739f62ff43, 45797cfda8571046 - could be the TOC problem
- [ ] Unify the matching logic from chapter mapping and table names mapping
- [ ] Inspect different files on the edge of acceptable limit as well as in the acceptable limit, look for errors that can be allowed to improve the parsing 

### In Progress


### Done ✓
- [x] Implement chapter_mapper
- [x] Use regexes for effective pattern matching
- [x] Test chapter_mapper against multiple files
- [x] Solve the issue of Hyphen-minus (-, U+002D) VS En dash (–, U+2013) VS Em dash (—, U+2014) as this will probably cause problems
- [x] Make Github public
- [x] Support 3rd level hierarchy when applicable (e.g algorithms)
- [x] Use Python library https://sec-certs.org/docs/index.html to filter out data from 2023 and make analysis of how many were processed by chapter_mapper
- [x] Fix the problem of separators being in the final output for multiline tables
- [x] Statistics on chapter_mapper output (something to include in the thesis)
- [x] Recreate more parts of the document into classes following the algorithm example 



