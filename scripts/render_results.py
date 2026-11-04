"""Render the recorded final result as SVG/PNG; no model or API calls."""
import json
from pathlib import Path
import statistics

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator


ROOT = Path(__file__).resolve().parents[1]


def render(root=ROOT):
    root = Path(root)
    summary = json.loads((root/'evaluation/pilot/runs/heldout-metrics-v1/summary.json').read_text(encoding='utf-8'))
    run = json.loads((root/'evaluation/pilot/runs/heldout-final-v1/run.json').read_text(encoding='utf-8'))
    keys = ['bm25', 'dense', 'hybrid', 'reranked_hybrid']
    names = ['BM25', 'Dense', 'Hybrid', 'Reranked hybrid']
    fields = ['bm25_ms', 'dense_ms', 'hybrid_ms', 'reranked_total_ms']
    quality = [summary['methods'][key]['ndcg_at_k'] for key in keys]
    latency = [statistics.median(row[field] for row in run['timings']) for field in fields]
    colors = ['#1864ab', '#738298', '#168478', '#8052bd']
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'svg.hashsalt': 'studyrag-final-v1', 'axes.titleweight': 'bold'})
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 5.0), sharey=True)
    fig.patch.set_facecolor('white')
    fig.subplots_adjust(left=.16, right=.96, top=.68, bottom=.26, wspace=.28)
    fig.text(.055, .92, 'StudyRAG | final retrieval check', fontsize=22, weight='bold', color='#192b43')
    fig.text(.055, .84, 'Reranking nearly tied BM25 while adding about 3.4 seconds of CPU processing.', fontsize=12, color='#47576c')
    y = list(range(4))
    axes[0].barh(y, quality, height=.52, color=colors)
    axes[0].set_yticks(y, names)
    axes[0].invert_yaxis()
    axes[0].set_xlim(0, 1)
    axes[0].set_xticks([0, .25, .5, .75, 1])
    axes[0].set_xlabel('nDCG@10 (higher is better)', labelpad=10)
    axes[0].set_title('Ranking quality', loc='left', pad=19, color='#192b43')
    for index, value in enumerate(quality):
        axes[0].text(value+.018, index, f'{value:.3f}', va='center', color='#263c55', fontsize=11)
    axes[1].set_xscale('log')
    axes[1].set_xlim(.1, 40000)
    for index, (value, color) in enumerate(zip(latency, colors)):
        axes[1].hlines(index, .1, value, color='#dfe5ee', linewidth=3)
        axes[1].scatter(value, index, s=78, color=color, zorder=3)
        axes[1].annotate(f'{value:,.2f} ms', (value, index), xytext=(9, 0), textcoords='offset points', va='center', fontsize=10, color='#263c55')
    axes[1].set_xticks([.1, 1, 10, 100, 1000, 10000], ['0.1', '1', '10', '100', '1,000', '10,000'])
    axes[1].xaxis.set_minor_locator(NullLocator())
    axes[1].set_xlabel('Median query time in ms (log scale)', labelpad=10)
    axes[1].set_title('CPU latency', loc='left', pad=19, color='#192b43')
    for axis in axes:
        axis.set_axisbelow(True)
        axis.grid(axis='x', color='#e7ecf2', linewidth=.8)
        axis.tick_params(axis='both', length=0, pad=8, colors='#47576c')
        for spine in axis.spines.values():
            spine.set_visible(False)
    fig.text(.055, .105, '12 answerable reserved questions | 323 AI-reviewed question/passage pairs | same corpus', fontsize=10, color='#47576c')
    fig.text(.055, .055, 'No independent human validation. One timed CPU pass/query; model loading excluded. Source: recorded final-run artifacts.', fontsize=9, color='#65748a')
    out = root/'docs/assets'
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out/'retrieval-results.svg', metadata={'Date': None}, facecolor='white')
    fig.savefig(out/'retrieval-results.png', dpi=160, facecolor='white', metadata={'Software': 'StudyRAG results renderer'})
    plt.close(fig)
    print('Rendered docs/assets/retrieval-results.svg and .png')


if __name__ == '__main__':
    render()
