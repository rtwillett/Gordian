# Gordian - Untangling the Gordian Knot of OSint

## Original Team Members
- Eric Brichetto (aka BUTTS)
- Ryan Willett (aka Mith)
- John Rodley (aka T-REX)


## Tool Description
Originally written as a graph analysis and file conversion tool as part of the 1st Bellingcat Hackathon. This fork is refactoring and expanding the code into a more robust CLI based tool and graph toolkit module for data science workflows.

## Installation
```
pip install git+ssh://git@github.com/rtwillett/Gordian.git
```

## CLI Usage
Description

## Future Directions
- Separating I/O file reading functionality from graph analysis and graph data visualization
- Convert all I/O files (Excel, CSV, GML, etc) to GML for standardization of graph representation and edgelist/nodelist for exports to more human readable formats.
- Provide convenient means to filter graphs, show graph outputs, and save useful file outputs.
