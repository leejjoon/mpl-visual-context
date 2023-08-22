def extract_offset_boxes_from_legend(legend):
    bboxes = []
    for vpacker in legend._legend_handle_box.get_children():
        for row in vpacker.get_children():
            bboxes.append(row)

    return legend._legend_title_box, bboxes


def set_max_length(offset_bboxes):

    maxwidth = max(ob.get_window_extent().width for ob in offset_bboxes)

    for ob in offset_bboxes:
        ob.set_width(maxwidth)
