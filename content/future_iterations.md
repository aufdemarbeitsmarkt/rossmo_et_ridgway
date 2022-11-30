# Future Iterations 

## General
- allow for "confidence" of location, e.g. some of the disappearance locations are "last seen in the Seattle area" (Patricia Yellowrobe)
- compensate score values for water, unreasonableness of commute or excessive commute times
    - Rossmo discusses this on pg. 154 - 155
        >With no potential victims situated in the English Channel to
the south, he [Jose Rodrigues] was forced to confine his attacks to locations north of his residence,
which resulted in a distorted target pattern
- adjust size of plot points; right now, their display leaves a bit to be desired (they're too small when zoomed out). Bokeh seems limited in its ability to support dynamic glyph sizes based on Zoom.
- varying values for `f` and `g` are not readily supported; in many cases, users will run into `RuntimeWarning: invalid value encountered in double_scalars` due to infinitesimal small values
