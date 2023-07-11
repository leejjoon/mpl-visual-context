import matplotlib.pyplot as plt
import seaborn as sns

from mpl_visual_context.patheffects import HLSModifyStroke

def main():
    df_peng = sns.load_dataset("penguins")

    fig, ax = plt.subplots(figsize=(5, 3), constrained_layout=True, clear=True)
    sns.countplot(y="species", data=df_peng, ax=ax)

    pe = [HLSModifyStroke(l = "-50%", s="100%")]

    p = ax.patches[0]
    p.set_ec("k")
    p.set_path_effects(pe)
    p = ax.patches[1]
    p.set_ec("k")
    p = ax.patches[2]
    p.set_path_effects(pe)

    plt.show()

if __name__ == '__main__':
    main()
