
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
from mpl_visual_context.patheffect_locator import (LocatorForAnn,
                                                   LocatorForIXYAR)

if True:

    fig, axs = plt.subplots(5, 1, num=1, clear=True, figsize=(5, 9))
    X = np.linspace(-np.pi, np.pi, 400, endpoint=True)
    # X = np.linspace(-np.pi, np.pi, 4, endpoint=True)
    C, S = np.cos(X), np.sin(X)

    # AX 0
    ax = axs[0]
    l1, = ax.plot(X, C, label="cosine", clip_on=False)
    l2, = ax.plot(X, S, label="sine", clip_on=False)

    ann_kwargs = dict(xy=(0, 0), xytext=(20, 0),
                      # xycoords="data",
                      xycoords="figure pixels",
                      textcoords="offset points",
                      # transform=mtransforms.IdentityTransform(),
                      va="center", ha="left", # size=15,
                      )
    pe_kwargs = dict(x=0.95,
                     coords="axes fraction",
                     # do_rotate=False,
                     locate_only=True,
                     split_path=False)

    for l in [l1, l2]:
        t = ax.annotate(l.get_label(), color=l.get_color(),
                        arrowprops=dict(arrowstyle="-", shrinkB=5,
                                        ec=l.get_color()),
                        **ann_kwargs)
        l.set_path_effects([LocatorForAnn(t, ax, **pe_kwargs)])


    # AX 1
    ax = axs[1]
    l1, = ax.plot(X, C, label="cosine", clip_on=False)
    l2, = ax.plot(X, S, label="sine", clip_on=False)

    ann_kwargs = dict(xy=(0, 0), xytext=(0, 0),
                      xycoords="figure pixels",
                      textcoords="offset points",
                      va="center", ha="center", # size=15,
                      )
    pe_kwargs = dict(coords="data",
                     do_rotate=True, do_curve=True,
                     split_path=True)

    for l, x in zip([l1, l2], [-0.5*np.pi, 0]):
        t = ax.annotate(l.get_label(), color=l.get_color(),
                        **ann_kwargs)
        l_pe = LocatorForAnn(t, ax, x=x, **pe_kwargs)
        l.set_path_effects([l_pe])

        t_pe = l_pe.new_curved_patheffect()
        t.set_path_effects([t_pe])


    # AX 2
    ax = axs[2]
    l1, = ax.plot(X, C, label="cosine", clip_on=False)
    l2, = ax.plot(X, S, label="sine", clip_on=False)

    ann_kwargs = dict(xy=(0, 0), xytext=(-20, 10),
                      # xycoords="data",
                      xycoords="figure pixels",
                      textcoords="offset points",
                      # transform=mtransforms.IdentityTransform(),
                      va="center", ha="right", # size=15,
                      )
    pe_kwargs = dict(coords="data",
                     locate_only=True,
                     # do_rotate=False,
                     split_path=False)

    for l, x in zip([l1, l2], [-0.5*np.pi, 0]):
        t = ax.annotate(l.get_label(), color=l.get_color(),
                        arrowprops=dict(arrowstyle="->", shrinkB=5,
                                        ec=l.get_color(),
                                        connectionstyle="arc3,rad=-0.3"),
                        **ann_kwargs)
        l.set_path_effects([LocatorForAnn(t, ax, x=x, **pe_kwargs)])


    # AX 3
    ax = axs[3]
    l1, = ax.plot(X, C, label="cosine", clip_on=False)
    l2, = ax.plot(X, S, label="sine", clip_on=False)

    from matplotlib.patches import Circle

    radius = 6
    pe_kwargs = dict(coords="axes fraction", pad=radius,
                     do_rotate=False,
                     split_path=True)

    for l, c in zip([l1, l2], ["A", "B"]):
        # while we set the radius here, we want the radius in points thus it
        # needs to be reset at drawing time.
        color = l.get_color()
        p = Circle((0, 0), radius, transform=mtransforms.IdentityTransform(),
                   ec=color, fc="none",
                   zorder=3) # zorder should be higher than l1
        ax.add_patch(p)
        t = ax.text(0, 0, c, transform=mtransforms.IdentityTransform(),
                    color=color,
                    ha="center", va="center", size=radius*1.2)

        def cb_ixyar(i, xy, angle, R, renderer, t=t, p=p):
            dpi_cor = renderer.points_to_pixels(1.)

            if i == -1:
                p.set_visible(False)
                t.set_visible(False)
            elif i == 0:
                p.set_visible(True)
                t.set_visible(True)
                p.set_center(xy)
                p.set_radius(radius*dpi_cor)
                t.set_position(xy)

        l.set_path_effects([LocatorForIXYAR(cb_ixyar, ax, x=0.1, **pe_kwargs)])


    # AX 4
    ax = axs[4]
    l1, = ax.plot(X, C, label="cosine", clip_on=False)
    l2, = ax.plot(X, S, label="sine", clip_on=False)

    from mpl_visual_context.patheffects import Affine

    ann_kwargs = dict(xy=(0, 0), xytext=(0, 0),
                      xycoords="figure pixels",
                      textcoords="offset points",
                      va="center", ha="center", # size=15,
                      )
    pe_kwargs = dict(coords="data",
                     do_rotate=True, do_curve=True,
                     split_path=False)

    for l, x in zip([l1, l2], [-0.5*np.pi, 0]):
        t = ax.annotate(l.get_label(), color=l.get_color(),
                        **ann_kwargs)
        l_pe = LocatorForAnn(t, ax, x=x, **pe_kwargs)
        l.set_path_effects([l_pe])

        t_pe = l_pe.new_curved_patheffect()
        t.set_path_effects([t_pe | Affine().translate(0, 80)])

    plt.show()
