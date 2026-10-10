import sys, xatra, pandas as pd
m = xatra.Map()
import random
random.seed(3)
gids = [f"IND.{i}" for i in range(1, 37)]
df = pd.DataFrame({"GID": gids, "literacy": [random.uniform(55, 95) for _ in gids]}).set_index("GID")
m.Dataframe(df)
m.TitleBox("<h2>Literacy rate</h2><p>Percent, by state (illustrative)</p>")
m.show(out_html=sys.argv[1])
