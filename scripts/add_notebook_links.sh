#!/bin/bash
omero hql --limit 2000 --ids-only --style csv "select l.child from ScreenPlateLink l where l.parent=2551" | cut -d , -f 2 | grep Plate > /tmp/plates.txt

for i in `cat /tmp/plates.txt`
do
	plateid=${i##*:}
	ma=$(omero obj new MapAnnotation)
	omero obj new PlateAnnotationLink parent=$i child=$ma
	omero obj map-set $ma mapValue "Study Notebook" "https://mybinder.org/v2/gh/IDR/idr0093-mueller-perturbation/master?urlpath=notebooks%2Fnotebooks%2Fidr0093_explore.ipynb%3FplateId%3D$plateid"
done

