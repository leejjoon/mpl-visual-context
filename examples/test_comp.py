import matplotlib.pyplot as plt
import seaborn as sns

from mpl_visual_context.color_matrix import ColorMatrixStroke as CMS
from mpl_visual_context.patheffects import HLSModifyStroke


def test1():
    df_peng = sns.load_dataset("penguins")

    pe_list = [None,
               [HLSModifyStroke(l="-50%")],
               [HLSModifyStroke(l="-50%") | CMS("grayscale")]]

    fig, axl = plt.subplots(len(pe_list), 1,
                           figsize=(3, 5),
                            constrained_layout=True,
                            clear=True)

    for ax, pe in zip(axl, pe_list):
        sns.countplot(y="species", data=df_peng, ax=ax)

        for p in ax.patches[:2]:
            p.set_path_effects(pe)

    plt.show()

from mpl_visual_context.path_effects_container import (PathEffectsContainer,
                                                       registry)

def test2():
    df_peng = sns.load_dataset("penguins")

    fig, axl = plt.subplots(3, 1,
                           figsize=(5, 8),
                            constrained_layout=True,
                            clear=True)

    pecl = [PathEffectsContainer(registry) for _ in range(len(axl))]

    for ax, pec in zip(axl, pecl):
        sns.countplot(y="species", data=df_peng, ax=ax)

        for p in ax.patches[:2]:
            p.set_path_effects(pec)

    pecl[1].use("bright")
    pecl[2].use("bright_gray")

    plt.show()

if __name__ == '__main__':
    test2()
