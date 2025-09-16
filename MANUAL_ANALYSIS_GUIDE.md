
# Manual Analysis Guide for ARC-AGI Tasks

## Common Patterns to Look For:

1. **Object Manipulation**
   - Moving objects to different positions
   - Copying objects to multiple locations
   - Removing or adding objects

2. **Color Transformations**
   - Color mapping (0->1, 1->2, etc.)
   - Color based on position or neighbors
   - Color based on object properties

3. **Spatial Rules**
   - Symmetry operations
   - Alignment with edges or centers
   - Distance-based rules

4. **Counting Rules**
   - Output based on count of colors
   - Output based on object sizes
   - Output based on spatial relationships

5. **Pattern Completion**
   - Fill missing parts of patterns
   - Complete symmetries
   - Extend sequences

## Analysis Steps:

1. Look at input/output shapes - same size or different?
2. Compare color distributions
3. Look for objects that move or change
4. Check for mathematical relationships
5. Test hypothesis on all training examples

## Code Templates:

### Color Mapping:
```python
def p(g):
    mapping = {0: 1, 1: 2, 2: 0}  # Adjust as needed
    return [[mapping.get(c, c) for c in row] for row in g]
```

### Object Movement:
```python
def p(g):
    # Find objects, apply movement rules
    # This requires custom logic per task
    return g
```

### Pattern Fill:
```python
def p(g):
    # Detect pattern and fill missing parts
    # This requires custom logic per task
    return g
```
