# ADS talk deck

A short deck for presenting ADS at 1920×1080, with room for a live demo.
For a single shareable slide, use [`../ads-one-pager.png`](../ads-one-pager.png).

| # | Slide | Covers |
|---|---|---|
| 1 | `01-cold-start` | why current approaches fail, agents start cold, fragmented knowledge |
| 2 | `02-state-not-path` | enter ADS, define the state, not the path |
| 3 | `03-vs-workflows` | comparison with workflow frameworks |
| | *live demo* | example: an agent starts a task in an ADS repo, `ads-lint` |
| 4 | `04-takeaway` | key takeaway |
| 5 | `../ads-one-pager.png` | everything, as a handout |

Edit the HTML, then re-render the PNGs with any Chromium:

```sh
for f in 0*.html; do
  chromium --headless=new --hide-scrollbars --allow-file-access-from-files \
    --window-size=1920,1080 --screenshot="$PWD/${f%.html}.png" "file://$PWD/$f"
done
```
