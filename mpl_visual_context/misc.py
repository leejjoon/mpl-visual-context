from .patheffect_locator import LocatorForAnn
from .patheffects_base import ChainedPathEffect


def curved_contour_labels(CS, text_patheffects=None,
                          line_patheffects=None):

    # text to i_contour
    txt2icon = dict((CS.get_text(lev, CS.labelFmt), i) for (i, lev)
                    in zip(CS.labelIndiceList, CS.labelLevelList))

    # there could be multiple labels per a level. So, we make a dictionary that
    # maps a level indice (icon) to the list of lables

    labelDict = dict()

    for t in CS.labelTexts:
        icon = txt2icon[t.get_text()]
        labelDict.setdefault(icon, []).append(t)

    for icon, coll in enumerate(CS.collections):

        if icon not in labelDict:
            continue

        pel = [LocatorForAnn(t, CS.axes,
                             t.get_position(), coords=t.get_transform(),
                             invisible_if_no_intersection=False,
                             do_curve=True)
               for t in labelDict[icon]]

        pe = ChainedPathEffect.from_pe_list(pel)
        if line_patheffects is None:
            _patheffects = [pe]
        else:
            _patheffects = [(pe | pe1) for pe1 in line_patheffects]

        coll.set_path_effects(_patheffects)

        for t, pe in zip(labelDict[icon], pel):
            pe_curved = pe.new_curved_patheffect()
            if text_patheffects is None:
                _patheffects = [pe]
            else:
                _patheffects = [(pe_curved | pe1) for pe1 in text_patheffects]

            t.set_path_effects(_patheffects)
