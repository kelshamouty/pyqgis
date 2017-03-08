# Find neighbors of touching polygons in an active layer in QGIS

from qgis.utils import iface
from PyQt4.QtCore import QVariant

# Replace the values below with values from your layer.
field_id = 'NAME'

# Names of the new fields to be added to the layer
neighbors = 'NEIGHBORS'

layer = iface.activeLayer()

# Create 2 new fields in the layer that will hold the list of neighbors and sum
# of the chosen field.
layer.startEditing()
layer.dataProvider().addAttributes(
        [QgsField(neighbors, QVariant.String)])
layer.updateFields()

# Create a dictionary of all features
feature_dict = {f.id(): f for f in layer.getFeatures()}

# Build a spatial index
index = QgsSpatialIndex()
for f in feature_dict.values():
    index.insertFeature(f)

# Loop through all features and find features that touch each feature
for f in feature_dict.values():
    print 'Working on %s' % f[field_id]
    geom = f.geometry()
    # Find all features that intersect the bounding box of the current feature.
    intersecting_ids = index.intersects(geom.boundingBox())
    # Initalize neighbors list and sum
    neighbors = []
    for intersecting_id in intersecting_ids:
        # Look up the feature from the dictionary
        intersecting_f = feature_dict[intersecting_id]

        # For this purpose, consider a feature as 'neighbor' if it touches or
        # intersects a feature. Use the 'disjoint' predicate to satisfy
        # these conditions. So if a feature is not disjoint, it is a neighbor.
        if (f != intersecting_f and
            not intersecting_f.geometry().disjoint(geom)):
            neighbors.append(intersecting_f[field_id])
    f[neighbors] = ','.join(neighbors)
    # Update the layer with new attribute values.
    layer.updateFeature(f)

layer.commitChanges()
print 'Processing complete.'
