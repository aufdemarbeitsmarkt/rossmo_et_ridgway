
## Summary

## Rossmo Overview

Use `glue:math` to display algorithm. 
https://jupyterbook.org/en/stable/content/executable/output-insert.html?highlight=glue#the-glue-math-directive


- The value of fff controling how fast the probability decays beyond the buffer zone
- The value of ggg controling how fast the probability decays inside the buffer zone
## Data

```{glue:} df_body_locations_final
```

```{glue:} df_disappearances_final
```

```{glue:} df_ridgway_final
```

Add Google Map here.

---



```{glue:} ridgway_map
```

```{raw} html
:file: /my-plot.html
```

## THE MAP
```{raw} html
:file: rossmo_et_ridgway/maps/None.html
```


https://pandas.pydata.org/pandas-docs/stable/user_guide/style.html



---
https://jeremykun.com/2011/07/20/serial-killers/
(f = 0.5, g = 1)

Specifically, 
>We admit to have no idea why they need to be related, and cannot find a good explanation in Rossmo’s novel of a dissertation. Instead, Rossmo claims both parameters should be equal. For the purposes of this blog we find their exact values irrelevant, and put them somewhere between a half and two thirds.

Rossmo's dissertation:
https://summit.sfu.ca/item/6820


---

Future considerations:
- address `RuntimeWarning: invalid value encountered in double_scalars` when using non-default values for `f` and `g` 
- radius / size of plot points 
- allow for user-defined approaches 
- allow for confidence of location, e.g. some of the disappearance locations are "last seen in the Seattle area" (Patricia Yellowrobe)
- allow user to define buffer _type_, e.g. min, max, etc.
- exclude water 





--- 

