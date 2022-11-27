# Introduction & Overview

Gary Ridgway - the Green River Killer - presents a unique, conflicting tension of serial killer tropes. 

He was staggeringly unintelligent, yet operated in a way we typically associate with the well-spoken, genius, highly organized type of killer. As well, Robert Keppel's interviews with Ted Bundy, featured in _`The Riverman`_ form the basis for much of the plot of _`Silence of the Lambs`_. His name doesn't ring out in the way Bundy, Dahmer, and Gacy's do; and generally speaking, he has not been crassly dramatized in the way these killers have been. However, his killings and the corresponding "hunt for the Green River Killer greatly contribute to the way we conceptualize this type of crime.

With this in the back of my mind, I thought it interesting to apply [Rossmo's formula](https://en.wikipedia.org/wiki/Rossmo%27s_formula) to Ridway's crimes.

---
## Explanation of Rossmo's Formula

The primary outline and explanations of Rossmo's formula can be found in [his dissertation](https://summit.sfu.ca/item/6820) on pg. 222 [2]. *Briefly, the formula is used as a model to predict where a serial criminal resides (or works).*

We use the following process to fill in our model:
1. determine map boundaries using the crime locations ([my approach](rossmo_et_ridgway/rossmo_et_ridgway.py#L102) differs from Rossmo's so I will describe it instead)
    a. grab the north-, south-, east-, and west-most coordinates for all crimes
    b. grab the max distance between all crimes
    c. add the max distance to the four coordinates found in step a.; these are our boundaries
2. find the Manhattan distance between each point within our boundaries and each crime
3. use these Manhattan distances as independent variables in the following function:

>$
p_{i,j} = k \sum_{n=1} \left [ \frac{\phi_{i,j}}{(|x_i - x_n| + |y_j - y_n|)^f)} + \frac{(1 - \phi_{i,j})(B^{g-f})}{(2B - |x_i - x_n| + |y_j - y_n|)^g} \right ],
$

**where:**

>$ 
\phi_{i,j} = \left\{\begin{matrix}
1, & if (|X_i - x_n| + |Y_j - y_n|) > B \\ 
0, & else
\end{matrix}\right.
$

This produces a score for each point in our map; a higher score denotes a higher probability that the criminal resides or works in that location.

### An explanation of the variables within this function:

- $P_{i,j}$ - the probability score for the point on our map, $i,j$
- $\phi$ - a weight; as above, if the Manhattan distance between a map point and a crime is greater than the buffer radius, then this value with be $1$, otherwise, it will be $0$
- $B$ - radius of our buffer zone; the function is written such that, if a map point lies within our buffer radius, a number will be generated that is larger, the longer the distance, **OR** a number will be generated that is smaller the longer the distance -- depending on $\phi$, of course
- $f$ - an "empirically" determined exponent; $f$ controls how quickly the score decays outside the buffer radius
- $g$ - an "empirically" determined exponent; $g$ controls how quickly the score decause _inside_ the buffer radius
- $x_i, y_j$ - the coordinates of map point, %i,j%
- $x_n, y_n$ - the coordinates of the $n$th crime location


### Additional notes:

- In Rossmo's disseration, he assigns a value of $1.2$ for both $f$ and $g$. He suggests these values should be the same, and it's a bit unclear why that is the case. In my implementation, both of these values default to $1.0$
- In the second term of Rossmo's formula, what I presume to be a Manhattan distance is shown as: $|X_i - X_n| - |Y_j - Y_n|$; Manhattan distance is calculated as follows: $|X_i - X_n| + |Y_j - Y_n|$, where the distances between each $X$ and $Y$ are _summed_. It's unclear whether this is a typo; my implementation uses the Manhattan distance calculation for _both_ terms.
- Rossmo includes a variable, $k$. The recommended value for $k$ is unclear; I am assuming this value is $1%, and I've excluded it from my implementation