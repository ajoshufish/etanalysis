Analysis project for local gym occupancy of east coast Earth Treks locations.

The pandemic created multiple issues where we had both a safety concern regarding going to Earth Treks gyms, as well as a scarcity problem as they capped the amoutn of individuals that were allowed to enter their facilities at any given time. 

It's easier to mitigate some of this if one is, say, only going to a bouldering gym, such as Earth Treks Hampden. However, one is a bit more rooted in place to a specific physical location (or, perhaps, 3-dimensional slice of location when climbing) if the goal for the day is route climbingt instead.

Thus, this project. We pull in the data that Earth Treks publishes to the web so we can look for trends and identify the best times to go to find days or times of day when gyms are less crowded.

Ingest:  Python script snagging the information --> Pandas --> GSpread Dataframe --> Google Sheet

Analysis: Google Sheet --> GSpread --> Pandas --> Streamlit